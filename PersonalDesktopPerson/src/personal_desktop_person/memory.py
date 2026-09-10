from __future__ import annotations
import json,time,re
class MemoryStore:
 TYPES={'working','episodic','semantic','procedural','preference','relationship','autobiographical','experience','reflection','dialogue','goal','lifecycle','user_feedback','action_proposal','approval','environment','user'}
 def __init__(self,storage):self.s=storage;self.db=storage.db
 def add(self,kind,content,importance=.5,confidence=1.,source='runtime',privacy='private',trace_id='',trusted=False):
  k=kind if kind in self.TYPES else 'episodic';return self.s.execute('INSERT INTO events(time,kind,content,importance,confidence,source,privacy,trace_id,trusted) VALUES(?,?,?,?,?,?,?,?,?)',(time.time(),k,content,max(0,min(1,importance)),max(0,min(1,confidence)),source,privacy,trace_id,int(trusted))).lastrowid
 def search(self,q,limit=10,kinds=None):
  clause=' AND e.kind IN (%s)'%','.join('?'*len(kinds)) if kinds else '';args=[]
  if not q.strip():sql='SELECT e.* FROM events e WHERE superseded_by IS NULL'+clause+' ORDER BY time DESC LIMIT ?';args=(list(kinds) if kinds else [])+[limit]
  else:
   safe=' '.join(re.findall(r'[\w-]+',q));sql='SELECT e.* FROM events_fts f JOIN events e ON e.id=f.rowid WHERE events_fts MATCH ? AND e.superseded_by IS NULL'+clause+' ORDER BY bm25(events_fts),e.importance DESC LIMIT ?';args=[safe]+(list(kinds) if kinds else [])+[limit]
  return [dict(r) for r in self.s.query(sql,args)]
 def correct(self,event_id,new_content):
  old=self.s.one('SELECT * FROM events WHERE id=?',(event_id,));
  if not old:raise KeyError(event_id)
  new=self.add(old['kind'],new_content,1,1,'user',old['privacy'],trusted=True);self.s.execute('UPDATE events SET superseded_by=? WHERE id=?',(new,event_id));return new
 def forget(self,event_id):self.s.execute('DELETE FROM events WHERE id=?',(event_id,))
 def set(self,key,value):self.s.execute('INSERT INTO kv VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value,updated=excluded.updated',(key,json.dumps(value),time.time()))
 def get(self,key,default=None):
  r=self.s.one('SELECT value FROM kv WHERE key=?',(key,));return json.loads(r[0]) if r else default
 def close(self):self.s.close()
