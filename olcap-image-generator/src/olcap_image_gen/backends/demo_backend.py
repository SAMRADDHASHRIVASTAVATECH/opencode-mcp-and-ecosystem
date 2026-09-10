"""Demo backend: deterministic, clearly-labelled test images.

Used ONLY by self_test / diagnostics to prove the full pipeline (params -> job ->
backend -> file -> metadata) works on any machine (even CPU-only, no GPU). It is
NOT an AI generation backend. Its outputs are plain labelled test fixtures and
are never returned from the real `generate_image` tools as if they were
AI-generated. Those tools route to real backends and fail honestly if none is
available.
"""
from __future__ import annotations

from pathlib import Path

from .base import Backend, ImageResult
from ..errors import NotAuthorized


class DemoBackend(Backend):
    name = "demo"
    display = "Demo test fixture backend (no AI)"

    def __init__(self):
        self._allow = False

    def allow(self, ok: bool = True):
        self._allow = ok

    def probe(self) -> dict:
        return {"available": True, "demo": True,
                "note": "produces labelled test fixtures only; not an AI backend"}

    def supports_family(self, family_id: str) -> bool:
        return True

    def _guard(self):
        if not self._allow:
            raise NotAuthorized(
                "demo backend is restricted to self_test/diagnostics; real "
                "generation requires an installed AI model + backend.")

    def generate(self, plan) -> ImageResult:
        self._guard()
        return self._make(plan)

    def image_to_image(self, plan):
        self._guard()
        return self._make(plan)

    def inpaint(self, plan):
        self._guard()
        return self._make(plan)

    def upscale(self, plan):
        self._guard()
        return self._make(plan)

    def _make(self, plan) -> ImageResult:
        from PIL import Image, ImageDraw
        w, h = plan.params.get("width", 256), plan.params.get("height", 256)
        img = Image.new("RGB", (w, h))
        for y in range(h):
            for x in range(w):
                img.putpixel((x, y),
                             (int(255 * x / max(w - 1, 1)),
                              int(255 * y / max(h - 1, 1)), 80))
        d = ImageDraw.Draw(img)
        d.text((8, 8), "OLCAP DEMO TEST IMAGE (not AI-generated)", fill=(255, 255, 255))
        d.text((8, h - 24), f"model={plan.model} seed={plan.params.get('seed')}",
               fill=(255, 255, 255))
        outdir = Path(plan.output_dir)
        outdir.mkdir(parents=True, exist_ok=True)
        path = outdir / (plan.filename or f"{plan.job_id}.png")
        img.save(path, format="PNG")
        return ImageResult(path=str(path), width=w, height=h, format="png",
                           backend=self.name, model=plan.model,
                           quant=plan.quant, seed=plan.params.get("seed"),
                           generation_s=0.01,
                           metadata={"demo": True,
                                     "note": "test fixture; not an AI image"})
