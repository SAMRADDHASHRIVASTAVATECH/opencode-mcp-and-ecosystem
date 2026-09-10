# Windows System / Printer / Driver MCP — Research Report

**Domain:** Windows administration: OS, services, processes, event logs, devices, drivers, printers, spooler, network, inventory  
**Date:** 2026-09-09  
**Status:** Research complete.

---

## 1. Domain model

Windows administration for this MCP is **local or remoted CIM/WMI + PowerShell**, not a GUI driver. The expert workflow is:

1. Identify the machine (OS, hardware, role).
2. Inspect a subsystem (print, service, device).
3. Correlate (event log + service state + queue).
4. Apply a **bounded** remediation (restart spooler, clear a job) with confirmation.
5. Never become an unconstrained remote shell.

**Key subsystems**

| Area | Primary interface |
|------|-------------------|
| OS / computer | `Win32_OperatingSystem`, `Win32_ComputerSystem`, `Get-ComputerInfo` |
| Services | `Get-Service`, `Win32_Service` |
| Processes | `Get-Process`, `Win32_Process` |
| Event logs | `Get-WinEvent` (modern), `Win32_NTLogEvent` (legacy, slow) |
| Devices | `Get-PnpDevice`, `Win32_PnPEntity` |
| Drivers | `Win32_PnPSignedDriver`, `Get-WindowsDriver` (online image) |
| Printers | PrintManagement module: `Get-Printer`, `Get-PrinterDriver`, `Get-PrinterPort`, `Get-PrintConfiguration` |
| Jobs | `Get-PrintJob`, `Win32_PrintJob` |
| Spooler | Service `Spooler` (`spoolsv.exe`), `HKLM\SYSTEM\CurrentControlSet\Control\Print` |
| Network | `Get-NetAdapter`, `Get-NetIPConfiguration`, `Win32_NetworkAdapterConfiguration` |
| Disk | `Get-Volume`, `Win32_LogicalDisk`, `Win32_DiskDrive` |
| Software | `Win32_Product` (slow/unreliable), prefer registry uninstall keys |
| Hotfixes | `Get-HotFix` / `Win32_QuickFixEngineering` |

**Print architecture (must be accurate)**

- Client app → spooler (`spoolsv.exe`) → print processor → port monitor → port (USB, TCP/IP, WSD, FILE:)
- Driver isolation: XPS/v4 vs v3 kernel-mode history
- Queues can be local or redirected (`\\server\share`)
- Stuck jobs: often spooler crash, bad driver, offline port, or paused queue
- Classic remediation: pause printer, cancel jobs, restart Spooler, clear `%SystemRoot%\System32\spool\PRINTERS` (destructive, needs admin)

PrintManagement cmdlets (Windows 8+ / Server 2012+): Add/Get/Remove/Rename/Set Printer, Driver, Port, Job, Configuration. Documented at Microsoft Learn.

CIM vs WMI: `Get-CimInstance` (WS-Man) replaces `Get-WmiObject` (DCOM). Prefer CIM.

---

## 2. Existing MCP servers

| Project | Focus | Gap vs this domain |
|---------|-------|--------------------|
| CursorTouch/Windows-MCP | GUI computer-use (clicks, screenshots) | Not admin/printers |
| InfraMCP/win-mcp-server | WinRM remote PowerShell | Generic shell risk; not printer-expert |
| mcp-com-server | Arbitrary COM | Dangerous confused deputy |
| WMI Python module | Library, not MCP | Old (2018) |

**Lesson:** do **not** expose unbounded `Invoke-Expression`. Expose semantic tools (`diagnose_printer`, `list_print_jobs`) that internally run curated PowerShell/CIM. Offer a **restricted** `win_cim_query` with class allowlist.

---

## 3. Technology options from Python

| Option | Pros | Cons |
|--------|------|------|
| PowerShell 5.1 / 7 (`pwsh`) JSON output | Official cmdlets, PrintManagement, remoting | Windows (or remote) only |
| pywin32 + WMI package | In-process | Windows-only, older WMI, extra deps |
| win32print | Fine-grained printers | Windows-only, low-level |
| WinRM from Linux (`pywinrm`) | Manage Windows from Linux MCP host | Credentials, still need allowlisted scripts |

**Choice:** PowerShell adapter is primary (curated scripts, `ConvertTo-Json -Depth`). pywin32 optional later. From non-Windows, the MCP still loads and:

- Reports `UNSUPPORTED` for local Windows APIs
- Can use `WIN_MCP_REMOTE_HOST` + WinRM if `pywinrm` is installed (optional)

This sandbox is Linux; tests mock the PowerShell runner.

---

## 4. Printer diagnostic playbook (encode as a tool)

`win_diagnose_printer` should chain:

1. OS + spooler service state (running, start mode)
2. `Get-Printer` (paused, offline, job count, port, driver)
3. `Get-PrinterPort` / `Get-PrinterDriver`
4. `Get-PrintJob` for that queue
5. Recent System/Application events mentioning spooler/print (IDs 7031, 7034, 6161, 372, 307, etc.)
6. Device status if USB
7. Heuristic recommendations (restart spooler, unpause, clear job, driver mismatch)

Do **not** auto-clear the spool directory without `confirm=true` and admin policy.

---

## 5. Security

Unconstrained Windows admin MCP is a full RCE surface.

- No arbitrary PowerShell
- CIM class allowlist
- Mutating operations (restart service, cancel job, set default printer) require `confirm=true`
- Destructive (clear spool files, remove printer) require `WIN_MCP_ALLOW_DESTRUCTIVE=1` + confirm
- Redact usernames/SIDs optionally
- Timeout every subprocess
- No credential logging

---

## 6. Platform-specific behavior

- PrintManagement is not on all SKUs (Home vs Pro/Server); fall back to `Win32_Printer`
- `Get-WinEvent` needs appropriate log ACLs
- Restarting Spooler needs admin
- Win32_Product triggers a consistency check — avoid; use uninstall registry
- Remote `-ComputerName` needs firewall + permissions

---

## 7. What “maximum practical” means here

A useful Windows MCP is an **admin runbook**, not a replica of every Win32 API. Cover inventory, print stack, services, processes, events, devices/drivers, network, disks, software, and one expert diagnostic workflow. Refuse to become a generic shell.
