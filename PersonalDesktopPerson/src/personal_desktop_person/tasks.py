from __future__ import annotations
import uuid,time,json
class TaskRuntime:
 TERMINAL={'completed','failed','cancelled','blocked'}
 def __init__(self,db,skills,governor,audit):self.db=db;self.skills=skills;self.gov=governor;self.audit=audit
 def propose(self,goal_id,steps,success,failure='',budget=900):
  tid=str(uuid.uuid4());data={'id':tid,'goal_id':goal_id,'steps':steps,'cursor':0,'success':success,'failure':failure,'budget':budget,'started':None,'failures':{},'last_result':None};self.db.execute('INSERT INTO tasks VALUES(?,?,?,?,?)',(tid,goal_id,json.dumps(data),'proposed',time.time()));return data|{'status':'proposed'}
 def update(self,tid,status=None,**changes):
  r=self.db.one('SELECT * FROM tasks WHERE id=?',(tid,));
  if not r:raise KeyError(tid)
  d=json.loads(r['data']);d.update(changes);st=status or r['status'];self.db.execute('UPDATE tasks SET data=?,status=?,updated=? WHERE id=?',(json.dumps(d),st,time.time(),tid));return d|{'status':st}
 def start(self,tid):return self.update(tid,'active',started=time.time())
 def result(self,tid,success,evidence):
  r=self.get(tid);d=r.copy();d['last_result']=evidence
  if success:d['cursor']+=1;st='completed' if d['cursor']>=len(d['steps']) else 'active'
  else:
   key=str(d['cursor']);d['failures'][key]=d['failures'].get(key,0)+1;st='blocked' if d['failures'][key]>=2 else 'active';d['strategy_change_required']=True
  return self.update(tid,st,**{k:v for k,v in d.items() if k!='status'})
 def get(self,tid):
  r=self.db.one('SELECT * FROM tasks WHERE id=?',(tid,));return (json.loads(r['data'])|{'status':r['status']}) if r else None
 def list(self):return [json.loads(r['data'])|{'status':r['status']} for r in self.db.query('SELECT * FROM tasks ORDER BY updated DESC')]
