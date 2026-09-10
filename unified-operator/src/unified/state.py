"""SQLite persistence that survives restarts: calls, call queue, workflows,
tasks/follow-ups, audit. All engines write here so nothing is lost on restart.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings


def _now():
    return datetime.now(timezone.utc).isoformat()


SCHEMA = """
CREATE TABLE IF NOT EXISTS audit(
  rowid INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT, request_id TEXT, session_id TEXT, call_id TEXT, workflow_id TEXT,
  platform TEXT, account TEXT, action TEXT, status TEXT, detail TEXT);
CREATE TABLE IF NOT EXISTS calls(
  call_id TEXT PRIMARY KEY, direction TEXT, target TEXT, caller TEXT,
  phone TEXT, account TEXT, status TEXT, start_time TEXT, end_time TEXT,
  transcript TEXT, summary TEXT, intent TEXT, outcome TEXT,
  follow_up TEXT, error TEXT, escalated INTEGER, payload TEXT);
CREATE TABLE IF NOT EXISTS call_queue(
  id TEXT PRIMARY KEY, priority INTEGER, schedule TEXT, status TEXT,
  retry_count INTEGER, max_attempts INTEGER, retry_delay_s INTEGER,
  target TEXT, purpose TEXT, workflow TEXT, result TEXT, follow_up TEXT,
  account TEXT, payload TEXT);
CREATE TABLE IF NOT EXISTS workflows(
  workflow_id TEXT PRIMARY KEY, name TEXT, status TEXT, definition TEXT,
  created TEXT, updated TEXT, state TEXT);
CREATE TABLE IF NOT EXISTS tasks(
  task_id TEXT PRIMARY KEY, summary TEXT, due TEXT, status TEXT,
  account TEXT, source TEXT, related_id TEXT, created TEXT);
"""


class StateStore:
    def __init__(self, settings: Settings):
        self.path = Path(settings.db_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        with self._lock:
            self.conn.executescript(SCHEMA)
            self.conn.commit()

    # ---- calls ------------------------------------------------------ #
    CALL_COLS = ("call_id", "direction", "target", "caller", "phone", "account",
                 "status", "start_time", "end_time", "transcript", "summary",
                 "intent", "outcome", "follow_up", "error", "escalated", "payload")

    def upsert_call(self, call_id, **fields):
        data = {"call_id": call_id}
        for k, v in fields.items():
            data[k] = json.dumps(v) if isinstance(v, (dict, list)) else v
        cols = [c for c in self.CALL_COLS if c in data]
        if not cols:
            return
        placeholders = ",".join(":" + c for c in cols)
        colnames = ",".join(cols)
        # updates only for mutable columns (exclude keys that should not clobber
        # on upsert: call_id, direction, target, caller, phone, account, start_time)
        upd = ",".join(f"{c}=excluded.{c}" for c in cols
                       if c not in ("call_id", "direction", "target", "caller",
                                    "phone", "account", "start_time"))
        sql = f"INSERT INTO calls({colnames}) VALUES({placeholders})"
        if upd:
            sql += " ON CONFLICT(call_id) DO UPDATE SET " + upd
        with self._lock:
            self.conn.execute(sql, data)
            self.conn.commit()

    def get_call(self, call_id):
        with self._lock:
            r = self.conn.execute("SELECT * FROM calls WHERE call_id=?",
                                  (call_id,)).fetchone()
        return dict(r) if r else None

    def list_calls(self, status=None, limit=100):
        with self._lock:
            if status:
                r = self.conn.execute("SELECT * FROM calls WHERE status=? "
                                      "ORDER BY rowid DESC LIMIT ?",
                                      (status, limit)).fetchall()
            else:
                r = self.conn.execute("SELECT * FROM calls ORDER BY rowid DESC "
                                      "LIMIT ?", (limit,)).fetchall()
        return [dict(x) for x in r]

    # ---- call queue -------------------------------------------------- #
    def enqueue(self, qid, priority, schedule, target, purpose, workflow,
                account="", max_attempts=3, retry_delay_s=300, payload=None):
        with self._lock:
            self.conn.execute(
                "INSERT INTO call_queue(id,priority,schedule,status,retry_count,"
                "max_attempts,retry_delay_s,target,purpose,workflow,result,"
                "follow_up,account,payload) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (qid, priority, schedule, "queued", 0, max_attempts, retry_delay_s,
                 target, purpose, workflow, None, None, account,
                 json.dumps(payload or {})))
            self.conn.commit()

    def queue_ready(self, now_iso):
        with self._lock:
            r = self.conn.execute(
                "SELECT * FROM call_queue WHERE status='queued' AND "
                "(schedule IS NULL OR schedule<=?) ORDER BY priority DESC, "
                "rowid ASC", (now_iso,)).fetchall()
        return [dict(x) for x in r]

    def update_queue(self, qid, **fields):
        with self._lock:
            sets = ", ".join(f"{k}=?" for k in fields)
            vals = list(fields.values())
            self.conn.execute(f"UPDATE call_queue SET {sets} WHERE id=?", (*vals, qid))
            self.conn.commit()

    def list_queue(self):
        with self._lock:
            r = self.conn.execute("SELECT * FROM call_queue ORDER BY rowid DESC "
                                  "LIMIT 200").fetchall()
        return [dict(x) for x in r]

    # ---- workflows --------------------------------------------------- #
    def put_workflow(self, workflow_id, name, definition):
        with self._lock:
            self.conn.execute(
                "INSERT OR REPLACE INTO workflows(workflow_id,name,status,definition,"
                "created,updated,state) VALUES(?,?,?,?,?,?,?)",
                (workflow_id, name, "created", json.dumps(definition), _now(), _now(), "{}"))
            self.conn.commit()

    def update_workflow(self, workflow_id, **fields):
        with self._lock:
            cur = self.conn.execute("SELECT state FROM workflows WHERE workflow_id=?",
                                    (workflow_id,)).fetchone()
            state = json.loads(cur["state"]) if cur and cur["state"] else {}
            state.update(fields.pop("_state", {}))
            fields["updated"] = _now()
            fields["state"] = json.dumps(state)
            sets = ", ".join(f"{k}=?" for k in fields)
            self.conn.execute(f"UPDATE workflows SET {sets} WHERE workflow_id=?",
                              (*fields.values(), workflow_id))
            self.conn.commit()

    def get_workflow(self, workflow_id):
        with self._lock:
            r = self.conn.execute("SELECT * FROM workflows WHERE workflow_id=?",
                                  (workflow_id,)).fetchone()
        d = dict(r) if r else None
        if d:
            try:
                d["definition"] = json.loads(d["definition"])
            except Exception:
                pass
        return d

    def list_workflows(self, status=None, limit=100):
        with self._lock:
            if status:
                r = self.conn.execute("SELECT * FROM workflows WHERE status=? "
                                      "ORDER BY rowid DESC LIMIT ?", (status, limit)).fetchall()
            else:
                r = self.conn.execute("SELECT * FROM workflows ORDER BY rowid DESC "
                                      "LIMIT ?", (limit,)).fetchall()
        return [dict(x) for x in r]

    # ---- tasks / follow-ups ------------------------------------------ #
    def add_task(self, task_id, summary, due=None, account="", source="", related_id=""):
        with self._lock:
            self.conn.execute(
                "INSERT OR REPLACE INTO tasks(task_id,summary,due,status,account,"
                "source,related_id,created) VALUES(?,?,?,?,?,?,?,?)",
                (task_id, summary, due, "open", account, source, related_id, _now()))
            self.conn.commit()

    def update_task(self, task_id, status=None, due=None):
        with self._lock:
            sets, vals = [], []
            if status is not None:
                sets.append("status=?"); vals.append(status)
            if due is not None:
                sets.append("due=?"); vals.append(due)
            if sets:
                self.conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE task_id=?",
                                  (*vals, task_id))
                self.conn.commit()

    def list_tasks(self, status=None, account="", limit=200):
        q = "SELECT * FROM tasks WHERE 1=1"
        args = []
        if status:
            q += " AND status=?"; args.append(status)
        if account:
            q += " AND account=?"; args.append(account)
        q += " ORDER BY rowid DESC LIMIT ?"; args.append(limit)
        with self._lock:
            r = self.conn.execute(q, args).fetchall()
        return [dict(x) for x in r]
