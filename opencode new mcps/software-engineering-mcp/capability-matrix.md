# SE MCP — Capability Matrix

| Capability | Tool | Notes |
|------------|------|-------|
| Host toolchain | `se_detect_environment` | Languages, PMs, git, docker |
| Ecosystem map | `se_ecosystem` | Existing specialist MCPs + skills |
| Route request | `se_route` | Which MCP/skill/stack |
| Discover repo | `se_discover_project` | Markers, language, build, tests |
| Create project | `se_create_project` | Multi-stack templates |
| Plan | `se_plan` | Decision sequence |
| Build | `se_build` | Detected toolchain |
| Test | `se_test` | pytest/npm/go/cargo/make test |
| Run | `se_run` | Entry command |
| Dependencies | `se_deps` | pip/npm/cargo/go/maven |
| Analyze | `se_analyze` | Structure, secrets, TODOs |
| Diagnose | `se_diagnose` | Log → cause |
| Security | `se_security_audit` | Generic + route Android |
| Quality | `se_quality` | ruff/eslint/tsc if present |
| Document | `se_document` | README from inspect |
| Package | `se_package` | wheel/npm pack/make dist |
| Git snapshot | `se_git` | status/diff (no force push) |
| ASCII trees | `se_ascii_tree` | parse / preview / scan / create (confirm) |
| SDLC catalog | `se_sdlc` | 21 phases, audiences, categories; generate / export |
| Desktop GUIs | `se_launch_gui` | ascii_tree or sdlc (needs a display) |

Android/Office/SQL/Windows **creation and domain ops** stay in those MCPs.
