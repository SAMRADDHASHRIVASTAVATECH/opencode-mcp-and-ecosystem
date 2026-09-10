from __future__ import annotations
import json,shutil,time,hashlib
from pathlib import Path
import numpy as np,soundfile as sf
PRESETS={
'Clean':[], 'Deep':[{'type':'filter','parameters':{'mode':'lowpass','frequency':6500}},{'type':'compressor','parameters':{'threshold_db':-20,'ratio':3}}],
'High':[{'type':'filter','parameters':{'mode':'highpass','frequency':180}},{'type':'gain','parameters':{'db':2}}],
'Robot':[{'type':'robot','parameters':{'rate':45,'mix':.85}},{'type':'delay','parameters':{'time_ms':55,'feedback':.15,'mix':.15}}],
'Alien':[{'type':'robot','parameters':{'rate':73,'mix':.45}},{'type':'tremolo','parameters':{'rate':7,'depth':.5}},{'type':'delay','parameters':{'time_ms':110,'mix':.2}}],
'Monster':[{'type':'distortion','parameters':{'drive':2.5,'mix':.4}},{'type':'filter','parameters':{'mode':'lowpass','frequency':4200}},{'type':'compressor','parameters':{'threshold_db':-24,'ratio':5}}],
'Radio':[{'type':'filter','parameters':{'mode':'bandpass','frequency':[350,3500]}},{'type':'distortion','parameters':{'drive':1.5,'mix':.2}},{'type':'compressor','parameters':{'threshold_db':-25,'ratio':6}}],
'Telephone':[{'type':'filter','parameters':{'mode':'bandpass','frequency':[450,3000]}},{'type':'distortion','parameters':{'drive':1.3,'mix':.12}}],
'Megaphone':[{'type':'filter','parameters':{'mode':'bandpass','frequency':[300,4500]}},{'type':'distortion','parameters':{'drive':3,'mix':.55}},{'type':'compressor','parameters':{'threshold_db':-30,'ratio':8}}],
'Synthetic':[{'type':'robot','parameters':{'rate':30,'mix':.3}},{'type':'tremolo','parameters':{'rate':4,'depth':.25}}],
'Distorted':[{'type':'distortion','parameters':{'drive':5,'mix':.7}},{'type':'limiter','parameters':{'ceiling_db':-2}}],
'Echo Chamber':[{'type':'delay','parameters':{'time_ms':220,'feedback':.45,'mix':.35}},{'type':'delay','parameters':{'time_ms':370,'feedback':.25,'mix':.2}}],
'Sci-Fi Comms':[{'type':'gate','parameters':{'threshold_db':-45}},{'type':'filter','parameters':{'mode':'bandpass','frequency':[280,5000]}},{'type':'robot','parameters':{'rate':60,'mix':.2}},{'type':'delay','parameters':{'time_ms':80,'mix':.12}}],
'Ghost':[{'type':'filter','parameters':{'mode':'highpass','frequency':250}},{'type':'delay','parameters':{'time_ms':300,'feedback':.55,'mix':.4}}]}
class VoiceLibrary:
 def __init__(self,root:Path):self.root=root;self.profiles=root/'voices/profiles';self.refs=root/'voices/references';self.profiles.mkdir(parents=True,exist_ok=True);self.refs.mkdir(parents=True,exist_ok=True);self._seed()
 def _seed(self):
  for name,chain in PRESETS.items():
   p=self.profiles/(name.lower().replace(' ','_')+'.json')
   if not p.exists():p.write_text(json.dumps({'name':name,'description':'Original DSP preset','engine':'dsp','effects':chain,'version':1},indent=2))
 def list(self):return [json.loads(p.read_text())|{'id':p.stem} for p in self.profiles.glob('*.json')]
 def save(self,name,data):
  ident=''.join(c for c in name.lower().replace(' ','_') if c.isalnum() or c=='_');assert ident;old=self.profiles/f'{ident}.json';v=(json.loads(old.read_text()).get('version',0)+1) if old.exists() else 1;payload={'name':name,'description':data.get('description',''),'engine':data.get('engine','dsp'),'effects':data.get('effects',[]),'reference':data.get('reference'),'parameters':data.get('parameters',{}),'version':v,'updated_at':time.time()};old.write_text(json.dumps(payload,indent=2));return payload|{'id':ident}
 def import_reference(self,source:Path,name:str):
  data,sr=sf.read(source,dtype='float32',always_2d=True);assert sr>=16000 and len(data)/sr>=1;mono=data.mean(axis=1);threshold=max(np.max(np.abs(mono))*.01,1e-4);idx=np.flatnonzero(np.abs(mono)>threshold);assert len(idx);mono=mono[idx[0]:idx[-1]+1];peak=np.max(np.abs(mono));mono=mono/(peak or 1)*.9;ident=hashlib.sha256(source.read_bytes()).hexdigest()[:16];dest=self.refs/f'{ident}.wav';sf.write(dest,mono,sr);return {'reference_id':ident,'path':str(dest),'sample_rate':sr,'duration':len(mono)/sr,'rms':float(np.sqrt(np.mean(mono*mono))),'peak':float(np.max(np.abs(mono))),'note':'Preprocessed reference only. A compatible trained model is still required for genuine AI conversion.'}
