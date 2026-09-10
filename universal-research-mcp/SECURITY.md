# Security model

This server can be pointed at arbitrary URLs and executes research on behalf of
an agent, so it is built to be defensive against the classic classes of abuse:
**SSRF**, **prompt injection from fetched content**, **unsafe content types**,
and **secret leakage**. These controls are implemented (see
`src/universal_research/security.py` and `network.py`), not just documented.

## SSRF & network boundary

Every outbound request goes through `security.validate_url(url, settings)`
before `httpx` is used. It rejects:

- **Private/loopback/link-local addresses** — `127.0.0.0/8`, `10/8`,
  `172.16/12`, `192.168/16`, `169.254.169.254` (cloud metadata), `::1`,
  `fe80::/10`, `fc00::/7`, and IPv4-mapped IPv6. Rejection happens by resolving
  the host, not just string matching, and is the default (`UR_ALLOW_PRIVATE_IPS`
  defaults to `false`; setting it `true` is intended only for controlled local
  testing and is **strongly discouraged in production**).
- **Disallowed schemes** — only `http`/`https` are allowed (`file://`,
  `ftp://`, `gopher://`, `data:` etc. are rejected).
- **Credentials embedded in a URL** (`https://user:pass@host/`) — rejected, both
  to stop credential exfiltration and to avoid surprising auth.

`network.py` additionally caps redirects (`UR_MAX_REDIRECTS`, default 8) and
caps response size by streaming (`UR_MAX_DOCUMENT_SIZE`, default 4 MB) so a
host cannot push unbounded content into memory. The single shared `httpx`
client enforces these uniformly for providers, the web reader, and the
crawler.

## Content safety

- `classify_url_type` / `is_dangerous_type` reject fetching dangerous
  extensions / content types (executables, archives outside the allow-list,
  etc.).
- PDF/docx/xlsx/pptx handling goes through the documents engine and is size and
  type gated.

## Prompt injection

Fetched web content is data, never trusted instructions. Concretely:

- Injected or adversarial HTML is sanitized into readable text; scripts, SVG,
  nav, forms and iframes are stripped before text extraction.
- `sanitize_injection(text, max_len)` truncates long untrusted text passed to
  model-facing code, and `looks_like_injection` flags classic
  "ignore previous instructions / run `curl`" style strings for downstream
  policy handling.
- Verification/evidence code treats supporting snippets as evidence objects,
  not as instructions; contradictions require an actual **negative signal**
  (negation), so hostile pages that merely repeat the topic do not flip a
  verdict.

## Secrets

- API keys are read only from the environment / `.env` (never hard-coded).
- `Settings.to_dict()` never dumps key values — it reports **presence only**
  (boolean).
- `redact_secrets(text)` is available to scrub secrets from any text before it
  is logged or surfaced; network errors avoid echoing response bodies.

## Robustness of the server loop

- `mcp_interface.handle_request` is always called through `_safe_handle`, so an
  unexpected exception from any method is converted into a JSON-RPC error frame
  rather than crashing the stdio server.
- Unknown tools/methods/prompts return typed `-32xxx` JSON-RPC errors.

## Operating guidance

- Run the server with the **least privilege** user account that can still
  reach the network. Do not expose it as an interactive general-purpose HTTP
  service.
- Prefer keyed/trusted providers (self-hosted SearXNG, a Brave key, an internal
  GitHub token) over scraping HTML endpoints; the engine works either way but
  treats the HTML engines as best-effort.
- Keep `UR_ALLOW_PRIVATE_IPS=false`. If you ever need to reach internal docs
  for a controlled test, scope it tightly and never in a network-exposed
  deployment.
- Do **not** bypass anti-bot blocks the engine itself declines to circumvent.
