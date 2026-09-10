"""Backend abstraction.

The MCP layer is backend-agnostic. A backend executes an image operation and
returns an ImageResult. Different backends (ComfyUI, diffusers, future runtimes)
implement this interface. The system never fabricates an image: if a real
backend + model is not available the operation raises a typed error.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class ImageResult:
    path: str                       # validated local file path
    width: int
    height: int
    format: str
    backend: str
    model: str
    quant: str | None = None
    seed: int | None = None
    generation_s: float | None = None
    metadata: dict = field(default_factory=dict)
    staged: str | None = None       # pipeline stage when result is intermediate

    def to_dict(self, *, include_path: bool = True) -> dict:
        d = {"success": True, "backend": self.backend, "model": self.model,
             "quant": self.quant, "seed": self.seed, "format": self.format,
             "width": self.width, "height": self.height,
             "generation_s": round(self.generation_s, 2)
             if self.generation_s else None,
             "metadata": self.metadata}
        if include_path:
            d["output"] = {"path": self.path, "width": self.width,
                           "height": self.height}
        return d


class Backend(ABC):
    name = "base"
    display = "Base"

    @abstractmethod
    def probe(self) -> dict:
        """Detect availability/version. Returns {available: bool, ...}."""

    @abstractmethod
    def supports_family(self, family_id: str) -> bool: ...

    def generate(self, plan) -> ImageResult:
        raise NotImplementedError

    def image_to_image(self, plan) -> ImageResult:
        raise NotImplementedError

    def inpaint(self, plan) -> ImageResult:
        raise NotImplementedError

    def upscale(self, plan) -> ImageResult:
        raise NotImplementedError

    def cancel(self) -> None:
        pass
