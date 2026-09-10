"""Observability: structured logging, request/session/call/workflow ids,
and an audit trail persisted to SQLite. Never logs credentials."""
from __future__ import annotations

import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _redact(obj):
    """Recursively redact common secret keys before logging/auditing."""
    if isinstance(obj, dict):
        return {k: (_redact(v) if k not in ("token", "access_token", "refresh_token",
                                            "password", "secret", "api_key", "bot_token",
                                            "client_secret", "key") else "***redacted***")
                for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_redact(x) for x in obj]
    return obj


class OperatorLog:
    def __init__(self, name="unified-operator"):
        self.log = logging.getLogger(name)
        if not self.log.handlers:
            self.log.setLevel(logging.DEBUG)
            fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
            sh = logging.StreamHandler(sys.stderr)
            sh.setFormatter(fmt)
            self.log.addHandler(sh)

    def bind(self, *, request_id=None, session_id=None, call_id=None,
             workflow_id=None, **kv):
        return _Bound(self.log, request_id=request_id, session_id=session_id,
                      call_id=call_id, workflow_id=workflow_id, kv=kv)

    def info(self, msg): self.log.info(msg)
    def debug(self, msg): self.log.debug(msg)
    def warning(self, msg): self.log.warning(msg)
    def error(self, msg): self.log.error(msg)


class _Bound:
    def __init__(self, log, **ctx):
        self.log = log
        self.ctx = ctx

    def _msg(self, msg, level):
        parts = " ".join(f"{k}={v}" for k, v in self.ctx["kv"].items() if k != "kv")
        base = " ".join(x for x in [f"{k}={v}" for k, v in self.ctx.items()
                                    if k not in ("kv",) and v] + [parts] if x)
        return f"{msg} | {base}" if base else msg

    def info(self, msg): self.log.info(self._msg(msg, "info"))
    def debug(self, msg): self.log.debug(self._msg(msg, "debug"))
    def warning(self, msg): self.log.warning(self._msg(msg, "warn"))
    def error(self, msg): self.log.error(self._msg(msg, "error"))


class Audit:
    """Persistent audit trail in SQLite (observer-neutral storage)."""
    def __init__(self, db_conn):
        self.conn = db_conn

    def record(self, *, request_id="", session_id="", account="", platform="",
               action="", status="", detail=None, call_id="", workflow_id=""):
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "request_id": request_id, "session_id": session_id,
            "call_id": call_id, "workflow_id": workflow_id,
            "platform": platform, "account": account, "action": action,
            "status": status,
            "detail": json.dumps(_redact(detail or {}), default=str),
        }
        try:
            self.conn.execute(
                "INSERT INTO audit(ts,request_id,session_id,call_id,workflow_id,"
                "platform,account,action,status,detail) VALUES "
                "(:ts,:request_id,:session_id,:call_id,:workflow_id,:platform,"
                ":account,:action,:status,:detail)", row)
            self.conn.commit()
        except Exception:
            pass
        return row

    def recent(self, limit=100):
        try:
            cur = self.conn.execute(
                "SELECT ts,request_id,platform,account,action,status FROM audit "
                "ORDER BY rowid DESC LIMIT ?", (limit,))
            return [dict(zip(["ts", "request_id", "platform", "account",
                              "action", "status"], r)) for r in cur.fetchall()]
        except Exception:
            return []
