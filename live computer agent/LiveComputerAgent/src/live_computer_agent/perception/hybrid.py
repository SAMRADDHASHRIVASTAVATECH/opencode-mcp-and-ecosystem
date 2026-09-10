from __future__ import annotations
import sys,time
from ..models import Element,Bounds
class UIAProvider:
 def __init__(self,max_elements=500):self.max=max_elements
 def scan(self,window):
  if sys.platform!='win32':return []
  try:
   from pywinauto import Desktop
   root=Desktop(backend='uia').window(handle=window.hwnd);out=[]
   for i,c in enumerate(root.descendants()[:self.max]):
    try:
     r=c.rectangle(); info=c.element_info; role=getattr(info,'control_type','unknown') or 'unknown';name=getattr(info,'name','') or ''
     out.append(Element(f'uia:{window.hwnd}:{i}',role.lower(),name,Bounds(r.left,r.top,r.width(),r.height()),1.,'uia',c.is_enabled(),{'automation_id':getattr(info,'automation_id','')}))
    except Exception:continue
   return out
  except Exception:return []
class OCRProvider:
 def __init__(self,enabled=True):self.enabled=enabled
 def scan(self,frame):
  if not self.enabled:return []
  try:
   import pytesseract
   from pytesseract import Output
   d=pytesseract.image_to_data(frame.image,output_type=Output.DICT);out=[]
   for i,text in enumerate(d['text']):
    text=text.strip();conf=float(d['conf'][i]) if str(d['conf'][i]).replace('.','',1).lstrip('-').isdigit() else -1
    if text and conf>=30:out.append({'text':text,'bounds':[d['left'][i],d['top'][i],d['width'][i],d['height'][i]],'confidence':conf/100,'source':'ocr'})
   return out
  except Exception:return []
class HybridPerception:
 def __init__(self,uia=True,ocr=True):self.uia=UIAProvider() if uia else None;self.ocr=OCRProvider(ocr)
 def analyze(self,frame,window):
  els=self.uia.scan(window) if self.uia else []; text=self.ocr.scan(frame)
  known={(e.name.lower(),e.bounds.x,e.bounds.y) for e in els if e.name}
  for i,t in enumerate(text):
   x,y,w,h=t['bounds'];key=(t['text'].lower(),x,y)
   if key not in known:els.append(Element(f'ocr:{frame.id}:{i}','text',t['text'],Bounds(x,y,w,h),t['confidence'],'ocr'))
  return els,text,[]
