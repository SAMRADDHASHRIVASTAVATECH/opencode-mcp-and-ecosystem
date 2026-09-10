"""Windows semantic tools."""

from __future__ import annotations

from typing import Any

from windows_mcp.backend import BACKEND, PowerShellBackend
from windows_mcp.config import CIM_ALLOWLIST, EVENT_LOGS, SETTINGS
from windows_mcp.errors import PolicyError, UnsupportedError, ValidationError, WinError
from windows_mcp.scripts import (
    DEVICES,
    DISKS,
    DRIVERS,
    FIREWALL,
    HARDWARE,
    NETWORK,
    PRINTERS,
    PROCESSES,
    SERVICES,
    SOFTWARE,
    SPOOLER,
    SYSTEM_INFO,
    USERS,
    action_job,
    action_service,
    cim_script,
    diagnose_printer_script,
    events_script,
    ident,
    jobs_script,
    spooler_purge,
)


def _ok(data: Any) -> dict[str, Any]:
    return {"ok": True, "data": data, "warnings": [], "meta": {}}


def _fail(exc: BaseException) -> dict[str, Any]:
    if isinstance(exc, WinError):
        return {"ok": False, "error": exc.to_dict(), "data": None, "warnings": []}
    return {
        "ok": False,
        "error": {"code": "INTERNAL", "message": str(exc), "details": {"type": type(exc).__name__}},
        "data": None,
        "warnings": [],
    }


def _run(fn, **kw):
    try:
        return _ok(fn(**kw))
    except Exception as exc:
        return _fail(exc)


def _need_windows(backend: PowerShellBackend) -> None:
    if not backend.available:
        raise UnsupportedError(
            "This tool needs Windows PowerShell. The MCP is installed, but the host OS is not Windows "
            "(or pwsh/powershell was not found).",
            backend.platform_info(),
        )


def _mutate(confirm: bool, destructive: bool = False) -> None:
    if SETTINGS.read_only:
        raise PolicyError("WIN_MCP_READ_ONLY is set")
    if not confirm:
        raise PolicyError("Mutating Windows operations require confirm=true")
    if destructive and not SETTINGS.allow_destructive:
        raise PolicyError("Destructive ops require WIN_MCP_ALLOW_DESTRUCTIVE=1")


def _normalize(data: Any) -> Any:
    if data is None:
        return []
    if isinstance(data, dict) and set(data.keys()) <= {"raw"}:
        return data
    if isinstance(data, dict):
        return [data]
    return data


def register(mcp: Any, backend: PowerShellBackend | None = None) -> None:
    be = backend or BACKEND

    @mcp.tool()
    def win_platform() -> dict[str, Any]:
        """Report whether Windows/PowerShell is available and the current safety policy."""
        return _run(lambda: be.platform_info())

    @mcp.tool()
    def win_system_info(include_hotfixes: bool = False) -> dict[str, Any]:
        """OS, computer model, memory, boot time. Optionally include hotfixes."""
        def inner() -> Any:
            _need_windows(be)
            data = be.json(SYSTEM_INFO)
            if include_hotfixes:
                hf = be.json(
                    "Get-CimInstance Win32_QuickFixEngineering | "
                    "Select-Object HotFixID, Description, InstalledOn | ConvertTo-Json -Compress -Depth 4"
                )
                if isinstance(data, dict):
                    data["hotfixes"] = _normalize(hf)
            return data

        return _run(inner)

    @mcp.tool()
    def win_services(name: str | None = None, action: str | None = None, confirm: bool = False) -> dict[str, Any]:
        """List Windows services, or start/stop/restart one service (confirm=true)."""
        def inner() -> Any:
            _need_windows(be)
            if action:
                _mutate(confirm)
                if not name:
                    raise ValidationError("name required for service action")
                return be.json(action_service(name, action))
            data = _normalize(be.json(SERVICES))
            if name:
                n = name.lower()
                data = [s for s in data if n in str(s.get("Name", "")).lower() or n in str(s.get("DisplayName", "")).lower()]
            return data[:400]

        return _run(inner)

    @mcp.tool()
    def win_processes(name: str | None = None, action: str | None = None, pid: int | None = None, confirm: bool = False) -> dict[str, Any]:
        """List processes, or stop a process by pid (action=stop, confirm=true)."""
        def inner() -> Any:
            _need_windows(be)
            if action == "stop":
                _mutate(confirm)
                if pid is None:
                    raise ValidationError("pid required")
                return be.json(
                    f"Stop-Process -Id {int(pid)} -Force; @{{ stopped = {int(pid)} }} | ConvertTo-Json -Compress"
                )
            data = _normalize(be.json(PROCESSES))
            if name:
                n = name.lower()
                data = [p for p in data if n in str(p.get("ProcessName", "")).lower()]
            return data[:400]

        return _run(inner)

    @mcp.tool()
    def win_printers(name: str | None = None, action: str | None = None, confirm: bool = False) -> dict[str, Any]:
        """List printers. action=set_default requires confirm=true."""
        def inner() -> Any:
            _need_windows(be)
            if action == "set_default":
                _mutate(confirm)
                if not name:
                    raise ValidationError("name required")
                n = ident(name)
                return be.json(
                    f"$null = (New-Object -ComObject WScript.Network).SetDefaultPrinter('{n}'); "
                    f"@{{ default = '{n}' }} | ConvertTo-Json -Compress"
                )
            data = _normalize(be.json(PRINTERS))
            if name:
                n = name.lower()
                data = [p for p in data if n in str(p.get("Name", "")).lower()]
            return data

        return _run(inner)

    @mcp.tool()
    def win_print_jobs(
        printer: str | None = None,
        action: str | None = None,
        job_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """List print jobs. action=remove|restart|suspend|resume needs printer, job_id, confirm=true."""
        def inner() -> Any:
            _need_windows(be)
            if action:
                _mutate(confirm)
                if printer is None or job_id is None:
                    raise ValidationError("printer and job_id required")
                return be.json(action_job(printer, job_id, action) + " | Out-Null; @{ ok = $true } | ConvertTo-Json -Compress")
            return _normalize(be.json(jobs_script(printer)))

        return _run(inner)

    @mcp.tool()
    def win_spooler(action: str | None = None, confirm: bool = False) -> dict[str, Any]:
        """Print Spooler status. action=restart or purge (purge is destructive: clears spool directory)."""
        def inner() -> Any:
            _need_windows(be)
            if action == "restart":
                _mutate(confirm)
                return be.json(action_service("Spooler", "restart"))
            if action == "purge":
                _mutate(confirm, destructive=True)
                return be.json(spooler_purge())
            return be.json(SPOOLER)

        return _run(inner)

    @mcp.tool()
    def win_diagnose_printer(printer: str | None = None) -> dict[str, Any]:
        """Expert print-stack diagnosis: spooler, queue, driver, port, jobs, recent related events, recommendations."""
        def inner() -> Any:
            _need_windows(be)
            raw = be.json(diagnose_printer_script(printer))
            recs = _recommendations(raw)
            if isinstance(raw, dict):
                raw["recommendations"] = recs
            else:
                raw = {"raw": raw, "recommendations": recs}
            return raw

        return _run(inner)

    @mcp.tool()
    def win_event_logs(log: str = "System", newest: int = 40, provider: str | None = None) -> dict[str, Any]:
        """Bounded Get-WinEvent query. log must be System, Application, Setup, or Security."""
        def inner() -> Any:
            _need_windows(be)
            if log not in EVENT_LOGS:
                raise PolicyError(f"Log not allowlisted: {log}", {"allowed": sorted(EVENT_LOGS)})
            return _normalize(be.json(events_script(log, newest, provider)))

        return _run(inner)

    @mcp.tool()
    def win_devices() -> dict[str, Any]:
        """PnP devices and problem codes."""
        return _run(lambda: (_need_windows(be), _normalize(be.json(DEVICES)))[1])

    @mcp.tool()
    def win_drivers() -> dict[str, Any]:
        """Signed driver inventory (Win32_PnPSignedDriver)."""
        return _run(lambda: (_need_windows(be), _normalize(be.json(DRIVERS)))[1])

    @mcp.tool()
    def win_network() -> dict[str, Any]:
        """IP configuration / adapters."""
        return _run(lambda: (_need_windows(be), _normalize(be.json(NETWORK)))[1])

    @mcp.tool()
    def win_disks() -> dict[str, Any]:
        """Logical disks with size and free space."""
        return _run(lambda: (_need_windows(be), _normalize(be.json(DISKS)))[1])

    @mcp.tool()
    def win_software() -> dict[str, Any]:
        """Installed software from Uninstall registry keys (not Win32_Product)."""
        return _run(lambda: (_need_windows(be), _normalize(be.json(SOFTWARE)))[1])

    @mcp.tool()
    def win_hardware() -> dict[str, Any]:
        """CPU, memory modules, BIOS."""
        return _run(lambda: (_need_windows(be), be.json(HARDWARE)))

    @mcp.tool()
    def win_firewall() -> dict[str, Any]:
        """Firewall profile enabled/inbound/outbound defaults."""
        return _run(lambda: (_need_windows(be), _normalize(be.json(FIREWALL)))[1])

    @mcp.tool()
    def win_users() -> dict[str, Any]:
        """Local users and groups (read-only)."""
        return _run(lambda: (_need_windows(be), be.json(USERS)))

    @mcp.tool()
    def win_cim_query(class_name: str, filtr: str | None = None) -> dict[str, Any]:
        """Allowlisted Get-CimInstance query. class_name must be on the CIM allowlist."""
        def inner() -> Any:
            _need_windows(be)
            if class_name not in CIM_ALLOWLIST:
                raise PolicyError(
                    "CIM class not allowlisted",
                    {"class": class_name, "allowed": sorted(CIM_ALLOWLIST)},
                )
            return _normalize(be.json(cim_script(class_name, filtr)))

        return _run(inner)


def _recommendations(raw: Any) -> list[str]:
    recs: list[str] = []
    if not isinstance(raw, dict):
        recs.append("Could not parse printer diagnostic JSON; inspect raw output.")
        return recs
    spooler = str(raw.get("spooler") or "")
    if spooler.lower() not in {"running", ""}:
        recs.append("Print Spooler is not Running. Restart it with win_spooler action=restart confirm=true (needs admin).")
    printers = raw.get("printers") or []
    if isinstance(printers, dict):
        printers = [printers]
    for pr in printers:
        status = str(pr.get("PrinterStatus") or "")
        jobs = pr.get("JobCount")
        if "Offline" in status or status in {"7", "128"}:
            recs.append(f"Printer {pr.get('Name')} looks offline. Check cable/IP port {pr.get('PortName')}.")
        if jobs and int(jobs) > 0:
            recs.append(f"Printer {pr.get('Name')} has {jobs} queued jobs. Inspect win_print_jobs; cancel stuck jobs.")
    jobs = raw.get("jobs") or []
    if isinstance(jobs, dict):
        jobs = [jobs]
    for job in jobs:
        st = str(job.get("JobStatus") or "")
        if "Error" in st or "Paused" in st:
            recs.append(f"Job {job.get('Id')} status={st}. Consider remove/restart with confirm=true.")
    if not recs:
        recs.append("Spooler running and no obvious queue errors. If printing still fails, compare driver vs port (WSD vs TCP/IP) and check device error codes via win_devices.")
    return recs
