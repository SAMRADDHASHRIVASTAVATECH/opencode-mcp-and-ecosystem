#!/usr/bin/env python3
import argparse,venv,subprocess,os,json,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];V=R/'.venv';P=V/('Scripts/python.exe' if os.name=='nt' else 'bin/python');S=R/'runtime'
def install():
 if not P.exists():venv.EnvBuilder(with_pip=True).create(V)
 subprocess.run([P,'-m','pip','install','-e',R],check=True)
def init():S.mkdir(exist_ok=True);(S/'artifacts').mkdir(exist_ok=True)
def config():return {'mcp':{'universal-graphics-vision':{'type':'local','command':[str(P),'-m','universal_visual.server'],'environment':{'UVC_ARTIFACT_ROOT':str(S/'artifacts')}}}}
def doctor():
 r=subprocess.run([P,'-c','from universal_visual.server import create_server; create_server(); print("OK")'],capture_output=True,text=True);print(r.stdout or r.stderr);return r.returncode
def main():
 a=argparse.ArgumentParser();a.add_argument('action',choices=['install','init','config','doctor','uninstall']);x=a.parse_args()
 if x.action=='install':install()
 elif x.action=='init':init()
 elif x.action=='config':print(json.dumps(config(),indent=2))
 elif x.action=='doctor':raise SystemExit(doctor())
 else:shutil.rmtree(V,ignore_errors=True)
if __name__=='__main__':main()
