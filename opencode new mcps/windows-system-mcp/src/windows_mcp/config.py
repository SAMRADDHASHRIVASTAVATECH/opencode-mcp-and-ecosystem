from __future__ import annotations

import os
from dataclasses import dataclass


def _bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)

    if raw is None:
        return default

    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int = 30) -> int:
    raw = os.environ.get(name)

    if not raw:
        return default

    try:
        value = int(raw)
        return value if value > 0 else default
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    """
    Runtime configuration for the Windows MCP.

    Important:
    - read_only=False allows write/mutation code paths to be considered.
    - allow_destructive=True allows destructive operations to proceed
      to the MCP's approval/permission layer.
    - allow_remote=True enables remote-operation code paths where implemented.
    - None of these settings bypass Windows permissions or UAC.
    """

    read_only: bool
    allow_destructive: bool
    allow_remote: bool
    timeout: int
    remote_host: str | None

    @classmethod
    def load(cls) -> "Settings":
        return cls(
            # Full operation mode by default.
            read_only=_bool("WIN_MCP_READ_ONLY", False),

            # Enable destructive/write-capable operations.
            # Individual tools should STILL enforce confirmation/approval.
            allow_destructive=_bool("WIN_MCP_ALLOW_DESTRUCTIVE", True),

            # Enable remote operation paths where implemented.
            allow_remote=_bool("WIN_MCP_ALLOW_REMOTE", True),

            timeout=_int("WIN_MCP_TIMEOUT", 30),

            remote_host=(
                os.environ.get("WIN_MCP_REMOTE_HOST")
                or None
            ),
        )


SETTINGS = Settings.load()


# Only these CIM classes may be queried by the MCP.
CIM_ALLOWLIST = {
    "Win32_OperatingSystem",
    "Win32_ComputerSystem",
    "Win32_Service",
    "Win32_Process",
    "Win32_Printer",
    "Win32_PrintJob",
    "Win32_TCPIPPrinterPort",
    "Win32_PrinterDriver",
    "Win32_PnPEntity",
    "Win32_PnPSignedDriver",
    "Win32_LogicalDisk",
    "Win32_DiskDrive",
    "Win32_NetworkAdapter",
    "Win32_NetworkAdapterConfiguration",
    "Win32_QuickFixEngineering",
    "Win32_BIOS",
    "Win32_Processor",
    "Win32_PhysicalMemory",
    "Win32_PageFileUsage",
    "Win32_BaseBoard",
    "Win32_VideoController",
}


EVENT_LOGS = {
    "System",
    "Application",
    "Setup",
    "Security",
}