"""Voice-conversion contracts. DSP effects and genuine model inference stay distinct."""
from __future__ import annotations
from abc import ABC,abstractmethod
import numpy as np
class VoiceConversionEngine(ABC):
 id:str;genuine_ai:bool=True
 @abstractmethod
 def probe(self)->dict:...
 @abstractmethod
 def load(self,model_path:str,parameters:dict)->dict:...
 @abstractmethod
 def process_chunk(self,audio:np.ndarray,sample_rate:int)->np.ndarray:...
 @abstractmethod
 def unload(self)->dict:...
class DSPVoiceEngine(VoiceConversionEngine):
 id='dsp';genuine_ai=False
 def probe(self):return {'id':self.id,'available':True,'genuine_ai':False}
 def load(self,model_path,parameters):raise ValueError('DSP engine does not load AI models')
 def process_chunk(self,audio,sample_rate):return audio
 def unload(self):return {'loaded':False}
class RVCAdapterContract(VoiceConversionEngine):
 """Contract for a separately installed reviewed RVC runtime.

 Implementations must use a bounded worker queue, validate model hashes, refuse
 unsafe pickle loading by default, measure p95 inference latency, and return the
 latest chunk rather than accumulating stale live audio. No runtime is bundled.
 """
 id='rvc';genuine_ai=True
 def probe(self):return {'id':self.id,'available':False,'reason':'No compatible RVC runtime adapter/model assets installed'}
 def load(self,model_path,parameters):raise RuntimeError(self.probe()['reason'])
 def process_chunk(self,audio,sample_rate):raise RuntimeError(self.probe()['reason'])
 def unload(self):return {'loaded':False}
