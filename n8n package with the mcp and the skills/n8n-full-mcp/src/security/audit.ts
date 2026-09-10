import{appendFile,mkdir}from'node:fs/promises';import path from'node:path';
const SECRET=/token|secret|password|api.?key|credential|authorization/i;
function clean(v:unknown,key=''):unknown{if(SECRET.test(key))return'[REDACTED]';if(Array.isArray(v))return v.map(x=>clean(x));if(v&&typeof v==='object')return Object.fromEntries(Object.entries(v as Record<string,unknown>).map(([k,x])=>[k,clean(x,k)]));return v}
export async function audit(file:string,event:string,fields:Record<string,unknown>={}){await mkdir(path.dirname(file),{recursive:true});await appendFile(file,JSON.stringify({time:new Date().toISOString(),event,...(clean(fields) as Record<string,unknown>)})+'\n',{encoding:'utf8',mode:0o600})}
