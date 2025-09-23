# Making Windows Better: A User's Guide to Input Liberation

## What You Can Build Today on Windows

### Overview
This guide shows how to implement the revolutionary input system concepts on Windows using available tools and APIs—no kernel drivers needed. Transform your single PC into a multi-user powerhouse with intelligent input routing.

## Core Components You Can Build

### 1. Input Router (Using Interception Driver)

```cpp
// Built on Oblita's signed Interception driver
class InputRouter {
    InterceptionContext context;
    std::map<InterceptionDevice, TargetProgram> routingTable;
    
public:
    void Initialize() {
        context = interception_create_context();
        EnumerateDevices();
        LoadRoutingRules();
    }
    
    void RouteInput() {
        InterceptionDevice device;
        InterceptionStroke stroke;
        
        while (interception_receive(context, device, &stroke, 1) > 0) {
            if (ShouldRoute(device)) {
                SendToTarget(routingTable[device], stroke);
            } else {
                interception_send(context, device, &stroke, 1);
            }
        }
    }
};
```

### 2. Window Manager (AutoHotkey + DLL)

```autohotkey
; Scancode-based for layout independence
#Include Interception.ahk

; User workspaces
global Users := {
    "Dad": {
        keyboard: "HID\VID_046D&PID_C52B",
        mouse: "HID\VID_046D&PID_C077", 
        monitors: [1, 2],
        workspace: 1
    },
    "Kid": {
        keyboard: "HID\VID_413C&PID_2003",
        mouse: "HID\VID_1BCF&PID_0005",
        monitors: [3],
        workspace: 2
    }
}

; Confine mouse to user's monitors
ConfineMouse(user) {
    monitors := Users[user].monitors
    bounds := GetMonitorBounds(monitors)
    ClipCursor(bounds)
}

; Route keyboard to user's workspace
RouteKeyboard(device, key) {
    user := GetUserByDevice(device)
    if (user) {
        SetActiveWorkspace(Users[user].workspace)
        SendInput(key)
    }
}
```

### 3. Universal Vim Mode (UI Automation)

```csharp
// C# implementation using UI Automation
public class UniversalVim {
    private readonly Dictionary<IntPtr, VimState> windowStates;
    
    public void HookWindow(IntPtr hwnd) {
        var element = AutomationElement.FromHandle(hwnd);
        var textPattern = element.GetCurrentPattern(TextPattern.Pattern);
        
        windowStates[hwnd] = new VimState {
            Mode = VimMode.Normal,
            TextPattern = textPattern
        };
    }
    
    public void ProcessKey(IntPtr hwnd, Key key) {
        var state = windowStates[hwnd];
        
        switch (state.Mode) {
            case VimMode.Normal:
                ProcessNormalMode(state, key);
                break;
            case VimMode.Insert:
                // Pass through
                break;
            case VimMode.Visual:
                ProcessVisualMode(state, key);
                break;
        }
    }
    
    private void ProcessNormalMode(VimState state, Key key) {
        switch (key) {
            case Key.H: MoveCursor(state, Direction.Left); break;
            case Key.J: MoveCursor(state, Direction.Down); break;
            case Key.K: MoveCursor(state, Direction.Up); break;
            case Key.L: MoveCursor(state, Direction.Right); break;
            case Key.I: state.Mode = VimMode.Insert; break;
            case Key.D: 
                if (state.LastKey == Key.D) DeleteLine(state);
                break;
        }
        state.LastKey = key;
    }
}
```

### 4. Multi-User Configuration UI

```csharp
// WPF configuration interface
public partial class RouterConfig : Window {
    public void SetupUserProfile() {
        // Visual device assignment
        var devices = InputDevice.EnumerateAll();
        
        foreach (var device in devices) {
            DeviceList.Items.Add(new DeviceItem {
                Name = device.FriendlyName,
                ID = device.HardwareID,
                Type = device.Type,
                AssignedUser = GetAssignment(device)
            });
        }
    }
    
    private void AssignDeviceToUser(InputDevice device, User user) {
        RouterService.UpdateRouting(new RoutingRule {
            DeviceID = device.HardwareID,
            Target = RoutingTarget.Workspace,
            WorkspaceID = user.WorkspaceID,
            MouseConfinement = user.MonitorBounds
        });
    }
}
```

## Practical Implementations

### The Family Computer Setup

```yaml
# config.yaml
users:
  parent1:
    devices:
      keyboard: "USB\VID_046D&PID_C31C"
      mouse: "USB\VID_046D&PID_C077"
    monitors: [1, 2]
    shortcuts:
      "\\terminal": "wt.exe"
      "\\browser": "firefox.exe"
    
  child1:
    devices:
      keyboard: "USB\VID_413C&PID_2003"
      mouse: "USB\VID_1BCF&PID_0005"
    monitors: [3]
    restrictions:
      allowed_programs: ["education.exe", "minecraft.exe"]
      time_limits: "9:00-21:00"

routing:
  exclusive_mode: true
  mouse_confinement: true
  workspace_isolation: true
```

### The Power User Setup

```python
# mapper_config.py
mappers = {
    "vim_everywhere": {
        "type": "vim",
        "programs": ["*"],
        "leader": "\\",
        "timeout_ms": 100
    },
    
    "code_snippets": {
        "type": "snippet", 
        "programs": ["code.exe", "notepad++.exe"],
        "expansions": {
            "forr": "for (int i = 0; i < |; i++)",
            "iff": "if (|) {\n    \n}",
            "classs": "class | {\npublic:\n    |();\n};"
        }
    },
    
    "media_control": {
        "type": "media",
        "device": "foot_pedals",
        "mappings": {
            "left": {"target": "youtube_tab_1", "action": "playpause"},
            "right": {"target": "spotify.exe", "action": "next"}
        }
    }
}
```

## Installation Guide

### Prerequisites
1. **Interception Driver**
   ```bash
   # Download and install Interception
   install-interception.exe /install
   ```

2. **Visual C++ Runtime**
   - Required for the router service

3. **AutoHotkey v2**
   - For window management scripts

### Basic Setup

1. **Install Core Components**
   ```powershell
   # Run as Administrator
   .\install-router-service.ps1
   .\register-mappers.ps1
   ```

2. **Configure Users**
   - Run `RouterConfig.exe`
   - Plug in each user's devices
   - Assign to workspaces
   - Set monitor boundaries

3. **Test Configuration**
   ```powershell
   # Verify routing
   Test-InputRouting -Device "keyboard1" -Target "workspace1"
   ```

## Advanced Features

### Temporal Commands

```cpp
class TemporalCommands {
    std::chrono::milliseconds timeout{100};
    std::string buffer;
    
    void ProcessKey(char key) {
        if (key == '\\') {
            if (buffer == "\\") {
                // Double backslash - command mode
                ShowCommandPalette();
            } else {
                buffer = "\\";
                StartTimer();
            }
        } else if (!buffer.empty()) {
            buffer += key;
            CheckCommand();
        }
    }
    
    void CheckCommand() {
        if (buffer == "\\ytp") {
            SendToProgram("youtube.exe", "space"); // play/pause
        } else if (buffer == "\\term") {
            LaunchProgram("wt.exe");
        }
        buffer.clear();
    }
};
```

### Gaming Mode

```cpp
// Low-latency gaming mapper
class GamingMapper {
    HANDLE gameProcess;
    
    void RouteToGame(InputEvent event) {
        // Skip Windows message queue
        INPUT input = ConvertToInput(event);
        
        // Direct injection
        SetForegroundWindow(gameWindow); // One-time setup
        SendInput(1, &input, sizeof(INPUT));
        
        // Or use PostMessage for some games
        PostMessage(gameWindow, WM_KEYDOWN, event.vkey, 0);
    }
};
```

## Troubleshooting

### Common Issues

1. **"Access Denied" errors**
   - Run as Administrator
   - Disable Secure Boot if needed

2. **Input lag**
   - Disable Windows Defender real-time scanning for router
   - Use Performance power plan

3. **Device not recognized**
   - Check Device Manager for hardware IDs
   - Use `listdev.exe` to enumerate devices

### Performance Optimization

```ini
# router.ini
[Performance]
UseRawInput=true
PollingRate=1000
BufferSize=64
Priority=Realtime

[Logging]
Enabled=false  # Disable for performance
```

## Real-World Examples

### Multi-User Family PC

**Morning Routine:**
- Mom: Monitors 1-2 for work email
- Dad: Monitor 3 for news
- Kid: Monitor 4 for online school

All simultaneously, no conflicts!

### Streamer Setup

```yaml
devices:
  gaming_keyboard:
    target: "game.exe"
    mode: "exclusive"
    
  streaming_keyboard:
    targets: ["obs.exe", "chat.exe"]
    mode: "shared"
    
  foot_pedals:
    left: "toggle_mic"
    right: "scene_switch"
```

### Developer Workflow

```python
# Foot pedal navigation
pedal_config = {
    "tap": "build_project",
    "hold": "run_tests",
    "double_tap": "commit_changes",
    "left_right": "switch_branch"
}
```

## Community Resources

- **Mapper Library**: Share your custom mappers
- **Device Profiles**: Pre-configured popular devices
- **Layout Templates**: Multi-user configurations
- **Discord**: Support and showcases

## Limitations and Workarounds

### What Works Well
- ✅ Multiple keyboards/mice routing
- ✅ Monitor confinement
- ✅ Basic vim emulation
- ✅ Temporal commands
- ✅ Gaming with acceptable latency

### Current Limitations
- ⚠️ Some anticheat systems may flag input
- ⚠️ UWP apps need special handling
- ⚠️ Admin rights required
- ⚠️ No kernel-level isolation

### Workarounds
- Use windowed mode for problematic games
- Run UWP apps in compatibility mode
- Schedule tasks to auto-start as admin
- Use process-level separation for security

## Future Roadmap

1. **Plugin System**
   - Community mappers
   - Visual configuration
   - Hot-reload support

2. **Better Integration**
   - Windows Hello for user switching
   - PowerToys integration
   - Stream Deck support

3. **Performance**
   - GPU-accelerated routing
   - Predictive caching
   - Lower latency modes

## Conclusion

While we can't achieve the full dream on Windows due to kernel restrictions, this implementation provides:
- 80% of the multi-user vision
- 90% of input routing capability  
- 100% of the economic benefit

One PC truly can serve a whole family. Your keyboard becomes your identity. Every program can have vim bindings. It's not perfect, but it's revolutionary enough to change how you compute.

Start small—route one extra keyboard. Then add family members. Before long, you'll wonder how you ever lived with Windows' single-user assumption.

The future of computing isn't waiting for Microsoft. We're building it ourselves, one routed input at a time.