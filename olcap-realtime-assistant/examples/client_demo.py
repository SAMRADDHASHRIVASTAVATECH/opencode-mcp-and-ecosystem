"""End-to-end MCP client demo for the OLCAP realtime assistant.

Demonstrates mode/session flow, practice + meeting analysis (deterministic),
transcript/context handling, and honest health reporting. No audio/screen is
required and no capability is faked - hardware/model tools report UNAVAILABLE
when absent. Run:  python examples/client_demo.py
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _cmd():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = dict(os.environ)
    env["PYTHONPATH"] = os.path.join(root, "src") + os.pathsep + env.get("PYTHONPATH", "")
    return StdioServerParameters(command=sys.executable,
                                 args=["-m", "olcap_realtime.main"], env=env)


async def main():
    async with stdio_client(_cmd()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"[client] connected; {len(tools.tools)} tools\n")

            async def call(tool, **kw):
                r = await session.call_tool(tool, kw)
                return "\n".join(c.text or "" for c in r.content if hasattr(c, "text"))

            print("== health (honest availability) ==")
            h = json.loads(await call("assistant.health"))
            print("mode:", h["mode"]["mode"], "| screen avail:",
                  h["screen"]["available"], "| lmstudio:",
                  h["reasoning"]["providers"]["lmstudio"]["available"])

            print("\n== enter INTERVIEW/PRACTICE mode ==")
            r = json.loads(await call("assistant.mode.interview"))
            print("mode:", r["mode"]["mode"], "| session:", r["session_id"])

            print("\n== practice: analyse a behavioral question ==")
            q = json.loads(await call("practice.analyze_question",
                question="Tell me about a time you handled a difficult deadline."))
            print("type:", q["question_type"])
            print("key point:", q["key_points"][0])

            print("\n== evaluate a practice answer ==")
            e = json.loads(await call("practice.evaluate_answer",
                question="Tell me about handling a deadline",
                answer="A project slipped, so I reprioritized tasks and shipped the "
                       "core feature on time, then communicated the change."))
            print("score:", e["score"], "|", e["feedback"][:80])

            print("\n== meeting actions/decisions ==")
            tr = "We decided to release Friday.\nAlice will write the tests.\n"
            tr += "Is the new API backward compatible?\nBob confirmed the deadline."
            m = json.loads(await call("meeting.extract_actions", transcript=tr))
            print("actions:", m["actions"])

            print("\n== session + transcript ==")
            sid = r["session_id"]
            await call("session.summarize", session_id=sid, summary="practice demo")
            print("export keys:", sorted((json.loads(await call("session.export",
                session_id=sid)))["session"].keys()))

            print("\n== emergency stop ==")
            print(json.loads(await call("assistant.emergency_stop")))


if __name__ == "__main__":
    asyncio.run(main())
