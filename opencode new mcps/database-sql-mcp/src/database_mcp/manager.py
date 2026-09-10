"""Named SQLAlchemy engines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine

from database_mcp.config import SETTINGS
from database_mcp.errors import DependencyMissing, NotFoundError, ValidationError
from database_mcp.redact import redact_error, redact_url

_ENGINES: dict[str, "ConnectionInfo"] = {}


@dataclass
class ConnectionInfo:
    name: str
    url: str
    engine: Engine
    dialect: str
    extra: dict[str, Any] = field(default_factory=dict)


def _dialect_of(url: str) -> str:
    raw = url.split("://", 1)[0].split("+", 1)[0].lower()
    if raw in {"postgres", "postgresql"}:
        return "postgresql"
    if raw in {"mysql", "mariadb"}:
        return "mysql"
    if raw in {"mssql"}:
        return "mssql"
    if raw in {"sqlite"}:
        return "sqlite"
    if raw in {"duckdb"}:
        return "duckdb"
    return raw or "unknown"


def connect(url: str, name: str = "default", **kwargs: Any) -> dict[str, Any]:
    dialect = _dialect_of(url)
    connect_args: dict[str, Any] = {}
    if dialect == "sqlite":
        connect_args["check_same_thread"] = False
    try:
        engine = create_engine(url, pool_pre_ping=True, future=True, connect_args=connect_args)
        if not SETTINGS.allow_write and dialect == "sqlite":

            @event.listens_for(engine, "connect")
            def _sqlite_ro(dbapi_conn, _connection_record):  # type: ignore[no-untyped-def]
                try:
                    dbapi_conn.execute("PRAGMA query_only = ON")
                except Exception:
                    pass

        if not SETTINGS.allow_write and dialect == "postgresql":

            @event.listens_for(engine, "connect")
            def _pg_ro(dbapi_conn, _connection_record):  # type: ignore[no-untyped-def]
                try:
                    cur = dbapi_conn.cursor()
                    cur.execute("SET default_transaction_read_only = on")
                    cur.close()
                except Exception:
                    pass

        # probe
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except ModuleNotFoundError as exc:
        raise DependencyMissing(
            f"Driver missing for {dialect}: {exc}. Install extras e.g. pip install 'database-sql-mcp[postgres]'",
            {"dialect": dialect},
        ) from exc
    except Exception as exc:
        raise ValidationError(
            f"Could not connect: {redact_error(str(exc))}",
            {"url": redact_url(url), "dialect": dialect},
        ) from exc
    if name in _ENGINES:
        try:
            _ENGINES[name].engine.dispose()
        except Exception:
            pass
    info = ConnectionInfo(name=name, url=url, engine=engine, dialect=dialect)
    _ENGINES[name] = info
    return status(name)


def disconnect(name: str = "default") -> dict[str, Any]:
    info = _ENGINES.pop(name, None)
    if not info:
        raise NotFoundError(f"No connection named {name}")
    info.engine.dispose()
    return {"disconnected": name}


def get(name: str = "default") -> ConnectionInfo:
    if name not in _ENGINES:
        if name == "default" and SETTINGS.default_url:
            connect(SETTINGS.default_url, "default")
        else:
            raise NotFoundError(
                f"No connection named {name}. Call db_connect first.",
                {"available": list(_ENGINES)},
            )
    return _ENGINES[name]


def status(name: str | None = None) -> dict[str, Any]:
    if name:
        info = get(name)
        return {
            "name": info.name,
            "dialect": info.dialect,
            "url": redact_url(info.url),
            "connected": True,
        }
    return {
        "connections": [
            {"name": i.name, "dialect": i.dialect, "url": redact_url(i.url)} for i in _ENGINES.values()
        ],
        "policy": {
            "allow_write": SETTINGS.allow_write,
            "allow_ddl": SETTINGS.allow_ddl,
            "allow_destructive": SETTINGS.allow_destructive,
        },
    }


def inspector(name: str = "default"):
    return inspect(get(name).engine)


# silence unused urlparse
_ = urlparse
