"""Curated PowerShell snippets. No user-supplied script interpolation except allowlisted names."""

from __future__ import annotations

import re

from windows_mcp.errors import ValidationError

_SAFE = re.compile(r"^[\w .\-@\\]+$")


def ident(value: str, field: str = "name") -> str:
    if value is None:
        raise ValidationError(f"{field} required")
    if not _SAFE.match(value) or len(value) > 256:
        raise ValidationError(f"Invalid {field}")
    return value.replace("'", "''")


def to_json_pipeline(expr: str) -> str:
    return f"{expr} | ConvertTo-Json -Compress -Depth 6"


SYSTEM_INFO = r"""
$os = Get-CimInstance Win32_OperatingSystem
$cs = Get-CimInstance Win32_ComputerSystem
$obj = [ordered]@{
  computer = $cs.Name
  domain = $cs.Domain
  manufacturer = $cs.Manufacturer
  model = $cs.Model
  total_memory_mb = [int]($cs.TotalPhysicalMemory / 1MB)
  os = $os.Caption
  version = $os.Version
  build = $os.BuildNumber
  last_boot = $os.LastBootUpTime.ToString('o')
  architecture = $os.OSArchitecture
}
$obj | ConvertTo-Json -Compress -Depth 4
"""

SERVICES = r"""
Get-CimInstance Win32_Service | Select-Object Name, DisplayName, State, StartMode, StartName, PathName |
  ConvertTo-Json -Compress -Depth 4
"""

PROCESSES = r"""
Get-Process | Select-Object Id, ProcessName, CPU, WorkingSet, StartTime |
  ConvertTo-Json -Compress -Depth 4
"""

PRINTERS = r"""
$printers = @()
try {
  $printers = @(Get-Printer | Select-Object Name, DriverName, PortName, Shared, Published, PrinterStatus, JobCount, Datatype, PrintProcessor)
} catch {
  $printers = @(Get-CimInstance Win32_Printer | Select-Object Name, DriverName, PortName, Shared, PrinterStatus, JobCount)
}
$printers | ConvertTo-Json -Compress -Depth 5
"""

SPOOLER = r"""
$svc = Get-Service Spooler
$cim = Get-CimInstance Win32_Service -Filter "Name='Spooler'"
[ordered]@{
  name = $svc.Name
  status = $svc.Status.ToString()
  start_type = $svc.StartType.ToString()
  pathname = $cim.PathName
} | ConvertTo-Json -Compress -Depth 4
"""

NETWORK = r"""
$adapters = @()
try {
  $adapters = @(Get-NetIPConfiguration | ForEach-Object {
    [ordered]@{
      interface = $_.InterfaceAlias
      ipv4 = @($_.IPv4Address.IPAddress)
      ipv6 = @($_.IPv6Address.IPAddress)
      gateway = @($_.IPv4DefaultGateway.NextHop)
      dns = @($_.DNSServer.ServerAddresses)
    }
  })
} catch {
  $adapters = @(Get-CimInstance Win32_NetworkAdapterConfiguration -Filter 'IPEnabled=TRUE' |
    Select-Object Description, MACAddress, IPAddress, DefaultIPGateway, DHCPEnabled)
}
$adapters | ConvertTo-Json -Compress -Depth 6
"""

DISKS = r"""
Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID, DriveType, FileSystem, VolumeName,
  @{n='size_gb';e={[math]::Round($_.Size/1GB,2)}},
  @{n='free_gb';e={[math]::Round($_.FreeSpace/1GB,2)}} |
  ConvertTo-Json -Compress -Depth 4
"""

DEVICES = r"""
try {
  Get-PnpDevice | Select-Object Status, Class, FriendlyName, InstanceId, Problem |
    ConvertTo-Json -Compress -Depth 4
} catch {
  Get-CimInstance Win32_PnPEntity | Select-Object Name, Status, ConfigManagerErrorCode, PNPClass |
    ConvertTo-Json -Compress -Depth 4
}
"""

DRIVERS = r"""
Get-CimInstance Win32_PnPSignedDriver | Select-Object DeviceName, DriverVersion, DriverProviderName, IsSigned, InfName, DriverDate |
  ConvertTo-Json -Compress -Depth 4
"""

HARDWARE = r"""
$cpu = Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed
$mem = Get-CimInstance Win32_PhysicalMemory | Select-Object BankLabel, Manufacturer, Speed, @{n='gb';e={[math]::Round($_.Capacity/1GB,2)}}
$bios = Get-CimInstance Win32_BIOS | Select-Object Manufacturer, SMBIOSBIOSVersion, SerialNumber
[ordered]@{ cpu = @($cpu); memory = @($mem); bios = $bios } | ConvertTo-Json -Compress -Depth 6
"""

SOFTWARE = r"""
$paths = @(
  'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
  'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*'
)
Get-ItemProperty $paths -ErrorAction SilentlyContinue |
  Where-Object { $_.DisplayName } |
  Select-Object DisplayName, DisplayVersion, Publisher, InstallDate |
  ConvertTo-Json -Compress -Depth 4
"""

FIREWALL = r"""
try {
  Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction |
    ConvertTo-Json -Compress -Depth 4
} catch {
  @{ error = 'Get-NetFirewallProfile not available' } | ConvertTo-Json
}
"""

USERS = r"""
$users = @(Get-LocalUser | Select-Object Name, Enabled, LastLogon, Description)
$groups = @(Get-LocalGroup | Select-Object Name, Description)
[ordered]@{ users = $users; groups = $groups } | ConvertTo-Json -Compress -Depth 5
"""


def jobs_script(printer: str | None) -> str:
    if printer:
        p = ident(printer, "printer")
        return (
            f"Get-PrintJob -PrinterName '{p}' | "
            "Select-Object Id, PrinterName, DocumentName, JobStatus, UserName, Size, PagesPrinted, TotalPages, SubmittedTime | "
            "ConvertTo-Json -Compress -Depth 4"
        )
    return (
        "Get-CimInstance Win32_PrintJob | "
        "Select-Object JobId, Name, Document, JobStatus, Owner, Size, TotalPages, TimeSubmitted | "
        "ConvertTo-Json -Compress -Depth 4"
    )


def events_script(log: str, newest: int, provider: str | None) -> str:
    newest = max(1, min(int(newest), 200))
    log_s = ident(log, "log")
    if provider:
        p = ident(provider, "provider")
        filt = f"-FilterHashtable @{{ LogName = '{log_s}'; ProviderName = '{p}' }} -MaxEvents {newest}"
    else:
        filt = f"-LogName '{log_s}' -MaxEvents {newest}"
    return (
        f"Get-WinEvent {filt} | "
        "Select-Object TimeCreated, Id, LevelDisplayName, ProviderName, Message | "
        "ConvertTo-Json -Compress -Depth 4"
    )


def cim_script(class_name: str, filtr: str | None) -> str:
    cls = ident(class_name, "class")
    if filtr:
        if not re.match(r"^[\w =.']+$", filtr):
            raise ValidationError("CIM filter contains unsafe characters")
        f = filtr.replace("'", "''")
        return f"Get-CimInstance -ClassName '{cls}' -Filter '{f}' | ConvertTo-Json -Compress -Depth 4"
    return f"Get-CimInstance -ClassName '{cls}' | ConvertTo-Json -Compress -Depth 4"


def diagnose_printer_script(printer: str | None) -> str:
    p = ident(printer, "printer") if printer else None
    printer_block = (
        f"$pr = Get-Printer -Name '{p}' -ErrorAction SilentlyContinue\n"
        if p
        else "$pr = @(Get-Printer)\n"
    )
    jobs_block = (
        f"$jobs = @(Get-PrintJob -PrinterName '{p}' -ErrorAction SilentlyContinue)\n"
        if p
        else "$jobs = @()\n"
    )
    return f"""
$spooler = Get-Service Spooler
{printer_block}
{jobs_block}
$drivers = @()
$ports = @()
try {{ $drivers = @(Get-PrinterDriver | Select-Object Name, Manufacturer, MajorVersion) }} catch {{}}
try {{ $ports = @(Get-PrinterPort | Select-Object Name, Description, PrinterHostAddress) }} catch {{}}
$events = @()
try {{
  $events = @(Get-WinEvent -FilterHashtable @{{ LogName='System'; Id=7031,7034 }} -MaxEvents 8 |
    Select-Object TimeCreated, Id, Message)
}} catch {{}}
[ordered]@{{
  spooler = $spooler.Status.ToString()
  spooler_start = $spooler.StartType.ToString()
  printers = @($pr | Select-Object Name, DriverName, PortName, PrinterStatus, JobCount)
  jobs = @($jobs | Select-Object Id, DocumentName, JobStatus, UserName)
  drivers = $drivers
  ports = $ports
  recent_spooler_events = $events
}} | ConvertTo-Json -Compress -Depth 6
"""


def action_service(name: str, action: str) -> str:
    n = ident(name)
    if action == "start":
        return f"Start-Service -Name '{n}'; Get-Service '{n}' | Select-Object Name,Status | ConvertTo-Json -Compress"
    if action == "stop":
        return f"Stop-Service -Name '{n}' -Force; Get-Service '{n}' | Select-Object Name,Status | ConvertTo-Json -Compress"
    if action == "restart":
        return f"Restart-Service -Name '{n}' -Force; Get-Service '{n}' | Select-Object Name,Status | ConvertTo-Json -Compress"
    raise ValidationError("action must be start, stop, or restart")


def action_process_stop(pid: int) -> str:
    pid = int(pid)
    if pid <= 0:
        raise ValidationError("pid")
    return f"Stop-Process -Id {pid} -Force; '{{ \"stopped\": {pid} }}'"


def action_job(printer: str, job_id: int, action: str) -> str:
    p = ident(printer)
    jid = int(job_id)
    if action == "remove":
        cmd = f"Remove-PrintJob -PrinterName '{p}' -ID {jid}"
    elif action == "restart":
        cmd = f"Restart-PrintJob -PrinterName '{p}' -ID {jid}"
    elif action == "suspend":
        cmd = f"Suspend-PrintJob -PrinterName '{p}' -ID {jid}"
    elif action == "resume":
        cmd = f"Resume-PrintJob -PrinterName '{p}' -ID {jid}"
    else:
        raise ValidationError("unknown job action")
    return cmd + "; '{ \"ok\": true }'"


def action_printer(name: str, action: str) -> str:
    n = ident(name)
    if action == "pause":
        return f"Set-Printer -Name '{n}' -Comment 'paused-by-mcp'; (Get-Printer -Name '{n}').PrinterStatus"
    # CIM pause
    if action in {"pause", "resume"}:
        pass
    if action == "set_default":
        return f"(New-Object -ComObject WScript.Network).SetDefaultPrinter('{n}'); '{{ \"default\": \"{n}\" }}'"
    raise ValidationError("unsupported printer action")


def spooler_purge() -> str:
    return r"""
Stop-Service Spooler -Force
Remove-Item -Path "$env:SystemRoot\System32\spool\PRINTERS\*" -Force -ErrorAction SilentlyContinue
Start-Service Spooler
Get-Service Spooler | Select-Object Name,Status | ConvertTo-Json -Compress
"""
