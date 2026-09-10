# Depth Chapter 26 — The Optimization Masterclass

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 176–178 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 26 — THE OPTIMIZATION
MASTERCLASS
Expands D14, D24, D26, D114, D126. The complete ladder of making Blender fast: from budgets and
LOD systems to memory, viewport, lightmaps, and render economics. Optimization is a  strategy
applied at every level — never a panic at the end.
26.1 THE OPTIMIZATION LADDER (apply top-down)
Budget (D14) — the root: decide polygon/texture/instance/sim budgets per asset class before
building. All later steps are enforcement.
Instancing (D85) — never duplicate; instance. Trees, rocks, props, particles.
LOD (D24) — high/mid/low mesh versions; distance-based switching (Blender: the LOD system
on objects — Object Properties → Levels of Detail — or GN LOD; engines have their own, Ch 25).
Proxies & viewport stand-ins — the display version vs the render version (viewport proxies for
characters, simplified collision meshes for sims, D39/D47).
Texture discipline (D26/D25) — texel density budgets, 4k only for heroes, atlases, compression
(BC/ASTC for real-time), baking procedural → texture for heavy scenes.
Simplify (D126) — the global switch: Render/Viewport → Simplify: max subdiv, texture size, child
particle count, volume resolution. One toggle for preview, off for final.
Render optimization (D114) — samples, denoise, bounces, adaptive sampling, light linking,
volume limits.
Memory management — VRAM, EXR sizes, caches (26.5).
Scene management — view layers (D15), collections, linked assets (D122), orphan cleanup.
Hardware — GPU compute enabled (D114), sufficient RAM/VRAM, SSD for caches (D123).
26.2 LOD SYSTEMS IN DETAIL
Blender's LOD: an object can have a LOD list (Object → LOD): each entry is another mesh with a
"Distance" — beyond that distance, the renderer uses the lighter version. Viewport LODs optional.
Rules: make LODs by decimation (Decimate modifier, collapse 0.5–0.7) or manual re-topo for heroes;
keep LOD transitions  unnoticeable (silhouette-first: far LODs can drop small detail aggressively —
buttons vanish, silhouettes stay); test at the actual camera distance. The distance budget (film):
hero (0–5 m): full detail; mid (5–30 m): LOD1 (50% polys, 2k textures); far (30–100 m): LOD2 (20%,
1k); background: silhouettes/proxies (2% or instanced cards). For real-time (Ch 25):  3–5 LODs per
asset, engines pick by screen size.  Impostors (extreme): replace far objects with  camera-facing
billboards (rendered images of the object) — for crowds, forests, city grids. GN can generate impostor
fields from instanced assets (D85/D86).
26.3 TEXTURE OPTIMIZATION (the silent memory eater)
Texel density discipline (D25): standardize texels/meter per asset class (hero 1024/m, prop
256/m, background 64/m) — then resolution choices become automatic.
Atlas everything: combine related props into one texture set (one 2k atlas vs four 1k) — fewer
draw calls + less memory (real-time gold, Ch 25).
1. 
2. 
3. 
4. 
5. 
6. 
7. 
8. 
9. 
10. 
• 
• 
DEPTH CHAPTER 26 — THE OPTIMIZATION MASTERCLASS

Bake procedural → image for heavy scenes: a 500-tree forest with procedural materials burns
render time; bake the material to a 1k/2k texture once (D28) — the trees look identical, render
10× faster.
Compression: real-time: BC7 (quality) / ASTC (mobile); film: keep EXR/PNG, but downscale far-
asset textures (a 1k texture on a mountain 2 km away is invisible — cut it to 256).
UV layout check: unused texture space = wasted memory (D25 packing).
Limit unique textures: 50 unique 4k textures = 800 MB VRAM; 50 unique 1k = 200 MB. Reuse
the library (D84) — materials should share textures where possible.
26.4 VIEWPORT PERFORMANCE (the iteration-speed
levers)
Viewport shading → Solid with color (fastest) for heavy scenes; Material Preview for lookdev
on isolated objects.
Overlays off during heavy manipulation (they cost surprisingly much).
Simplify (26.1 #6) — the viewport killer-solver.
Visibility discipline: collections (D15) — hide what you're not working on; Local view
(Numpad /) for isolated focus; hide render-expensive things (volumes, hair) while posing.
Viewport instance display: GN "Limit" display counts; hair "strand display" simplification;
particle display % — everything has a display-limit switch.
GPU vs CPU viewport: enable GPU for viewport (Preferences → System); some features
(volumes) run CPU — know which is choking.
Proxies: substitute the heavy character for a low-poly stand-in in the shot file while animating
(link the final at render time — D122 library overrides for this).
Cache playback: sims/hair cached to disk play faster than live sim (D88).
26.5 MEMORY & CACHE MANAGEMENT (the 40-GB-
surprise prevention)
VRAM budget: know your GPU's limit; monitor with T ask Manager/nvidia-smi ; if a render dies at
8 GB with 4k textures, the fix is textures, not patience.
EXR math: a 4k EXR multilayer with 8 passes ≈ 100–200 MB/frame; a 120-frame shot ≈ 15–25
GB. Plan disk; render single-layer EXR (or pass-split) when possible; delete WIP renders after
approval (D127).
Sim caches: cloth/hair/fluid caches are huge (GBs); name them per shot+version (D123 cache/
folder), delete stale versions (D124); cache to SSD for speed.
Orphan data: File → Clean Up → Unused Data-Blocks; check the Outliner's "Orphan" filter; keep
files lean (D15).
The archive rule (D129): at archive time, keep final caches only if re-rendering is planned;
otherwise keep the settings + final renders.
• 
• 
• 
• 
1. 
2. 
3. 
4. 
5. 
6. 
7. 
8. 
• 
• 
• 
• 
• 
DEPTH CHAPTER 26 — THE OPTIMIZATION MASTERCLASS

26.6 RENDER ECONOMICS (making final renders
affordable)
Scenario Strategy
Long film, Cycles LOD + textures + light linking + volumes budgeted + denoise at 64–128 samples + render
farm (Ch 24.5)
Long film, real-time
style
EEVEE final (D113) — the "render" is viewport speed
Hero shots Cycles high quality on the few money shots; the rest EEVEE/comped
Everything too slow Profile (D114 "identify the slow part") — fix the layer, not the settings
Night render window Batch the render queue; EXR per frame; resume/re-render failures in the morning
The final truth:  optimization is  budget + discipline + measurement  — set numbers early,
enforce them at gates (D127), and measure in the target (viewport, render, engine). The scenes that
"won't render" are always the scenes that skipped the ladder.
DEPTH CHAPTER 26 — THE OPTIMIZATION MASTERCLASS
