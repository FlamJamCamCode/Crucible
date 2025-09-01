# The Mapper Pipeline: Composable Input Transformation Architecture

## Overview

The Mapper Pipeline is the heart of the input transformation system. It processes raw hardware events through a series of composable mappers, each of which can transform, consume, buffer, or fork input events. This document details the complete implementation.

## Core Architecture

### Pipeline Flow

```
Raw Input → [Context Builder] → [Mapper Chain] → [Output Router] → Applications
                    ↓                ↓                   ↓
              [Context Data]   [Temporal Buffer]   [Legacy Bridge]
```

## Implementation

### 1. Core Pipeline Manager

```csharp
// MapperPipeline.cs - The main pipeline orchestrator
public class MapperPipeline : IDisposable
{
    private readonly List<IInputMapper> mappers = new();
    private readonly TemporalBuffer temporalBuffer = new();
    private readonly ContextEngine contextEngine = new();
    private readonly OutputRouter outputRouter = new();
    private readonly PipelineMetrics metrics = new();
    private readonly ReaderWriterLockSlim mapperLock = new();
    
    // Performance optimization: pre-compiled mapper chains
    private readonly Dictionary<ContextKey, MapperChain> compiledChains = new();
    
    public MapperPipeline()
    {
        // Initialize with core mappers
        RegisterMapper(new SystemCommandMapper(), MapperPriority.System);
        RegisterMapper(new DomainSwitchMapper(), MapperPriority.System);
        RegisterMapper(new EmergencyEscapeMapper(), MapperPriority.Highest);
    }
    
    public void RegisterMapper(IInputMapper mapper, MapperPriority priority = MapperPriority.Normal)
    {
        mapperLock.EnterWriteLock();
        try
        {
            // Insert mapper at correct position
            var insertIndex = mappers.FindIndex(m => m.Priority < priority);
            if (insertIndex == -1)
            {
                mappers.Add(mapper);
            }
            else
            {
                mappers.Insert(insertIndex, mapper);
            }
            
            // Invalidate compiled chains
            compiledChains.Clear();
            
            // Initialize mapper
            mapper.Initialize(this);
            
            Logger.Log($"Registered mapper: {mapper.Name} at priority {priority}");
        }
        finally
        {
            mapperLock.ExitWriteLock();
        }
    }
    
    public async Task<ProcessingResult> ProcessInputAsync(InputEvent input)
    {
        var startTime = Stopwatch.GetTimestamp();
        
        try
        {
            // Build context
            var context = await contextEngine.BuildContextAsync(input);
            
            // Get or compile mapper chain for this context
            var chain = GetOrCompileChain(context);
            
            // Process through chain
            var result = await chain.ProcessAsync(input, context);
            
            // Record metrics
            metrics.RecordProcessing(input, result, Stopwatch.GetTimestamp() - startTime);
            
            return result;
        }
        catch (Exception ex)
        {
            Logger.LogError($"Pipeline processing error: {ex.Message}", ex);
            return ProcessingResult.Error(ex);
        }
    }
    
    private MapperChain GetOrCompileChain(MapperContext context)
    {
        var key = context.GetCacheKey();
        
        if (compiledChains.TryGetValue(key, out var chain))
        {
            return chain;
        }
        
        // Compile new chain
        mapperLock.EnterReadLock();
        try
        {
            var applicableMappers = mappers
                .Where(m => m.IsActiveInContext(context))
                .ToList();
            
            chain = new MapperChain(applicableMappers);
            compiledChains[key] = chain;
            
            return chain;
        }
        finally
        {
            mapperLock.ExitReadLock();
        }
    }
}

// MapperChain.cs - Optimized chain of mappers
public class MapperChain
{
    private readonly IInputMapper[] mappers;
    private readonly bool hasTemporalMappers;
    private readonly bool hasStatefulMappers;
    
    public MapperChain(IList<IInputMapper> mapperList)
    {
        mappers = mapperList.ToArray();
        hasTemporalMappers = mappers.Any(m => m.Capabilities.HasFlag(MapperCapabilities.Temporal));
        hasStatefulMappers = mappers.Any(m => m.Capabilities.HasFlag(MapperCapabilities.Stateful));
    }
    
    public async Task<ProcessingResult> ProcessAsync(InputEvent input, MapperContext context)
    {
        var current = input;
        var outputs = new List<OutputEvent>();
        
        foreach (var mapper in mappers)
        {
            var result = await ProcessMapper(mapper, current, context);
            
            switch (result.Action)
            {
                case ResultAction.PassThrough:
                    // Continue to next mapper
                    continue;
                    
                case ResultAction.Transform:
                    // Use transformed events for remaining mappers
                    if (result.TransformedInputs?.Any() == true)
                    {
                        // Process each transformed input through remaining mappers
                        var remainingMappers = mappers.Skip(Array.IndexOf(mappers, mapper) + 1).ToArray();
                        foreach (var transformed in result.TransformedInputs)
                        {
                            var subChain = new MapperChain(remainingMappers);
                            var subResult = await subChain.ProcessAsync(transformed, context);
                            outputs.AddRange(subResult.Outputs);
                        }
                        return new ProcessingResult { Outputs = outputs };
                    }
                    
                    // Direct output events
                    outputs.AddRange(result.Outputs);
                    return new ProcessingResult { Outputs = outputs };
                    
                case ResultAction.Consume:
                    // Stop processing
                    return new ProcessingResult { Consumed = true };
                    
                case ResultAction.Buffer:
                    // Add to temporal buffer
                    TemporalBuffer.Instance.Add(current, result.BufferDuration, mapper);
                    return new ProcessingResult { Buffered = true };
                    
                case ResultAction.Fork:
                    // Process in parallel branches
                    var forkTasks = result.ForkBranches.Select(branch =>
                        ProcessBranch(branch, current, context)
                    );
                    var forkResults = await Task.WhenAll(forkTasks);
                    outputs.AddRange(forkResults.SelectMany(r => r.Outputs));
                    return new ProcessingResult { Outputs = outputs };
            }
        }
        
        // No mapper handled it - convert to legacy
        outputs.Add(ConvertToLegacy(current));
        return new ProcessingResult { Outputs = outputs };
    }
    
    private async Task<InputResult> ProcessMapper(IInputMapper mapper, InputEvent input, MapperContext context)
    {
        try
        {
            // Check device compatibility
            if (!mapper.CanHandleDevice(input.Device))
            {
                return InputResult.PassThrough();
            }
            
            // Process with timeout
            using var cts = new CancellationTokenSource(TimeSpan.FromMilliseconds(5));
            return await Task.Run(() => mapper.ProcessInput(input, context), cts.Token);
        }
        catch (OperationCanceledException)
        {
            Logger.LogWarning($"Mapper {mapper.Name} timed out");
            return InputResult.PassThrough();
        }
    }
}
```

### 2. Context Engine

```csharp
// ContextEngine.cs - Builds rich context for mappers
public class ContextEngine
{
    private readonly ApplicationDetector appDetector = new();
    private readonly WindowTracker windowTracker = new();
    private readonly UserProfileManager profileManager = new();
    private readonly SystemStateMonitor systemMonitor = new();
    private readonly InputHistoryTracker historyTracker = new();
    
    // Cache contexts for performance
    private readonly MemoryCache contextCache = new(new MemoryCacheOptions
    {
        SizeLimit = 1000,
        ExpirationScanFrequency = TimeSpan.FromSeconds(10)
    });
    
    public async Task<MapperContext> BuildContextAsync(InputEvent input)
    {
        // Try cache first
        var cacheKey = GenerateCacheKey(input);
        if (contextCache.TryGetValue<MapperContext>(cacheKey, out var cached))
        {
            return cached.WithUpdatedInput(input);
        }
        
        // Build new context
        var context = new MapperContext
        {
            Input = input,
            Timestamp = input.Timestamp,
            Device = await GetDeviceInfoAsync(input.Device),
            Domain = DomainManager.GetDomainForDevice(input.Device),
            User = profileManager.GetActiveUser(),
            Application = await appDetector.DetectApplicationAsync(),
            Window = windowTracker.GetActiveWindow(),
            System = systemMonitor.GetCurrentState(),
            History = historyTracker.GetRecentHistory(TimeSpan.FromSeconds(5))
        };
        
        // Enhanced context information
        context.Enhanced = new EnhancedContext
        {
            IsFullscreen = context.Window.IsFullscreen,
            IsGaming = await DetectGamingMode(context),
            ActiveModifiers = GetActiveModifiers(),
            CursorPosition = GetCursorPosition(),
            MonitorInfo = GetMonitorInfo(context.Window),
            NetworkLatency = systemMonitor.GetNetworkLatency(),
            SystemLoad = systemMonitor.GetSystemLoad()
        };
        
        // Cache with sliding expiration
        contextCache.Set(cacheKey, context, new MemoryCacheEntryOptions
        {
            Size = 1,
            SlidingExpiration = TimeSpan.FromMilliseconds(100)
        });
        
        return context;
    }
    
    private async Task<ApplicationInfo> DetectApplicationAsync()
    {
        var hwnd = GetForegroundWindow();
        if (hwnd == IntPtr.Zero) return ApplicationInfo.Desktop;
        
        // Get process info
        GetWindowThreadProcessId(hwnd, out uint pid);
        using var process = Process.GetProcessById((int)pid);
        
        var appInfo = new ApplicationInfo
        {
            ProcessId = pid,
            ProcessName = process.ProcessName,
            ExecutablePath = process.MainModule?.FileName,
            WindowHandle = hwnd,
            WindowTitle = GetWindowTitle(hwnd),
            WindowClass = GetWindowClass(hwnd)
        };
        
        // Detect application category
        appInfo.Categories = await CategoryDetector.DetectCategoriesAsync(appInfo);
        
        // Check for special applications
        if (GameDetector.IsGame(appInfo))
        {
            appInfo.Categories.Add("Game");
            appInfo.GameInfo = await GameDetector.GetGameInfoAsync(appInfo);
        }
        
        if (appInfo.ProcessName.Contains("Code") || appInfo.WindowClass.Contains("Editor"))
        {
            appInfo.Categories.Add("IDE");
        }
        
        return appInfo;
    }
}

// CategoryDetector.cs - Smart application categorization
public static class CategoryDetector
{
    private static readonly Dictionary<string, List<string>> ProcessCategories = new()
    {
        ["Game"] = new() { "game", "steam", "origin", "uplay", "epicgames" },
        ["Browser"] = new() { "chrome", "firefox", "edge", "opera", "brave" },
        ["IDE"] = new() { "devenv", "code", "idea", "eclipse", "sublime" },
        ["Communication"] = new() { "discord", "slack", "teams", "zoom", "skype" },
        ["Media"] = new() { "vlc", "spotify", "itunes", "winamp", "mpv" },
        ["Office"] = new() { "winword", "excel", "powerpoint", "outlook" },
        ["Graphics"] = new() { "photoshop", "illustrator", "gimp", "blender" },
        ["Terminal"] = new() { "cmd", "powershell", "wt", "conemu", "mintty" }
    };
    
    public static async Task<HashSet<string>> DetectCategoriesAsync(ApplicationInfo app)
    {
        var categories = new HashSet<string>();
        
        // Check process name patterns
        var processLower = app.ProcessName.ToLower();
        foreach (var (category, patterns) in ProcessCategories)
        {
            if (patterns.Any(p => processLower.Contains(p)))
            {
                categories.Add(category);
            }
        }
        
        // Check window title for hints
        if (app.WindowTitle.Contains(" - Visual Studio"))
            categories.Add("IDE");
        
        // Check for fullscreen games
        if (app.Window.IsFullscreen && await CheckGameHeuristics(app))
            categories.Add("Game");
        
        // Use ML model for unknown applications
        if (!categories.Any())
        {
            categories = await MLCategorizer.PredictCategoriesAsync(app);
        }
        
        return categories;
    }
}
```

### 3. Temporal Buffer System

```csharp
// TemporalBuffer.cs - Handles time-based input patterns
public class TemporalBuffer
{
    private readonly ConcurrentDictionary<BufferKey, BufferEntry> buffers = new();
    private readonly Timer cleanupTimer;
    private readonly Subject<TemporalPattern> patternDetected = new();
    
    public IObservable<TemporalPattern> PatternDetected => patternDetected;
    
    public TemporalBuffer()
    {
        // Cleanup expired buffers every 50ms
        cleanupTimer = new Timer(_ => CleanupExpired(), null, 50, 50);
    }
    
    public void Add(InputEvent input, TimeSpan duration, IInputMapper mapper)
    {
        var key = new BufferKey(mapper.Id, input.Device);
        
        buffers.AddOrUpdate(key,
            k => new BufferEntry
            {
                Events = new List<InputEvent> { input },
                StartTime = input.Timestamp,
                Duration = duration,
                Mapper = mapper
            },
            (k, existing) =>
            {
                existing.Events.Add(input);
                return existing;
            });
        
        // Check for pattern completion
        CheckPatterns(key);
    }
    
    private void CheckPatterns(BufferKey key)
    {
        if (!buffers.TryGetValue(key, out var entry)) return;
        
        var patterns = entry.Mapper.GetTemporalPatterns();
        
        foreach (var pattern in patterns)
        {
            if (MatchesPattern(entry.Events, pattern))
            {
                // Pattern matched!
                patternDetected.OnNext(new TemporalPattern
                {
                    Pattern = pattern,
                    Events = entry.Events.ToList(),
                    Mapper = entry.Mapper
                });
                
                // Clear buffer
                buffers.TryRemove(key, out _);
                return;
            }
        }
    }
    
    private bool MatchesPattern(List<InputEvent> events, ITemporalPattern pattern)
    {
        return pattern.Match(events);
    }
    
    private void CleanupExpired()
    {
        var now = Stopwatch.GetTimestamp();
        var expired = buffers
            .Where(kvp => IsExpired(kvp.Value, now))
            .Select(kvp => kvp.Key)
            .ToList();
        
        foreach (var key in expired)
        {
            if (buffers.TryRemove(key, out var entry))
            {
                // Flush expired events as individual inputs
                FlushBuffer(entry);
            }
        }
    }
    
    private void FlushBuffer(BufferEntry entry)
    {
        foreach (var evt in entry.Events)
        {
            // Send directly to output
            OutputRouter.Instance.RouteDirectly(evt);
        }
    }
}

// TemporalPattern.cs - Pattern definitions
public interface ITemporalPattern
{
    string Name { get; }
    bool Match(IList<InputEvent> events);
    OutputEvent[] GetOutput(IList<InputEvent> matchedEvents);
}

public class SequencePattern : ITemporalPattern
{
    public string Name { get; set; }
    public uint[] KeySequence { get; set; }
    public TimeSpan MaxInterval { get; set; }
    public OutputEvent Output { get; set; }
    
    public bool Match(IList<InputEvent> events)
    {
        if (events.Count < KeySequence.Length) return false;
        
        // Check if last N events match sequence
        var startIndex = events.Count - KeySequence.Length;
        
        for (int i = 0; i < KeySequence.Length; i++)
        {
            var evt = events[startIndex + i];
            
            // Check key match
            if (evt.RawCode != KeySequence[i]) return false;
            
            // Check timing
            if (i > 0)
            {
                var prevEvt = events[startIndex + i - 1];
                var interval = evt.Timestamp - prevEvt.Timestamp;
                if (interval > MaxInterval.Ticks) return false;
            }
        }
        
        return true;
    }
    
    public OutputEvent[] GetOutput(IList<InputEvent> matchedEvents)
    {
        return new[] { Output };
    }
}

public class RhythmPattern : ITemporalPattern
{
    public string Name { get; set; }
    public TimeSpan[] ExpectedIntervals { get; set; }
    public TimeSpan Tolerance { get; set; }
    public Func<InputEvent[], OutputEvent[]> OutputGenerator { get; set; }
    
    public bool Match(IList<InputEvent> events)
    {
        if (events.Count < ExpectedIntervals.Length + 1) return false;
        
        var startIndex = events.Count - ExpectedIntervals.Length - 1;
        
        for (int i = 0; i < ExpectedIntervals.Length; i++)
        {
            var interval = events[startIndex + i + 1].Timestamp - events[startIndex + i].Timestamp;
            var expected = ExpectedIntervals[i].Ticks;
            
            if (Math.Abs(interval - expected) > Tolerance.Ticks)
                return false;
        }
        
        return true;
    }
    
    public OutputEvent[] GetOutput(IList<InputEvent> matchedEvents)
    {
        return OutputGenerator(matchedEvents.ToArray());
    }
}
```

### 4. Mapper Implementations

#### Base Mapper Class

```csharp
// InputMapper.cs - Base class for all mappers
public abstract class InputMapper : IInputMapper
{
    public Guid Id { get; } = Guid.NewGuid();
    public abstract string Name { get; }
    public abstract string Description { get; }
    public virtual MapperPriority Priority => MapperPriority.Normal;
    public virtual MapperCapabilities Capabilities => MapperCapabilities.None;
    
    protected MapperPipeline Pipeline { get; private set; }
    protected IMapperConfig Config { get; private set; }
    
    public virtual void Initialize(MapperPipeline pipeline)
    {
        Pipeline = pipeline;
        LoadConfiguration();
    }
    
    public virtual void Configure(IMapperConfig config)
    {
        Config = config;
        OnConfigurationChanged();
    }
    
    public virtual bool CanHandleDevice(InputDevice device)
    {
        // Override to filter by device type
        return true;
    }
    
    public virtual bool IsActiveInContext(MapperContext context)
    {
        // Override to enable/disable based on context
        return true;
    }
    
    public abstract InputResult ProcessInput(InputEvent input, MapperContext context);
    
    protected virtual void LoadConfiguration()
    {
        var configPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "Explorer2", "Mappers", $"{GetType().Name}.json"
        );
        
        if (File.Exists(configPath))
        {
            var json = File.ReadAllText(configPath);
            Config = JsonSerializer.Deserialize<MapperConfig>(json);
        }
        else
        {
            Config = GetDefaultConfiguration();
        }
    }
    
    protected abstract IMapperConfig GetDefaultConfiguration();
    protected virtual void OnConfigurationChanged() { }
}
```

#### Modal Mapper Implementation

```csharp
// ModalMapper.cs - Provides modal input like vim
public class ModalMapper : InputMapper
{
    public override string Name => "Modal Input System";
    public override string Description => "Provides vim-like modal input with visual feedback";
    public override MapperCapabilities Capabilities => 
        MapperCapabilities.Stateful | MapperCapabilities.Visual;
    
    private Mode currentMode = Mode.Normal;
    private readonly ModeIndicator indicator = new();
    private readonly Dictionary<Mode, IModeHandler> handlers = new();
    
    public enum Mode
    {
        Normal,
        Insert,
        Visual,
        Command,
        Replace,
        Operator
    }
    
    public ModalMapper()
    {
        // Initialize mode handlers
        handlers[Mode.Normal] = new NormalModeHandler(this);
        handlers[Mode.Insert] = new InsertModeHandler(this);
        handlers[Mode.Visual] = new VisualModeHandler(this);
        handlers[Mode.Command] = new CommandModeHandler(this);
        handlers[Mode.Replace] = new ReplaceModeHandler(this);
        handlers[Mode.Operator] = new OperatorModeHandler(this);
    }
    
    public override InputResult ProcessInput(InputEvent input, MapperContext context)
    {
        // Let current mode handle input
        var result = handlers[currentMode].ProcessInput(input, context);
        
        // Handle mode changes
        if (result.NewMode.HasValue && result.NewMode.Value != currentMode)
        {
            ChangeMode(result.NewMode.Value);
        }
        
        return result;
    }
    
    private void ChangeMode(Mode newMode)
    {
        var oldMode = currentMode;
        currentMode = newMode;
        
        // Visual feedback
        indicator.ShowModeChange(oldMode, newMode);
        
        // Audio feedback
        if (Config.AudioFeedback)
        {
            AudioFeedback.PlayModeChange(newMode);
        }
        
        // Notify other systems
        ModeChanged?.Invoke(this, new ModeChangedEventArgs(oldMode, newMode));
    }
    
    public event EventHandler<ModeChangedEventArgs> ModeChanged;
}

// NormalModeHandler.cs - Handles normal mode input
public class NormalModeHandler : IModeHandler
{
    private readonly ModalMapper mapper;
    private readonly Dictionary<uint, Action<MapperContext>> keyBindings;
    private readonly MotionParser motionParser = new();
    
    public NormalModeHandler(ModalMapper mapper)
    {
        this.mapper = mapper;
        this.keyBindings = LoadKeyBindings();
    }
    
    public InputResult ProcessInput(InputEvent input, MapperContext context)
    {
        if (input.Type != InputType.Key || input.State != InputState.Down)
            return InputResult.PassThrough();
        
        // Check for mode switches
        switch (input.RawCode)
        {
            case Keys.I:
                return InputResult.ChangeMode(Mode.Insert);
                
            case Keys.V:
                return InputResult.ChangeMode(Mode.Visual);
                
            case Keys.Colon:
                return InputResult.ChangeMode(Mode.Command);
                
            case Keys.R:
                return InputResult.ChangeMode(Mode.Replace);
        }
        
        // Check motion commands
        var motion = motionParser.ParseMotion(input);
        if (motion != null)
        {
            return InputResult.Transform(
                new SemanticEvent
                {
                    ActionType = TextEditorActions.Navigate,
                    Data = motion
                }
            );
        }
        
        // Check key bindings
        if (keyBindings.TryGetValue(input.RawCode, out var action))
        {
            action(context);
            return InputResult.Consume();
        }
        
        return InputResult.PassThrough();
    }
}

// ModeIndicator.cs - Visual feedback for modes
public class ModeIndicator : IDisposable
{
    private readonly OverlayWindow overlay;
    private readonly AnimationEngine animator;
    
    public ModeIndicator()
    {
        overlay = new OverlayWindow
        {
            Width = 200,
            Height = 50,
            Opacity = 0
        };
        
        animator = new AnimationEngine();
    }
    
    public void ShowModeChange(Mode from, Mode to)
    {
        var color = GetModeColor(to);
        var text = GetModeText(to);
        
        overlay.SetContent(text, color);
        
        // Animate in
        animator.Animate(overlay, new Animation
        {
            Duration = TimeSpan.FromMilliseconds(150),
            Properties = new[]
            {
                new AnimationProperty("Opacity", 0, 0.9),
                new AnimationProperty("Scale", 0.8, 1.0)
            }
        });
        
        // Hold
        Task.Delay(1000).ContinueWith(_ =>
        {
            // Animate out
            animator.Animate(overlay, new Animation
            {
                Duration = TimeSpan.FromMilliseconds(150),
                Properties = new[]
                {
                    new AnimationProperty("Opacity", 0.9, 0),
                    new AnimationProperty("Scale", 1.0, 0.8)
                }
            });
        });
    }
    
    private Color GetModeColor(Mode mode) => mode switch
    {
        Mode.Normal => Color.Blue,
        Mode.Insert => Color.Green,
        Mode.Visual => Color.Orange,
        Mode.Command => Color.Purple,
        Mode.Replace => Color.Red,
        _ => Color.Gray
    };
    
    private string GetModeText(Mode mode) => mode switch
    {
        Mode.Normal => "-- NORMAL --",
        Mode.Insert => "-- INSERT --",
        Mode.Visual => "-- VISUAL --",
        Mode.Command => ":",
        Mode.Replace => "-- REPLACE --",
        _ => "-- ? --"
    };
}
```

#### Gaming Mapper

```csharp
// GamingMapper.cs - Optimized mapper for gaming
public class GamingMapper : InputMapper
{
    public override string Name => "Gaming Performance Mapper";
    public override string Description => "Ultra-low latency mapper for competitive gaming";
    public override MapperPriority Priority => MapperPriority.High;
    
    private readonly GameProfileManager profileManager = new();
    private readonly AntiCheatCompatibility antiCheat = new();
    private GameProfile activeProfile;
    
    public override bool IsActiveInContext(MapperContext context)
    {
        return context.Application.Categories.Contains("Game") ||
               context.Domain.IsGaming;
    }
    
    public override InputResult ProcessInput(InputEvent input, MapperContext context)
    {
        // Load game profile if needed
        if (activeProfile?.ProcessName != context.Application.ProcessName)
        {
            activeProfile = profileManager.GetProfile(context.Application);
        }
        
        // Direct passthrough for trusted games
        if (activeProfile.TrustLevel == TrustLevel.Full)
        {
            return InputResult.DirectInject(input);
        }
        
        // Check anti-cheat compatibility
        if (!antiCheat.IsCompatible(context.Application))
        {
            return InputResult.PassThrough();
        }
        
        // Apply game-specific mappings
        if (activeProfile.Mappings.TryGetValue(input.RawCode, out var mapping))
        {
            return InputResult.Transform(
                new LegacyEvent
                {
                    VirtualKey = mapping.VirtualKey,
                    ScanCode = mapping.ScanCode,
                    Flags = mapping.Flags | InputFlags.Hardware
                }
            );
        }
        
        // Performance optimization for mouse
        if (input.Device.Type == DeviceType.Mouse)
        {
            return ProcessMouseForGaming(input, context);
        }
        
        return InputResult.PassThrough();
    }
    
    private InputResult ProcessMouseForGaming(InputEvent input, MapperContext context)
    {
        // Apply profile settings
        var settings = activeProfile.MouseSettings;
        
        if (input.Mouse != null)
        {
            // Apply sensitivity
            var x = input.Mouse.X * settings.Sensitivity;
            var y = input.Mouse.Y * settings.Sensitivity;
            
            // Apply acceleration curve
            if (settings.AccelerationEnabled)
            {
                var velocity = Math.Sqrt(x * x + y * y);
                var accel = settings.AccelerationCurve.Evaluate(velocity);
                x *= accel;
                y *= accel;
            }
            
            // Apply angle snapping
            if (settings.AngleSnapping)
            {
                (x, y) = ApplyAngleSnapping(x, y, settings.SnapAngle);
            }
            
            return InputResult.Transform(
                new LegacyEvent
                {
                    Mouse = new MouseData
                    {
                        X = (int)x,
                        Y = (int)y,
                        Flags = MouseFlags.Move | MouseFlags.Absolute
                    }
                }
            );
        }
        
        return InputResult.PassThrough();
    }
}

// GameProfile.cs - Per-game configuration
public class GameProfile
{
    public string ProcessName { get; set; }
    public string GameTitle { get; set; }
    public TrustLevel TrustLevel { get; set; }
    public Dictionary<uint, KeyMapping> Mappings { get; set; }
    public MouseSettings MouseSettings { get; set; }
    public PerformanceSettings Performance { get; set; }
}

public class MouseSettings
{
    public float Sensitivity { get; set; } = 1.0f;
    public bool AccelerationEnabled { get; set; }
    public AnimationCurve AccelerationCurve { get; set; }
    public bool AngleSnapping { get; set; }
    public float SnapAngle { get; set; } = 15.0f;
    public int PollingRate { get; set; } = 1000;
    public bool RawInput { get; set; } = true;
}

// AntiCheatCompatibility.cs - Ensure we don't trigger anti-cheat
public class AntiCheatCompatibility
{
    private readonly HashSet<string> incompatibleProcesses = new()
    {
        "valorant", "riot", "vanguard",  // Riot Vanguard
        "easyanticheat", "eac",          // Easy Anti-Cheat
        "battleye", "be"                 // BattlEye
    };
    
    public bool IsCompatible(ApplicationInfo app)
    {
        // Check for known anti-cheat
        var processLower = app.ProcessName.ToLower();
        if (incompatibleProcesses.Any(p => processLower.Contains(p)))
        {
            return false;
        }
        
        // Check for kernel drivers
        if (HasKernelAntiCheat(app))
        {
            return false;
        }
        
        // Check signature
        return !IsProtectedProcess(app);
    }
    
    private bool HasKernelAntiCheat(ApplicationInfo app)
    {
        // Check for loaded kernel drivers
        var drivers = GetLoadedDrivers();
        return drivers.Any(d => 
            d.Contains("vgk.sys") ||      // Valorant
            d.Contains("easyanticheat") || // EAC
            d.Contains("battleye")         // BattlEye
        );
    }
}
```

### 5. Output Router

```csharp
// OutputRouter.cs - Routes processed events to destinations
public class OutputRouter
{
    private readonly LegacyBridge legacyBridge = new();
    private readonly SemanticDispatcher semanticDispatcher = new();
    private readonly DirectInjector directInjector = new();
    private readonly OutputMetrics metrics = new();
    
    public async Task RouteAsync(OutputEvent output)
    {
        var startTime = Stopwatch.GetTimestamp();
        
        try
        {
            switch (output)
            {
                case SemanticEvent semantic:
                    await RouteSemanticAsync(semantic);
                    break;
                    
                case LegacyEvent legacy:
                    await RouteLegacyAsync(legacy);
                    break;
                    
                case DirectInjectEvent direct:
                    await RouteDirectAsync(direct);
                    break;
                    
                default:
                    throw new NotSupportedException($"Unknown output type: {output.GetType()}");
            }
            
            metrics.RecordSuccess(output, Stopwatch.GetTimestamp() - startTime);
        }
        catch (Exception ex)
        {
            metrics.RecordFailure(output, ex);
            throw;
        }
    }
    
    private async Task RouteSemanticAsync(SemanticEvent semantic)
    {
        // Find target application
        var target = semantic.TargetDomain?.FocusedApplication 
                  ?? ApplicationTracker.GetForegroundApplication();
        
        // Check if app supports semantic input
        if (await semanticDispatcher.IsSemanticAware(target))
        {
            await semanticDispatcher.DispatchAsync(semantic, target);
        }
        else
        {
            // Convert to legacy for compatibility
            var legacy = await legacyBridge.ConvertToLegacyAsync(semantic, target);
            await RouteLegacyAsync(legacy);
        }
    }
    
    private async Task RouteLegacyAsync(LegacyEvent legacy)
    {
        // Use SendInput for compatibility
        var inputs = BuildInputArray(legacy);
        
        var result = SendInput(
            (uint)inputs.Length,
            inputs,
            Marshal.SizeOf(typeof(INPUT))
        );
        
        if (result != inputs.Length)
        {
            throw new Win32Exception(Marshal.GetLastWin32Error());
        }
    }
    
    private INPUT[] BuildInputArray(LegacyEvent legacy)
    {
        var inputs = new List<INPUT>();
        
        if (legacy.Keyboard != null)
        {
            inputs.Add(new INPUT
            {
                type = INPUT_KEYBOARD,
                ki = new KEYBDINPUT
                {
                    wVk = (ushort)legacy.Keyboard.VirtualKey,
                    wScan = (ushort)legacy.Keyboard.ScanCode,
                    dwFlags = ConvertFlags(legacy.Keyboard.Flags),
                    time = 0,
                    dwExtraInfo = GetMessageExtraInfo()
                }
            });
        }
        
        if (legacy.Mouse != null)
        {
            inputs.Add(new INPUT
            {
                type = INPUT_MOUSE,
                mi = new MOUSEINPUT
                {
                    dx = legacy.Mouse.X,
                    dy = legacy.Mouse.Y,
                    mouseData = legacy.Mouse.WheelDelta,
                    dwFlags = ConvertMouseFlags(legacy.Mouse.Flags),
                    time = 0,
                    dwExtraInfo = GetMessageExtraInfo()
                }
            });
        }
        
        return inputs.ToArray();
    }
}

// DirectInjector.cs - Bypass normal input for performance
public class DirectInjector
{
    private readonly Dictionary<IntPtr, InjectionMethod> methodCache = new();
    
    public async Task InjectAsync(DirectInjectEvent evt)
    {
        var method = GetInjectionMethod(evt.TargetWindow);
        
        switch (method)
        {
            case InjectionMethod.PostMessage:
                PostMessage(evt.TargetWindow, evt.Message, evt.WParam, evt.LParam);
                break;
                
            case InjectionMethod.SendMessage:
                await Task.Run(() => 
                    SendMessage(evt.TargetWindow, evt.Message, evt.WParam, evt.LParam)
                );
                break;
                
            case InjectionMethod.DirectWrite:
                await DirectWriteToProcess(evt);
                break;
        }
    }
    
    private InjectionMethod GetInjectionMethod(IntPtr hwnd)
    {
        if (methodCache.TryGetValue(hwnd, out var method))
            return method;
        
        // Detect best method for this window
        var className = GetWindowClass(hwnd);
        
        if (className.Contains("UnrealWindow"))
            method = InjectionMethod.DirectWrite;
        else if (className.Contains("Unity"))
            method = InjectionMethod.PostMessage;
        else
            method = InjectionMethod.SendMessage;
        
        methodCache[hwnd] = method;
        return method;
    }
}
```

### 6. Configuration System

```csharp
// MapperConfiguration.cs - Flexible configuration system
public interface IMapperConfig
{
    T GetValue<T>(string key, T defaultValue = default);
    void SetValue<T>(string key, T value);
    void Save();
    void Load();
}

public class JsonMapperConfig : IMapperConfig
{
    private readonly string configPath;
    private Dictionary<string, JsonElement> values = new();
    
    public JsonMapperConfig(string mapperName)
    {
        configPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
            "Explorer2", "Mappers", $"{mapperName}.json"
        );
        
        Load();
    }
    
    public T GetValue<T>(string key, T defaultValue = default)
    {
        if (values.TryGetValue(key, out var element))
        {
            try
            {
                return JsonSerializer.Deserialize<T>(element.GetRawText());
            }
            catch
            {
                return defaultValue;
            }
        }
        
        return defaultValue;
    }
    
    public void SetValue<T>(string key, T value)
    {
        var json = JsonSerializer.SerializeToElement(value);
        values[key] = json;
    }
    
    public void Save()
    {
        Directory.CreateDirectory(Path.GetDirectoryName(configPath));
        
        var json = JsonSerializer.Serialize(values, new JsonSerializerOptions
        {
            WriteIndented = true
        });
        
        File.WriteAllText(configPath, json);
    }
    
    public void Load()
    {
        if (!File.Exists(configPath))
        {
            values = new Dictionary<string, JsonElement>();
            return;
        }
        
        try
        {
            var json = File.ReadAllText(configPath);
            values = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(json) 
                  ?? new Dictionary<string, JsonElement>();
        }
        catch
        {
            values = new Dictionary<string, JsonElement>();
        }
    }
}

// MapperConfigUI.cs - Configuration UI
public class MapperConfigurationDialog : Form
{
    private readonly IInputMapper mapper;
    private readonly PropertyGrid propertyGrid;
    private readonly TabControl tabs;
    
    public MapperConfigurationDialog(IInputMapper mapper)
    {
        this.mapper = mapper;
        
        Text = $"Configure {mapper.Name}";
        Size = new Size(600, 400);
        
        tabs = new TabControl { Dock = DockStyle.Fill };
        
        // General tab
        var generalTab = new TabPage("General");
        propertyGrid = new PropertyGrid
        {
            Dock = DockStyle.Fill,
            SelectedObject = mapper.Config
        };
        generalTab.Controls.Add(propertyGrid);
        tabs.TabPages.Add(generalTab);
        
        // Add mapper-specific tabs
        mapper.CreateConfigurationTabs(tabs);
        
        Controls.Add(tabs);
        
        // Buttons
        var buttonPanel = new FlowLayoutPanel
        {
            Dock = DockStyle.Bottom,
            FlowDirection = FlowDirection.RightToLeft,
            Height = 40
        };
        
        var okButton = new Button { Text = "OK", DialogResult = DialogResult.OK };
        var cancelButton = new Button { Text = "Cancel", DialogResult = DialogResult.Cancel };
        var applyButton = new Button { Text = "Apply" };
        
        applyButton.Click += (s, e) => ApplyConfiguration();
        
        buttonPanel.Controls.AddRange(new[] { okButton, cancelButton, applyButton });
        Controls.Add(buttonPanel);
    }
    
    private void ApplyConfiguration()
    {
        mapper.Config.Save();
        mapper.Configure(mapper.Config);
    }
}
```

### 7. Performance Monitoring

```csharp
// PipelineMetrics.cs - Track pipeline performance
public class PipelineMetrics
{
    private readonly MetricsCollector collector = new();
    private readonly ConcurrentDictionary<string, Histogram> histograms = new();
    
    public void RecordProcessing(InputEvent input, ProcessingResult result, long ticks)
    {
        var latencyMs = TicksToMs(ticks);
        
        // Record overall latency
        GetHistogram("pipeline.latency").Record(latencyMs);
        
        // Record per-device latency
        GetHistogram($"device.{input.Device.Type}.latency").Record(latencyMs);
        
        // Record per-mapper metrics
        foreach (var mapperTime in result.MapperTimings)
        {
            GetHistogram($"mapper.{mapperTime.MapperName}.latency")
                .Record(TicksToMs(mapperTime.Ticks));
        }
        
        // Count events
        collector.IncrementCounter("pipeline.events.total");
        
        if (result.Consumed)
            collector.IncrementCounter("pipeline.events.consumed");
        else if (result.Transformed)
            collector.IncrementCounter("pipeline.events.transformed");
        else
            collector.IncrementCounter("pipeline.events.passthrough");
    }
    
    public PipelineStats GetStats()
    {
        return new PipelineStats
        {
            TotalEvents = collector.GetCounter("pipeline.events.total"),
            AverageLatencyMs = GetHistogram("pipeline.latency").Mean,
            P99LatencyMs = GetHistogram("pipeline.latency").GetPercentile(0.99),
            P95LatencyMs = GetHistogram("pipeline.latency").GetPercentile(0.95),
            EventsPerSecond = CalculateRate("pipeline.events.total"),
            MapperStats = GetMapperStats()
        };
    }
    
    private Dictionary<string, MapperStats> GetMapperStats()
    {
        return histograms
            .Where(kvp => kvp.Key.StartsWith("mapper."))
            .Select(kvp =>
            {
                var mapperName = kvp.Key.Split('.')[1];
                return new
                {
                    Name = mapperName,
                    Stats = new MapperStats
                    {
                        AverageLatencyMs = kvp.Value.Mean,
                        P99LatencyMs = kvp.Value.GetPercentile(0.99),
                        CallCount = kvp.Value.Count
                    }
                };
            })
            .ToDictionary(x => x.Name, x => x.Stats);
    }
}

// Real-time performance dashboard
public class PerformanceDashboard : Form
{
    private readonly PipelineMetrics metrics;
    private readonly Timer updateTimer;
    private readonly LiveChart latencyChart;
    private readonly Label statsLabel;
    
    public PerformanceDashboard(PipelineMetrics metrics)
    {
        this.metrics = metrics;
        
        Text = "Input Pipeline Performance";
        Size = new Size(800, 600);
        
        // Create UI
        var splitContainer = new SplitContainer
        {
            Dock = DockStyle.Fill,
            Orientation = Orientation.Horizontal
        };
        
        // Charts
        latencyChart = new LiveChart
        {
            Title = "Input Latency (ms)",
            MaxPoints = 300,
            YAxisMax = 10
        };
        splitContainer.Panel1.Controls.Add(latencyChart);
        
        // Stats
        statsLabel = new Label
        {
            Dock = DockStyle.Fill,
            Font = new Font("Consolas", 10),
            ForeColor = Color.LightGreen,
            BackColor = Color.Black
        };
        splitContainer.Panel2.Controls.Add(statsLabel);
        
        Controls.Add(splitContainer);
        
        // Update timer
        updateTimer = new Timer { Interval = 100 };
        updateTimer.Tick += UpdateDisplay;
        updateTimer.Start();
    }
    
    private void UpdateDisplay(object sender, EventArgs e)
    {
        var stats = metrics.GetStats();
        
        // Update chart
        latencyChart.AddPoint(stats.AverageLatencyMs);
        
        // Update stats
        var sb = new StringBuilder();
        sb.AppendLine($"Total Events: {stats.TotalEvents:N0}");
        sb.AppendLine($"Events/sec: {stats.EventsPerSecond:F1}");
        sb.AppendLine($"Avg Latency: {stats.AverageLatencyMs:F2}ms");
        sb.AppendLine($"P95 Latency: {stats.P95LatencyMs:F2}ms");
        sb.AppendLine($"P99 Latency: {stats.P99LatencyMs:F2}ms");
        sb.AppendLine();
        sb.AppendLine("Mapper Performance:");
        
        foreach (var (name, mapperStats) in stats.MapperStats.OrderBy(x => x.Key))
        {
            sb.AppendLine($"  {name}: {mapperStats.AverageLatencyMs:F2}ms " +
                         $"(calls: {mapperStats.CallCount:N0})");
        }
        
        statsLabel.Text = sb.ToString();
    }
}
```

## Usage Examples

### Creating a Custom Mapper

```csharp
// CustomMacroMapper.cs - Example custom mapper
public class CustomMacroMapper : InputMapper
{
    public override string Name => "Custom Macro System";
    public override string Description => "User-defined macro mappings";
    
    private Dictionary<uint, Macro> macros = new();
    
    public override InputResult ProcessInput(InputEvent input, MapperContext context)
    {
        if (input.Type != InputType.Key || input.State != InputState.Down)
            return InputResult.PassThrough();
        
        if (macros.TryGetValue(input.RawCode, out var macro))
        {
            return ExecuteMacro(macro, context);
        }
        
        return InputResult.PassThrough();
    }
    
    private InputResult ExecuteMacro(Macro macro, MapperContext context)
    {
        var outputs = new List<OutputEvent>();
        
        foreach (var action in macro.Actions)
        {
            switch (action)
            {
                case KeyAction key:
                    outputs.Add(new LegacyEvent
                    {
                        Keyboard = new KeyboardData
                        {
                            VirtualKey = key.VirtualKey,
                            State = key.State
                        }
                    });
                    break;
                    
                case DelayAction delay:
                    outputs.Add(new DelayEvent { Duration = delay.Duration });
                    break;
                    
                case TextAction text:
                    outputs.AddRange(ConvertTextToKeys(text.Text));
                    break;
            }
        }
        
        return InputResult.Transform(outputs.ToArray());
    }
}
```

### Registering Mappers

```csharp
// In Explorer2 initialization
var pipeline = new MapperPipeline();

// Register system mappers
pipeline.RegisterMapper(new EmergencyEscapeMapper(), MapperPriority.Highest);
pipeline.RegisterMapper(new DomainSwitchMapper(), MapperPriority.System);

// Register feature mappers
pipeline.RegisterMapper(new ModalMapper(), MapperPriority.High);
pipeline.RegisterMapper(new TemporalMapper(), MapperPriority.High);
pipeline.RegisterMapper(new GamingMapper(), MapperPriority.High);

// Register user mappers
foreach (var mapperPath in Directory.GetFiles(mappersDir, "*.dll"))
{
    var mapper = LoadMapper(mapperPath);
    pipeline.RegisterMapper(mapper);
}
```

## Conclusion

The Mapper Pipeline provides:

1. **Composable Architecture** - Stack mappers like LEGO blocks
2. **High Performance** - Sub-millisecond processing with smart optimization
3. **Rich Context** - Mappers have full awareness of system state
4. **Temporal Awareness** - Pattern detection across time
5. **Modal Flexibility** - Different input modes for different contexts
6. **Gaming Compatibility** - Works with anti-cheat systems
7. **Visual Feedback** - Users always know what mode they're in
8. **Easy Extension** - Anyone can write custom mappers

This system transforms raw hardware events into semantic intentions, enabling revolutionary input experiences while maintaining compatibility with all existing Windows applications.