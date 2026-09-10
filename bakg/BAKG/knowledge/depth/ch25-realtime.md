# Depth Chapter 25 — Real-Time & Interactive Pipelines

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 173–175 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 25 — REAL-TIME &
INTERACTIVE PIPELINES
Expands D113, D137. When the target is a game engine, a web viewer, or EEVEE-rendered film:
EEVEE Next production settings, real-time character/animation practice, export pipelines, and the
performance discipline that makes real-time work.
25.1 EEVEE NEXT — PRODUCTION SETTINGS (Blender
4.2+)
What it is:  the rewritten real-time renderer — rasterized base + optional raytracing (reflections,
refraction,  diffuse,  AO)  in  the  same  frame,  GPU-accelerated.  It  renders  the  Principled look  at
interactive speed.
The settings that matter: | Setting | Where | Production values | Notes | |---|---|---|---| | Raytracing |
Render → Raytracing | Screen (fast) or World (accurate) | Reflections/refraction/AO on demand — this
is the EEVEE-Next "realism" switch | | Raytracing resolution | per-effect | ½ or full | Lower = faster,
softer | | Shadows | Render → Shadows | Soft shadows ON, ray-traced or shadow map | Shadow
softness by light size  is the realism jump | | Volumetrics | Render → Volumetrics | tile size 4–8,
samples 8–32 | Needed for fog/shafts (D111); watch memory | | Bloom | Compositor | enabled for
glow look | 0.5–1 strength, threshold 0.8+ (D117) | | Motion Blur | Render → Motion Blur | ON for film
feel | EEVEE's is decent — use it | | Depth of Field | camera | ON | EEVEE DoF is fast — do it in-render |
| Ambient occlusion | Render → AO | ON (distance 0.2–0.5 m) | grounding (D109) — with raytraced
AO, better | | Screen-space reflections | Render → SSR | ON + traces | Fast reflections; off-screen =
missing (know the limit) | | Color management | Render → Color | AgX | same pipeline as Cycles
(D112) |
EEVEE vs Cycles material gaps:  SSS is approximated (screen-space — looks ok on skin at close
range, weaker at distance); refraction needs raytracing on; multiple bounces are limited (a room lit
by one lamp is fine; heavy GI scenes read darker/flatter); volumetrics are tiled (cheaper look than
Cycles). Plan materials with EEVEE's limits in mind  (or do a hybrid: EEVEE lookdev, Cycles for
hero shots).
25.2 REAL-TIME CHARACTER PRACTICE (making EEVEE
footage look intentional)
Lighting for EEVEE: more, smaller, deliberate lights than Cycles (GI is limited — bake AO/
lightmaps or place fills where bounce would be, D108); use light linking heavily; shadow maps
love tight light angles.
The "fake GI" recipe: a subtle blue-ish ambient fill + warm key + AO pass baked or ray-traced +
contact shadows — reads as full GI at a fraction of the cost.
Volumetrics discipline: one or two localized volume domains (D111) at low tile size — the
money shot without the cost.
Motion & camera: EEVEE handles fast motion well; add motion blur so motion reads filmic
(D112); camera shake (D107) is free in EEVEE — use it.
• 
• 
• 
• 
DEPTH CHAPTER 25 — REAL-TIME & INTERACTIVE PIPELINES

25.3 EXPORT TO GAME ENGINES & WEB (the real-time 
target pipeline)
The pipeline: Blender → glTF (web/games) or FBX (Unity/Unreal) or USD (engines/studio) → engine.
Critical correctness points (D24.4): scale (Unreal = cm, Unity = m), axis (Y-up export), tangent space,
animation bake (drivers/constraints baked — engines don't evaluate Blender drivers!), mesh LODs
(build in Blender — engines import LOD groups), texture compression (BC7/ASTC via engine import
settings),  skeleton  conventions (bone  naming  must  match  the  engine's  expectations  for
retargeting — Unreal skeleton names, etc.). Real-time character budget (game targets): 5k–50k
triangles · 1–4 × 2k textures · 1–2 skeletons · 30–80 bones · blendshapes ≤ 50 (engines limit counts) ·
LOD 3 levels. Film EEVEE budget:  much higher — EEVEE is a renderer, not a game engine; your
constraints are GPU memory and interactive frame rate, not draw calls. Web: glTF/GLB + three.js/
PlayCanvas/Babylon.js — character + animation + PBR materials work out of the box; texture sizes
stay ≤ 2k for download weight; animations as separate clips (walk, idle, attack) — build them as
actions in Blender (D64/NLA) and export the set.  Interactive/VR: VR scenes = real-time rules +
head-tracking considerations (camera = the player's head; design around the viewer); performance is
the contract (90 fps VR).
25.4 THE REAL-TIME PERFORMANCE DISCIPLINE (draw
calls, memory, LODs)
Lever What it is Practical rule
Draw calls per-object render
submissions
merge static geometry (combine props into atlases/meshes); instancing
for repeated objects (D85)
T exture
memory
VRAM usage atlas textures (one image per material set); ≤ 2k for props, 4k hero only;
compression via engine import
Vertex count geometry LODs: build 3 levels in Blender (Decimate/GN — D24); engines switch
automatically
Materials shader cost merge materials (fewer material slots per mesh); avoid per-object
material instances
Lights light count × shadows real-time shadows are expensive — bake static lights to lightmaps, keep
1–2 dynamic shadow casters
Particles/VFX overdraw cap particle counts; billboards (cards) over 3D meshes (D100)
Animation skinning cost bone counts ≤ 80; fewer blended animations running at once
Occlusion culling engines cull — keep geometry in units so culling works (don't merge the
whole map into one mesh!)
The golden rule:  measure in the  target (engine/EEVEE viewport) with its profiler — don't guess.
Budgets without measurements are fiction (D14).
DEPTH CHAPTER 25 — REAL-TIME & INTERACTIVE PIPELINES

25.5 REAL-TIME FAILURE MODES & FIXES
Symptom Cause Fix
Character looks dark/flat in
EEVEE
no GI, no AO AO on + ambient fill + light linking
Reflections missing SSR limit (off-screen) Ray-traced reflections on, or plan shots to keep
reflectors on-screen
Slow frame rate in viewport everything visible Simplify (D126), collections visibility, viewport
proxies
Export looks wrong in
engine
scale/axis/tangents Export discipline (24.4); test-import early
Animations don't play in
engine
drivers not baked / NLA not
exported
Bake actions; export each action as a clip
T extures blurry in engine compression/UV density Re-UV with texel density (D25); check mipmap
settings
Volumetric fog "chunky" low tile res Raise tile resolution (memory trade), reduce density
DEPTH CHAPTER 25 — REAL-TIME & INTERACTIVE PIPELINES
