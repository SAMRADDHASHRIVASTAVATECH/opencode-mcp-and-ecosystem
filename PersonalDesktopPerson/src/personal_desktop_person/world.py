from __future__ import annotations
from dataclasses import dataclass,asdict
import time,json
@dataclass
class Belief:
 namespace:str;key:str;value:object;confidence:float;source:str;timestamp:float;freshness_seconds:float;sensitivity:str='private';contradictions:list[str]=None
 def __post_init__(self):self.contradictions=self.contradictions or []
 @property
 def fresh(self):return time.time()-self.timestamp<=self.freshness_seconds
class WorldModel:
 NAMESPACES={'self','user','desktop','applications','filesystem','browser','games','time','environment'}
 def __init__(self,db):self.db=db;self.beliefs={};self._load()
 def _load(self):
  for r in self.db.query('SELECT * FROM beliefs'):
   b=Belief(r['namespace'],r['key'],json.loads(r['value']),r['confidence'],r['source'],r['timestamp'],r['freshness'],r['sensitivity'],json.loads(r['contradictions']));self.beliefs[(b.namespace,b.key)]=b
 def update(self,namespace,key,value,confidence,source,freshness=60,sensitivity='private'):
  if namespace not in self.NAMESPACES:raise ValueError('Invalid world namespace')
  old=self.beliefs.get((namespace,key));contr=[]
  if old and old.value!=value and old.confidence>.7 and confidence>.7:contr=[f'{old.source}:{old.value!r}']
  b=Belief(namespace,key,value,max(0,min(1,confidence)),source,time.time(),freshness,sensitivity,contr);self.beliefs[(namespace,key)]=b
  self.db.execute('INSERT INTO beliefs VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(namespace,key) DO UPDATE SET value=excluded.value,confidence=excluded.confidence,source=excluded.source,timestamp=excluded.timestamp,freshness=excluded.freshness,sensitivity=excluded.sensitivity,contradictions=excluded.contradictions',(namespace,key,json.dumps(value),b.confidence,source,b.timestamp,freshness,sensitivity,json.dumps(contr)));return asdict(b)
 def summary(self,namespace=None):return [dict(asdict(b),fresh=b.fresh) for b in self.beliefs.values() if namespace is None or b.namespace==namespace]
