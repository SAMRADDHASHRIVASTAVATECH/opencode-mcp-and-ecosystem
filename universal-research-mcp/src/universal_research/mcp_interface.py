"""MCP interface layer (#57-59).

Implements the Model Context Protocol over stdio using newline-delimited
JSON-RPC messages (the standard reference transport). It exposes:
  * tools  (from the ToolRegistry, one per tool spec)
  * resources (research://…)
  * prompts (deep_research, fact_check, error_investigation, …)

The server is deliberately thin and SDK-independent so it stays importable in
any MCP-compatible client without depending on a particular MCP SDK version.
"""
from __future__ import annotations

import json
import sys
from typing import Optional

from . import functions as F
from .registry.tools import build_tool_registry
from .registry.skills import build_skill_registry
from .errors import ResearchError

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "universal-research"
SERVER_VERSION = "1.0.0"


# ---------------------------------------------------------------------------
# Tool execution mapping (from function registry)
# ---------------------------------------------------------------------------
def _make_tools() -> dict:
    reg = build_tool_registry()
    return {t.name: t for t in reg.all()}


def _invoke_tool(name: str, arguments: dict):
    tools = _make_tools()
    if name not in tools:
        raise ResearchError(f"unknown tool: {name}")
    tool = tools[name]
    # coerce simple JSON Schema types from the string-ish client args
    kwargs = _coerce(tool.input_schema, arguments or {})
    return tool.invoke(**kwargs)


def _coerce(schema, args: dict) -> dict:
    """Best-effort type coercion of arguments according to the JSON Schema."""
    props = schema.get("properties", {})
    out = {}
    for k, v in args.items():
        p = props.get(k, {})
        typ = p.get("type", "string")
        if v is None:
            out[k] = None
        elif typ == "string":
            out[k] = str(v)
        elif typ == "integer":
            try:
                out[k] = int(v)
            except (TypeError, ValueError):
                out[k] = v
        elif typ == "number":
            try:
                out[k] = float(v)
            except (TypeError, ValueError):
                out[k] = v
        elif typ == "boolean":
            if isinstance(v, bool):
                out[k] = v
            else:
                out[k] = str(v).lower() in {"1", "true", "yes"}
        elif typ == "array":
            out[k] = v if isinstance(v, list) else ([] if v in ("", None) else [v])
        else:
            out[k] = v
    return out


# ---------------------------------------------------------------------------
# Resources & prompts
# ---------------------------------------------------------------------------
_RESOURCE_CATALOG = [
    ("research://skills", "List of all built-in research skills"),
    ("research://tools", "List of all MCP tools"),
    ("research://operators", "Search operator reference"),
    ("research://providers", "Provider configuration status"),
    ("research://strategies", "Query strategy families"),
]
_RESOURCE_PREFIX = {
    "research://research/": ("research task status/result", F.research_status, "task_id"),
    "research://graph/": ("research knowledge graph", F.research_graph, "task_id"),
}

_PROMPTS = {
    "deep_research": {
        "description": "Run autonomous multi-source deep research on a topic.",
        "arguments": [{"name": "objective", "required": True,
                       "description": "research objective"}],
        "template": ("Research the following deeply across web, code, academic, "
                     "documents and community sources, then produce a cited, "
                     "balanced summary with contradictions.\nOBJECTIVE: "
                     "{objective}"),
        "tool": "deep_research",
    },
    "technical_research": {
        "description": "Technical/architecture research on a stack or approach.",
        "arguments": [{"name": "topic", "required": True,
                       "description": "technical topic"}],
        "template": "Research the technical architecture/options for: {topic}",
        "tool": "deep_research",
    },
    "web_investigation": {
        "description": "Investigate a claim or question on the web.",
        "arguments": [{"name": "question", "required": True}],
        "template": "Investigate: {question}. Find sources, verify, contradict.",
        "tool": "deep_research",
    },
    "github_research": {
        "description": "Research a code library/repo ecosystem.",
        "arguments": [{"name": "library", "required": True}],
        "template": "Research the GitHub project / library: {library}.",
        "tool": "deep_research",
    },
    "academic_research": {
        "description": "Academic/literature research on a topic.",
        "arguments": [{"name": "topic", "required": True}],
        "template": "Do academic literature research on: {topic}.",
        "tool": "deep_research",
    },
    "document_research": {
        "description": "Find & analyze documents about a topic.",
        "arguments": [{"name": "topic", "required": True}],
        "template": "Find documents and PDFs about: {topic}.",
        "tool": "deep_research",
    },
    "fact_check": {
        "description": "Fact-check a statement.",
        "arguments": [{"name": "statement", "required": True}],
        "template": "Fact-check: {statement}",
        "tool": "fact_check",
    },
    "error_investigation": {
        "description": "Investigate an error message.",
        "arguments": [{"name": "error", "required": True}],
        "template": "Investigate the error: {error}",
        "tool": "investigate_error",
    },
    "competitive_research": {
        "description": "Competitive comparison of entities.",
        "arguments": [{"name": "entities", "required": True}],
        "template": "Competitively compare: {entities}",
        "tool": "compare_entities",
    },
    "literature_review": {
        "description": "Structured literature review.",
        "arguments": [{"name": "topic", "required": True}],
        "template": "Produce a literature review on: {topic}",
        "tool": "literature_review",
    },
    "source_verification": {
        "description": "Verify the reliability of sources.",
        "arguments": [{"name": "topic", "required": True}],
        "template": "Verify sources about: {topic}",
        "tool": "verify_claim",
    },
}


def _resource_content(uri: str) -> dict:
    if uri == "research://skills":
        text = json.dumps(F.list_skills(), indent=2)
    elif uri == "research://tools":
        text = json.dumps([{"name": t["name"], "description": t["description"],
                            "inputSchema": t["input_schema"]}
                           for t in F.list_tools()["tools"]], indent=2)
    elif uri == "research://operators":
        text = json.dumps(F.list_operators(), indent=2)
    elif uri == "research://providers":
        text = json.dumps(F.list_providers(), indent=2)
    elif uri == "research://strategies":
        text = json.dumps({"families": ["discovery", "exact", "technical",
                                        "implementation", "source_specific",
                                        "verification", "contradiction",
                                        "historical", "current", "alternative"]},
                          indent=2)
    elif uri.startswith("research://research/"):
        tid = uri.rsplit("/", 1)[-1]
        text = json.dumps(F.research_status(tid), indent=2)
    elif uri.startswith("research://graph/"):
        tid = uri.rsplit("/", 1)[-1]
        text = json.dumps(F.research_graph(tid), indent=2)
    else:
        raise ResearchError(f"unknown resource: {uri}")
    return {"uri": uri, "mimeType": "application/json", "text": text}


# ---------------------------------------------------------------------------
# JSON-RPC message loop
# ---------------------------------------------------------------------------
def _resp(id, result):
    return {"jsonrpc": "2.0", "id": id, "result": result}


def _err(id, code, message):
    return {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}


def handle_request(msg: dict) -> Optional[dict]:
    method = msg.get("method")
    mid = msg.get("id")
    params = msg.get("params") or {}
    if method == "initialize":
        return _resp(mid, {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": True},
                             "resources": {"listChanged": True},
                             "prompts": {"listChanged": True}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}})
    if method == "notifications/initialized":
        return None
    if method in ("ping",):
        return _resp(mid, {})
    if method == "tools/list":
        tools = []
        for t in F.list_tools()["tools"]:
            tools.append({"name": t["name"], "description": t["description"],
                          "inputSchema": t["input_schema"]})
        return _resp(mid, {"tools": tools})
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            result = _invoke_tool(name, args)
            if not isinstance(result, dict):
                result = {"result": result}
            return _resp(mid, {"content": [
                {"type": "text", "text": json.dumps(result, indent=2)}],
                "isError": False})
        except ResearchError as e:
            return _err(mid, -32000, str(e))
        except Exception as e:  # noqa: BLE001
            return _err(mid, -32603, f"{type(e).__name__}: {e}")
    if method == "resources/list":
        uris = [{"uri": u, "name": d, "description": d}
                for u, d in _RESOURCE_CATALOG]
        uris.append({"uri": "research://research/{id}",
                     "name": "research task status"})
        uris.append({"uri": "research://graph/{id}", "name": "research graph"})
        return _resp(mid, {"resources": uris})
    if method == "resources/read":
        uri = params.get("uri")
        try:
            return _resp(mid, {"contents": [_resource_content(uri)]})
        except ResearchError as e:
            return _err(mid, -32002, str(e))
    if method == "prompts/list":
        prompts = []
        for name, p in _PROMPTS.items():
            prompts.append({"name": name, "description": p["description"],
                            "arguments": p["arguments"]})
        return _resp(mid, {"prompts": prompts})
    if method == "prompts/get":
        name = params.get("name")
        if name not in _PROMPTS:
            return _err(mid, -32002, f"unknown prompt: {name}")
        p = _PROMPTS[name]
        args = params.get("arguments") or {}
        declared = p.get("arguments", [])
        required_missing = [d["name"] for d in declared
                            if d.get("required") and d["name"] not in args]
        if required_missing:
            return _err(mid, -32002,
                        f"prompt '{name}' missing required argument(s): "
                        + ", ".join(required_missing))
        try:
            rendered = p["template"].format(**args)
        except (KeyError, ValueError) as e:
            return _err(mid, -32602, f"prompt '{name}' argument error: {e}")
        tool_use = p.get("tool")
        content = [{"type": "text", "text": rendered}]
        # note the recommended tool without forcing a tool call
        content.append({"type": "text",
                        "text": f"\n(recommended tool: {tool_use})"})
        return _resp(mid, {"description": p["description"],
                           "messages": [{"role": "user", "content": content}]})
    # notifications
    if mid is None:
        return None
    return _err(mid, -32601, f"method not found: {method}")


def _safe_handle(msg: dict) -> Optional[dict]:
    """handle_request that never lets an exception kill the stdio loop."""
    try:
        return handle_request(msg)
    except ResearchError as e:
        return _err(msg.get("id"), -32000, str(e))
    except Exception as e:  # noqa: BLE001
        return _err(msg.get("id"), -32603,
                    f"{type(e).__name__}: {e}")


# ---------------------------------------------------------------------------
# stdio framing: newline-delimited JSON (reference MCP stdio transport)
# ---------------------------------------------------------------------------
def _read_messages(stream):
    """Yield parsed messages from a text stream (one JSON object per line)."""
    for line in stream:
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def run_stdio():
    """Entry point for the MCP server over stdin/stdout (newline JSON)."""
    out = sys.stdout
    for msg in _read_messages(sys.stdin):
        if msg.get("method") == "notifications/initialized":
            # some clients wait; flush nothing
            continue
        result = _safe_handle(msg)
        if result is not None:
            out.write(json.dumps(result) + "\n")
            out.flush()


def serve_stdio_from_binary():
    """Same as run_stdio but decodes bytes to text robustly (UTF-8)."""
    for raw in sys.stdin.buffer:
        line = raw.decode("utf-8", "replace").strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("method") == "notifications/initialized":
            continue
        result = _safe_handle(msg)
        if result is not None:
            sys.stdout.write(json.dumps(result) + "\n")
            sys.stdout.flush()
