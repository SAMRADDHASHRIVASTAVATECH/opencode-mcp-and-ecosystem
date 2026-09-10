from __future__ import annotations
import signal,time
from .config import Config
from .runtime import PersonRuntime
from .avatar import AvatarServer
def main():
 c=Config.load();r=PersonRuntime(c);a=None;r.start()
 if c.avatar_enabled:a=AvatarServer(r,c.avatar_host,c.avatar_port,__import__('pathlib').Path(__file__).parent/'web');a.start()
 stopping=False
 def stop(*_):
  nonlocal stopping;stopping=True
 signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
 try:
  while not stopping:time.sleep(.5)
 finally:
  if a:a.stop()
  r.stop(False);r.memory.close()
if __name__=='__main__':main()
