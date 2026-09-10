# Windows System MCP — Technology Evaluation

| Option | Verdict |
|--------|---------|
| PowerShell + PrintManagement + CIM | **Primary.** Official, complete printer coverage, JSON-friendly |
| Get-WmiObject | Legacy; use only as fallback comment in scripts |
| pywin32 / WMI 1.5 | Fallback on Windows if powershell missing; not required |
| win32print | Too low-level for semantic tools |
| Windows-MCP (CursorTouch) | Different domain (GUI) |
| Unbounded WinRM shell | Rejected as a tool |
| pywinrm from Linux | Optional remote adapter |

PowerShell 7 (`pwsh`) preferred; Windows PowerShell 5.1 acceptable. Scripts use `-NoProfile -NonInteractive -ExecutionPolicy Bypass` for the curated file only (Bypass is for our generated script block, not user code). Output: `ConvertTo-Json -Compress -Depth 6`.
