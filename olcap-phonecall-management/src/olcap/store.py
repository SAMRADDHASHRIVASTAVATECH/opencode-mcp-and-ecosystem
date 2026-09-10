"""Persistent state store (SQLite). Survives restart so call history, summaries,
policies and audit persist across service/reboot restarts (spec sections 15, 17).
Only metadata/transcripts are stored - never raw audio unless record_calls enabled
(and even then only if the user explicitly enables it).
"""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS calls(
  call_id TEXT PRIMARY KEY,
  payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS policies(
  name TEXT PRIMARY KEY,
  payload TEXT NOT NULL
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
            self.conn.close()

    # ---- calls ------------------------------------------------------- #
    def put_call(self, record: dict):
        with self._lock:
            self.conn.execute("INSERT OR REPLACE INTO calls(call_id,payload) VALUES(?,?)",
                              (record["call_id"], json.dumps(record)))
            self.conn.commit()

    def get_call(self, call_id: str) -> dict | None:
        with self._lock:
            r = self.conn.execute("SELECT payload FROM calls WHERE call_id=?",
                                  (call_id,)).fetchone()
        return json.loads(r[0]) if r else None

    def list_calls(self, limit=200):
        with self._lock:
            rows = self.conn.execute(
                "SELECT payload FROM calls ORDER BY rowid DESC LIMIT ?",
                (limit,)).fetchall()
        return [json.loads(r[0]) for r in rows]

    # ---- policies ---------------------------------------------------- #
    def put_policy(self, name: str, policy: dict):
        with self._lock:
            self.conn.execute("INSERT OR REPLACE INTO policies(name,payload) VALUES(?,?)",
                              (name, json.dumps(policy)))
            self.conn.commit()

    def get_policy(self, name: str) -> dict | None:
        with self._lock:
            r = self.conn.execute("SELECT name,payload FROM policies WHERE name=?",
                                  (name,)).fetchone()
        if not r:
            return None
        p = json.loads(r[1])
        p["name"] = r[0]
        return p

    def list_policies(self):
        with self._lock:
            rows = self.conn.execute("SELECT name,payload FROM policies").fetchall()
        out = []
        for name, payload in rows:
            p = json.loads(payload)
            p["name"] = name
            out.append(p)
        return out

    def delete_policy(self, name: str) -> bool:
        with self._lock:
            cur = self.conn.execute("DELETE FROM policies WHERE name=?", (name,))
            self.conn.commit()
            return cur.rowcount > 0

    # ---- audit ------------------------------------------------------- #
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
            d = json.loads(r[3]) if r[3] else None
            out.append({"ts": r[0], "actor": r[1], "action": r[2], "detail": d})
        return out

    # ---- kv ---------------------------------------------------------- #
    def get_kv(self, key):
        with self._lock:
            r = self.conn.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        return r[0] if r else None

    def put_kv(self, key, value):
        with self._lock:
            self.conn.execute("INSERT OR REPLACE INTO kv(key,value) VALUES(?,?)",
                              (key, value))
            self.conn.commit()
