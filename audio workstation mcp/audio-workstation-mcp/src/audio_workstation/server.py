from __future__ import annotations
from mcp.server.fastmcp import FastMCP
from .service import Workstation
ws=Workstation();mcp=FastMCP('audio-workstation',instructions='Local real-time audio control. Read state first. Mutations return approval plans; call audio_approve_change then audio_execute_change. Never claim AI conversion or device delivery unless capability and stream verification prove it.')
# Approval
@mcp.tool()
def audio_approve_change(plan_id:str,explicit_approval:str)->dict:"""Approve an exact consequential change for 60 seconds.""";return ws.approval.approve(plan_id,explicit_approval)
@mcp.tool()
def audio_execute_change(plan_id:str,approval_token:str)->dict:"""Execute an approved exact change and verify readback.""";return ws.execute(plan_id,approval_token)
# Devices/read
@mcp.tool()
def audio_list_devices()->object:"""Discover actual PortAudio devices.""";return ws.devices()
@mcp.tool()
def audio_list_virtual_devices()->object:"""Discover endpoints whose names indicate virtual/cable/loopback transport.""";d=ws.devices();return [x for x in d if x['virtual']] if isinstance(d,list) else d
@mcp.tool()
def audio_get_device_info(device_id:int)->dict:"""Get one discovered device.""";return next(x for x in ws.devices() if x['id']==device_id)
@mcp.tool()
def audio_get_default_devices()->dict:
 """Get PortAudio default input/output identifiers."""
 try:return {'input':ws.engine.backend.sd.default.device[0],'output':ws.engine.backend.sd.default.device[1]}
 except Exception as e:return {'available':False,'error':str(e)}
@mcp.tool()
def audio_get_capabilities()->dict:"""Get real backend, model, acceleration and device capabilities.""";return ws.capabilities()
# Engine/routing
@mcp.tool()
def audio_start(input_device:int,output_device:int,sample_rate:int=48000,channels:int=1,blocksize:int=0,latency:str='low')->dict:"""Plan activation of live microphone capture and output.""";return ws.plan('engine_start',{'input':input_device,'output':output_device,'sample_rate':sample_rate,'channels':channels,'blocksize':blocksize,'latency':latency})
@mcp.tool()
def audio_stop()->dict:"""Plan stopping active stream.""";return ws.plan('engine_stop',{})
@mcp.tool()
def audio_pause()->dict:"""Plan pausing the open PortAudio stream.""";return ws.plan('engine_pause',{})
@mcp.tool()
def audio_resume()->dict:"""Plan resuming a paused PortAudio stream.""";return ws.plan('engine_resume',{})
@mcp.tool()
def audio_restart()->dict:"""Return current config so caller can approve stop then start.""";return {'two_step_required':True,'configuration':ws.store.data['engine'],'note':'Stop and start are separately verified.'}
@mcp.tool()
def audio_get_status()->dict:"""Read persistent and live backend status.""";return ws.engine.verify()
@mcp.tool()
def audio_verify()->dict:"""Verify active stream, callback recency, levels and resources.""";return ws.engine.verify()
@mcp.tool()
def audio_get_routes()->dict:"""Read configured endpoints and routes.""";return {'engine':ws.store.data['engine'],'routes':ws.store.data['routing']}
@mcp.tool()
def audio_set_input(device_id:int)->dict:"""Plan input endpoint change; restart required if running.""";return ws.plan('set_route',{'direction':'input','device':device_id})
@mcp.tool()
def audio_set_output(device_id:int)->dict:"""Plan output endpoint change; restart required if running.""";return ws.plan('set_route',{'direction':'output','device':device_id})
# Mixer
@mcp.tool()
def audio_get_mixer_state()->dict:return ws.store.data['mixer']
def _m(target,param,value):return ws.plan('set_mixer',{'target':target,'parameter':param,'value':value})
@mcp.tool()
def audio_set_volume(target:str,value:float)->dict:"""Plan source/master linear volume 0..2.""";assert 0<=value<=2;return _m(target,'volume',value)
@mcp.tool()
def audio_set_gain(target:str,db:float)->dict:"""Plan gain in dB.""";assert -60<=db<=24;return _m(target,'gain_db',db)
@mcp.tool()
def audio_set_pan(target:str,value:float)->dict:"""Plan pan from -1 to 1.""";assert -1<=value<=1;return _m(target,'pan',value)
@mcp.tool()
def audio_mute(target:str,muted:bool=True)->dict:return _m(target,'mute',muted)
@mcp.tool()
def audio_solo(target:str,solo:bool=True)->dict:return _m(target,'solo',solo)
@mcp.tool()
def audio_set_crossfader(value:float)->dict:"""Plan deck crossfader -1 (A) to +1 (B).""";assert -1<=value<=1;return _m('master','crossfader',value)
# DSP/EQ
@mcp.tool()
def audio_get_effect_chain(target:str)->list:return ws.store.data['chains'][target]
@mcp.tool()
def audio_set_effect_chain(target:str,effects:list[dict])->dict:"""Plan complete validated composable chain replacement.""";return ws.plan('set_chain',{'target':target,'effects':effects})
@mcp.tool()
def audio_add_effect(target:str,effect_type:str,parameters:dict)->dict:"""Plan appending a real DSP effect.""";chain=ws.store.data['chains'][target]+[{'type':effect_type,'parameters':parameters,'enabled':True}];return ws.plan('set_chain',{'target':target,'effects':chain})
@mcp.tool()
def audio_remove_effect(target:str,index:int)->dict:chain=list(ws.store.data['chains'][target]);chain.pop(index);return ws.plan('set_chain',{'target':target,'effects':chain})
@mcp.tool()
def audio_set_eq(target:str,bands:list[dict],preamp_db:float=0)->dict:"""Plan pass filters and peaking/notch/shelf parametric bands plus preamp.""";fx=[{'type':'gain','parameters':{'db':preamp_db}}]+[{'type':'parametric_eq' if b.get('mode') in ('peaking','notch','lowshelf','highshelf') else 'filter','parameters':b} for b in bands];return ws.plan('set_chain',{'target':target,'effects':fx})
@mcp.tool()
def audio_set_bass(target:str,db:float)->dict:"""Plan semantic bass adjustment (gain plus low-pass parallel approximation is not claimed).""";return audio_add_effect(target,'parametric_eq',{'mode':'lowshelf','frequency':180,'gain_db':db,'q':.707})
@mcp.tool()
def audio_set_treble(target:str,db:float)->dict:return audio_add_effect(target,'parametric_eq',{'mode':'highshelf','frequency':4500,'gain_db':db,'q':.707})
@mcp.tool()
def audio_set_compressor(target:str,threshold_db:float=-18,ratio:float=4,makeup_db:float=0)->dict:return audio_add_effect(target,'compressor',{'threshold_db':threshold_db,'ratio':ratio,'makeup_db':makeup_db})
@mcp.tool()
def audio_set_limiter(target:str,ceiling_db:float=-1)->dict:return audio_add_effect(target,'limiter',{'ceiling_db':ceiling_db})
@mcp.tool()
def audio_set_gate(target:str,threshold_db:float=-50)->dict:return audio_add_effect(target,'gate',{'threshold_db':threshold_db})
# Voice
@mcp.tool()
def voice_list_profiles(query:str='')->list:return [x for x in ws.voice.list() if query.lower() in x['name'].lower()]
@mcp.tool()
def voice_get_state()->dict:return ws.store.data['voice']|{'chain':ws.store.data['chains']['voice']}
@mcp.tool()
def voice_create_profile(name:str,description:str,effects:list[dict],engine:str='dsp',reference:str|None=None,parameters:dict|None=None)->dict:return ws.plan('save_voice',{'name':name,'description':description,'effects':effects,'engine':engine,'reference':reference,'parameters':parameters or {}})
@mcp.tool()
def voice_import_reference(path:str,name:str,rights_confirmation:bool)->dict:
 """Plan local validation/preprocessing of authorized reference audio. Does not pretend to train a model."""
 if not rights_confirmation:raise ValueError('rights confirmation required')
 return ws.plan('import_reference',{'path':path,'name':name})
@mcp.tool()
def voice_analyze_reference(path:str)->dict:return ws.analyze_file(path)
@mcp.tool()
def voice_activate(profile_id:str)->dict:return ws.plan('activate_voice',{'id':profile_id})
@mcp.tool()
def voice_deactivate()->dict:return ws.plan('set_chain',{'target':'voice','effects':[]})
@mcp.tool()
def voice_delete(profile_id:str)->dict:return ws.plan('delete_voice',{'id':profile_id})
@mcp.tool()
def voice_set_pitch(semitones:float)->dict:
 """Pitch shift needs a phase-vocoder plugin not included in the callback; reports truthful unavailable status."""
 return {'available':False,'required':'real-time phase vocoder/Rubber Band adapter','requested_semitones':semitones}
@mcp.tool()
def voice_list_engines()->list:return ws.capabilities()['voice_engines']
@mcp.tool()
def voice_get_conversion_status()->dict:return {'selected':ws.store.data['voice'],'engines':ws.capabilities()['voice_engines'],'warning':'Reference preprocessing is not AI model training. Genuine conversion remains unavailable until a compatible runtime/model adapter is installed.'}
# Sounds
@mcp.tool()
def soundboard_list(query:str='',category:str='')->list:return [v for v in ws.sounds.items.values() if query.lower() in v['name'].lower() and (not category or v['category']==category)]
@mcp.tool()
def soundboard_import(path:str,name:str,category:str='custom',normalize:bool=True)->dict:return ws.plan('sound_import',{'path':path,'name':name,'category':category,'normalize':normalize})
@mcp.tool()
def sound_create(name:str,spec:dict,category:str='generated',sample_rate:int=48000)->dict:"""Plan actual oscillator/noise/envelope/layer/effect synthesis to WAV and library.""";return ws.plan('sound_create',{'name':name,'spec':spec,'category':category,'sample_rate':sample_rate})
@mcp.tool()
def soundboard_play(sound_id:str,volume:float=1,loop:bool=False,speed:float=1,pitch_semitones:float=0)->dict:return ws.plan('sound_play',{'id':sound_id,'volume':volume,'loop':loop,'speed':speed,'pitch':pitch_semitones})
@mcp.tool()
def soundboard_stop(sound_id:str|None=None)->dict:return ws.plan('sound_control',{'id':sound_id,'command':'stop'})
@mcp.tool()
def soundboard_pause(sound_id:str|None=None)->dict:return ws.plan('sound_control',{'id':sound_id,'command':'pause'})
@mcp.tool()
def soundboard_resume(sound_id:str|None=None)->dict:return ws.plan('sound_control',{'id':sound_id,'command':'resume'})
@mcp.tool()
def soundboard_get_state()->dict:return ws.sounds.state()
@mcp.tool()
def soundboard_categorize(sound_id:str,category:str)->dict:return ws.plan('sound_update',{'id':sound_id,'values':{'category':category}})
@mcp.tool()
def soundboard_set_favorite(sound_id:str,favorite:bool=True)->dict:return ws.plan('sound_update',{'id':sound_id,'values':{'favorite':favorite}})
@mcp.tool()
def soundboard_delete(sound_id:str)->dict:return ws.plan('sound_delete',{'id':sound_id})
# DJ state/control
@mcp.tool()
def dj_load_track(deck:str,path:str)->dict:return ws.plan('dj_load',{'deck':deck,'path':path})
@mcp.tool()
def dj_get_state()->dict:return ws.store.data['dj']
@mcp.tool()
def dj_play(deck:str)->dict:return ws.plan('dj_control',{'deck':deck,'values':{'status':'playing'}})
@mcp.tool()
def dj_pause(deck:str)->dict:return ws.plan('dj_control',{'deck':deck,'values':{'status':'paused'}})
@mcp.tool()
def dj_stop(deck:str)->dict:return ws.plan('dj_control',{'deck':deck,'values':{'status':'stopped','position':0}})
@mcp.tool()
def dj_seek(deck:str,seconds:float)->dict:return ws.plan('dj_control',{'deck':deck,'values':{'position':seconds}})
@mcp.tool()
def dj_set_speed(deck:str,speed:float)->dict:return ws.plan('dj_control',{'deck':deck,'values':{'speed':speed}})
@mcp.tool()
def dj_set_pitch(deck:str,semitones:float)->dict:return ws.plan('dj_control',{'deck':deck,'values':{'pitch':semitones}})
@mcp.tool()
def dj_set_crossfader(value:float)->dict:return audio_set_crossfader(value)
# Analysis/presets/triggers
@mcp.tool()
def audio_get_levels()->dict:return ws.engine.level
@mcp.tool()
def audio_get_latency()->dict:return ws.engine.verify()
@mcp.tool()
def audio_get_stream_health()->dict:return ws.engine.verify()
@mcp.tool()
def audio_analyze_file(path:str)->dict:return ws.analyze_file(path)
@mcp.tool()
def preset_list()->dict:return ws.store.data['presets']
@mcp.tool()
def preset_save(name:str)->dict:return ws.plan('preset_save',{'name':name})
@mcp.tool()
def preset_load(name:str)->dict:return ws.plan('preset_load',{'name':name})
@mcp.tool()
def preset_clone(name:str,new_name:str)->dict:return ws.plan('preset_clone',{'name':name,'new_name':new_name})
@mcp.tool()
def preset_delete(name:str)->dict:return ws.plan('preset_delete',{'name':name})
@mcp.tool()
def preset_export(name:str)->dict:"""Return portable preset JSON; read-only.""";return ws.store.data['presets'][name]
@mcp.tool()
def trigger_list()->dict:return ws.triggers
@mcp.tool()
def trigger_create(key:str,action:dict)->dict:return ws.plan('trigger_save',{'key':key,'action':action})
@mcp.tool()
def audio_get_complete_state()->dict:return ws.store.snapshot()|{'live':ws.engine.verify(),'soundboard_live':ws.sounds.state()}
def main():mcp.run(transport='stdio')
if __name__=='__main__':main()
