import hashlib,json,secrets,time
class Approval:
 def __init__(self):self.plans={};self.tokens={}
 def create(self,action,payload,impact):
  x={'action':action,'payload':payload,'impact':impact,'created_at':time.time()};i=hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest();self.plans[i]=x;return {'approval_required':True,'plan_id':i,**x}
 def approve(self,i,text):
  if text.strip().lower() not in ('yes','approve','approved'):raise ValueError('explicit approval required')
  if i not in self.plans:raise KeyError('plan missing')
  t=secrets.token_urlsafe(32);self.tokens[t]=(i,time.time()+60);return {'token':t,'plan_id':i,'expires_at':time.time()+60}
 def consume(self,i,t):
  x=self.tokens.pop(t,None)
  if not x or x[0]!=i or x[1]<time.time():raise PermissionError('approval invalid, expired, used, or wrong plan')
  return self.plans.pop(i)
