from __future__ import annotations
import math,time
class TrajectoryEngine:
 def generate(self,points,brush=None,duration_ms=None,max_step=3.0,seed=0):
  if len(points)<2:raise ValueError('At least two points required')
  out=[];dist=sum(math.dist(points[i-1][:2],points[i][:2]) for i in range(1,len(points)));duration_ms=duration_ms or max(120,min(8000,dist*2.2));elapsed=0.
  for i in range(1,len(points)):
   a,b=points[i-1],points[i];seg=math.dist(a[:2],b[:2]);n=max(1,math.ceil(seg/max_step))
   for j in range(n):
    t=j/n;s=t*t*(3-2*t);x=a[0]+(b[0]-a[0])*s;y=a[1]+(b[1]-a[1])*s;pressure=(a[2] if len(a)>2 else .65)+(b[2]-a[2])*s if len(a)>2 and len(b)>2 else .65;out.append({'x':round(x,3),'y':round(y,3),'pressure':round(max(0,min(1,pressure)),3),'t_ms':round(elapsed) });elapsed+=duration_ms*seg/max(dist,1)/n
  b=points[-1];out.append({'x':b[0],'y':b[1],'pressure':b[2] if len(b)>2 else .4,'t_ms':round(duration_ms)})
  return {'schema':'artist.trajectory/1','coordinate_space':'canvas_physical_pixels','brush':brush or {},'samples':out,'duration_ms':duration_ms,'safety':{'button':'primary','release_on_abort':True,'bounds_required':True}}
