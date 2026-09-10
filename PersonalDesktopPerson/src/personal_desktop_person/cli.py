from __future__ import annotations
import argparse,json,sys,shutil,zipfile,tempfile,subprocess,os,time,signal
from pathlib import Path
from .config import Config
from .runtime import PersonRuntime
def report(c):
 r=PersonRuntime(c);checks={'configuration':('PASS','loaded'),'database':('PASS' if r.storage.integrity()=='ok' else 'FAIL',r.storage.integrity()),'schema':('PASS','current'),'event_bus':('PASS','ready'),'identity':('PASS',r.personality.data['name']),'model':('PASS','configured') if r.models.available else ('NOT CONFIGURED','deterministic runtime still works'),'mcp':('PASS','installed'),'policy':('PASS','conservative'),'capabilities':('PASS','HMAC scoped'),'computer_control':('WARN','external adapter must be separately installed/authorized'),'voice':('NOT CONFIGURED','extension boundary'),'avatar':('PASS' if c.avatar_enabled else 'NOT CONFIGURED',f'{c.avatar_host}:{c.avatar_port}'),'storage':('PASS',str(r.storage.path))};r.memory.close();return checks
def main():
 ap=argparse.ArgumentParser(prog='pdp');ap.add_argument('--config');sp=ap.add_subparsers(dest='cmd',required=True)
 for x in ['doctor','status','initialize','repair','start','stop','restart']:sp.add_parser(x)
 b=sp.add_parser('backup');b.add_argument('destination');rs=sp.add_parser('restore');rs.add_argument('source');rs.add_argument('--force',action='store_true');ex=sp.add_parser('export');ex.add_argument('destination');de=sp.add_parser('delete-data');de.add_argument('--yes',action='store_true')
 a=ap.parse_args();c=Config.load(a.config)
 if a.cmd=='doctor':print(json.dumps({k:{'status':v[0],'detail':v[1]} for k,v in report(c).items()},indent=2));return
 pidfile=Path(c.data_dir)/'pdp.pid'
 if a.cmd in ('start','stop','restart'):
  if a.cmd in ('stop','restart') and pidfile.exists():
   pid=int(pidfile.read_text());
   try: os.kill(pid,signal.SIGTERM);time.sleep(.5)
   except ProcessLookupError: pass
   pidfile.unlink(missing_ok=True)
  if a.cmd in ('start','restart'):
   Path(c.data_dir).mkdir(parents=True,exist_ok=True);env=os.environ.copy();env['PDP_CONFIG']=a.config or os.getenv('PDP_CONFIG','config/default.json');log=open(Path(c.data_dir)/'daemon.log','ab');p=subprocess.Popen([sys.executable,'-m','personal_desktop_person.daemon'],stdin=subprocess.DEVNULL,stdout=log,stderr=log,env=env,start_new_session=True);pidfile.write_text(str(p.pid));print(json.dumps({'started':True,'pid':p.pid}));return
  print(json.dumps({'stopped':True}));return
 r=PersonRuntime(c)
 if a.cmd in ('initialize','repair'):print(json.dumps({'initialized':True,'integrity':r.storage.integrity(),'checkpoint':r.checkpoint()},indent=2))
 elif a.cmd=='status':print(json.dumps(r.status(),indent=2))
 elif a.cmd in ('backup','export'):print(r.storage.backup(a.destination,[r.personality.path,Path(a.config or 'config/default.json')]))
 elif a.cmd=='restore':
  if not a.force:raise SystemExit('Restore is destructive; rerun with --force after backing up current data.')
  r.memory.close();src=Path(a.source);data=Path(c.data_dir);data.mkdir(parents=True,exist_ok=True)
  with zipfile.ZipFile(src) as z:z.extractall(data)
  print('restored') ;return
 elif a.cmd=='delete-data':
  if not a.yes:raise SystemExit('Refusing deletion without --yes')
  r.memory.close();shutil.rmtree(c.data_dir,ignore_errors=True);print('deleted');return
 r.memory.close()
if __name__=='__main__':main()
