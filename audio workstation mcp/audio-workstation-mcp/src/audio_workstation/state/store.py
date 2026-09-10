from __future__ import annotations
import json,os,tempfile,threading,time
from pathlib import Path
DEFAULT={"schema":1,"revision":0,"engine":{"status":"stopped","input":None,"output":None,"sample_rate":48000,"channels":1,"blocksize":0,"latency":"low","underruns":0,"overruns":0},"routing":[],"mixer":{"master":{"volume":1.0,"gain_db":0.0,"pan":0.0,"mute":False,"solo":False},"microphone":{"volume":1.0},"soundboard":{"volume":1.0},"decks":{"a":{"volume":1.0},"b":{"volume":1.0}},"crossfader":0.0},"chains":{"microphone":[],"voice":[],"soundboard":[],"master":[],"deck_a":[],"deck_b":[]},"voice":{"active":None,"engine":"dsp","model":None,"conversion":{}},"soundboard":{"playing":{},"queue":[]},"dj":{"decks":{"a":{},"b":{}},"crossfader":0.0},"presets":{}}
class StateStore:
 def __init__(self,path:Path):self.path=path;self.lock=threading.RLock();self.data=self._load()
 def _load(self):
  if self.path.exists():
   try:return json.loads(self.path.read_text())
   except Exception:pass
  return json.loads(json.dumps(DEFAULT))
 def save(self):
  with self.lock:
   self.data["revision"]+=1;self.data["updated_at"]=time.time();self.path.parent.mkdir(parents=True,exist_ok=True)
   fd,tmp=tempfile.mkstemp(dir=self.path.parent,prefix='.state-',text=True)
   try:
    with os.fdopen(fd,'w') as f:json.dump(self.data,f,indent=2);f.flush();os.fsync(f.fileno())
    os.replace(tmp,self.path)
   finally:
    if os.path.exists(tmp):os.unlink(tmp)
 def snapshot(self):
  with self.lock:return json.loads(json.dumps(self.data))
