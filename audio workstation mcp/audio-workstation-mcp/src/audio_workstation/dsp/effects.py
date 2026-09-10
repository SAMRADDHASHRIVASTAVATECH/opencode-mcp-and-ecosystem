from __future__ import annotations
import numpy as np
from scipy.signal import butter,sosfilt
class Effect:
 kind='effect'
 def process(self,x:np.ndarray,sr:int)->np.ndarray:return x
class Gain(Effect):
 kind='gain'
 def __init__(self,db=0):self.db=float(db)
 def process(self,x,sr):return x*np.float32(10**(self.db/20))
class Biquad(Effect):
 kind='filter'
 def __init__(self,mode='lowpass',frequency=8000,q=.707,order=2):self.mode=mode;self.frequency=frequency;self.q=float(q);self.order=int(order);self._key=None;self._zi=None
 def process(self,x,sr):
  f=[min(float(v),sr*.49) for v in self.frequency] if isinstance(self.frequency,(list,tuple)) else min(float(self.frequency),sr*.49);mode={'highpass':'highpass','lowpass':'lowpass','bandpass':'bandpass'}.get(self.mode,self.mode);key=(sr,str(f),mode,self.order,x.shape[1])
  if key!=self._key:self._sos=butter(self.order,f,btype=mode,fs=sr,output='sos');self._zi=np.zeros((len(self._sos),2,x.shape[1]),np.float32);self._key=key
  y,self._zi=sosfilt(self._sos,x,axis=0,zi=self._zi);return y.astype(np.float32)
class Compressor(Effect):
 kind='compressor'
 def __init__(self,threshold_db=-18,ratio=4,makeup_db=0):self.threshold=float(threshold_db);self.ratio=max(1,float(ratio));self.makeup=float(makeup_db)
 def process(self,x,sr):
  a=np.abs(x)+1e-9;db=20*np.log10(a);over=np.maximum(db-self.threshold,0);gain=10**((-(over*(1-1/self.ratio))+self.makeup)/20);return (x*gain).astype(np.float32)
class Gate(Effect):
 kind='gate'
 def __init__(self,threshold_db=-50):self.threshold=10**(float(threshold_db)/20)
 def process(self,x,sr):return np.where(np.abs(x)>=self.threshold,x,0).astype(np.float32)
class Limiter(Effect):
 kind='limiter'
 def __init__(self,ceiling_db=-1):self.ceiling=10**(float(ceiling_db)/20)
 def process(self,x,sr):return np.clip(x,-self.ceiling,self.ceiling).astype(np.float32)
class Distortion(Effect):
 kind='distortion'
 def __init__(self,drive=2,mix=1):self.drive=float(drive);self.mix=float(mix)
 def process(self,x,sr):return ((1-self.mix)*x+self.mix*np.tanh(x*self.drive)).astype(np.float32)
class Delay(Effect):
 kind='delay'
 def __init__(self,time_ms=180,feedback=.3,mix=.25):self.ms=float(time_ms);self.feedback=float(feedback);self.mix=float(mix);self.buf=None;self.pos=0
 def process(self,x,sr):
  n=max(1,int(sr*self.ms/1000));ch=x.shape[1]
  if self.buf is None or self.buf.shape!=(n,ch):self.buf=np.zeros((n,ch),np.float32);self.pos=0
  y=x.copy()
  for i in range(len(x)):
   d=self.buf[self.pos].copy();self.buf[self.pos]=x[i]+d*self.feedback;y[i]=(1-self.mix)*x[i]+self.mix*d;self.pos=(self.pos+1)%n
  return y
class Tremolo(Effect):
 kind='tremolo'
 def __init__(self,rate=5,depth=.5):self.rate=float(rate);self.depth=float(depth);self.phase=0.
 def process(self,x,sr):
  t=(np.arange(len(x))+self.phase)/sr;m=1-self.depth/2+self.depth/2*np.sin(2*np.pi*self.rate*t);self.phase=(self.phase+len(x))%sr;return (x*m[:,None]).astype(np.float32)
class Robot(Effect):
 kind='robot'
 def __init__(self,rate=45,mix=.8):self.rate=float(rate);self.mix=float(mix);self.phase=0.
 def process(self,x,sr):
  t=(np.arange(len(x))+self.phase)/sr;m=np.sign(np.sin(2*np.pi*self.rate*t));self.phase=(self.phase+len(x))%sr;return (x*((1-self.mix)+self.mix*m[:,None])).astype(np.float32)
REGISTRY={'gain':Gain,'filter':Biquad,'compressor':Compressor,'gate':Gate,'limiter':Limiter,'distortion':Distortion,'delay':Delay,'echo':Delay,'tremolo':Tremolo,'robot':Robot}
def build(spec):
 k=spec['type'];return REGISTRY[k](**spec.get('parameters',{}))
class Chain:
 def __init__(self,specs=None):self.specs=specs or [];self.effects=[build(s) for s in self.specs if s.get('enabled',True)]
 def process(self,x,sr):
  for e in self.effects:x=e.process(x,sr)
  return x
class ParametricEQ(Effect):
 kind='parametric_eq'
 def __init__(self,mode='peaking',frequency=1000,gain_db=0,q=.707):self.mode=mode;self.frequency=float(frequency);self.gain=float(gain_db);self.q=float(q);self._key=None
 def process(self,x,sr):
  key=(sr,x.shape[1],self.mode,self.frequency,self.gain,self.q)
  if key!=self._key:
   A=10**(self.gain/40);w=2*np.pi*min(self.frequency,sr*.49)/sr;c=np.cos(w);s=np.sin(w);alpha=s/(2*self.q)
   if self.mode=='peaking':b=[1+alpha*A,-2*c,1-alpha*A];a=[1+alpha/A,-2*c,1-alpha/A]
   elif self.mode=='notch':b=[1,-2*c,1];a=[1+alpha,-2*c,1-alpha]
   else:
    root=np.sqrt(A);two=2*root*alpha
    if self.mode=='lowshelf':b=[A*((A+1)-(A-1)*c+two),2*A*((A-1)-(A+1)*c),A*((A+1)-(A-1)*c-two)];a=[(A+1)+(A-1)*c+two,-2*((A-1)+(A+1)*c),(A+1)+(A-1)*c-two]
    elif self.mode=='highshelf':b=[A*((A+1)+(A-1)*c+two),-2*A*((A-1)+(A+1)*c),A*((A+1)+(A-1)*c-two)];a=[(A+1)-(A-1)*c+two,2*((A-1)-(A+1)*c),(A+1)-(A-1)*c-two]
    else:raise ValueError('invalid parametric EQ mode')
   a0=a[0];self._sos=np.array([[b[0]/a0,b[1]/a0,b[2]/a0,1,a[1]/a0,a[2]/a0]]);self._zi=np.zeros((1,2,x.shape[1]));self._key=key
  y,self._zi=sosfilt(self._sos,x,axis=0,zi=self._zi);return y.astype(np.float32)
REGISTRY['parametric_eq']=ParametricEQ
