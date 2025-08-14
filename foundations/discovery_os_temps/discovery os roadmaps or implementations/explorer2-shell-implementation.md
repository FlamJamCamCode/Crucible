# Explorer2: Building a Windows Shell Replacement with Raw Input Capture

## Overview

This guide details how to build Explorer2.exe, a complete Windows shell replacement that captures all system input at the raw level, enabling revolutionary input transformation while maintaining full Windows compatibility.

## Architecture

### Core Components

```
Explorer2.exe (Shell)
├── Shell Services
│   ├── Taskbar Manager
│   ├── Desktop Window Manager
│   ├── System Tray Handler
│   └── Start Menu Provider
├── Raw Input System
│   ├── Device Enumerator
│   ├── Input Capture Engine
│   ├── Event Dispatcher
│   └── Performance Monitor
├── Mapper Pipeline
│   ├── Pipeline Manager
│   ├── Mapper Registry
│   ├── Context Engine
│   └── Output Router
└── Legacy Compatibility
    ├── SendInput Bridge
    ├── Hook Manager
    ├── Focus Tracker
    └── Window Manager
```

## Implementation

### 1. Shell Registration and Startup

```csharp
// Program.cs - Entry point
using System;
using System.Diagnostics;
using Microsoft.Win32;

namespace Explorer2
{
    class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            // Check if we're being launched as shell
            if (args.Length > 0 && args[0] == "/shell")
            {
                RunAsShell();
            }
            else
            {
                // Interactive setup mode
                ShellInstaller.Run();
            }
        }
        
        static void RunAsShell()
        {
            try
            {
                // Prevent multiple instances
                using var mutex = new Mutex(true, "Explorer2_Shell_Mutex", out bool createdNew);
                if (!createdNew)
                {
                    Environment.Exit(1);
                }
                
                // Initialize core systems
                var shell = new Explorer2Shell();
                shell.Initialize();
                shell.Run();
            }
            catch (Exception ex)
            {
                // Critical failure - log and restart default shell
                CrashHandler.LogCriticalError(ex);
                RestoreDefaultShell();
            }
        }
    }
}

// ShellInstaller.cs - Handles shell replacement
public static class ShellInstaller
{
    private const string SHELL_KEY = @"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon";
    
    public static void Run()
    {
        Console.WriteLine("Explorer2 Shell Installer");
        Console.WriteLine("========================");
        Console.WriteLine("1. Install as default shell");
        Console.WriteLine("2. Restore Windows Explorer");
        Console.WriteLine("3. Run once without installing");
        
        switch (Console.ReadKey().KeyChar)
        {
            case '1':
                InstallAsShell();
                break;
            case '2':
                RestoreExplorer();
                break;
            case '3':
                RunOnce();
                break;
        }
    }
    
    private static void InstallAsShell()
    {
        try
        {
            // Kill existing Explorer
            foreach (var process in Process.GetProcessesByName("explorer"))
            {
                process.Kill();
                process.WaitForExit();
            }
            
            // Update registry
            using (var key = Registry.LocalMachine.OpenSubKey(SHELL_KEY, true))
            {
                key.SetValue("Shell", $"\"{Application.ExecutablePath}\" /shell");
            }
            
            // Start ourselves as shell
            Process.Start(Application.ExecutablePath, "/shell");
            
            Console.WriteLine("Explorer2 installed as default shell!");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Installation failed: {ex.Message}");
            Console.WriteLine("Run as Administrator!");
        }
    }
}
```

### 2. Core Shell Implementation

```csharp
// Explorer2Shell.cs - Main shell class
public class Explorer2Shell : IDisposable
{
    private RawInputManager rawInput;
    private TaskbarManager taskbar;
    private DesktopManager desktop;
    private SystemTrayManager tray;
    private MapperPipeline pipeline;
    private bool running = true;
    
    public void Initialize()
    {
        // Set up process priority for responsiveness
        Process.GetCurrentProcess().PriorityClass = ProcessPriorityClass.High;
        
        // Initialize subsystems in order
        InitializeDesktop();
        InitializeTaskbar();
        InitializeSystemTray();
        InitializeRawInput();
        InitializeMapperPipeline();
        
        // Register for system events
        SystemEvents.SessionEnding += OnSessionEnding;
        SystemEvents.DisplaySettingsChanged += OnDisplaySettingsChanged;
    }
    
    private void InitializeDesktop()
    {
        desktop = new DesktopManager();
        
        // Create the desktop window
        var desktopWindow = new DesktopWindow();
        desktopWindow.CreateHandle();
        
        // Set as shell window
        User32.SetShellWindow(desktopWindow.Handle);
        
        // Enable desktop icons, wallpaper, etc.
        desktop.EnableDesktopIcons();
        desktop.RestoreWallpaper();
    }
    
    private void InitializeTaskbar()
    {
        taskbar = new TaskbarManager();
        
        // Create taskbar window
        var taskbarWindow = new TaskbarWindow();
        taskbarWindow.Show();
        
        // Register app bar
        var appBarData = new APPBARDATA
        {
            cbSize = Marshal.SizeOf<APPBARDATA>(),
            hWnd = taskbarWindow.Handle,
            uEdge = ABE_BOTTOM
        };
        Shell32.SHAppBarMessage(ABM_NEW, ref appBarData);
        
        // Set position
        taskbar.UpdatePosition();
        
        // Start monitoring running applications
        taskbar.StartApplicationMonitoring();
    }
    
    private void InitializeRawInput()
    {
        rawInput = new RawInputManager();
        
        // Register for all input devices
        var devices = new[]
        {
            new RAWINPUTDEVICE
            {
                usUsagePage = HID_USAGE_PAGE_GENERIC,
                usUsage = HID_USAGE_GENERIC_KEYBOARD,
                dwFlags = RIDEV_INPUTSINK | RIDEV_DEVNOTIFY,
                hwndTarget = desktop.Handle
            },
            new RAWINPUTDEVICE
            {
                usUsagePage = HID_USAGE_PAGE_GENERIC,
                usUsage = HID_USAGE_GENERIC_MOUSE,
                dwFlags = RIDEV_INPUTSINK | RIDEV_DEVNOTIFY,
                hwndTarget = desktop.Handle
            }
        };
        
        if (!RegisterRawInputDevices(devices, devices.Length, Marshal.SizeOf<RAWINPUTDEVICE>()))
        {
            throw new Win32Exception(Marshal.GetLastWin32Error());
        }
        
        // Start device enumeration
        rawInput.EnumerateDevices();
    }
    
    public void Run()
    {
        // Main message loop
        var msg = new MSG();
        while (running)
        {
            if (PeekMessage(out msg, IntPtr.Zero, 0, 0, PM_REMOVE))
            {
                if (msg.message == WM_QUIT)
                {
                    running = false;
                    break;
                }
                
                // Handle raw input specially
                if (msg.message == WM_INPUT)
                {
                    ProcessRawInput(msg.lParam);
                }
                else
                {
                    TranslateMessage(ref msg);
                    DispatchMessage(ref msg);
                }
            }
            else
            {
                // No messages - do background work
                Thread.Sleep(1);
                pipeline.ProcessBufferedEvents();
            }
        }
    }
}
```

### 3. Raw Input Capture System

```csharp
// RawInputManager.cs - Core input capture
public class RawInputManager
{
    private readonly Dictionary<IntPtr, InputDevice> devices = new();
    private readonly Subject<RawInputEvent> inputStream = new();
    private readonly PerformanceCounter perfCounter = new();
    
    public IObservable<RawInputEvent> InputStream => inputStream.AsObservable();
    
    public void ProcessRawInput(IntPtr lParam)
    {
        uint dwSize = 0;
        
        // Get size of input data
        GetRawInputData(lParam, RID_INPUT, IntPtr.Zero, ref dwSize, Marshal.SizeOf<RAWINPUTHEADER>());
        
        if (dwSize == 0) return;
        
        // Allocate buffer
        var buffer = Marshal.AllocHGlobal((int)dwSize);
        try
        {
            // Get the actual data
            if (GetRawInputData(lParam, RID_INPUT, buffer, ref dwSize, Marshal.SizeOf<RAWINPUTHEADER>()) == dwSize)
            {
                // Parse the input
                var raw = Marshal.PtrToStructure<RAWINPUT>(buffer);
                
                // Track performance
                perfCounter.InputReceived();
                
                // Convert to our event format
                var inputEvent = ConvertRawInput(raw);
                if (inputEvent != null)
                {
                    // Send through pipeline
                    inputStream.OnNext(inputEvent);
                }
            }
        }
        finally
        {
            Marshal.FreeHGlobal(buffer);
        }
    }
    
    private RawInputEvent ConvertRawInput(RAWINPUT raw)
    {
        // Get device info
        if (!devices.TryGetValue(raw.header.hDevice, out var device))
        {
            device = EnumerateDevice(raw.header.hDevice);
            devices[raw.header.hDevice] = device;
        }
        
        switch (raw.header.dwType)
        {
            case RIM_TYPEKEYBOARD:
                return ConvertKeyboardInput(raw.keyboard, device);
                
            case RIM_TYPEMOUSE:
                return ConvertMouseInput(raw.mouse, device);
                
            case RIM_TYPEHID:
                return ConvertHIDInput(raw.hid, device);
                
            default:
                return null;
        }
    }
    
    private RawInputEvent ConvertKeyboardInput(RAWKEYBOARD keyboard, InputDevice device)
    {
        return new RawInputEvent
        {
            Device = device,
            Type = InputType.Keyboard,
            Timestamp = GetHighResolutionTimestamp(),
            Keyboard = new KeyboardData
            {
                ScanCode = keyboard.MakeCode,
                VirtualKey = keyboard.VKey,
                Flags = (KeyboardFlags)keyboard.Flags,
                IsDown = (keyboard.Flags & RI_KEY_BREAK) == 0,
                IsExtended = (keyboard.Flags & RI_KEY_E0) != 0
            }
        };
    }
    
    public void EnumerateDevices()
    {
        uint deviceCount = 0;
        uint deviceSize = (uint)Marshal.SizeOf<RAWINPUTDEVICELIST>();
        
        // Get device count
        GetRawInputDeviceList(IntPtr.Zero, ref deviceCount, deviceSize);
        
        if (deviceCount == 0) return;
        
        // Allocate buffer for device list
        var deviceList = new RAWINPUTDEVICELIST[deviceCount];
        var gcHandle = GCHandle.Alloc(deviceList, GCHandleType.Pinned);
        
        try
        {
            // Get device list
            GetRawInputDeviceList(gcHandle.AddrOfPinnedObject(), ref deviceCount, deviceSize);
            
            // Process each device
            foreach (var device in deviceList)
            {
                var info = GetDeviceInfo(device.hDevice);
                devices[device.hDevice] = info;
                
                // Notify device connected
                OnDeviceConnected(info);
            }
        }
        finally
        {
            gcHandle.Free();
        }
    }
    
    private InputDevice GetDeviceInfo(IntPtr hDevice)
    {
        uint size = 0;
        GetRawInputDeviceInfo(hDevice, RIDI_DEVICEINFO, IntPtr.Zero, ref size);
        
        var buffer = Marshal.AllocHGlobal((int)size);
        try
        {
            GetRawInputDeviceInfo(hDevice, RIDI_DEVICEINFO, buffer, ref size);
            var info = Marshal.PtrToStructure<RID_DEVICE_INFO>(buffer);
            
            // Get device name
            GetRawInputDeviceInfo(hDevice, RIDI_DEVICENAME, IntPtr.Zero, ref size);
            var nameBuffer = Marshal.AllocHGlobal((int)size * 2); // Unicode
            string deviceName = "";
            
            try
            {
                GetRawInputDeviceInfo(hDevice, RIDI_DEVICENAME, nameBuffer, ref size);
                deviceName = Marshal.PtrToStringUni(nameBuffer);
            }
            finally
            {
                Marshal.FreeHGlobal(nameBuffer);
            }
            
            return new InputDevice
            {
                Handle = hDevice,
                Name = deviceName,
                Type = GetDeviceType(info),
                VendorId = info.hid.dwVendorId,
                ProductId = info.hid.dwProductId,
                VersionNumber = info.hid.dwVersionNumber
            };
        }
        finally
        {
            Marshal.FreeHGlobal(buffer);
        }
    }
}

// PerformanceMonitor.cs - Track input performance
public class InputPerformanceMonitor
{
    private readonly CircularBuffer<long> latencies = new(1000);
    private readonly Stopwatch stopwatch = Stopwatch.StartNew();
    private long lastInputTime;
    
    public void InputReceived()
    {
        var now = stopwatch.ElapsedTicks;
        if (lastInputTime != 0)
        {
            var latency = now - lastInputTime;
            latencies.Add(latency);
        }
        lastInputTime = now;
    }
    
    public InputPerformanceStats GetStats()
    {
        var latencyArray = latencies.ToArray();
        if (latencyArray.Length == 0)
        {
            return new InputPerformanceStats();
        }
        
        Array.Sort(latencyArray);
        
        return new InputPerformanceStats
        {
            AverageLatencyMs = TicksToMs(latencyArray.Average()),
            P99LatencyMs = TicksToMs(latencyArray[(int)(latencyArray.Length * 0.99)]),
            P95LatencyMs = TicksToMs(latencyArray[(int)(latencyArray.Length * 0.95)]),
            MedianLatencyMs = TicksToMs(latencyArray[latencyArray.Length / 2]),
            InputsPerSecond = latencyArray.Length > 1 ? 
                1000.0 / TicksToMs(latencyArray.Average()) : 0
        };
    }
    
    private double TicksToMs(double ticks)
    {
        return (ticks / Stopwatch.Frequency) * 1000.0;
    }
}
```

### 4. Desktop Window Implementation

```csharp
// DesktopWindow.cs - The root window that receives input
public class DesktopWindow : NativeWindow
{
    private const string DESKTOP_CLASS = "Explorer2Desktop";
    private readonly MapperPipeline pipeline;
    
    public DesktopWindow(MapperPipeline pipeline)
    {
        this.pipeline = pipeline;
        CreateDesktopWindow();
    }
    
    private void CreateDesktopWindow()
    {
        // Register window class
        var wndClass = new WNDCLASSEX
        {
            cbSize = Marshal.SizeOf<WNDCLASSEX>(),
            style = CS_DBLCLKS,
            lpfnWndProc = WndProc,
            hInstance = GetModuleHandle(null),
            hCursor = LoadCursor(IntPtr.Zero, IDC_ARROW),
            hbrBackground = (IntPtr)(COLOR_DESKTOP + 1),
            lpszClassName = DESKTOP_CLASS
        };
        
        RegisterClassEx(ref wndClass);
        
        // Create window covering entire screen
        var screenWidth = GetSystemMetrics(SM_CXSCREEN);
        var screenHeight = GetSystemMetrics(SM_CYSCREEN);
        
        var hwnd = CreateWindowEx(
            0,
            DESKTOP_CLASS,
            "Explorer2 Desktop",
            WS_POPUP | WS_VISIBLE | WS_CLIPSIBLINGS,
            0, 0, screenWidth, screenHeight,
            IntPtr.Zero,
            IntPtr.Zero,
            GetModuleHandle(null),
            IntPtr.Zero
        );
        
        AssignHandle(hwnd);
        
        // Set as desktop window
        SetShellWindow(hwnd);
        
        // Enable drag-drop
        DragAcceptFiles(hwnd, true);
    }
    
    protected override void WndProc(ref Message m)
    {
        switch (m.Msg)
        {
            case WM_INPUT:
                HandleRawInput(m.LParam);
                break;
                
            case WM_INPUT_DEVICE_CHANGE:
                HandleDeviceChange(m.WParam, m.LParam);
                break;
                
            case WM_CONTEXTMENU:
                ShowDesktopContextMenu(m.LParam);
                break;
                
            case WM_DROPFILES:
                HandleFileDrop(m.WParam);
                break;
                
            default:
                base.WndProc(ref m);
                break;
        }
    }
    
    private void HandleRawInput(IntPtr lParam)
    {
        try
        {
            // Get input data size
            uint size = 0;
            GetRawInputData(lParam, RID_INPUT, IntPtr.Zero, ref size, Marshal.SizeOf<RAWINPUTHEADER>());
            
            if (size == 0) return;
            
            // Process through high-performance path
            using (var buffer = new UnmanagedBuffer((int)size))
            {
                if (GetRawInputData(lParam, RID_INPUT, buffer.Pointer, ref size, Marshal.SizeOf<RAWINPUTHEADER>()) == size)
                {
                    // Direct memory access for performance
                    unsafe
                    {
                        var raw = (RAWINPUT*)buffer.Pointer;
                        ProcessRawInputDirect(raw);
                    }
                }
            }
        }
        catch (Exception ex)
        {
            Logger.LogError("Raw input processing error", ex);
        }
    }
    
    private unsafe void ProcessRawInputDirect(RAWINPUT* raw)
    {
        // Ultra-fast processing path
        var timestamp = QueryPerformanceCounter();
        
        switch (raw->header.dwType)
        {
            case RIM_TYPEKEYBOARD:
                var keyEvent = new InputEvent
                {
                    Type = InputType.Key,
                    Device = GetOrCreateDevice(raw->header.hDevice),
                    RawCode = raw->keyboard.MakeCode,
                    State = (raw->keyboard.Flags & RI_KEY_BREAK) == 0 ? 
                        InputState.Down : InputState.Up,
                    Timestamp = timestamp
                };
                
                pipeline.ProcessInputAsync(keyEvent);
                break;
                
            case RIM_TYPEMOUSE:
                // Process mouse with minimal allocation
                ProcessMouseDirect(&raw->mouse, raw->header.hDevice, timestamp);
                break;
        }
    }
}
```

### 5. Taskbar Implementation

```csharp
// TaskbarWindow.cs - Modern taskbar with domain support
public class TaskbarWindow : Form
{
    private readonly FlowLayoutPanel taskButtons;
    private readonly SystemTray systemTray;
    private readonly DomainIndicator domainIndicator;
    private readonly NotificationArea notifications;
    
    public TaskbarWindow()
    {
        InitializeTaskbar();
        SetupAppBar();
    }
    
    private void InitializeTaskbar()
    {
        // Configure window
        FormBorderStyle = FormBorderStyle.None;
        ShowInTaskbar = false;
        TopMost = true;
        Height = 40;
        BackColor = Color.FromArgb(32, 32, 32);
        
        // Create layout
        var layout = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 4,
            RowCount = 1
        };
        
        // Start button
        var startButton = new StartButton();
        startButton.Click += OnStartClick;
        layout.Controls.Add(startButton, 0, 0);
        
        // Task buttons
        taskButtons = new FlowLayoutPanel
        {
            Dock = DockStyle.Fill,
            FlowDirection = FlowDirection.LeftToRight,
            WrapContents = false
        };
        layout.Controls.Add(taskButtons, 1, 0);
        
        // Domain indicator
        domainIndicator = new DomainIndicator();
        layout.Controls.Add(domainIndicator, 2, 0);
        
        // System tray
        systemTray = new SystemTray();
        layout.Controls.Add(systemTray, 3, 0);
        
        Controls.Add(layout);
    }
    
    private void SetupAppBar()
    {
        var abd = new APPBARDATA
        {
            cbSize = Marshal.SizeOf<APPBARDATA>(),
            hWnd = Handle,
            uCallbackMessage = WM_APPBAR_CALLBACK
        };
        
        // Register as app bar
        SHAppBarMessage(ABM_NEW, ref abd);
        
        // Set position
        abd.uEdge = ABE_BOTTOM;
        abd.rc = new RECT
        {
            left = 0,
            top = Screen.PrimaryScreen.Bounds.Height - Height,
            right = Screen.PrimaryScreen.Bounds.Width,
            bottom = Screen.PrimaryScreen.Bounds.Height
        };
        
        SHAppBarMessage(ABM_SETPOS, ref abd);
    }
    
    public void AddTaskButton(IntPtr hwnd, string title, Icon icon)
    {
        var button = new TaskButton
        {
            WindowHandle = hwnd,
            Text = title,
            Image = icon?.ToBitmap(),
            Width = 200,
            Height = 36
        };
        
        button.Click += (s, e) => ActivateWindow(hwnd);
        button.ContextMenuStrip = CreateTaskContextMenu(hwnd);
        
        taskButtons.Controls.Add(button);
    }
    
    private void ActivateWindow(IntPtr hwnd)
    {
        // Check if window belongs to current domain
        var domain = DomainManager.GetWindowDomain(hwnd);
        if (domain != DomainManager.CurrentDomain)
        {
            // Show domain switch prompt
            if (MessageBox.Show(
                $"This window belongs to {domain.Name}. Switch domain?",
                "Domain Switch",
                MessageBoxButtons.YesNo) == DialogResult.Yes)
            {
                DomainManager.SwitchToDomain(domain);
            }
            else
            {
                return;
            }
        }
        
        // Activate the window
        SetForegroundWindow(hwnd);
        
        // Restore if minimized
        if (IsIconic(hwnd))
        {
            ShowWindow(hwnd, SW_RESTORE);
        }
    }
}

// DomainIndicator.cs - Shows current input domain
public class DomainIndicator : UserControl
{
    private Label domainLabel;
    private PictureBox userIcon;
    
    public DomainIndicator()
    {
        Width = 150;
        
        userIcon = new PictureBox
        {
            Size = new Size(32, 32),
            Location = new Point(4, 4),
            SizeMode = PictureBoxSizeMode.Zoom
        };
        
        domainLabel = new Label
        {
            Location = new Point(40, 8),
            Size = new Size(106, 24),
            TextAlign = ContentAlignment.MiddleLeft,
            ForeColor = Color.White
        };
        
        Controls.AddRange(new Control[] { userIcon, domainLabel });
        
        // Subscribe to domain changes
        DomainManager.DomainChanged += OnDomainChanged;
        UpdateDisplay();
    }
    
    private void OnDomainChanged(object sender, DomainChangedEventArgs e)
    {
        UpdateDisplay();
    }
    
    private void UpdateDisplay()
    {
        var domain = DomainManager.CurrentDomain;
        domainLabel.Text = domain.Name;
        userIcon.Image = domain.UserIcon;
        BackColor = domain.ThemeColor;
    }
    
    protected override void OnClick(EventArgs e)
    {
        // Show domain switcher
        var switcher = new DomainSwitcher();
        switcher.Show(this, new Point(0, -switcher.Height));
    }
}
```

### 6. Critical System Integration

```csharp
// SystemIntegration.cs - Ensures Windows continues to work
public static class SystemIntegration
{
    public static void EnsureCriticalServices()
    {
        // Start critical Windows services our shell needs
        EnsureService("Themes");      // Visual styles
        EnsureService("AudioSrv");    // Sound
        EnsureService("Spooler");     // Printing
        EnsureService("ShellHWDetection"); // Hardware
        
        // Initialize COM
        CoInitializeEx(IntPtr.Zero, COINIT_APARTMENTTHREADED);
        
        // Register for power notifications
        RegisterPowerSettingNotification(
            Process.GetCurrentProcess().Handle,
            ref GUID_CONSOLE_DISPLAY_STATE,
            DEVICE_NOTIFY_CALLBACK);
        
        // Set up file associations
        RestoreFileAssociations();
        
        // Initialize notification system
        InitializeNotificationPlatform();
    }
    
    private static void RestoreFileAssociations()
    {
        // Ensure file types open correctly
        var assocKey = Registry.CurrentUser.OpenSubKey(
            @"Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts",
            true);
        
        // Re-register common types
        RegisterFileType(".exe", "exefile", "Application");
        RegisterFileType(".txt", "txtfile", "Text Document");
        RegisterFileType(".jpg", "jpegfile", "JPEG Image");
        // ... etc
    }
    
    public static void HandleCriticalError(Exception ex)
    {
        // Log error
        EventLog.WriteEntry("Explorer2", 
            $"Critical error: {ex.Message}\n{ex.StackTrace}", 
            EventLogEntryType.Error);
        
        // Show user-friendly error
        MessageBox.Show(
            "Explorer2 encountered an error and needs to restart.\n\n" +
            "Your work has been saved.",
            "Explorer2",
            MessageBoxButtons.OK,
            MessageBoxIcon.Error);
        
        // Restart shell
        RestartShell();
    }
    
    private static void RestartShell()
    {
        // Save state
        SaveShellState();
        
        // Start new instance
        Process.Start(Application.ExecutablePath, "/shell");
        
        // Exit this instance
        Environment.Exit(1);
    }
}

// CrashHandler.cs - Graceful failure handling
public static class CrashHandler
{
    public static void Install()
    {
        AppDomain.CurrentDomain.UnhandledException += OnUnhandledException;
        Application.ThreadException += OnThreadException;
        Application.SetUnhandledExceptionMode(UnhandledExceptionMode.CatchException);
    }
    
    private static void OnUnhandledException(object sender, UnhandledExceptionEventArgs e)
    {
        var ex = e.ExceptionObject as Exception;
        LogCriticalError(ex);
        
        if (e.IsTerminating)
        {
            // We're going down - ensure Windows has a shell
            EnsureShellContinuity();
        }
    }
    
    private static void EnsureShellContinuity()
    {
        try
        {
            // Try to restart ourselves
            Process.Start(Application.ExecutablePath, "/shell /recovery");
        }
        catch
        {
            // Failed - restore Windows Explorer
            try
            {
                Process.Start("explorer.exe");
            }
            catch
            {
                // System is in bad state - trigger Windows recovery
                Native.NtRaiseHardError(
                    0xC0000135, // STATUS_DLL_NOT_FOUND
                    0, 0, IntPtr.Zero, 0, 
                    out uint response);
            }
        }
    }
}
```

### 7. Performance Optimizations

```csharp
// HighPerformanceInput.cs - Optimized input processing
public class HighPerformanceInputProcessor
{
    private readonly ThreadLocal<InputBatch> threadLocalBatch;
    private readonly BlockingCollection<InputBatch> batchQueue;
    private readonly Thread[] workerThreads;
    
    public HighPerformanceInputProcessor(int threadCount = 4)
    {
        threadLocalBatch = new ThreadLocal<InputBatch>(() => new InputBatch());
        batchQueue = new BlockingCollection<InputBatch>();
        
        // Start worker threads
        workerThreads = new Thread[threadCount];
        for (int i = 0; i < threadCount; i++)
        {
            workerThreads[i] = new Thread(ProcessBatches)
            {
                Name = $"InputProcessor{i}",
                IsBackground = false,
                Priority = ThreadPriority.Highest
            };
            workerThreads[i].Start();
        }
    }
    
    public void ProcessInput(RawInputEvent input)
    {
        var batch = threadLocalBatch.Value;
        batch.Add(input);
        
        if (batch.Count >= 32 || batch.Age > TimeSpan.FromMilliseconds(1))
        {
            batchQueue.Add(batch);
            threadLocalBatch.Value = new InputBatch();
        }
    }
    
    private void ProcessBatches()
    {
        // Pin thread to CPU core
        Thread.BeginThreadAffinity();
        
        // Reduce GC pressure
        GC.TryStartNoGCRegion(10 * 1024 * 1024); // 10MB
        
        try
        {
            foreach (var batch in batchQueue.GetConsumingEnumerable())
            {
                ProcessBatchOptimized(batch);
                batch.Return(); // Object pooling
            }
        }
        finally
        {
            GC.EndNoGCRegion();
            Thread.EndThreadAffinity();
        }
    }
    
    private unsafe void ProcessBatchOptimized(InputBatch batch)
    {
        // Process in tight loop with minimal allocations
        fixed (InputEvent* events = batch.Events)
        {
            for (int i = 0; i < batch.Count; i++)
            {
                var evt = events[i];
                
                // Fast path for gaming input
                if (evt.Domain.IsGaming && evt.Device.IsGamingDevice)
                {
                    DirectInject(&evt);
                }
                else
                {
                    // Normal pipeline
                    pipeline.Process(evt);
                }
            }
        }
    }
}
```

## Installation and Configuration

### Registry Settings

```registry
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon]
"Shell"="C:\\Program Files\\Explorer2\\Explorer2.exe /shell"

[HKEY_LOCAL_MACHINE\SOFTWARE\Explorer2]
"Version"="1.0.0"
"InstallPath"="C:\\Program Files\\Explorer2"
"ConfigPath"="C:\\ProgramData\\Explorer2\\Config"

[HKEY_LOCAL_MACHINE\SOFTWARE\Explorer2\Mappers]
"Path"="C:\\ProgramData\\Explorer2\\Mappers"
"AutoLoad"=dword:00000001

[HKEY_LOCAL_MACHINE\SOFTWARE\Explorer2\Performance]
"InputThreads"=dword:00000004
"BatchSize"=dword:00000020
"MaxLatencyMs"=dword:00000001
```

### Configuration File

```xml
<!-- Explorer2.config -->
<configuration>
  <shell>
    <taskbar position="bottom" height="40" autohide="false" />
    <desktop showIcons="true" wallpaper="preserve" />
    <startMenu style="modern" />
  </shell>
  
  <input>
    <performance>
      <threading model="dedicated" count="4" />
      <batching enabled="true" size="32" />
      <latency target="1ms" />
    </performance>
    
    <devices>
      <enumeration interval="1000" />
      <persistence enabled="true" />
    </devices>
  </input>
  
  <domains>
    <isolation level="strict" />
    <switching animation="fade" duration="200" />
  </domains>
  
  <compatibility>
    <legacyBridge enabled="true" />
    <sendInput mode="hardware" />
    <hooks allowed="true" />
  </compatibility>
</configuration>
```

## Deployment

### MSI Installer Structure

```
Explorer2.msi
├── Program Files/
│   └── Explorer2/
│       ├── Explorer2.exe (signed)
│       ├── Explorer2.Core.dll
│       ├── Explorer2.Input.dll
│       ├── Explorer2.UI.dll
│       └── Mappers/
│           ├── Vim.dll
│           ├── Gaming.dll
│           └── Temporal.dll
├── ProgramData/
│   └── Explorer2/
│       ├── Config/
│       ├── Logs/
│       └── Mappers/
└── Registry entries
```

### Safety Features

1. **Automatic Fallback**: If Explorer2 crashes 3 times in 5 minutes, Windows Explorer is restored
2. **Safe Mode**: Hold Shift during boot to use Windows Explorer
3. **Recovery Command**: `explorer2 /restore` reverts to Windows Explorer
4. **Logging**: Comprehensive logging for debugging

## Conclusion

Explorer2 provides a complete shell replacement that:

1. **Captures all raw input** before any application sees it
2. **Maintains Windows compatibility** through careful system integration
3. **Enables revolutionary input routing** through the mapper pipeline
4. **Performs at native speed** through optimized processing
5. **Fails gracefully** with automatic recovery

This foundation enables the complete mapper/router system while keeping Windows stable and responsive. Users get a revolutionary input experience without sacrificing reliability.