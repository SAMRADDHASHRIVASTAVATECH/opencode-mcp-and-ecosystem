"""Unified operator MCP server.

ONE MCP server exposing everything to OpenCode:
  google.*        Google Workspace (Gmail/Calendar/Drive/Docs/Sheets/Contacts/
                  Tasks/Chat) via official Google APIs
  discord.*       Discord via the Discord HTTP API
  voice.*         Telephony (provider-agnostic)
  meet.*          Google Meet (create via Calendar; join/participate gated by
                  a configured transport - reported honestly)
  openclaw.*      OpenClaw agent/gateway + channels
  workflow.*      Persistent multi-step workflow engine
  operator.*      Call management + follow-ups + high-level orchestration
  system.*        capability/permission/account/discovery/audit

Every connector operation is auto-registered as a typed tool with account,
authorized and reason parameters (account isolation + permission system).
"""
from __future__ import annotations

import functools
import json
from typing import Annotated, Any

try:
    from mcp.server.mcpserver import MCPServer
    _HAS_MCPSERVER = True
except ImportError:  # modern MCP SDK: FastMCP is the compatible base class
    from mcp.server.fastmcp import FastMCP as MCPServer
    _HAS_MCPSERVER = False
from pydantic import Field

from .base import Op, PY
from .registry import Runtime


def _json(d) -> str:
    return json.dumps(d, ensure_ascii=False, default=str)


class OperatorServer(MCPServer):
    def __init__(self, runtime: Runtime | None = None):
        self.rt = runtime or Runtime()
        self.workflows = self.rt.workflows
        self.calls = self.rt.calls
        _init = {
            "name": "unified-operator-mcp",
            "instructions": (
                "Autonomous communications & productivity operator. "
                "Google Workspace + Discord + Voice + Meet + OpenClaw, "
                "one MCP server. Ask in natural language. Use "
                "system.capabilities first to see configured "
                "connectors and modes. Mutating/destructive actions "
                "require authorized=true; account isolates identity."),
        }
        if _HAS_MCPSERVER:
            _init["version"] = "1.0.0"
        super().__init__(**_init)
        self._register_all()

    # guard
    def tool(self, *a, **k):
        orig = super().tool(*a, **k)

        def _g(fn):
            @functools.wraps(fn)
            def w(*args, **kw):
                try:
                    r = fn(*args, **kw)
                except Exception as e:
                    r = {"ok": False, "error": str(e), "error_type": type(e).__name__}
                return r if isinstance(r, str) else _json(r)
            return orig(w)
        return _g

    # ------------------------------------------------------------------ #
    # Auto-register connector operations as typed MCP tools.
    # ------------------------------------------------------------------ #
    def _register_connector_tools(self):
        for ns, conn in self.rt.connectors.items():
            for op_name, spec in conn.OPS.items():
                full = f"{conn.namespace}.{op_name}"
                self._register_conn_op(full, spec)

    def _register_conn_op(self, full: str, spec: Op):
        import json as _json
        arg_spec = ", ".join(
            f"{p.name}:{p.type}{'*' if p.required else ''}" for p in spec.params) or "none"
        desc_text = spec.desc + (" | args (JSON object) keys: " + arg_spec
                                 if spec.params else " | No arguments.")

        def make(full=full, desc_text=desc_text):
            def fn(
                args: Annotated[str, Field(description="Operation arguments as a "
                                                       "JSON object. See tool "
                                                       "description for the keys.")] = "{}",
                account: Annotated[str, Field(description="Optional account id for "
                                                          "this platform.")] = "",
                authorized: Annotated[bool, Field(description="Explicit "
                                                              "authorisation for "
                                                              "mutating/destructive "
                                                              "operations.")] = False,
                reason: Annotated[str, Field(description="Rationale for the "
                                                         "operation.")] = "",
            ) -> str:
                parsed = _json.loads(args) if isinstance(args, str) and args.strip() else {}
                return self.rt.call(full, parsed or {}, account=account or None,
                                    authorized=authorized, reason=reason)
            fn.__name__ = full.replace(".", "_")
            return fn
        fn = make()
        self.tool(name=full, description=desc_text)(fn)

    # ---- system / engine / high-level tools -------------------------- #
    def _register_system(self):
        @self.tool(description="Report which connectors are configured/live and "
                               "list every available operation per namespace, plus "
                               "mode (live/mock) and voice provider.")
        def system_capabilities():
            return self.rt.capability_report()

        @self.tool(description="Return the effective permission policy for an "
                               "action.")
        def system_permission(action: str, account: str = ""):
            return {"action": action, "policy": self.rt.perms.effective(action, account)}

        @self.tool(description="Set a permission override for an action (automatic|"
                               "confirmation_required|blocked).")
        def system_permission_set(action: str, policy: str, account: str = ""):
            self.rt.perms.set_override(action, policy, account)
            return self.rt.perms.snapshot()

        @self.tool(description="List accounts / identities per platform.")
        def system_accounts():
            return self.rt.accounts.accounts()

        @self.tool(description="Recent audit trail entries.")
        def system_audit(limit: int = 50):
            return {"audit": self.rt.audit.recent(limit)}

    def _register_workflow_tools(self):
        @self.tool(description="Create a persistent multi-step workflow (list of "
                               "step objects). Steps call tools like "
                               "'google.gmail.send' or run parallel/approval/notify. "
                               "See workflow.example for a template.")
        def workflow_create(name: str, steps: Any):
            return self.workflows.create(name, steps)

        @self.tool(description="A ready-made workflow template demonstrating the "
                               "cross-platform acceptance flow (call -> decide -> "
                               "calendar/email/discord/tasks).")
        def workflow_example():
            return self.workflows.create("acceptance-sarah", _acceptance_steps())

        @self.tool(description="Run (or resume) a workflow by id. Blocks until the "
                               "workflow completes, pauses on approval, or fails.")
        def workflow_run(workflow_id: str):
            return self.workflows.run(workflow_id)

        @self.tool(description="Get the current status + step results of a workflow.")
        def workflow_status(workflow_id: str):
            return self.workflows.status(workflow_id)

        @self.tool(description="Pause a running workflow.")
        def workflow_pause(workflow_id: str):
            return self.workflows.pause(workflow_id)

        @self.tool(description="Resume a paused/waiting workflow. Pass approved_step "
                               "= the approval step id you approve.")
        def workflow_resume(workflow_id: str, approved_step: str = ""):
            return self.workflows.resume(workflow_id, approved_step or None)

        @self.tool(description="Cancel a workflow.")
        def workflow_cancel(workflow_id: str):
            return self.workflows.cancel(workflow_id)

        @self.tool(description="List workflows (optionally by status).")
        def workflow_list(status: str = ""):
            return self.workflows.list(status or None)

    def _register_call_tools(self):
        @self.tool(description="Schedule an outbound call (persistent queue). Dials "
                               "at the due time and retries up to max attempts.")
        def operator_call_schedule(to: str, at: str, purpose: str = "",
                                   objective: str = "", priority: int = 0,
                                   account: str = "", max_attempts: int = 3):
            return self.calls.schedule(to, at, purpose=purpose, workflow=objective,
                                       priority=priority, account=account,
                                       objective=objective, max_attempts=max_attempts)

        @self.tool(description="Dial all due queued calls now.")
        def operator_call_run_due():
            return {"actions": self.calls.run_due()}

        @self.tool(description="List the persistent call queue.")
        def operator_call_queue():
            return self.calls.list_queue()

        @self.tool(description="Cancel a queued call.")
        def operator_call_cancel(queue_id: str):
            return self.calls.cancel_queue(queue_id)

        @self.tool(description="Call history (persistent).")
        def operator_call_history(status: str = "", limit: int = 50):
            return self.calls.history(status or None, limit)

        @self.tool(description="Create a follow-up task (e.g. 'call back tomorrow').")
        def operator_followup(summary: str, due: str = "", account: str = ""):
            return self.calls.followup(summary, due=due, account=account)

        @self.tool(description="List follow-up/open tasks.")
        def operator_tasks(status: str = "open", account: str = ""):
            return self.calls.tasks(status or None, account)

        @self.tool(description="Escalate a call to a human (transfers + follow-up).")
        def operator_escalate(call_id: str, reason: str, destination: str):
            return self.calls.escalate(call_id, reason, destination)

    def _register_orchestrate(self):
        @self.tool(description="High-level natural-language orchestration: given a "
                               "job, returns a concrete, step-by-step plan of the "
                               "exact MCP tools to run and flags what needs "
                               "confirmation/credentials. Does not execute blindly "
                               "for ambiguous jobs.")
        def operator_execute(task: str):
            return self._orchestrate(task)

        @self.tool(description="Read an inbound-call style workflow request and map "
                               "it to steps. Alias of operator.execute.")
        def operator_plan(task: str):
            return self._orchestrate(task)

    def _orchestrate(self, task: str):
        low = task.lower()
        phases = []
        if any(k in low for k in ("call", "phone", "ring")):
            phases.append({"phase": "schedule/dial", "tools": ["operator_call_schedule", "voice.call"]})
        if any(k in low for k in ("calendar", "meet", "appointment", "schedule a time", "availability")):
            phases.append({"phase": "calendar", "tools": ["google.calendar.availability", "google.calendar.create"]})
        if any(k in low for k in ("email", "gmail", "confirm", "send")):
            phases.append({"phase": "gmail", "tools": ["google.gmail.search", "google.gmail.send"]})
        if any(k in low for k in ("discord",)):
            phases.append({"phase": "discord", "tools": ["discord.send", "openclaw.channel_send"]})
        if any(k in low for k in ("sheet", "spreadsheet", "customer list")):
            phases.append({"phase": "sheets", "tools": ["google.sheets.read", "google.sheets.write"]})
        if any(k in low for k in ("meet", "join", "notes", "transcri")):
            phases.append({"phase": "meet", "tools": ["meet.capability", "meet.join", "google.docs.create"]})
        if any(k in low for k in ("task", "follow", "callback")):
            phases.append({"phase": "tasks", "tools": ["operator_followup", "google.tasks.create"]})
        return {
            "task": task,
            "plan": phases or [{"phase": "assess", "tools": ["system_capabilities"]}],
            "note": ("Run system_capabilities first. Tools marked requires_"
                     "confirmation/credentials: confirm with the user before "
                     "executing. This orchestrator decomposes clear intents into "
                     "observable steps; ambiguous jobs are escalated to the user."),
            "recommend_workflow": ("Build a persistent workflow with workflow.create "
                                   "for repeatable jobs (see workflow.example)."),
        }

    def _register_all(self):
        self._register_connector_tools()
        self._register_system()
        self._register_workflow_tools()
        self._register_call_tools()
        self._register_orchestrate()


def _acceptance_steps():
    return [
        {"id": "s0", "type": "approval", "message": "Run the acceptance workflow "
         "'call Sarah tomorrow 10am re: Friday meeting'?"},
        {"id": "s1", "tool": "voice.schedule",
         "args": {"to": "<sarah-number>", "at": "<tomorrow-10:00>",
                  "objective": "Ask if she can attend Friday's project meeting."}},
        {"id": "s2", "type": "approval", "message": "What did Sarah say? Approved => "
         "agreed, else the workflow branches (see operator.plan)."},
        {"id": "s3", "tool": "google.calendar.create",
         "args": {"summary": "Friday project meeting", "start": "<friday-time>",
                  "end": "<friday-time+1h>", "attendees": ["<sarah-email>"]}},
        {"id": "s4", "tool": "google.gmail.send",
         "args": {"to": "<sarah-email>", "subject": "Meeting confirmation",
                  "body": "Confirmed: Friday project meeting."}},
        {"id": "s5", "type": "notify", "channel": "discord", "to": "#general",
         "text": "Meeting scheduled with Sarah."},
    ]
