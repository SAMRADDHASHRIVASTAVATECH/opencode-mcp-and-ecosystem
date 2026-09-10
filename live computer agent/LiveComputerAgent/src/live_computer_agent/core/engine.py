from __future__ import annotations
import threading,time,uuid,subprocess,shlex,base64,io,os
from copy import deepcopy
from ..config import Config
from ..models import *
from ..capture.backends import create_capture
from ..windows.win32 import create_windows
from ..input.win32 import create_input
from ..perception.hybrid import HybridPerception
from ..verification.engine import Verifier
from ..memory.store import Memory
from ..planning.providers import NoPlanner,OpenAICompatiblePlanner
from .emergency import EmergencyHotkey
class LiveComputerAgent:
 def __init__(self,config=None,capture=None,windows=None,input_provider=None,perception=None,planner=None):
  self.cfg=config or Config();self.capture=capture or create_capture(self.cfg.capture_backend,self.cfg.monitor);self.windows=windows or create_windows();self.input=input_provider or create_input();self.perception=perception or HybridPerception(self.cfg.uia_enabled,self.cfg.ocr_provider!='none');self.planner=planner or NoPlanner();self.verifier=Verifier();self.memory=Memory(persistent=self.cfg.persistent_memory,path=os.path.join(self.cfg.runtime_dir,'memory.jsonl'));self.state=AgentState();self.lock=threading.RLock();self.stop_event=threading.Event();self.pause_event=threading.Event();self.threads=[];self.latest_frame=None;self._last_perception=0.;self._auto_thread=None;self.emergency=EmergencyHotkey(self.emergency_stop)
 def start(self,mode='direct',target=None):
  with self.lock:
   if self.state.status in (Status.RUNNING,Status.PAUSED):return serial(self.state)
   self.stop_event.clear();self.pause_event.clear();self.state=AgentState(str(uuid.uuid4()),Status.RUNNING,Mode(mode),started_at=time.time())
  self.threads=[threading.Thread(target=self._fast_loop,name='lca-capture',daemon=True)];[t.start() for t in self.threads];self.emergency.start();return serial(self.state)
 def _fast_loop(self):
  period=1/max(.1,self.cfg.capture_fps);medium=1/max(.1,self.cfg.perception_fps)
  while not self.stop_event.is_set():
   tic=time.perf_counter()
   if not self.pause_event.is_set():
    try:
     f=self.capture.grab(self.cfg.capture_target,self.cfg.monitor);w=self.windows.active();self.latest_frame=f
     els=text=objs=[]
     if time.monotonic()-self._last_perception>=medium or self.state.screen.revision==0:
      p=time.perf_counter();els,text,objs=self.perception.analyze(f,w);plat=(time.perf_counter()-p)*1000;self._last_perception=time.monotonic()
     else:
      els=self.state.screen.elements;text=self.state.screen.text;objs=self.state.screen.objects;plat=0
     with self.lock:
      rev=self.state.screen.revision+1;self.state.screen=ScreenState(rev,time.time(),f.id,w,els,text,objs,{},min(1.,max([e.confidence for e in els],default=.5)),['capture','active_window']+(['uia/ocr'] if plat else []),{'capture_ms':(time.perf_counter()-tic)*1000,'perception_ms':plat,'change_ratio':f.change_ratio})
    except Exception as e:self._error(f'capture_loop: {e}')
   self.stop_event.wait(max(0,period-(time.perf_counter()-tic)))
 def pause(self):
  self.pause_event.set();self.input.release_all();self.state.status=Status.PAUSED;self.state.paused_at=time.time();return serial(self.state)
 def resume(self):
  if not self.state.session_id:raise RuntimeError('No session')
  self.pause_event.clear();self.state.status=Status.RUNNING;return serial(self.state)
 def stop(self):
  self.stop_event.set();self.pause_event.clear();self.input.release_all();self.state.status=Status.STOPPED
  for t in self.threads:
   if t is not threading.current_thread():t.join(timeout=2)
  return serial(self.state)
 def emergency_stop(self):return self.stop()
 def close(self):self.stop();self.capture.close()
 def _error(self,msg):
  with self.lock:self.state.errors=(self.state.errors+[msg])[-50:]
 def snapshot(self):
  with self.lock:return deepcopy(self.state.screen)
 def _guard(self):
  if self.state.status!=Status.RUNNING:raise RuntimeError('Session must be running')
  w=self.windows.active();name=(w.application or '').lower()
  if any(x.lower() in name for x in self.cfg.denied_apps):raise PermissionError('Application denied by policy')
  if self.cfg.allowed_apps and not any(x.lower() in name for x in self.cfg.allowed_apps):raise PermissionError('Application not allowlisted')
  if self.cfg.require_focus and not w.focused:raise RuntimeError('Target window is not focused')
  return w
 def observe(self,force=False):
  if force:
   f=self.capture.grab(self.cfg.capture_target,self.cfg.monitor);w=self.windows.active();els,text,objs=self.perception.analyze(f,w)
   with self.lock:self.state.screen=ScreenState(self.state.screen.revision+1,time.time(),f.id,w,els,text,objs,{},.8,['forced_observation'],{'change_ratio':f.change_ratio})
  return serial(self.snapshot())
 def screen_png(self):
  if self.latest_frame is None:self.observe(True)
  from PIL import Image
  a=self.latest_frame.image
  if a.ndim==3 and a.shape[2]>=3:a=a[:,:,:3][:,:,::-1]
  b=io.BytesIO();Image.fromarray(a).save(b,'PNG');return base64.b64encode(b.getvalue()).decode()
 def find_element(self,query):
  q=query.lower();matches=[e for e in self.snapshot().elements if q==e.id.lower() or q in e.name.lower()]
  if not matches:raise LookupError(f'Element not found: {query}')
  matches.sort(key=lambda e:(q!=e.name.lower(),-e.confidence,e.bounds.width*e.bounds.height));return matches[0]
 def perform(self,action,verify=True,expect=None,**p):
  before=self.snapshot();r=ActionResult(action=action,before_revision=before.revision)
  try:
   self._guard()
   if action in ('click','double_click'):
    x,y=int(p['x']),int(p['y']);self._validate_point(x,y);self.input.click(x,y,p.get('button','left'),2 if action=='double_click' else 1)
   elif action=='move_mouse':x,y=int(p['x']),int(p['y']);self._validate_point(x,y);self.input.move(x,y,float(p.get('duration',0)))
   elif action=='drag':self._validate_point(int(p['x1']),int(p['y1']));self._validate_point(int(p['x2']),int(p['y2']));self.input.drag(int(p['x1']),int(p['y1']),int(p['x2']),int(p['y2']),float(p.get('duration',.3)),p.get('button','left'))
   elif action=='scroll':self.input.scroll(int(p['amount']),p.get('x'),p.get('y'))
   elif action=='press_key':self.input.key_down(p['key']);time.sleep(float(p.get('duration',.05)));self.input.key_up(p['key'])
   elif action=='release_key':self.input.key_up(p['key'])
   elif action=='hotkey':
    keys=p['keys'] if isinstance(p['keys'],list) else [x.strip() for x in p['keys'].split('+')];
    for k in keys:self.input.key_down(k)
    for k in reversed(keys):self.input.key_up(k)
   elif action=='type_text':self.input.type_text(p['text'],float(p.get('interval',0)))
   elif action=='click_element':
    e=self.find_element(p['element']);x,y=e.bounds.center;self._validate_point(x,y);self.input.click(x,y,p.get('button','left'),1);expect=expect or {'kind':'screen_changed'}
   elif action=='focus_window':
    if not self.windows.focus(int(p['hwnd'])):raise RuntimeError('Window focus failed')
   elif action=='open_application':
    if not self.cfg.allow_process_launch:raise PermissionError('Process launch disabled by configuration')
    args=[p['path']]+list(p.get('args',[]));subprocess.Popen(args,shell=False)
   elif action=='wait':time.sleep(min(float(p.get('seconds',1)),self.cfg.action_timeout))
   else:raise ValueError(f'Unknown action: {action}')
   if verify:
    time.sleep(self.cfg.verification_delay);after_obj=self.snapshot();ok,status,evidence=self.verifier.compare(before,after_obj,expect);r.after_revision=after_obj.revision;r.finish(status,'Post-action observation evaluated',ok,**evidence)
   else:r.after_revision=self.snapshot().revision;r.finish('success','Dispatched; verification disabled',False)
  except Exception as e:self.input.release_all();r.finish('failed',str(e),False)
  with self.lock:self.state.last_actions=(self.state.last_actions+[r])[-50:]
  self.memory.add(serial(r));return serial(r)
 def _validate_point(self,x,y):
  f=self.latest_frame
  if f and not (0<=x<f.width and 0<=y<f.height):raise ValueError(f'Point outside captured desktop: {x},{y} not in {f.width}x{f.height}')
 def set_goal(self,goal,mode='assisted'):self.state.goal=goal;self.state.mode=Mode(mode);return serial(self.state)
 def cancel_goal(self):self.state.goal=None;self.state.subgoal=None;return serial(self.state)
 def start_autonomous(self,goal,timeout=120):
  self.set_goal(goal,'autonomous')
  if self._auto_thread and self._auto_thread.is_alive():raise RuntimeError('Autonomous loop already running')
  self._auto_thread=threading.Thread(target=self._auto_loop,args=(timeout,),daemon=True,name='lca-reasoning');self._auto_thread.start();return {'started':True,'goal':goal}
 def _auto_loop(self,timeout):
  deadline=time.time()+timeout
  for _ in range(self.cfg.max_autonomous_steps):
   if self.stop_event.is_set() or not self.state.goal or time.time()>deadline:return
   if self.pause_event.wait(.01):time.sleep(.1);continue
   try:a=self.planner.next_action(self.state.goal,self.snapshot(),self.memory.recent())
   except Exception as e:self._error(f'planner: {e}');return
   kind=a.pop('action','stop')
   if kind in ('complete','stop'):self.memory.add({'planner':kind,'detail':a});self.state.goal=None;return
   self.perform(kind,True,**a)
 def agent_state(self):return serial(self.state)
