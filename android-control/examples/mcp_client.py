#!/usr/bin/env python3
"""Drive the unified Android Control MCP server from a client (agent host).

Spawns `android-control-mcp` (or mcp_server.py) and exchanges newline JSON-RPC
so you can see exactly what an MCP client/agent sees. Offline by default.

Run from repo root:
    PYTHONPATH=src python examples/mcp_client.py [--offline] [--no-offline]
"""
import argparse
import json
import os
import select
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(description="drive the android-control MCP server")
    p.add_argument("--offline", dest="offline", action="store_true", default=True)
    p.add_argument("--no-offline", dest="offline", action="store_false")
    p.add_argument("--goal", default="list", choices=["list", "status", "msg"])
    a = p.parse_args()

    cmd = [sys.executable, "mcp_server.py"]
    env = {**os.environ, "PYTHONPATH": "src"}
    if a.offline:
        cmd.append("--offline")
        env["AC_OFFLINE"] = "1"
    else:
        env["AC_OFFLINE"] = "0"

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                            text=True, env=env)

    def send(m):
        proc.stdin.write(json.dumps(m) + "\n"); proc.stdin.flush()

    def rpc(m):
        send(m)
        ready, _, _ = select.select([proc.stdout], [], [], 15)
        if not ready:
            raise TimeoutError("no MCP response from server")
        line = proc.stdout.readline()
        return json.loads(line) if line.strip() else None

    rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "mcp-example", "version": "1"}}})
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    if a.goal == "list":
        r = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        print("tools:", len(r["result"]["tools"]))
        for t in r["result"]["tools"]:
            print("  -", t["name"])
    elif a.goal == "status":
        r = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                 "params": {"name": "discover", "arguments": {}}})
        d = json.loads(r["result"]["content"][0]["text"])
        print("discover ->", d["status"],
              "devices:", [x["device_id"] for x in d["data"]])
    else:
        r = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                 "params": {"name": "send_message",
                            "arguments": {"message": "hello over MCP",
                                          "device": "device_001"}}})
        d = json.loads(r["result"]["content"][0]["text"])
        kind = d["devices"][0]["data"].get("kind")
        print("send_message ->", d["status"], kind)

    proc.stdin.close(); proc.wait()


if __name__ == "__main__":
    main()
