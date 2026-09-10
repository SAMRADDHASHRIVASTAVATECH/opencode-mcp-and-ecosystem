# Database / SQL MCP — Security Model

## Threats

| Threat | Control |
|--------|---------|
| SQL injection | Bound `params`; classifier; multi-statement reject |
| Destructive SQL | DDL/destructive gated; `DROP DATABASE` always refused |
| Credential leak | DSN password stripped from logs/errors/status |
| Path traversal (sqlite files, export paths) | Sandbox root |
| COPY TO PROGRAM / xp_cmdshell | Dangerous keyword denylist |
| Unbounded result | limit + max_rows + cell truncation |
| SSRF via FILE_TABLE / LOAD_FILE | Deny FILE/LOAD_FILE/INTO OUTFILE unless export tool |
| Write in “query” | `db_query` is read-class only |
| LLM confused deputy | Default read-only even if URL user can write |

## Policy levels

| Env | Allows |
|-----|--------|
| default | SELECT/WITH/EXPLAIN/SHOW/DESCRIBE/PRAGMA(read)/VALUES |
| `DB_MCP_ALLOW_WRITE=1` | INSERT/UPDATE/DELETE/CREATE TEMP |
| `DB_MCP_ALLOW_DDL=1` | CREATE/ALTER/CREATE INDEX + confirm |
| `DB_MCP_ALLOW_DESTRUCTIVE=1` | DROP/TRUNCATE/VACUUM FULL + confirm=true |

`DROP DATABASE`, `DROP SCHEMA CASCADE`, `xp_cmdshell`, `LOAD_FILE`, `INTO OUTFILE`, `COPY ... PROGRAM` are **never** executed.

## SQLite file policy

Database path must be under sandbox unless URL is explicitly absolute and `DB_MCP_ALLOW_ANY_PATH=1`.

## Network

Connecting to remote hosts is allowed (that is the point) but credentials come from env/URL, not from writing `.pgpass` for the user. No cloud metadata probing.
