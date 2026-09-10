from typing import Literal
from pydantic import BaseModel,Field,model_validator
class EdgeSettings(BaseModel):
 method:Literal['canny','sobel','laplacian','scharr']='canny';canny_low:int=Field(100,ge=0,le=255);canny_high:int=Field(200,ge=0,le=255);blur_kernel:int=Field(3,ge=1,le=31);morphology:Literal['none','close','open','dilate','erode']='none';morph_kernel:int=Field(3,ge=1,le=15);invert:bool=False
 @model_validator(mode='after')
 def valid(self):
  if self.blur_kernel%2==0 or self.morph_kernel%2==0:raise ValueError('kernels must be odd')
  if self.canny_low>=self.canny_high:raise ValueError('canny_low must be below canny_high')
  return self
class VectorSettings(BaseModel):
 simplify_epsilon:float=Field(.002,ge=0,le=.1);min_area:float=Field(2,ge=0);retrieval:Literal['external','list','tree','ccomp']='list';max_contours:int=Field(10000,ge=1,le=100000)
class ExportSettings(BaseModel):
 dpi:int=Field(300,ge=72,le=1200);edge_color:str=Field('#00FFFF',pattern=r'^#[0-9A-Fa-f]{6}$');edge_width:float=Field(.35,gt=0,le=20);include_bitmap:bool=True;include_vectors:bool=True;output_format:Literal['eps','pdf','svg','png']='eps';transparent:bool=False
 @model_validator(mode='after')
 def layer(self):
  if not(self.include_bitmap or self.include_vectors):raise ValueError('at least one layer required')
  return self
