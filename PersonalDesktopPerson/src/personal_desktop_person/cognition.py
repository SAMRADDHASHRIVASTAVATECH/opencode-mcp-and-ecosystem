from __future__ import annotations
import time,math,re
from .models import Affect,Goal
class AppraisalEngine:
 def __init__(self,traits):self.t=traits
 def event(self,a:Affect,text:str,kind='environment'):
  s=text.lower();challenge=any(x in s for x in ['boss','beat','challenge','competition','win']);failure=any(x in s for x in ['failed','error','lost','could not']);success=any(x in s for x in ['success','completed','won','finished']);novel=any(x in s for x in ['new','interesting','investigate','discover'])
  a.arousal=min(1,a.arousal+.18*challenge+.08*novel);a.curiosity=min(1,a.curiosity+.2*novel);a.frustration=min(1,a.frustration+.22*failure-.18*success);a.confidence=max(0,min(1,a.confidence+.12*success-.1*failure));a.valence=max(0,min(1,a.valence+.15*success-.12*failure));a.urgency=min(1,a.urgency+.15*challenge);a.causes=([text[:100]]+a.causes)[:5];a.updated_at=time.time();self.mode(a);return a
 def decay(self,a,dt):
  bases={'valence':.55,'arousal':.22,'confidence':.55,'load':.08,'fatigue':.05,'frustration':0.,'curiosity':self.t.get('curiosity',.6),'social':.5,'control':.6,'urgency':0.,'risk':0.}
  rate=min(.08,dt/300)
  for k,b in bases.items():setattr(a,k,getattr(a,k)+(b-getattr(a,k))*rate)
  a.updated_at=time.time();self.mode(a)
 def mode(self,a):
  old=a.mode
  if a.risk>.65:a.mode='CAUTIOUS'
  elif a.frustration>.58:a.mode='FRUSTRATED'
  elif a.fatigue>.7:a.mode='TIRED'
  elif a.urgency>.58 and a.confidence>.5:a.mode='LOCKED-IN'
  elif a.load>.5 or a.urgency>.3:a.mode='FOCUSED'
  elif a.curiosity>.72:a.mode='CURIOUS'
  elif a.valence>.68 and a.arousal>.35:a.mode='PLAYFUL'
  else:a.mode='CALM'
  return old!=a.mode
class IntentionEngine:
 def choose(self,state):
  if state.status.value!='running':return 'remain safely idle'
  if state.pending_approvals:return 'wait for user approval'
  if state.active_goal and state.active_goal.status in ('approved','active'):return f'advance goal: {state.active_goal.text}'
  return 'observe quietly and remain available'
