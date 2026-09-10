from __future__ import annotations
from dataclasses import dataclass,asdict
import time,uuid,hmac,hashlib,json
@dataclass
class Capability:
 id:str;name:str;scope:dict;issued_at:float;expires_at:float;revoked:bool;task_id:str;signature:str
class CapabilityBroker:
 def __init__(self,secret,db):self.secret=secret.encode();self.db=db
 def _sig(self,d):return hmac.new(self.secret,json.dumps(d,sort_keys=True,separators=(',',':')).encode(),hashlib.sha256).hexdigest()
 def issue(self,name,scope,task_id,ttl=300):
  core={'id':str(uuid.uuid4()),'name':name,'scope':scope,'issued_at':time.time(),'expires_at':time.time()+min(ttl,3600),'revoked':False,'task_id':task_id};c=Capability(**core,signature=self._sig(core));self.db.execute('INSERT INTO capabilities VALUES(?,?,?,?,?,?,?,?)',(c.id,c.name,json.dumps(c.scope),c.issued_at,c.expires_at,0,c.task_id,c.signature));return asdict(c)
 def validate(self,cid,name=None):
  r=self.db.one('SELECT * FROM capabilities WHERE id=?',(cid,));
  if not r:return False
  return not r['revoked'] and r['expires_at']>time.time() and (name is None or r['name']==name)
 def revoke(self,cid):self.db.execute('UPDATE capabilities SET revoked=1 WHERE id=?',(cid,))
 def revoke_all(self):self.db.execute('UPDATE capabilities SET revoked=1 WHERE revoked=0')
 def list(self):return [dict(r) for r in self.db.query('SELECT id,name,scope,issued_at,expires_at,revoked,task_id FROM capabilities ORDER BY issued_at DESC LIMIT 100')]
