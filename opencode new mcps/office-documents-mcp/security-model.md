# Office Documents MCP — Security Model

## Threats identified in research

| Threat | How it appears | Control |
|--------|----------------|---------|
| Path traversal | `../../etc/passwd` in tool args | Resolve to realpath; must stay under `OFFICE_MCP_ROOT` (cwd default) |
| Arbitrary file write | `office_create` / save paths | Same sandbox; optional read-only mode |
| Zip bomb | Overlapping / huge uncompressed OOXML | Max uncompressed ratio and bytes before parse |
| Billion laughs / XXE | Office XML | `defusedxml`; lxml without network entities |
| Macro execution | `.docm/.xlsm` `vbaProject.bin` | Detect only; never load/run VBA |
| External relationships | `TargetMode="External"` http(s) | Do not fetch; report |
| Secret leakage | passwords in args, document properties | Never log secrets; redacted errors |
| Command injection | LibreOffice argv | `subprocess` list args; never `shell=True` |
| PDF conversion SSRF | soffice opening remote URLs | Only local sandboxed paths |
| Data destruction | overwrite without backup | Writes are explicit; `overwrite` flag default false for create |
| Huge output | 1M-row dump into MCP | Cell/row/char caps |

## Modes

| Mode | Env | Effect |
|------|-----|--------|
| Sandbox root | `OFFICE_MCP_ROOT` | All file I/O confined |
| Read-only | `OFFICE_MCP_READ_ONLY=1` | Mutating tools refused |
| Max bytes | `OFFICE_MCP_MAX_BYTES` | Default 52428800 (50 MiB) |
| Max cells | `OFFICE_MCP_MAX_CELLS` | Default 200000 |
| Conversion | `OFFICE_MCP_ALLOW_SOFFICE=1` | Default on if binary exists; can disable |

## Dangerous operations

Allowed with flags (not hidden):

- Overwrite existing files (`overwrite=true`)
- Delete a sheet/slide
- LibreOffice spawn

Never allowed:

- Execute macros
- Follow network targets in the package
- Read files outside the sandbox
- Shell interpolation of filenames

## Privilege

The server runs as the MCP host user. It never requests elevation. LibreOffice is spawned with `--headless --norestore --nofirststartwizard`.
