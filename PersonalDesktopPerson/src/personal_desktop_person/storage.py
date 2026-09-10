from __future__ import annotations
import sqlite3,threading,json,time,shutil,zipfile,os
from pathlib import Path
SCHEMA_VERSION=3
MIGRATIONS={
1:['CREATE TABLE IF NOT EXISTS schema_info(version INTEGER NOT NULL)','INSERT INTO schema_info SELECT 0 WHERE NOT EXISTS(SELECT 1 FROM schema_info)','CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,time REAL,kind TEXT,content TEXT,importance REAL,confidence REAL,source TEXT,privacy TEXT,superseded_by INTEGER,trace_id TEXT DEFAULT "",trusted INTEGER DEFAULT 0)','CREATE VIRTUAL TABLE IF NOT EXISTS events_fts USING fts5(content,content="events",content_rowid="id")','CREATE TRIGGER IF NOT EXISTS events_ai AFTER INSERT ON events BEGIN INSERT INTO events_fts(rowid,content) VALUES(new.id,new.content);END','CREATE TABLE IF NOT EXISTS kv(key TEXT PRIMARY KEY,value TEXT,updated REAL)','ALTER TABLE events ADD COLUMN trace_id TEXT DEFAULT ""','ALTER TABLE events ADD COLUMN trusted INTEGER DEFAULT 0'],
2:['CREATE TABLE IF NOT EXISTS beliefs(namespace TEXT,key TEXT,value TEXT,confidence REAL,source TEXT,timestamp REAL,freshness REAL,sensitivity TEXT,contradictions TEXT,PRIMARY KEY(namespace,key))','CREATE TABLE IF NOT EXISTS goals(id TEXT PRIMARY KEY,data TEXT,status TEXT,updated REAL)','CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,goal_id TEXT,data TEXT,status TEXT,updated REAL)','CREATE TABLE IF NOT EXISTS skills(id TEXT PRIMARY KEY,name TEXT,version INTEGER,manifest TEXT,status TEXT,successes INTEGER DEFAULT 0,failures INTEGER DEFAULT 0,reward REAL DEFAULT 0,signature TEXT)','CREATE TABLE IF NOT EXISTS approvals(id TEXT PRIMARY KEY,data TEXT,status TEXT,updated REAL)','CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,time REAL,trace_id TEXT,stage TEXT,data TEXT,hash TEXT,prev_hash TEXT)'],
3:['CREATE TABLE IF NOT EXISTS capabilities(id TEXT PRIMARY KEY,name TEXT,scope TEXT,issued_at REAL,expires_at REAL,revoked INTEGER,task_id TEXT,signature TEXT)','CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY,time REAL,target TEXT,label TEXT,value REAL,context TEXT)','CREATE INDEX IF NOT EXISTS idx_events_kind_time ON events(kind,time)','CREATE INDEX IF NOT EXISTS idx_audit_trace ON audit(trace_id)']}
class Storage:
 def __init__(self,path):
  self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True);self.db=sqlite3.connect(self.path,check_same_thread=False);self.db.row_factory=sqlite3.Row;self.lock=threading.RLock();self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA foreign_keys=ON');self.migrate()
 def migrate(self):
  with self.lock:
   self.db.execute('CREATE TABLE IF NOT EXISTS schema_info(version INTEGER NOT NULL)');self.db.execute('INSERT INTO schema_info SELECT 0 WHERE NOT EXISTS(SELECT 1 FROM schema_info)');v=self.db.execute('SELECT version FROM schema_info').fetchone()[0]
   for n in range(v+1,SCHEMA_VERSION+1):
    for sql in MIGRATIONS[n]:
     try:self.db.execute(sql)
     except sqlite3.OperationalError as e:
      if 'duplicate column' not in str(e):raise
    self.db.execute('UPDATE schema_info SET version=?',(n,));self.db.commit()
 def execute(self,sql,args=()):
  with self.lock:r=self.db.execute(sql,args);self.db.commit();return r
 def query(self,sql,args=()):
  with self.lock:return self.db.execute(sql,args).fetchall()
 def one(self,sql,args=()):
  with self.lock:return self.db.execute(sql,args).fetchone()
 def integrity(self):return self.one('PRAGMA integrity_check')[0]
 def checkpoint(self):self.db.execute('PRAGMA wal_checkpoint(FULL)')
 def backup(self,dest,extras=()):
  self.checkpoint();dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
  tmp=dest.with_suffix('.dbcopy');out=sqlite3.connect(tmp);self.db.backup(out);out.close()
  if dest.suffix=='.zip':
   with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:z.write(tmp,'person.db');[z.write(p,Path(p).name) for p in extras if Path(p).exists()]
   tmp.unlink()
  else:tmp.replace(dest)
  return str(dest)
 def close(self):self.db.close()
