"""Call management engine: persistent calls + queue + follow-ups + retry.

Holds authoritative call state (survives restart via StateStore). A scheduler
worker (run_due) fires queued outbound calls at their due time through the
voice connector, applies retry/backoff up to max attempts, records outcomes and
creates follow-up tasks. No information is shared between concurrent calls.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ..observability import new_id


def _now():
    return datetime.now(timezone.utc)


def iso(dt=None):
    return (dt or _now()).isoformat()


class CallEngine:
    CALL_STATES = ["queued", "scheduled", "dialing", "ringing", "answered",
                   "greeting", "listening", "speaking", "processing",
                   "executing", "waiting", "transferring", "transferred",
                   "voicemail", "busy", "no_answer", "failed", "completed",
                   "escalated"]

    def __init__(self, runtime):
        self.runtime = runtime
        self.store = runtime.store
        self.settings = runtime.settings

    # ---- records ----------------------------------------------------- #
    def new_call(self, direction, target, *, caller="", phone="", account=""):
        cid = new_id("call")
        now = iso()
        self.store.upsert_call(cid, direction=direction, target=target,
                               caller=caller, phone=phone, account=account,
                               status="created", start_time=now)
        return self.store.get_call(cid)

    def update_call(self, call_id, **fields):
        self.store.upsert_call(call_id, **fields)
        return self.store.get_call(call_id)

    def history(self, status=None, limit=100):
        return self.store.list_calls(status=status, limit=limit)

    # ---- queue ------------------------------------------------------- #
    def schedule(self, to, at_iso, *, purpose="", workflow="", priority=0,
                 account="", objective="", max_attempts=None, retry_delay_s=None,
                 call_id=None):
        qid = call_id or new_id("q")
        self.store.enqueue(
            qid, priority=priority, schedule=at_iso, target=to, purpose=purpose,
            workflow=workflow, account=account,
            max_attempts=max_attempts or self.settings.call_max_attempts,
            retry_delay_s=retry_delay_s or self.settings.call_retry_delay_s,
            payload={"objective": objective})
        return {"queue_id": qid, "to": to, "at": at_iso, "status": "queued"}

    def list_queue(self):
        return self.store.list_queue()

    def cancel_queue(self, queue_id):
        self.store.update_queue(queue_id, status="cancelled")
        return {"queue_id": queue_id, "cancelled": True}

    def run_due(self):
        """Dial every queued item whose schedule <= now. Returns actions taken."""
        taken = []
        for item in self.store.queue_ready(iso()):
            taken.append(self._dial(item))
        return taken

    def _dial(self, item):
        qid = item["id"]
        payload = json_load(item.get("payload"))
        self.store.update_queue(qid, status="dialing")
        outcome = None
        try:
            res = self.runtime.call("voice.call",
                                    {"to": item["target"],
                                     "objective": (payload or {}).get("objective")},
                                    account=item.get("account") or None,
                                    authorized=True, reason="scheduled outbound call")
            # map provider outcome
            status = (res.get("result") or {}).get("status", "completed")
            outcome = self._normalise_outcome(status)
        except Exception as e:
            self.store.update_queue(qid, status="failed",
                                    result=f"dial error: {e}")
            return {"queue_id": qid, "outcome": "failed", "error": str(e)}
        # record call
        cid = new_id("call")
        self.store.upsert_call(cid, direction="outbound", target=item["target"],
                               account=item.get("account"), status=outcome,
                               start_time=iso(), outcome=outcome)
        if outcome in ("no_answer", "busy", "voicemail", "failed"):
            retry_count = int(item.get("retry_count", 0)) + 1
            if retry_count < int(item.get("max_attempts", 3)):
                delay = int(item.get("retry_delay_s", 300))
                due = iso(_now() + timedelta(seconds=delay))
                self.store.update_queue(qid, retry_count=retry_count,
                                        schedule=due, status="queued")
                self.store.update_queue(qid, result=f"retry scheduled ({outcome})")
                return {"queue_id": qid, "call_id": cid, "outcome": outcome,
                        "retry": True, "retry_at": due}
            self.store.update_queue(qid, status="exhausted", result=outcome)
            self.followup(f"Reached max attempts for {item['target']} ({outcome})",
                          account=item.get("account"), related=cid)
            return {"queue_id": qid, "call_id": cid, "outcome": outcome,
                    "exhausted": True}
        self.store.update_queue(qid, status="completed", result=outcome)
        return {"queue_id": qid, "call_id": cid, "outcome": outcome}

    def _normalise_outcome(self, s):
        s = (s or "").lower().replace(" ", "_")
        if s in self.CALL_STATES:
            return s
        if s in ("answered", "ok", "completed"):
            return "completed"
        if s in ("no_answer", "noanswer"):
            return "no_answer"
        return s if s in self.CALL_STATES else "completed"

    # ---- follow-up / escalation -------------------------------------- #
    def followup(self, summary, *, due=None, account="", related=""):
        from ..observability import new_id
        tid = new_id("task")
        due_iso = None
        if due:
            due_iso = due if isinstance(due, str) else iso(due)
        self.store.add_task(tid, summary, due=due_iso, account=account,
                            source="followup", related_id=related)
        return {"task_id": tid, "summary": summary, "due": due_iso}

    def escalate(self, call_id, reason, destination):
        self.update_call(call_id, status="escalated", error=reason,
                         escalated=1)
        self.followup(f"Escalated call {call_id} to {destination}: {reason}",
                      related=call_id)
        # transfer if a destination/transport is available
        return {"call_id": call_id, "escalated": True, "destination": destination}

    def tasks(self, status=None, account=""):
        return self.store.list_tasks(status=status, account=account)


def json_load(s):
    import json
    if not s:
        return {}
    if isinstance(s, dict):
        return s
    try:
        return json.loads(s)
    except Exception:
        return {}
