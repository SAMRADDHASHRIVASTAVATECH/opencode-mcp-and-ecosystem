"""SQL classification and safety policy."""

from __future__ import annotations

import re
from dataclasses import dataclass

import sqlparse

from database_mcp.config import SETTINGS, Settings
from database_mcp.errors import PolicyError, ValidationError

READ_HEAD = {
    "SELECT",
    "WITH",
    "EXPLAIN",
    "SHOW",
    "DESCRIBE",
    "DESC",
    "VALUES",
    "PRAGMA",
    "ANALYZE",  # PG ANALYZE vs sqlite; still gated if it writes - we treat ANALYZE as admin
}

WRITE_HEAD = {"INSERT", "UPDATE", "DELETE", "REPLACE", "MERGE"}
DDL_HEAD = {"CREATE", "ALTER", "COMMENT", "GRANT", "REVOKE", "REINDEX"}
DESTRUCTIVE_HEAD = {"DROP", "TRUNCATE"}

ALWAYS_DENY = [
    re.compile(r"\bdrop\s+database\b", re.I),
    re.compile(r"\bdrop\s+schema\b", re.I),
    re.compile(r"\bxp_cmdshell\b", re.I),
    re.compile(r"\bcopy\s+.+\s+program\b", re.I),
    re.compile(r"\binto\s+outfile\b", re.I),
    re.compile(r"\binto\s+dumpfile\b", re.I),
    re.compile(r"\bload_file\s*\(", re.I),
    re.compile(r"\bpg_read_file\s*\(", re.I),
    re.compile(r"\blo_import\s*\(", re.I),
    re.compile(r"\battach\s+database\b", re.I),
    re.compile(r"\bload_extension\s*\(", re.I),
]

PRAGMA_WRITE = re.compile(
    r"pragma\s+(journal_mode|synchronous|writable_schema|rekey|key)\b", re.I
)


@dataclass
class Classification:
    kind: str  # read, write, ddl, destructive, unknown
    statements: list[str]
    first_keyword: str | None
    raw: str


def strip_comments(sql: str) -> str:
    parts = sqlparse.format(sql, strip_comments=True)
    return parts.strip()


def classify(sql: str) -> Classification:
    if not sql or not sql.strip():
        raise ValidationError("SQL is empty")
    parsed = sqlparse.parse(sql)
    statements = [str(s).strip() for s in parsed if str(s).strip() and str(s).strip() != ";"]
    # sqlparse may keep empty
    statements = [s for s in statements if s and not set(s) <= {";", " ", "\n", "\t"}]
    first_kw = None
    if statements:
        tokens = sqlparse.parse(statements[0])[0].tokens
        for tok in tokens:
            if tok.ttype is sqlparse.tokens.Keyword or tok.ttype in (
                sqlparse.tokens.Keyword.DML,
                sqlparse.tokens.Keyword.DDL,
            ):
                first_kw = str(tok).upper()
                break
            if tok.ttype is None and str(tok).strip():
                # maybe CTE
                val = str(tok).strip().split()[0].upper()
                first_kw = val
                break
    head = (first_kw or "").upper()
    if head in DESTRUCTIVE_HEAD:
        kind = "destructive"
    elif head in DDL_HEAD:
        kind = "ddl"
    elif head in WRITE_HEAD:
        kind = "write"
    elif head == "ANALYZE":
        kind = "ddl"
    elif head in READ_HEAD or head == "TABLE":
        kind = "read"
    elif head == "PRAGMA":
        kind = "write" if PRAGMA_WRITE.search(sql) else "read"
    elif head == "VACUUM":
        kind = "destructive"
    elif head == "COPY":
        kind = "write"
    else:
        kind = "unknown"
    return Classification(kind=kind, statements=statements, first_keyword=first_kw, raw=sql)


def enforce(
    sql: str,
    *,
    for_query: bool = False,
    confirm: bool = False,
    allow_multi: bool | None = None,
    settings: Settings | None = None,
) -> Classification:
    settings = settings or SETTINGS
    lowered = sql
    for pat in ALWAYS_DENY:
        if pat.search(lowered):
            raise PolicyError("This SQL pattern is never executed by the MCP", {"pattern": pat.pattern})
    clf = classify(sql)
    multi = allow_multi if allow_multi is not None else settings.allow_multi
    if len(clf.statements) > 1 and not multi:
        raise PolicyError(
            "Multiple SQL statements are blocked (possible smuggling). Set DB_MCP_ALLOW_MULTI=1 and allow_multi=true if you really need it.",
            {"count": len(clf.statements)},
        )
    if for_query and clf.kind != "read":
        raise PolicyError(
            f"db_query only allows read SQL (got {clf.kind}/{clf.first_keyword}). Use db_execute for writes.",
            {"kind": clf.kind, "keyword": clf.first_keyword},
        )
    if clf.kind == "unknown":
        raise PolicyError("Could not classify SQL; refused. Rewrite as explicit SELECT/INSERT/...")
    if clf.kind == "write" and not settings.allow_write:
        raise PolicyError("Writes disabled. Set DB_MCP_ALLOW_WRITE=1")
    if clf.kind == "ddl" and not settings.allow_ddl:
        raise PolicyError("DDL disabled. Set DB_MCP_ALLOW_DDL=1")
    if clf.kind == "destructive":
        if not settings.allow_destructive:
            raise PolicyError("Destructive SQL disabled. Set DB_MCP_ALLOW_DESTRUCTIVE=1")
        if not confirm:
            raise PolicyError("Destructive SQL requires confirm=true")
    return clf


def format_sql(sql: str) -> str:
    return sqlparse.format(sql, reindent=True, keyword_case="upper")
