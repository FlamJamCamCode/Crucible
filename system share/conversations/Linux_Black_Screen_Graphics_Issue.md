# Linux Black Screen Graphics Issue

**Created:** 2025-07-16 08:36:26 UTC  
**Updated:** 2025-07-16 10:14:56 UTC

**User:** MagMaM (boyantflam885@gmail.com)

---

## Unknown

Puzzle for you. You're a tech supporter. Customer calls. They have started their linux computer and one of the graphics cards show only black screens. They're registered in the xrandr or xfce display settings. And the mouse is able to move freely upon them. However no windows or background images or panels render onto them.

What is the problem?

---

## Unknown



Interesting puzzle! This sounds like a compositor or GPU driver issue. Before I dive into research on this problem, let me clarify a few things to narrow down the possibilities:

1. Is this a multi-GPU setup (e.g., integrated + dedicated, or multiple dedicated GPUs)? And if so, which GPU is having the black screen issue?

2. What GPU drivers are you using (nvidia proprietary, nouveau, amdgpu, etc.) and did this issue start after a recent driver update or system update?

3. Can you switch to a TTY (Ctrl+Alt+F2) on the affected displays, or are they completely black even outside of the graphical session?

These details will help me research the most relevant solutions for your specific setup!

---

## Unknown

Customer responds:
1. AMD and nVidia card. nVidia screens are the black ones.
2. Customer needs step by step guide to answer your questions.
3. TTYs are black as well on nvidia but they have terminals on all amd exits.

---

## Unknown



Got it - this is a classic Nvidia driver issue on Linux with a mixed GPU setup. Since the TTYs are also black on the Nvidia outputs, this points to a deeper driver or kernel mode setting problem. Let me research the most effective troubleshooting steps for this specific scenario.



Your Linux Nvidia black screen troubleshooting guide is ready. It covers driver status verification, common causes in dual GPU systems, kernel mode setting solutions, Xorg configuration for mixed setups, driver conflict diagnosis methods, and practical recovery procedures. The guide includes specific commands, configuration examples, and solutions focused on AMD/Nvidia hybrid systems experiencing black screens with visible cursors.

---

## Unknown

nvidia-smi not available. drivers have no proprietary nvidia drivers and there will not be installed any by principle. All changes has to be "hacks" not software updates. Tinkering to fix it.

lsmod info
iommu_v2, gpu_sched, drm_buddy show only amdgpu
mxm_wmi only nouveau; and wmi shows only video, wmi_bmof, mxm_wmi, nouveau

The rest has both like video, drm_ttm_helper, ttm, drm_display_helper shows amdgpu, nouveau

In terms of claiming or non-claiming more step by step is needed.

The login screen was nvidia then once past logging in it switched to amdgpu. At "8.033579 fbcon: amdgpudrmfb (fb0) is primary device". That is the only primary device message from dmesg.
fb0 is mentioned at "1.647052 fb0: EFI VGA frame buffer device" and after the primary device message "8.033610 [drm] fb0: amdgpudrmfb frame buffer device"

---

## Unknown



Ah, this changes everything! You're using nouveau (open source) drivers, not proprietary Nvidia drivers. The framebuffer handoff from nouveau to amdgpu after login is your core issue. Let me research specific solutions for forcing nouveau to maintain display output in a nouveau+amdgpu dual GPU setup without using proprietary drivers.



Your report on fixing nouveau black screens when amdgpu claims the framebuffer is ready. It explains the root cause of the display issue and provides several solutions including kernel parameters, Xorg configurations, framebuffer control methods, and emergency recovery procedures. The simplest solution is using "amdgpu.modeset=0" with "nouveau.modeset=1 fbcon=map:0", with more complex options for systems requiring both GPUs to remain active.

---

## Unknown

GPGPU in QubesOS and PVH; while the above concerns.

---

## Unknown



Interesting challenge - combining GPGPU needs in QubesOS with your nouveau/amdgpu display issues. Let me clarify a few things to give you the most relevant solution:

1. **Which GPU do you want to use for GPGPU compute tasks** - the NVIDIA card (with nouveau) or the AMD card? And do you need GPU passthrough to specific qubes or dom0 compute access?

2. **Are you trying to maintain display output on one GPU while using the other for compute** in VMs? (e.g., AMD for display, NVIDIA for GPGPU in qubes)

3. **Is your concern about PVH mode compatibility** with GPU passthrough, or are you experiencing additional display issues when using PVH qubes?

These details will help me research the specific intersection of QubesOS GPU passthrough, PVH virtualization constraints, and how to work around your framebuffer issues in a Xen environment.

---

## Unknown

1. Any Card. Could be hand over both GPUs to a qube to process some units. Then upon return or timeout hand back the GPUs to dom0. But if that is too complex to write code for. Then merely having nVidia card be handed over to a qube for gpgpu.
2. Yes. That was how I used it previously. With GPU Passthrough. handed over to a qube and not used in dom0 for display. Also, they begang a GPU-GUI-Qube back then. How is that going?
3. I guess, I'd prefer partial PVH mode. Where it virtualizes say 22GB GPU 3090RTX and leaves 2GB for dom0. Where memory is strictly enforced different spaces by normal CPU RAM virtualization (if possible)

---

## Unknown



Fascinating requirements! Dynamic GPU handoff between dom0 and qubes, plus the idea of partial GPU memory virtualization in PVH mode - that's pushing the boundaries of what QubesOS typically supports. Let me research the current state of GPU passthrough in QubesOS, PVH compatibility, GPU GUI qube progress, and whether partial GPU virtualization is feasible with your nouveau/amdgpu setup.



Your QubesOS GPU passthrough report is ready. It covers dynamic GPU passthrough limitations, mixed GPU configuration requirements, GPU GUI Qube project status, PVH mode incompatibility, GPU memory partitioning constraints, Nouveau driver configuration, GPGPU compute implementation, Xen hypervisor limitations, automation tools, and a recommended solution for your RTX 3090 + AMD GPU setup with specific configuration details for optimal performance.

---

## Unknown

Can't I simply

---

## Unknown



---

## Unknown

Can't I simply have a service-qube for my GPUs. Then have bare minimum wrapping of the devices in terms of drivers (Then they can be proprietary as well).
Then as dom0 needs to display something, it uses the GPU service instead of running dangerous massive bodies of code in dom0 space?
Also I could have X11 in a service on its own.

Anyway. These GPU service-qubes then have to have an OS that "does the virtualization" of other qubes using it for it??
I didn't read the document yet. So maybe you already pointed it out. But now you have some more stuff to reserach while I read it.

---

## Unknown



Brilliant architecture thinking! You're essentially describing a GPU microservice model that would dramatically improve QubesOS security. This approach would move all the risky GPU driver code out of dom0 into isolated service qubes. Let me research the feasibility of GPU service qubes providing virtualized access to other qubes, remote rendering protocols that could enable this, and how close the community has gotten to implementing this vision.



Your GPU service qubes analysis is ready. It explores the fundamental barriers to GPU virtualization in QubesOS, examining current isolation methods, VirtualGL as a potential solution, Xen architecture limitations, security challenges, and implementation trade-offs. The report includes technical assessments of virtualization technologies and a phased implementation roadmap balancing security requirements with GPU functionality.

---

## Unknown

Also makes it more safe for me to experiment with graphics drivers and setup. I can handle a single GPU at a time turning it into a well-functioning GPU-service-qube.
Then once it is ready I can do the other GPU as a service-qube while using the other for my dom0. Then when both are ready I try to make the switch where dom0 code is changed to call on GPU-service-qubes for rendering and other tasks.
Then I make the switch with X11 or Wayland or some other display-serving/communication-protocol afterwards.

I guess I am interested in making these parts work well. Even though I might want to ditch the virtualization hypervisors in general. They seem messy to me.
But having nice OS atomic units of making a device function as VM-service unit. Seem very nice to me. In having many parts play together. Simply, let each have their own VM "that works" for that hardware and do inter-VM communication of tasks. At least for now it seems reasonable insofar inter-VM communication can be low to no overhead.

So.. I guess we have to do a deep dive into Virtualization in computers and how these different hypervisors work. Say how does Windows Server's GPU-P or VMware's vGPU work. Or how does large datacenters currently manage massive heterogenous compute units; or massive homogenous compute units. Or how does Golemn or other decentralized networks deal with compute tasks and do they employ virtualization by protocol or only in particular instantiations.

---

## Unknown



---

## Unknown

Also makes it more safe for me to experiment with graphics drivers and setup. I can handle a single GPU at a time turning it into a well-functioning GPU-service-qube.
Then once it is ready I can do the other GPU as a service-qube while using the other for my dom0. Then when both are ready I try to make the switch where dom0 code is changed to call on GPU-service-qubes for rendering and other tasks.
Then I make the switch with X11 or Wayland or some other display-serving/communication-protocol afterwards.

I guess I am interested in making these parts work well. Even though I might want to ditch the virtualization hypervisors in general. They seem messy to me.
But having nice OS atomic units of making a device function as VM-service unit. Seem very nice to me. In having many parts play together. Simply, let each have their own VM "that works" for that hardware and do inter-VM communication of tasks. At least for now it seems reasonable insofar inter-VM communication can be low to no overhead.

So.. I guess we have to do a deep dive into Virtualization in computers and how these different hypervisors work. Say how does Windows Server's GPU-P or VMware's vGPU work. Or how does large datacenters currently manage massive heterogenous compute units; or massive homogenous compute units. Or how does Golemn or other decentralized networks deal with compute tasks and do they employ virtualization by protocol or only in particular instantiations..

---

## Unknown



Your incremental approach is brilliant - building GPU service qubes one at a time while maintaining a working system is much safer than attempting a complete cutover. Before I dive deep into virtualization architectures and how datacenters manage heterogeneous compute, let me clarify a few key points:



1. When you mention potentially ditching virtualization hypervisors as "messy" - are you thinking about alternatives like containers, unikernels, or a completely different architecture for hardware isolation?

2. For datacenter compute management, are you more interested in the orchestration layer (like Kubernetes/Slurm) or the lower-level resource allocation and scheduling mechanisms?

3. Since you're considering Golem and decentralized networks - are you interested in how they handle untrusted compute (security/verification) or more in their task distribution and resource management protocols?

These details will help me focus the research on the aspects most relevant to your GPU service qube project and future architectural plans.

---

## Unknown

Also makes it more safe for me to experiment with graphics drivers and setup. I can handle a single GPU at a time turning it into a well-functioning GPU-service-qube. Then once it is ready I can do the other GPU as a service-qube while using the other for my dom0. Then when both are ready I try to make the switch where dom0 code is changed to call on GPU-service-qubes for rendering and other tasks. Then I make the switch with X11 or Wayland or some other display-serving/communication-protocol afterwards.

I guess I am interested in making these parts work well. Even though I might want to ditch the virtualization hypervisors in general. They seem messy to me. But having nice OS atomic units of making a device function as VM-service unit. Seem very nice to me. In having many parts play together. Simply, let each have their own VM "that works" for that hardware and do inter-VM communication of tasks. At least for now it seems reasonable insofar inter-VM communication can be low to no overhead.

So.. I guess we have to do a deep dive into Virtualization in computers and how these different hypervisors work. Say how does Windows Server's GPU-P or VMware's vGPU work. Or how does large datacenters currently manage massive heterogenous compute units; or massive homogenous compute units. 

Or how does Golemn or other decentralized networks deal with compute tasks and do they employ virtualization by protocol or only in particular instantiations..

---

## Unknown



Your incremental approach is excellent - testing one GPU service qube at a time while keeping the other for dom0 stability is a smart migration strategy. Let me dive deep into how modern virtualization systems handle GPU sharing and compute orchestration to inform your design.



Your comprehensive virtualization report is ready. It covers GPU virtualization techniques, compute management at scale, cluster orchestration systems, inter-VM communication methods, and next-generation isolation technologies. The analysis includes performance metrics, architectural trade-offs, and practical implementation insights for GPU service qube design across enterprise and cloud environments.

---

## Unknown

""Create a compute-focused HVM with these settings:
* Memory: 16-32GB (apply max-ram-below-4g=2G fix)
* vCPUs: 8-16 cores
* PCI devices: RTX 3090 (both functions) with permissive and no-strict-reset flags""

Okay. What is the ultimate HVM setup for GPGPU of nVidia 3090? And don't tell me it is Windows HVM :P xD (If it is then okay xD)
Do the top 5 of them in short description pros and cons.
Then do step by step of the top 2.

Also, let's do a deep dive into VirtualGL and also why sys-gui-gpu isn't using it to solve its issues?

---

## Unknown



Great questions! Let me research the optimal HVM setups for RTX 3090 GPGPU in QubesOS, along with a deep dive into VirtualGL and why sys-gui-gpu isn't leveraging it.



Your QubesOS RTX 3090 configuration report is ready. It covers optimal Linux distributions for GPGPU workloads, breakthrough memory configuration settings (max-ram-below-4g=2G), CPU/storage optimizations, VirtualGL analysis, sys-gui-gpu architecture details, and step-by-step setup guides for Ubuntu and Rocky Linux. The report shows RTX 3090 can achieve 90-98% native CUDA performance with proper configuration while maintaining QubesOS security isolation.

---

