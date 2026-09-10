from __future__ import annotations
import subprocess,zipfile,dis,io,ast,json,re
from pathlib import Path
class Runner:
 def __init__(self,timeout=120,max_output=5_000_000):self.timeout=timeout;self.max=max_output
 def run(self,argv,cwd=None):
  try:r=subprocess.run(argv,cwd=cwd,capture_output=True,timeout=self.timeout,shell=False);o=r.stdout[:self.max].decode('utf-8','replace');e=r.stderr[:self.max].decode('utf-8','replace');return {'argv':argv,'exit_code':r.returncode,'stdout':o,'stderr':e,'truncated':len(r.stdout)>self.max or len(r.stderr)>self.max}
  except subprocess.TimeoutExpired:return {'argv':argv,'exit_code':None,'stdout':'','stderr':'TIMEOUT','timed_out':True}
def generic(p,out,r):
 results={};results['file']=r.run(['file','-b',str(p)])
 results['strings_ascii']=r.run(['strings','-a','-n','4',str(p)]);results['strings_utf16']=r.run(['strings','-a','-e','l','-n','4',str(p)])
 (out/'strings').mkdir(parents=True,exist_ok=True);(out/'strings/ascii.txt').write_text(results['strings_ascii']['stdout']);(out/'strings/utf16le.txt').write_text(results['strings_utf16']['stdout']);return results
def native(p,out,r,depth):
 cmds={'headers':['objdump','-f',str(p)],'sections':['objdump','-h',str(p)],'imports_dynamic':['objdump','-p',str(p)],'symbols':['nm','-a','-C',str(p)],'disassembly':['objdump','-d','-C',str(p)]}
 if depth=='quick':cmds={k:v for k,v in cmds.items() if k in ('headers','sections')}
 d=out/'metadata';d.mkdir(parents=True,exist_ok=True);res={}
 for k,a in cmds.items():res[k]=r.run(a);(d/f'{k}.txt').write_text(res[k]['stdout']+'\n'+res[k]['stderr'])
 return res
def container(p,out,r):
 d=out/'metadata';d.mkdir(parents=True,exist_ok=True)
 try:
  with zipfile.ZipFile(p) as z:
   items=[{'name':x.filename,'compressed':x.compress_size,'size':x.file_size,'crc':hex(x.CRC),'encrypted':bool(x.flag_bits&1)} for x in z.infolist()];(d/'container.json').write_text(json.dumps(items,indent=2));return {'entries':items,'extracted':False,'reason':'static listing only; prevents traversal/decompression bombs'}
 except Exception as e:return {'error':str(e)}
def python_source(p,out):
 source=p.read_text(errors='replace');tree=ast.parse(source);code=compile(tree,str(p),'exec');s=io.StringIO();dis.dis(code,file=s,depth=10);d=out/'disassembly';d.mkdir(parents=True,exist_ok=True);(d/'python-bytecode.txt').write_text(s.getvalue());return {'syntax_valid':True,'functions':[x.name for x in ast.walk(tree) if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))],'classes':[x.name for x in ast.walk(tree) if isinstance(x,ast.ClassDef)],'imports':[ast.unparse(x) for x in ast.walk(tree) if isinstance(x,(ast.Import,ast.ImportFrom))]}
def jvm(p,out,r):
 if not __import__('shutil').which('javap'):return {'unavailable':'javap not installed (JDK required)'}
 x=r.run(['javap','-c','-p','-s',str(p)]);d=out/'disassembly';d.mkdir(parents=True,exist_ok=True);(d/'javap.txt').write_text(x['stdout']);return x
def wasm(p,out,r):
 import shutil
 res={};d=out/'disassembly';d.mkdir(parents=True,exist_ok=True)
 for x,args,name in [('wasm-objdump',['-x','-d'],'wasm-objdump.txt'),('wasm2wat',[],'module.wat'),('wasm-decompile',[],'decompiled.dcmp')]:
  if shutil.which(x):res[x]=r.run([x,*args,str(p)]);(d/name).write_text(res[x]['stdout'])
 return res or {'unavailable':'WABT not installed'}
def decompilers(p,out,r,fmt,registry):
 import shutil
 res={};d=out/'decompilation';d.mkdir(parents=True,exist_ok=True)
 if fmt in ('APK','DEX') and shutil.which('jadx'):
  dest=d/'jadx';res['jadx']=r.run(['jadx','--no-res','--show-bad-code','-d',str(dest),str(p)])
 if fmt in ('JAR','JVM CLASS'):
  cfr=next((x for x in registry if x['id']=='cfr' and x['installed']),None)
  if cfr and shutil.which('java'):
   dest=d/'cfr';res['cfr']=r.run(['java','-jar',cfr['executable'],str(p),'--outputdir',str(dest)])
 if fmt=='PE' and shutil.which('ilspycmd'):
  dest=d/'ilspy';res['ilspycmd']=r.run(['ilspycmd','-p','-o',str(dest),str(p)])
 return res
