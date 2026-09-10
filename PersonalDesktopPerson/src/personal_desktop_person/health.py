import json,sys
from .config import Config
from .runtime import PersonRuntime
def main():
 c=Config.load();r=PersonRuntime(c);s=r.start();r.stop(False);r.memory.close();print(json.dumps({'ok':True,'python':sys.version,'status':s['status'],'data_dir':c.data_dir},indent=2))
if __name__=='__main__':main()
