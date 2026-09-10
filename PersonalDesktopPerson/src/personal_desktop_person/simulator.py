from __future__ import annotations
import tempfile,time,json,random
from .config import Config
from .runtime import PersonRuntime
class Simulator:
 def __init__(self,data_dir=None,traits=None):
  self.dir=data_dir or tempfile.mkdtemp();self.r=PersonRuntime(Config(data_dir=self.dir,cognitive_hz=50,avatar_enabled=False))
  if traits:self.r.personality.data['traits'].update(traits);self.r.appraisal.t=self.r.personality.data['traits']
  self.r.start()
 def scenario(self,events,goal=None):
  if goal:self.r.set_goal(goal.get('text','task'),goal.get('success','done'),goal.get('priority',50));self.r.approve_goal()
  trace=[]
  for e in events:
   self.r.event(e['description'],e.get('kind','environment'),e.get('importance',.6));time.sleep(.02);trace.append({'event':e,'affect':self.r.status()['affect'],'intention':self.r.state.intention})
  return trace
 def action_outcome(self,summary,success):self.r.record_experience(summary,'success' if success else 'failed',1,.8);time.sleep(.03);return self.r.status()
 def close(self):self.r.stop(False);self.r.memory.close()
def demo():
 s=Simulator();t=s.scenario([{'description':'A difficult boss challenge appeared','kind':'environment','importance':.9}],{'text':'Beat boss','success':'victory'});before=s.action_outcome('attack strategy failed',False);after=s.action_outcome('alternate defensive strategy succeeded',True);print(json.dumps({'trace':t,'failure':before['affect'],'success':after['affect'],'memories':s.r.memory.search('strategy',10)},indent=2));s.close()
if __name__=='__main__':demo()
