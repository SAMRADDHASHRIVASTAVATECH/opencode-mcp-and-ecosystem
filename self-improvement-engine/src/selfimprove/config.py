"""Configuration for the experience-memory engine.

State lives in workspace files so it persists. Defaults can be overridden via env
or CLI. No secrets involved.
"""
from __future__ import annotations

import os
from pathlib import Path


def _s(names, default):
    for n in names:
        v = os.environ.get(n)
        if v:
            return v
    return default


def default_state_dir() -> str:
    # ~/.selfimprove == /home/user/.selfimprove, inside the persistent workspace.
    return _s(["SELFIMPROVE_STATE_DIR", "EXPERIENCE_STATE_DIR"], "~/.selfimprove")


class MemoryConfig:
    def __init__(self, state_dir: str = ""):
        self.state_dir = str(Path(state_dir or default_state_dir()).expanduser())
        Path(self.state_dir).mkdir(parents=True, exist_ok=True)
        self.db_path = str(Path(self.state_dir) / "memory.db")
        # portable JSON snapshot that also lives in the workspace
        self.snapshot_path = str(Path(self.state_dir) / "memory-snapshot.json")
        # Local LLM mode artifacts (dataset / trainer run outputs / checkpoints)
        self.local_dir = str(Path(self.state_dir) / "local")

    def redacted(self) -> dict:
        return {"state_dir": self.state_dir, "db_path": self.db_path,
                "snapshot_path": self.snapshot_path}
