from __future__ import annotations
import json,shutil,subprocess,sys,os,time
from pathlib import Path
from ..models import ToolRecord
from .paths import TOOL_ROOT
CATALOG=Path(__file__).parents[1]/'catalog.json'
EXES={'file':['file'],'binutils':['objdump','readelf','nm','strings'],'ghidra':['analyzeHeadless'],'radare2':['r2','radare2'],'jadx':['jadx'],'cfr':[],'ilspycmd':['ilspycmd'],'wabt':['wasm2wat','wasm-decompile','wasm-objdump'],'python-tools':['pycdc','uncompyle6','decompyle3'],'lief':[],'pefile':[]}
class Registry:
 def __init__(self):self.path=TOOL_ROOT/'registry/registry.json';self.path.parent.mkdir(parents=True,exist_ok=True);self.catalog=json.loads(CATALOG.read_text())
 def scan(self):
  out=[]
  for d in self.catalog:
   found={x:shutil.which(x) for x in EXES.get(d['id'],[]) if shutil.which(x)}
   if d['id'] in ('lief','pefile'):
    q=TOOL_ROOT/'installed'/d['id'];module={'lief':'lief','pefile':'pefile'}[d['id']];installed=(q/module).exists() or (q/(module+'.py')).exists();exe=str(q) if installed else None
   elif d['id']=='cfr':
    jars=list((TOOL_ROOT/'installed/cfr').glob('*.jar')) if (TOOL_ROOT/'installed/cfr').exists() else [];installed=bool(jars) and bool(shutil.which('java'));exe=str(jars[0]) if jars else None
   else:installed=bool(found);exe=next(iter(found.values()),None)
   health='ok' if installed else 'missing';r=ToolRecord(**d,installed=installed,executable=exe,health=health).model_dump();r['discovered_executables']=found;out.append(r)
  self.path.write_text(json.dumps({'updated_at':time.time(),'tools':out},indent=2));return out
 def tools_for(self,capability):return [x for x in self.scan() if capability in x['capabilities'] or '*' in x['formats']]
 def plan_install(self,tool_id):
  d=next(x for x in self.catalog if x['id']==tool_id);i=d.get('install',{});plan={'tool_id':tool_id,'source':d['source'],'install':i,'tool_root':str(TOOL_ROOT),'network':True,'executes_downloaded_code':True,'requires_explicit_approval':True}
  if i.get('kind')=='pip_target':plan['argv']=[sys.executable,'-m','pip','install','--disable-pip-version-check','--no-input','--target',str(TOOL_ROOT/'installed'/tool_id),i['package']];plan['automatic_supported']=True
  elif i.get('kind')=='dotnet_tool' and shutil.which('dotnet'):plan['argv']=['dotnet','tool','install','--tool-path',str(TOOL_ROOT/'installed'/tool_id),i['package']];plan['automatic_supported']=True
  else:plan['automatic_supported']=False;plan['reason']=i.get('reason','Manual installation/review required; no verified pinned artifact recipe for this OS.')
  return plan
 def execute_install(self,plan,timeout=600):
  if not plan.get('automatic_supported'):raise RuntimeError(plan.get('reason'))
  dest=TOOL_ROOT/'installed'/plan['tool_id'];dest.mkdir(parents=True,exist_ok=True);r=subprocess.run(plan['argv'],capture_output=True,text=True,timeout=timeout,shell=False);result={'exit_code':r.returncode,'stdout':r.stdout[-20000:],'stderr':r.stderr[-20000:]}
  if r.returncode!=0:raise RuntimeError(f"installer failed ({r.returncode}): {r.stderr[-4000:]}")
  result['registry']=next(x for x in self.scan() if x['id']==plan['tool_id'])
  if not result['registry']['installed']:raise RuntimeError('installation command succeeded but health/registration verification failed')
  return result
