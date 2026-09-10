from __future__ import annotations
from abc import ABC,abstractmethod
class AudioBackend(ABC):
 @abstractmethod
 def devices(self):...
 @abstractmethod
 def start(self,**kwargs):...
 @abstractmethod
 def stop(self):...
class PortAudioBackend(AudioBackend):
 def __init__(self,callback):
  self.callback=callback;self.stream=None;self.sd=None;self.error=None
  try:
   import sounddevice as sd
   self.sd=sd
  except Exception as e:self.error=str(e)
 def _require(self):
  if self.sd is None:raise RuntimeError(f'PortAudio unavailable: {self.error}')
 def devices(self):
  self._require();apis=self.sd.query_hostapis();out=[]
  for i,d in enumerate(self.sd.query_devices()):
   name=str(d['name']);out.append({"id":i,"name":name,"hostapi":apis[d['hostapi']]['name'],"input_channels":d['max_input_channels'],"output_channels":d['max_output_channels'],"default_sample_rate":d['default_samplerate'],"low_input_latency":d['default_low_input_latency'],"low_output_latency":d['default_low_output_latency'],"virtual":any(k in name.lower() for k in ('virtual','cable','voicemeeter','blackhole','loopback'))})
  return out
 def start(self,input,output,sample_rate=48000,channels=1,blocksize=0,latency='low'):
  self._require();self.sd.check_input_settings(device=input,channels=channels,samplerate=sample_rate,dtype='float32');self.sd.check_output_settings(device=output,channels=channels,samplerate=sample_rate,dtype='float32')
  self.stream=self.sd.Stream(device=(input,output),samplerate=sample_rate,channels=channels,blocksize=blocksize,dtype='float32',latency=latency,callback=self.callback);self.stream.start()
 def stop(self):
  if self.stream:self.stream.stop();self.stream.close();self.stream=None
 def status(self):return {"available":self.sd is not None,"error":self.error,"active":bool(self.stream and self.stream.active),"latency":getattr(self.stream,'latency',None),"cpu_load":getattr(self.stream,'cpu_load',0)}
