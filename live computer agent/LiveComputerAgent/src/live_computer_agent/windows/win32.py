from __future__ import annotations
import sys,subprocess
from ..models import WindowInfo,Bounds
class Win32Windows:
 def __init__(self):
  if sys.platform!='win32':raise RuntimeError('Win32 provider requires Windows')
  import win32gui,win32process,win32api;self.g=win32gui;self.p=win32process;self.a=win32api
 def _info(self,h):
  g=self.g;title=g.GetWindowText(h);l,t,r,b=g.GetWindowRect(h);_,pid=self.p.GetWindowThreadProcessId(h)
  try:
   import psutil;app=psutil.Process(pid).name()
  except Exception:app=''
  return WindowInfo(h,title,app,pid,Bounds(l,t,max(0,r-l),max(0,b-t)),h==g.GetForegroundWindow(),0)
 def active(self):
  h=self.g.GetForegroundWindow();return self._info(h) if h else WindowInfo()
 def list(self):
  out=[]
  def cb(h,_):
   if self.g.IsWindowVisible(h) and self.g.GetWindowText(h):
    try:out.append(self._info(h))
    except Exception:pass
  self.g.EnumWindows(cb,None);return out
 def focus(self,hwnd):
  try:self.g.ShowWindow(hwnd,9);self.g.SetForegroundWindow(hwnd);return self.g.GetForegroundWindow()==hwnd
  except Exception:return False
class SyntheticWindows:
 def __init__(self):self.win=WindowInfo(1,'Synthetic Test Window','synthetic.exe',1,Bounds(0,0,800,600),True,0)
 def active(self):return self.win
 def list(self):return [self.win]
 def focus(self,hwnd):self.win.focused=hwnd==1;return self.win.focused
def create_windows():return Win32Windows() if sys.platform=='win32' else SyntheticWindows()
