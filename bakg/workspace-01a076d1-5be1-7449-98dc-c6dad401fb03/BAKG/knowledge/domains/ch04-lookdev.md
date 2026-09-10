# Chapter 4 — UV, Textures, Materials, Shaders, Organic Lookdev (D25–D36)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 62–67 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 4 — UV MAPPING, TEXTURES,
MATERIALS, SHADERS, AND ORGANIC
LOOKDEV
Domains D25–D36. This chapter takes geometry to surface: how 3D becomes 2D texture space, how
maps are made, and how Principled-shader materials are built for skin, eyes, teeth, tongue, and
claws.
D25 — UV MAPPING [REQ]
DEF: Unwrapping: projecting 3D surfaces into 2D (U,V) texture space so images can cover the mesh.
WHY: Without UVs, no image texture (paint, photo, baked maps) can exist. UV quality directly
controls texture resolution, painting sanity, and baking fidelity. It's also where "texture stretching"
and "seam" problems are born. HOW (workflow): 1. Mark seams: choose where the 3D surface will
be cut open. Rules: hide seams in crevices, edges of features, and deformation-neutral zones (inner
leg, underarm, back of head, along the spine); never across visible front surfaces or through the face
center. 2.  Unwrap: select all (A) → U → Unwrap (or Smart UV Project for blocky assets). Blender
computes a flattening; watch the checker/stretch overlay (UV editor: UV → Checker T exture). 3.
Adjust islands: move/scale/rotate islands (G/R/S in UV editor) to maximize texture space use and
orient consistently; straighten edges (U → Follow Active Quads for pipes); pin vertices (P) to control
unwrap behavior. 4.  Pack: U → Pack Islands with margin settings; islands scaled to their  texture
importance (face gets more texels than back) — done deliberately, not automatically. 5. Check: turn
on the stretch overlay (UV editor → Display → Stretch); fix red (stretched) areas by re-seaming or
relaxing (U → Relax / Minimize Stretch). 6. UV layers: multiple UV maps possible (e.g., one for color,
one for lightmap baking — D28). PARAM: texture resolution per island (texel density — texels per
meter, keep consistent per asset class); margin (2–8 px typical at 2k/4k); island padding; UDIM
support (multiple tiles for huge models — 1001, 1002, …). MIST: seams across visible surfaces; tiny
islands  (wasted  texture  memory);  overlapping  islands  (unless  intentional  for  mirrored  textures);
stretched islands (blurry textures).  FAIL: baking artifacts from overlapping/seam-adjacent islands;
visible  seams  at  render.  DIAG: checker  texture  test;  stretch  overlay.  FIX: move  seams;  relax
stretches; bake with margin padding (D28); for characters, use the same unwrap plan as the topology
plan (they're linked decisions).  EDGES: → D26 textures, → D27 painting, → D28 baking, → D30
materials.
Deep chain — UV → Island → Seam → Texel density
Seam choice → island shape → rotation (anisotropy) → texel density → padding → packing → stretch check
D26 — TEXTURE CREATION [SIT]
DEF: Creating  the  2D  images  (maps)  that  define  surface  color/detail:  painted,  photo-derived,
generated, or baked.  WHY: T extures carry the  micro-surface story (wear, dirt, patterns, variation)
that materials (D30) apply with shader logic. Map types (the core set): - Base color / albedo: the
"paint" color, without lighting baked in. (For stylized, often the whole look lives here.) - Roughness:
0=mirror, 1=matte; the #1 map that sells materials (greasy metal vs brushed vs paint). - Metallic:
0=dielectric, 1=metal (use 0/1, rarely in between). - Normal map: fake micro-relief from tangent-
CHAPTER 4 — UV MAPPING, TEXTURES, MATERIALS, SHADERS, AND ORGANIC LOOKDEV

space  RGB;  cheap  detail.  -  Bump  (height)  map: grayscale  height;  weaker  than  normal,  can
combine. -  Displacement: true geometric offset (micro-displacement in Cycles/EEVEE); expensive
but physically real silhouette. - Specular / tint:  reflection tint (Principled's specular input; use for
materials like skin/glass). - Alpha / opacity / mask:  transparency and material masks. - Ambient
occlusion (AO):  contact shadow map (baked — D28). -  Masks (color/roughness/height ID):
region separators for procedural blending (D29) and painting (D27).  How textures are made:  1.
Painting (D27), 2. Photo projection/photogrammetry (reality capture → textures), 3. Generated/
procedural (D29), 4. Baked from sculpt/high-poly  (D28), 5. External tools (Substance Painter/
Designer, Photoshop, Krita, Quixel; genuinely useful for high-end lookdev — export PBR maps, import
into Blender). Texture resolution: 2k (2048²) standard for props; 4k for hero characters/faces; 8k
for full-body heroes or film-grade (memory!); UDIM for extra coverage.  MIST: textures without a
material plan (each map must map to a shader input); 8k everywhere (memory death); "texture
salad" (no coherence — see D138 style guides).  EDGES: → D27 painting, → D28 baking, → D29
procedural, → D30 materials.
D27 — TEXTURE PAINTING [OPT]
DEF: Painting directly on the 3D model (T exture Paint mode) or in the UV editor (2D image editor).
WHY: The  most  direct  way  to  add  design  detail  (patterns,  dirt,  wounds,  color  callouts)  with
immediate 3D feedback; essential for stylized characters and hero props. HOW: 1. Create an image
(Image Editor → New, size, color); assign to the material's Base Color. 2. T exture Paint mode: paint
with brushes (strength, radius, texture alpha); use mask to paint selectively; clone tool to copy from
reference photos; smear for blends. 3. Stencil / projection painting: place reference images as stencils
(T exture Paint → stencil) and paint through them. 4. Work in the UV editor too: precise 2D edits,
symmetry painting (X), bleeding-edge concerns: paint with a margin so seams don't show. 5. Save
images (F3 / Image → Save As); set file paths —  pack or save to the project textures folder
(D123).  PARAM: brush settings; mask layers; symmetry; stencil images; image resolution; texture
bleed/padding.  MIST: painting over UV seams without bleeding; not saving images (they're data
blocks — unsaved = lost); painting without base-color logic (light baked into color). EDGES: → D26, →
D25, → D30.
D28 — TEXTURE BAKING [OPT]
DEF: Transferring detail from one mesh/map to another (high-poly → low-poly; sculpt → texture maps;
world-space → UV space). WHY: Bakes let a low-poly (fast, animatable) mesh look like a high-poly
sculpture:  all  sculpt  detail  becomes  normal/displacement/AO  maps.  Also  used  for  lighting  bakes
(lightmaps) and material ID maps. HOW (Blender): 1. Setup: low-poly object active with UVs; high-
poly object selected; both at same location (or use cage object for better projection). 2. Bake panel:
Render  Properties  →  Bake:  choose  map  type:  -  Combined (all),  Diffuse/Base  Color,  Roughness, 
Metallic, Normal (tangent space, 0.5–1.5 strength), Ambient Occlusion (samples!), Displacement (for
true displacement),  Emission,  Alpha. 3.  Projection: enable  Selected to Active ; set  Extrusion
(cage offset) and Max Ray Distance ; use a cage mesh (shrinkwrap copy of the low-poly, pushed
out) for perfect projection. 4. Resolution & margins: bake at 2× final texture size then downscale
(quality); set margin/padding to kill seams. 5. Image node: create the target images in the Shader
Editor and select them in the Bake panel (Images node as bake target). PARAM: bake type; samples
(AO 16–128); extrusion; ray distance; cage; margin; float images (for HDR data).  MIST: baking
normal maps with wrong settings (inverted green channel — flip Y for DirectX/OpenGL conventions);
seams showing; black/white AO from missing cage; baking  lighting into base color (bake albedo
CHAPTER 4 — UV MAPPING, TEXTURES, MATERIALS, SHADERS, AND ORGANIC LOOKDEV

only!).  FAIL: hard seams at UV borders; "overbake" artifacts.  DIAG: inspect map in viewport with
Material Preview; check UV island padding. FIX: proper cage + margin; consistent normal convention
(Blender = OpenGL, +Y green up); test-bake a low-res version first. EDGES: → D22 sculpting, → D23
retopo, → D25 UV, → D30 materials, → D114 optimization (lightmaps).
D29 — PROCEDURAL TEXTURING [OPT]
DEF: Building textures entirely with shader nodes (no image files): noise, gradients, math, and masks
evaluated at render time.  WHY: Resolution-independent, infinitely varied, no UV dependency, and
parameterized (change one value, update everything). The default for environments, sci-fi surfaces,
stylized materials, and any repetitive-but-varied surface. Core node vocabulary: - Textures: Noise
T exture (the workhorse — fractal detail), Voronoi (cells, scales, cracks), Musgrave (fractal terrain/dirt),
Wave,  Magic,  Gradient,  Image  T exture.  -  Mapping  &  coordinates: T exture  Coordinate  node
(Generated/UV/Object/Normal) + Mapping node (offset/rotate/scale); Object coordinates scale with
the object (great for materials that must look the same on any object size). - Math & color:  Math
(add, multiply, mix, power, clamp — the language of procedural graphs), Map Range (remap values),
Color Ramp (band noise → masks), RGB Curves, MixRGB. - Noise layering: stack noises at different
scales (fBm = fractal Brownian motion) for realistic variation.  Signature recipes:  -  Dirt/grunge
mask: Voronoi + Noise → Color Ramp → mask for roughness variation / color variation. - Scratched
metal: Noise  stretched  (mapping  scale)  +  Wave  →  roughness  mask.  -  Terrain: Musgrave  →
displacement (D80). - Skin variation: low-frequency Noise → subtle color blotch mask + roughness
variation  (combined  with  image  maps).  USE: environments,  stylized  lookdev,  surfaces  needing
variation without UV painting, rigged materials (e.g., a "cloak" shader with parameterized wetness).
AVOID: when  a  specific  artistic  image  is  needed  (paint  it,  D27),  or  when  a  node  graph  gets
unmaintainable (wrap in node groups, D138).  MIST: procedural everything (no art direction, looks
"procedural"); node spaghetti (no node groups); noise scales that don't relate to real-world size (a 1
m noise on a 100 m wall). PERF: node graphs are cheap at render; heavy displacement is not (use
micro-displacement  carefully,  D114).  EDGES: →  D30  materials,  →  D85  geometry  nodes,  →  D86
procedural systems.
D30 — MATERIALS [REQ]
DEF: The  definition  of  a  surface's  visual  response  to  light:  color,  reflectance,  roughness,
transparency, emission, etc.  WHY: Materials are 80% of why a model looks "real" or "cheap." The
same mesh with different materials can read as plastic, metal, skin, or marble. HOW (Blender 4.x):
the  Principled BSDF  is the universal base node — a physically-based, energy-conserving shader
with all common surface parameters. Set its inputs from your maps (D26): - Base Color ← albedo
map;  Roughness ← roughness map;  Metallic ← metallic map;  Normal ← normal map;  Specular
(reflection  tint),  IOR,  Transmission (glass/water/skin-lite),  Subsurface (skin/wax/milk  —  with
Subsurface Radius & Color), Emission (+ Emission Strength), Alpha (masked/clipped transparency),
Sheen (fabric),  Coat (clearcoat: car paint, varnished wood — with Coat Roughness),  Anisotropic
(brushed metal — needs tangent direction). Material types in one page:  | Surface | Key settings |
|---|---| | Skin | Principled + SSS (radius ~0.1–0.3), subsurface color (reddish), roughness 0.4–0.6,
specular 0.5 | | Wet skin | lower roughness + added specular layer / sheen | | Metal | metallic 1,
roughness 0.05–0.8, base color = tint (gold #FFD700 etc.), anisotropic for brushed | | Wood | base
color + roughness variation + clearcoat, normal from grain | | Stone/concrete | roughness 0.9–1, high-
frequency normal + AO | | Glass | transmission 1, IOR 1.45–1.52, roughness ~0 (or 0.1 for frosted), no
metallic | | Plastic | roughness 0.1–0.4, no metal, slight clearcoat for shiny toys | | Ice | transmission +
CHAPTER 4 — UV MAPPING, TEXTURES, MATERIALS, SHADERS, AND ORGANIC LOOKDEV

SSS (blue), low roughness, IOR 1.31 | | Water | transmission 1, IOR 1.33, roughness ~0 (calm) / higher
(choppy)  |  |  Slime/organic  wet  |  transmission  +  SSS  +  high  specular,  low  roughness,  strong
subsurface color | | Emissive (magic, screens) | Emission color + strength, often added to another
base | MIST: metallic 0.5 (wrong — use 0/1); no roughness variation (plastic look); SSS everywhere
(slow);  missing  normal  map  on  hero  assets;  alpha/transmission  confusion.  FAIL: black  renders
(missing texture paths); "everything is shiny plastic". DIAG: light test with HDRI; isolate maps one by
one.  FIX: build  materials  from  maps,  not  guesses;  use  the  same  map  pipeline  for  all  assets
(consistency, D138). EDGES: → D31 shaders, → D108 lighting, → D112 rendering.
D31 — SHADERS [REQ]
DEF: The node graph behind a material: how inputs are computed — texture blending, masks, math,
custom BSDFs. WHY: Real surfaces are rarely one constant — they're layered, masked, and varied.
Shader graphs make materials alive and parameterized. HOW: Shader Editor; build node trees: maps
→ math → mix → Principled inputs. Group reusable logic into node groups (D138). Use mix shader
nodes to layer BSDFs (e.g., dusty over glossy). Use attribute nodes (object data, vertex color, UV
layers) to drive variation per-vertex/per-face.  Advanced: custom BSDF via  Shader to RGB  (view-
dependent tricks, stylized toon shading),  Emission + Light Path  tricks (fake effects),  drivers on
shader  values  (D54  —  e.g.,  wetness  driven  by  rain  sim).  MIST: mixing  shaders  without  masks
(uncontrolled blend); using Mix Shader where MixRGB on inputs is cheaper and cleaner; spaghetti
graphs. EDGES: → D29, → D30, → D54 drivers, → D117 compositing.
D32 — SKIN [SIT]
DEF: Humanoid skin shading: layered, translucent, slightly oily, with pore-scale detail. WHY: Skin is
the most-seen organic surface in character work; bad skin kills realism instantly. Its signature is
subsurface scattering  (light penetrates, scatters red) + subtle specular + high-frequency pore
detail.  HOW (the skin pipeline):  1.  Maps: base color (with red/blue variation: cheeks, knuckles,
ears), roughness map (0.3–0.7 variation), SSS map (thickness variation: ears/nose/fingers = thin =
more  transmission),  normal  map  (pores  +  micro-wrinkles).  2.  Principled  setup: SSS  enabled,
subsurface  radius  (R/G/B:  ~1,  0.25,  0.15  scaled  small  —  red-heavy),  subsurface  color  (reddish/
brown), subsurface scale (per-object: ~0.01–0.05 for characters), roughness ~0.5, specular ~0.5. 3.
Detail layering: pores via normal map; oil sheen (slight roughness reduction on nose/forehead); wet
skin = lower roughness + reflection layer (rain!). 4. Stylized skin: SSS off or subtle; flat shading with
2-tone ramp (anime), or cartoon shading via Shader-to-RGB (D31). MIST: SSS everywhere (skin looks
like wax/milk); roughness constant (plastic); no thickness variation (fingers glow like ears).  DIAG:
render  under  a  strong  backlight  —  if  ears/fingers  don't  glow  red,  SSS  is  wrong.  PERF: SSS  is
expensive in Cycles — use screenspace/BSSRDF approximations in EEVEE; keep SSS objects few.
EDGES: → D33 eyes (eyes sit ON skin), → D30, → D108 lighting (skin needs good light to shine).
D33 — EYES [SIT]
DEF: The eye: sclera (white), iris, pupil, cornea (front bulge), plus wet gloss. The most important
single feature for life. WHY: Audiences read life from eyes first. A great eye shader + gaze system
(D63) is the difference between a doll and a character. HOW (anatomy-accurate construction): 1.
Geometry: eyeball sphere + separate cornea (slightly larger sphere, front cap) + iris disc recessed
in the sclera. (Real eyes have the cornea bulge — it creates the iris's "lens" look and glint.) 2.
CHAPTER 4 — UV MAPPING, TEXTURES, MATERIALS, SHADERS, AND ORGANIC LOOKDEV

Shaders: sclera: white with faint red/brown tint + roughness variation (blood vessels via texture);
iris: radial texture, translucent, highly detailed normal map (crypts); cornea: transmission (IOR 1.376,
glass-like) with a  tiny roughness  — this gives the wet lens specular; add  specular highlight
naturally via lighting. 3. Refraction: the cornea transmits/refracts — light passing through the iris
region gives the eye its depth; in EEVEE use screen-space refraction or fake with emissive iris +
clearcoat. 4.  Wet gloss: a tight specular (clearcoat layer, roughness ~0.02) over the whole front.
MIST: eyeball as a single flat-textured sphere (no cornea depth); pure white sclera (dead doll); iris
without detail; no glint control.  DIAG: close-up render — if the eye looks painted-on, geometry/
refraction is missing.  FIX: build the 3-piece eye; give the rig separate eye controls (D63)  and a
dedicated high-res iris texture (2k just for the iris is normal).  EDGES: → D63 eye systems, → D61
facial animation, → D30 materials.
D34 — TEETH [SIT]
DEF: T eeth: enamel (hard, translucent, glossy) over dentin (warmer, yellower); gums attached. WHY:
T eeth sit in the mouth — visible in speech (D62) and smiles; wrong teeth read instantly as fake (too
white/too opaque). HOW: geometry: individual tooth meshes (or a tooth strip for stylized); shader:
Principled with subsurface (enamel transmission), base color warm ivory, roughness 0.1–0.3, slight
yellowing toward the gum; gums: pink-red, SSS, roughness ~0.6; keep teeth  separate meshes  if
individual tooth movement is needed (rare) or a single strip (common). PARAM: enamel SSS; tooth
color variation (avoid pure white); occlusion between teeth (AO bake).  MIST: teeth as pure white
plastic; teeth stuck to the jaw mesh (can't animate lips over them cleanly); no gums. EDGES: → D62
lip sync, → D60 facial rig.
D35 — TONGUE [SIT]
DEF: The  tongue:  muscular,  wet,  highly  flexible  —  crucial  for  phonemes  (D62)  and  character
moments. HOW: geometry: a tapered, flexible mesh with loop topology along its length; shader: SSS
+ transmission (wet), base color pink-red with variation, roughness ~0.4, specular wet gloss; rig: 3–6
bones with IK/FK (tongue rig — see D60/D49). MIST: tongue as a rigid shape (can't articulate L/T/D
sounds); dry material. EDGES: → D60 facial rig, → D62 lip sync.
D36 — NAILS / CLAWS [SIT]
DEF: Keratin tips: fingernails, toenails, claws, talons, hooves — hard, translucent, curved.  HOW:
geometry: built into finger tips or separate meshes (for claws, separate is better for rigging); shader:
Principled with slight transmission/SSS (keratin transmits a little), base color from pale pink (human)
to  black/ivory/bone  (creatures),  roughness  0.1–0.3,  clearcoat  for  sheen.  Claw-specific: curves
matter  (talons  recurve  for  grasping);  ridges  via  normal  maps;  wear  marks  on  tips  (roughness
variation); for creatures, match claw design to  function (D05) — digging claws broad, killing claws
hooked, climbing claws sharp.  MIST: claws as plain cones (no curve/ridge); same material as skin
(keratin ≠ skin). EDGES: → D05 creature design, → D30 materials, → D58 deformation (claw tips need
joint support).
CHAPTER 4 — UV MAPPING, TEXTURES, MATERIALS, SHADERS, AND ORGANIC LOOKDEV

LOOKDEV HANDOFF CHECKLIST
[ ] UV plan approved (seams hidden, texel density set)
[ ] All maps: base color (no baked light), roughness, normal, masks
[ ] Materials built from Principled with correct IOR/SSS/transmission
[ ] Skin/eye/teeth/tongue/nails tested in close-up with hero lighting
[ ] Procedural materials wrapped in named node groups
[ ] T exture files saved in project folder (not just packed)
[ ] T est render approved under final lighting intent
• 
• 
• 
• 
• 
• 
• 
CHAPTER 4 — UV MAPPING, TEXTURES, MATERIALS, SHADERS, AND ORGANIC LOOKDEV
