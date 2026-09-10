from __future__ import annotations
import time
from .models import Approval,Risk
RANK={Risk.R0.value:0,Risk.R1.value:1,Risk.R2.value:2,Risk.R3.value:3,Risk.R4.value:4}
class Governor:
 def assess(self,action):
  s=(action.get('summary','')+' '+action.get('type','')).lower()
  if any(x in s for x in ['purchase','payment','password','security setting','delete account']):return Risk.R4.value
  if any(x in s for x in ['send','upload','publish','install','overwrite','delete','commit','push']):return Risk.R3.value
  if any(x in s for x in ['click','type','edit','launch','play','control']):return Risk.R2.value
  if any(x in s for x in ['read','observe','search','inspect']):return Risk.R1.value
  return Risk.R0.value
 def request(self,action):
  risk=self.assess(action);return Approval(summary=action.get('summary',action.get('type','action')),risk=risk,scope=action,expires_at=time.time()+600)
 def permits_automatic(self,risk):return RANK[risk]==0
