from typing import Literal
from pydantic import BaseModel,Field
class TargetRequest(BaseModel):
 target:str;goal:str='understand structure and recover source where possible';depth:Literal['quick','normal','deep','extreme']='normal';output_directory:str|None=None;preferred_language:str|None=None;analysis_mode:Literal['static']='static';recursive:bool=True
class ToolRecord(BaseModel):
 id:str;name:str;version:str|None=None;source:str;installed:bool=False;executable:str|None=None;capabilities:list[str]=[];formats:list[str]=[];architectures:list[str]=[];languages:list[str]=[];install:dict|None=None;health:Literal['ok','missing','unknown','broken']='unknown';notes:list[str]=[]
