"""Factory helpers to open the engine + memory path."""
from __future__ import annotations

import json

from .config import MemoryConfig
from .engine import ExperienceEngine
from .store import Store


def open_engine(state_dir: str = "") -> tuple[ExperienceEngine, MemoryConfig, Store]:
    cfg = MemoryConfig(state_dir)
    store = Store(cfg.db_path)
    eng = ExperienceEngine(store)
    eng.memory_path = cfg.db_path
    return eng, cfg, store


def improvement(eng: ExperienceEngine, cfg: MemoryConfig):
    """Build a Local-mode improvement runner bound to this engine/config."""
    from .improve import ImprovementRun
    return ImprovementRun(eng, cfg)


def export_snapshot(eng: ExperienceEngine, cfg: MemoryConfig) -> str:
    data = eng.store.export_json()
    with open(cfg.snapshot_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    return cfg.snapshot_path


def import_snapshot(eng: ExperienceEngine, path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return eng.store.import_json(data)
