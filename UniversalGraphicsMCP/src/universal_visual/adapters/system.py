from __future__ import annotations
import shutil,subprocess,sys,platform,importlib.util,os,json
class SystemAdapter:
 TOOLS={'ffmpeg':['ffmpeg','-version'],'blender':['blender','--version'],'inkscape':['inkscape','--version'],'tesseract':['tesseract','--version'],'vtracer':['vtracer','--version'],'krita':['krita','--version'],'gimp':['gimp','--version']}
 def discover(self):
  out={}
  for n,cmd in self.TOOLS.items():
   p=shutil.which(cmd[0]);ver=''
   if p:
    try:ver=subprocess.run(cmd,capture_output=True,text=True,timeout=3).stdout.splitlines()[0][:200]
    except Exception:pass
   out[n]={'available':bool(p),'path':p,'version':ver}
  mods=['cv2','onnxruntime','torch','pytesseract','trimesh','vtracer','skimage']
  out['python']={m:bool(importlib.util.find_spec(m)) for m in mods};return out
 def hardware(self):
  d={'platform':platform.platform(),'python':sys.version,'cpu_count':os.cpu_count(),'gpu':[]}
  try:
   import psutil;d.update({'ram_total':psutil.virtual_memory().total,'ram_available':psutil.virtual_memory().available,'disk_free':shutil.disk_usage('.').free})
  except Exception:pass
  try:
   import onnxruntime as ort;d['onnx_providers']=ort.get_available_providers()
  except Exception:d['onnx_providers']=[]
  try:
   import torch;d['torch']={'cuda':torch.cuda.is_available(),'devices':torch.cuda.device_count() if torch.cuda.is_available() else 0}
  except Exception:d['torch']=None
  return d
