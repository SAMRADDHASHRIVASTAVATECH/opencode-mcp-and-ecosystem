"""Persistent, versioned, auditable experience-memory store.

SQLite (workspace files) holds lessons, experiences and an audit/undo log. Every
mutating write is versioned and logged so changes are reversible. A JSON export
allows portable snapshots in the workspace.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS lessons(
  id TEXT PRIMARY KEY,
  identity TEXT,
  payload TEXT NOT NULL,
  created REAL, updated REAL, version INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS experiences(
  id TEXT PRIMARY KEY,
  payload TEXT NOT NULL,
  ts REAL
);
CREATE TABLE IF NOT EXISTS audit(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts REAL, action TEXT, entity TEXT, entity_id TEXT, before TEXT, after TEXT
);
CREATE TABLE IF NOT EXISTS kv(key TEXT PRIMARY KEY, value TEXT);
CREATE INDEX IF NOT EXISTS idx_lessons_identity ON lessons(identity);
"""


def gen_id(prefix="lsn"):
    return f"{prefix}_{int(time.time()*1000)}_{id(object()) & 0xFFFF}"


class Store:
    def __init__(self, db_path: str):
        self.path = db_path
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        with self._lock:
            self.conn.executescript(SCHEMA)
            self.conn.commit()
        if self.get_kv("head_version") is None:
            self.put_kv("head_version", "0")

    def close(self):
        with self._lock:
            try:
                self.conn.close()
            except Exception:
                pass

    # ---- kv / versions ----
    def get_kv(self, key):
        with self._lock:
            r = self.conn.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        return r[0] if r else None

    def put_kv(self, key, value):
        with self._lock:
            self.conn.execute("INSERT OR REPLACE INTO kv(key,value) VALUES(?,?)",
                              (key, value))
            self.conn.commit()

    def _bump_version(self):
        v = int(self.get_kv("head_version") or "0") + 1
        self.put_kv("head_version", str(v))
        return v

    # ---- audit ----
    def log(self, action, entity, entity_id, before=None, after=None):
        with self._lock:
            self.conn.execute(
                "INSERT INTO audit(ts,action,entity,entity_id,before,after) "
                "VALUES(?,?,?,?,?,?)",
                (time.time(), action, entity, entity_id,
                 json.dumps(before) if before is not None else None,
                 json.dumps(after) if after is not None else None))
            self.conn.commit()

    def recent_audit(self, limit=200):
        with self._lock:
            rows = self.conn.execute(
                "SELECT ts,action,entity,entity_id,before,after FROM audit "
                "ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        out = []
        for ts, action, entity, eid, before, after in rows:
            out.append({"ts": ts, "action": action, "entity": entity,
                        "entity_id": eid,
                        "before": json.loads(before) if before else None,
                        "after": json.loads(after) if after else None})
        return out

    def _restore_lesson(self, eid, before):
        if not before:
            return False
        self.conn.execute(
            "INSERT OR REPLACE INTO lessons(id,identity,payload,created,updated,"
            "version) VALUES(?,?,?,?,?,?)",
            (eid, before.get("identity", before["statement"].lower()),
             json.dumps(before), before.get("created", time.time()),
             before.get("updated", time.time()), before.get("version", 1)))
        return True

    def undo_last(self):
        """Reversibility: roll back the most recent reversible lesson-mutating
        change (scanning past non-lesson / create-only rows)."""
        outcome = None
        with self._lock:
            rows = self.conn.execute(
                "SELECT id,action,entity,entity_id,before,after FROM audit "
                "ORDER BY id DESC").fetchall()
            for rid, action, entity, eid, before, after in rows:
                before = json.loads(before) if before else None
                after = json.loads(after) if after else None
                if entity != "lesson":
                    continue
                if action == "lesson.create":
                    self.conn.execute("DELETE FROM lessons WHERE id=?", (eid,))
                    outcome = {"undone": action, "entity_id": eid}
                    break
                if action in ("lesson.update", "lesson.archive", "lesson.delete",
                              "lesson.promote"):
                    if self._restore_lesson(eid, before):
                        outcome = {"undone": action, "entity_id": eid}
                        break
            if outcome:
                self.conn.commit()
        if outcome:
            # audit outside the lock to avoid a non-reentrant deadlock
            self.log("undo", "lesson", outcome["entity_id"],
                     before={"note": "see prior audit row"},
                     after={"restored": True})
        return outcome

    # ---- lessons ----
    def put_lesson(self, lesson: dict):
        # strip transient underscore-prefixed markers (e.g. "_created") before store
        clean = {k: v for k, v in lesson.items() if not k.startswith("_")}
        with self._lock:
            self.conn.execute(
                "INSERT OR REPLACE INTO lessons(id,identity,payload,created,updated,"
                "version) VALUES(?,?,?,?,?,?)",
                (clean["id"], clean.get("identity", clean["statement"].lower()),
                 json.dumps(clean), clean.get("created", time.time()),
                 clean.get("updated", time.time()), clean.get("version", 1)))
            self.conn.commit()

    def get_lesson(self, lesson_id):
        with self._lock:
            r = self.conn.execute("SELECT payload FROM lessons WHERE id=?",
                                  (lesson_id,)).fetchone()
        return json.loads(r[0]) if r else None

    def list_lessons(self, status=None):
        with self._lock:
            if status:
                rows = self.conn.execute(
                    "SELECT payload FROM lessons").fetchall()
                out = [json.loads(r[0]) for r in rows]
                return [l for l in out if l.get("status") == status]
            rows = self.conn.execute("SELECT payload FROM lessons").fetchall()
        return [json.loads(r[0]) for r in rows]

    def delete_lesson_row(self, lesson_id):
        with self._lock:
            self.conn.execute("DELETE FROM lessons WHERE id=?", (lesson_id,))
            self.conn.commit()

    # ---- experiences ----
    def put_experience(self, exp: dict):
        with self._lock:
            self.conn.execute(
                "INSERT OR REPLACE INTO experiences(id,payload,ts) VALUES(?,?,?)",
                (exp["id"], json.dumps(exp), exp.get("ts", time.time())))
            self.conn.commit()

    def list_experiences(self, limit=200):
        with self._lock:
            rows = self.conn.execute(
                "SELECT payload FROM experiences ORDER BY ts DESC LIMIT ?",
                (limit,)).fetchall()
        return [json.loads(r[0]) for r in rows]

    # ---- json snapshot (portable, versioned, in-workspace) ----
    def export_json(self) -> dict:
        return {"format_version": 1, "exported": time.time(),
                "lessons": self.list_lessons(),
                "experiences": self.list_experiences()}

    def import_json(self, data: dict):
        for l in data.get("lessons", []):
            if l.get("id"):
                self.put_lesson(l)
        for e in data.get("experiences", []):
            if e.get("id"):
                self.put_experience(e)
        return {"lessons": len(data.get("lessons", [])),
                "experiences": len(data.get("experiences", []))}
