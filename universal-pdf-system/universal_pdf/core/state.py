"""Persistent document knowledge store (requirement 28).

Externalised state so the model never has to remember a document. Each PDF
gets a ``document_id`` and structured records (pages, chunks, tables, images,
metadata, OCR/index/processing state, provenance, validation, errors) stored
durably in a SQLite database under ``knowledge/``.

This supports: (a) incremental processing that later operations can reuse,
(b) provenance anchored to document ids, and (c) resumable large-document
pipelines.
"""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Iterable, Optional

from .. import config
from .provenance import file_fingerprint

DB = config.ROOT / "knowledge" / "store.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents(
  id TEXT PRIMARY KEY,
  path TEXT, fingerprint TEXT, page_count INTEGER,
  title TEXT, author TEXT, subject TEXT, created INTEGER);
CREATE TABLE IF NOT EXISTS pages(
  doc_id TEXT, page INTEGER, text TEXT, char_count INTEGER,
  width REAL, height REAL, has_text INTEGER,
  PRIMARY KEY(doc_id,page));
CREATE TABLE IF NOT EXISTS chunks(
  doc_id TEXT, chunk_id TEXT, page INTEGER, start INTEGER, text TEXT,
  embedding BLOB, PRIMARY KEY(doc_id,chunk_id));
CREATE TABLE IF NOT EXISTS tables(
  doc_id TEXT, table_id TEXT, page INTEGER, source TEXT, json TEXT,
  PRIMARY KEY(doc_id,table_id));
CREATE TABLE IF NOT EXISTS images(
  doc_id TEXT, image_id TEXT, page INTEGER, xref INTEGER, width INTEGER,
  height INTEGER, PRIMARY KEY(doc_id,image_id));
CREATE TABLE IF NOT EXISTS sections(
  doc_id TEXT, title TEXT, level INTEGER, page INTEGER,
  PRIMARY KEY(doc_id,title));
CREATE TABLE IF NOT EXISTS meta(
  doc_id TEXT, key TEXT, value TEXT, PRIMARY KEY(doc_id,key));
CREATE TABLE IF NOT EXISTS processing(
  doc_id TEXT, step TEXT, status TEXT, updated REAL,
  detail TEXT, PRIMARY KEY(doc_id,step));
CREATE TABLE IF NOT EXISTS validation(
  doc_id TEXT, step TEXT, name TEXT, passed INTEGER, detail TEXT,
  PRIMARY KEY(doc_id,step,name));
CREATE TABLE IF NOT EXISTS summaries(
  doc_id TEXT, scope TEXT, page INTEGER, text TEXT, PRIMARY KEY(doc_id,scope,page));
CREATE TABLE IF NOT EXISTS errors(
  doc_id TEXT, step TEXT, message TEXT, updated REAL);
"""


class DocumentStore:
    """SQLite-backed knowledge base for all processed documents."""

    def __init__(self, db: str | Path = DB):
        self.db = Path(db)
        self.db.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    def close(self):
        self.conn.close()

    # --- documents ---------------------------------------------------------
    def register_document(self, path: str, page_count: int = 0,
                          **info) -> str:
        """Register (or fetch) a document; returns a stable document_id."""
        fp = file_fingerprint(path)
        row = self.conn.execute(
            "SELECT id FROM documents WHERE fingerprint=?",
            (fp,)).fetchone()
        if row:
            return row["id"]
        did = info.get("id") or str(uuid.uuid4())[:12]
        self.conn.execute(
            "INSERT OR REPLACE INTO documents(id,path,fingerprint,page_count,"
            "title,author,subject,created) VALUES(?,?,?,?,?,?,?,?)",
            (did, path, fp, page_count, info.get("title"),
             info.get("author"), info.get("subject"), time.time()))
        self.conn.commit()
        return did

    def get_document(self, doc_id: str) -> Optional[dict]:
        r = self.conn.execute("SELECT * FROM documents WHERE id=?",
                              (doc_id,)).fetchone()
        return dict(r) if r else None

    def find_by_path(self, path: str) -> Optional[str]:
        r = self.conn.execute("SELECT id FROM documents WHERE path=?",
                              (str(path),)).fetchone()
        return r["id"] if r else None

    # --- records -----------------------------------------------------------
    def put_page(self, doc_id: str, page: int, text: str,
                 width: float = 0, height: float = 0):
        self.conn.execute(
            "INSERT OR REPLACE INTO pages VALUES(?,?,?,?,?,?,?)",
            (doc_id, page, text, len(text or ""), width, height,
             1 if (text and text.strip()) else 0))
        self.conn.commit()

    def page(self, doc_id: str, page: int) -> Optional[dict]:
        r = self.conn.execute("SELECT * FROM pages WHERE doc_id=? AND page=?",
                              (doc_id, page)).fetchone()
        return dict(r) if r else None

    def page_count_in_store(self, doc_id: str) -> int:
        r = self.conn.execute("SELECT COUNT(*) c FROM pages WHERE doc_id=?",
                              (doc_id,)).fetchone()
        return int(r["c"]) if r else 0

    def put_chunk(self, doc_id: str, chunk_id: str, page: int,
                  start: int, text: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO chunks VALUES(?,?,?,?,?,NULL)",
            (doc_id, chunk_id, page, start, text))
        self.conn.commit()

    def put_table(self, doc_id: str, table_id: str, page: int,
                  source: str, data: Any):
        self.conn.execute(
            "INSERT OR REPLACE INTO tables VALUES(?,?,?,?,?)",
            (doc_id, table_id, page, source, json.dumps(data, default=str)))
        self.conn.commit()

    def put_image(self, doc_id: str, image_id: str, page: int,
                  xref: int, w: int, h: int):
        self.conn.execute(
            "INSERT OR REPLACE INTO images VALUES(?,?,?,?,?,?)",
            (doc_id, image_id, page, xref, w, h))
        self.conn.commit()

    def put_section(self, doc_id: str, title: str, level: int, page: int):
        self.conn.execute(
            "INSERT OR REPLACE INTO sections VALUES(?,?,?,?)",
            (doc_id, title, level, page))
        self.conn.commit()

    def set_meta(self, doc_id: str, key: str, value: Any):
        self.conn.execute(
            "INSERT OR REPLACE INTO meta VALUES(?,?,?)",
            (doc_id, key, json.dumps(value, default=str)))
        self.conn.commit()

    def get_meta(self, doc_id: str, key: str):
        r = self.conn.execute("SELECT value FROM meta WHERE doc_id=? AND key=?",
                              (doc_id, key)).fetchone()
        return json.loads(r["value"]) if r else None

    # --- pipeline state ------------------------------------------------------
    def mark(self, doc_id: str, step: str, status: str, detail: str = ""):
        self.conn.execute(
            "INSERT OR REPLACE INTO processing VALUES(?,?,?,?,?)",
            (doc_id, step, status, time.time(), detail))
        self.conn.commit()

    def status(self, doc_id: str, step: str) -> Optional[str]:
        r = self.conn.execute(
            "SELECT status FROM processing WHERE doc_id=? AND step=?",
            (doc_id, step)).fetchone()
        return r["status"] if r else None

    def log_error(self, doc_id: str, step: str, message: str):
        self.conn.execute("INSERT INTO errors VALUES(?,?,?,?)",
                          (doc_id, step, message, time.time()))
        self.conn.commit()

    def put_summary(self, doc_id: str, scope: str, page: int, text: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO summaries VALUES(?,?,?,?)",
            (doc_id, scope, page, text))
        self.conn.commit()

    def summary(self, doc_id: str, scope: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT page,text FROM summaries WHERE doc_id=? AND scope=? "
            "ORDER BY page", (doc_id, scope)).fetchall()
        return [dict(r) for r in rows]

    def all_chunks(self, doc_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT chunk_id,page,text FROM chunks WHERE doc_id=? ORDER BY page,start",
            (doc_id,)).fetchall()
        return [dict(r) for r in rows]

    def errors_for(self, doc_id: str) -> list[str]:
        rows = self.conn.execute(
            "SELECT message FROM errors WHERE doc_id=? ORDER BY updated",
            (doc_id,)).fetchall()
        return [r["message"] for r in rows]


def get_store() -> DocumentStore:
    return DocumentStore()
