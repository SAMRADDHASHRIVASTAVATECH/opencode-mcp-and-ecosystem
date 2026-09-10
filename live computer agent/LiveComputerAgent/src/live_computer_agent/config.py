from __future__ import annotations
from dataclasses import dataclass,field
from pathlib import Path
import json,os
@dataclass
class Config:
 capture_fps:float=20.; perception_fps:float=2.; window_poll_fps:float=5.; reasoning_fps:float=.2
 capture_backend:str='auto'; capture_target:str='desktop'; monitor:int=0; change_threshold:float=.002
 ocr_provider:str='auto'; uia_enabled:bool=True; vision_provider:str='none'; planner_provider:str='none'
 safe_mode:bool=True; require_focus:bool=True; allow_process_launch:bool=False; allow_clipboard:bool=False
 action_timeout:float=5.; verification_delay:float=.35; max_autonomous_steps:int=30
 emergency_hotkey:str='ctrl+alt+pause'; persistent_memory:bool=False; retain_screenshots:bool=False
 runtime_dir:str='runtime'; log_level:str='INFO'; allowed_apps:list[str]=field(default_factory=list); denied_apps:list[str]=field(default_factory=list)
 @classmethod
 def load(cls,path=None):
  path=path or os.getenv('LCA_CONFIG','config/default.json'); data={}
  p=Path(path)
  if p.exists():data=json.loads(p.read_text(encoding='utf-8'))
  return cls(**{k:v for k,v in data.items() if k in cls.__dataclass_fields__})
