from __future__ import annotations
import json,urllib.request
class NoPlanner:
 def next_action(self,goal,state,history):return {'action':'stop','reason':'No planner configured; use assisted/direct tools or configure OpenAI-compatible provider.'}
class OpenAICompatiblePlanner:
 def __init__(self,url,model,api_key='',timeout=30):self.url=url;self.model=model;self.key=api_key;self.timeout=timeout
 def next_action(self,goal,state,history):
  elements=[{'id':e.id,'role':e.role,'name':e.name,'bounds':[e.bounds.x,e.bounds.y,e.bounds.width,e.bounds.height]} for e in state.elements[:150]]
  prompt={'goal':goal,'window':state.window.title,'elements':elements,'recent':history[-5:],'instruction':'Return one JSON action: click_element(id), type_text(text), hotkey(keys), press_key(key), focus_window(hwnd), open_application(path,args), wait(seconds), complete(reason), or stop(reason).'}
  body=json.dumps({'model':self.model,'messages':[{'role':'system','content':'You control Windows through bounded verified actions. Output JSON only.'},{'role':'user','content':json.dumps(prompt)}],'temperature':0}).encode()
  req=urllib.request.Request(self.url.rstrip('/')+'/chat/completions',body,{'Content-Type':'application/json','Authorization':'Bearer '+self.key})
  with urllib.request.urlopen(req,timeout=self.timeout) as r:data=json.load(r)
  text=data['choices'][0]['message']['content'].strip().strip('`');text=text.removeprefix('json').strip();return json.loads(text)
