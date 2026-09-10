from __future__ import annotations
import time,concurrent.futures
from .types import NodeResult
class Pipeline:
 def __init__(self,registry,store,max_nodes=64):self.r=registry;self.s=store;self.max=max_nodes
 def validate(self,g):
  nodes=g.get('nodes',[])
  if not nodes or len(nodes)>self.max:raise ValueError('Pipeline requires 1..%d nodes'%self.max)
  ids=[n['id'] for n in nodes]
  if len(ids)!=len(set(ids)):raise ValueError('Duplicate node id')
  deps={n['id']:set(n.get('depends_on',[])) for n in nodes}
  if any(not d<=set(ids) for d in deps.values()):raise ValueError('Unknown dependency')
  done=set()
  while len(done)<len(ids):
   ready=[i for i,d in deps.items() if i not in done and d<=done]
   if not ready:raise ValueError('Pipeline cycle detected')
   done.update(ready)
  return nodes
 def execute(self,g):
  nodes=self.validate(g);outputs={};results=[];pending={n['id']:n for n in nodes};deadline=time.time()+min(float(g.get('timeout',120)),600)
  while pending:
   progressed=False
   for nid,n in list(pending.items()):
    if all(x in outputs for x in n.get('depends_on',[])):
     if time.time()>deadline:raise TimeoutError('Pipeline timeout')
     ins=list(n.get('inputs',[]))
     for d in n.get('depends_on',[]):ins.extend(outputs[d])
     t=time.perf_counter()
     try:
      a=self.r.resolve(n['operation'],n.get('adapter'));arts,data=a.run(n['operation'],ins,n.get('params',{}),self.s);outputs[nid]=[x.id for x in arts];results.append(NodeResult(nid,'success',[x.__dict__ for x in arts],data,(time.perf_counter()-t)*1000).__dict__)
     except Exception as e:
      results.append(NodeResult(nid,'failed',duration_ms=(time.perf_counter()-t)*1000,error=str(e)).__dict__)
      if n.get('on_error','stop')=='stop':return {'status':'failed','results':results,'outputs':outputs}
      outputs[nid]=[]
     del pending[nid];progressed=True
   if not progressed:raise RuntimeError('No runnable nodes')
  return {'status':'success','results':results,'outputs':outputs}
