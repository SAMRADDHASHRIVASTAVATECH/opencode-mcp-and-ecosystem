from __future__ import annotations
import sys,time,threading,hashlib,subprocess,json,ctypes
from dataclasses import dataclass,asdict
@dataclass
class DesktopObservation:
 active_application:str='';window_title:str='';window_id:str='';bounds:tuple=(0,0,0,0);cursor:tuple=(0,0);screen_size:tuple=(0,0);frame_hash:str='';change_ratio:float=0.;uia_summary:list=None;timestamp:float=0.
 def __post_init__(self):self.uia_summary=self.uia_summary or [];self.timestamp=self.timestamp or time.time()
class DesktopSensor:
 """Consent-gated, metadata-first desktop sensor. Pixels stay local and are not retained."""
 def __init__(self,capture=False,uia=True):self.capture_enabled=capture;self.uia=uia;self.last=None;self.sct=None
 def _window(self):
  if sys.platform=='win32':
   u=ctypes.windll.user32;h=u.GetForegroundWindow();n=u.GetWindowTextLengthW(h);buf=ctypes.create_unicode_buffer(n+1);u.GetWindowTextW(h,buf,n+1);r=ctypes.wintypes.RECT();u.GetWindowRect(h,ctypes.byref(r));pid=ctypes.c_ulong();u.GetWindowThreadProcessId(h,ctypes.byref(pid));app=''
   try:
    import psutil;app=psutil.Process(pid.value).name()
   except Exception:pass
   pt=ctypes.wintypes.POINT();u.GetCursorPos(ctypes.byref(pt));return str(h),app,buf.value,(r.left,r.top,r.right-r.left,r.bottom-r.top),(pt.x,pt.y),(u.GetSystemMetrics(0),u.GetSystemMetrics(1))
  if sys.platform=='darwin':
   try:title=subprocess.check_output(['osascript','-e','tell application "System Events" to get name of first application process whose frontmost is true'],text=True,timeout=1).strip();return title,title,title,(0,0,0,0),(0,0),(0,0)
   except Exception:return '','','',(0,0,0,0),(0,0),(0,0)
  try:
   title=subprocess.check_output(['sh','-lc','xprop -root _NET_ACTIVE_WINDOW'],text=True,timeout=1).strip();return title,'',title,(0,0,0,0),(0,0),(0,0)
  except Exception:return '','','',(0,0,0,0),(0,0),(0,0)
 def observe(self):
  wid,app,title,bounds,cursor,size=self._window();fh='';ratio=0.
  if self.capture_enabled:
   try:
    import mss,numpy as np
    self.sct=self.sct or mss.mss();a=np.asarray(self.sct.grab(self.sct.monitors[0]))[:,:,:3];small=a[::32,::32];fh=hashlib.sha256(small.tobytes()).hexdigest()
    if self.last is not None and self.last.shape==small.shape:ratio=float(np.mean(np.any(abs(small.astype('int16')-self.last.astype('int16'))>12,axis=2)))
    self.last=small.copy()
   except Exception:pass
  ui=[]
  if self.uia and sys.platform=='win32' and wid:
   try:
    from pywinauto import Desktop
    for c in Desktop(backend='uia').window(handle=int(wid)).descendants()[:100]:
     i=c.element_info;name=getattr(i,'name','') or '';role=getattr(i,'control_type','') or ''
     if name:ui.append({'role':role,'name':name[:160]})
   except Exception:pass
  return DesktopObservation(app,title,wid,bounds,cursor,size,fh,ratio,ui)
class DesktopWatcher:
 def __init__(self,runtime,sensor,interval=1.,meaningful_change=.08):self.r=runtime;self.sensor=sensor;self.interval=max(.1,interval);self.threshold=meaningful_change;self.stop_event=threading.Event();self.thread=None;self.last=None
 def start(self):self.stop_event.clear();self.thread=threading.Thread(target=self._loop,daemon=True,name='pdp-desktop-environment');self.thread.start()
 def stop(self):self.stop_event.set()
 def _loop(self):
  while not self.stop_event.wait(self.interval):
   o=self.sensor.observe();old=self.last;self.last=o
   if old is None:self.r.emit('environment',{'description':f'Active application is {o.active_application}: {o.window_title}','desktop':asdict(o),'novel':True},45,'desktop_sensor',False,'sensitive');continue
   changes=[]
   if o.window_id!=old.window_id:changes.append(f'active window changed to {o.active_application}: {o.window_title}')
   if o.cursor!=old.cursor: self.r.world.update('desktop','cursor',o.cursor,.95,'os_cursor',2,'sensitive')
   if o.change_ratio>=self.threshold:changes.append(f'relevant screen regions changed ({o.change_ratio:.2f})')
   if changes:self.r.emit('environment',{'description':'; '.join(changes),'desktop':asdict(o),'novel':o.window_id!=old.window_id,'cost':.1},55,'desktop_sensor',False,'sensitive')
