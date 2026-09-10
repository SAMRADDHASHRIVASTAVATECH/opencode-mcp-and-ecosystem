from __future__ import annotations
import json,os,platform,shutil,time
from pathlib import Path
import numpy as np,soundfile as sf,psutil
from scipy.fft import rfft,rfftfreq
from .state.store import StateStore
from .state.approval import Approval
from .audio.engine import RealtimeEngine
from .voice.profiles import VoiceLibrary
from .sound.library import SoundLibrary
from .sound.synthesis import render
class Workstation:
 def __init__(self):
  self.root=Path(os.environ.get('AUDIO_WORKSTATION_DATA',Path.home()/'audio-workstation-data')).resolve();self.root.mkdir(parents=True,exist_ok=True);self.store=StateStore(self.root/'config/state.json');self.approval=Approval();self.voice=VoiceLibrary(self.root);self.sounds=SoundLibrary(self.root);self.engine=RealtimeEngine(self.store);self.triggers=self._json('config/triggers.json',{});self._attach_mix()
 def _attach_mix(self):
  original=self.engine.chain
  # soundboard is mixed by wrapping callback directly
  old=self.engine._callback
  def cb(indata,outdata,frames,t,status):
   old(indata,outdata,frames,t,status);s=self.sounds.mix(frames,self.store.data['engine']['sample_rate'],outdata.shape[1]);mic_active=self.engine.level['rms']>.02;factor=self.sounds.duck if mic_active else 1.;outdata[:]=np.clip(outdata+s*factor,-1,1)
  self.engine.backend.callback=cb
 def _json(self,rel,default):
  p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True)
  try:return json.loads(p.read_text())
  except:return default
 def devices(self):
  try:return self.engine.backend.devices()
  except Exception as e:return {'available':False,'devices':[],'error':str(e),'host':platform.platform()}
 def capabilities(self):
  mods={m:bool(__import__('importlib').util.find_spec(m)) for m in ('sounddevice','soundfile','numpy','scipy','torch','onnxruntime')};mods['sounddevice']=bool(self.engine.backend.status()['available']);return {'backend':'PortAudio/sounddevice','modules':mods,'devices':self.devices(),'voice_engines':[{'id':'dsp','available':True,'genuine_ai':False},{'id':'rvc_external','available':mods['torch'] and any((self.root/'models').glob('*.pth')),'genuine_ai':True,'note':'Requires compatible RVC runtime, HuBERT/F0 assets and authorized model; not loaded by this process.'},{'id':'onnx_plugin','available':mods['onnxruntime'],'genuine_ai':True,'note':'Requires a compatible explicitly integrated model adapter.'}],'hardware':{'cpu_count':psutil.cpu_count(),'memory_gb':round(psutil.virtual_memory().total/2**30,2),'cuda':mods['torch'] and __import__('torch').cuda.is_available() if mods['torch'] else False}}
 def plan(self,action,args):return self.approval.plan(action,args,self.store.snapshot(),self._impact(action,args))
 def execute(self,pid,token):
  p=self.approval.consume(pid,token);started=time.time();result=self._apply(p['action'],p['arguments']);verified=self.verify_action(p['action'],result);log=self.root/'logs/operations.jsonl';log.parent.mkdir(parents=True,exist_ok=True);safe={'time':started,'action':p['action'],'arguments':{k:v for k,v in p['arguments'].items() if k not in ('audio','content','password','token')},'duration_ms':(time.time()-started)*1000,'verified':bool(verified)}
  with log.open('a') as f:f.write(json.dumps(safe)+'\n')
  return {'success':True,'requested':p,'result':result,'verified':verified}
 def _impact(self,a,x):
  impacts={'engine_start':'Activates microphone capture and audio output','set_route':'Changes live audio endpoints','sound_play':'Emits audio to configured output','import_reference':'Copies and analyzes user voice audio locally; no training occurs','delete':'Permanently removes local library data','preset_load':'Replaces active audio configuration'}
  return impacts.get(a,'Changes persistent or live audio workstation state')
 def _apply(self,a,x):
  if a=='engine_start':return self.engine.start(x['input'],x['output'],int(x.get('sample_rate',48000)),int(x.get('channels',1)),int(x.get('blocksize',0)),x.get('latency','low'))
  if a=='engine_stop':return self.engine.stop()
  if a=='engine_pause':return self.engine.pause()
  if a=='engine_resume':return self.engine.resume()
  if a=='set_route':self.store.data['engine'][x['direction']]=x['device'];self.store.save();return self.store.data['engine']
  if a=='set_mixer':
   target=x['target'];self.store.data['mixer'].setdefault(target,{}).update({x['parameter']:x['value']})
   if x['parameter']=='crossfader':
    v=float(x['value']);self.store.data['dj']['crossfader']=v
    for deck,factor in [('a',(1-v)/2),('b',(1+v)/2)]:
     ident=f'deck_{deck}'
     if ident in self.sounds.playing:self.sounds.playing[ident].volume=self.store.data['mixer']['decks'][deck]['volume']*factor
   self.store.save();return self.store.data['mixer'][target]
  if a=='set_chain':self.store.data['chains'][x['target']]=x['effects'];self.engine.rebuild();self.store.save();return self.store.data['chains'][x['target']]
  if a=='activate_voice':
   profile=next(v for v in self.voice.list() if v['id']==x['id']);self.store.data['voice']['active']=x['id'];self.store.data['chains']['voice']=profile['effects'];self.engine.rebuild();self.store.save();return self.store.data['voice']|{'chain':profile['effects']}
  if a=='save_voice':return self.voice.save(x['name'],x)
  if a=='import_reference':return self.voice.import_reference(Path(x['path']).resolve(),x['name'])
  if a=='delete_voice':
   p=self.voice.profiles/f"{x['id']}.json";p.unlink();return {'deleted':x['id'],'verified':not p.exists()}
  if a=='sound_create':
   path=self.root/'sounds/generated'/f"{x['name']}.wav";meta=render(x['spec'],path,int(x.get('sample_rate',48000)));item=self.sounds.add(path,x['name'],x.get('category','generated'),False);return {'render':meta,'library':item}
  if a=='sound_import':return self.sounds.add(Path(x['path']).resolve(),x['name'],x.get('category','custom'),x.get('normalize',True))
  if a=='sound_update':self.sounds.items[x['id']].update(x['values']);self.sounds.save();return self.sounds.items[x['id']]
  if a=='sound_delete':
   item=self.sounds.items.pop(x['id']);Path(item['path']).unlink(missing_ok=True);self.sounds.playing.pop(x['id'],None);self.sounds.save();return {'deleted':x['id'],'verified':x['id'] not in self.sounds.items}
  if a=='sound_play':return self.sounds.play(x['id'],float(x.get('volume',1)),x.get('loop',False),float(x.get('speed',1)),float(x.get('pitch',0)))
  if a=='sound_control':
   ident=x.get('id');cmd=x['command'];targets=list(self.sounds.playing) if ident is None else [ident]
   for i in targets:
    if cmd=='stop':self.sounds.playing.pop(i,None)
    elif i in self.sounds.playing:self.sounds.playing[i].paused=cmd=='pause'
   return self.sounds.state()
  if a=='preset_save':self.store.data['presets'][x['name']]={'version':self.store.data['presets'].get(x['name'],{}).get('version',0)+1,'state':self.store.snapshot(),'saved_at':time.time()};self.store.save();return self.store.data['presets'][x['name']]
  if a=='preset_load':
   keep=self.store.data['presets'];self.store.data=self.store.data['presets'][x['name']]['state'];self.store.data['presets']=keep;self.engine.rebuild();self.store.save();return self.store.snapshot()
  if a=='preset_clone':self.store.data['presets'][x['new_name']]=json.loads(json.dumps(self.store.data['presets'][x['name']]));self.store.data['presets'][x['new_name']]['version']=1;self.store.save();return self.store.data['presets'][x['new_name']]
  if a=='preset_delete':del self.store.data['presets'][x['name']];self.store.save();return {'deleted':x['name']}
  if a=='trigger_save':self.triggers[x['key']]=x['action'];p=self.root/'config/triggers.json';p.write_text(json.dumps(self.triggers,indent=2));return self.triggers[x['key']]
  if a=='dj_load':
   path=Path(x['path']).resolve();data,sr=sf.read(path,dtype='float32',always_2d=True);ident=f"deck_{x['deck']}";dest=self.root/'cache'/f'{ident}.wav';dest.parent.mkdir(parents=True,exist_ok=True);sf.write(dest,data,sr);self.sounds.items[ident]={'id':ident,'name':path.name,'category':'dj','path':str(dest),'duration':len(data)/sr,'channels':data.shape[1],'sample_rate':sr};self.store.data['dj']['decks'][x['deck']]={'track':str(path),'sound_id':ident,'status':'loaded','position':0.,'speed':1.,'pitch':0.};self.store.save();return self.store.data['dj']['decks'][x['deck']]
  if a=='dj_control':
   deck=self.store.data['dj']['decks'][x['deck']];values=x['values'];ident=deck['sound_id']
   if values.get('status')=='playing':self.sounds.play(ident,float(self.store.data['mixer']['decks'][x['deck']]['volume']),False,float(values.get('speed',deck.get('speed',1))),float(values.get('pitch',deck.get('pitch',0))))
   elif values.get('status')=='paused' and ident in self.sounds.playing:self.sounds.playing[ident].paused=True
   elif values.get('status')=='stopped':self.sounds.playing.pop(ident,None)
   if 'position' in values and ident in self.sounds.playing:self.sounds.playing[ident].pos=float(values['position'])*self.sounds.playing[ident].data[1]
   deck.update(values);self.store.save();return deck|{'playback_verified':ident in self.sounds.playing}
  raise ValueError('unsupported action')
 def verify_action(self,a,result):return {'state_revision':self.store.data['revision'],'engine':self.engine.verify(),'readback':result}
 def analyze_file(self,path):
  data,sr=sf.read(Path(path),dtype='float32',always_2d=True);mono=data.mean(axis=1);peak=float(np.max(np.abs(data)));rms=float(np.sqrt(np.mean(data*data)));win=mono[:min(len(mono),sr*10)];spec=np.abs(rfft(win*np.hanning(len(win))));freq=rfftfreq(len(win),1/sr);top=np.argsort(spec)[-20:][::-1];return {'sample_rate':sr,'channels':data.shape[1],'frames':len(data),'duration':len(data)/sr,'peak':peak,'rms':rms,'dbfs_rms':20*np.log10(rms+1e-12),'clipping_samples':int(np.sum(np.abs(data)>=.999)),'spectrum_peaks':[{'hz':float(freq[i]),'magnitude':float(spec[i])} for i in top]}
