from __future__ import annotations
import json,time
class ReflectionEngine:
 def __init__(self,memory,models):self.memory=memory;self.models=models
 def reflect(self,reason,limit=20):
  src=self.memory.search('',limit,['experience','episodic','user_feedback']);ids=[x['id'] for x in src]
  if not src:return {'status':'skipped','reason':'no source experiences'}
  if self.models.available:
   prompt='Source experiences: '+json.dumps(src)+'\nProduce JSON with lesson,hypothesis,strategy,confidence. Do not invent facts; cite source IDs.'
   text=self.models.chat('You are a bounded reflection module. Output only grounded conclusions.',prompt);content=text
  else:
   failures=[x for x in src if any(w in x['content'].lower() for w in ['failed','error'])];content=json.dumps({'lesson':'Review verified failures before repeating a strategy.' if failures else 'Retain successful verified procedures.','hypothesis':'No model configured; deterministic consolidation only.','strategy':'change_strategy' if failures else 'reuse_verified','confidence':.6,'source_ids':ids})
  mid=self.memory.add('reflection',content,.75,.6,'reflection','private',trusted=False);return {'status':'created','memory_id':mid,'source_ids':ids,'content':content}
