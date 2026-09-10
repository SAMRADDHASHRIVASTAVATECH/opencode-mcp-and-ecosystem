from pathlib import Path
from .core.state import ArtworkStore
from .core.planner import ArtistPlanner
from .core.trajectory import TrajectoryEngine
from .core.qa import Critic
from .core.control import envelope
from .adapters.apps import ApplicationRegistry
from .core.domains import DomainKnowledge
class ArtistRuntime:
 def __init__(self,root=None):
  root=Path(root or Path.home()/'.universal-artist');root.mkdir(parents=True,exist_ok=True);self.root=root;self.store=ArtworkStore(root/'artwork.sqlite3');self.planner=ArtistPlanner();self.trajectory=TrajectoryEngine();self.critic=Critic();self.apps=ApplicationRegistry();self.domains=DomainKnowledge()
