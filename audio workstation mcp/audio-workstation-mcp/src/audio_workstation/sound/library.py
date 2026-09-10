from __future__ import annotations
import json,shutil,time,uuid,threading
from pathlib import Path
import numpy as np,soundfile as sf
from scipy.signal import resample_poly
class Playback:
 def __init__(self,data,volume=1,loop=False,speed=1,pitch=0):self.data=data;self.volume=volume;self.loop=loop;self.speed=speed*2**(pitch/12);self.pos=0.;self.paused=False
class SoundLibrary:
 def __init__(self,root:Path):self.root=root;self.imported=root/'sounds/imported';self.generated=root/'sounds/generated';self.index=root/'sounds/library.json';self.lock=threading.RLock();self.playing={};self.master=1.;self.duck=.35;self.items=self._load()
 def _load(self):
  self.imported.mkdir(parents=True,exist_ok=True);self.generated.mkdir(parents=True,exist_ok=True)
  try:return json.loads(self.index.read_text())
  except:return {}
 def save(self):self.index.write_text(json.dumps(self.items,indent=2))
 def add(self,path:Path,name,category='custom',normalize=True):
  data,sr=sf.read(path,dtype='float32',always_2d=True);assert len(data)>0 and len(data)/sr<=3600
  if normalize:data=data/(np.max(np.abs(data)) or 1)*.9
  ident=uuid.uuid4().hex;dest=self.imported/f'{ident}.wav';sf.write(dest,data,sr);self.items[ident]={'id':ident,'name':name,'category':category,'path':str(dest),'duration':len(data)/sr,'channels':data.shape[1],'sample_rate':sr,'favorite':False,'created_at':time.time()};self.save();return self.items[ident]
 def play(self,ident,volume=1,loop=False,speed=1,pitch=0):
  item=self.items[ident];data,sr=sf.read(item['path'],dtype='float32',always_2d=True);self.playing[ident]=Playback((data,sr),volume,loop,speed,pitch);return self.state()
 def mix(self,frames,sr,ch):
  y=np.zeros((frames,ch),np.float32);done=[]
  for ident,p in list(self.playing.items()):
   if p.paused:continue
   data,source_sr=p.data;ratio=p.speed*source_sr/sr;idx=(p.pos+np.arange(frames)*ratio).astype(int)
   if p.loop:idx%=len(data)
   valid=idx<len(data);d=data[idx[valid]]
   if d.shape[1]!=ch:d=np.repeat(d[:,:1],ch,axis=1) if ch>1 else d.mean(axis=1,keepdims=True)
   y[valid]+=d*p.volume*self.master;p.pos+=frames*ratio
   if not p.loop and p.pos>=len(data):done.append(ident)
  for i in done:self.playing.pop(i,None)
  return y
 def state(self):return {'items':len(self.items),'playing':{k:{'paused':v.paused,'loop':v.loop,'volume':v.volume,'position':v.pos} for k,v in self.playing.items()},'master_volume':self.master}
