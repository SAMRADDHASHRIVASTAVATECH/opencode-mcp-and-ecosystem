from __future__ import annotations
import threading,time,numpy as np,psutil
from .backend import PortAudioBackend
from ..dsp.effects import Chain
class RealtimeEngine:
 def __init__(self,store):self.store=store;self.lock=threading.RLock();self.backend=PortAudioBackend(self._callback);self.chain=Chain();self.level={"peak":0.,"rms":0.,"clipping":False};self.last_callback=0.;self.error=None
 def rebuild(self):
  with self.lock:self.chain=Chain(self.store.data['chains']['microphone']+self.store.data['chains']['voice']+self.store.data['chains']['master'])
 def _callback(self,indata,outdata,frames,time_info,status):
  try:
   if status.input_overflow:self.store.data['engine']['overruns']+=1
   if status.output_underflow:self.store.data['engine']['underruns']+=1
   chain=self.chain;y=chain.process(indata,self.store.data['engine']['sample_rate']);vol=self.store.data['mixer']['master']['volume'];y=np.clip(y*vol,-1,1);outdata[:]=y
   self.level={"peak":float(np.max(np.abs(y))),"rms":float(np.sqrt(np.mean(y*y))),"clipping":bool(np.max(np.abs(y))>=.999)};self.last_callback=time.monotonic()
  except Exception as e:outdata.fill(0);self.error=str(e)
 def start(self,input,output,sample_rate,channels,blocksize,latency):
  self.rebuild();self.backend.start(input=input,output=output,sample_rate=sample_rate,channels=channels,blocksize=blocksize,latency=latency);self.store.data['engine'].update(status='running',input=input,output=output,sample_rate=sample_rate,channels=channels,blocksize=blocksize,latency=latency);self.store.save();return self.verify()
 def stop(self):self.backend.stop();self.store.data['engine']['status']='stopped';self.store.save();return self.verify()
 def pause(self):
  if not self.backend.stream:raise RuntimeError('stream not running')
  self.backend.stream.stop();self.store.data['engine']['status']='paused';self.store.save();return self.verify()
 def resume(self):
  if not self.backend.stream:raise RuntimeError('stream not open')
  self.backend.stream.start();self.store.data['engine']['status']='running';self.store.save();return self.verify()
 def verify(self):
  b=self.backend.status();e=self.store.data['engine'];return {"configured":e,"backend":b,"verified_running":bool(e['status']=='running' and b['active']),"levels":self.level,"callback_age_ms":(time.monotonic()-self.last_callback)*1000 if self.last_callback else None,"process_cpu":psutil.Process().cpu_percent(),"memory_mb":psutil.Process().memory_info().rss/1048576,"error":self.error}
