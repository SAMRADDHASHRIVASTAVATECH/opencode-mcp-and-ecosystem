from __future__ import annotations
import json,re
class InteractionRouter:
 def __init__(self,models,name):self.models=models;self.name=name.lower()
 def classify(self,text,current_goal=None):
  t=text.strip();lo=t.lower();kind='conversation';confidence=.65
  if any(x in lo for x in ['stop','pause','wait']) and len(lo.split())<8:kind='interrupt';confidence=.9
  elif any(x in lo for x in ['wrong','incorrect','do it this way','too slow','unsafe','good job','well done']):kind='feedback';confidence=.82
  elif lo.startswith(('remember ','important:','my preference')):kind='information';confidence=.8
  elif any(lo.startswith(x) for x in ['open ','find ','make ','play ','work on ','do ','upload ','close ','run ']):kind='task';confidence=.75
  elif self.name and self.name in lo:kind='direct_address';confidence=.8
  if self.models.available:
   raw=self.models.chat('Classify user intent. Output strict JSON only. Categories: conversation,information,goal_change,interrupt,task,feedback,direct_address.',json.dumps({'text':t,'current_goal':current_goal}))
   try:
    j=json.loads(raw.strip().strip('`').removeprefix('json').strip());kind=j.get('kind',kind);confidence=float(j.get('confidence',confidence))
   except Exception:pass
  return {'kind':kind,'confidence':max(0,min(1,confidence)),'text':t}
