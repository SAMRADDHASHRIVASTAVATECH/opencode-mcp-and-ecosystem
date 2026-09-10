# Specialist MCP + skills ecosystem

Independent servers plus a **universal software-engineering layer**. No master process — the SE MCP **routes**.

| Piece | Role | Path |
|-------|------|------|
| **Software engineering MCP** | Capability layer: discover, route, scaffold, ASCII trees, SDLC, build, test, audit | `software-engineering-mcp/` |
| **Skill set** | How to decide (SKILL.md) | `skills/` |
| Office documents | DOCX/XLSX/PPTX | `office-documents-mcp/` |
| Database / SQL | SQLite/PG/MySQL/MSSQL/DuckDB | `database-sql-mcp/` |
| Windows system | Printers, services, CIM | `windows-system-mcp/` |
| Android development | App lifecycle | `android-development-mcp/` |

Client config: `mcp.json`. Agent playbook: `AGENTS.md`.

```bash
pip install -e ./software-engineering-mcp
python -m se_mcp
```
