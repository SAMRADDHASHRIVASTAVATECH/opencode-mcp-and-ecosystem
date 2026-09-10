# Antigravity CLI (`agy`) — headless reference

Source: https://antigravity.google/docs/cli/headless/
Binary: `C:\Users\HP\AppData\Local\agy\bin\agy.exe` (verified `agy --version` = 1.1.27)
Auth: cached credentials (one interactive sign-in required before headless use).

## Executable resolution

`scripts\ag.py` finds `agy` via: env `AGY_PATH` → `shutil.which("agy")` → well-known paths
(`~\AppData\Local\agy\bin\agy.exe` first). Use `py` as the interpreter.

## Headless mode (single prompt, runs once, exits)

- `agy -p "prompt"` (aliases `--print`, `--prompt`) — run once and print the response.
- Response → stdout; diagnostics → stderr.
- Shared/sandboxed (non-host) invocation requires explicit permission or a sandbox flag.

## Output formats

- `--output-format text` (default) — plain response text only.
- `--output-format json` — single JSON envelope (used by the wrapper):
  ```json
  {"conversation_id":"...","status":"SUCCESS","response":"...","duration_seconds":...,
   "num_turns":...,"usage":{"input_tokens":...,"output_tokens":...,"thinking_tokens":...,
   "cache_read_tokens":...,"total_tokens":...}}
  ```
- `--output-format stream-json` — NDJSON feed: `init`, `step_update`*, final `result`.

## Timing / control

- `--print-timeout <100ms|10s|5m|...>` — abort if output not ready within the budget.

## Conversation / context

- `--continue <conversation_id>` (alias `--conversation`) — resume a prior conversation.
- `--conversation-new` — force a fresh conversation.
- `--user-id` for identity-context (names, style) if configured.

## Model / behavior

- `--model <slug>` — pin model (e.g. a Gemini pro/flash model).
- `--effort <low|medium|high>` — reasoning effort.
- `--agent <name>` — select an agent variant.

## Credentials / non-interactive behavior

- Headless runs use cached credentials; if the user has not authenticated once, a non-interactive
  run exits with `authentication required`.
- Wrapper detects that via `status != SUCCESS` + error text and reports graceful degradation
  (`status: UNAVAILABLE`) rather than fabricating a result.