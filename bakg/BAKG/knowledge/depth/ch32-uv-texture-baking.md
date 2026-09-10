# Depth Chapter 32 — UV, Texture & Baking Depth

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 199–202 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 32 — UV, TEXTURE & BAKING
DEPTH
Expands D25–D29. The complete surface-coordinate and map-creation craft: UV strategy per asset
class,  seam  planning,  texel  density,  UDIMs,  painting  workflow,  the  full  baking  pipeline,  photo
projection, and the artifact-fix catalog.
32.1 UV STRATEGY PER ASSET CLASS
Asset Strategy Notes
Character per-island by importance: face/hands get max texel density; body 2–4
islands (front/back/arms/legs); seams hidden (underarm, inner leg, back of
neck, along spine)
face often gets its own
2k+ island
Hard-surface per-part islands (panels, details); seams along panel edges clean boxes = easy
unwrap
Organic
creature
follow sculpt regions; scales need stretched-less islands avoid stretching over
curved forms
Environment
tiling
tileable UVs (0–1 repeating) for ground/walls/roofs tiles never need
unwrapping
Props one island per major surface; small props = single atlas share atlases between
props (Ch 26.3)
Background automatic (Smart UV) or none (no textures) save the time
Hair/fur UV rarely needed (strand shaders, Ch 33) —
32.2 SEAM PLANNING (the hidden art)
Rules: (1) hide seams in crevices and low-visibility zones (underarm, inner leg, back of head, inside
the ear); (2) never across visible front surfaces or the face centerline; (3) follow the deformation —
seams placed along fold lines deform least visibly; (4) fewer, larger islands beat many small ones
(less seam length, better packing); (5) keep UV orientation consistent (straight edges along loops —
U → Follow Active Quads). The classic character seam set:  head: one seam up the back of the
neck; body: underarm → down the side → crotch → back up (the "T" seam); arms: inside of the arm;
legs: inner leg to the ankle; hands: inside the palm, up the inner wrist. Testing: apply the checker
texture; any stretched squares = bad seam/angle choice; fix with Relax/Minimize Stretch (UV editor →
UV → Minimize Stretch, pin key verts first).
DEPTH CHAPTER 32 — UV, TEXTURE & BAKING DEPTH

32.3 TEXEL DENSITY TABLE (texels per meter —
consistency across a project)
Asset class Film (px/m) Realtime (px/m) Example at 2k
Hero face 3000–6000 1500–3000 face island ≈ 1536–2048 px
Hero body 1500–3000 800–1500 body island ≈ 2048
Clothing 1000–2000 500–1000 —
Props (hero) 1000–2000 500–1000 —
Environment hero 500–1000 200–500 —
Background 100–300 50–150 often tileable
Tiling surfaces any (tile) any tiles are density-free by design
The rule: consistent texel density across a scene prevents "sharp face, blurry body" — match islands
to the same px/m so the whole character reads uniformly. Measure with the UV editor's texel-density
overlay (View → T exel Density).
32.4 UDIM & MULTI-TILE
UDIM: multiple  texture  tiles  (1001,  1002,  …)  on  one  UV  map  —  for  huge  models  (a  full-body
character at 4k-per-tile, an environment wall mural). Blender supports UDIM image tiles natively;
pack islands into tiles manually or with tools. Use when: the asset needs more texel density than
one tile at a reasonable resolution, or the model is too big for one atlas. Manage: texture budget (Ch
26.3) — each tile is memory.
32.5 UV EDITING WORKFLOW & TOOLS
Mark seams (Edge → Mark Seam) → 2. Select all → U → Unwrap (or Smart UV Project for blocky). 3.
In the UV editor: check checker stretch → fix with pins + Relax. 4. Scale islands to importance
(select island, S). 5. Straighten with Follow Active Quads for pipes/cylinders. 6. Pack Islands
(margin: 2–8 px at 2k+; use "Pack to original" carefully) — check the packing quality; manual
adjust for hero islands (faces, focal areas). Tools: UV Sync Selection (the linked icon), Stitch (sew
islands), Pin (P), Unpin (Alt-P), Island selection (L in UV), Average Islands Scale (texel density
equalizer).
32.6 TEXTURE PAINTING DEPTH
Layers: paint in Texture Paint mode on image textures; for layered painting (base → details →
grunge), use the compositor workflow or external tools (Substance/Krita) — Blender's native
painting is single-image (with masks for selective editing).
Stencils: T exture Paint → brush texture = a reference image; paint through it (the fastest way to
transfer a design — runes, insignias, patterns).
Projection painting: paint from a view/camera — project a photo onto the model (UV Project
modifier / texture painting with a camera projection) — great for faces and concept transfer.
Masks: paint masks on a mask texture (weight-paint-style) to control where effects apply (grime,
wear, wetness — Ch 17 recipes).
1. 
• 
• 
• 
• 
DEPTH CHAPTER 32 — UV, TEXTURE & BAKING DEPTH

Symmetry: paint with symmetry (X) for base, off for the final pass.
Bleeding: paint with a margin (pad the islands) so seams don't show — or bake with margin
(32.7).
Saving: save images to the project textures folder (D123); pack or relative paths.
32.7 THE BAKING PIPELINE (full recipe)
Setup: low-poly  active  with  UVs  (target);  high-poly  selected;  same  location  (or  cage).  Render
Properties → Bake: 1.  Normal map:  tangent space; Extrusion 0.01–0.05 (cage offset); Max Ray
Distance 0.1–0.3; margin 8–16 px; bake at 2× final → downscale (quality + edge softening). 2. AO:
samples  32–128  (higher  =  cleaner);  distance  0.1–1.0  m  (world  scale!);  margin  8+;  AO  is  the
grounding  layer  (D109).  3.  Curvature: (via  GN/vertex  colors  or  external  tools)  —  masks  for
weathering (Ch 26 recipes). 4.  Thickness: bake for SSS maps (thin ears/fingers glow — D32) and
transmission. 5.  Material/ID: per-object or per-material flat colors — for selection masks in comp
(D115  Cryptomatte  alternative).  6.  Height/Displacement: for  true  displacement;  float  EXR  for
precision. 7. Combined/Diffuse: only if you must (prefer albedo from the source material, not baked
lighting).
Cage discipline:  a  cage mesh  (shrinkwrap copy of the low-poly, pushed out ~0.02–0.05) is the
professional guarantee against ray-miss artifacts (black/red streaks).  Always test-bake a small
region first.
32.8 PHOTO PROJECTION & SCANS
Projection: unwrap → UV Project modifier with a camera → project the photo; paint/blend edges
(the "photo texture" look — for faces, buildings).
Photogrammetry: capture a real object (phone photos → Meshroom/RealityCapture) → import
mesh + textures → retopo (D31) → rebake (32.7). Use for: realistic props, terrain textures, real-
world materials. License/consent note: capture only what you're allowed to use.
Material scans: capture roughness/color patches (a photo of a rusted plate = instant grunge
texture — just fix perspective and levels).
• 
• 
• 
• 
• 
• 
DEPTH CHAPTER 32 — UV, TEXTURE & BAKING DEPTH

32.9 PROCEDURAL TEXTURE RECIPES (beyond Ch 17's
ten)
Recipe Nodes Use
T errain layers Noise height → ColorRamp → Mix rock/grass/snow by height+slope (Ch 17.10
style)
D80 terrain
Weathering
mask
Curvature (bake) → ramp → grime on edges; or Voronoi crack lines + noise
fill
metal/wood wear
Fabric weave small-scale checker/grid noise → normal bump + roughness cloth (D34)
Water ripple Wave texture (dual, offset) → normal/bump, animated via Mapping time puddles, lakes
(D94)
Stylized flat ColorRamp posterize on the shading (Ch 18) toon
Magic runes UV-grid mask → emission + pulse driver D101
Scales Voronoi (F2-F1) → color/bump per cell creature (D30)
Ice cracks Voronoi edges → emissive/white lines + transmission D30 ice
Rust streaks stretched noise (mapping scale X) + Mask (gravity direction) vertical streaks
Firewood bark stretched noise vertical + darker valleys D30 wood
32.10 TEXTURE FORMATS & COMPRESSION
Format Use Notes
PNG color/albedo, masks lossless, 8-bit; big files
JPEG photo albedo, references lossy — avoid for final maps with gradients
EXR HDR data: displacement, light, AO float 16/32-bit float (D112)
TGA/TIFF legacy/painting intermediates rarely needed
BC7/ASTC (realtime) engine textures compression at import (Ch 25)
DDS/KTX2 engine-native texture transcoding (Ch 25)
32.11 TEXTURE ARTIFACTS & FIXES
Artifact Cause Fix
Visible seam island bleeding/no margin margin 8–16 px, bleed, or paint across
Stretched texture bad unwrap angle/density re-unwrap, relax, texel-density check
Inverted normals green channel wrong (DirectX/OpenGL) flip Y (Image → Invert, Y)
Black/red baking streaks cage/ray distance cage mesh + extrusion + test region
Blurry at distance low texel density raise density for the shot distance
Banding in gradients 8-bit + grade work 16-bit EXR, or dither/grain
T exture "pops" at LOD switch mipmap/compression engine import settings; LOD texture levels
Muddy colors baked lighting in albedo re-source albedo (D26 rule)
DEPTH CHAPTER 32 — UV, TEXTURE & BAKING DEPTH
