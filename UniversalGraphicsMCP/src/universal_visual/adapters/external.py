from __future__ import annotations
import shutil,subprocess,json,re
class ExternalAdapter:
 name='external'
 def capabilities(self):
  c=[]
  if shutil.which('tesseract'):c+=['ocr.read']
  if shutil.which('ffmpeg'):c+=['video.extract_frame','media.probe']
  return c
 def run(self,op,inputs,p,store):
  src=store.get(inputs[0]).path
  if op=='ocr.read':
   lang=re.sub(r'[^A-Za-z0-9_+-]','',p.get('language','eng'));cmd=['tesseract',src,'stdout','-l',lang,'tsv'];r=subprocess.run(cmd,capture_output=True,text=True,timeout=min(int(p.get('timeout',30)),120));
   if r.returncode:raise RuntimeError(r.stderr[-1000:])
   rows=[]
   for line in r.stdout.splitlines()[1:]:
    x=line.split('\t')
    if len(x)>=12 and x[11].strip():rows.append({'x':int(x[6]),'y':int(x[7]),'width':int(x[8]),'height':int(x[9]),'confidence':float(x[10]),'text':x[11]})
   return [],{'text':' '.join(x['text'] for x in rows),'regions':rows}
  if op=='video.extract_frame':
   out=store.create_path('.png');cmd=['ffmpeg','-nostdin','-v','error','-ss',str(max(0,float(p.get('seconds',0)))),'-i',src,'-frames:v','1','-y',str(out)];r=subprocess.run(cmd,capture_output=True,text=True,timeout=min(int(p.get('timeout',60)),180));
   if r.returncode:raise RuntimeError(r.stderr[-1000:])
   a=store.register(out,'image',self.name,inputs,{'seconds':p.get('seconds',0)});return [a],{}
  raise ValueError(op)
