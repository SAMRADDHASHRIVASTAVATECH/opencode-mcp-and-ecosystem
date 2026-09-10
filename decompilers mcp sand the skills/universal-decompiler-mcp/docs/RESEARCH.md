# Technology research and capability map (2026-09-10)

Official/reputable references used:
- GNU Binutils manuals: https://sourceware.org/binutils/docs/ — `objdump`, `readelf`, `nm`, `strings`, `c++filt`, archives, symbols, relocations, headers and disassembly.
- Ghidra headless analyzer: https://github.com/NationalSecurityAgency/ghidra — multi-format/multi-architecture SLEIGH/P-code analysis, decompiler and scriptable headless projects.
- Official Radare2 book: https://book.rada.re/ — binary plugins, `rabin2`, architecture discovery, analysis, disassembly, CFG and r2pipe automation.
- JADX: https://github.com/skylot/jadx — APK/DEX/JAR/class decompilation, resource decoding, deobfuscation heuristics, CFG and Gradle export.
- CFR: https://github.com/leibnitz27/cfr — modern JVM bytecode to Java source and whole-JAR output.
- ILSpy/ilspycmd package: https://www.nuget.org/packages/ilspycmd — C#/IL decompilation, type listing, project and PDB output.
- WABT: https://github.com/WebAssembly/wabt — WASM validation, objdump, WAT, C-like decompile and wasm2c.
- CPython `dis`/importlib documentation: https://docs.python.org/3/library/dis.html — version-specific bytecode; untrusted marshal loading is intentionally excluded from the MCP process.
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk — typed local stdio tool server.

## Existing local capability
The build host has file/libmagic CLI and GNU Binutils (`readelf`, `objdump`, `nm`, `strings`, `c++filt`, `ar`), plus Java runtime and archive listing. Those provide genuine static ELF/native triage and disassembly, but not high-level native decompilation.

## Available but unused until installed
Ghidra/radare2 add broad native architecture, function, graph and decompiler analysis. JADX/CFR/Javap cover Android/JVM at different levels. ILSpyCmd covers .NET. WABT covers WASM. LIEF/pefile add structured parser APIs. Version-matched Python decompilers may recover PYC source. Each has a catalog record and explicit install path/limitation.

## Potential agent workflows
The agent can identify unknown content, route by actual signature/runtime, compare independent metadata/disassembly/decompiler outputs, escalate depth, request a curated installation, preserve every artifact with hashes, and report disagreement and irrecoverable information. Dynamic execution, license/DRM bypass, credential extraction automation, target patching, and unsafe unpacker execution are intentionally outside scope.
