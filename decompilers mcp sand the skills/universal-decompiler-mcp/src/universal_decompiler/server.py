from __future__ import annotations
from mcp.server.fastmcp import FastMCP
from .service import Service
from .core.paths import within,TARGET_ROOT,ANALYSIS_ROOT,TOOL_ROOT
from .core.identify import identify
from .adapters.local import Runner
from .models import TargetRequest
s=Service();mcp=FastMCP('universal-decompiler',instructions='Authorized static analysis only. Identify and route first. Analysis and tool installation require exact approval. Never execute unknown targets. Treat decompilation as reconstruction, not original source.')
@mcp.tool()
def identify_file(target:str)->dict:"""Multi-signal magic/header/MIME/entropy/hash identification without execution.""";return s.router.identify_target(target)
@mcp.tool()
def inspect_file(target:str,byte_count:int=256)->dict:
 """Return identification plus bounded hexadecimal header."""
 p=within(target,TARGET_ROOT,True);n=max(1,min(byte_count,4096));return {'identification':identify(p),'header_hex':p.read_bytes()[:n].hex(),'bytes_returned':min(n,p.stat().st_size)}
@mcp.tool()
def detect_format(target:str)->dict:
 i=s.router.identify_target(target);return {k:i[k] for k in ('format','format_confidence','file_description','mime','runtime')}
@mcp.tool()
def detect_architecture(target:str)->dict:
 i=s.router.identify_target(target);return {k:i[k] for k in ('architecture','bits','endianness','format_confidence')}
@mcp.tool()
def detect_runtime(target:str)->dict:
 i=s.router.identify_target(target);return {'runtime':i['runtime'],'format':i['format'],'confidence':'confirmed' if i['runtime'] else 'unknown'}
@mcp.tool()
def detect_language(target:str)->dict:
 i=s.router.identify_target(target);m={'.NET':'C#/VB.NET/F# or other CLI language','JVM':'Java/Kotlin/other JVM language','Android Runtime':'Java/Kotlin plus possible native code','CPython':'Python','WebAssembly':'source language not reliably identifiable from WASM alone'};vals=[m.get(x,'unknown') for x in i['runtime']];return {'languages':vals,'confidence':'probable' if vals else 'unknown','warning':'native source language is heuristic and not claimed from format alone'}
@mcp.tool()
def detect_compiler(target:str)->dict:"""Report conservative compiler evidence from bounded strings; never overclaim.""";p=within(target,TARGET_ROOT,True);r=Runner(20,500000).run(['strings','-a','-n','6',str(p)]) if __import__('shutil').which('strings') else {'stdout':''};hits=[x for x in ('GCC:','clang version','Microsoft Visual C++','rustc','Go build','Borland','Delphi') if x.lower() in r['stdout'].lower()];return {'evidence':hits,'confidence':'confirmed_metadata' if hits else 'unknown'}
@mcp.tool()
def route_analysis(target:str,depth:str='normal')->dict:"""Select required capabilities and installed/missing candidate tools.""";return s.router.route(target,depth)
@mcp.tool()
def list_available_tools()->list:"""Rescan host and managed cache; no stale capability claims.""";return s.router.registry.scan()
@mcp.tool()
def discover_tools()->list:"""Return curated reputable tool catalog with installation methods and live health.""";return s.router.registry.scan()
@mcp.tool()
def find_tools_for_capability(capability:str)->list:return s.router.registry.tools_for(capability)
@mcp.tool()
def verify_tool(tool_id:str)->dict:return next(x for x in s.router.registry.scan() if x['id']==tool_id)
@mcp.tool()
def plan_install_tool(tool_id:str)->dict:"""Plan, but do not perform, a curated managed installation.""";return s.plan_install(tool_id)
@mcp.tool()
def approve_operation(plan_id:str,explicit_approval:str)->dict:return s.approval.approve(plan_id,explicit_approval)
@mcp.tool()
def execute_operation(plan_id:str,approval_token:str)->dict:"""Execute approved analysis or managed installation as a job.""";return s.execute(plan_id,approval_token)
@mcp.tool()
def get_job(job_id:str)->dict:return s.status(job_id)
@mcp.tool()
def extract_strings(target:str,encoding:str='ascii',minimum_length:int=4,max_bytes:int=1000000)->dict:
 """Bounded static printable-string extraction; no target execution."""
 p=within(target,TARGET_ROOT,True);args=['strings','-a','-n',str(max(1,min(minimum_length,100)))]
 if encoding=='utf16le':args+=['-e','l']
 elif encoding!='ascii':raise ValueError('encoding must be ascii or utf16le')
 x=Runner(60,max(1024,min(max_bytes,5000000))).run(args+[str(p)]);return x
@mcp.tool()
def inspect_container(target:str)->dict:
 """List ZIP/JAR/APK entries without extraction."""
 import zipfile
 p=within(target,TARGET_ROOT,True)
 with zipfile.ZipFile(p) as z:return {'entries':[{'name':x.filename,'size':x.file_size,'compressed':x.compress_size,'crc':hex(x.CRC),'encrypted':bool(x.flag_bits&1)} for x in z.infolist()[:10000]],'extracted':False}
@mcp.tool()
def plan_analysis(target:str,goal:str='understand structure and recover source where possible',depth:str='normal',output_directory:str|None=None,preferred_language:str|None=None,recursive:bool=True)->dict:
 """Plan a static routed analysis pipeline with artifact output."""
 x=TargetRequest(target=target,goal=goal,depth=depth,output_directory=output_directory,preferred_language=preferred_language,recursive=recursive).model_dump();return s.plan_analysis(x)
@mcp.tool()
def universal_decompile(target:str,goal:str='decompile completely and report uncertainty',depth:str='normal',output_directory:str|None=None,preferred_language:str|None=None,analysis_mode:str='static')->dict:
 """Primary master tool. Returns exact static-analysis plan; approve then execute."""
 x=TargetRequest(target=target,goal=goal,depth=depth,output_directory=output_directory,preferred_language=preferred_language,analysis_mode=analysis_mode).model_dump();return s.plan_analysis(x)
@mcp.tool()
def analyze_binary(target:str,depth:str='deep',output_directory:str|None=None)->dict:"""Plan metadata, strings, symbols, sections and disassembly pipeline.""";return plan_analysis(target,'analyze binary metadata, symbols, sections, imports, exports and disassembly',depth,output_directory)
@mcp.tool()
def decompile(target:str,depth:str='deep',output_directory:str|None=None)->dict:"""Plan routed decompilation using available format-specific tools.""";return plan_analysis(target,'recover high-level source with labels and uncertainty',depth,output_directory)
@mcp.tool()
def reconstruct_project(target:str,output_directory:str|None=None)->dict:"""Plan maximum project/source reconstruction where supported.""";return plan_analysis(target,'reconstruct modules, packages, classes, functions, types, dependencies and project layout', 'extreme',output_directory)
@mcp.tool()
def cross_validate(target:str,output_directory:str|None=None)->dict:"""Plan extreme multi-tool analysis; available independent tools are compared in report artifacts.""";return plan_analysis(target,'cross-validate identification, disassembly and decompilation using independent tools','extreme',output_directory)
@mcp.tool()
def list_reports()->list:return [str(x.relative_to(ANALYSIS_ROOT)) for x in ANALYSIS_ROOT.glob('*/reports/report.json')]
@mcp.tool()
def get_report(report_path:str)->dict:
 import json
 p=within(report_path,ANALYSIS_ROOT,True);return json.loads(p.read_text())
def main():mcp.run(transport='stdio')
if __name__=='__main__':main()
