# ForthOS: The Git-Native Operating System

## Philosophy: Everything is Source, Everything is Versioned

In ForthOS, there are no binaries, no hidden state, no black boxes. The entire operating system—from bootloader to window manager—exists as human-readable Forth source code in a git repository. Every change is tracked, every state is revertible, every branch is a complete system.

## Core Architecture

### The Boot Process

```forth
\ boot.forth - The entire OS starts here
: boot ( -- )
    git-init-kernel
    mount-root-as-git
    checkout-branch machine-state
    compile-kernel-words
    start-init ;

: git-init-kernel ( -- )
    s" /dev/sda1" git-open-repo
    s" HEAD" git-checkout
    kernel-vocabulary set-current ;

: compile-kernel-words ( -- )
    s" kernel/*.forth" git-ls-files
    BEGIN dup WHILE
        dup git-cat-file evaluate
        next-file
    REPEAT drop ;
```

### Everything is a Git Operation

```forth
\ Installing software
: install ( package-url -- )
    git-remote-add
    s" main" git-fetch
    git-diff-preview
    user-confirms? IF
        git-merge
        recompile-affected-words
    THEN ;

\ Example: Installing the input router
s" https://github.com/forthos/input-router" install

\ Creating a VM is creating a branch
: create-vm ( name -- )
    git-branch
    git-checkout
    customize-environment ;

\ Switching VMs
: switch-vm ( name -- )
    current-state git-commit
    git-checkout
    hot-reload-kernel ;
```

### The Filesystem is Git

```forth
\ No traditional filesystem - everything is git objects
: read-file ( path -- addr len )
    current-branch git-show ;

: write-file ( addr len path -- )
    git-hash-object
    git-update-index
    s" Auto-save" git-commit ;

\ Every file change is automatically versioned
: auto-commit-daemon ( -- )
    BEGIN
        file-change-detected? IF
            generate-commit-message git-commit
        THEN
        100 ms
    AGAIN ;
```

## System Components in Forth

### Memory Manager (10 lines)

```forth
variable heap-ptr  1MB heap-ptr !
: allocate ( n -- addr ) heap-ptr @ swap heap-ptr +! ;
: free ( addr -- ) drop ;  \ GC handles it
: gc ( -- ) mark-roots sweep ;
```

### Process Scheduler (15 lines)

```forth
create process-queue 1000 cells allot
variable current-process
variable quantum 10 constant

: schedule ( -- )
    process-queue @ 0= IF idle THEN
    process-queue dequeue current-process !
    current-process @ restore-context
    quantum set-timer ;

: yield ( -- )
    save-context current-process @
    current-process @ process-queue enqueue
    schedule ;

: spawn ( xt -- pid )
    next-pid allocate-process
    init-context process-queue enqueue ;
```

### Input Router in Forth

```forth
\ Device identification
: device-id ( device -- id )
    dup usb-vendor 16 lshift
    swap usb-product or ;

\ Routing table
create routing-table 256 cells allot
variable route-count

: add-route ( device target -- )
    route-count @ cells routing-table + 2!
    1 route-count +! ;

: route-input ( device event -- )
    over find-route ?dup IF
        send-to-target
    ELSE
        focused-window send-to-target
    THEN ;

\ Multi-user domains
: create-domain ( name -- domain )
    here >r
    0 , \ device list
    0 , \ monitor list  
    0 , \ routing rules
    r> ;

: assign-device-to-domain ( device domain -- )
    >device-list chain-add ;
```

### Window Manager

```forth
\ Tiling window manager in ~50 lines
variable window-list
variable master-size 60 constant

: tile-windows ( -- )
    count-windows CASE
        0 OF ENDOF
        1 OF maximize-single ENDOF
        2 OF split-half ENDOF
        split-master-stack
    ENDCASE ;

: split-master-stack ( -- )
    window-list @ master-window
    screen-width master-size * 100 / 
    screen-height position-window
    
    window-list @ next-window
    stack-area stack-count divide-among ;

: handle-key ( key -- )
    CASE
        [char] h OF focus-left ENDOF
        [char] j OF focus-down ENDOF
        [char] k OF focus-up ENDOF
        [char] l OF focus-right ENDOF
        [char] q OF close-window ENDOF
    ENDCASE ;
```

### Universal Vim Mode

```forth
\ Vim mode for any text area
variable vim-mode  0 constant normal  1 constant insert

: vim-key ( key -- )
    vim-mode @ CASE
        normal OF normal-mode-key ENDOF
        insert OF insert-mode-key ENDOF
    ENDCASE ;

: normal-mode-key ( key -- )
    CASE
        [char] i OF insert vim-mode ! ENDOF
        [char] h OF cursor-left ENDOF
        [char] j OF cursor-down ENDOF
        [char] k OF cursor-up ENDOF
        [char] l OF cursor-right ENDOF
        [char] d OF 
            last-key [char] d = IF delete-line THEN
        ENDOF
        [char] w OF word-forward ENDOF
        [char] b OF word-backward ENDOF
    ENDCASE
    dup last-key ! ;

\ Apply vim to any text widget
: vimify ( widget -- )
    ['] vim-key swap >key-handler ! ;
```

## Git-Based Features

### Time Travel Debugging

```forth
\ Debug by checking out earlier states
: debug-bisect ( test-word -- )
    s" HEAD" good-rev !
    s" HEAD~100" bad-rev !
    BEGIN
        bisect-midpoint git-checkout
        recompile-kernel
        test-word execute IF
            current-rev good-rev !
        ELSE
            current-rev bad-rev !
        THEN
        good-rev @ bad-rev @ 1 = 
    UNTIL
    bad-rev @ git-show ;

\ Example: When did input routing break?
: test-routing ( -- flag )
    test-keyboard-device test-mouse-device
    route-input 
    expected-target = ;

' test-routing debug-bisect
```

### Branch-Based User Isolation

```forth
\ Each user is a branch
: create-user ( name -- )
    s" main" git-checkout
    git-branch
    git-checkout
    default-user-environment ;

: login ( username password -- )
    authenticate IF
        current-state auto-commit
        username git-checkout
        load-user-environment
    THEN ;

\ User branches can merge updates
: update-user-system ( -- )
    s" origin/main" git-fetch
    git-merge-strategy 'user set
    git-merge ;
```

### Package Management via Git

```forth
\ No package manager needed - just git
: package-list ( -- )
    git-remote-list
    BEGIN dup WHILE
        dup git-remote-show
        cr type
        next-remote
    REPEAT drop ;

: update-all ( -- )
    git-remote-list
    BEGIN dup WHILE
        dup git-fetch
        git-merge-if-safe
        next-remote
    REPEAT drop
    full-recompile ;

\ Dependency resolution
: resolve-deps ( package -- )
    s" deps.forth" git-show evaluate ;
```

## System State as Commits

```forth
\ Every significant event is a commit
: commit-hooks ( -- )
    install-hook 'before-suspend ['] commit-state
    install-hook 'after-crash ['] commit-crash-dump
    install-hook 'user-switch ['] commit-user-state
    install-hook 'major-change ['] auto-snapshot ;

\ System logs are commit messages
: enhanced-commit ( message -- )
    here log-buffer !
    system-vitals append-log
    memory-usage append-log
    process-list append-log
    log-buffer @ git-commit-with-message ;
```

## Configuration as Code

```forth
\ User configuration
: config.forth ( -- )
    \ Input routing
    keyboard-1 domain-dad add-route
    mouse-1 domain-dad add-route
    monitors 1 2 domain-dad assign-monitors
    
    keyboard-2 domain-kid add-route
    mouse-2 domain-kid add-route  
    monitor 3 domain-kid assign-monitor
    
    \ Window manager
    'tile default-layout !
    10 window-gap !
    
    \ Vim everywhere
    ['] vim-key global-key-handler ! ;
```

## Performance Through Simplicity

```forth
\ JIT compilation for hot paths
: optimize-word ( word -- )
    usage-count 1000 > IF
        to-machine-code
        patch-references
    THEN ;

\ Minimal memory usage
: system-size ( -- n )
    s" .git/objects" du ;  \ ~50MB for complete OS

\ Fast boot via compilation cache
: cached-boot ( -- )
    last-compiled-state git-rev-parse
    current-state git-rev-parse
    = IF
        load-compiled-image  \ <1 second boot
    ELSE
        full-compile         \ ~5 second boot
    THEN ;
```

## Hardware Abstraction

```forth
\ Simple driver model
: driver ( name -- )
    create
        0 , \ init
        0 , \ read  
        0 , \ write
        0 , \ ioctl
    does> driver-dispatch ;

\ USB keyboard driver in ~20 lines
driver usb-keyboard
    :noname usb-enumerate-keyboards ; is init
    :noname usb-poll-keyboard ; is read
    :noname drop ; is write
    :noname usb-keyboard-ioctl ; is ioctl
```

## Multi-User Revolution

```forth
\ True multi-user via input domains
: family-computer ( -- )
    \ Each family member gets a git branch
    s" dad" create-user
    s" mom" create-user
    s" kid1" create-user
    s" kid2" create-user
    
    \ Devices auto-switch branches
    keyboard-1 'dad map-to-branch
    keyboard-2 'mom map-to-branch
    keyboard-3 'kid1 map-to-branch
    keyboard-4 'kid2 map-to-branch
    
    \ Shared applications via git worktrees
    s" shared-browser" git-worktree-add
    all-users shared-browser grant-access ;

\ Resource isolation via branches
: resource-limits ( user -- )
    CASE
        'kid1 OF 2GB memory-limit ! ENDOF
        'kid2 OF 1GB memory-limit ! ENDOF
        \ Parents get remaining resources
    ENDCASE ;
```

## Security Through Transparency

```forth
\ Every change is visible
: security-audit ( -- )
    git-log
    BEGIN dup WHILE
        dup suspicious-change? IF
            highlight-red cr
            git-show
        THEN
        next-commit
    REPEAT drop ;

\ Capability-based security
: grant-capability ( user capability -- )
    2dup permission-exists? not IF
        here >r
        user , capability , timestamp ,
        r> git-add
        s" Grant " user append capability append git-commit
    THEN ;
```

## The Complete System

```forth
\ The entire OS in one file hierarchy
repository/
├── boot.forth          \ ~50 lines
├── kernel/
│   ├── memory.forth    \ ~200 lines
│   ├── process.forth   \ ~300 lines
│   ├── drivers.forth   \ ~500 lines
│   └── git.forth       \ ~400 lines
├── system/
│   ├── router.forth    \ ~300 lines
│   ├── wm.forth        \ ~400 lines
│   └── shell.forth     \ ~200 lines
├── apps/
│   ├── editor.forth    \ ~500 lines
│   ├── browser.forth   \ ~1000 lines
│   └── terminal.forth  \ ~300 lines
└── users/
    ├── dad.forth       \ Personal config
    ├── mom.forth       \ Personal config
    └── kids.forth      \ Shared config

\ Total: ~5MB of source code = Complete OS
```

## Bootstrap Instructions

```bash
# Create bootable USB
git clone https://github.com/forthos/base
cd base
make-bootable /dev/sdb

# First boot
boot: git checkout main
boot: compile-all
boot: init

# System is now running
# Make any changes, they're automatically committed
# Break something? Just git checkout HEAD~1
```

## Philosophy Realized

1. **No Binaries**: Everything compiles from source on every boot (cached)
2. **Perfect History**: Every change tracked, nothing hidden
3. **Branches as VMs**: Zero-overhead isolation
4. **Git as Package Manager**: No special tools needed
5. **Time Travel**: Debug by binary searching history
6. **Multi-User**: Each user is a branch with their own state
7. **Transparent Security**: See every change, audit everything

## Conclusion

ForthOS proves that an entire operating system can be:
- Understandable (read the whole source in a day)
- Versioned (every state in git)
- Efficient (50MB for everything)
- Multi-user (via branches)
- Powerful (input routing, universal vim, etc.)

By building on two of computing's most elegant ideas—Forth and Git—we create an OS where experimentation is safe, understanding is possible, and control is absolute.

**The computer becomes a living document, not a black box.**

```forth
: fortune ( -- )
    s" In ForthOS, there are no users, only authors." type cr
    s" Every keystroke is a commit in the story of your system." type cr ;
```