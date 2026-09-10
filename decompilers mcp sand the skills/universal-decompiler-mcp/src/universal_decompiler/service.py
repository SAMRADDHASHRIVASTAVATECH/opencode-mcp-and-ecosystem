from __future__ import annotations
import json,time,uuid,threading,traceback
from concurrent.futures import ThreadPoolExecutor
from .core.router import Router
from .core.approval import Approval
from .core.paths import ANALYSIS_ROOT
class Service:
 def __init__(self):self.router=Router();self.approval=Approval();self.pool=ThreadPoolExecutor(max_workers=2,thread_name_prefix='decompiler');self.jobs={};self.cancel={}
 def plan_analysis(self,request):
  route=self.router.route(request['target'],request.get('depth','normal'));impact='Static analysis only; never executes target. Writes artifacts and may expose embedded strings/source in analysis output.';return self.approval.create('analyze',request|{'route_snapshot':route},impact)
 def plan_install(self,tool_id):return self.approval.create('install',self.router.registry.plan_install(tool_id),'Downloads and executes installer/package code into managed tool cache; review source, version, argv, network and trust.')
 def execute(self,pid,token):
  p=self.approval.consume(pid,token);jid=uuid.uuid4().hex;self.jobs[jid]={'id':jid,'action':p['action'],'status':'running','started_at':time.time()};f=self.pool.submit(self._run,jid,p);self.jobs[jid]['future']=f;return self.status(jid)
 def _run(self,jid,p):
  j=self.jobs[jid]
  try:
   if p['action']=='analyze':
    x=dict(p['payload']);x.pop('route_snapshot',None);x.pop('analysis_mode',None);j['result']=self.router.analyze(x.pop('target'),**x)
   else:j['result']=self.router.registry.execute_install(p['payload'])
   j['status']='completed';j['verified']=True
  except Exception as e:j.update(status='failed',error=type(e).__name__+': '+str(e),traceback=traceback.format_exc(limit=8),verified=False)
  finally:j['completed_at']=time.time()
 def status(self,i):
  x=self.jobs.get(i)
  if not x:raise KeyError('job not found')
  return {k:v for k,v in x.items() if k not in ('future','traceback')}
