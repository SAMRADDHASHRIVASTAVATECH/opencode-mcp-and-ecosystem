from __future__ import annotations
import json,time,hashlib,threading
class Audit:
 def __init__(self,db):self.db=db;self.lock=threading.RLock()
 def add(self,trace,stage,data):
  with self.lock:
   prev=self.db.one('SELECT hash FROM audit ORDER BY id DESC LIMIT 1');ph=prev[0] if prev else '';now=time.time();raw=json.dumps({'time':now,'trace':trace,'stage':stage,'data':data,'prev':ph},sort_keys=True,default=str);h=hashlib.sha256(raw.encode()).hexdigest();return self.db.execute('INSERT INTO audit(time,trace_id,stage,data,hash,prev_hash) VALUES(?,?,?,?,?,?)',(now,trace,stage,json.dumps(data,default=str),h,ph)).lastrowid
 def trace(self,trace):return [dict(r) for r in self.db.query('SELECT * FROM audit WHERE trace_id=? ORDER BY id',(trace,))]
 def verify(self):
  prev=''
  for r in self.db.query('SELECT * FROM audit ORDER BY id'):
   if r['prev_hash']!=prev:return False
   prev=r['hash']
  return True
