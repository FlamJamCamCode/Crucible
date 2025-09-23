# SourceOS: Linux Where Everything Builds to Micro-VMs

## Core Concept: Every Application is a Reproducible VM

In SourceOS, we eliminate the distinction between applications and systems. Every program runs in its own micro-VM, built from source on-demand, with intelligent caching making it as fast as native execution.

## Architecture Overview

```yaml
# Instead of installing packages:
traditional: apt install firefox
sourceos: run firefox  # Builds micro-VM with exactly what firefox needs

# What actually happens:
1. Hash requested configuration
2. Check if VM image exists in cache
3. If not, build minimal VM with just required dependencies
4. Run application in isolated VM with ~0 overhead
5. Share identical layers between VMs (like Docker but deeper)
```

## The Source-First Package Format

```toml
# firefox.source.toml
[package]
name = "firefox"
version = "120.0"
source = "https://firefox-source.mozilla.org/firefox-120.0.tar.xz"

[build]
script = '''
./configure --enable-optimize --disable-debug
make -j$(nproc)
'''

[runtime]
kernel_features = ["NET", "SND", "DRM"]
devices = ["/dev/dri", "/dev/snd"]
filesystem = "overlayfs"
network = "user"

[dependencies]
gtk3 = { version = "3.24", features = ["wayland"] }
mesa = { version = "23.0", features = ["vulkan"] }

[integration]
input_router = true
vim_mode = "optional"
clipboard = "shared"
```

## Build System Architecture

### Deterministic VM Builder

```rust
// Every app builds to a micro-VM
pub struct VMBuilder {
    cache: ContentAddressableStore,
    compiler: DistccCluster,
}

impl VMBuilder {
    pub fn build(&self, spec: &PackageSpec) -> Result<VMImage> {
        let hash = spec.content_hash();
        
        // Check cache first
        if let Some(image) = self.cache.get(hash) {
            return Ok(image);
        }
        
        // Build minimal kernel
        let kernel = self.build_kernel(&spec.kernel_features)?;
        
        // Build userspace
        let rootfs = self.build_rootfs(&spec)?;
        
        // Create VM image
        let image = VMImage {
            kernel,
            rootfs,
            config: spec.runtime.clone(),
        };
        
        // Cache for next time
        self.cache.store(hash, &image);
        
        Ok(image)
    }
    
    fn build_kernel(&self, features: &[String]) -> Result<Kernel> {
        // Build minimal kernel with only required features
        let config = generate_minimal_config(features);
        
        // Distributed compilation
        self.compiler.compile_kernel(config)
    }
}
```

### Intelligent Caching System

```rust
// Content-addressable storage for all builds
pub struct CacheLayer {
    // Kernel cache - different feature combinations
    kernels: HashMap<FeatureSet, KernelImage>,
    
    // Library cache - shared between VMs
    libraries: HashMap<(Name, Version, Features), Library>,
    
    // Application cache - full VM images
    vms: HashMap<ConfigHash, VMImage>,
    
    // Layer cache - deduplication
    layers: ContentStore,
}

impl CacheLayer {
    // Smart sharing between VMs
    pub fn deduplicate(&mut self, vm1: &VMImage, vm2: &VMImage) {
        let common_layers = vm1.find_common_layers(vm2);
        
        for layer in common_layers {
            self.layers.refcount_increment(layer);
            vm1.replace_with_reference(layer);
            vm2.replace_with_reference(layer);
        }
    }
}
```

## Running Applications

### The `run` Command

```bash
# Traditional: binary in PATH
firefox

# SourceOS: builds and runs VM
run firefox

# With specific configuration
run firefox --with-profile=work --vim-mode=enabled

# With custom input routing
run firefox --input-domain=personal --keyboard=2
```

### Implementation

```rust
// The universal application runner
pub fn run(args: &Args) -> Result<()> {
    // Parse application request
    let spec = PackageSpec::from_args(args)?;
    
    // Build or retrieve VM
    let vm = VM_BUILDER.build(&spec)?;
    
    // Set up input routing
    if let Some(domain) = args.input_domain {
        INPUT_ROUTER.route_to_vm(&vm, domain);
    }
    
    // Launch with near-zero overhead
    let mut launcher = MicroVMLauncher::new();
    launcher.share_memory_with_host();
    launcher.use_virtio_fs();  // Instant file access
    launcher.enable_enlightenments();  // ~98% native performance
    
    launcher.run(vm)
}
```

### Micro-VM Technology

```c
// Minimal hypervisor for application VMs
struct microvm {
    // Shared memory with host - no copying
    struct shared_memory_region *memory;
    
    // Direct device assignment where possible
    struct assigned_devices *devices;
    
    // Enlightenments for near-native performance
    struct paravirt_ops *pvops;
    
    // Input routing integration
    struct input_domain *input;
};

// Launch time: ~50ms
// Memory overhead: ~10MB
// CPU overhead: ~2%
```

## Source-Based Configuration

### System Configuration as Code

```nix
# system.source.nix
{
  # Define the entire system
  system = {
    kernel = {
      version = "6.6";
      features = ["PREEMPT", "NO_HZ_FULL", "VFIO"];
      patches = [./gaming-latency.patch];
    };
    
    # Input router configuration
    input = {
      domains = {
        dad = {
          devices = ["keyboard:046D:C31C", "mouse:046D:C077"];
          monitors = [1, 2];
          default_apps = ["firefox-work", "vscode", "terminal"];
        };
        
        gaming = {
          devices = ["keyboard:1532:0221", "mouse:1532:0073"];
          monitors = [3];
          exclusive = true;
          direct_input = true;
        };
      };
    };
    
    # Applications to pre-build
    applications = {
      firefox-work = firefox.override {
        profile = ./work-profile;
        extensions = [vim-vixen ublock-origin];
        vim_mode = true;
      };
      
      vscode = vscode.override {
        extensions = [vim rust-analyzer];
        integrated_terminal = "zsh";
      };
    };
  };
}
```

### User Environments

```nix
# user-env.nix
{ pkgs, lib, ... }:
{
  # Each user gets their own environment
  users.dad = {
    # Applications built specifically for this user
    packages = [
      (firefox.withProfile ./dad-profile)
      (emacs.withConfig ./doom.d)
      (terminal.withShell "zsh")
    ];
    
    # Input routing
    input.domain = "dad";
    input.vim_everywhere = true;
    
    # VM templates
    vms = {
      work = {
        base = "ubuntu-22.04";
        packages = ["docker", "kubectl"];
        input.inherit = true;
      };
      
      banking = {
        base = "hardened-alpine";
        network = "isolated";
        clipboard = "disabled";
      };
    };
  };
}
```

## Git Integration

### Everything Versioned

```bash
# System configuration in git
cd /etc/sourceos
git init

# Track all changes
git add system.source.nix
git commit -m "Initial system"

# Atomic updates
git pull origin main
sourceos-rebuild switch

# Rollback
git checkout HEAD~1
sourceos-rebuild switch

# Compare systems
git diff HEAD~10 HEAD system.source.nix
```

### Build Cache as Git

```bash
# All builds are stored in git
/var/cache/sourceos/
├── .git/
├── kernels/
│   ├── 6.6-minimal-net/  # Each kernel config
│   └── 6.6-gaming/
├── vms/
│   ├── firefox-abc123/    # Content-addressed
│   └── firefox-def456/    # Different config
└── layers/
    └── gtk3-wayland/      # Shared components
```

## Advanced Features

### Cross-VM Input Routing

```rust
// Input router works across VMs
impl InputRouter {
    fn route_event(&mut self, device: DeviceID, event: InputEvent) {
        let target = self.routing_table.get(device);
        
        match target {
            Target::VM(vm_id) => {
                // Direct injection into VM
                self.vms[vm_id].inject_input(event);
            },
            Target::AllVMs(domain) => {
                // Broadcast to all VMs in domain
                for vm in self.domains[domain].vms() {
                    vm.inject_input(event.clone());
                }
            },
            Target::HostProcess(pid) => {
                // Or route to host process
                self.send_to_process(pid, event);
            }
        }
    }
}
```

### VM Checkpointing

```rust
// Instant save/restore of running applications
impl VM {
    fn checkpoint(&self) -> Checkpoint {
        Checkpoint {
            memory: self.memory.snapshot(),
            devices: self.devices.save_state(),
            timestamp: Instant::now(),
        }
    }
    
    fn restore(&mut self, checkpoint: Checkpoint) {
        self.memory.restore(checkpoint.memory);
        self.devices.restore(checkpoint.devices);
        // Continue running in <100ms
    }
}

// Usage
let checkpoint = firefox_vm.checkpoint();
// ... system update, reboot, whatever ...
firefox_vm.restore(checkpoint);  // Continue where you left off
```

### Smart Prebuilding

```rust
// Predictive building based on usage
struct PrebuildScheduler {
    usage_patterns: UsageDatabase,
    build_cluster: DistccCluster,
}

impl PrebuildScheduler {
    fn schedule(&self) {
        // Analyze usage patterns
        let predictions = self.usage_patterns.predict_next_24h();
        
        // Prebuild during idle time
        for (app, probability) in predictions {
            if probability > 0.7 {
                self.build_cluster.queue_build(app, Priority::Low);
            }
        }
    }
}
```

### Universal Vim Mode via VM Layer

```c
// Implement vim at hypervisor level
struct vm_vim_state {
    enum { NORMAL, INSERT, VISUAL } mode;
    struct key_buffer pending;
};

// Intercept all text rendering
void vm_text_render_hook(struct vm *vm, struct text_surface *surface) {
    if (vm->vim_enabled) {
        vim_analyze_surface(surface);
        vim_create_jump_targets(surface);
        vim_overlay_hints(surface);
    }
}

// Process keys before VM sees them
bool vm_input_filter(struct vm *vm, struct input_event *event) {
    if (vm->vim_enabled && vm->vim_state.mode != INSERT) {
        return vim_process_key(vm, event);
    }
    return false;  // Pass through
}
```

## Performance Optimizations

### Kernel Sharing

```rust
// Multiple VMs can share one kernel instance
struct SharedKernel {
    kernel: Arc<Kernel>,
    refcount: AtomicU32,
    features: FeatureSet,
}

// Only differences are in userspace
let firefox_vm = VM::new(shared_kernel.clone(), firefox_rootfs);
let chrome_vm = VM::new(shared_kernel.clone(), chrome_rootfs);
```

### Memory Deduplication

```c
// KSM on steroids - share identical pages between VMs
void deduplicate_vm_memory(struct vm *vm1, struct vm *vm2) {
    for (page in vm1->pages) {
        matching_page = find_matching_page(vm2, page);
        if (matching_page) {
            map_copy_on_write(page, matching_page);
            free_duplicate(page);
        }
    }
}
```

### Build Caching Network

```toml
# Distributed build cache
[cache]
local = "/var/cache/sourceos"
remote = [
    "https://cache.sourceos.org",
    "https://company-cache.local",
    "ipfs://community-cache"
]

# Share builds with others
[sharing]
upload_popular = true
min_uses_before_share = 3
```

## Use Cases

### Development Environment

```bash
# Each project gets its own VM
cd my-project
cat .sourceos.toml
```

```toml
[vm]
base = "debian-sid"
packages = ["gcc", "rust", "nodejs"]

[mount]
"/home/user/project" = "."

[network]
ports = [3000, 8080]

[input]
inherit_domain = true
```

```bash
# Just run - VM builds if needed
run .

# Now you're in a perfectly isolated dev environment
# With your keyboard/mouse domain preserved
```

### Gaming

```nix
# gaming.nix
{
  vms.gaming = {
    kernel = kernel.override {
      preempt = "full";
      timer_hz = 1000;
      no_debug = true;
    };
    
    gpu_passthrough = "/dev/dri/card1";
    cpu_pinning = [4, 5, 6, 7];  # Dedicated cores
    
    input = {
      devices = ["gaming-keyboard", "gaming-mouse"];
      exclusive = true;
      raw_mode = true;  # Bypass all processing
    };
  };
}
```

### Family Computer

```nix
# family.nix
{
  # Each family member gets isolated VMs
  users = {
    dad = {
      vms.browser = firefox.override { profile = "work"; };
      vms.development = vscode-environment;
    };
    
    kid1 = {
      vms.browser = firefox.override { 
        profile = "kids";
        content_filter = true;
      };
      vms.homework = libreoffice-environment;
      vms.gaming = minecraft-vm;
    };
  };
  
  # But they can share when needed
  shared.vms.movie-player = {
    package = vlc;
    input.domains = ["dad", "mom", "kid1", "kid2"];
    output.monitor = 4;  # Living room TV
  };
}
```

## Migration Path

### From Traditional Linux

```bash
# Import existing system
sourceos-import --from-debian

# Gradually convert packages
sourceos-convert firefox  # Now runs in VM
sourceos-convert chrome   # Another VM

# System still works normally
# But converted apps are isolated
```

### Comparison with Existing Tech

| Feature | Docker | Nix | Qubes | SourceOS |
|---------|--------|-----|-------|----------|
| Isolation | Process | None | VM | Micro-VM |
| Build from source | Sometimes | Yes | No | Always |
| Input routing | No | No | Basic | Advanced |
| Performance | ~95% | 100% | ~80% | ~98% |
| Storage efficiency | Good | Poor | Poor | Excellent |
| Configuration | Dockerfile | Nix | XML | Nix+ |

## Conclusion

SourceOS demonstrates that we can have:
- **Perfect isolation** without containers' limitations
- **Build-from-source** without compilation wait times
- **VM-per-app** without resource waste
- **Input routing** integrated at the deepest level
- **Git versioning** for the entire system

By building micro-VMs on-demand with intelligent caching, we get the best of all worlds: the isolation of Qubes, the reproducibility of Nix, the efficiency of containers, and the power of our input routing system.

Every application becomes a perfectly isolated, perfectly reproducible, perfectly controlled environment. And with ~98% native performance, there's no reason not to run everything this way.

**The future isn't containers or VMs—it's micro-VMs built from source, cached intelligently, and controlled completely.**