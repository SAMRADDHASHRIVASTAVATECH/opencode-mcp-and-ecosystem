"""Model knowledge base.

Each model family entry carries documented/estimated traits used by the
selection engine. Approx sizes are labelled as estimates; real feasibility is
confirmed by install+verify+benchmark, never by static claim alone. Newer or
asset-variable families are flagged `provenance: "verify"` so the installer
validates the actual downloadable asset rather than assuming a URL.

Download sizes and exact asset URLs are NOT hard-coded as universal truth: the
installer resolves and verifies real sources.
"""
from __future__ import annotations

# approximation of on-disk / in-RAM size for the primary weights per quant family
_QUANT_SIZES = {
    "fp16": 1.0, "bf16": 1.0, "fp8": 0.5, "q8": 0.28, "q6": 0.22,
    "q5": 0.19, "q4": 0.16, "q3": 0.12, "q2": 0.09,
}


class ModelFamily:
    def __init__(self, *, id, name, params_b, quality, photorealism,
                 prompt_adherence, text_rendering, license,
                 capabilities, backends, base_quant_size_gb, notes=""):
        self.id = id
        self.name = name
        self.params_b = params_b
        self.quality = quality
        self.photorealism = photorealism
        self.prompt_adherence = prompt_adherence
        self.text_rendering = text_rendering
        self.license = license
        self.capabilities = capabilities
        self.backends = backends
        self.base_quant_size_gb = base_quant_size_gb
        self.notes = notes

    def quant_sizes(self) -> dict:
        if self.params_b <= 0:
            return {"fp16": self.base_quant_size_gb}
        base = max(self.base_quant_size_gb, self.params_b * 1.8)
        out = {}
        for q, rel in _QUANT_SIZES.items():
            out[q] = round(base * _QUANT_REL.get(q, 1.0), 2)
        return out

    def to_dict(self):
        return {"id": self.id, "name": self.name, "params_b": self.params_b,
                "quality": self.quality,
                "photorealism": self.photorealism,
                "prompt_adherence": self.prompt_adherence,
                "text_rendering": self.text_rendering, "license": self.license,
                "capabilities": self.capabilities, "backends": self.backends,
                "approx_sizes_gb": self.quant_sizes(), "notes": self.notes}


# relative weight size to full fp16
_QUANT_REL = {"fp16": 1.0, "bf16": 1.0, "fp8": 0.5, "q8": 0.28, "q6": 0.22,
              "q5": 0.19, "q4": 0.16, "q3": 0.12, "q2": 0.09}

# Ordered list of quant codes from highest to lowest quality.
QUANT_QUALITY_ORDER = ["fp16", "bf16", "fp8", "q8", "q6", "q5", "q4", "q3",
                       "q2"]


def _mk(id, name, pb, quality, pr, pa, tr, lic, caps, backends, ref, notes=""):
    return ModelFamily(id=id, name=name, params_b=pb, quality=quality,
                       photorealism=pr, prompt_adherence=pa, text_rendering=tr,
                       license=lic, capabilities=caps, backends=backends,
                       base_quant_size_gb=ref, notes=notes)


def catalog() -> dict[str, ModelFamily]:
    fam = {}
    t2i = ["text_to_image"]
    img2 = t2i + ["image_to_image"]
    full = img2 + ["editing", "inpaint"]
    fam["flux.1-dev"] = _mk(
        "flux.1-dev", "FLUX.1-dev", 12, quality=9, pr=8, pa=9, tr=9,
        lic="FLUX.1 [dev] Non-Commercial License",
        caps=t2i + ["image_to_image", "editing"],
        backends=["comfyui", "diffusers"], ref=23.8,
        notes="High quality open dev weights; 12B requires heavy offload on 4GB.")
    fam["flux.1-schnell"] = _mk(
        "flux.1-schnell", "FLUX.1-schnell", 12, quality=8, pr=8, pa=8, tr=9,
        lic="Apache-2.0",
        caps=img2, backends=["comfyui", "diffusers"], ref=23.8,
        notes="Apache-licensed; fewer steps.")
    fam["flux.2"] = _mk(
        "flux.2", "FLUX.2", 12, quality=9, pr=8, pa=9, tr=9,
        lic="proprietary/open-check", caps=full, backends=["comfyui"], ref=24.0,
        notes="Verify exact available asset/licence before install.")
    fam["flux.2-klein"] = _mk(
        "flux.2-klein", "FLUX.2 Klein", 4, quality=8, pr=8, pa=8, tr=8,
        lic="proprietary/open-check", caps=full, backends=["comfyui"], ref=7.5,
        notes="~4B candidate well suited to low VRAM when an asset is available "
              "and licensed for local use.")
    fam["qwen-image"] = _mk(
        "qwen-image", "Qwen-Image", 20, quality=8, pr=8, pa=9, tr=9,
        lic="Apache-2.0", caps=full, backends=["comfyui"], ref=40.0,
        notes="Large; verify asset + quantized availability.")
    fam["z-image"] = _mk(
        "z-image", "Z-Image", 4, quality=7, pr=7, pa=8, tr=7,
        lic="Apache-2.0", caps=t2i + ["image_to_image"], backends=["comfyui"],
        ref=7.5, notes="Verify asset availability.")
    fam["hunyuan-image"] = _mk(
        "hunyuan-image", "Hunyuan Image", 13, quality=8, pr=8, pa=8, tr=7,
        lic="Tencent", caps=full, backends=["comfyui"], ref=24.0,
        notes="Verify exact asset.")
    fam["sdxl"] = _mk(
        "sdxl", "SDXL", 3.5, quality=7, pr=8, pa=7, tr=4, lic="OpenRAIL++",
        caps=img2 + ["inpaint"], backends=["comfyui", "diffusers"], ref=6.9,
        notes="Runs comfortably on 4GB with offload.")
    fam["sd1.5"] = _mk(
        "sd1.5", "Stable Diffusion 1.5", 0.9, quality=5, pr=6, pa=5, tr=2,
        lic="CreativeML OpenRAIL-M", caps=img2 + ["inpaint"],
        backends=["comfyui", "diffusers"], ref=3.8,
        notes="Lightest reliable option; lowest quality/text capability.")
    return fam


def best_quality_order() -> list[str]:
    return ["flux.2-klein", "flux.2", "flux.1-dev", "qwen-image",
            "hunyuan-image", "z-image", "sdxl", "sd1.5"]
