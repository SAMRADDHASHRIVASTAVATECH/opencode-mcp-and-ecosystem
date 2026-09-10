from __future__ import annotations
import sys,time
class Win32Input:
 def __init__(self):
  if sys.platform!='win32':raise RuntimeError('Win32 input requires Windows')
  import pyautogui;self.p=pyautogui;self.held=set();pyautogui.FAILSAFE=True;pyautogui.PAUSE=0.02
 def move(self,x,y,duration=0):self.p.moveTo(x,y,duration=max(0,duration))
 def click(self,x,y,button='left',count=1):self.p.click(x,y,clicks=count,button=button)
 def drag(self,x1,y1,x2,y2,duration=.3,button='left'):self.move(x1,y1);self.p.dragTo(x2,y2,duration=max(.05,duration),button=button)
 def scroll(self,amount,x=None,y=None):
  if x is not None:self.move(x,y or 0)
  self.p.scroll(amount)
 def key_down(self,key):self.p.keyDown(key);self.held.add(key)
 def key_up(self,key):self.p.keyUp(key);self.held.discard(key)
 def type_text(self,text,interval=0):self.p.write(text,interval=interval)
 def release_all(self):
  for k in list(self.held):
   try:self.p.keyUp(k)
   finally:self.held.discard(k)
class RecordingInput:
 def __init__(self):self.events=[];self.held=set()
 def move(self,x,y,duration=0):self.events.append(('move',x,y,duration))
 def click(self,x,y,button='left',count=1):self.events.append(('click',x,y,button,count))
 def drag(self,x1,y1,x2,y2,duration=.3,button='left'):self.events.append(('drag',x1,y1,x2,y2,duration,button))
 def scroll(self,amount,x=None,y=None):self.events.append(('scroll',amount,x,y))
 def key_down(self,key):self.held.add(key);self.events.append(('down',key))
 def key_up(self,key):self.held.discard(key);self.events.append(('up',key))
 def type_text(self,text,interval=0):self.events.append(('type',text,interval))
 def release_all(self):
  for k in list(self.held):self.key_up(k)
def create_input():return Win32Input() if sys.platform=='win32' else RecordingInput()
