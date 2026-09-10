from __future__ import annotations
import numpy as np
from scipy.signal import chirp,butter,sosfilt
import soundfile as sf
from pathlib import Path
def envelope(n,sr,attack=.01,decay=.05,sustain=.7,release=.1):
 a=min(n,int(attack*sr));d=min(n-a,int(decay*sr));r=min(n-a-d,int(release*sr));s=n-a-d-r;return np.concatenate([np.linspace(0,1,a,endpoint=False),np.linspace(1,sustain,d,endpoint=False),np.full(s,sustain),np.linspace(sustain,0,r)])
def render(spec:dict,path:Path,sr=48000):
 dur=float(spec.get('duration',1));assert .02<=dur<=30;n=int(sr*dur);t=np.arange(n)/sr;layers=[]
 for layer in spec.get('layers',[{"wave":"sine","frequency":440}]):
  wave=layer.get('wave','sine');f0=float(layer.get('frequency',440));f1=float(layer.get('end_frequency',f0));phase=2*np.pi*(f0*t+(f1-f0)*t*t/(2*dur))
  if wave=='sine':x=np.sin(phase)
  elif wave=='square':x=np.sign(np.sin(phase))
  elif wave=='saw':x=2*((f0*t)%1)-1
  elif wave=='triangle':x=2*np.abs(2*((f0*t)%1)-1)-1
  elif wave in ('noise','white_noise'):x=np.random.default_rng(int(layer.get('seed',0))).uniform(-1,1,n)
  else:raise ValueError('unsupported waveform')
  x*=float(layer.get('gain',.5))*envelope(n,sr,**layer.get('envelope',{}));layers.append(x)
 x=np.sum(layers,axis=0)
 for fx in spec.get('effects',[]):
  if fx['type']=='distortion':x=np.tanh(x*float(fx.get('drive',3)))
  elif fx['type']=='filter':x=sosfilt(butter(2,float(fx.get('frequency',4000)),btype=fx.get('mode','lowpass'),fs=sr,output='sos'),x)
  elif fx['type']=='reverse':x=x[::-1]
  elif fx['type']=='delay':
   k=int(sr*float(fx.get('time_ms',160))/1000);y=x.copy();fb=float(fx.get('feedback',.3));
   for pos in range(k,n,k):y[pos:]+=x[:n-pos]*(fb**(pos//k))
   x=y
 peak=np.max(np.abs(x)) or 1;x=(x/peak*float(spec.get('peak',.9))).astype(np.float32);stereo=np.column_stack((x,x)) if spec.get('stereo',False) else x;path.parent.mkdir(parents=True,exist_ok=True);sf.write(path,stereo,sr,subtype='PCM_16');return {"path":str(path),"frames":n,"sample_rate":sr,"duration":dur,"peak":float(np.max(np.abs(x)))}
