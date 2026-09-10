# Windows System MCP — Capability Matrix

## BASIC

| Capability | Status | Tool |
|------------|--------|------|
| Platform / adapter health | P | `win_platform` |
| OS & computer identity | P | `win_system_info` |
| List services + filter | P | `win_services` |
| List processes | P | `win_processes` |
| List printers | P | `win_printers` |
| List print jobs | P | `win_print_jobs` |
| Spooler status | P | `win_spooler` |
| Disk / volume free space | P | `win_disks` |
| Basic network adapters/IPs | P | `win_network` |

## ADVANCED

| Capability | Status | Tool |
|------------|--------|------|
| Start/stop/restart service (confirm) | P | `win_services` action= |
| Kill process (confirm) | P | `win_processes` action=stop |
| Pause/unpause printer | P | `win_printers` action= |
| Cancel/restart print job | P | `win_print_jobs` action= |
| Event log query (bounded) | P | `win_event_logs` |
| PnP devices | P | `win_devices` |
| Signed driver inventory | P | `win_drivers` |
| Software inventory (registry) | P | `win_software` |
| Hardware summary | P | `win_hardware` |
| Firewall profile status | P | `win_firewall` |
| Local users/groups (read) | P | `win_users` |

## EXPERT / DIAGNOSTICS / RECOVERY

| Capability | Status | Tool |
|------------|--------|------|
| Printer stack diagnose | P | `win_diagnose_printer` |
| Allowlisted CIM query | P | `win_cim_query` |
| Restart spooler (confirm) | P | `win_spooler` action=restart |
| Clear jobs on a printer | P | `win_print_jobs` action=clear |
| Clear spool directory | F | `win_spooler` action=purge (destructive flag) |
| Hotfixes | P | `win_system_info` include=hotfixes |

## Out of scope

Arbitrary PowerShell; registry write; GPO edit; driver INF install from random paths; dumping LSASS; enabling RDP from MCP without extra policy (not implemented).
