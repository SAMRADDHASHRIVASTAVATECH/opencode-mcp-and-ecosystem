import hashlib,json,secrets,time
class Approval:
 def __init__(self):self.pending={};self.tokens={}
 def plan(self,action,args,current,impact):
  payload={'action':action,'arguments':args,'current':current,'impact':impact,'created_at':time.time()};raw=json.dumps(payload,sort_keys=True,separators=(',',':'));pid=hashlib.sha256(raw.encode()).hexdigest();self.pending[pid]=payload;return {'approval_required':True,'plan_id':pid,**payload}
 def approve(self,pid,confirmation):
  if confirmation.strip().lower() not in ('approve','approved','yes'):raise ValueError('explicit approval required')
  if pid not in self.pending:raise KeyError('plan not found');
  token=secrets.token_urlsafe(32);self.tokens[token]=(pid,time.time()+60);return {'token':token,'plan_id':pid,'expires_at':time.time()+60}
 def consume(self,pid,token):
  found=self.tokens.pop(token,None)
  if not found or found[0]!=pid or found[1]<time.time():raise PermissionError('approval invalid, expired, used, or wrong plan')
  return self.pending.pop(pid)
