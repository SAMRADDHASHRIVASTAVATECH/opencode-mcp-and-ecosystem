---
name: universal-decompiler
summary: Safely identify, route, statically analyze, decompile, cross-validate and reconstruct authorized software with dynamic tool discovery.
---
# Universal Decompiler

## Operating doctrine
Never execute an unknown target. Confirm authorization. Start static and quick, escalate based on evidence. Keep **RECOVERED** facts separate from **INFERRED**, **RECONSTRUCTED**, **GENERATED**, and **UNKNOWN** material. Decompiled output is never automatically “original source.”

## Decision sequence
1. `identify_file(target)` for signature/hash/entropy/runtime/architecture evidence. Use `inspect_file` only for a bounded header. `detect_format`, `detect_architecture`, `detect_runtime`, `detect_language`, and `detect_compiler` provide focused evidence; language/compiler confidence can remain unknown.
2. `route_analysis(target, depth)` maps evidence to required capabilities and installed/missing candidates. `list_available_tools` performs a live scan. `discover_tools` returns the curated ecosystem catalog. `find_tools_for_capability` answers a focused tool question; `verify_tool` validates one tool.
3. If an essential tool is missing, call `plan_install_tool`. Inspect source, version, mechanism, argv, network and third-party code risk. Ask explicit approval, then `approve_operation` and `execute_operation`; poll `get_job`, then `verify_tool`. Never substitute an unreviewed arbitrary URL or shell command. Manual-only plans remain manual.
4. Choose depth: **quick** = identity/basic metadata; **normal** = strings and format analysis; **deep** = full compatible static adapters/decompilation; **extreme** = maximum relevant tools/artifacts/cross-validation. Do not use extreme reflexively.
5. `universal_decompile` is the master planner. It does not execute immediately. Explain target, goal, depth, output, tools, missing capabilities, artifact exposure and CPU/storage impact. Obtain approval, call `approve_operation`, then `execute_operation`; poll `get_job`.
6. Inspect report with `list_reports` and `get_report`. Verify hashes/manifests and reconcile tool errors before conclusions.

## Specialized tools
- `extract_strings`: bounded ASCII or UTF-16LE triage. Strings are evidence, not proof of behavior.
- `inspect_container`: lists ZIP/JAR/APK entries without extraction.
- `plan_analysis`: custom static goal.
- `analyze_binary`: native metadata/sections/symbols/imports/disassembly-oriented plan.
- `decompile`: high-level recovery-oriented plan.
- `reconstruct_project`: extreme modules/classes/functions/types/dependencies/layout goal.
- `cross_validate`: extreme independent-tool comparison goal.

## Format strategy
- ELF/PE/Mach-O: binutils for independent headers/sections/symbols/disassembly; Ghidra for decompilation/types/data flow; radare2 for lightweight JSON/CFG cross-check when installed.
- .NET: confirm CLI metadata, then ILSpyCmd project/IL output; distinguish native ReadyToRun/AOT portions.
- CLASS/JAR: Javap bytecode plus CFR source; JVM language may only be probable. Preserve manifests/resources.
- APK/DEX: JADX source and resources; inspect embedded native libraries separately. Never treat Java decompilation as coverage of JNI code.
- WASM: WABT validate/objdump/WAT/decompile/wasm2c as available. Original source language often cannot be proven.
- PYC: determine exact CPython version; use a compatible external decompiler. Never deserialize untrusted marshal data in the server process.
- Firmware/raw: file signature/entropy/embedded detection first, then Ghidra/radare2 with architecture only when evidence supports it.

## Packed, stripped, obfuscated, unknown
High entropy is an indicator, not confirmation. Report stripped symbols and obfuscated names as limitations. Do not add unpacking that executes the target. For unknown formats, inspect header/strings/container evidence, search the catalog, and recommend a reputable format-specific tool; never fabricate a parser or architecture.

## Failure recovery
Timeout → reduce depth/target scope or use a specialized tool. Unsupported format → rediscover tools. Decompiler disagreement → retain all outputs and compare function boundaries, calls, constants, symbols and CFG. Missing runtime → install only after approval. Syntax-check failure → mark reconstructed, inspect raw IL/disassembly, never “repair” by inventing behavior.
