from __future__ import annotations
from collections import deque
import json,threading
from pathlib import Path
class Memory:
 def __init__(self,limit=200,persistent=False,path='runtime/memory.jsonl'):
  self.events=deque(maxlen=limit);self.persistent=persistent;self.path=Path(path);self.lock=threading.Lock()
 def add(self,event):
  with self.lock:
   self.events.append(event)
   if self.persistent:self.path.parent.mkdir(parents=True,exist_ok=True);open(self.path,'a',encoding='utf8').write(json.dumps(event,default=str)+'\n')
 def recent(self,n=20):return list(self.events)[-n:]
 def clear(self):self.events.clear()
