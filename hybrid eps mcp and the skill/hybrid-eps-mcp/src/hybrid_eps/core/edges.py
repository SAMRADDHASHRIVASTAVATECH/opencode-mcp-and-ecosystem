import cv2,numpy as np
from ..models import EdgeSettings,VectorSettings
def normalize(x):
 m=float(np.max(np.abs(x)));return np.zeros(x.shape,np.uint8) if m<=1e-12 else np.clip(np.abs(x)*255/m,0,255).astype(np.uint8)
def detect(rgb:np.ndarray,s:EdgeSettings):
 gray=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY);gray=cv2.GaussianBlur(gray,(s.blur_kernel,s.blur_kernel),0)
 if s.method=='canny':e=cv2.Canny(gray,s.canny_low,s.canny_high,L2gradient=True)
 elif s.method=='sobel':e=normalize(cv2.magnitude(cv2.Sobel(gray,cv2.CV_32F,1,0,ksize=3),cv2.Sobel(gray,cv2.CV_32F,0,1,ksize=3)))
 elif s.method=='scharr':e=normalize(cv2.magnitude(cv2.Scharr(gray,cv2.CV_32F,1,0),cv2.Scharr(gray,cv2.CV_32F,0,1)))
 else:e=normalize(cv2.Laplacian(gray,cv2.CV_32F,ksize=3))
 if s.morphology!='none':
  k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(s.morph_kernel,s.morph_kernel));op={'close':cv2.MORPH_CLOSE,'open':cv2.MORPH_OPEN,'dilate':cv2.MORPH_DILATE,'erode':cv2.MORPH_ERODE}[s.morphology];e=cv2.morphologyEx(e,op,k)
 if s.invert:e=255-e
 return e
def contours(edge:np.ndarray,s:VectorSettings):
 mode={'external':cv2.RETR_EXTERNAL,'list':cv2.RETR_LIST,'tree':cv2.RETR_TREE,'ccomp':cv2.RETR_CCOMP}[s.retrieval];cs,h=cv2.findContours((edge>0).astype(np.uint8),mode,cv2.CHAIN_APPROX_SIMPLE);out=[]
 for c in sorted(cs,key=cv2.contourArea,reverse=True):
  if cv2.contourArea(c)<s.min_area:continue
  eps=s.simplify_epsilon*cv2.arcLength(c,True);a=cv2.approxPolyDP(c,eps,True).reshape(-1,2)
  if len(a)>=2:out.append(a.tolist())
  if len(out)>=s.max_contours:break
 return out,h.tolist() if h is not None else None
def stats(edge,paths):
 n,_,st,_=cv2.connectedComponentsWithStats((edge>0).astype(np.uint8),8);pixels=int(np.count_nonzero(edge));return {'edge_pixels':pixels,'edge_density':pixels/edge.size,'components':max(0,n-1),'contours':len(paths),'vertices':sum(len(x) for x in paths),'component_areas':sorted([int(x[cv2.CC_STAT_AREA]) for x in st[1:]],reverse=True)[:100]}
