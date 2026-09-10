from __future__ import annotations
from dataclasses import dataclass,field,asdict
from enum import Enum
from typing import Any
import time,uuid
class RuntimeStatus(str,Enum): STOPPED='stopped';RUNNING='running';PAUSED='paused';SAFE_IDLE='safe_idle'
class Risk(str,Enum): R0='internal';R1='read_only';R2='reversible_local';R3='consequential';R4='high_impact'
@dataclass
class Affect:
 valence:float=.55;arousal:float=.25;confidence:float=.55;load:float=.1;fatigue:float=.05;frustration:float=0.;curiosity:float=.6;social:float=.5;control:float=.6;urgency:float=0.;risk:float=0.;mode:str='CALM';causes:list[str]=field(default_factory=list);updated_at:float=field(default_factory=time.time)
@dataclass
class Goal:
 id:str=field(default_factory=lambda:str(uuid.uuid4()));text:str='';owner:str='user';origin:str='user';type:str='task';desired_state:str='';priority:int=50;status:str='proposed';created_at:float=field(default_factory=time.time);deadline:float|None=None;dependencies:list[str]=field(default_factory=list);privacy_class:str='private';required_capabilities:list[str]=field(default_factory=list);success:str='';failure:str='';cancellation_policy:str='user_or_safety';risk_ceiling:str='reversible_local';budget_seconds:int=900
@dataclass
class Approval:
 id:str=field(default_factory=lambda:str(uuid.uuid4()));summary:str='';risk:str='reversible_local';scope:dict[str,Any]=field(default_factory=dict);status:str='pending';created_at:float=field(default_factory=time.time);expires_at:float=0.
@dataclass
class State:
 status:RuntimeStatus=RuntimeStatus.STOPPED;identity_name:str='Companion';affect:Affect=field(default_factory=Affect);active_goal:Goal|None=None;intention:str='';activity:str='idle';last_event:str='';started_at:float=0.;tick:int=0;quiet:bool=False;pending_approvals:list[Approval]=field(default_factory=list);errors:list[str]=field(default_factory=list)
def obj(x):
 if hasattr(x,'__dataclass_fields__'):return {k:obj(v) for k,v in asdict(x).items()}
 if isinstance(x,Enum):return x.value
 if isinstance(x,list):return [obj(v) for v in x]
 if isinstance(x,dict):return {k:obj(v) for k,v in x.items()}
 return x
