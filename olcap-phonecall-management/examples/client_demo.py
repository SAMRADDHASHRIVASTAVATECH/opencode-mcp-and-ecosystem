"""End-to-end MCP client demo for OLCAP Phone Call Management (offline/simulated).

Shows capability discovery, an inbound call -> auto-answer policy, an outbound
AI call lifecycle, transcripts, summary, policy CRUD, and emergency stop. No real
phone calls are made (simulated backend).
Run:  python examples/client_demo.py
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
    return StdioServerParameters(command=sys.executable,
                                 args=["-m", "olcap.main"], env=env)


async def main():
    async with stdio_client(_cmd()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"[client] connected; {len(tools.tools)} tools\n")

            async def call(tool, **kw):
                r = await session.call_tool(tool, kw)
                return "\n".join(c.text or "" for c in r.content if hasattr(c, "text"))

            print("== capabilities ==")
            cap = json.loads(await call("phone.get_capabilities"))
            print("audio/control honesty:", {k: cap[k] for k in
                  ("cellular_call_control", "call_audio_capture",
                   "call_audio_injection", "ai_cellular_conversation",
                   "provider_realtime_voice", "voice_mode", "source")})

            print("\n== create an AI-answer policy for an allowlisted caller ==")
            print(await call("phone.create_call_policy",
                             name="AI Assistant Calls",
                             policy=json.dumps({"enabled": True,
                                                "callers": ["+919900000001"],
                                                "action": "ai_answer",
                                                "hours": "00:00-23:59"})))

            print("\n== inbound call from allowlisted number (auto AI-answered) ==")
            r = json.loads(await call("phone.place_call",
                                      destination="+919900000001",
                                      authorized=True))
            cid = r["call_id"]
            print("outbound call:", cid, r["state"])
            print(await call("phone.answer_call", call_id=cid))

            print("\n== start an AI session with an objective ==")
            s = json.loads(await call("phone.start_ai_voice_session", call_id=cid,
                                      objective="Confirm Friday 4pm works."))
            sid = s["session_id"]
            print("session:", sid, s.get("state"), "simulated:", s.get("simulated"))

            print("\n== summary + transcript (simulated feed) ==")
            print(await call("phone.get_call_summary", call_id=cid))

            print("\n== hang up ==")
            print(await call("phone.hangup_call", call_id=cid))

            print("\n== history ==")
            h = json.loads(await call("phone.get_call_history"))
            print("calls recorded:", len(h["calls"]))

            print("\n== emergency stop ==")
            print(await call("phone.emergency_stop"))


if __name__ == "__main__":
    asyncio.run(main())
