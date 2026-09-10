# Troubleshooting
- Outside-root error: move the target or output beneath configured roots.
- Missing capability: inspect routing candidates and installation plan; install from official source after approval.
- `objdump` rejects format: use a format-specific adapter or Ghidra/radare2; do not force an architecture without evidence.
- Empty symbols: likely stripped; rely on functions/CFG/decompiler heuristics and report uncertainty.
- High entropy: may indicate compression/encryption/packing, but entropy alone does not prove it.
- Decompiler disagreement: retain both outputs; compare function boundaries, calls, constants and metadata.
- PYC failure: match the CPython bytecode version; never unmarshal untrusted bytecode in the MCP process.
