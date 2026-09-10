from __future__ import annotations
from PIL import Image
import numpy as np
class Critic:
 def analyze(self,path):
  im=Image.open(path).convert('RGB');a=np.asarray(im,dtype=np.float32)/255;lum=.2126*a[:,:,0]+.7152*a[:,:,1]+.0722*a[:,:,2];gy,gx=np.gradient(lum);edges=np.hypot(gx,gy);h,w=lum.shape;thirds=[float(edges[:,max(0,int(w*t)-2):min(w,int(w*t)+2)].mean()) for t in (1/3,2/3)]+[float(edges[max(0,int(h*t)-2):min(h,int(h*t)+2),:].mean()) for t in (1/3,2/3)];sat=(a.max(2)-a.min(2));issues=[]
  if lum.std()<.08:issues.append({'severity':'warning','code':'low_contrast','suggestion':'Increase value separation at the focal hierarchy.'})
  if edges.mean()<.01:issues.append({'severity':'info','code':'low_detail','suggestion':'Check whether sparse detail is intentional.'})
  if sat.mean()>.75:issues.append({'severity':'info','code':'high_saturation','suggestion':'Reserve strongest chroma for focal elements.'})
  return {'schema':'artist.critique/1','dimensions':[w,h],'metrics':{'mean_luminance':float(lum.mean()),'contrast':float(lum.std()),'edge_density':float((edges>.08).mean()),'mean_saturation':float(sat.mean()),'thirds_energy':thirds},'issues':issues,'note':'Heuristic technical critique; semantic/aesthetic judgment should combine brief, artwork state and visual reasoning.'}
