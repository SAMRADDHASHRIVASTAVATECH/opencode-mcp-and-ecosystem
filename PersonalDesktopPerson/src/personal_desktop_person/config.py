from dataclasses import dataclass,field
from pathlib import Path
import json,os
@dataclass
class Config:
 data_dir:str='runtime'; cognitive_hz:float=2.; avatar_host:str='127.0.0.1';avatar_port:int=8765;avatar_enabled:bool=True
 provider_url:str='';provider_model:str='';provider_key_env:str='PDP_API_KEY';provider_timeout:int=60
 retention_days:int=365;store_dialogue:bool=True;quiet_hours:list[int]=field(default_factory=lambda:[23,7]);computer_use_server:str='open_computer_use';conservative:bool=True
 desktop_sensor_enabled:bool=False;screen_change_enabled:bool=False;accessibility_enabled:bool=True;desktop_poll_seconds:float=1.;meaningful_change_threshold:float=.08;semantic_environment_reasoning:bool=True
 @classmethod
 def load(cls,path=None):
  p=Path(path or os.getenv('PDP_CONFIG','config/default.json'));d=json.loads(p.read_text()) if p.exists() else {}
  unknown=set(d)-set(cls.__dataclass_fields__)
  if unknown:raise ValueError('Unknown configuration keys: '+','.join(sorted(unknown)))
  c=cls(**d)
  if not .1<=c.cognitive_hz<=20:raise ValueError('cognitive_hz must be 0.1..20')
  if c.avatar_host not in ('127.0.0.1','localhost'):raise ValueError('avatar must bind to loopback')
  if not 1024<=c.avatar_port<=65535:raise ValueError('invalid avatar_port')
  if not c.conservative:raise ValueError('this release requires conservative=true')
  return c
