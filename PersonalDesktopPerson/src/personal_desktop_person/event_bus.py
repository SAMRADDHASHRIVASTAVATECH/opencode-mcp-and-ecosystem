from __future__ import annotations
from dataclasses import dataclass,field
from queue import PriorityQueue,Empty
from threading import RLock
import time,uuid
@dataclass(order=True)
class Event:
 sort_key:tuple=field(init=False,repr=False);priority:int=50;created_at:float=field(default_factory=time.time);kind:str='environment';payload:dict=field(default_factory=dict);source:str='runtime';trusted:bool=False;privacy:str='private';id:str=field(default_factory=lambda:str(uuid.uuid4()));trace_id:str=field(default_factory=lambda:str(uuid.uuid4()))
 def __post_init__(self):self.sort_key=(-self.priority,self.created_at)
class EventBus:
 def __init__(self,maxsize=10000):self.q=PriorityQueue(maxsize);self.subs={};self.lock=RLock();self.dropped=0
 def publish(self,e:Event):
  if self.q.full() and e.priority<80:self.dropped+=1;return False
  self.q.put(e);return True
 def subscribe(self,kind,fn):
  with self.lock:self.subs.setdefault(kind,[]).append(fn)
 def dispatch_one(self,timeout=.05):
  try:e=self.q.get(timeout=timeout)
  except Empty:return None
  for fn in self.subs.get(e.kind,[])+self.subs.get('*',[]):
   try:fn(e)
   except Exception:continue
  return e
 def depth(self):return self.q.qsize()
