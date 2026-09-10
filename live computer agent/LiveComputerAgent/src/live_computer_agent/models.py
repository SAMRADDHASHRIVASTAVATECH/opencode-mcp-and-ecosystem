from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any
import time, uuid
class Status(str,Enum): IDLE='idle';RUNNING='running';PAUSED='paused';STOPPED='stopped';ERROR='error'
class Mode(str,Enum): DIRECT='direct';ASSISTED='assisted';AUTONOMOUS='autonomous'
@dataclass
class Bounds:
 x:int;y:int;width:int;height:int
 @property
 def center(self): return (self.x+self.width//2,self.y+self.height//2)
@dataclass
class WindowInfo:
 hwnd:int=0; title:str=''; application:str=''; process_id:int=0; bounds:Bounds=field(default_factory=lambda:Bounds(0,0,0,0)); focused:bool=False; monitor:int=0
@dataclass
class Element:
 id:str; role:str; name:str=''; bounds:Bounds=field(default_factory=lambda:Bounds(0,0,0,0)); confidence:float=1.; source:str='uia'; enabled:bool=True; metadata:dict[str,Any]=field(default_factory=dict)
@dataclass
class Frame:
 id:str; timestamp:float; image:Any; width:int;height:int; changed:bool=True; change_ratio:float=1.; target:str='desktop'
@dataclass
class ScreenState:
 revision:int=0;timestamp:float=field(default_factory=time.time);frame_id:str='';window:WindowInfo=field(default_factory=WindowInfo);elements:list[Element]=field(default_factory=list);text:list[dict[str,Any]]=field(default_factory=list);objects:list[dict[str,Any]]=field(default_factory=list);cursor:dict[str,Any]=field(default_factory=dict);confidence:float=0.;provenance:list[str]=field(default_factory=list);metrics:dict[str,float]=field(default_factory=dict)
@dataclass
class ActionResult:
 id:str=field(default_factory=lambda:str(uuid.uuid4())); action:str='';status:str='uncertain';message:str='';started_at:float=field(default_factory=time.time);ended_at:float=0.;before_revision:int=0;after_revision:int=0;verified:bool=False;evidence:dict[str,Any]=field(default_factory=dict)
 def finish(self,status,message='',verified=False,**evidence): self.status=status;self.message=message;self.verified=verified;self.evidence=evidence;self.ended_at=time.time();return self
@dataclass
class AgentState:
 session_id:str='';status:Status=Status.IDLE;mode:Mode=Mode.DIRECT;goal:str|None=None;subgoal:str|None=None;screen:ScreenState=field(default_factory=ScreenState);last_actions:list[ActionResult]=field(default_factory=list);errors:list[str]=field(default_factory=list);started_at:float=0.;paused_at:float=0.
def serial(obj):
 if hasattr(obj,'__dataclass_fields__'): return {k:serial(v) for k,v in asdict(obj).items()}
 if isinstance(obj,Enum):return obj.value
 if isinstance(obj,list):return [serial(v) for v in obj]
 if isinstance(obj,dict):return {k:serial(v) for k,v in obj.items()}
 return obj
