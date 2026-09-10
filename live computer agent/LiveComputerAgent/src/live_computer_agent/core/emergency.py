from __future__ import annotations
import sys,threading
class EmergencyHotkey:
 def __init__(self,callback):self.callback=callback;self.thread=None;self.ready=threading.Event()
 def start(self):
  if sys.platform!='win32':return False
  self.thread=threading.Thread(target=self._run,daemon=True,name='lca-emergency-hotkey');self.thread.start();self.ready.wait(1);return self.ready.is_set()
 def _run(self):
  import ctypes
  u=ctypes.windll.user32;MOD_ALT=1;MOD_CONTROL=2;VK_PAUSE=0x13;WM_HOTKEY=0x0312
  if not u.RegisterHotKey(None,1,MOD_ALT|MOD_CONTROL,VK_PAUSE):return
  self.ready.set();msg=ctypes.wintypes.MSG()
  try:
   while u.GetMessageW(ctypes.byref(msg),None,0,0)>0:
    if msg.message==WM_HOTKEY:self.callback()
  finally:u.UnregisterHotKey(None,1)
