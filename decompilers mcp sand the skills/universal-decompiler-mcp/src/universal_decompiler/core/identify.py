from __future__ import annotations
import hashlib,math,mimetypes,subprocess,struct,zipfile
from collections import Counter
from pathlib import Path
def entropy(data):
 if not data:return 0.
 n=len(data);return -sum((c/n)*math.log2(c/n) for c in Counter(data).values())
def identify(p:Path):
 head=p.read_bytes()[:65536];sig='unknown';runtime=[];arch=None;bits=None;endian=None;confidence='possible'
 if head.startswith(b'\x7fELF'):
  sig='ELF';bits={1:32,2:64}.get(head[4]);endian={1:'little',2:'big'}.get(head[5]);machine=int.from_bytes(head[18:20],endian or 'little');arch={3:'x86',62:'x86-64',40:'ARM',183:'AArch64',8:'MIPS',20:'PowerPC',243:'RISC-V',2:'SPARC'}.get(machine,f'ELF machine {machine}');confidence='confirmed'
 elif head[:2]==b'MZ':
  sig='PE';confidence='confirmed'
  if len(head)>0x40:
   off=int.from_bytes(head[0x3c:0x40],'little')
   if off+26<len(head) and head[off:off+4]==b'PE\0\0':
    m=int.from_bytes(head[off+4:off+6],'little');arch={0x14c:'x86',0x8664:'x86-64',0x1c0:'ARM',0xaa64:'AArch64'}.get(m,hex(m));bits=64 if m in (0x8664,0xaa64) else 32;opt=int.from_bytes(head[off+24:off+26],'little');dirs=off+24+(112 if opt==0x20b else 96)
    if dirs+15*8<=len(head) and int.from_bytes(head[dirs+14*8:dirs+14*8+4],'little'):runtime.append('.NET')
 elif head.startswith(b'\xca\xfe\xba\xbe') and len(head)>=8 and 45<=int.from_bytes(head[6:8],'big')<=100:sig='JVM CLASS';runtime=['JVM'];confidence='confirmed'
 elif head.startswith(b'dex\n'):sig='DEX';runtime=['Android Runtime'];confidence='confirmed'
 elif head.startswith(b'\0asm'):sig='WASM';runtime=['WebAssembly'];confidence='confirmed'
 elif head[:4] in (b'\xfe\xed\xfa\xce',b'\xce\xfa\xed\xfe',b'\xfe\xed\xfa\xcf',b'\xcf\xfa\xed\xfe',b'\xca\xfe\xba\xbe'):sig='Mach-O/Fat';confidence='confirmed'
 elif head.startswith(b'PK\x03\x04'):
  sig='ZIP/container';confidence='confirmed'
  try:
   with zipfile.ZipFile(p) as z:
    names=z.namelist()
    if 'AndroidManifest.xml' in names or any(x.endswith('.dex') for x in names):sig='APK';runtime=['Android Runtime']
    elif 'META-INF/MANIFEST.MF' in names or any(x.endswith('.class') for x in names):sig='JAR';runtime=['JVM']
  except:pass
 elif len(head)>=4 and head[2:4]==b'\r\n':sig='possible PYC';runtime=['CPython'];confidence='possible'
 try:desc=subprocess.run(['file','-b',str(p)],capture_output=True,text=True,timeout=10).stdout.strip()
 except Exception:desc='file utility unavailable'
 sample=p.read_bytes()[:4*1024*1024];return {'path':str(p),'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'format':sig,'format_confidence':confidence,'architecture':arch,'bits':bits,'endianness':endian,'runtime':runtime,'mime':mimetypes.guess_type(p.name)[0],'file_description':desc,'entropy_sample':entropy(sample),'packed_or_compressed_indicator':'high' if entropy(sample)>7.5 else 'not_high','never_executed':True}
