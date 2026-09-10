from __future__ import annotations
import sqlite3,json,uuid,time
class ArtworkStore:
 def __init__(self,path):
  self.db=sqlite3.connect(path);self.db.row_factory=sqlite3.Row;self.db.executescript('''CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,name TEXT,brief TEXT,state TEXT,created REAL,updated REAL); CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT,project_id TEXT,type TEXT,payload TEXT,created REAL);''')
 def create(self,name,brief,canvas=None):
  i=str(uuid.uuid4());t=time.time();s={'schema':'artist.artwork/1','canvas':canvas or {'width':1920,'height':1080,'unit':'px','color_space':'sRGB','background':'#ffffff'},'objects':[],'layers':[{'id':'layer-1','name':'Artwork','visible':True,'locked':False}],'constraints':[],'references':[],'history':[]};self.db.execute('INSERT INTO projects VALUES(?,?,?,?,?,?)',(i,name,brief,json.dumps(s),t,t));self.db.commit();self.event(i,'created',{'name':name});return self.get(i)
 def get(self,i):
  r=self.db.execute('SELECT * FROM projects WHERE id=?',(i,)).fetchone()
  if not r:raise KeyError(i)
  d=dict(r);d['state']=json.loads(d['state']);return d
 def update(self,i,patch,expected_updated=None):
  p=self.get(i)
  if expected_updated and p['updated']!=expected_updated:raise RuntimeError('Artwork state changed; reload before editing')
  s=p['state']
  for k,v in patch.items():
   if k in {'schema'}:raise ValueError('Immutable field')
   s[k]=v
  t=time.time();self.db.execute('UPDATE projects SET state=?,updated=? WHERE id=?',(json.dumps(s),t,i));self.db.commit();self.event(i,'updated',{'keys':list(patch)});return self.get(i)
 def event(self,i,typ,payload):self.db.execute('INSERT INTO events(project_id,type,payload,created) VALUES(?,?,?,?)',(i,typ,json.dumps(payload),time.time()));self.db.commit()
 def events(self,i,limit=100):return [dict(x) for x in self.db.execute('SELECT * FROM events WHERE project_id=? ORDER BY id DESC LIMIT ?',(i,limit))]
