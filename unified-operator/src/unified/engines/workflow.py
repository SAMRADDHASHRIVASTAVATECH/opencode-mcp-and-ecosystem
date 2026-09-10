"""Persistent workflow engine.

Workflow definition (JSON) is a list of steps:
  { "id": "...", "tool": "google.gmail.send", "args": {...},
    "when": [ {"key":"steps.grep.count","exists":true}, ],   # optional gate
    "retries": 2, "timeout_s": 120, "account": "..." }
Special step types:
  { "type":"parallel", "id":"...", "steps": [ {tool,args,id,...}, ... ] }
  { "type":"approval", "id":"...", "message":"...", "authorized":false }
  { "type":"notify", "id":"...", "channel": "discord|gmail|...",
    "to":"...", "text":"..." }

Engine state is persisted; a workflow can be paused (on approval or manually)
and resumed after a restart. Results of each step are stored under
workflow.state.steps[<id>] so later steps can gate on them.
"""
from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone

from ..observability import new_id


def _now():
    return datetime.now(timezone.utc).isoformat()


class WorkflowEngine:
    def __init__(self, runtime, dispatch=None):
        self.runtime = runtime
        self.store = runtime.store
        # dispatch(action,args,account)->result ; defaults to runtime.call
        self.dispatch = dispatch or (lambda action, args, account, auth, reason:
                                     runtime.call(action, args, account=account,
                                                  authorized=auth, reason=reason))
        self._lock = threading.Lock()

    # ---- lifecycle --------------------------------------------------- #
    def create(self, name: str, steps: list, definition_meta=None) -> dict:
        wid = new_id("wf")
        self.store.put_workflow(wid, name, {"steps": steps,
                                            "meta": definition_meta or {}})
        return {"workflow_id": wid, "name": name, "status": "created",
                "steps": len(steps)}

    def run(self, workflow_id: str, *, resume=False) -> dict:
        wf = self.store.get_workflow(workflow_id)
        if not wf:
            raise ValueError(f"unknown workflow {workflow_id}")
        self.store.update_workflow(workflow_id, status="running")
        with self._lock:
            self._execute(wf)
        return self.status(workflow_id)

    def _execute(self, wf):
        wid = wf["workflow_id"]
        defs = wf["definition"]["steps"]
        state = self._load_state(wf)
        results = state.setdefault("steps", {})
        state.setdefault("pointer", state.get("pointer", 0))
        # for simplicity rerun remaining steps from pointer when resume
        for idx in range(state["pointer"], len(defs)):
            step = defs[idx]
            if self.store.get_workflow(wid).get("status") == "paused":
                break
            self.store.update_workflow(wid, _state={"pointer": idx})
            try:
                out = self._run_step(step, results)
                results[step["id"]] = out
                if out.get("_pause"):
                    self.store.update_workflow(wid, status="paused",
                                               _state={"steps": results,
                                                       "pointer": idx + 1})
                    return
            except _Approval as ap:
                results[step["id"]] = {"status": "waiting_approval",
                                       "message": ap.message}
                self.store.update_workflow(wid, status="waiting_approval",
                                           _state={"steps": results,
                                                   "pointer": idx,
                                                   "pending_approval": step["id"]})
                return
            except Exception as e:
                results[step["id"]] = {"status": "error", "error": str(e)}
                self.store.update_workflow(wid, status="failed",
                                           _state={"steps": results})
                return
        self.store.update_workflow(wid, status="succeeded",
                                   _state={"steps": results,
                                           "pointer": len(defs)})

    def _load_state(self, wf):
        raw = wf.get("state") or {}
        try:
            return json.loads(raw) if isinstance(raw, str) else raw
        except Exception:
            return {}

    def _run_step(self, step, results):
        typ = step.get("type", "tool")
        if typ == "parallel":
            return self._parallel(step, results)
        if typ == "approval":
            if step.get("authorized"):
                return {"status": "approved"}
            raise _Approval(step.get("message", "Human approval required"))
        if typ == "notify":
            return self._notify(step)
        # tool step
        gate = self._gate(step.get("when", []), results)
        if gate is not None and not gate:
            return {"status": "skipped", "reason": "condition not met"}
        return self._tool(step, results)

    def _tool(self, step, results):
        tool = step.get("tool")
        args = step.get("args", {})
        acct = step.get("account")
        retries = int(step.get("retries", 0))
        auth = bool(step.get("authorized"))
        reason = step.get("reason", "workflow step")
        last = None
        for attempt in range(retries + 1):
            try:
                r = self.dispatch(tool, args, acct, auth, reason)
                return {"status": "ok", "attempt": attempt + 1, "result": r}
            except Exception as e:
                last = {"status": "error", "attempt": attempt + 1, "error": str(e)}
        return last

    def _parallel(self, step, results):
        outs = []
        for sub in step.get("steps", []):
            try:
                outs.append({sub.get("id"): self._run_step(sub, results)})
            except _Approval as a:
                outs.append({sub.get("id"): {"status": "waiting_approval",
                                             "message": a.message}})
            except Exception as e:
                outs.append({sub.get("id"): {"status": "error", "error": str(e)}})
        return {"status": "ok", "results": outs}

    def _notify(self, step):
        # Route a notification through the messaging platforms.
        channel = step.get("channel")
        to = step.get("to")
        text = step.get("text")
        try:
            if channel == "gmail":
                res = self.dispatch("google.gmail.send",
                                    {"to": to, "subject": step.get("subject",
                                                                   "Notification"),
                                     "body": text}, None, False, "workflow notify")
            else:
                # default: discord via openclaw
                res = self.dispatch("openclaw.channel_send",
                                    {"channel": "discord", "to": to, "text": text},
                                    None, False, "workflow notify")
            if isinstance(res, dict) and res.get("ok") is False:
                return {"status": "notify_failed", "error": res.get("error")}
            return {"status": "ok", "result": res}
        except Exception as e:
            return {"status": "notify_failed", "error": str(e)}

    def _gate(self, when, results):
        """when: list of conditions, all must hold (AND). None -> run."""
        for cond in when:
            val = self._deref(cond.get("key"), results)
            if cond.get("exists") is not None:
                if bool(cond["exists"]) != (val is not None and val != "" and val != []):
                    return False
            if "eq" in cond and val != cond["eq"]:
                return False
            if "ne" in cond and val == cond["ne"]:
                return False
            if cond.get("truthy") is True and not val:
                return False
        return True

    @staticmethod
    def _deref(key, results):
        cur = results
        for part in key.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur

    # ---- controls ---------------------------------------------------- #
    def pause(self, workflow_id):
        self.store.update_workflow(workflow_id, status="paused")
        return self.status(workflow_id)

    def resume(self, workflow_id, approved_step=None):
        wf = self.store.get_workflow(workflow_id)
        defs = wf["definition"]["steps"]
        st = self._load_state(wf)
        pending = st.get("pending_approval")
        if pending and approved_step == pending:
            steps = st.get("steps", {})
            steps[pending] = {"status": "approved"}
            # advance pointer past the approval step so it is not re-run
            idx = next((i for i, s in enumerate(defs) if s.get("id") == pending), 0)
            st["pointer"] = max(st.get("pointer", 0), idx + 1)
            st["steps"] = steps
            st.pop("pending_approval", None)
            self.store.update_workflow(workflow_id, status="running", _state=st)
        else:
            self.store.update_workflow(workflow_id, status="running")
        return self.run(workflow_id, resume=True)

    def cancel(self, workflow_id):
        self.store.update_workflow(workflow_id, status="cancelled")
        return self.status(workflow_id)

    def status(self, workflow_id):
        wf = self.store.get_workflow(workflow_id)
        if not wf:
            raise ValueError(f"unknown workflow {workflow_id}")
        return {"workflow_id": wf["workflow_id"], "name": wf["name"],
                "status": wf["status"], "updated": wf["updated"],
                "state": self._load_state(wf)}

    def list(self, status=None):
        return self.store.list_workflows(status=status)

    def add_task(self, summary, due=None, account="", source="", related_id=""):
        tid = new_id("task")
        self.store.add_task(tid, summary, due=due, account=account,
                            source=source, related_id=related_id)
        return {"task_id": tid, "summary": summary, "due": due}

    def complete_task(self, task_id):
        self.store.update_task(task_id, status="completed")
        return {"task_id": task_id, "completed": True}

    def list_tasks(self, status=None, account=""):
        return self.store.list_tasks(status=status, account=account)


class _Approval(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
