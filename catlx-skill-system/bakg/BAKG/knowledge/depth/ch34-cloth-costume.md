# Depth Chapter 34 — Cloth, Costume & Wear Depth

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 207–209 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 34 — CLOTH, COSTUME &
WEAR DEPTH
Expands D37–D41, D91. The complete garment craft: construction techniques, the cloth-sim tuning
masterclass, fabric behavior library, armor/accessory integration, aging & wear, and sim budgets.
34.1 GARMENT CONSTRUCTION TECHNIQUES
Technique How Best for Notes
Pattern/
sewing-springs
flat 2D panels sewn together
with Cloth Sewing Springs
historical/accurate
garments, complex
draping
the panels are the pattern (real
tailoring); sew-closed sim then
cache as rest
Shell modeling model the garment as a closed
shell over the body (clearance
2–8 cm)
most production
garments
fastest; sim handles motion, not fit
Hybrid modeled base + simulated loose
parts (hem, skirt, cloak, sleeves)
the professional
standard
coat modeled, skirt simulated; best
control/cost
Sculpted
garments
sculpt the garment over the
body (D22)
stylized/one-piece
outfits
no sim; rigs like skin (D48) +
correctives (D59)
Procedural
garments
GN-generated (extrude profiles,
curve-draped)
sci-fi/armor panels,
mass outfits
parameter-driven (Ch 20.4)
Construction checklist per garment:  clearance by fabric (heavy wool 4–8 cm, silk 2–4, skin-tight
0.5–1.5); panel seams (model the seam lines — they're where folds form); hem weight (a weighted
hem drapes — add a vertex group + weight); collars/cuffs (structure points — pin these); thickness
(Solidify or shader); closures (buttons/zippers/laces as separate meshes, D40).
34.2 THE CLOTH-SIM TUNING MASTERCLASS
The settings map (Cloth modifier): | Setting | What it does | Range / typical | |---|---|---| | Quality |
solver steps per frame | 5–15 (raise when unstable) | | Mass | fabric weight | 0.1–2 kg; heavier = more
drape | | Air Damping | "floatiness" | 0.1–1 (0.5 typical) | | Bending Model | Linear (light, fast) /
Angular (crisp folds, stiff) / Bending+Shearing (woven, best) | choose by fabric (34.3) | | Stiffness:
Bending | resistance to folds | 0.1–1 (cotton 0.3, leather 0.9) | | Stiffness: T ension | resistance to
stretch | 15–100 (cotton ~30) | | Stiffness: Compression | resistance to squish | 0–30 | | Damping |
energy loss | 0.1–1 (0.5–0.9 typical) | | Self-Collision | fabric-fabric | ON for loose garments; Quality 2–
8 | | Collision (object) | body/world | Distance 1–5 mm (scale!); Friction 0.5 | | Sewing Springs | panel-
sewing (34.1) | stiffness per seam | | Pinning | vertex group anchor | shoulders/waist/collar = 1.0 |
The tuning method (never random):  (1) start from a preset (cotton/silk/leather); (2) simulate 30
frames — watch  drape (does it sit right? adjust mass/bending); (3) watch  motion (follow-through?
adjust  damping/air);  (4)  watch  collision (poking?  adjust  distance/self-collision);  (5)  bake.  One
variable at a time  — change mass, test; change damping, test.  Lead-in rule:  simulate 30–60
frames before the shot starts so the cloth settles (the first frames of a sim are garbage). Animation-
driven: cloth is pulled by the body — extreme fast moves need higher Quality + lower timestep, or
the cloth "tears" numerically.
DEPTH CHAPTER 34 — CLOTH, COSTUME & WEAR DEPTH

34.3 THE FABRIC BEHAVIOR LIBRARY (which settings =
which fabric)
Fabric Mass Bending Damping Motion character Use
Light
cotton
0.5–0.8 0.2–0.3 0.5 soft, moderate flow shirts, dresses
Silk/chiffon 0.2–0.4 0.1–0.2 0.4 floaty, flowing, snaps capes, gowns, scarves
Heavy
wool
1.0–1.5 0.4–0.6 0.7 heavy drape, few folds,
slow
cloaks, coats (the user's
cloak!)
Denim 0.8–1.2 0.3–0.5 0.6 stiff, creases hold pants, jackets
Leather 1.0–2.0 0.7–0.9 0.8 stiff, holds shape, creaks jackets, belts, armor trim
Canvas/
tent
1.5–2.5 0.6–0.8 0.8 very stiff, heavy sails, tents, backpacks
Knit 0.4–0.7 0.15–
0.25
0.5 stretchy, clings sweaters
Wet cloth ×0.7 mass, ×0.5
bending
— 0.9 clings, heavy, matte-
glossy
rain scenes (D99)
The "fabric story" (D37):  the silhouette the design promises must match the fabric's settings — a
"flowing  cloak"  needs  silk/wool  settings,  not  denim;  a  "taut  tactical  vest"  needs  leather/canvas
stiffness, not chiffon. Match the settings to the design intent, not to convenience.
34.4 ARMOR & ACCESSORY INTEGRATION (the hard-on-
soft system)
Rigid plates (D41 recap): parented to bones (no weights), staggered joints (pauldron lames
overlap), limits per plate (28.6).
Under-suit: weighted cloth (D57) or cloth-sim (D39) — the flexible base.
Straps/belts: cloth-sim or weighted; buckle = rigid child.
Dangly bits: chains, tassels, amulets — rigid-body chains (D89 constraints) or cloth with high
stiffness; always include them in collision (D40).
The interaction test: armor must not clip the cloak, the cloak must not clip the armor; dress in
layers and collide each layer against the others (D37 layering).
• 
• 
• 
• 
• 
DEPTH CHAPTER 34 — CLOTH, COSTUME & WEAR DEPTH

34.5 AGING & WEAR (the material story)
Wear type How Result
Fading BC desaturation + roughness up on sun-facing areas sun-bleached cloth
Grime grunge mask (Ch 17 r2) on hem/cuffs/armpits lived-in
Wrinkles (permanent) normal map creases at elbow/knee (compression zones) worn folds
Holes/tears alpha masks + displaced edges damage
Stains painted masks (D27) or procedural coffee, blood, mud
Metal wear edge-mask (AO/curvature) → fresh metal revealed scuffed armor
Frayed hems alpha noise on the edge texture detail
Dust/snow accumulation world-state driver (D99) → mask amount seasonal
The rule: a costume without wear is a costume that was made yesterday. Weathering is part of the
design (D37/D26) — budget a wear pass per hero costume.
34.6 SIM BUDGETS & CACHING
Vertex budget: cloth 10k–50k faces per garment (sim cost ~linear with verts); 5–15 Quality
steps; 2–3 garments per hero character max (production rule).
Caching: bake to disk (project cache folder — D123); name per shot+version (D124); cache after
animation lock (D88 rule).
Proxy collision: the body collision mesh = a low-poly shrinkwrapped proxy (not the dense hero
mesh) — the #1 cloth perf lever.
The economics: cloth sims are CPU; a 2-minute shot at 15 steps ≈ minutes-to-hours of bake —
budget in the schedule (D125); simulate only what's visible.
34.7 CLOTH & COSTUME FAILURE MODES & FIXES
Symptom Cause Fix
Cloth explodes on
frame 1
too few steps / collision distance too small /
wrong scale
Quality ↑, distance ↑, check scene scale
(D14)
Cloth passes through
body
no collision object / distance too small Collision modifier + distance + proxy
Fabric jitters forever damping low / self-collision weak damping 0.7+, self-collision quality ↑
Garment slides off no pins pin shoulders/waist/collar (34.2)
Unnatural folds wrong bending model Angular for stiff, Bending+Shearing for
woven (34.3)
Cloth "tears" at fast
moves
timestep too coarse Quality 10–15, lower timestep
Armor clips cloak no layer collision layer collisions + dress in order (34.4)
Sim different every
session
not baked bake to disk (34.6)
Cloth looks like plastic material wrong (D30/Ch 17.7) + no wear fabric material + weathering (34.5)
• 
• 
• 
• 
DEPTH CHAPTER 34 — CLOTH, COSTUME & WEAR DEPTH
