from __future__ import annotations
from collections import deque
class Attention:
 def __init__(self):self.foreground=None;self.peripheral=deque(maxlen=100);self.interruptions=deque(maxlen=100)
 def score(self,event,goal=''):
  p=event.payload;text=str(p).lower();sal=event.priority/100;rel=.35 if goal and any(w in text for w in goal.lower().split() if len(w)>3) else 0;nov=.15 if p.get('novel') else 0;risk=.3*float(p.get('risk',0));social=.3 if event.kind in ('user','user_feedback','stop') else 0;cost=.15*float(p.get('cost',0));return max(0,min(1,sal+rel+nov+risk+social-cost))
 def route(self,event,goal=''):
  s=self.score(event,goal)
  if event.kind=='stop' or s>=.8:self.interruptions.append(event);self.foreground=event;return 'interrupt'
  if s>=.45:self.foreground=event;return 'foreground'
  self.peripheral.append(event);return 'peripheral'
