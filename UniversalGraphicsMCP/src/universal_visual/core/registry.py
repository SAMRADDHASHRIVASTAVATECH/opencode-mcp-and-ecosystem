from __future__ import annotations
import importlib.metadata
from .types import Capability
class Registry:
 def __init__(self,adapters):self.adapters=adapters;self.map={};self.refresh()
 def refresh(self):
  self.map={}
  for a in self.adapters:
   for c in a.capabilities():self.map.setdefault(c,[]).append(a)
 def discover(self,name=''):
  return [Capability(c,a.name,True,['artifact'],['artifact'],reason='registered adapter').__dict__ for c,aa in self.map.items() for a in aa if not name or name.lower() in c.lower()]
 def resolve(self,op,preferred=None):
  aa=self.map.get(op,[])
  if preferred:aa=[x for x in aa if x.name==preferred]
  if not aa:raise LookupError(f'No available adapter for {op}')
  return aa[0]
