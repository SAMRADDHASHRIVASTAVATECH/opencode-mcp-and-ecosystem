from __future__ import annotations
from dataclasses import dataclass,field,asdict
from typing import Any
import time,uuid
@dataclass
class Artifact:
 id:str;kind:str;path:str;mime:str;metadata:dict[str,Any]=field(default_factory=dict);created_at:float=field(default_factory=time.time);producer:str='';parents:list[str]=field(default_factory=list)
@dataclass
class Capability:
 name:str;adapter:str;available:bool;inputs:list[str];outputs:list[str];device:str='cpu';cost:str='low';version:str='';reason:str=''
@dataclass
class NodeResult:
 node_id:str;status:str;artifacts:list[dict]=field(default_factory=list);data:dict=field(default_factory=dict);duration_ms:float=0.;error:str=''
def asdict_safe(x):return asdict(x) if hasattr(x,'__dataclass_fields__') else x
