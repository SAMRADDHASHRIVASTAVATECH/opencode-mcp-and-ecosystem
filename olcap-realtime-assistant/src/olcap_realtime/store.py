"""Persistent session storage (spec section 24).

Sessions + transcripts + summaries + events + audit survive restarts. Raw audio /
screenshots are never stored unless recording is explicitly configured.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions(
  session_id TEXT PRIMARY KEY,
  payload TEXT NOT NULL,
  created REAL
);
CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT, payload TEXT, ts REAL
);
CREATE TABLE IF NOT EXISTS audit(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts REAL, actor TEXT, action TEXT, detail TEXT
);
CREATE TABLE IF NOT EXISTS kv(key TEXT PRIMARY KEY, value TEXT);
"""


class Store:
    def __init__(self, db_path: str):
        self.path = db_path
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        with self._lock:
            self.conn.executescript(SCHEMA)
            self.conn.commit()

    def close(self):
        with self._lock:
            try:
                self.conn.close()
            except Exception:
                pass

    # ---- sessions ---- #
    def put_session(self, rec: dict):
        with self._lock:
            self.conn.execute(
                "INSERT OR REPLACE INTO sessions(session_id,payload,created) VALUES(?,?,?)",
                (rec["session_id"], json.dumps(rec), rec.get("start_time") or 0))
            self.conn.commit()

    def get_session(self, session_id: str) -> dict | None:
        with self._lock:
            r = self.conn.execute("SELECT payload FROM sessions WHERE session_id=?",
                                  (session_id,)).fetchone()
        return json.loads(r[0]) if r else None

    def list_sessions(self, limit=100):
        with self._lock:
            rows = self.conn.execute(
                "SELECT payload FROM sessions ORDER BY created DESC LIMIT ?",
                (limit,)).fetchall()
        return [json.loads(r[0]) for r in rows]

    def delete_session(self, session_id: str) -> bool:
        with self._lock:
            cur = self.conn.execute("DELETE FROM sessions WHERE session_id=?",
                                    (session_id,))
            self.conn.execute("DELETE FROM events WHERE session_id=?", (session_id,))
            self.conn.commit()
            return cur.rowcount > 0

    # ---- per-session events ---- #
    def append_event(self, session_id: str, payload: dict):
        with self._lock:
            self.conn.execute("INSERT INTO events(session_id,payload,ts) VALUES(?,?,?)",
                              (session_id, json.dumps(payload),
                               payload.get("ts", 0)))
            self.conn.commit()

    def session_events(self, session_id: str, limit=500):
        with self._lock:
            rows = self.conn.execute(
                "SELECT payload FROM events WHERE session_id=? "
                "ORDER BY id ASC LIMIT ?", (session_id, limit)).fetchall()
        return [json.loads(r[0]) for r in rows]

    # ---- kv / audit ---- #
    def get_kv(self, key):
        with self._lock:
            r = self.conn.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        return r[0] if r else None

    def put_kv(self, key, value):
        with self._lock:
            self.conn.execute("INSERT OR REPLACE INTO kv(key,value) VALUES(?,?)",
                              (key, value))
            self.conn.commit()

    def audit(self, ts, actor, action, detail=None):
        with self._lock:
            self.conn.execute("INSERT INTO audit(ts,actor,action,detail) VALUES(?,?,?,?)",
                              (ts, actor, action,
                               json.dumps(detail) if detail is not None else None))
            self.conn.commit()

    def recent_audit(self, limit=200):
        with self._lock:
            rows = self.conn.execute(
                "SELECT ts,actor,action,detail FROM audit ORDER BY id DESC LIMIT ?",
                (limit,)).fetchall()
        out = []
        for r in rows:
            out.append({"ts": r[0], "actor": r[1], "action": r[2],
                        "detail": json.loads(r[3]) if r[3] else None})
        return out
