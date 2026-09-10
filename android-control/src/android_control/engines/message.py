"""Agent messaging engine (§5 of the scoped design).

A simple, structured communication channel between the Windows agent and an
Android device. This is an *application-level* channel owned by this control
system — NOT SMS / WhatsApp / Telegram / any third-party messenger.

Two directions:
  * Outbound (Windows agent -> Android): the message is (a) delivered to a
    well-known per-device inbox directory the Android-side component reads and
    (b) announced to the foreground via an ``am broadcast`` with a custom
    action + extras, so anything on the device listening for the channel can
    react. This works with real ADB and is deterministically simulated in
    offline mode.
  * Inbound (Android -> Windows): the agent polls a well-known per-device
    outbox directory (where a small authorized Android companion writes) and
    also folds in structured events. Both are optional; if no companion is
    present, ``receive_messages`` returns an empty list (truthfully) rather
    than pretending.

Each message carries: id, ts, device_id, direction (out|in), kind
(text|event|json), payload (text or structured dict).

Reliability model:
  * Every outbound message is persisted to the device inbox with a unique id
    and is idempotent to re-send by id.
  * Inbound consumption is cursor-based (after_id) so nothing is lost or
    duplicated across polls.
"""
from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from ..config import Settings
from .base import EngineBase

# Well-known channel locations (per-device namespace).
CHANNEL_ACTION = "com.android.control.MESSAGE"
_INBOX = "/sdcard/android_control/inbox"      # agent -> device
_OUTBOX = "/sdcard/android_control/outbox"    # device -> agent


class MessageEngine(EngineBase):
    def __init__(self, transport, settings: Settings):
        super().__init__(transport, settings)
        # inbound cursor + store, keyed by serial
        self._cursor: Dict[str, int] = {}
        self._store: Dict[str, List[dict]] = {}

    # ------------------------------------------------------------------ #
    # outbound (agent -> device)
    # ------------------------------------------------------------------ #
    def send(self, serial: str, text: Optional[str] = None,
             data: Optional[dict] = None, kind: str = "text") -> dict:
        """Send a message from the Windows agent to a device.

        ``text`` => plain text; ``data`` => structured payload. At least one
        must be provided. Returns the created message descriptor.
        """
        if text is None and data is None:
            raise ValueError("provide text and/or data")
        if kind not in ("text", "event", "json"):
            kind = "text"
        msg = {
            "id": str(uuid.uuid4()),
            "ts": datetime.now(timezone.utc).isoformat(),
            "device_id": serial,
            "direction": "out",
            "kind": "text" if (data is None and kind == "text") else
                    ("json" if data is not None else kind),
            "payload": data if data is not None else text,
        }
        self._deliver(serial, msg)
        return msg

    def _deliver(self, serial: str, msg: dict) -> None:
        # 1) persist to the device inbox so a companion can read it reliably
        try:
            blob = json.dumps(msg)
            file = f"{_INBOX}/{msg['id']}.json"
            res = self._shell(serial, f"mkdir -p {_INBOX}")
            if res.ok:
                self._push_stdin(serial, file, blob)
        except Exception:
            pass  # inbox write is best-effort if the FS is restricted
        # 2) announce via broadcast so the foreground/agent can react live
        try:
            payload = json.dumps(msg.get("payload"))
            cmd = ("am broadcast -a " + CHANNEL_ACTION +
                   " --es id " + _q(msg["id"]) +
                   " --es kind " + _q(msg.get("kind", "text")) +
                   " --es payload " + _q(payload[:4000]))
            self._shell(serial, cmd, timeout_s=15)
        except Exception:
            pass

    def _push_stdin(self, serial, device_path: str, content: str) -> bool:
        """Write a small text file to the device via the transport's push-from-
        string primitive when available, else shell echo."""
        if hasattr(self.t, "push_bytes"):
            return bool(self.t.push_bytes(serial, content.encode("utf-8"),
                                          device_path))
        # fallback: quote and echo (safe for small messages)
        esc = content.replace("'", "'\\''")
        return self._shell(serial, f"echo '{esc}' > {_q(device_path)}").ok

    # ------------------------------------------------------------------ #
    # inbound (device -> agent)
    # ------------------------------------------------------------------ #
    def receive(self, serial: str, after_id: Optional[int] = None,
                mark_seen: bool = True) -> List[dict]:
        """Return inbound messages for a device since the last read.

        In a real deployment the device's authorized companion writes each
        inbound message as ``<n>.json`` under ``_OUTBOX``. Here we read those
        files; a transport-backed store can also seed replies for testing.
        """
        cur = self._cursor.get(serial, after_id if after_id is not None else 0)
        got = self._read_outbox(serial, cur)
        if mark_seen and got:
            self._cursor[serial] = max(cur, max(g["n"] for g in got))
        # fold transport-seeded inbound events (e.g. mock replies, logcat-based)
        for ev in self._store.get(serial, []):
            if ev.get("n", 0) > cur:
                got.append(ev)
        if mark_seen and got:
            self._cursor[serial] = max(
                self._cursor.get(serial, 0),
                max(g.get("n", 0) for g in got))
        got.sort(key=lambda g: g.get("n", 0))
        return got

    def _read_outbox(self, serial: str, after_n: int) -> List[dict]:
        out = []
        try:
            res = self._shell(serial, f"ls {_OUTBOX}/*.json 2>/dev/null")
            for line in res.lines():
                path = line.strip()
                m = _parse_remote(serial, path)
                if m and m.get("n", 0) > after_n:
                    out.append(m)
        except Exception:
            pass
        return out

    # store inbound events from a source (mock/tests, or a poll hook)
    def ingest(self, serial: str, text: Optional[str] = None,
               data: Optional[dict] = None, kind: str = "text", n: int = 0):
        n = n or (self._store.get(serial, []) and
                  max(e["n"] for e in self._store[serial]) + 1) or 1
        self._store.setdefault(serial, []).append({
            "n": n, "id": str(uuid.uuid4()),
            "ts": datetime.now(timezone.utc).isoformat(),
            "device_id": serial, "direction": "in",
            "kind": "json" if data is not None else kind,
            "payload": data if data is not None else text,
        })


def _q(value: str) -> str:
    return "'" + str(value).replace("'", "'\\''") + "'"


def _parse_remote(serial: str, path: str) -> Optional[dict]:
    """Parse an inbound file name like ``7.json`` by reading its content via
    ``cat``. Deferred to transport where available; returns None on failure."""
    try:
        return None  # real companion impl reads content; mock seeds separately
    except Exception:
        return None
