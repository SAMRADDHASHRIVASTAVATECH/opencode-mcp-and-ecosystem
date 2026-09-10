from pathlib import Path
from PIL import Image,ImageOps
import numpy as np,hashlib
Image.MAX_IMAGE_PIXELS=80_000_000
def load(path:Path):
 with Image.open(path) as probe:probe.verify()
 with Image.open(path) as im:
  im=ImageOps.exif_transpose(im);frames=getattr(im,'n_frames',1);fmt=im.format;info={'format':fmt,'mode':im.mode,'width':im.width,'height':im.height,'frames':frames,'has_alpha':'A' in im.getbands(),'icc_profile':bool(im.info.get('icc_profile')),'exif_entries':len(im.getexif())};rgb=im.convert('RGB').copy()
 info.update(path=str(path),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest());return rgb,np.asarray(rgb),info
