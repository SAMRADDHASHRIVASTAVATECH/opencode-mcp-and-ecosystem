from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

from database_mcp.config import Settings
from database_mcp.errors import PolicyError
from database_mcp.manager import _ENGINES, connect
from database_mcp.sql_policy import classify, enforce
from database_mcp.tools import (
    _compare,
    _execute,
    _export,
    _introspect,
    _migrate,
    _query,
    _relationships,
    _sample,
    _search,
    _sql_analyze,
)


@pytest.fixture
def memdb(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    settings = Settings(
        root=tmp_path.resolve(),
        default_url=None,
        allow_write=True,
        allow_ddl=True,
        allow_destructive=False,
        allow_multi=False,
        allow_any_path=False,
        max_rows=500,
        default_limit=50,
        max_cell_chars=200,
        query_timeout=10,
    )
    monkeypatch.setattr("database_mcp.sql_policy.SETTINGS", settings)
    monkeypatch.setattr("database_mcp.config.SETTINGS", settings)
    monkeypatch.setattr("database_mcp.tools.SETTINGS", settings)
    monkeypatch.setattr("database_mcp.manager.SETTINGS", settings)
    _ENGINES.clear()
    url = "sqlite:///:memory:"
    connect(url, "default")
    info = _ENGINES["default"]
    with info.engine.begin() as conn:
        conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)"))
        conn.execute(text("CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, FOREIGN KEY(user_id) REFERENCES users(id))"))
        conn.execute(text("INSERT INTO users (id, name, email) VALUES (1, 'Ada', 'ada@example.com'), (2, 'Bob', 'bob@example.com')"))
        conn.execute(text("INSERT INTO orders (id, user_id, amount) VALUES (1, 1, 9.5), (2, 1, 3.0)"))
    return url


def test_classify_and_injection() -> None:
    assert classify("SELECT * FROM users").kind == "read"
    assert classify("INSERT INTO t VALUES (1)").kind == "write"
    assert classify("DROP TABLE users").kind == "destructive"
    with pytest.raises(PolicyError):
        enforce("SELECT 1; DROP TABLE users", for_query=True)
    with pytest.raises(PolicyError):
        enforce("DROP DATABASE foo")


def test_beginner_query(memdb: str) -> None:
    rows = _query("SELECT name FROM users ORDER BY id", "default", None, None)
    assert rows["rows"][0]["name"] == "Ada"
    schema = _introspect("default", None, "users")
    assert "users" in schema["tables"]
    assert any(c["name"] == "email" for c in schema["columns"])


def test_write_gate(memdb: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    settings = Settings(
        root=tmp_path.resolve(),
        default_url=None,
        allow_write=False,
        allow_ddl=False,
        allow_destructive=False,
        allow_multi=False,
        allow_any_path=False,
        max_rows=50,
        default_limit=20,
        max_cell_chars=100,
        query_timeout=5,
    )
    monkeypatch.setattr("database_mcp.sql_policy.SETTINGS", settings)
    with pytest.raises(PolicyError):
        enforce("INSERT INTO users (name) VALUES ('x')")


def test_professional_relationships_and_sample(memdb: str) -> None:
    rel = _relationships("default", None)
    assert any(e["from_table"] == "orders" for e in rel["foreign_keys"])
    sample = _sample("users", "default", 10, None)
    assert sample["rowcount"] == 2
    hits = _search("email", "default")
    assert any(h["column"] == "email" for h in hits["hits"])


def test_export_and_migrate(memdb: str, tmp_path: Path) -> None:
    dest = tmp_path / "users.csv"
    out = _export("users", str(dest), "default", "csv", 100)
    assert dest.exists()
    assert out["rows"] == 2
    sql = _migrate(
        [{"op": "add_column", "table": "users", "column": "phone", "type": "TEXT"}],
        apply=False,
        name="default",
        confirm=False,
    )
    assert "ADD COLUMN" in sql["sql"]
    applied = _migrate(
        [{"op": "add_column", "table": "users", "column": "phone", "type": "TEXT"}],
        apply=True,
        name="default",
        confirm=False,
    )
    assert applied["applied"] is True


def test_sql_analyze() -> None:
    info = _sql_analyze("select name from users where id = 1")
    assert info["kind"] == "read"
    assert "SELECT" in info["formatted"]


def test_compare_schema(memdb: str) -> None:
    connect("sqlite:///:memory:", "other")
    with _ENGINES["other"].engine.begin() as conn:
        conn.execute(text("CREATE TABLE users (id INTEGER, name TEXT)"))
    diff = _compare("default", "other")
    assert "orders" in diff["only_in_a"]
