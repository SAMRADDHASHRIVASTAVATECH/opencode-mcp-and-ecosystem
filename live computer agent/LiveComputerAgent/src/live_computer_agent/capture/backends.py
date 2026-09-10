from __future__ import annotations
import time,uuid,hashlib,sys
import numpy as np
from ..models import Frame
class MSSCapture:
 def __init__(self):
  import mss; self.sct=mss.mss();self.last=None
 def grab(self,target='desktop',monitor=0,window=None):
  mons=self.sct.monitors; idx=monitor+1 if monitor+1<len(mons) else 1; box=mons[idx] if target!='all' else mons[0]
  a=np.asarray(self.sct.grab(box))[:,:,:3].copy(); return _frame(a,target,self)
 def close(self):self.sct.close()
class DXCamCapture:
 def __init__(self,monitor=0):
  import dxcam;self.cam=dxcam.create(output_idx=monitor,output_color='BGR');self.last=None
 def grab(self,target='desktop',monitor=0,window=None):
  a=self.cam.grab()
  if a is None: a=self.last.copy() if self.last is not None else np.zeros((1,1,3),np.uint8)
  return _frame(a,target,self)
 def close(self):self.cam.release()
class SyntheticCapture:
 def __init__(self,width=800,height=600):self.a=np.zeros((height,width,3),np.uint8);self.last=None;self.counter=0
 def grab(self,target='desktop',monitor=0,window=None):self.counter+=1;return _frame(self.a.copy(),target,self)
 def close(self):pass
def _frame(a,target,obj):
 old=obj.last; ratio=1. if old is None or old.shape!=a.shape else float(np.mean(np.any(abs(a.astype(np.int16)-old.astype(np.int16))>8,axis=2)))
 obj.last=a.copy();h,w=a.shape[:2];return Frame(str(uuid.uuid4()),time.time(),a,w,h,ratio>0.002,ratio,target)
def create_capture(name='auto',monitor=0):
 if name=='synthetic':return SyntheticCapture()
 if sys.platform=='win32' and name in ('auto','dxcam'):
  try:return DXCamCapture(monitor)
  except Exception:
   if name=='dxcam':raise
 if name in ('auto','mss'):
  try:return MSSCapture()
  except Exception:
   if name=='mss':raise
 return SyntheticCapture()
