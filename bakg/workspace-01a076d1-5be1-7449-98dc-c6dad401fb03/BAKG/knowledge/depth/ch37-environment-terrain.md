# Depth Chapter 37 — Environment & Terrain Depth

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 217–219 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 37 — ENVIRONMENT &
TERRAIN DEPTH
Expands D79–D86. The complete world-building craft in 3D: terrain generation systems, vegetation
ecosystems, modular architecture, water systems, environment lighting integration, and the hero/
background split that makes worlds affordable.
37.1 THE ENVIRONMENT PRODUCTION PIPELINE (order of
build)
World brief (D02/D83): geography, climate, time, palette — the constraints table (Ch 27.1).
Layout (D16): terrain blockout + structure masses + camera framing (previs, D11).
Hero/background split (D79): the camera-tested hero area gets full detail; mid-ground
modular/procedural; background silhouettes/impostors (Ch 26).
Terrain (37.2) → architecture (37.4) → vegetation (37.3) → water (37.5) → dressing
(D83) → atmosphere (D110/D111) → lighting (Ch 22).
Optimization pass (Ch 26): LODs, instancing, texture budgets, culling.
Continuity: weather/time/palette systems consistent across shots (Ch 27.5).
37.2 TERRAIN GENERATION SYSTEMS
System How Best for Notes
GN procedural
terrain
stacked noise (fBm: scale/lacunarity/
persistence) → height → slope-based material
mask → erosion shortcuts (Voronoi cliffs)
hero + mid
terrain, infinite
variation
the professional standard
(D85); parameterize seed/
scale/roughness
Displace
modifier
noise texture displacement on a subdivided
plane
quick terrain,
tiling
use real heightmaps for
accuracy
Sculpted
terrain (D22)
sculpt large forms + micro-relief hero ground,
story-critical
terrain
most control, hand-made
Heightmap
import
GIS/World Machine/ANT (built-in add-on)
heightmaps → displacement
real-world
locations, large
regions
check resolution & scale
(D14)
Mixing sculpted hero + procedural mid + imported
distant
the production
recipe
blend at the seams
Terrain material recipe (slope + height — the classic):  height attribute → ColorRamp (low =
water/grass, mid = rock, high = snow); slope attribute (from normals) → mask (flat = grass, steep =
rock/cliff); mix → displacement + textures (Ch 17.5). Erosion logic (D80): water cuts valleys (mask
by flow direction), scree at cliff bases (mask by slope + height), vegetation follows moisture.
37.3 VEGETATION ECOSYSTEMS (GN scattering at scale)
The GN scatter recipe (D82/D85):  terrain surface → distribute points (density mask: painted/
height/moisture) → instance per-species assets (random scale/rotation) → distance culling (Ch 26) →
1. 
2. 
3. 
4. 
5. 
6. 
DEPTH CHAPTER 37 — ENVIRONMENT & TERRAIN DEPTH

wind sway (driven attribute, D99).  Species rules:  -  Trees: trunk (Sapling add-on / GN branch
recursion) + leaf canopy (instanced planes with alpha, or low-poly). LOD: canopy cards at distance. -
Grass: instanced blades/planes with wind sway; density falls off with distance (the #1 perf trick). -
Rocks: 2–4  sculpted  rocks,  random  scale/rotation;  or  procedural  (Voronoi  cluster  +  displace).  -
Ground cover: leaves, pine needles, flowers — scatter with color variation. - Moss/lichen: texture
mask + displacement on rock surfaces (Ch 17.5).
Biome palettes (D138):  each biome = its own species set + color palette (forest greens, desert
ochres, tundra whites) — keeps the world coherent (Ch 27.4).
37.4 MODULAR ARCHITECTURE (the kit system)
The kit: walls, corners, doors, windows, roofs, columns, stairs, trim — each a reusable asset (D84) at
standard grid scale  (e.g., 4 m modules). Assemble variations by combination; add  GN building
generators (D85: footprint curve → extrude floors → window grid → roof) for cities and background
rows. Scale discipline (D81): door ~2 m, floor ~3 m, stair rise ~17 cm — check with the blockman
(D16); architecture is designed against the character's scale (a 6-legged creature needs 5 m doors —
D05).  Materials  &  weathering  (Ch  17/34.5): stone/brick/wood  with  grime,  moss,  patina  —
buildings must look lived in (D83); the era/tech level from the world brief (D02) decides the material
palette.
37.5 WATER SYSTEMS (the full water toolbox)
Water body System Notes
Ocean/sea Ocean modifier (built-in: waves, choppiness, scale) +
water shader (D30/D94)
the standard; add foam/spray via particles
or shader mask
Lake/pond flat plane + ripple shader (wave texture animated) +
shore blend
cheap, beautiful
River/stream plane following terrain + scrolling shader + flow
normal
animated offset
Puddles (rain) planes with ripple shader + wetness drivers on the
ground (D99)
the rain-city essential (D94)
Waterfall vertical scrolling plane + foam + mist particles add sound (Ch 23)
Hero splash/
pour
fluid sim (D93) only when shader+particles fail (D88 rule)
Flooded
street
large reflective plane + depth fog (D110) reflections sell it (35/4.4)
Water  material  recap  (Ch  17.4): transmission  1,  IOR  1.33,  roughness  0–0.3  (calm→rough),
absorption for depth; reflections are 80% of water realism  — the sky/environment must reflect
(D108);  add  caustics  (light  patterns)  for  shallow  water  (Cycles  caustics  expensive  —  fake  with
shader).
37.6 ENVIRONMENT LIGHTING INTEGRATION (the world's
light)
The world light plan (Ch 22): time/weather from the brief → HDRI/sun → key direction for the
scene → interior vs exterior separation (interiors get window/practical light, D108).
• 
DEPTH CHAPTER 37 — ENVIRONMENT & TERRAIN DEPTH

Light shafts (D111): volumetrics through windows/trees — the money shot; one localized
volume domain (Ch 26).
Ambient occlusion: the AO pass grounds everything (D109) — never skip on environments.
Reflections: wet streets, glass, water — the environment's materials need the environment to
reflect (HDRI + geometry, D108).
Atmosphere (D110): mist pass for aerial perspective; fog color from the palette (Ch 27.4);
volumetrics budgeted.
37.7 ENVIRONMENT PERFORMANCE (the split that saves
you)
Zone Detail System
Hero (0–30 m, camera-tested) full detail, hero textures (4k), sculpted/procedural best assets hand-assembled
Mid (30–150 m) modular + procedural, LOD1, 2k textures instancing (D85)
Far (150 m+) LOD2/impostors, 1k or cards billboards (Ch 26)
Sky HDRI + clouds + sun world settings
The rules: never detail what the camera can't see (shot list is the budget, D10); instance everything
repeatable; bake procedural materials to textures for scattered assets (Ch 26.3); use  Simplify +
viewport LOD while working (D126).
37.8 ENVIRONMENT FAILURE MODES & FIXES
Symptom Cause Fix
World feels empty no set dressing (D83) add layers: ground/mid/high/atmospheric
T errain looks "noise soup" uniform fBm, no erosion logic slope/height masks + erosion (37.2)
Forest looks like carpet identical trees, no distance falloff randomize + culling + canopy LOD
Buildings float no foundation/contact detail plinths, ground plane merge, AO
Water looks flat no reflections/foam reflection + foam mask + shore blend
World too heavy to render no hero/background split the split (37.7) + instancing + LOD
Palette mush no world palette (D138) biome palettes (37.3) + grade (D119)
Scale errors no blockman checks scale master + blockman pass (D16)
• 
• 
• 
• 
DEPTH CHAPTER 37 — ENVIRONMENT & TERRAIN DEPTH
