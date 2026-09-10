from __future__ import annotations
import math,time,json
class StrategyLearner:
 """Bounded contextual bandit: Beta success estimates; no identity/policy mutation."""
 def __init__(self,db):self.db=db
 def feedback(self,target,label,value,context=''):
  v=max(-1,min(1,float(value)));self.db.execute('INSERT INTO feedback(time,target,label,value,context) VALUES(?,?,?,?,?)',(time.time(),target,label,v,context));return {'target':target,'label':label,'value':v}
 def strategy_score(self,skill_id,prior=.5):
  rows=self.db.query('SELECT value FROM feedback WHERE target=?',(skill_id,));wins=sum(1 for r in rows if r[0]>0);loss=sum(1 for r in rows if r[0]<0);return (1+wins)/(2+wins+loss)
 def classify(self,text):
  t=text.lower();labels={'correct':1,'successful':1,'better':.5,'incorrect':-1,'failed':-1,'worse':-.5,'unsafe':-1,'too aggressive':-.8,'too slow':-.4}
  found=[(k,v) for k,v in labels.items() if k in t];return max(found,key=lambda x:abs(x[1])) if found else ('neutral',0)
