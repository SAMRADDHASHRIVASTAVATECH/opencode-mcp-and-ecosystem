from __future__ import annotations
from PIL import Image,ImageEnhance,ImageFilter,ImageOps,ImageDraw
import numpy as np,math
class PillowAdapter:
 name='pillow'
 def capabilities(self):return ['image.info','image.resize','image.crop','image.rotate','image.flip','image.filter','image.threshold','image.color_correct','image.composite','image.mask','image.draw','image.compare','image.measure','procedural.generate']
 def run(self,op,inputs,p,store):
  imgs=[Image.open(store.get(x).path).convert('RGBA') for x in inputs]
  out=store.create_path('.png');data={}
  if op=='image.info':
   im=imgs[0];return [],{'width':im.width,'height':im.height,'mode':im.mode,'bands':im.getbands()}
  if op=='image.resize':im=imgs[0].resize((int(p['width']),int(p['height'])),Image.Resampling.LANCZOS)
  elif op=='image.crop':im=imgs[0].crop(tuple(map(int,p['box'])))
  elif op=='image.rotate':im=imgs[0].rotate(float(p['angle']),expand=bool(p.get('expand',True)),resample=Image.Resampling.BICUBIC)
  elif op=='image.flip':im=ImageOps.mirror(imgs[0]) if p.get('axis','horizontal')=='horizontal' else ImageOps.flip(imgs[0])
  elif op=='image.filter':
   fs={'blur':ImageFilter.GaussianBlur(float(p.get('radius',2))),'sharpen':ImageFilter.SHARPEN,'edge':ImageFilter.FIND_EDGES};im=imgs[0].filter(fs[p['name']])
  elif op=='image.threshold':
   g=ImageOps.grayscale(imgs[0]);im=g.point(lambda x:255 if x>=int(p.get('value',128)) else 0).convert('RGBA')
  elif op=='image.color_correct':
   im=imgs[0];im=ImageEnhance.Brightness(im).enhance(float(p.get('brightness',1)));im=ImageEnhance.Contrast(im).enhance(float(p.get('contrast',1)));im=ImageEnhance.Color(im).enhance(float(p.get('saturation',1)))
  elif op=='image.composite':
   base=imgs[0];over=imgs[1];over=over.resize(base.size) if p.get('fit') else over;im=base.copy();im.alpha_composite(over,(int(p.get('x',0)),int(p.get('y',0))))
  elif op=='image.mask':im=Image.composite(imgs[0],Image.new('RGBA',imgs[0].size,tuple(p.get('background',[0,0,0,0]))),Image.open(store.get(inputs[1]).path).convert('L'))
  elif op=='image.draw':
   im=imgs[0].copy();d=ImageDraw.Draw(im);color=tuple(p.get('color',[0,0,0,255]));shape=p['shape'];box=tuple(p['box']);getattr(d,{'rectangle':'rectangle','ellipse':'ellipse','line':'line'}[shape])(box,fill=color if p.get('fill',True) else None,outline=color,width=int(p.get('width',1)))
  elif op=='image.compare':
   a=np.array(imgs[0].convert('RGB'),dtype=np.float32);b=np.array(imgs[1].resize(imgs[0].size).convert('RGB'),dtype=np.float32);mse=float(np.mean((a-b)**2));return [],{'mse':mse,'rmse':math.sqrt(mse),'similarity':max(0,1-mse/(255**2))}
  elif op=='image.measure':
   a=np.array(imgs[0].convert('RGB'));return [],{'mean_rgb':a.mean((0,1)).tolist(),'std_rgb':a.std((0,1)).tolist(),'min_rgb':a.min((0,1)).tolist(),'max_rgb':a.max((0,1)).tolist()}
  elif op=='procedural.generate':im=self._procedural(p)
  else:raise ValueError(op)
  im.save(out);a=store.register(out,'image',self.name,inputs,{'operation':op});return [a],data
 def _procedural(self,p):
  w,h=int(p.get('width',1024)),int(p.get('height',1024));kind=p.get('kind','gradient');im=Image.new('RGBA',(w,h));pix=im.load()
  if kind=='gradient':
   c1=p.get('color1',[10,20,60]);c2=p.get('color2',[230,100,120])
   for y in range(h):
    t=y/max(1,h-1);c=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3))+(255,)
    for x in range(w):pix[x,y]=c
  elif kind=='checker':
   n=int(p.get('size',32));c1=tuple(p.get('color1',[255,255,255]))+(255,);c2=tuple(p.get('color2',[0,0,0]))+(255,)
   for y in range(h):
    for x in range(w):pix[x,y]=c1 if (x//n+y//n)%2==0 else c2
  else:
   rng=np.random.default_rng(int(p.get('seed',0)));a=rng.integers(0,256,(h,w),dtype=np.uint8);im=Image.fromarray(a,'L').convert('RGBA')
  return im
