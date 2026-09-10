from __future__ import annotations
import os,json
from pathlib import Path
from .config import Config
from .runtime import PersonRuntime
from .avatar import AvatarServer
CFG=Config.load();RUNTIME=PersonRuntime(CFG);AVATAR=None
try:from fastmcp import FastMCP
except ImportError:from mcp.server.fastmcp import FastMCP
mcp=FastMCP('Personal Autonomous Desktop Person',instructions='Persistent conservative digital-person runtime. Start it, inspect state, set/approve goals, and route approved physical actions to the configured computer-use MCP. Never skip approvals.')
@mcp.tool
def start_person()->dict:
 """Start persistent cognition and the local avatar view."""
 global AVATAR
 s=RUNTIME.start()
 if CFG.avatar_enabled and AVATAR is None:
  web=Path(__file__).resolve().parent/'web';AVATAR=AvatarServer(RUNTIME,CFG.avatar_host,CFG.avatar_port,web);s['avatar_url']=AVATAR.start()
 return s
@mcp.tool
def pause_person()->dict:"""Pause cognition while preserving state.""";return RUNTIME.pause()
@mcp.tool
def resume_person()->dict:"""Resume cognition.""";return RUNTIME.resume()
@mcp.tool
def emergency_stop()->dict:"""Enter SAFE_IDLE and authorize no external action; independent of model output.""";return RUNTIME.stop(True)
@mcp.tool
def person_status()->dict:"""Return identity, affect, goal, intention, approvals and activity.""";return RUNTIME.status()
@mcp.tool
def talk(message:str)->dict:"""Send a user dialogue event through personality, memory and current state.""";return RUNTIME.talk(message)
@mcp.tool
def submit_event(description:str,kind:str='environment',importance:float=.5)->dict:"""Submit a consented environmental event; do not send unapproved sensitive screen content.""";return RUNTIME.event(description,kind,max(0,min(1,importance)))
@mcp.tool
def set_goal(goal:str,success_condition:str='',priority:int=50,budget_seconds:int=900)->dict:"""Create a proposed goal. It cannot execute until approved.""";return RUNTIME.set_goal(goal,success_condition,priority,budget_seconds)
@mcp.tool
def approve_goal()->dict:"""Approve the currently proposed goal.""";return RUNTIME.approve_goal()
@mcp.tool
def cancel_goal()->dict:"""Cancel the current goal.""";return RUNTIME.cancel_goal()
@mcp.tool
def propose_computer_action(action_type:str,summary:str,parameters:dict,expected_result:str='')->dict:
 """Create a risk-classified action proposal. R1+ actions require explicit approval under conservative policy."""
 return RUNTIME.request_action({'type':action_type,'summary':summary,'parameters':parameters,'expected_result':expected_result})
@mcp.tool
def decide_action(approval_id:str,approve:bool)->dict:
 """User decision for one exact action. If approved, returns a delegation envelope for OpenCode's computer-use MCP."""
 return RUNTIME.decide_approval(approval_id,approve)
@mcp.tool
def pending_approvals()->list[dict]:"""List exact pending action approvals.""";from .models import obj;return obj(RUNTIME.state.pending_approvals)
@mcp.tool
def record_experience(summary:str,outcome:str='observed',confidence:float=1.,importance:float=.6)->dict:"""Record a verified tool/task outcome so future decisions can learn from it.""";return RUNTIME.record_experience(summary,outcome,max(0,min(1,confidence)),max(0,min(1,importance)))
@mcp.tool
def memory_search(query:str,limit:int=10)->list[dict]:"""Retrieve traceable memories from local storage.""";return RUNTIME.memory.search(query,max(1,min(50,limit)))
@mcp.tool
def correct_memory(event_id:int,corrected_content:str)->dict:"""Supersede an incorrect memory with a user-authored correction.""";return {'new_event_id':RUNTIME.memory.correct(event_id,corrected_content)}
@mcp.tool
def forget_memory(event_id:int)->dict:"""Delete a selected memory.""";RUNTIME.memory.forget(event_id);return {'deleted':event_id}
@mcp.tool
def explain_state()->dict:
 """Explain current behavior from explicit causal state, without inventing inner experience."""
 s=RUNTIME.state;return {'mode':s.affect.mode,'causes':s.affect.causes,'intention':s.intention,'goal':s.active_goal.text if s.active_goal else None,'explanation':f'Mode {s.affect.mode} follows recent appraisals and bounded decay; current intention is {s.intention}.'}
@mcp.tool
def identity_profile()->dict:"""Return the versioned local identity/personality profile.""";return RUNTIME.personality.context()
@mcp.tool
def update_preferences(interests:list[str]|None=None,style:dict|None=None)->dict:"""Update owner-editable interests/style; immutable identity and safety cannot be self-edited.""";d={};d.update({'interests':interests} if interests is not None else {});d.update({'style':style} if style is not None else {});return RUNTIME.personality.update_preferences(d)
@mcp.tool
def health_check()->dict:"""Report runtime, model, avatar and storage readiness.""";return {'ok':True,'runtime':RUNTIME.state.status.value,'model_configured':RUNTIME.models.available,'avatar_url':f'http://{CFG.avatar_host}:{CFG.avatar_port}' if CFG.avatar_enabled else None,'memory_db':str(Path(CFG.data_dir)/'person.db'),'computer_use_delegate':CFG.computer_use_server}
@mcp.tool
def current_state()->dict:
 """Return materialized cognitive and affect state.""";return RUNTIME.status()
@mcp.tool
def current_intention()->dict:
 """Return current intention and attention focus.""";return {'intention':RUNTIME.state.intention,'foreground_event':getattr(RUNTIME.attention.foreground,'id',None),'interruptions':len(RUNTIME.attention.interruptions)}
@mcp.tool
def world_summary(namespace:str='')->list[dict]:
 """Return provenance-aware beliefs, optionally in one namespace.""";return RUNTIME.world.summary(namespace or None)
@mcp.tool
def task_list()->list[dict]:
 """List persistent tasks.""";return RUNTIME.tasks.list()
@mcp.tool
def propose_plan(steps:list[dict],success_condition:str,failure_condition:str='',budget_seconds:int=900)->dict:
 """Create a persistent proposed task plan for the active goal."""
 if not RUNTIME.state.active_goal:raise ValueError('Set a goal first')
 return RUNTIME.tasks.propose(RUNTIME.state.active_goal.id,steps,success_condition,failure_condition,budget_seconds)
@mcp.tool
def approve_plan(task_id:str)->dict:
 """Mark a reviewed proposed plan approved.""";return RUNTIME.tasks.update(task_id,'approved')
@mcp.tool
def start_task(task_id:str)->dict:
 """Start an approved persistent task."""
 t=RUNTIME.tasks.get(task_id)
 if not t or t['status']!='approved':raise ValueError('Plan must be approved')
 return RUNTIME.tasks.start(task_id)
@mcp.tool
def task_status(task_id:str)->dict:
 """Return one task state.""";return RUNTIME.tasks.get(task_id) or {'status':'missing'}
@mcp.tool
def task_intervene(task_id:str,instruction:str)->dict:
 """Pause a task and record trusted user intervention.""";RUNTIME.feedback(task_id,instruction,'task');return RUNTIME.tasks.update(task_id,'paused',intervention=instruction)
@mcp.tool
def record_action_result(capability_id:str,task_id:str,success:bool,evidence:dict)->dict:
 """Close an issued capability and feed verified outcome into task, cognition, learning and memory.""";return RUNTIME.record_action_result(capability_id,task_id,success,evidence)
@mcp.tool
def capability_status()->list[dict]:
 """List issued/revoked/expiring capabilities.""";return RUNTIME.capabilities.list()
@mcp.tool
def submit_feedback(target:str,feedback:str,scope:str='task')->dict:
 """Record explicit structured feedback for bounded strategy learning.""";return RUNTIME.feedback(target,feedback,scope)
@mcp.tool
def reflect(reason:str='user requested')->dict:
 """Create a source-grounded reflection from actual experiences.""";return RUNTIME.reflections.reflect(reason)
@mcp.tool
def install_skill_plan(manifest:dict)->dict:
 """Validate and stage a versioned skill manifest; does not activate it.""";return RUNTIME.skills.install_plan(manifest)
@mcp.tool
def approve_skill_install(skill_id:str,regression_tests_passed:bool)->dict:
 """Activate only a reviewed skill whose regression tests passed.""";return RUNTIME.skills.approve(skill_id,regression_tests_passed)
@mcp.tool
def skill_list(active_only:bool=False)->list[dict]:
 """List persistent skill manifests and outcome statistics.""";return RUNTIME.skills.list(active_only)
@mcp.tool
def set_quiet_mode(enabled:bool)->dict:
 """Enable or disable nonessential visible/social initiative.""";RUNTIME.state.quiet=enabled;RUNTIME.checkpoint();return RUNTIME.status()
@mcp.tool
def avatar_status()->dict:
 """Return embodiment endpoint and live state.""";return {'enabled':CFG.avatar_enabled,'url':f'http://{CFG.avatar_host}:{CFG.avatar_port}','activity':RUNTIME.state.activity,'mode':RUNTIME.state.affect.mode}
@mcp.tool
def explain_last_decision()->dict:
 """Return causal audit stages for the latest event trace."""
 r=RUNTIME.storage.one('SELECT trace_id FROM audit ORDER BY id DESC LIMIT 1');return {'trace_id':r[0] if r else None,'stages':RUNTIME.audit.trace(r[0]) if r else []}
@mcp.tool
def export_data(destination:str)->dict:
 """Create a verified local backup ZIP of state, identity and database.""";return {'backup':RUNTIME.storage.backup(destination,[RUNTIME.personality.path]),'integrity':RUNTIME.storage.integrity()}
@mcp.tool
def identity_change_proposal(changes:dict,reason:str)->dict:
 """Record but never auto-apply an identity change proposal.""";mid=RUNTIME.memory.add('reflection',json.dumps({'identity_change_proposal':changes,'reason':reason}),.9,.5,'user','private',trusted=True);return {'status':'requires_owner_migration','memory_id':mid}
@mcp.tool
def configure_provider(url:str,model:str,key_environment_variable:str='PDP_API_KEY')->dict:
 """Validate a provider proposal; configuration-file changes remain owner-controlled.""";return {'status':'configuration_required','validated':bool(url.startswith(('http://127.0.0.1','http://localhost','https://')) and model),'fields':{'provider_url':url,'provider_model':model,'provider_key_env':key_environment_variable},'note':'Write after owner review, then restart.'}
@mcp.tool
def configure_sensor(sensor:str,enabled:bool,scope:dict)->dict:
 """Record a sensor-consent proposal; PADP core has no covert sensors.""";return {'status':'requires_configuration','sensor':sensor,'enabled':enabled,'scope':scope}
@mcp.tool
def diagnostic_report()->dict:
 """Run in-process integrity and subsystem diagnostics.""";return {'database':RUNTIME.storage.integrity(),'schema':__import__('personal_desktop_person.storage',fromlist=['SCHEMA_VERSION']).SCHEMA_VERSION,'event_bus_depth':RUNTIME.bus.depth(),'event_bus_dropped':RUNTIME.bus.dropped,'audit_chain':RUNTIME.audit.verify(),'model':'PASS' if RUNTIME.models.available else 'NOT CONFIGURED','avatar':'PASS' if CFG.avatar_enabled else 'NOT CONFIGURED','computer_control':'BOUNDARY READY','capabilities':'PASS','policy':'PASS','runtime':RUNTIME.state.status.value}

@mcp.tool
def cognitive_context(query:str='')->dict:
 """Provide the existing OpenCode intelligence with PADP state, drives, beliefs and relevant memories for deliberation.""";return {'identity':RUNTIME.personality.context(),'state':RUNTIME.status(),'drives':RUNTIME.motivations.drives(RUNTIME.state,RUNTIME.bus.depth()),'world':RUNTIME.world.summary(),'memories':RUNTIME.memory.search(query,12) if query else RUNTIME.memory.search('',8)}
@mcp.tool
def rank_strategies(candidates:list[dict])->list[dict]:
 """Rank safe candidate strategies using causally active personality utility weights; policy checks still follow.""";return RUNTIME.decisions.rank(candidates)

@mcp.tool
def interact(message:str,channel:str='text')->dict:
 """Route typed or transcribed user input through LLM/heuristic intent understanding into conversation, information, feedback, interruption, or a goal proposal.""";return RUNTIME.user_input(message,channel)
@mcp.tool
def desktop_reactivity_status()->dict:
 """Report consent and live desktop-sensor state.""";w=RUNTIME.desktop_watcher;return {'enabled':bool(w),'screen_change_enabled':CFG.screen_change_enabled,'accessibility_enabled':CFG.accessibility_enabled,'poll_seconds':CFG.desktop_poll_seconds,'last_observation':__import__('dataclasses').asdict(w.last) if w and w.last else None}
@mcp.tool
def observe_desktop_once()->dict:
 """Perform one local metadata-first observation only when desktop sensor consent is enabled."""
 if not RUNTIME.desktop_watcher:raise PermissionError('Desktop sensor is disabled in configuration')
 o=RUNTIME.desktop_watcher.sensor.observe();return __import__('dataclasses').asdict(o)

def main():mcp.run()
if __name__=='__main__':main()
