# Windows MCP — second research pass / gap analysis

## Confirmed

- PrintManagement module is the correct high-level surface ([Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/printmanagement/))
- Win32_Product is avoided (software via Uninstall registry)
- Get-WinEvent over Win32_NTLogEvent

## Remaining gaps

| Gap | Notes |
|-----|-------|
| Live tests | Require Windows; Linux uses fake executor |
| pywin32 fallback | Not needed if PowerShell exists |
| WinRM remote backend | Optional extra, not wired by default |
| Printer pause via CIM Pause/Resume | set_default implemented; pause can be added as CIM method |
| Driver INF install | Too dangerous for default MCP |
| Clustered print servers | ComputerName remoting gated off |

The MCP will not grow a generic `run_powershell` tool.
