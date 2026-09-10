"""OLCAP context: assembles all subsystems for the MCP server."""
from __future__ import annotations

from pathlib import Path

from .config import Settings, load_settings
from .hardware.profiler import detect
from .hardware.profile import Profile
from .models.registry import ModelRegistry
from .models.catalog import catalog
from .models.selector import Selector
from .memory.manager import MemoryManager
from .jobs import JobManager
from .storage import StorageManager
from .generation.service import ImageService
from .runtimes.comfy_runtime import ComfyRuntime
from .backends.diffusers_backend import DiffusersBackend
from .backends.demo_backend import DemoBackend


class Context:
    def __init__(self, state_dir: str = ""):
        self.settings: Settings = load_settings(state_dir)
        self.profile: Profile = detect()
        self.registry = ModelRegistry(str(self.settings.registry_path()))
        self.catalog = catalog()
        self.selector = Selector(self.registry,
                                 str(self.settings.selection_cache_path()))
        self.memory = MemoryManager(self.profile)
        self.jobs = JobManager()
        self.storage = StorageManager(self.settings)

        self.comfy = ComfyRuntime(self.settings)
        self.demo = DemoBackend()
        self.diffusers = DiffusersBackend(str(self.settings.resolved_models_dir()))

        self.service = ImageService(self)
        self._seed_default_workflows()

    def _seed_default_workflows(self) -> None:
        """Copy packaged ComfyUI workflow templates into the state workflows dir."""
        import shutil
        src_dir = Path(__file__).parent / "workflows"
        dst = self.settings.resolved_workflows_dir()
        dst.mkdir(parents=True, exist_ok=True)
        if src_dir.is_dir():
            for f in src_dir.glob("*.json"):
                out = dst / f.name
                if not out.exists():
                    shutil.copy2(f, out)

    def refresh_hardware(self) -> Profile:
        self.profile = detect()
        self.memory = MemoryManager(self.profile)
        return self.profile

    def available_backends(self, *, include_demo: bool = False) -> list:
        out = []
        if self.settings.backend in ("auto", "comfyui"):
            if self.comfy.health():
                from .runtimes.comfy_runtime import ComfyBackend
                out.append(ComfyBackend(self.comfy,
                                        str(self.settings.resolved_workflows_dir())))
        if self.settings.backend in ("auto", "diffusers"):
            if self.diffusers.probe().get("available"):
                out.append(self.diffusers)
        if include_demo or self.settings.backend == "demo":
            out.append(self.demo)
        return out
