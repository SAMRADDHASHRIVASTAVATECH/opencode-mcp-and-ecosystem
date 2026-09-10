# Depth Chapter 33 — Hair, Fur & Feathers Depth

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 203–206 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 33 — HAIR, FUR & FEATHERS
DEPTH
Expands  D43–D47.  The  complete  strand-craft:  curves-hair  system  workflow,  grooming  brushes,
strand materials, styling patterns, GN fur recipes, feather construction, dynamics tuning, budgets,
and stylized variants.
33.1 THE CURVES HAIR SYSTEM (full workflow)
Creation: select the scalp/skin mesh → Add → Curves → Hair (or the legacy particle system for old
pipelines). The curves object roots strands on the mesh surface. Key pipeline: (1) grow (count) → (2)
groom guides → (3) add children → (4) style detail → (5) shade → (6) dynamics → (7) render. Core
parameters (Curves properties / Hair modifier):  - Count / Children:  total strands = guides ×
children. Film hero hair: 100k–500k total; stylized: 10k–50k; background: 1k–5k. Children interpolate
between guides (saving sim/render cost). - Strand resolution: segments per strand (4–8 typical; 8+
for curls/softness). - Root radius / tip radius:  taper (the hair taper is what makes it look like hair,
not wire). -  Length: from the groom (Grow/Shrink brushes). -  Material: the hair BSDF (33.3). -
Display: viewport strand display (simplify, "Children" display count) for interactivity (Ch 26).
33.2 GROOMING BRUSHES (the styling language)
Brush What it does Use
Comb pushes strands along the stroke direction, part lines, flow
Smooth evens strand density/direction cleanup, merging clumps
Puff adds volume outward body/volume (avoid flat "helmet" hair)
Pinch pulls strands together clumping (wet look, defined strands)
Snake Hook pulls a tuft out flyaways, spikes, wisps
Grow / Shrink lengthen / shorten length styling, fringe
Roll curls strands around their axis waves, curls
T wist spirals the strands ringlets, spirals
Randomize adds noise natural variation (final pass)
Scale adjusts strand width taper control
Workflow: guides first (20–200): Comb the direction (gravity + part line), Puff for volume, Shrink/
Grow  for  length;  then  children;  then  detail  brushes  (Pinch  clumps,  Roll  curls,  Randomize  for
naturalism); always finish with a Smooth pass.  Style to the character sheet silhouette (D08) and
test in motion early (D46) — static-perfect hair often dies in motion.
33.3 STRAND MATERIALS & SHADING
Principled Hair BSDF (the film standard):  -  Melanin: color by melanin amount (0 = white/
platinum,  1  =  black)  +  Melanin  Redness  (0–1:  red/gold  tones  —  eumelanin  vs  pheomelanin).  -
Roughness: gloss level (0.05–0.3 glossy hero hair; higher = matte/frizzy). - Random Roughness:
DEPTH CHAPTER 33 — HAIR, FUR & FEATHERS DEPTH

per-strand variation (0.1–0.5 — kills the "CG plastic wig" look; always > 0). - Absorption / Scatter /
IOR: light behavior inside strands — higher absorption = darker, richer; scatter = the soft glow on
thin edges. -  Alternative for stylized:  Principled BSDF with transmission (strands as translucent
cylinders) — good for toon hair with strong color control; or plain emission for anime streaks (Ch 18).
Alpha/card hair (stylized/realtime):  flat planes with alpha textures (hair strand cards) — cheap;
use for anime hair, game LODs. The texture does the strand look; cards face the camera (billboard) or
cross-hatch.
33.4 STYLING PATTERNS (the catalog)
Style Technique Notes
Straight/level Comb down, Smooth, even length needs volume (Puff) or it's a helmet
Part line Comb from the part in both directions the part is the origin — start grooming there
Bangs/fringe Grow short over the forehead, comb forward keep the forehead loop clean
Ponytail Gather → grow long → comb back → Pinch at the
tie
the tie is a pin for dynamics (33.7)
Braids T wist/Roll in segments + Pinch segment rotation sells the braid
Curls Roll/T wist with decreasing radius toward tip curls need high strand resolution
Mohawk/
undercut
Grow center, Shrink sides contrast sells it
Wet look Pinch clumps hard + glossy material (R 0.1) clumps + low roughness
Flyaways Snake Hook wisps at the hairline/crown the "alive" final pass
Updo/bun Gather + twist + Grow short on top dynamics: the bun is heavy, the neck
moves
33.5 GN FUR RECIPES (procedural fur — D44)
The base recipe (Geometry Nodes on the skin mesh): distribute points on surface (density from
a painted mask or height) → for each point: instance a strand curve (length from noise/attribute;
direction = surface normal + pelt-grain vector + curl noise) → set root/tip radius → children via the
curve  "children"  or  instanced  sub-curves  →  material  (Hair  BSDF).  The  pro  layers: (1)  pelt
direction: a vector attribute painted on the skin (or from a flow field) — fur follows it (down the back,
out at the chest); (2) undercoat vs guard:  two systems — short dense fuzzy (high roughness) +
long sparse glossy; (3)  clumping: group strands by noise, offset toward the clump center (wet
clumps  tighter);  (4)  length/color  variation: noise  attributes  per  strand  (tortoiseshell,  tabby,
gradient); (5)  distance culling: density falls off with camera distance (Ch 26) — the #1 fur perf
trick.  Budgets (film): 10k–100k strands/cm²-equivalent... in practice: 500k–5M total strands for a
hero mammal; 50k–200k for background. Realtime: 10k–50k or cards.
33.6 FEATHERS (construction & instancing)
Feather asset: a curve (rachis) + tapered vanes (mesh or alpha plane); make 3–5 variants (primary
flight: long, asymmetric; contour: short, round; down: fuzzy). Placement: GN instancing on the skin:
rows along the wing/body (direction = growth map), attribute-driven size/rotation/curl per feather;
row hierarchy for wings (D45/D72):  primaries attach to the  hand bones, secondaries to the
forearm, coverts layered over — each row is a separate instancing system parented to its bone group
DEPTH CHAPTER 33 — HAIR, FUR & FEATHERS DEPTH

so the wing folds like a fan (28.7). Material: base color + coat (iridescence via coat color/anisotropy)
+ alpha (vane gaps — the alpha is what makes feathers read as feathers); down = high roughness +
alpha noise.
33.7 DYNAMICS TUNING (hair/fur/feather motion)
Parameter Effect Starting values
Pins (root vertex
group)
which strands stay
attached
roots = full pin (1.0)
Stiffness (bending) resistance to bending 0.1–0.5 (soft hair) to 1.0 (stiff fur)
Damping energy loss (settle) 0.5–1.0; too low = endless jiggle
Mass inertia per strand higher = heavier, slower
Collision (body) strands don't sink body mesh with Collision modifier (or proxy); distance 0.5–2
cm
Wind/turbulence (D88) environmental motion wind strength 0.1–2; turbulence for life
Gravity strand weight default; reduce for "weightless" styles
Baking: bake to disk (project cache folder, D123) after animation lock; simulate guides + children
follow (huge  savings);  pin  ponytail/braid  ties  (33.4);  test  every  hairstyle in  a  head-toss  before
production.  Fake  dynamics  (stylized/realtime): driver-based  sway  (Ch  19  recipe  style:
sin(frame*freq)*amp  per control strand, attenuated by distance from root) — the "hair sway" cheat
that never explodes; vertex/curve deform with noise (D85).
33.8 BUDGETS & PERFORMANCE (the honest table)
Target Strands System Render
Film hero hair 100k–500k Curves + children Cycles (Hair BSDF), 3–8 samples extra
Film hero fur 500k–5M GN fur Cycles; heavy — LOD by distance
Stylized film 10k–50k Curves EEVEE/Cycles; cheap
Realtime character 1k–10k strands or cards Cards/GN low EEVEE/engine (Ch 25)
Background creature 1k–5k Low-density curves anything
Feathers (hero bird) 200–2000 feathers GN instances Cycles; alpha-heavy
Perf  levers  (Ch  26): distance  culling,  child  strands  (not  full),  strand  display  simplification  in
viewport, bake dynamics, denoise (Hair BSDF is noisy at low samples), separate hair render pass
(D115) for comp control.
33.9 STYLIZED HAIR (the art of not-real)
Toon/anime: cards or low-poly strands with solid colors (Ch 18 palette); the "2-piece" hair (base
+ highlight piece); sharp clumps; no physics or simple sway.
Cartoon: few big strands (3–5 visible clumps); strong silhouette; squash-friendly (stretches with
the head — rig the hair bones loosely, D28.8).
Silhouette-first: stylized hair is read from the silhouette — design the hair shape like a character
accessory (D04), then groom to it.
• 
• 
• 
DEPTH CHAPTER 33 — HAIR, FUR & FEATHERS DEPTH

33.10 HAIR/FUR/FEATHERS FAILURE MODES & FIXES
Symptom Cause Fix
Hair sinks into shoulders no/wrong collision Collision modifier on body proxy; check distance
Strands explode/teleport sim instability lower speed, raise steps, damp more, check scale
(D14)
"Plastic wig" look no Random Roughness / no
variation
Random Roughness 0.2+, strand width taper, color
variation
Fur looks like carpet uniform length/direction pelt map + length noise + clumping (33.5)
Feathers look like hairy
blob
no individual feather identity/
alpha
alpha + rows + direction (33.6)
Render too slow full strands everywhere children + culling + separate pass (33.8)
T oon hair too shiny physical gloss in toon shader flat colors, no coat (33.9)
Hair jiggles forever damping too low damping 0.8+, bake, test
DEPTH CHAPTER 33 — HAIR, FUR & FEATHERS DEPTH
