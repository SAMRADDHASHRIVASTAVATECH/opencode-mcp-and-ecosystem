class OpenCVAdapter:
 name='opencv'
 def __init__(self):
  try:import cv2;self.cv=cv2;self.available=True
  except Exception:self.available=False
 def capabilities(self):return ['vision.edges','vision.contours','vision.features','vision.changed_regions','vision.track_template'] if self.available else []
 def run(self,op,inputs,p,store):
  cv=self.cv;im=cv.imread(store.get(inputs[0]).path)
  if im is None:raise ValueError('decode failed')
  data={};out=store.create_path('.png')
  if op=='vision.edges':result=cv.Canny(cv.cvtColor(im,cv.COLOR_BGR2GRAY),int(p.get('low',80)),int(p.get('high',160)))
  elif op=='vision.contours':
   g=cv.cvtColor(im,cv.COLOR_BGR2GRAY);_,b=cv.threshold(g,int(p.get('threshold',128)),255,cv.THRESH_BINARY);cs,_=cv.findContours(b,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE);result=im.copy();cv.drawContours(result,cs,-1,(0,255,0),2);data={'contours':[{'area':cv.contourArea(c),'perimeter':cv.arcLength(c,True),'bbox':cv.boundingRect(c)} for c in cs[:1000]]}
  elif op=='vision.features':
   orb=cv.ORB_create(int(p.get('max_features',500)));k,d=orb.detectAndCompute(cv.cvtColor(im,cv.COLOR_BGR2GRAY),None);result=cv.drawKeypoints(im,k,None,color=(0,255,0));data={'keypoints':[{'x':x.pt[0],'y':x.pt[1],'size':x.size,'angle':x.angle,'response':x.response} for x in k]}
  elif op=='vision.changed_regions':
   other=cv.imread(store.get(inputs[1]).path);other=cv.resize(other,(im.shape[1],im.shape[0]));delta=cv.absdiff(im,other);g=cv.cvtColor(delta,cv.COLOR_BGR2GRAY);_,mask=cv.threshold(g,int(p.get('threshold',20)),255,cv.THRESH_BINARY);mask=cv.dilate(mask,None,iterations=int(p.get('dilate',2)));cs,_=cv.findContours(mask,cv.RETR_EXTERNAL,cv.CHAIN_APPROX_SIMPLE);boxes=[cv.boundingRect(c) for c in cs if cv.contourArea(c)>=float(p.get('min_area',16))];result=other.copy();[cv.rectangle(result,(x,y),(x+w,y+h),(0,0,255),2) for x,y,w,h in boxes];data={'regions':[{'x':x,'y':y,'width':w,'height':h} for x,y,w,h in boxes]}
  elif op=='vision.track_template':
   template=cv.imread(store.get(inputs[1]).path);score=cv.matchTemplate(im,template,cv.TM_CCOEFF_NORMED);_,mx,_,loc=cv.minMaxLoc(score);h,w=template.shape[:2];result=im.copy();cv.rectangle(result,loc,(loc[0]+w,loc[1]+h),(255,0,255),2);data={'x':loc[0],'y':loc[1],'width':w,'height':h,'confidence':float(mx)}
  else:raise ValueError('Unsupported OpenCV operation')
  cv.imwrite(str(out),result);a=store.register(out,'image',self.name,inputs,{'operation':op});return [a],data
