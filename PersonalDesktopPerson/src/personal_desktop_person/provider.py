from __future__ import annotations
import json,urllib.request,os
class ModelGateway:
 def __init__(self,url='',model='',key_env='PDP_API_KEY',timeout=60):self.url=url;self.model=model;self.key=os.getenv(key_env,'');self.timeout=timeout
 @property
 def available(self):return bool(self.url and self.model)
 def chat(self,system,user,schema_hint=''):
  if not self.available:return None
  body=json.dumps({'model':self.model,'messages':[{'role':'system','content':system},{'role':'user','content':user+(('\nReturn JSON: '+schema_hint) if schema_hint else '')}],'temperature':.4}).encode();headers={'Content-Type':'application/json'}
  if self.key:headers['Authorization']='Bearer '+self.key
  req=urllib.request.Request(self.url.rstrip('/')+'/chat/completions',body,headers)
  with urllib.request.urlopen(req,timeout=self.timeout) as r:return json.load(r)['choices'][0]['message']['content']
