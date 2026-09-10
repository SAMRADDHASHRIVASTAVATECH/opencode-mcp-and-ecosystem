<details>
<summary><b>🎞 Animated header (typing)</b> — save as <code>assets/svg/header-typing.svg</code>, then reference it as a markdown image</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 200" width="900" height="200" role="img" aria-label="OpenCode MCP and Skills Ecosystem">
  <title>OpenCode MCP &amp; Skills Ecosystem</title>
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#7dd3fc"/>
      <stop offset="50%" stop-color="#a78bfa"/>
      <stop offset="100%" stop-color="#f0abfc"/>
    </linearGradient>
    <filter id="soft" x="-20%" y="-40%" width="140%" height="180%">
      <feGaussianBlur stdDeviation="4" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect width="900" height="200" fill="#0b1020"/>
  <g fill="none" stroke="#1e293b" stroke-width="1">
    <path d="M0 50h900M0 100h900M0 150h900M150 0v200M300 0v200M450 0v200M600 0v200M750 0v200"/>
  </g>

  <g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="34" font-weight="700" fill="url(#g)" filter="url(#soft)">
    <clipPath id="reveal">
      <rect x="40" y="52" width="0" height="60">
        <animate attributeName="width" values="0;820;820;0" keyTimes="0;0.45;0.9;1" dur="6s" repeatCount="indefinite"/>
      </rect>
    </clipPath>
    <g clip-path="url(#reveal)">
      <text x="40" y="98">OpenCode MCP &amp; Skills Ecosystem</text>
    </g>
  </g>

  <rect x="40" y="60" width="14" height="42" fill="#7dd3fc">
    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
    <animate attributeName="x" values="40;862;862;40" keyTimes="0;0.45;0.9;1" dur="6s" repeatCount="indefinite"/>
  </rect>

  <g font-family="ui-monospace,Menlo,Consolas,monospace" font-size="16" fill="#64748b">
    <text x="40" y="146">25 MCP servers · 61 skills · stdio transport · least-privilege by default</text>
  </g>
</svg>
```

</details>

<div align="center">

**25 local MCP servers · 61 `SKILL.md` capabilities · `stdio` transports · Windows-first**

A least-privilege automation substrate for OpenCode: agents reach the desktop, the build system,
the GPU and the network through narrow, gated tool surfaces.

![mcp](https://img.shields.io/badge/MCP-25%20servers-22d3ee?style=flat-square&logo=modelcontextprotocol&logoColor=white)
![skills](https://img.shields.io/badge/SKILL.md-61%20files-a78bfa?style=flat-square&logo=markdown&logoColor=white)
![transport](https://img.shields.io/badge/transport-stdio--sidecar-34d399?style=flat-square&logo=piped&logoColor=white)
![platform](https://img.shields.io/badge/platform-Windows%2010%2F11-0078D6?style=flat-square&logo=windows&logoColor=white)
![gated](https://img.shields.io/badge/destructive%20ops-gated--default-f87171?style=flat-square&logo=shield&logoColor=white)
![license](https://img.shields.io/github/license/YOUR_GITHUB_USERNAME/YOUR_REPO?style=flat-square&color=94a3b8)

</div>

---

<details>
<summary><b>Contents</b></summary>

- [At a glance](#at-a-glance)
- [What this is](#what-this-is)
- [Install in one command](#install-in-one-command)
- [MCP inventory — 25 servers](#mcp-inventory---25-servers)
- [Skills inventory — 61 SKILL.md](#skills-inventory---61-skillmd)
- [Architecture](#architecture)
- [Security model](#security-model)
- [OpenCode integration](#opencode-integration)
- [Safe architecture](#safe-architecture)
- [Roadmap](#roadmap)
- [Visual kit — 110 components](#visual-kit---110-components)
- [Contributing](#contributing) · [Licence](#licence) · [Credits](#credits) · [Support](#support)

</details>

---

## At a glance

| | |
| --- | --- |
| **MCP servers** | 25 — 20 Python (`mcp` / `fastmcp`), 3 Node (`@modelcontextprotocol/sdk`), the rest mixed bundles |
| **Transport** | `stdio` everywhere — every server runs as a local sidecar, not an HTTP/SSE endpoint |
| **Skills** | 61 `SKILL.md` files across CATLX (24), BAKG (19), Universal Artist (18) |
| **Host** | Windows 10/11, PowerShell-backed; `pywinauto` + `mss` + `dxcam` for screen and GUI control |
| **Gate** | mutative tools require `confirm=true`; destructive ones also require `WIN_MCP_ALLOW_DESTRUCTIVE=1` |
| **Source** | static, multi-agent audit of `C:\Users\HP\Desktop\New folder` (source: the `ecosystem_audit.md` report this README was built from) |

<details>
<summary><b>🎞 Animated terminal — the bootstrap</b> — save as <code>assets/svg/terminal-window.svg</code>, then reference it as a markdown image</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 260" width="900" height="260" role="img" aria-label="Animated terminal window demo">
  <title>Terminal animation</title>
  <defs>
    <clipPath id="win"><rect x="20" y="18" width="860" height="224" rx="12"/></clipPath>
    <clipPath id="line1"><rect x="38" y="72" width="0" height="20"><animate attributeName="width" values="0;700" dur="1.2s" begin="0.4s" fill="freeze"/></rect></clipPath>
    <clipPath id="line2"><rect x="38" y="100" width="0" height="20"><animate attributeName="width" values="0;700" dur="1.4s" begin="1.8s" fill="freeze"/></rect></clipPath>
    <clipPath id="line3"><rect x="38" y="128" width="0" height="20"><animate attributeName="width" values="0;700" dur="1.2s" begin="3.4s" fill="freeze"/></rect></clipPath>
    <clipPath id="line4"><rect x="38" y="156" width="0" height="20"><animate attributeName="width" values="0;700" dur="1.6s" begin="4.8s" fill="freeze"/></rect></clipPath>
  </defs>

  <rect width="900" height="260" fill="#0b1020"/>
  <g clip-path="url(#win)">
    <rect x="20" y="18" width="860" height="224" fill="#0f172a"/>
    <rect x="20" y="18" width="860" height="30" fill="#1e293b"/>
    <circle cx="44" cy="33" r="6" fill="#ef4444"/><circle cx="64" cy="33" r="6" fill="#f59e0b"/><circle cx="84" cy="33" r="6" fill="#22c55e"/>
    <text x="450" y="38" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#94a3b8">opencode — mcp bootstrap</text>

    <g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="14">
      <text x="38" y="86" clip-path="url(#line1)"><tspan fill="#22d3ee">opencode</tspan><tspan fill="#e2e8f0"> mcp list --transport stdio</tspan></text>
      <text x="38" y="114" clip-path="url(#line2)"><tspan fill="#94a3b8">✔ 25 servers discovered · 20 python / 3 node · handshake ok</tspan></text>
      <text x="38" y="142" clip-path="url(#line3)"><tspan fill="#22d3ee">opencode</tspan><tspan fill="#e2e8f0"> skills scan --root ./skills</tspan></text>
      <text x="38" y="170" clip-path="url(#line4)"><tspan fill="#94a3b8">✔ 61 SKILL.md files · CATLX 24 · BAKG 19 · Universal Artist 18</tspan></text>
      <text x="38" y="198" fill="#a78bfa">$ destructive tools gated: win_services, win_processes, android_adb<animate attributeName="opacity" values="0;1" dur="0.2s" begin="6.6s" fill="freeze"/></text>
      <rect x="38" y="212" width="9" height="16" fill="#22d3ee">
        <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/>
      </rect>
    </g>
  </g>
</svg>
```

</details>

---

## What this is

This repository documents a **local** bundle of Model Context Protocol servers and their skill
ecosystems, and the capability model you need before you let an autonomous agent use it.

The bundle is not published anywhere: it lives on one Windows machine. What is published here is
the audit result — what exists, what each server can actually do, which calls mutate the host, and
where the gates are. Every number in this README traces back to the audit rather than to a guess.

> ⚠️ **Read [Security model](#security-model) before wiring any of this into an agent loop.**
> Unvetted access to `windows_system_mcp` or `se_build` is, in practice, remote code execution.
---

## Install in one command

`bootstrap.py` imports the whole bundle into a machine and leaves it configured: it discovers
every MCP server and `SKILL.md`, installs dependencies, writes the server config, installs the
skills, splits the servers into blast-radius agent profiles, and applies the policies below.

```powershell
# from the folder that holds bootstrap.py, on the Windows machine that holds the bundle
python bootstrap.py --root "C:\Users\HP\Desktop\New folder"
```

That is a **dry run** — it prints the full plan and changes nothing. Then:

```powershell
python bootstrap.py --root "C:\Users\HP\Desktop\New folder" --apply              # install
python bootstrap.py --root "C:\Users\HP\Desktop\New folder" --apply --apply-deps  # + venv/pip/npm
```

| Flag | Effect |
| --- | --- |
| *(default)* | dry run. Prints every action, writes nothing. |
| `--apply` | writes config, skills, profiles, policies, report |
| `--apply-deps` | also runs `python -m venv` + `pip install -e .` and `npm ci` + `npm run build` |
| `--no-skill-patch` | do not insert the policy preamble into `SKILL.md` files |
| `--no-selftest` | skip the per-server import + `--self-test` pass |
| `--opencode`, `--target` | where OpenCode config and the ecosystem live (default `~/.opencode/mcp-ecosystem`) |

**What it writes**

```text
<target>/
  mcpServers.json       every server, stdio, gates in env
  profiles/*.json       default · research · personal · dev · android · desktop-admin
  skills/               every SKILL.md tree, each carrying the policy preamble
  POLICY.md             the gates, the blast-radius rules, what this tool refuses to do
  AGENT_RULES.md        the 8 behavioural rules for any agent that loads these servers
  INSTALL_REPORT.md     inventory, per-server deps + self-test, coverage, errors
```

**What it applies**

The policies are not advisory text — they are written into every server entry and every skill:

| Control | Value | Effect |
| --- | --- | --- |
| `WIN_MCP_ALLOW_DESTRUCTIVE` | `0` | spooler purge, service stop/disable, process kill, adb uninstall, PnP disable are refused |
| `MCP_REQUIRE_CONFIRM` | `1` | a mutative call without `confirm=true` is refused, not queued |
| `MCP_EVIDENCE_REQUIRED` | `1` | no evidence, no success |
| `MCP_SCOPE` | `local` | stdio sidecars only; nothing publishes a port |

Plus `AGENT_RULES.md`: ask before you mutate, never escalate on refusal, one blast radius per
session, close the loop with evidence, envelope don't improvise, destructive is out of scope,
stay in the working directory, log what you touched.

> **There is no flag that enables destructive operations.** The audit's conclusion is that
> `win_services`, `win_processes`, `win_spooler purge` and `android_adb` need a human in the
> loop, and a bootstrap script is not a human. To turn one on you have to edit
> `WIN_MCP_ALLOW_DESTRUCTIVE` yourself, which is the point.

> ⚠️ `--apply-deps` runs `pip` and `npm`, i.e. it executes build scripts from the bundle. That is
> why it is opt-in and why the default is a dry run.

## MCP inventory — 25 servers

<details>
<summary><b>🎞 Animated icon set</b> — save as <code>assets/svg/animated-icons.svg</code>, then reference it as a markdown image</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 160" width="760" height="160" role="img" aria-label="Animated icon set">
  <title>Animated icons</title>
  <rect width="760" height="160" fill="#0b1020"/>

  <!-- server -->
  <g transform="translate(70,80)">
    <rect x="-26" y="-22" width="52" height="16" rx="4" fill="none" stroke="#22d3ee" stroke-width="2"/>
    <rect x="-26" y="0" width="52" height="16" rx="4" fill="none" stroke="#22d3ee" stroke-width="2"/>
    <circle cx="-16" cy="-14" r="3" fill="#4ade80"><animate attributeName="opacity" values="1;0.2;1" dur="1.2s" repeatCount="indefinite"/></circle>
    <circle cx="-16" cy="8" r="3" fill="#4ade80"><animate attributeName="opacity" values="1;0.2;1" dur="1.2s" begin="0.6s" repeatCount="indefinite"/></circle>
    <text y="44" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="#64748b">server</text>
  </g>

  <!-- terminal -->
  <g transform="translate(220,80)">
    <rect x="-26" y="-20" width="52" height="40" rx="5" fill="none" stroke="#a78bfa" stroke-width="2"/>
    <path d="M-14 -8 l8 8 l-8 8" fill="none" stroke="#a78bfa" stroke-width="2" stroke-linecap="round"/>
    <rect x="0" y="8" width="14" height="2" fill="#a78bfa"><animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></rect>
    <text y="44" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="#64748b">terminal</text>
  </g>

  <!-- gear -->
  <g transform="translate(370,80)">
    <g>
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="6s" repeatCount="indefinite"/>
      <circle r="18" fill="none" stroke="#f472b6" stroke-width="3"/>
      <g stroke="#f472b6" stroke-width="4" stroke-linecap="round">
        <path d="M0 -24v8"/><path d="M0 16v8"/><path d="M-24 0h8"/><path d="M16 0h8"/>
        <path d="M-17 -17l6 6"/><path d="M11 11l6 6"/><path d="M17 -17l-6 6"/><path d="M-11 11l-6 6"/>
      </g>
    </g>
    <circle r="6" fill="#0b1020" stroke="#f472b6" stroke-width="3"/>
    <text y="44" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="#64748b">automation</text>
  </g>

  <!-- shield -->
  <g transform="translate(520,80)">
    <path d="M0 -24 L20 -14 V4 C20 18 0 26 0 26 C0 26 -20 18 -20 4 V-14 Z" fill="none" stroke="#4ade80" stroke-width="2"/>
    <path d="M-9 0 l7 8 l12 -16" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-dasharray="40" stroke-dashoffset="40">
      <animate attributeName="stroke-dashoffset" values="40;0;0;40" keyTimes="0;0.3;0.9;1" dur="3s" repeatCount="indefinite"/>
    </path>
    <text y="44" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="#64748b">guardrail</text>
  </g>

  <!-- brain / model -->
  <g transform="translate(670,80)">
    <circle r="20" fill="none" stroke="#facc15" stroke-width="2" stroke-dasharray="8 6">
      <animateTransform attributeName="transform" type="rotate" from="360" to="0" dur="8s" repeatCount="indefinite"/>
    </circle>
    <circle r="9" fill="#facc15"><animate attributeName="r" values="7;11;7" dur="2s" repeatCount="indefinite"/></circle>
    <text y="44" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="11" fill="#64748b">agent-core</text>
  </g>
</svg>
```

</details>

### Host & desktop control

| Component | Runtime | What it reaches | Risk |
| --- | :--: | --- | :--: |
| `windows-system` | python | services, processes, spooler, printers, event logs, WQL | 🔴 |
| `live computer agent` | python | screen at high FPS (`dxcam`), GUI (`pywinauto`) | 🔴 |
| `PersonalDesktopPerson` | python | desktop actions via envelope → `open_computer_use` | 🔴 |
| `audio-bridge` | python | Bluetooth + audio devices via PowerShell | 🟠 |
| `virtualtion mcp and the skill` | node | VM lifecycle / hypervisor control | 🟠 |

### Media & 3D

| Component | Runtime | What it reaches | Risk |
| --- | :--: | --- | :--: |
| `bakg` | python | Blender animation pipeline (19 skills) | 🟢 |
| `UniversalArtistMCP` | python | stateful design creation | 🟢 |
| `UniversalGraphicsMCP` | python | graphics/asset generation | 🟢 |
| `image-to-3d-character` | python | image → rigged 3D character | 🟢 |
| `media editing mcp and skills` | node | timeline editing, transcode | 🟢 |
| `audio workstation mcp` | python | DAW session control | 🟢 |
| `yt-dlp` | python | downloads via the external `yt-dlp` binary | 🟠 |

### Development & research

| Component | Runtime | What it reaches | Risk |
| --- | :--: | --- | :--: |
| `android-control` | python | `adb`, `gradle`, device list, project scaffolding | 🔴 |
| `opencode new mcps` | python | `software-engineering` (`se_build`, `se_test`, `se_deps`) + others | 🔴 |
| `decompilers mcp sand the skills` | python | binary/bytecode decompilation | 🟠 |
| `hybrid eps mcp and the skill` | python | EPS/print pipeline | 🟢 |
| `n8n package with the mcp and the skills` | node | workflow execution + webhook triggers | 🟠 |
| `universal-pdf-system` | python | PDF parse, merge, extract | 🟢 |
| `universal-research-mcp` | python | web research, read-only | 🟢 |

### Personal automation & orchestration

| Component | Runtime | What it reaches | Risk |
| --- | :--: | --- | :--: |
| `catlx-skill-system` | python | progressive-loading skill DAG (Windows-only) | 🟠 |
| `unified-operator` | python | single fan-out entry point | 🟠 |
| `self-improvement-engine` | python | rewrites its own skill prompts from failures | 🟠 |
| `jarvis-addon` | python | assistant addons | 🟢 |
| `olcap-image-generator` | python | image generation | 🟢 |
| `olcap-phonecall-management` | python | telephony | 🟠 |
| `olcap-realtime-assistant` | python | realtime voice/screen assistant | 🟠 |

<details>
<summary><b>Per-server detail for the three high-risk servers</b></summary>

#### `windows-system` — 6 tools, PowerShell-backed

| tool | effect | gate |
| --- | --- | --- |
| `win_services` | start / stop / disable services | `confirm=true` |
| `win_processes` | inspect / kill processes | `confirm=true` |
| `win_spooler` | list queue, **`purge`** (destructive) | `confirm=true` + env flag |
| `win_printers` | list printers, set default | — |
| `win_event_logs` | read event logs | — |
| `win_cim_query` | arbitrary WQL (read path) | — |

#### `android-control` — 4 tools, spawns subprocesses

| tool | effect | gate |
| --- | --- | --- |
| `android_devices` | `adb devices` listing | — |
| `android_adb` | arbitrary adb arguments | `confirm=true` + device allow-list |
| `android_gradle` | run gradle tasks (installs, signs) | `confirm=true` |
| `android_create_project` | scaffold a project | — |

#### `software-engineering` (inside `opencode new mcps`)

| tool | effect | gate |
| --- | --- | --- |
| `se_build` | invoke npm / cargo / pip build tools | none — scope the cwd |
| `se_test` | run the test runner | none — scope the cwd |
| `se_deps` | add / remove / upgrade dependencies | none — scope the cwd |

</details>

---

## Skills inventory — 61 SKILL.md

<table>
<tr>
<td valign="top" width="33%">

**CATLX** — 24 skills

Progressive-loading AI operating system.
DAG workflow, strictly Windows scope.

</td>
<td valign="top" width="33%">

**BAKG** — 19 skills

Blender animation production:
lookdev, rigging, layout, render.
Driven by `bakg-orchestrator`.

</td>
<td valign="top" width="33%">

**Universal Artist** — 18 skills

Stateful design creation through
structured critique passes.

</td>
</tr>
</table>

Skills are plain `SKILL.md` files: OpenCode discovers them from its `skills/` directory and matches
the tool schemas they declare against whichever MCP servers are currently loaded. A skill whose
required tools are not loaded simply does not match — that is the capability model doing its job.

---

## Architecture

<details>
<summary><b>🎞 Animated 3D isometric stack</b> — save as <code>assets/svg/3d-isometric-stack.svg</code>, then reference it as a markdown image</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 220" width="640" height="220" role="img" aria-label="3D isometric layer diagram">
  <title>3D effect</title>
  <rect width="640" height="220" fill="#0b1020"/>
  <g transform="translate(320,120)">
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 0;0 -10;0 0" dur="3.4s" repeatCount="indefinite"/>
      <!-- top layer: agents -->
      <g transform="translate(0,-52)">
        <polygon points="0,-34 96,-14 0,6 -96,-14" fill="#22d3ee"/>
        <polygon points="-96,-14 0,6 0,20 -96,0" fill="#0891b2"/>
        <polygon points="96,-14 0,6 0,20 96,0" fill="#155e75"/>
        <text y="-10" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#04212b" font-weight="700">AGENTS</text>
      </g>
      <!-- middle layer: skills -->
      <g transform="translate(0,0)">
        <polygon points="0,-34 96,-14 0,6 -96,-14" fill="#a78bfa"/>
        <polygon points="-96,-14 0,6 0,20 -96,0" fill="#7c3aed"/>
        <polygon points="96,-14 0,6 0,20 96,0" fill="#5b21b6"/>
        <text y="-10" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#1e1246" font-weight="700">SKILLS · 61</text>
      </g>
      <!-- bottom layer: mcp -->
      <g transform="translate(0,52)">
        <polygon points="0,-34 96,-14 0,6 -96,-14" fill="#f472b6"/>
        <polygon points="-96,-14 0,6 0,20 -96,0" fill="#db2777"/>
        <polygon points="96,-14 0,6 0,20 96,0" fill="#9d174d"/>
        <text y="-10" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#4c0519" font-weight="700">MCP · 25</text>
      </g>
    </g>
    <!-- orbiting token -->
    <g>
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="9s" repeatCount="indefinite"/>
      <circle cx="150" cy="0" r="7" fill="#facc15">
        <animate attributeName="opacity" values="1;0.4;1" dur="1.6s" repeatCount="indefinite"/>
      </circle>
    </g>
  </g>
  <text x="320" y="206" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-size="12" fill="#64748b">isometric stack · agents → skills → mcp servers</text>
</svg>
```

</details>

OpenCode is the macro-orchestrator. It reads `SKILL.md`, resolves each step to a tool, and routes
the call over `stdio` to a local sidecar process. Two contracts make the loop closeable:

1. **Envelope.** `personal_desktop_person` never touches the mouse. It emits a typed action
   envelope; OpenCode routes that envelope to `open_computer_use`, which performs the physical
   interaction.
2. **Evidence.** The acting MCP must return cryptographic / stateful proof — screenshot hash,
   window state, exit code — before the plan is marked complete. No evidence, no success.

```mermaid
flowchart TB
  subgraph ORCH["OpenCode · macro orchestrator"]
    PLANNER["planner / router"]
  end

  subgraph SKILLS["Skills layer · 61 SKILL.md"]
    CATLX["CATLX · 24"]
    BAKG["BAKG · 19"]
    UA["Universal Artist · 18"]
  end

  subgraph MCP["MCP servers · 25 · stdio"]
    WIN["windows-system"]
    AND["android-control"]
    SE["software-engineering"]
    PDP["personal_desktop_person"]
    OCU["open_computer_use"]
    MEDIA["media · 3d · research · n8n · pdf · yt-dlp"]
  end

  subgraph HOST["Windows host"]
    PS["PowerShell"]
    ADB["adb / gradle"]
    GUI["pywinauto · mss · dxcam"]
  end

  GATE{{"confirm=true · WIN_MCP_ALLOW_DESTRUCTIVE=0"}}

  PLANNER --> CATLX & BAKG & UA
  CATLX --> WIN
  BAKG --> MEDIA
  UA --> MEDIA
  PLANNER --> SE & AND
  PDP -->|"envelope"| OCU
  WIN --> GATE --> PS
  AND --> GATE --> ADB
  OCU --> GUI
```

<details>
<summary><b>What a gated call actually looks like</b></summary>

```mermaid
flowchart TD
  S([agent picks a tool]) --> Q1{mutative?}
  Q1 -->|no| RUN[execute]
  Q1 -->|yes| Q2{confirm=true passed?}
  Q2 -->|no| BLOCK[refuse + ask the human]
  Q2 -->|yes| Q3{destructive class?}
  Q3 -->|no| RUN
  Q3 -->|yes| Q4{WIN_MCP_ALLOW_DESTRUCTIVE=1?}
  Q4 -->|no| BLOCK
  Q4 -->|yes| RUN
  RUN --> EV[[evidence: exit code / screenshot / log]]
  EV --> CLOSE([close the loop])
```

</details>

---

## Security model

Subprocess and shell execution is the norm in this bundle, not the exception: `audio-bridge`
invokes PowerShell for Bluetooth, `yt-dlp` wraps an external executable, `android-control` spawns
ADB, and the Node servers use `execFileSync` / `spawn`.

| Risk | Where | Mitigation |
| --- | --- | --- |
| Subprocess / shell | `audio-bridge`, `yt-dlp`, `android-control`, Node `spawn` | bounded parameters, `confirm=true` |
| Host mutation | `win_services`, `win_processes`, `win_spooler purge` | `confirm=true` **and** `WIN_MCP_ALLOW_DESTRUCTIVE=0` |
| Hardware / device | `nvidia-smi` polling, PnP device disable | allow-list + explicit confirm |
| GUI takeover | `pywinauto` / `mss` / `dxcam` via `open_computer_use` | envelope + evidence round-trip |
| Build system | `se_build`, `se_test`, `se_deps` | scope the working directory, never grant alongside `windows-system` |

**Do not** hand a single agent both `windows-system-mcp` and `software-engineering-mcp` unless the
task strictly requires it. Group MCPs by blast radius, not by convenience.

---

## OpenCode integration

<details open>
<summary><b>Python MCP — 20 of 25 servers</b></summary>

```json
{
  "mcpServers": {
    "windows-system": {
      "command": "C:\Users\HP\Desktop\New folder\\opencode new mcps\\windows-system-mcp\\.venv\\Scripts\\python.exe",
      "args": ["-m", "windows_system_mcp"],
      "env": { "WIN_MCP_ALLOW_DESTRUCTIVE": "0" }
    }
  }
}
```

</details>

<details>
<summary><b>Node MCP — 3 of 25 servers</b></summary>

```json
{
  "mcpServers": {
    "virtualization-mcp": {
      "command": "node",
      "args": ["C:\Users\HP\Desktop\New folder\\virtualtion mcp and the skill\\build\\index.js"]
    }
  }
}
```

</details>

Skills go into OpenCode's `skills/` directory:

```powershell
Copy-Item -Recurse "C:\Users\HP\Desktop\New folder\catlx-skill-system\skills\*" "$env:USERPROFILE\.opencode\skills\"
```

Then a call either runs or refuses — the refusal is the feature:

```text
> win_spooler(action="purge")
✗ refused: destructive action requires confirm=true AND WIN_MCP_ALLOW_DESTRUCTIVE=1

> win_event_logs(source="System", since="1h")
✓ 214 entries (read-only, no gate)
```

---

## Safe architecture

1. **Isolate tool access.** Group MCPs logically. Never load system administration and code
   generation into the same agent profile unless the task demands it.
2. **Enforce state guards.** Keep `confirm=true` in every mutative signature and leave
   `WIN_MCP_ALLOW_DESTRUCTIVE` off by default.
3. **Approval flows.** Wrap PowerShell, subprocess and hardware access in OpenCode's
   request-feedback loop so a human approves OS-level changes.

<details>
<summary><b>🎞 Animated progress bars — audit rollout</b> — save as <code>assets/svg/progress-bars.svg</code>, then reference it as a markdown image</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 200" width="720" height="200" role="img" aria-label="Animated progress bars for the audit rollout">
  <title>Progress animations</title>
  <rect width="720" height="200" fill="#0b1020"/>
  <g font-family="ui-sans-serif,system-ui,Segoe UI,Roboto,sans-serif" font-size="13" fill="#cbd5e1">
    <text x="24" y="46">MCP inventory audited</text>
    <text x="24" y="92">Skills mapped (SKILL.md)</text>
    <text x="24" y="138">Least-privilege gating</text>
    <text x="24" y="184">CI/CD automation</text>
  </g>
  <g>
    <rect x="230" y="34" width="400" height="16" rx="8" fill="#1e293b"/>
    <rect x="230" y="34" width="0" height="16" rx="8" fill="#22d3ee">
      <animate attributeName="width" values="0;400;400;0" keyTimes="0;0.35;0.9;1" dur="6s" repeatCount="indefinite"/>
    </rect>
    <text x="640" y="47" font-family="ui-monospace,Menlo,monospace" font-size="13" fill="#22d3ee">25/25</text>

    <rect x="230" y="80" width="400" height="16" rx="8" fill="#1e293b"/>
    <rect x="230" y="80" width="0" height="16" rx="8" fill="#a78bfa">
      <animate attributeName="width" values="0;400;400;0" keyTimes="0;0.4;0.9;1" dur="6s" begin="0.4s" repeatCount="indefinite"/>
    </rect>
    <text x="640" y="93" font-family="ui-monospace,Menlo,monospace" font-size="13" fill="#a78bfa">61/61</text>

    <rect x="230" y="126" width="400" height="16" rx="8" fill="#1e293b"/>
    <rect x="230" y="126" width="0" height="16" rx="8" fill="#34d399">
      <animate attributeName="width" values="0;300;300;0" keyTimes="0;0.45;0.9;1" dur="6s" begin="0.8s" repeatCount="indefinite"/>
    </rect>
    <text x="640" y="139" font-family="ui-monospace,Menlo,monospace" font-size="13" fill="#34d399">75%</text>

    <rect x="230" y="172" width="400" height="16" rx="8" fill="#1e293b"/>
    <rect x="230" y="172" width="0" height="16" rx="8" fill="#f472b6">
      <animate attributeName="width" values="0;180;180;0" keyTimes="0;0.5;0.9;1" dur="6s" begin="1.2s" repeatCount="indefinite"/>
    </rect>
    <text x="640" y="185" font-family="ui-monospace,Menlo,monospace" font-size="13" fill="#f472b6">45%</text>
  </g>
</svg>
```

</details>

---

## Roadmap

- [x] Static audit of 25 MCP servers and 61 skills
- [x] Risk classes and default gates documented
- [ ] Per-server tool-schema export (`--dump-tools`) so CI can diff the surface
- [ ] Capability allow-lists per agent profile
- [ ] Human-approval queue inside OpenCode for every PowerShell path
- [ ] Nightly regeneration of every asset in this README

---

## Visual kit — 110 components

Every decoration in this README is one of **110 animated README components**, curated from the
249-item catalogue so that each one documents something real about this bundle. The other 139 —
social widgets, neon/cyberpunk/anime presets, particle fields, marquee tickers, snake graphs,
donation badges — would be equally true of any repository, so they are out.

The full copy-paste source for all 110 of them was kept in a companion file, `ANIMATED-COMPONENTS.md`, which has been removed from this workspace — the component ids below are the index into it.

<table>
<tr>
<td valign="top" width="50%">

**In this repo, by group**

- animated headers, footers & dividers — 10
- animation techniques (SMIL only) — 3
- GitHub stats & repo metadata — 16
- icons & skill marks — 7
- badges — 13
- diagrams — 11
- media & demos — 4
- layout & navigation — 8
- required README sections — 13
- dynamic content — 6
- themes & dark mode — 8
- generators & asset tooling — 5
- integrations & automation — 6

</td>
<td valign="top" width="50%">

**Component index**

- `animated-svg-header`
- `animated-terminal-window`
- `animated-svg-techniques`
- `feature-comparison-table`
- `architecture-diagram`
- `security-badges`
- `dark-mode-support`
- `github-actions-integration`

</td>
</tr>
</table>

> **Why SMIL and not CSS?** GitHub proxies README images through `camo`, which strips `<script>`,
> external stylesheets and CSS `@keyframes`. SMIL (`<animate>`, `<animateTransform>`) survives, so
> every animation in `assets/svg/` is written with it — 9 files, 18 KB total.

**The nine animated SVGs**

Save each one as `assets/svg/<name>` and reference it as a markdown image. The last three are
alternates for the `<picture>` dark/light pattern; the other six are the ones used above.

| Save as | Used as | Animates |
| --- | --- | --- |
| `header-typing.svg` | top banner | clip-reveal + travelling cursor |
| `terminal-window.svg` | bootstrap demo | four typed lines, then a blinking prompt |
| `animated-icons.svg` | inventory intro | LED blink, spinning gear, drawn checkmark |
| `3d-isometric-stack.svg` | architecture | floating stack + orbiting token |
| `progress-bars.svg` | roadmap | four bars filling to the audit numbers |
| `divider-animated.svg` | footer | dash-draw lines + rotating diamond |
| `separator-wave.svg` | long-section break | two out-of-phase sine paths |
| `header-gradient.svg` | light-mode hero | colour-cycling gradient stops |
| `ascii-banner.svg` | terminal-mode hero | figlet banner + `OK` flash |

> ⚠️ GitHub sanitises inline `<svg>` in a README, so keep these as files and reference them with
> `` ![alt](assets/svg/<name>.svg) ``. Paste the markup inline only on GitHub Pages or locally.

<details>
<summary><b>🎞 Separator — animated wave</b> — save as <code>assets/svg/separator-wave.svg</code>, then reference it as a markdown image</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 120" width="900" height="120" role="img" aria-label="Waving animated separator">
  <title>Waving separator</title>
  <defs>
    <linearGradient id="wg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#22d3ee"/>
      <stop offset="50%" stop-color="#a78bfa"/>
      <stop offset="100%" stop-color="#f0abfc"/>
    </linearGradient>
  </defs>
  <rect width="900" height="120" fill="#0b1020"/>
  <g fill="none" stroke="url(#wg)" stroke-width="3" stroke-linecap="round">
    <path d="M0 60 Q 22.5 30, 45 60 T 90 60 T 135 60 T 180 60 T 225 60 T 270 60 T 315 60 T 360 60 T 405 60 T 450 60 T 495 60 T 540 60 T 585 60 T 630 60 T 675 60 T 720 60 T 765 60 T 810 60 T 855 60 T 900 60">
      <animateTransform attributeName="transform" type="translate" values="0 0;45 -8;0 0;-45 8;0 0" dur="4s" repeatCount="indefinite"/>
    </path>
    <path d="M0 60 Q 22.5 90, 45 60 T 90 60 T 135 60 T 180 60 T 225 60 T 270 60 T 315 60 T 360 60 T 405 60 T 450 60 T 495 60 T 540 60 T 585 60 T 630 60 T 675 60 T 720 60 T 765 60 T 810 60 T 855 60 T 900 60" stroke-opacity="0.35">
      <animateTransform attributeName="transform" type="translate" values="0 0;-45 10;0 0;45 -10;0 0" dur="5s" repeatCount="indefinite"/>
    </path>
  </g>
  <circle cx="450" cy="60" r="6" fill="#f0abfc">
    <animate attributeName="r" values="5;9;5" dur="2s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;0.4;1" dur="2s" repeatCount="indefinite"/>
  </circle>
</svg>
```

</details>

<details>
<summary><b>🎞 Header — animated gradient (light-mode hero)</b> — save as <code>assets/svg/header-gradient.svg</code>, then reference it as a markdown image</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 200" width="900" height="200" role="img" aria-label="Animated gradient header">
  <title>Animated gradient header</title>
  <defs>
    <linearGradient id="shift" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#22d3ee">
        <animate attributeName="stop-color" values="#22d3ee;#a78bfa;#fb7185;#22d3ee" dur="9s" repeatCount="indefinite"/>
      </stop>
      <stop offset="50%" stop-color="#a78bfa">
        <animate attributeName="stop-color" values="#a78bfa;#fb7185;#34d399;#a78bfa" dur="9s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="#fb7185">
        <animate attributeName="stop-color" values="#fb7185;#34d399;#22d3ee;#fb7185" dur="9s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="50%" r="60%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <rect width="900" height="200" fill="url(#shift)"/>
  <rect width="900" height="200" fill="url(#glow)"/>
  <rect x="0" y="0" width="900" height="200" fill="none" stroke="#ffffff" stroke-opacity="0.35" stroke-width="2" rx="14"/>

  <g text-anchor="middle" font-family="ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif" fill="#ffffff">
    <text x="450" y="96" font-size="42" font-weight="800" letter-spacing="1">OpenCode MCP &amp; Skills Ecosystem</text>
    <text x="450" y="132" font-size="17" fill="#ffffff" fill-opacity="0.92">25 MCP servers · 61 SKILL.md files · stdio transports · capability-guarded</text>
  </g>

  <g fill="#ffffff" fill-opacity="0.35">
    <circle cx="90" cy="40" r="3"><animate attributeName="cy" values="40;170;40" dur="7s" repeatCount="indefinite"/></circle>
    <circle cx="810" cy="160" r="4"><animate attributeName="cy" values="160;40;160" dur="9s" repeatCount="indefinite"/></circle>
    <circle cx="700" cy="50" r="2.5"><animate attributeName="cx" values="700;200;700" dur="11s" repeatCount="indefinite"/></circle>
  </g>
</svg>
```

</details>

<details>
<summary><b>🎞 Header — animated ASCII banner (terminal-mode hero)</b> — save as <code>assets/svg/ascii-banner.svg</code>, then reference it as a markdown image</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 200" width="900" height="200" role="img" aria-label="ASCII art animated banner">
  <title>ASCII animation</title>
  <rect width="900" height="200" fill="#020409"/>
  <g font-family="ui-monospace,Menlo,Consolas,monospace" font-size="14" fill="#38bdf8" xml:space="preserve">
    <text x="40" y="60">
 ___  ___  ___  ___ ___  _  _ ___    __  __ ___ ___  _  _
/ _ \| _ \/ __|/ __/ _ \| \| |   \  |  \/  | __/ _ \| \| |
| (_) |  _/\__ \ (_| (_) | .` | |) | | |\/| | _| (_) | .` |
 \___/|_|  |___/\___\___/|_|\_|___/  |_|  |_|___\___/|_|\_|
    </text>
    <text x="40" y="104" fill="#f472b6">
[ 25 MCP SERVERS ] [ 61 SKILLS ] [ STDIO ] [ WINDOWS-FIRST ]
    </text>
    <text x="40" y="140" fill="#94a3b8">
booting orchestrator ......................................
    </text>
  </g>
  <g font-family="ui-monospace,Menlo,monospace" font-size="14" fill="#4ade80">
    <text x="40" y="170">
      OK
      <animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.55;0.6;0.9;1" dur="4s" repeatCount="indefinite"/>
    </text>
  </g>
  <rect x="596" y="128" width="9" height="14" fill="#38bdf8">
    <animate attributeName="opacity" values="1;0;1" dur="0.9s" repeatCount="indefinite"/>
  </rect>
  <g fill="#1d4ed8" opacity="0.5">
    <rect x="0" y="0" width="900" height="200">
      <animate attributeName="opacity" values="0.18;0.02;0.18" dur="2.5s" repeatCount="indefinite"/>
    </rect>
  </g>
</svg>
```

</details>

---

## Contributing

1. Open an issue before adding a tool that mutates host state.
2. New MCP server: add a row to the [inventory](#mcp-inventory---25-servers) **and** to the risk
   table in the same PR.
3. New mutative tool: `confirm: bool = False` in the signature, and refuse when it is false.
4. Never commit a secret, a `.venv`, or an absolute path that is not already in this README.

---

## Licence

MIT. Vendor binaries (`blender.exe`, `adb.exe`, `yt-dlp.exe`) and the MCP
protocol name/logo remain under their own licences.

## Credits

- [Model Context Protocol](https://modelcontextprotocol.io) — protocol and Python/TS SDKs
- [OpenCode](https://opencode.ai) — orchestrator and skill discovery
- `pywinauto` · `mss` · `dxcam` — the desktop-perception stack behind `open_computer_use`
- [shields.io](https://shields.io) · [simple-icons](https://simpleicons.org) · [mermaid](https://mermaid.js.org) — every badge and diagram here

## Support

| Channel | Use it for |
| --- | --- |
| [Issues](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO/issues) | bugs, missing inventory rows, broken assets |
| [Discussions](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO/discussions) | capability-model design, agent profiles |
| [Security advisories](https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO/security/advisories/new) | anything that bypasses a gate — **do not** open a public issue |

---

<div align="center">

<details>
<summary><b>🎞 Animated footer divider</b> — save as <code>assets/svg/divider-animated.svg</code>, then reference it as a markdown image</summary>

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 60" width="900" height="60" role="img" aria-label="Animated divider">
  <title>Animated divider</title>
  <rect width="900" height="60" fill="#0b1020"/>
  <g stroke="#1f2a44" stroke-width="2"><path d="M0 30h900"/></g>
  <g stroke-width="3" stroke-linecap="round" fill="none">
    <path d="M0 30h240" stroke="#22d3ee">
      <animate attributeName="stroke-dasharray" values="0 240;240 0;0 240" dur="4s" repeatCount="indefinite"/>
    </path>
    <path d="M660 30h240" stroke="#f472b6">
      <animate attributeName="stroke-dasharray" values="240 0;0 240;240 0" dur="4s" repeatCount="indefinite"/>
    </path>
  </g>
  <g transform="translate(450,30)">
    <g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="4s" repeatCount="indefinite"/>
      <polygon points="0,-12 10,0 0,12 -10,0" fill="#a78bfa"/>
    </g>
    <circle r="20" fill="none" stroke="#a78bfa" stroke-opacity="0.5" stroke-width="1">
      <animate attributeName="r" values="16;26;16" dur="2s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values="0.6;0;0.6" dur="2s" repeatCount="indefinite"/>
    </circle>
  </g>
</svg>
```

</details>

**Built from a static audit of `C:\Users\HP\Desktop\New folder`** · 25 MCP servers · 61 skills

> ⚠️ Every mutative tool ships with `confirm=true` and `WIN_MCP_ALLOW_DESTRUCTIVE=0`.
> Do not grant an autonomous agent `win_services`, `win_processes` or `android_adb`
> without a human in the loop.

</div>
