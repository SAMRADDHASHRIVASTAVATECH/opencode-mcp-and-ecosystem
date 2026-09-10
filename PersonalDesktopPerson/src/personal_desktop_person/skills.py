from __future__ import annotations
import json,hashlib,time,uuid
class SkillRegistry:
 def __init__(self,db,learner):self.db=db;self.learner=learner
 def install_plan(self,manifest):
  req={'name','preconditions','capabilities','parameters','steps','expected_observations','timeout','verification','recovery','version'};missing=req-set(manifest)
  if missing:raise ValueError('Missing skill fields: '+','.join(sorted(missing)))
  raw=json.dumps(manifest,sort_keys=True);sid=manifest.get('id',str(uuid.uuid4()));sig=hashlib.sha256(raw.encode()).hexdigest();self.db.execute('INSERT INTO skills(id,name,version,manifest,status,signature) VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET manifest=excluded.manifest,status=excluded.status,signature=excluded.signature',(sid,manifest['name'],manifest['version'],raw,'proposed',sig));return {'id':sid,'status':'proposed','signature':sig}
 def approve(self,sid,regression_passed):
  if not regression_passed:raise ValueError('Skill regression tests must pass')
  self.db.execute('UPDATE skills SET status="active" WHERE id=? AND status="proposed"',(sid,));return self.get(sid)
 def get(self,sid):
  r=self.db.one('SELECT * FROM skills WHERE id=?',(sid,));return dict(r) if r else None
 def list(self,active_only=False):return [dict(r) for r in self.db.query('SELECT * FROM skills'+(' WHERE status="active"' if active_only else '')+' ORDER BY name')]
 def record(self,sid,success,reward):self.db.execute('UPDATE skills SET successes=successes+?,failures=failures+?,reward=reward+? WHERE id=?',(int(success),int(not success),max(-1,min(1,reward)),sid));self.learner.feedback(sid,'success' if success else 'failure',1 if success else -1)
