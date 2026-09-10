# Capability matrix

| Platform | Discovery | Level 1 execution | Level 2 |
|---|---|---|---|
| VirtualBox | installed CLI, all/running VMs | lifecycle, save, snapshots, clone | SSH or verified Guest Additions guestcontrol |
| Hyper-V | PowerShell + Hyper-V module | lifecycle and checkpoints | capability reported; use SSH in this release |
| VMware | `vmrun`, running VMs | lifecycle and snapshots | SSH in this release; powered-off inventory needs external configuration |
| libvirt | `virsh`, all names | lifecycle and snapshots | SSH; QEMU agent is not treated as arbitrary shell |
| WSL | `wsl.exe`, distributions | launch, terminate, export/import/unregister | direct exec |

Creation, broad resource/network/storage mutation, file-copy wrappers, WinRM, PowerShell Direct, VMware Tools guest operations, and multi-host orchestration are intentionally not exposed until their prerequisites and robust verification are implemented. Platform metadata may describe broader native capabilities; executable planner support is narrower and rejects everything else.
