from __future__ import annotations
import hashlib,json,secrets,time,threading,uuid,traceback
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,Future
from PIL import Image
import PIL
import cv2,numpy as np
from .paths import safe_path,ROOT
from .images import load
from .edges import detect,contours,stats
from .export import render
from ..models import EdgeSettings,VectorSettings,ExportSettings
class Approval:
 def __init__(self):self.plans={};self.tokens={};self.lock=threading.Lock()
 def plan(self,action,payload,impact):
  x={'action':action,'payload':payload,'impact':impact,'created_at':time.time()};pid=hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest();self.plans[pid]=x;return {'approval_required':True,'plan_id':pid,**x}
 def approve(self,pid,text):
  if text.strip().lower() not in {'approve','approved','yes'}:raise ValueError('explicit approval required')
  if pid not in self.plans:raise KeyError('plan not found')
  t=secrets.token_urlsafe(32);self.tokens[t]=(pid,time.time()+60);return {'token':t,'plan_id':pid,'expires_at':time.time()+60}
 def consume(self,pid,t):
  v=self.tokens.pop(t,None)
  if not v or v[0]!=pid or v[1]<time.time():raise PermissionError('approval invalid, expired, used, or mismatched')
  return self.plans.pop(pid)
class Service:
 def __init__(self):self.approval=Approval();self.pool=ThreadPoolExecutor(max_workers=2,thread_name_prefix='hybrid-eps');self.render_lock=threading.Lock();self.jobs={};self.cancel={};self.log=ROOT/'.hybrid-eps/logs.jsonl';self.presets=self._load_presets()
 def _load_presets(self):
  p=ROOT/'.hybrid-eps/presets.json'
  try:return json.loads(p.read_text())
  except:return {'default':{'edge':EdgeSettings().model_dump(),'vector':VectorSettings().model_dump(),'export':ExportSettings().model_dump()},'sharp':{'edge':EdgeSettings(canny_low=50,canny_high=150,blur_kernel=1).model_dump(),'vector':VectorSettings(simplify_epsilon=.001).model_dump(),'export':ExportSettings(edge_width=.5).model_dump()},'soft':{'edge':EdgeSettings(canny_low=150,canny_high=250,blur_kernel=7).model_dump(),'vector':VectorSettings(simplify_epsilon=.004,min_area=5).model_dump(),'export':ExportSettings(edge_width=.2).model_dump()},'artistic':{'edge':EdgeSettings(canny_low=80,canny_high=180,blur_kernel=5).model_dump(),'vector':VectorSettings().model_dump(),'export':ExportSettings(edge_color='#FF00FF',edge_width=1).model_dump()}}
 def capabilities(self):return {'root':str(ROOT),'edge_methods':['canny','sobel','laplacian','scharr'],'morphology':['none','close','open','dilate','erode'],'outputs':['eps','pdf','svg','png'],'true_vectorization':'OpenCV contours + Douglas-Peucker polygons','hybrid':'embedded raster plus vector paths','dependencies':{'opencv':cv2.__version__,'numpy':np.__version__,'pillow':PIL.__version__},'limits':{'max_pixels':80_000_000,'workers':2,'approval_seconds':60}}
 def inspect(self,path):return load(safe_path(path,True))[2]
 def analyze(self,path,edge,vector):
  _,rgb,info=load(safe_path(path,True));e=detect(rgb,EdgeSettings(**edge));ps,_=contours(e,VectorSettings(**vector));return info|stats(e,ps)|{'edge_settings':edge,'vector_settings':vector}
 def compare(self,path,methods,base):
  _,rgb,info=load(safe_path(path,True));result={}
  for m in methods:
   s=EdgeSettings(**(base|{'method':m}));e=detect(rgb,s);ps,_=contours(e,VectorSettings());result[m]=stats(e,ps)
  return {'image':info,'methods':result}
 def plan_export(self,input,output,edge,vector,export):
  inp=safe_path(input,True);out=safe_path(output);es=EdgeSettings(**edge);vs=VectorSettings(**vector);xs=ExportSettings(**export)
  if out.suffix.lower()!=f'.{xs.output_format}':raise ValueError('output extension must match output_format')
  payload={'input':str(inp.relative_to(ROOT)),'output':str(out.relative_to(ROOT)),'edge':es.model_dump(),'vector':vs.model_dump(),'export':xs.model_dump(),'overwrite':out.exists()};return self.approval.plan('export',payload,f"Creates {'or replaces ' if out.exists() else ''}{out}; may consume substantial CPU/memory")
 def plan_batch(self,inputs,output_dir,edge,vector,export,suffix='_hybrid'):
  xs=ExportSettings(**export);items=[];d=safe_path(output_dir)
  for x in inputs:
   p=safe_path(x,True);o=d/(p.stem+suffix+'.'+xs.output_format);items.append({'input':str(p.relative_to(ROOT)),'output':str(o.relative_to(ROOT)),'overwrite':o.exists()})
  if len(items)>1000:raise ValueError('batch maximum is 1000')
  return self.approval.plan('batch',{'items':items,'edge':EdgeSettings(**edge).model_dump(),'vector':VectorSettings(**vector).model_dump(),'export':xs.model_dump()},f'Writes {len(items)} outputs; existing outputs disclosed per item')
 def execute(self,pid,token):
  p=self.approval.consume(pid,token);jid=uuid.uuid4().hex;flag=threading.Event();self.cancel[jid]=flag;self.jobs[jid]={'id':jid,'status':'running','action':p['action'],'started_at':time.time()};f=self.pool.submit(self._run,jid,p,flag);self.jobs[jid]['future']=f;return self.status(jid)
 def _one(self,x,edge,vector,export):
  _,rgb,_=load(safe_path(x['input'],True));e=detect(rgb,EdgeSettings(**edge));ps,_=contours(e,VectorSettings(**vector));out=safe_path(x['output']);out.parent.mkdir(parents=True,exist_ok=True);tmp=out.with_name('.'+out.name+'.'+uuid.uuid4().hex+'.tmp')
  try:
   with self.render_lock:render(rgb,ps,tmp,ExportSettings(**export))
   tmp.replace(out)
  finally:tmp.unlink(missing_ok=True)
  return {'output':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'contours':len(ps),'verified':out.is_file() and out.stat().st_size>0}
 def _run(self,jid,p,flag):
  j=self.jobs[jid]
  try:
   payload=p['payload'];items=[payload] if p['action']=='export' else payload['items'];results=[]
   for i,x in enumerate(items):
    if flag.is_set():j['status']='cancelled';break
    results.append(self._one(x,payload['edge'],payload['vector'],payload['export']));j['progress']=(i+1)/len(items)
   if j['status']=='running':j['status']='completed';j['results']=results;j['verified']=all(x['verified'] for x in results)
  except Exception as e:j.update(status='failed',error=type(e).__name__+': '+str(e),traceback=traceback.format_exc(limit=5))
  finally:
   j['completed_at']=time.time();self.log.parent.mkdir(parents=True,exist_ok=True)
   with self.log.open('a') as f:f.write(json.dumps({k:v for k,v in j.items() if k not in {'future','traceback'}})+'\n')
 def status(self,jid):
  j=self.jobs.get(jid)
  if not j:raise KeyError('job not found')
  return {k:v for k,v in j.items() if k!='future'}
 def cancel_job(self,jid):self.cancel[jid].set();return self.status(jid)
