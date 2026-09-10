from __future__ import annotations
from pathlib import Path
import uuid,json,mimetypes,shutil
from .types import Artifact
class ArtifactStore:
 def __init__(self,root,allowed_roots=None):self.root=Path(root).resolve();self.root.mkdir(parents=True,exist_ok=True);self.allowed=[Path(x).resolve() for x in (allowed_roots or [self.root])];self.index={};self._load()
 def _load(self):
  p=self.root/'index.json'
  if p.exists():
   try:self.index=json.loads(p.read_text())
   except Exception:self.index={}
 def _save(self):(self.root/'index.json').write_text(json.dumps(self.index,indent=2))
 def validate_read(self,path):
  p=Path(path).resolve()
  if not any(p==r or r in p.parents for r in self.allowed):raise PermissionError(f'Path outside allowed roots: {p}')
  if not p.is_file():raise FileNotFoundError(p)
  return p
 def create_path(self,suffix):return self.root/(str(uuid.uuid4())+suffix)
 def register(self,path,kind,producer='',parents=None,metadata=None):
  p=Path(path).resolve()
  if not (p==self.root or self.root in p.parents):raise PermissionError('Outputs must be in artifact store')
  a=Artifact(str(uuid.uuid4()),kind,str(p),mimetypes.guess_type(p.name)[0] or 'application/octet-stream',metadata or {},producer=producer,parents=parents or []);self.index[a.id]=a.__dict__;self._save();return a
 def import_file(self,path):
  src=self.validate_read(path);dst=self.create_path(src.suffix.lower());shutil.copy2(src,dst);return self.register(dst,'image' if src.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.bmp','.tif','.tiff'} else 'file','import')
 def get(self,aid):
  if aid not in self.index:raise KeyError(aid)
  return Artifact(**self.index[aid])
