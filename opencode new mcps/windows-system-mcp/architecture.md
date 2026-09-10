# Windows System MCP — Architecture

```
MCP tools (semantic)
    ▼
policy (confirm, destructive, class allowlist)
    ▼
backend
    ├── LocalPowerShellBackend  (Windows)
    ├── WinRMBackend            (optional)
    └── UnavailableBackend      (Linux/macOS local)
    ▼
curated PowerShell snippets → JSON → domain normalize
```

Every mutating tool maps to a **named action**, not to a script the model writes.

CIM allowlist includes Win32_OperatingSystem, ComputerSystem, Service, Process, Printer, PrintJob, PnPEntity, PnPSignedDriver, LogicalDisk, DiskDrive, NetworkAdapterConfiguration, QuickFixEngineering, BIOS, Processor, PhysicalMemory, PageFileUsage. Nothing else.
