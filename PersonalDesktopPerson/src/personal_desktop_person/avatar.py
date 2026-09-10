from __future__ import annotations
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import threading,json
class AvatarServer:
 def __init__(self,runtime,host,port,web_dir):self.runtime=runtime;self.host=host;self.port=port;self.web=Path(web_dir);self.server=None;self.thread=None
 def start(self):
  runtime=self.runtime;web=self.web
  class H(SimpleHTTPRequestHandler):
   def log_message(self,*a):return
   def do_GET(self):
    if self.path=='/api/state':
     from .models import obj
     payload=obj(runtime.state);payload['world']=runtime.world.summary('desktop');b=json.dumps(payload).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b);return
    target=web/('index.html' if self.path in ('/','') else self.path.lstrip('/'))
    if not target.resolve().is_relative_to(web.resolve()) or not target.exists():self.send_error(404);return
    b=target.read_bytes();self.send_response(200);self.send_header('Content-Type','text/html' if target.suffix=='.html' else 'text/css' if target.suffix=='.css' else 'application/javascript');self.end_headers();self.wfile.write(b)
  self.server=ThreadingHTTPServer((self.host,self.port),H);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True,name='person-avatar');self.thread.start();return f'http://{self.host}:{self.port}'
 def stop(self):
  if self.server:self.server.shutdown();self.server.server_close()
