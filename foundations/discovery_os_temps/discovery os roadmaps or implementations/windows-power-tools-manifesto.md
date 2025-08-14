# Windows 11 Power Tools: A Manifesto for Input Liberation and System Control

## Executive Summary

This document outlines a revolutionary suite of tools designed to transform Windows 11 from a single-user, rigidly-controlled operating system into a flexible, multi-user, power-user paradise. Through three interconnected but independent components—a Universal Input Router, an Advanced Window Manager, and a Process Priority Visualizer—we liberate computing from decades-old paradigms.

The core philosophy: **Every assumption about how we interact with computers is just a historical accident waiting to be questioned.**

Most remarkably, this software solution effectively transforms one physical computer into multiple independent workstations—each with its own keyboard, mouse, and monitor(s)—without virtualization overhead. A single powerful PC can serve an entire family, classroom, or office as if it were multiple separate computers.

---

## Table of Contents

1. [Vision: Computing Unchained](#vision-computing-unchained)
2. [Component 1: Universal Input Router](#component-1-universal-input-router)
3. [Component 2: Advanced Window Manager](#component-2-advanced-window-manager)
3. [Component 3: Process Priority Visualizer](#component-3-process-priority-visualizer)
5. [Integration Philosophy](#integration-philosophy)
6. [Revolutionary Use Cases](#revolutionary-use-cases)
7. [Technical Feasibility](#technical-feasibility)

---

## Vision: Computing Unchained

### The Problem Space

Modern operating systems trap us in assumptions from the 1980s:
- One keyboard, one mouse, one user
- Only Ctrl, Alt, Shift, and Win are "modifiers"
- Input goes to one program at a time
- Process priority is invisible and immutable
- Window management is mouse-centric
- Every program reinvents text editing

### The Solution Space

We propose a radical reimagining where:
- Any number of input devices serve any number of users on one machine
- Every key can be a modifier, every rhythm a command
- Input streams fork, merge, and transform freely
- Process priority becomes visible and interactive
- Navigation is modal, efficient, and consistent where possible
- Common input patterns work across applications

---

## Component 1: Universal Input Router

### Core Philosophy: Device-Aware Input Routing

Using Windows Raw Input API, we can identify specific devices and route their input to specific programs, regardless of window focus.

```
Raw Device Event → Router (where?) → Mapper (what?) → Target Program
```

### The Architecture

```
Device ID: 0x1234, ScanCode: 0x24, State: Down
              ↓
         [ROUTER RULES]
         ├→ Active Window (traditional behavior)
         ├→ Specific Program (device-locked)
         └→ Multiple Programs (multicast)
              ↓
    [MAPPER SELECTION PER TARGET]
    ├→ Raw Events (passthrough)
    ├→ Key Remapping (simple substitution)
    ├→ Macro Expansion (complex sequences)
    ├→ Context-Aware (program-specific)
    └→ Modal States (vim-like layers)
```

### Technical Implementation

**Raw Input Registration**
```cpp
RAWINPUTDEVICE rid[2];
rid[0].usUsagePage = 0x01;  // Generic Desktop
rid[0].usUsage = 0x06;      // Keyboard
rid[0].dwFlags = RIDEV_INPUTSINK | RIDEV_DEVNOTIFY;
rid[0].hwndTarget = hWnd;

RegisterRawInputDevices(rid, 2, sizeof(RAWINPUTDEVICE));
```

**Device Identification**
Each USB device has a unique hardware ID that persists across reboots:
- VID/PID for USB devices
- Instance path for differentiation
- Bluetooth devices have persistent IDs

### Input Transformation Pipeline

1. **Capture**: Raw Input API provides hardware events
2. **Route**: Determine target program(s) based on device
3. **Transform**: Apply mapper rules
4. **Inject**: Use appropriate method:
   - SendInput() for global injection
   - PostMessage() for specific windows
   - Hooks for intercepting existing input

### Key Innovations

#### 1. Per-Device Routing
```yaml
routing_rules:
  keyboard_1: 
    target: "code.exe"
    exclusive: true
  
  keyboard_2:
    target: "active_window"
    
  foot_pedals:
    targets: ["spotify.exe", "obs.exe"]
    mode: "multicast"
```

#### 2. Temporal Commands
Instead of chord combinations, use time-based patterns:
- Double-tap backslash within 100ms = command mode
- Hold for different durations = different commands
- Rhythmic patterns = complex macros

#### 3. Language-Aware Input
The router can maintain multiple keyboard layouts simultaneously:
```
Physical Key → Router → Multiple Interpretations
                 ↓
           Program receives:
           - US Layout: 'a'
           - Greek: 'α'  
           - Cyrillic: 'а'
```

### Realistic Mapper Types

1. **Simple Remapping**: Key A → Key B
2. **Macro Player**: Key sequence → Complex output
3. **Layer System**: Modal states like vim
4. **Auto-Switcher**: Context-based layout switching
5. **Rate Limiter**: Gaming-specific anti-cheat compliance

---

## Component 2: Advanced Window Manager

### Core Concept: Enhanced Window Control

Instead of replacing Windows' window manager (technically infeasible), we enhance it with:
- Keyboard-driven window manipulation
- Multi-monitor workspace management
- Device-specific focus rules
- Tiling window layouts

### Implementation Approach

**Window Manipulation via Windows API**
```cpp
// Move and resize windows programmatically
SetWindowPos(hwnd, HWND_TOP, x, y, width, height, SWP_SHOWWINDOW);

// Monitor enumeration for multi-monitor support
EnumDisplayMonitors(NULL, NULL, MonitorEnumProc, 0);

// Window focus management
SetForegroundWindow(hwnd);
SetFocus(hwnd);
```

### Key Features

#### 1. Keyboard-Driven Navigation
- Win+Number: Quick window switching
- Win+Arrows: Directional focus movement
- Custom hotkeys for window manipulation

#### 2. Virtual Desktops Enhancement
Extend Windows 11's virtual desktops:
- Per-monitor desktop switching
- Device-specific desktop affinity
- Programmatic desktop management

#### 3. Tiling Layouts
```cpp
// Automatic window tiling
void TileWindows(HMONITOR monitor, TilingMode mode) {
    RECT monitorRect = GetMonitorWorkArea(monitor);
    vector<HWND> windows = GetWindowsOnMonitor(monitor);
    
    switch(mode) {
        case TILE_VERTICAL:
            // Divide monitor vertically
            break;
        case TILE_GRID:
            // Create grid layout
            break;
    }
}
```

### Multi-User Window Management

**Monitor-Based User Zones**
```cpp
struct UserZone {
    vector<HMONITOR> monitors;
    RECT boundingBox;
    bool confineMouse;
    
    void ConfineCursor() {
        ClipCursor(&boundingBox);
    }
};
```

**Focus Isolation**
Each device can have independent focus:
- Keyboard 1 types into Window A
- Keyboard 2 types into Window B
- Both simultaneously, no focus switching

---

## Component 3: Process Priority Visualizer

### Realistic Scope: Visualization, Not Control

Windows kernel scheduling is not modifiable from userspace. Instead, we:
- Visualize current process priorities
- Show CPU usage and blocking relationships
- Allow priority adjustment within Windows limits
- Provide visual feedback for system behavior

### Implementation

**Process Information Gathering**
```cpp
// Enumerate processes
HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);

// Get process priority
HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, FALSE, pid);
DWORD priority = GetPriorityClass(hProcess);

// Monitor CPU usage via Performance Counters
PDH_HQUERY query;
PdhOpenQuery(NULL, 0, &query);
PdhAddCounter(query, L"\\Process(*)\\% Processor Time", 0, &counter);
```

**Visualization Components**
- D3.js or similar for interactive graphs
- Node = Process
- Edge = Resource dependency
- Size = CPU usage
- Color = Priority class

**User Interaction**
- Drag to request priority change
- Windows may or may not honor it
- Visual feedback shows actual vs requested

---

## Integration Philosophy

### Modular Architecture

Each component operates independently:
- Router works without window manager
- Window manager works without router
- Visualizer is purely observational

### Communication via Windows Messages

Components communicate through:
- Named pipes for IPC
- Custom Windows messages
- Shared memory for performance
- Registry for configuration

### No Kernel Drivers Required

Everything runs in userspace:
- Raw Input API for device access
- Windows API for window control
- Performance counters for monitoring
- No admin rights needed for basic features

---

## Revolutionary Use Cases

### The Multi-User Desktop
```
Family Computer Setup:
- Parent: Keyboard/Mouse 1 → Monitors 1-2
- Teen: Keyboard/Mouse 2 → Monitor 3
- Child: Keyboard/Mouse 3 → Monitor 4

Each has:
- Independent focus
- Confined mouse movement
- Personal workspace
```

### The Streaming Setup
```
Gaming Devices → Game (never loses focus)
Secondary Keyboard → OBS/Chat
Foot Pedals → Universal hotkeys
Eye Tracker → Window selection
```

### The Accessibility Solution
- Limited mobility: Foot pedals for common actions
- Repetitive strain: Distribute input across devices
- Visual impairment: Consistent keyboard navigation

### The Power User Workspace
- Primary keyboard: Current focus window
- Macro pad: Always controls specific apps
- Gaming mouse: Extra buttons for window management
- Touchpad: Gesture-based desktop switching

---

## Technical Feasibility

### What's Possible
✅ Device-specific input routing via Raw Input API  
✅ Window manipulation and tiling via Windows API  
✅ Process priority visualization  
✅ Multi-monitor management  
✅ Virtual desktop enhancement  
✅ Keyboard-driven navigation  
✅ Basic multi-user scenarios  

### What's Challenging
⚠️ True focus isolation (requires hooks)  
⚠️ Universal text navigation (limited by application)  
⚠️ Complete mouse confinement (security restrictions)  
⚠️ System-wide vim mode (needs per-app implementation)  

### What's Not Possible
❌ Kernel-level scheduling changes  
❌ Bypassing Windows security model  
❌ Universal font layer interception  
❌ Complete input isolation between users  

---

## Conclusion

This system transforms Windows from a single-user paradigm to a flexible, multi-device, potentially multi-user environment. By working within Windows' constraints while pushing its capabilities, we can achieve:

- Device-aware input routing
- Enhanced window management
- Visual system monitoring
- Improved accessibility
- Novel interaction patterns

The future isn't about replacing Windows—it's about unlocking its hidden potential.

---

*"The best tools don't fight the system; they transcend its limitations."*