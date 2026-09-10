"""Image analysis for reconstruction suitability.

Reads a character image and reports objective facts (resolution, background
type, silhouette bounds, color complexity, symmetry, estimated facing) and a
suitability verdict. Background removal helpers are provided and only run when a
removal engine (rembg / opencv) is actually installed.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path

from .hardware import Hardware, detect_hardware


@dataclass
class ImageInfo:
    path: str
    width: int = 0
    height: int = 0
    mode: str = ""
    format: str = ""
    has_alpha: bool = False
    background_type: str = "unknown"     # solid | gradient | photo | transparent | busy
    silhouette_bbox: list | None = None  # [x0,y0,x1,y1] of non-bg content
    silhouette_fill: float = 0.0         # fraction of image occupied by content
    dominant_colors: list = field(default_factory=list)
    colorfulness: float = 0.0
    approx_facing: str = "unknown"       # front | frontish | side | back | unknown
    estimated_perspective: str = "unknown"
    warnings: list = field(default_factory=list)
    suitable_for_reconstruction: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


def load(path: str) -> tuple[Path, object]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    from PIL import Image
    im = Image.open(str(p))
    im.load()
    return p, im


def analyze(path: str) -> ImageInfo:
    p, im = load(path)
    import numpy as np
    info = ImageInfo(path=str(p), width=im.width, height=im.height,
                     mode=im.mode, format=(im.format or ""))
    rgba = _as_rgba(im, np)
    info.has_alpha = _has_transparency(im, np)
    info.background_type = _classify_background(rgba, np)
    bbox, fill = _content_bbox(rgba, np, info.background_type)
    info.silhouette_bbox = bbox
    info.silhouette_fill = fill
    info.colorfulness = _colorfulness(rgba, np)
    info.dominant_colors = _dominant(rgba, np, k=6)
    info.approx_facing = _facing(rgba, np, info.background_type)
    info.warnings = _warnings(info)
    info.suitable_for_reconstruction = (
        info.width >= 256 and info.height >= 256
        and info.silhouette_fill >= 0.03 and not _obviously_broken(info))
    return info


def _as_rgba(im, np) -> "np.ndarray":
    return np.asarray(im.convert("RGBA"), dtype="uint8")


def _has_transparency(im, np) -> bool:
    if im.mode in ("RGBA", "LA", "P"):
        a = np.asarray(im.convert("RGBA"))[..., 3]
        return bool((a < 250).any())
    return False


def _classify_background(rgba, np) -> str:
    rgb = rgba[..., :3].astype("int16")
    # sample border pixels
    h, w = rgba.shape[:2]
    border = np.concatenate([
        rgba[:max(1, h // 20)].reshape(-1, 4),
        rgba[-max(1, h // 20):].reshape(-1, 4),
        rgba[:, :max(1, w // 20)].reshape(-1, 4),
        rgba[:, -max(1, w // 20):].reshape(-1, 4)], axis=0)
    if border[:, 3].mean() < 200:
        return "transparent"
    if border[:, 3].mean() < 200:
        return "transparent"
    # Spatial uniformity: mean absolute deviation of each border pixel's colour
    # from the mean border colour (not per-channel spread, which is large for
    # any saturated fill).
    bg_colour = border[:, :3].mean(axis=0)
    dev = float(np.abs(border[:, :3] - bg_colour).mean())
    if dev < 18:
        return "solid"
    if dev < 60:
        return "gradient"
    return "photo"


def _bg_mask(rgba, np, bg_type) -> "np.ndarray":
    alpha = rgba[..., 3]
    if bg_type == "transparent":
        return alpha >= 250
    rgb = rgba[..., :3].astype("int16")
    # border average as proxy background colour
    h, w = rgba.shape[:2]
    m = int(max(1, min(h, w) * 0.02))
    border = rgba[:m].reshape(-1, 4)
    # sample 4 corners
    corners = [rgba[:m, :m], rgba[:m, -m:], rgba[-m:, :m], rgba[-m:, -m:]]
    corners = np.concatenate([c.reshape(-1, 4) for c in corners], axis=0)
    bg = corners[:, :3].mean(axis=0)
    dist = np.abs(rgb - bg).mean(axis=2)
    return dist > 40


def _content_bbox(rgba, np, bg_type) -> tuple[list, float]:
    if bg_type in ("solid", "gradient", "photo"):
        mask = _bg_mask(rgba, np, bg_type)
    else:
        mask = rgba[..., 3] >= 250
    content = ~mask
    h, w = content.shape
    fill = float(content.mean())
    ys, xs = np.where(content)
    if len(xs) == 0:
        return [0, 0, w - 1, h - 1], 0.0
    return [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())], fill


def _colorfulness(rgba, np) -> float:
    rgb = rgba[..., :3].astype("float32") / 255.0
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    rg = np.abs(r - g)
    yb = np.abs(0.5 * (r + g) - b)
    return float((rg.mean() + yb.mean()))


def _dominant(rgba, np, k: int) -> list:
    try:
        from sklearn.cluster import KMeans   # optional
        pts = rgba[..., :3].reshape(-1, 3)
        # subsample for speed
        if len(pts) > 20000:
            idx = np.random.RandomState(0).choice(len(pts), 20000, replace=False)
            pts = pts[idx]
        km = KMeans(n_clusters=k, n_init=1, random_state=0).fit(pts)
        counts = np.bincount(km.labels_, minlength=k)
        order = counts.argsort()[::-1]
        return [{"rgb": [int(c) for c in km.cluster_centers_[i]],
                 "share": float(counts[i] / counts.sum())} for i in order]
    except Exception:   # noqa: BLE001
        return []


def _facing(rgba, np, bg_type) -> str:
    """Rough symmetry heuristic: symmetric face-width => front-ish."""
    if bg_type == "transparent":
        a = rgba[..., 3]
    else:
        mask = _bg_mask(rgba, np, bg_type)
        a = np.where(mask, 0, 255).astype("uint8")
    h, w = a.shape
    # use upper half (head zone)
    half_h = int(h * 0.4)
    if half_h < 10:
        return "unknown"
    region = a[5:half_h, :]
    # content centre of mass x
    ys, xs = np.where(region > 0)
    if len(xs) == 0:
        return "unknown"
    cx = xs.mean()
    # symmetry: overlap of flipped content
    left = region[:, :w // 2]
    right = region[:, w // 2:]
    # compare horizontal distribution symmetry
    lc = (left > 0).sum()
    rc = (right > 0).sum()
    ratio = min(lc, rc) / max(lc, rc) if max(lc, rc) else 1
    if ratio > 0.85:
        return "front"
    if ratio > 0.6:
        return "frontish"
    if cx < w * 0.4:
        return "side"      # content biased to one side (profile)
    return "unknown"


def _warnings(info: ImageInfo) -> list:
    w = []
    if info.width < 256 or info.height < 256:
        w.append(f"Low resolution {info.width}x{info.height}; a sharper source "
                 "improves reconstruction.")
    if info.silhouette_fill < 0.03:
        w.append("Very little detected foreground; background removal or a "
                 "tighter crop recommended.")
    if info.background_type == "photo":
        w.append("Photo background detected; remove background before "
                 "reconstruction for best results.")
    if info.approx_facing == "side":
        w.append("Detected as a side/profile view; additional front or 3/4 "
                 "views will materially help reconstruction.")
    return w


def _obviously_broken(info: ImageInfo) -> bool:
    # e.g. all-one-colour / degenerate
    return info.colorfulness < 0.01


def remove_background(image_path: str, out_path: str,
                      method: str = "auto") -> dict:
    """Remove background using an available engine. Honest about availability.

    Returns {"ok": bool, "engine": ...}. Engines: 'rembg', 'opencv' (simple
    colour-key fallback), or 'none' -> not attempted.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    from PIL import Image
    p, im = load(image_path)
    rgba = im.convert("RGBA")
    import numpy as np
    arr = np.asarray(rgba)
    engine = None
    try:
        if method in ("auto", "rembg"):
            import rembg  # noqa: F401
            from rembg import remove as _rbg
            # attempt rembg (may need onnxruntime/models -> download)
            out = _rbg(rgba)
            engine = "rembg"
    except Exception:   # noqa: BLE001
        engine = None
    if engine is None:
        # opencv grabcut? fallback simple: flood from edges colour-key
        try:
            import cv2   # noqa: F401
            engine = "opencv"
        except Exception:   # noqa: BLE001
            engine = None
    if engine is None:
        return {"ok": False, "engine": "none",
                "reason": "No background-removal engine installed "
                          "(rembg/onnxruntime or opencv). Provide a PNG with "
                          "alpha, or install one."}
    if engine == "rembg":
        im2 = Image.fromarray(np.asarray(out).astype("uint8"))
        im2.save(out_path, format="PNG")
    else:
        # minimal: white/nearest-corner chroma removal to alpha
        arr2 = _chroma_remove(rgba)
        Image.fromarray(arr2).save(out_path, format="PNG")
    return {"ok": True, "engine": engine, "out": out_path}


def _chroma_remove(rgba) -> "np.ndarray":
    import numpy as np
    a = np.asarray(rgba).astype("int16")
    h, w = a.shape[:2]
    m = max(1, int(min(h, w) * 0.02))
    bg = np.concatenate([a[:m].reshape(-1, 4), a[-m:].reshape(-1, 4),
                         a[:, :m].reshape(-1, 4), a[:, -m:].reshape(-1, 4)],
                        axis=0)[:, :3].mean(axis=0)
    dist = np.abs(a[..., :3] - bg).mean(axis=2)
    alpha = np.where(dist < 35, 0, 255).astype("uint8")
    out = np.dstack([a[..., :3], alpha]).astype("uint8")
    return out
