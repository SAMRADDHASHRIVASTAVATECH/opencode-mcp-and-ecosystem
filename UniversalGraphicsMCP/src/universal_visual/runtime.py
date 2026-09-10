from pathlib import Path
from .core.store import ArtifactStore
from .core.registry import Registry
from .core.pipeline import Pipeline
from .adapters.pillow import PillowAdapter
from .adapters.opencv import OpenCVAdapter
from .adapters.svg import SVGAdapter
from .adapters.external import ExternalAdapter
from .adapters.system import SystemAdapter
from .core.domains import DomainCapabilityMap
class VisualRuntime:
 def __init__(self,root=None,allowed_roots=None):
  root=Path(root or Path.home()/'.universal-visual'/'artifacts');self.store=ArtifactStore(root,allowed_roots or [root,Path.cwd()]);self.system=SystemAdapter();self.registry=Registry([PillowAdapter(),OpenCVAdapter(),SVGAdapter(),ExternalAdapter()]);self.pipeline=Pipeline(self.registry,self.store);self.domains=DomainCapabilityMap()
 def capabilities(self,query=''):return self.registry.discover(query)
 def execute(self,graph):return self.pipeline.execute(graph)
