#!/usr/bin/env python3
"""Minimal MCP client talking to this server over stdio.

Demonstrates the exact wire format an MCP client uses: spawn mcp_server.py,
send newline-delimited JSON-RPC, and print responses. This is also a quick way
to smoke-test the server without any MCP SDK.

Usage:
    python examples/example_client.py [--offline]
"""
import argparse
import json
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(description="drive the MCP server over stdio")
    p.add_argument("--offline", action="store_true",
                   help="run the server in deterministic offline mode")
    p.add_argument("--server", default="python mcp_server.py",
                   help="server invocation (space separated)")
    a = p.parse_args()

    cmd = a.server.split()
    if a.offline and "--offline" not in cmd:
        cmd.append("--offline")
    env = {"PYTHONPATH": "src"}
    if a.offline:
        env["UR_OFFLINE"] = "1"

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,
                            env={**__import__("os").environ, **env},
                            text=True)

    def rpc(msg):
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()
        line = proc.stdout.readline()
        return json.loads(line) if line.strip() else None

    rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                    "clientInfo": {"name": "example-client", "version": "1"}}})
    rpc({"jsonrpc": "2.0", "method": "notifications/initialized"})

    tl = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = [t["name"] for t in tl["result"]["tools"]]
    print(f"tools/list -> {len(names)} tools")

    call = rpc({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {"name": "fact_check",
                           "arguments": {
                               "statement": "PyMuPDF is a PDF library"}}})
    res = call["result"]
    print("fact_check ->", (res["content"][0]["text"].splitlines()[2]
                            if res["content"] else "?"))

    res_read = rpc({"jsonrpc": "2.0", "id": 4, "method": "resources/read",
                    "params": {"uri": "research://providers"}})
    if "result" in res_read:
        print("resources/read research://providers -> ok")

    pg = rpc({"jsonrpc": "2.0", "id": 5, "method": "prompts/get",
              "params": {"name": "fact_check",
                         "arguments": {"statement": "x is y"}}})
    if "result" in pg:
        print("prompts/get fact_check -> ok")

    proc.stdin.close()
    proc.wait()


if __name__ == "__main__":
    main()
