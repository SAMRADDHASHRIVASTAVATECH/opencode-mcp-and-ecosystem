# Chapter 5 — Clothing, Armor, Props, Hair, Fur, Feathers (D37–D47)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 68–72 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 5 — CLOTHING, ARMOR, PROPS,
HAIR, FUR, FEATHERS
Domains D37–D47. Costume and grooming turn a character into a person and a creature into a being.
These systems carry heavy simulation and render costs — plan them at design time.
D37 — CLOTHING [SIT]
DEF: Designing and constructing garments for 3D characters: silhouettes, patterns, panels, and
materials — from design intent to animatable geometry. WHY: Clothing communicates era, culture,
climate, personality, and class (a "flowing cloak" vs a "taut tactical vest" tell different stories). It also
drives sim cost and rig complexity — the design must respect the budget.  HOW: 1.  Design with
fabric in mind: fabric weight (heavy wool drapes, silk flows, leather holds creases, armor is rigid) —
the  design's  silhouette  is  really  the  fabric's silhouette.  2.  Garment  blockout: build  over  the
character body (or a "dummy" copy) with loose-fit shells (2–8 cm clearance depending on fabric). 3.
Construction approach options:  -  Modeled  garments (sewn-together  panels  modeled  as  one
mesh) — for tight/stylized clothing; animates with the rig + corrective shapes. - Simulated garments
(cloth sim, D39) — for loose/flowing fabric; needs construction with seams and pinning. -  Hybrid:
modeled  base  +  simulated  loose  parts  (the  professional  standard:  coat  modeled,  skirt/hem
simulated). 4.  Pattern logic: real garments are  panels sewn at seams. Modeling with seam lines
(and shader-seam detail) looks real; a single "tube" garment looks fake. 5. Layering: underwear →
base layer → outer layer → armor/accessories; each layer needs its own clearance and sim setup. 6.
Garment construction details:  seams, stitching (bump/normal), buttons/zippers (D40), thickness
(Solidify),  collar/cuff/hem  structure,  fold  anticipation  (relaxed  folds  where  fabric  compresses).
PARAM: fabric type (density, stiffness, bending — D39); clearance per layer; panel count; seam
placement; hem weights; material (weave, roughness, sheen, D30). MIST: skin-tight everything (no
fabric logic); garments as one unbroken mesh (no seams/panels); ignoring thickness (cloth z-fights
with skin); designing garments the sim can't afford. FAIL: cloth interpenetrating the body (clearance
too small / sim bad); folded mesh at elbows (no extra loops). DIAG: pose the character in a bind pose
— check pinch points at armpits, elbows, knees, crotch. FIX: add fabric clearance; put fold-friendly
loop  density  at  compression  zones;  use  cloth  sim  only  where  it  pays.  EDGES: →  D38  cloth
construction, → D39 cloth sim, → D40 accessories, → D41 armor.
Deep chain — Clothing → Garment → Panels → Seams
Silhouette → fabric weight → panel layout → seam placement → stitching detail → hem → closure (buttons/
zippers/lacing) → wear & weathering
D38 — CLOTH CONSTRUCTION [SIT]
DEF: The  3D  tailoring  techniques  for  making  garments  that  simulate  and  deform  well.  WHY:
Simulated cloth is only as good as its construction: topology density, seam placement, and pinning
decide whether the sim looks like fabric or a jellyfish. HOW: 1. Sewing (the pattern approach):
model flat pattern pieces (like real tailoring), place them around the body, add  Cloth Sewing
Springs (D39) along seams, let the sim "sew" them shut — produces  realistic fit and draping.
Blender's cloth modifier supports sewing springs; garments can be sewn closed in a quick sim then
CHAPTER 5 — CLOTHING, ARMOR, PROPS, HAIR, FUR, FEATHERS

cached as a rest shape. 2. Modeled + sim approach:  model the garment as a closed shell around
the body; use the cloth sim only for motion (draping settled via a pre-sim). Faster, more controllable;
standard for production. 3. Topology for cloth: fairly even quads, denser where folds form (hems,
waist, sleeves); avoid poles on visible drape areas; keep density moderate (10k–50k faces typical) —
sim cost scales with vertex count. 4. Pinning: pin seams, shoulders, collars, waistbands to the body/
skeleton so the garment doesn't slide; pins are  anchors — everything below them is free. 5.  Rest
state: pre-simulate the garment to its draped rest (500–2000 frames of settling with high damping)
and cache that as the rest pose — never start shots from the flat state. PARAM: cloth vertex count;
seam/spring stiffness; pinning strategy; rest-state cache. MIST: starting sims from flat pattern state
(chaotic first frames); no pins (garment slides off); uneven topology (fold artifacts). EDGES: → D39
cloth sim, → D37 clothing.
D39 — CLOTH SIMULATION [SIT]
DEF: Physics simulation of fabric: gravity, bending, stretching, collisions with body and world. WHY:
Loose fabric's motion (drape, flow, snap) cannot be hand-animated believably — simulation is the
only practical way, and it's a secondary-motion powerhouse (D77). HOW (Blender Cloth modifier):
1. Setup: Cloth modifier on the garment mesh; choose preset (cotton/silk/leather/etc. — these set
stiffness/damping); add a  Vertex Group for pins (weight 1 = pinned). 2.  Key settings:  Quality
(steps per frame); Mass (heavier drapes more); Air Damping (fabric "float"); Bending Model (Linear
for most; Angular for heavier; see below); Stiffness (bending/tension/compression); Damping; Sewing
Springs (D38); Collisions: Self-Collision (fabric-fabric, ON for loose clothes), Collision Object (body/
world, with Distance & Friction; the body needs a  Collision modifier  or use the garment's own
collision collection). 3.  Baking: after settings are stable,  Cache → Bake  to disk (in the project's
cache folder, D123). Simulate to the shot length + 30–60 frames of lead-in so motion settles. 4.
Interaction with animation: cloth is driven by the character animation; always simulate after the
character animation is locked. Use the final mesh (or a simplified proxy collider mesh for speed). 5.
Troubleshooting fast: explosions (steps too few / collision distance too small); jitter (self-collision
distance too small / damping); sagging (stiffness low); sliding (pins missing). PARAM: preset; quality
steps; stiffness (bending/tension/compression); damping; mass; air damping; self-collision quality/
distance;  collision  distance/friction;  cache  settings;  pin  vertex  groups.  MIST: simulating  before
animation  lock  (re-sim  loops);  no  lead-in  frames;  self-collision  off  (fabric  passes  through  itself);
collision mesh = the full dense character mesh (slow) instead of a simplified collider.  FAIL: cloth
explosion (instability) — the #1 cloth failure.  DIAG: play the sim; explosion = numeric instability.
FIX: raise Quality steps; lower timestep; increase collision distance; increase damping; reduce vertex
count; pin more.  PERF: cloth sim is CPU; use simplified colliders; bake once; cache to disk; only
simulate visible garments. EDGES: → D37/D38, → D77 secondary animation, → D91 cloth physics, →
D99 env sim (wind!).
Deep chain — Cloth sim → Fabric → Motion → Collision
Fabric stiffness → gravity → draping → animation-driven acceleration → inertia → folds → snapping
(trailing edge) → wind → self-collision → final motion
D40 — ACCESSORIES [SIT]
DEF: Belts, straps, pouches, jewelry, scarves, goggles, weapon holsters, and character-specific gear.
WHY: Accessories sell  character (a smuggler's many belts, a scholar's satchel) and provide focal
CHAPTER 5 — CLOTHING, ARMOR, PROPS, HAIR, FUR, FEATHERS

points; they also add rigging complexity (they move with the body) — plan them. HOW: model as
separate meshes (parented/constrained to the skeleton — D53); simulate long dangly bits (scarf tails,
chains) with cloth/rigid constraints; use the  Asset Browser  to reuse common accessories (D84).
PARAM: parenting  (vertex  groups  or  bone  constraints);  collision  inclusion;  sim  budget.  MIST:
merging accessories into the body mesh (breaks rig); forgetting accessories in collision layers (chain
clips through cloak). EDGES: → D53 constraints, → D37 clothing, → D84 props.
D41 — ARMOR [SIT]
DEF: Protective gear: rigid plates (metal, chitin, bone) over a flexible under-layer. WHY: Armor is the
classic  hard-on-soft problem: rigid pieces must  not deform like cloth, but the body under them
moves. The technique is rigid pieces parented to the skeleton (or rigid-body constrained) + a flexible
under-suit. HOW: 1. Weight logic (D05 principle):  armor adds mass — a full-plate knight moves
differently  than  a  leather  scout  (affects  D66/D76  animation).  2.  Construction: separate  plate
meshes (hard-surface, D18); under-layer garment (cloth or modeled). 3.  Rigging armor:  plates
parented to bones (Copy Transforms / Child Of constraints, D53) with  local corrections; articulated
plate stacks (segmented cuirass, pauldron lames) need their own small bone chains so plates overlap
naturally as the body bends; straps/leather parts deform (weighted) or simulate. 4. Materials: metal
(D30)  +  wear  (scratches,  dents,  paint  loss  —  D26  maps);  contrasting  trim  (cloth/leather)  for
readability.  MIST: armor as a deformed part of the body mesh (plates bend like rubber); plates
intersecting at joints; armor heavier than the character's animation suggests. EDGES: → D18 hard-
surface, → D37 clothing, → D53 constraints, → D48 rig.
D42 — PROPS [SIT]
DEF: Held/handled objects: weapons, tools, cups, books, anything a character interacts with. WHY:
Props anchor hands and sell interaction; they are the most-rigged simple objects (every one needs a
hand-attach system).  HOW: model at real scale from reference (D07); rig with a  prop handle
(empty/bone) that hands snap to via constraints (D53); for simple props, parent to the hand bone
directly; simulate only if needed (sword sheath strap, cape).  PARAM: attachment point (handle,
grip); scale; collision (if simulated); LOD (D24). EDGES: → D84 props & assets, → D53 constraints, →
D18 hard-surface.
D43 — HAIR [SIT]
DEF: Curves-based hair on characters: grooming, styling, shading, and rendering (Blender's modern
Hair curves system — "Curves" objects with hair attributes; legacy particle hair still supported). WHY:
Hair is a huge identity feature (shape, color, movement) and a notorious cost center (thousands of
strands × physics × shading). It must be  groomed like real hair, not scattered randomly.  HOW
(curves hair workflow): 1. Add hair: select scalp mesh → Add → Curves → Hair (or use the "Hair"
particle system for legacy). The curves object has strands rooted on the mesh surface. 2. Grooming
(sculpt-like): in  Sculpt  Mode on  the  curves  object  use  grooming  brushes:  Comb (direction),
Smooth, Puff (volume), Pinch (clumping), Snake Hook (pull strands), Grow/Shrink (length), Roll
(curl), Twist (spiral). Use guides — a sparse set of control strands — to drive dense strands (guide-
follow). 3.  Density & children:  set Children (interpolated) count in the  Hair modifier / properties
(e.g., 100k–500k total strands for film; 10k–50k stylized/realtime); children derive from guides, saving
sim cost. 4. Curve types: use Bezier (smooth, sim-friendly) or Poly/NURBS (stiff styles); resolution
CHAPTER 5 — CLOTHING, ARMOR, PROPS, HAIR, FUR, FEATHERS

per  strand.  5.  Hair  material  (D30  variant): Principled  Hair  BSDF  (melanin-based:  Melanin
concentration (color), Melanin Redness, Roughness (gloss), Random Roughness, Absorption, Scatter,
IOR); or Principled BSDF with transmission for stylized strands. Alpha for strand cards (if using mesh
cards). 6. Styling: lengths, bangs, part lines (root direction), clumps (Pinch), waviness (Roll/T wist +
noise); keep  silhouette from the design sheet (D08).  PARAM: strand count; children; resolution;
guide count; material melanin/roughness; collision settings (D47).  MIST: uniform random hair (no
direction/grooming);  too  many  strands  (render  death);  hair  shading  without  melanin  (plastic);
ignoring the part line / gravity. FAIL: hair clipping through shoulders/neck (collision issues — D47);
noisy/aliased strands at distance (AA). PERF: use children + low-res guides; denoise; reduce strand
count for background; use viewport "strand display" simplification. EDGES: → D46 grooming, → D47
hair dynamics, → D30 materials (Hair BSDF), → D43→D08 sheets.
Deep chain — Hair → Groom → Guides → Detail
Scalp root map → guide placement → part line → direction → length → clumps → volume (puff) → curl →
flyaways → material (melanin) → dynamics (D47)
D44 — FUR [SIT]
DEF: Dense short hair covering creatures (mammals) — often procedural rather than hand-groomed.
WHY: Fur is a statistical surface: thousands of short tapered strands; its look comes from density,
length variation, clumping, and layering (undercoat + guard hairs).  HOW: 1.  Method choice: (a)
Curves hair with procedural length/curl via noise (fast to set up); (b) Geometry Nodes fur (instance
strand curves with attribute-driven length/direction/curl/clump — full control, reusable); (c) particle
hair (legacy); (d)  texture/alpha-card fur  (cheap, for distance or stylized). 2.  Layers: undercoat
(short, dense, fuzzy — high roughness) + guard hairs (longer, sparser, glossier). T wo systems or two
material variations. 3. Direction: follow the pelt map (grain of the animal: down the back, out at the
chest); use root rotation + noise. 4. Clumping: wet fur clumps; dry fur breaks into clumps by length
(use clump noise). 5. Materials: Principled Hair BSDF (melanin for natural colors; RGB for stylized);
roughness low (glossy guard) + high (undercoat). PARAM: density (per cm² — film 10k–50k strands/
cm²... scaled to total budget); length distribution; clump settings; color variation; dynamics (D47).
MIST: uniform fur (looks like carpet); no undercoat/guard layering; ignoring pelt direction; full-detail
fur on background creatures. PERF: fur is one of the most expensive things in rendering — budget
ruthlessly: distance-based density, child strands, viewport proxies. EDGES: → D46 grooming, → D47
dynamics, → D85 geometry nodes, → D114 optimization.
D45 — FEATHERS [SIT]
DEF: Feather construction and coverage for birds/avian creatures: flight feathers, contour feathers,
down. WHY: Feathers are individual blades with a spine (rachis) and barbs — they layer like shingles,
and wings need mechanical fold logic (D72). Done wrong, birds look like hairy blobs.  HOW: 1.
Feather asset:  model/curve one feather (rachis + vanes, tapered, slight curve); make variants
(primary flight feather long/asymmetric; contour feather round; down = fuzzy). 2. Coverage: place
feathers in rows (like real plumage) — overlapping shingles, direction from the body; use Geometry
Nodes instancing on the skin with attribute-driven rotation/size/curl (D85). 3. Wings: flight feathers
attach to the arm bones (they extend past the fingers — wing structure D72); primaries (outer, long),
secondaries (inner), coverts (overlapping, short) — each row has a transform hierarchy so the wing
folds like a fan. 4.  Material: feather shader = base color + iridescence (coat/anisotropy) + alpha
CHAPTER 5 — CLOTHING, ARMOR, PROPS, HAIR, FUR, FEATHERS

(vanes have gaps); down = fuzzy (high roughness, alpha noise). 5. Dynamics: feathers are rigid-ish
— they flap/fold with the wing (D47 hair dynamics works for soft flutter; wing fold is bone-driven).
MIST: feathers as a single furry surface (no individual feather identity); wings that don't fold (no row
hierarchy); ignoring alpha gaps. EDGES: → D72 flying creatures, → D46 grooming, → D85 geometry
nodes.
D46 — GROOMING [SIT]
DEF: The deliberate styling of hair/fur/feathers into a  designed shape  — the hair equivalent of
modeling. WHY: Random hair is never a hairstyle. Grooming transforms raw strands into a designed
silhouette (bangs, ponytail, mohawk, mane) that matches the character sheet.  HOW: guides-first
workflow: (1) place ~20–200 guides with Comb; (2) add children; (3) sculpt details (clumps, curls,
volume) on guides or full; (4) add dynamics (D47); (5) test in motion (hair that looks good static can
look wrong in motion — test early). Tools: Sculpt-mode grooming brushes (D43 list), Guides (control
strands), curve deform; for fur: procedural grooming (noise-driven) is standard; for hero hair: manual
grooming.  PARAM: guide count; child density; clump scale; curl; fringe; part; silhouette check vs
sheet.  MIST: grooming  without  the  character  sheet;  no  motion  test;  over-grooming  (unrealistic
perfection). EDGES: → D43/D44/D45, → D47 dynamics, → D08 sheets.
D47 — HAIR DYNAMICS [SIT]
DEF: Simulation of hair/fur/feather motion: inertia, gravity, wind, collision with body and world. WHY:
Static hair is fine for turntables; moving characters need hair that  reacts (head toss, run bounce,
wind) — a core secondary-motion element (D77).  HOW (Blender):  with Curves hair: add  Force
Fields (wind,  turbulence)  +  collision  objects (body  meshes  with  Collision  modifier,  or  use
"Collision" on a simplified proxy); enable dynamics in the hair properties (Pins = root scalp, Stiffness,
Damping, Mass); bake the simulation cache. Alternative: bone-driven "fake" hair (driver/curve-driven
sway  —  cheap,  stylized)  or  cloth on a hair proxy mesh  (blob  +  cloth  →  strands  follow  via
shrinkwrap/curve).  PARAM: stiffness  (bending);  damping;  mass;  pin  strength;  collision  distance/
friction; wind strength; bake length. MIST: full collision with the dense head mesh (slow); no collision
(hair sinks into shoulders); simulating before animation lock.  FAIL: hair exploding/teleporting (sim
instability — reduce speed, increase steps); hair "poking through" at high speed (collision distance
too small).  PERF: simulate only guides + children follow (huge savings); bake to disk; cap strand
count per shot; viewport preview with simplified display. EDGES: → D77 secondary animation, → D99
env sim (wind), → D92 hair physics.
CHAPTER 5 — CLOTHING, ARMOR, PROPS, HAIR, FUR, FEATHERS
