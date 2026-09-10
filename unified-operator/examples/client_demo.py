"""End-to-end MCP *client* demo (offline by default) for the unified operator.

Shows: capability discovery, a Google mock call, a persistent workflow built &
run, and call scheduling. OpenCode connects to the same MCP server.
Run:  python examples/client_demo.py            (offline)
      UNIFIED_OFFLINE=0 python examples/client_demo.py   (live, with creds)
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _cmd():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    env = dict(os.environ)
    env["PYTHONPATH"] = os.path.join(root, "src") + os.pathsep + env.get("PYTHONPATH", "")
    args = [sys.executable, "-m", "unified.main"]
    if os.environ.get("UNIFIED_OFFLINE", "1") != "0":
        args.append("--offline")
    return StdioServerParameters(command=args[0], args=args[1:], env=env)


async def main():
    async with stdio_client(_cmd()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"[client] connected; {len(tools.tools)} tools\n")

            async def call(tool, **kw):
                r = await session.call_tool(tool, kw)
                return "\n".join(c.text or "" for c in r.content if hasattr(c, "text"))

            print("== system_capabilities (namespaces) ==")
            cap = json.loads(await call("system_capabilities"))
            print("mode:", cap["mode"], "| connectors:", list(cap.keys())[:-1])

            print("\n== google.gmail.search (offline mock, flagged) ==")
            print(await call("google.gmail.search", args='{"query":"is:unread"}'))

            print("\n== workflow: build a short cross-platform workflow and run ==")
            steps = [
                {"id": "a", "type": "approval", "message": "Proceed with demo workflow?"},
                {"id": "s1", "tool": "google.calendar.availability",
                 "args": {"timeMin": "2026-09-08T00:00:00Z",
                          "timeMax": "2026-09-08T23:00:00Z"}},
                {"id": "s2", "tool": "google.gmail.send", "authorized": True,
                 "args": {"to": "demo@example.com", "subject": "Done",
                          "body": "Workflow executed."}},
            ]
            c = json.loads(await call("workflow_create", name="demo", steps=json.dumps(steps)))
            wid = c["workflow_id"]
            print("created", wid)
            print(await call("workflow_run", workflow_id=wid))   # will pause on approval
            print(await call("workflow_status", workflow_id=wid))
            print(await call("workflow_resume", workflow_id=wid, approved_step="a"))
            print("final:", await call("workflow_status", workflow_id=wid))

            print("\n== operator_call_schedule (persistent) ==")
            print(await call("operator_call_schedule", to="+15550000000",
                             at="2026-09-09T09:00:00Z", purpose="confirm"))
            print("queue:", await call("operator_call_queue"))


if __name__ == "__main__":
    asyncio.run(main())
