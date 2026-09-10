# CATLX — Windows-First Implementation Rules

> Source: adaptation of the OS-specific mechanisms in Parts II–XVI to a Windows-only target. Replace
> every Linux/macOS reference in the source with its Windows equivalent. USB flash-drive scenarios are
> removed entirely.

This conversion targets **Windows 10 and Windows 11**. The following table is the canonical mapping of
source OS mechanisms to their Windows equivalents. Any skill that mentions a Linux/macOS mechanism must
reference this rule and use the Windows mechanism instead.

## OS mechanism mapping

| Concern | Source (cross-platform) | Windows implementation |
|---|---|---|
| Runtime / Node | Portable Node.js on Windows; statically-linked Node on Linux; bundles its own Node | Bundle a **portable Node.js** distribution; all npm deps vendored in `node_modules/`; no global Node required |
| Credentials | DPAPI on Windows; libsecret on Linux | **DPAPI** (ties encryption to the Windows login credential). No plaintext, no env vars in production |
| Secondary cred store | Windows Credential Manager | **Windows Credential Manager** — read with consent, write for cross-app sharing |
| Capability firewall | AppContainer on Windows; seccomp BPF on Linux | **AppContainer** (plus **Windows Filtering Platform** network rules) |
| Keyboard synthesis | SendInput on Windows; XTest/uinput on Linux | **SendInput** API |
| Window accessibility | UIAutomation on Windows; AT-SPI2 on Linux | **UIAutomation** |
| Native notifications | Windows Notification Center; libnotify on Linux | **Windows Notification Center** |
| GPU enumerate | CUDA / Vulkan / DirectX | **DirectX** (and CUDA for RTX tiers) |
| Containers | Docker; Docker Desktop on desktop | **Docker Desktop with WSL2 backend**; Compose; GPU passthrough |
| File/OS isolation | Process isolation; AppContainer | Process isolation + AppContainer; Docker for T2+ plugins |
| OS target | Windows 10/11 / Linux / macOS | **Windows 10 and Windows 11 only** |

## Windows-specific behavior to preserve

1. **Portable launcher** — `launcher.exe` at `CATLX_ROOT`; locates `CATLX_ROOT` from its own path.
2. **Portable-mode installer (external SSD)** — assigns a consistent drive letter using the disk serial
   number via a lightweight driver shim, writes a portability manifest to the drive root, and starts the
   Electron shell **tray-only** (no taskbar entry) to minimize footprint on guest machines. (USB
   flash drive wording is removed; target is external NVMe SSD.)
3. **DPAPI credential vault** — encryption is tied to the Windows user's login credential; this is the
   primary vault, with Windows Credential Manager as the secondary store for cross-app credentials.
4. **AppContainer + Windows Filtering Platform** — plugin/binary-level enforcement so a compromised
   module cannot exceed its declared permissions, even in-process.
5. **UIAutomation** — window enumeration and non-browser application automation for modern Windows apps;
   OCR fallback for legacy apps without accessibility trees; native COM/WMI for Microsoft Office.
6. **SendInput** — raw key events, text typing, hotkeys, clipboard read/write, secure input mode.
7. **Docker Desktop + WSL2** — the container runtime for heavy ML workloads and T2+ plugin sandboxes;
   GPU passthrough via WSL2 for CUDA workloads.

## What is NOT done

- No Linux-only paths (`/opt`, `/usr`), no macOS paths, no Linux-only commands (`sed` semantics,
  `seccomp`, `libnotify`, `XTest`, `uinput`, `AT-SPI2`, `libsecret`, `KWallet`).
- No USB performance tiering based on USB 3.2 speed, and no
  "USB drive" mentions in portability. Portable storage means **external NVMe SSD**.
- No cross-platform "OS Target" rows that list Linux/macOS.
