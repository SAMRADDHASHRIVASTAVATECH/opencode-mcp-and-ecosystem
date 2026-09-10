"""Runtime improvement mode.

Two improvement strategies share one persistent, audited memory store:

* Cloud Mode  (``MODE_CLOUD``): the memory-based self-improvement loop only
  (record -> reflect -> learn -> retrieve -> consolidate). No model file is ever
  produced or altered.

* Local LLM Mode (``MODE_LOCAL``): the same memory loop PLUS a local model
  self-improvement / fine-tuning mechanism. Each completed task or learning
  cycle accumulates verified learning into a fine-tuning dataset and, when a
  local trainer + base model are available, runs a training step to produce a
  versioned checkpoint the user loads back into LM Studio. This lets a local
  model progressively specialize to the user's tasks.

The mode is stored persistently (kv in the memory store) so it survives
sessions. Deterministic memory behaviour is identical in both modes; only the
local model output/training path is added in Local mode.
"""
from __future__ import annotations

MODE_CLOUD = "cloud"
MODE_LOCAL = "local"
MODES = (MODE_CLOUD, MODE_LOCAL)

# kv keys used for mode + local model runtime config.
KEY_MODE = "mode"
KEY_LOCAL_MODEL = "local.model"      # name/id of the local model performing tasks
KEY_LOCAL_BASE = "local.base_model"  # local filesystem path / HF repo of base to fine-tune
KEY_LOCAL_TRAINER = "local.trainer"  # chosen trainer backend ('' = auto)


def _validate(mode: str) -> str:
    mode = (mode or "").strip().lower()
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}, got {mode!r}")
    return mode


def get_mode(store) -> str:
    return (store.get_kv(KEY_MODE) or MODE_CLOUD)


def set_mode(store, mode: str) -> dict:
    """Persist + audit the active improvement mode."""
    mode = _validate(mode)
    previous = get_mode(store)
    store.put_kv(KEY_MODE, mode)
    store.log("mode.set", "mode", mode,
              before={"mode": previous}, after={"mode": mode})
    return {"mode": mode, "previous": previous}


def get_local_model(store) -> dict:
    return {
        "model": store.get_kv(KEY_LOCAL_MODEL) or "",
        "base_model": store.get_kv(KEY_LOCAL_BASE) or "",
        "trainer": store.get_kv(KEY_LOCAL_TRAINER) or "",
    }


def set_local_model(store, *, model: str = "", base_model: str = "") -> dict:
    store.put_kv(KEY_LOCAL_MODEL, model)
    if base_model:
        store.put_kv(KEY_LOCAL_BASE, base_model)
    store.log("local.model.set", "mode", "local",
              after={"model": model, "base_model": base_model})
    return get_local_model(store)
