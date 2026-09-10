from __future__ import annotations
import json,time,uuid,hashlib,shutil,os
from pathlib import Path
from .identify import identify
from .paths import within,TARGET_ROOT,ANALYSIS_ROOT
from .registry import Registry
from ..adapters.local import Runner,generic,native,container,python_source,jvm,wasm,decompilers
CAPS={'ELF':['native-metadata','disassembly','decompilation'],'PE':['native-metadata','disassembly','decompilation'],'.NET assembly':['dotnet-decompile'],'PE/.NET':['dotnet-decompile'],'JVM CLASS':['jvm-decompile'],'JAR':['jvm-decompile'],'APK':['android-decompile'],'DEX':['android-decompile'],'WASM':['wasm-disassembly','wasm-decompile'],'possible PYC':['python-decompile']}
class Router:
 def __init__(self):self.registry=Registry()
 def identify_target(self,target):return identify(within(target,TARGET_ROOT,True))
 def route(self,target,depth='normal'):
  i=self.identify_target(target);fmt='.NET assembly' if '.NET' in i['runtime'] else i['format'];caps=CAPS.get(fmt,['identify','strings']);tools=self.registry.scan();return {'identification':i,'required_capabilities':caps,'candidates':[{'tool':t['id'],'installed':t['installed'],'matching_capabilities':sorted(set(caps)&set(t['capabilities']))} for t in tools if set(caps)&set(t['capabilities'])],'depth':depth,'static_only':True}
 def analyze(self,target,depth='normal',output_directory=None,goal='understand',preferred_language=None,recursive=True):
  p=within(target,TARGET_ROOT,True);route=self.route(target,depth);ident=route['identification'];name=output_directory or f"{p.stem}-{ident['sha256'][:12]}";out=within(name,ANALYSIS_ROOT);out.mkdir(parents=True,exist_ok=True)
  for d in ('identification','metadata','strings','imports','exports','symbols','disassembly','decompilation','reconstruction','verification','reports'):(out/d).mkdir(exist_ok=True)
  (out/'identification/identification.json').write_text(json.dumps(ident,indent=2));r=Runner(timeout={'quick':30,'normal':120,'deep':300,'extreme':600}[depth]);results={'generic':generic(p,out,r)};fmt=ident['format']
  if fmt in ('ELF','PE','Mach-O/Fat'):results['native']=native(p,out,r,depth)
  if fmt in ('ZIP/container','JAR','APK'):results['container']=container(p,out,r)
  if fmt=='JVM CLASS':results['jvm']=jvm(p,out,r)
  if fmt=='WASM':results['wasm']=wasm(p,out,r)
  if p.suffix.lower()=='.py':results['python']=python_source(p,out)
  high=decompilers(p,out,r,fmt,self.registry.scan())
  if high:results['decompilers']=high
  missing=[x for x in route['candidates'] if not x['installed'] and x['matching_capabilities']];used=[x for x in route['candidates'] if x['installed'] and x['matching_capabilities']]
  confidence={'format':ident['format_confidence'],'architecture':'confirmed' if ident['architecture'] else 'unknown','language':'probable' if ident['runtime'] else 'unknown','source_recovery':'partial_or_unavailable'}
  report={'target':str(p),'goal':goal,'depth':depth,'route':route,'tools_used':used,'missing_recommended_tools':missing,'results':results,'confidence':confidence,'reconstruction_labels':{'RECOVERED':'direct symbols/metadata/bytecode facts','INFERRED':'language/compiler heuristics','RECONSTRUCTED':'decompiler output where available','GENERATED':'reports/project scaffolding','UNKNOWN':'information removed or not recoverable'},'limitations':['analysis never executed target','original comments/local names/types may be irretrievably lost','optimization, stripping, packing and obfuscation reduce recovery','decompiler output is approximation and must be cross-validated'],'generated_at':time.time(),'output_directory':str(out)}
  (out/'reports/report.json').write_text(json.dumps(report,indent=2));(out/'reports/summary.md').write_text(self.markdown(report));(out/'verification/manifest.json').write_text(json.dumps(self.manifest(out),indent=2));return report
 def markdown(self,x):return f"# Universal decompilation report\n\nTarget: `{x['target']}`\n\nFormat: **{x['route']['identification']['format']}** ({x['confidence']['format']})\n\nArchitecture: **{x['route']['identification']['architecture'] or 'unknown'}**\n\nTools used: {', '.join(t['tool'] for t in x['tools_used']) or 'built-in static triage only'}\n\nMissing recommended tools: {', '.join(t['tool'] for t in x['missing_recommended_tools']) or 'none'}\n\nNo target code was executed. Reconstructed output is not guaranteed original source.\n"
 def manifest(self,out):return [{'path':str(p.relative_to(out)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in out.rglob('*') if p.is_file()]
