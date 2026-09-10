# Windows System / Printer / Driver MCP

Standalone MCP for **Windows administration** with an expert print stack: printers, jobs, drivers, ports, and the Print Spooler.

It is independently installable. On Linux/macOS the server still starts; live tools return structured `UNSUPPORTED` errors via `win_platform`.

Research: `research-report.md`, `capability-matrix.md`, `technology-evaluation.md`, `architecture.md`, `security-model.md`.

## Why PowerShell + CIM, not a generic shell

PrintManagement (`Get-Printer`, `Get-PrintJob`, …) and `Get-CimInstance` are the supported admin surface. Unbounded `Invoke-Expression` would be remote code execution. This MCP only runs **curated** snippets and an **allowlisted** CIM class list.

## Install

```bash
pip install -e ./windows-system-mcp
```

## Run (on Windows)

```bash
python -m windows_mcp
```

```json
{
  "mcpServers": {
    "windows-system": {
      "command": "python",
      "args": ["-m", "windows_mcp"],
      "env": {
        "WIN_MCP_READ_ONLY": "0"
      }
    }
  }
}
```

## Tools

`win_platform` `win_system_info` `win_services` `win_processes` `win_printers` `win_print_jobs` `win_spooler` `win_diagnose_printer` `win_event_logs` `win_devices` `win_drivers` `win_network` `win_disks` `win_software` `win_hardware` `win_firewall` `win_users` `win_cim_query`

Mutations require `confirm=true`. Clearing the spool directory requires `WIN_MCP_ALLOW_DESTRUCTIVE=1`.
