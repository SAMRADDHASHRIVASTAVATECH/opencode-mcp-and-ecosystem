import json

import pytest

from windows_mcp.backend import PowerShellBackend
from windows_mcp.config import Settings
from windows_mcp.errors import PolicyError, UnsupportedError, ValidationError
from windows_mcp.scripts import cim_script, ident, jobs_script
from windows_mcp.tools import _need_windows, _recommendations, register


class FakeExec:
    def __init__(self, payload: object | None = None) -> None:
        self.scripts: list[str] = []
        self.payload = payload if payload is not None else [{"Name": "HP LaserJet", "PrinterStatus": "Normal", "JobCount": 0}]

    def run(self, script: str, timeout: int) -> str:
        self.scripts.append(script)
        if isinstance(self.payload, str):
            return self.payload
        return json.dumps(self.payload)


def test_ident_rejects_injection() -> None:
    with pytest.raises(ValidationError):
        ident("foo; Remove-Item C:\\Windows")
    with pytest.raises(ValidationError):
        ident("a' OR 1=1")


def test_cim_allowlist_script() -> None:
    s = cim_script("Win32_Printer", "Name='HP'")
    assert "Win32_Printer" in s
    with pytest.raises(ValidationError):
        cim_script("Win32_Printer", "Name='x'; Get-Process")


def test_unavailable_backend() -> None:
    be = PowerShellBackend(executor=None)
    # On Linux this is unavailable
    if not be.available:
        with pytest.raises(UnsupportedError):
            _need_windows(be)


def test_diagnose_recommendations() -> None:
    recs = _recommendations(
        {
            "spooler": "Stopped",
            "printers": [{"Name": "HP", "PrinterStatus": "Offline", "PortName": "USB001", "JobCount": 3}],
            "jobs": [{"Id": 12, "JobStatus": "Error"}],
        }
    )
    assert any("Spooler" in r for r in recs)
    assert any("offline" in r.lower() for r in recs)


def test_jobs_script_sanitizes() -> None:
    s = jobs_script("Office Printer")
    assert "Office Printer" in s


def test_fake_printer_list() -> None:
    fx = FakeExec()
    be = PowerShellBackend(executor=fx, settings=Settings(False, False, False, 5, None))
    assert be.available
    data = be.json("Get-Printer")
    assert data[0]["Name"] == "HP LaserJet"


class DummyMCP:
    def __init__(self) -> None:
        self.tools = {}

    def tool(self):
        def deco(fn):
            self.tools[fn.__name__] = fn
            return fn

        return deco


def test_platform_tool_always_works() -> None:
    mcp = DummyMCP()
    fx = FakeExec({"os": "Windows"})
    be = PowerShellBackend(executor=fx, settings=Settings(False, False, False, 5, None))
    register(mcp, backend=be)
    result = mcp.tools["win_platform"]()
    assert result["ok"] is True
    printers = mcp.tools["win_printers"]()
    assert printers["ok"] is True


def test_mutation_requires_confirm() -> None:
    mcp = DummyMCP()
    fx = FakeExec({"ok": True})
    be = PowerShellBackend(executor=fx, settings=Settings(False, False, False, 5, None))
    register(mcp, backend=be)
    result = mcp.tools["win_spooler"](action="restart", confirm=False)
    assert result["ok"] is False
    assert result["error"]["code"] == "SECURITY"
