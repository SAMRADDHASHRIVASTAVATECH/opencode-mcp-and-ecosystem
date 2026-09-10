# Chapter 3 — Modeling, Anatomy, Sculpting, Retopology, Topology (D17–D24)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 57–61 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 3 — MODELING, ANATOMY,
SCULPTING, RETOPOLOGY, TOPOLOGY
Domains  D17–D24.  Modeling  converts  design  into  geometry;  topology  makes  that  geometry
animatable; sculpting adds life and detail. This chapter is the structural heart of the graph.
D17 — ORGANIC MODELING [SIT]
DEF: Modeling  smooth,  curved,  living  forms  (characters,  creatures,  plants,  soft  props)  using
subdivision-surface-friendly  methods.  WHY: Organic  forms  must  deform  (D58)  and  catch  light
smoothly; their geometry is therefore curvature-driven, not corner-driven. HOW (core techniques):
-  Box modeling (subdiv):  start from a primitive; add loops; shape with proportional editing and
Smooth; use a Subdivision Surface modifier (2 levels view, 3 render) for final smoothness. Model
the cage (low-poly) knowing the subdiv does the smoothing. - Edge flow for organic forms:  loops
follow muscle bands and creases (see D24); poles (3/5-edge) placed where least visible or least
deformed. -  Proportional editing (O):  push/pull large regions with falloff — the fastest organic
shaping tool. -  Sculpt-then-retopo: for complex organic forms (see D22/D23) — the default for
characters/creatures with real anatomy. - Curve-based organic: surfaces from curves for tentacles,
tails, vines (see also D85).  PARAM: subdiv levels (view/render); crease weights; edge creases for
sharp-ish organic corners; shade smooth + auto smooth normals; mirror modifier while modeling
(D19).  MIST: modeling  with  triangles/ngons  on  deformable  areas;  subdiv  on  non-quad  topology
(pinching); relying on sculpt detail in low-poly (see D28 baking). FAIL: pinching/puckering at poles
under subdivision. DIAG: view the subdiv cage — pinch = bad loop placement. FIX: move poles off
high-curvature zones; add support loops around creases; use crease weights sparingly.  EDGES: →
D24 topology, → D22 sculpting, → D58 deformation.
D18 — HARD-SURFACE MODELING [SIT]
DEF: Modeling  mechanical,  angular,  manufactured  forms:  robots,  armor,  vehicles,  architecture,
weapons, machines, props.  WHY: Hard surfaces need  sharp edges with bevel logic  and precise
dimensions; they read as "manufactured" through perfect symmetry, parallel lines, and controlled
bevels.  HOW (core techniques):  -  Box modeling + bevels:  model the blockout; add  Bevel
modifier for  controlled  edge  sharpness  (weight-based  or  angle-based);  Solidify for  thickness;
Mirror for symmetry. - Modifier stack discipline: mirror → bevel → solidify → subdiv (order matters;
see below). - Boolean workflows: add/subtract shapes via Boolean modifier (or Geometry Nodes);
then  clean up  (booleans leave n-gons and artifacts — repair with merge/cleanup, or use "exact"
solver + remesh). - Shrinkwrap + projection: for panels conforming to curved hulls. - Procedural
hard-surface: Geometry Nodes (D85) for repeated greebles, panel lines, vents, pipelines. - Creases
& bevel weights:  sharp edges via Edge Crease or Bevel weight attributes.  PARAM: bevel width/
segments; solidify thickness; boolean solver (exact vs fast); shade flat + auto smooth (hard surface
usually  flat-shaded  normals  with  bevels).  MIST: relying  on  booleans  without  cleanup  (broken
normals, n-gon pinching); beveling after subdiv (wrong bevel shape); forgetting thickness (paper-thin
walls catch light wrong). FAIL: boolean artifacts under subdivision; non-manifold geometry breaking
booleans.  DIAG: select  non-manifold  (Select  →  All  by  Trait  →  Non-Manifold).  FIX: cleanup  after
booleans;  use  bevel  weights;  check  normals  (Shift-N).  PROD: hard-surface  assets  are  the  most
CHAPTER 3 — MODELING, ANATOMY, SCULPTING, RETOPOLOGY, TOPOLOGY

reusable — build modular kits (panels, pipes, greebles) as asset libraries (D84).  EDGES: → D41
armor, → D81 architecture, → D84 props, → D85 geometry nodes.
Deep chain — Hard-surface workflow → Modifier stack → Result
Blockout → mirror → bevel(weight) → solidify → subdiv → shading (flat+auto smooth) → normals check →
texture-ready UVs
D19 — CHARACTER MODELING [REQ]
DEF: Modeling human/humanoid characters (and by extension any biped) to the design sheet, with
deformation-ready topology. WHY: Characters are the most demanding models: they must look right
from every angle AND deform believably through a full animation range (D58).  HOW: 1.  Setup:
import turnaround (D08) as background images in front/side views; set character height to real scale
(D14). 2. Start point options:  (a) box-model from a cube/cylinder; (b) base mesh from Blender's
default human or add-on base meshes (D135) — fastest for realistic bodies; (c) sculpt-first then
retopo (D22/D23) — best for stylized/original bodies; (d) procedural base (D85). 3. Symmetry: work
with a Mirror modifier (X axis) while modeling; finalize both sides via the modifier or apply. 4. Body
blockout: torso → pelvis → limbs (as tapered cylinders) → hands → feet → neck → head. Match
proportions  from  the  sheet  (head-height  grid,  shoulder/hip  widths,  limb  lengths).  5.  Facial
construction: the face is the highest-stakes surface (D24 facial topology): eye sockets, nose, mouth,
ear.  Model  eyes  open in  neutral;  keep  eyelids  as  their  own  loop  structures  for  blink  rigs.  6.
Subdivision-friendly  final: quads  everywhere  on  deformable  areas;  pole  placement  hidden;
support loops at creases (armpit, groin, elbow/knee insides). 7. Clothing-ready: keep a naked base
model; build garments over it (D37). PARAM: target polygon count; subdiv levels; proportion targets
from sheet; edge loop plan (see topology chains below); hand/foot detail level. MIST: modeling to the
front view only (profile/back invented); hands as mitten blobs (hands are always visible in acting
shots);  no  edge  loops  for  joints  (see  D24);  starting  detail  before  proportions  are  right.  FAIL:
deformation breaks at joints; face topology prevents expressions. DIAG: pose-test early — apply a
quick  armature  (auto-weights)  at  blockout  and  bend  the  joints.  FIX: fix  topology,  not  weights
(repeated weight fixes on bad topology are a money pit). EDGES: → D21 anatomy, → D24 topology,
→ D48 rig, → D25 UV.
Deep chain — Character modeling → Body parts → Topology regions
Torso → ribcage loops → abdomen → pelvis loops → hip crease Arm → shoulder deltoid loop → armpit pole
→ elbow inner/outer loops → wrist Leg → hip ball socket pole → thigh → knee loops → ankle loops
Hand → palm → finger loops (per finger 3-4 segments) → thumb rotation loop Head → brow loops → eye
ring (16-20 verts) → nose bridge → mouth ring (24+ verts) → chin loops → neck
D20 — CREATURE MODELING [SIT]
DEF: Modeling non-human life from the creature spec sheet (D05): original anatomy, unusual limbs,
surfaces,  proportions.  WHY: Creatures  are  where  modeling  logic  is  tested  hardest  —  invented
anatomy  must  still  look  believable (structure,  mass,  joint  logic).  HOW: Follow  the  same  sub-
processes as characters but driven by the  creature spec: 1.  Silhouette-to-mass: start with the
mass primitives (head/torso/limb blocks) matching the spec's proportions; verify silhouette against
the design thumbnail (D04/D05). 2. Spine logic first: creatures live or die by their spine (curvature,
segment count, tail extension). Model the spine curve before limbs; limbs attach to it at correct
CHAPTER 3 — MODELING, ANATOMY, SCULPTING, RETOPOLOGY, TOPOLOGY

angles. 3. Limb count & joints: n legs → n× joints; decide joint schemes (digitigrade vs plantigrade
vs extra joints) at blockout, because rigging (D48) and animation (D69) depend on it. 4.  Surface
layers: sculpt skin/scales/fur base (D22) or model plates/spikes/chitin as hard-surface (D18) on the
organic body. 5.  Extras with purpose:  horns/antlers (real attachment logic), mandibles (rigged),
wings (fold/wing structure — D45), tails (weight logic).  Creature-specific topology notes:  long
flexible parts (tails, tentacles, necks) want even loop distribution  (no sudden loop compression);
wings need fold line topology; multi-leg creatures need pelvis-less "body loop" topology where each
leg has its own socket loop; gills/mandibles need separate mesh pieces with their own rigs. MIST:
treating creature like a human with a costume (wrong mass logic); joint count that rigging can't
support; tail topology with poles at the flex point.  DIAG: silhouette test at 3 sizes; pose test at
extreme ranges.  EDGES: → D05 creature design, → D22 sculpting, → D69–D73 movement, → D45
feathers/D44 fur.
D21 — ANATOMY [SIT]
DEF: The structural logic under the surface: skeleton (proportions, joints, ranges), muscles (mass,
attachment,  function),  fat  (distribution),  and  surface  landmarks.  WHY: Anatomy  is  why  realistic
characters  read  as  human  and  creatures  read  as  functional.  Stylized  art  still  needs  simplified
anatomy — caricature is anatomy with exaggeration. Nothing looks "off" quite like bad anatomy.
HOW: 1. Learn the landmarks:  the visible bone/fat landmarks that drive topology and sculpting:
clavicle,  acromion,  iliac  crest,  ASIS,  patella,  tibia  crest,  spine  of  scapula,  7th  cervical  vertebra,
mastoid, brow ridge, zygomatic arch, jaw angle. 2. Proportions (adult human, head = unit): total
≈ 7.5 heads; nipples ≈ head 2; navel ≈ head 3; pubis ≈ mid-point; knees ≈ head 4.5; wrists at pubis
level; hands ≈ 0.9 head; foot ≈ 1 head; shoulder width ≈ 2 heads; hip width ≈ 1.5–2 heads. 3.
Muscle logic (learn as form, not names):  mass groups that matter visually: deltoid (shoulder
cap), pectorals, abs (6-pack = 2 columns × 3), obliques, trapezius (neck slope), latissimus (back
wings),  gluteals,  quads,  hamstrings,  calves  (gastrocnemius),  biceps/triceps,  forearms  (extensors/
flexors). 4. Skeletal ranges (for rigging, D49):  elbow ≈ 140–150° flex, near 0 extension; knee ≈
130° flex, ~5° hyperextension; hip flex ≈ 120°, extension ≈ 20°; shoulder huge range (ball & socket);
wrist ≈ 70° flex, 60° ext; neck ≈ 60° total; spine segments (cervical 7, thoracic 12, lumbar 5 —
animators  only  need  the  curves:  cervical  lordosis,  thoracic  kyphosis,  lumbar  lordosis).  5.  Fat
distribution: differs by age/sex/body type — cheeks, chin, belly, hips, thighs; drives secondary
forms. 6. Style adaptation: anime/cartoon = simplified landmarks + exaggerated features; realism
= full anatomy; creatures = equivalent structures by analogy (quadruped scapula, digitigrade hock =
human  ankle  analog).  MIST: memorizing  muscle  names without  forms;  symmetrical  "statue"
anatomy (no asymmetry); ignoring the skeleton when modeling the head (skull drives the face).
EDGES: → D19/D20 modeling, → D22 sculpting, → D49 skeleton design, → D66 locomotion.
Deep chain — Anatomy → Region → Structure → Landmark
Head → skull → cranium → brow ridge → zygomatic → maxilla → mandible → jaw angle Torso → ribcage →
sternum → costal arch → pelvis → iliac crest → sacrum → spine curves Limbs → shoulder girdle → scapula
→ humerus → radius/ulna → wrist → hand arch
D22 — SCULPTING [SIT]
DEF: High-poly digital sculpting: building form and detail like clay, in Blender's Sculpt Mode. WHY:
Sculpting is the fastest way to create organic truth — anatomy, asymmetry, folds, pores — that box
CHAPTER 3 — MODELING, ANATOMY, SCULPTING, RETOPOLOGY, TOPOLOGY

modeling can't reach. It's the default for characters, creatures, and organic environments. HOW (the
three-form  hierarchy): 1.  Primary  forms: the  big  masses  (head  sphere,  torso  block,  limb
cylinders) — the silhouette. Use basic primitives + Draw/Drag/Clay Strips brushes with large sizes
and strong falloff. 2. Secondary forms: anatomical structure — muscles, bone landmarks, fat pads.
Clay Strips, Clay, Crease, Inflate, Pinch, Flatten  brushes. 3. Tertiary details: pores, wrinkles,
scales, scars, fabric folds —  small brushes + alphas (stamps) ; done  last, only after forms are
approved.  Key tools & settings:  -  Dyntopo (dynamic topology):  adds topology on demand
where you sculpt — great for exploration, terrible for final (messy mesh). Use for concept sculpts,
blockouts. -  Voxel Remesh: uniform density remesh — the workhorse for organic sculpting (keep
remesh size small enough for detail, large enough for performance). -  Multiresolution modifier:
subdivision-based sculpting on a base mesh — keeps a clean base (retopo-friendly) with subdivision
levels for detail; the professional character workflow (sculpt at level 1-2, detail at higher levels). -
Symmetry: sculpt with symmetry (X) for the base, then turn it OFF for final asymmetry pass (life is
asymmetric). - Masks: protect regions (mask brush, box mask, Lasso mask); hide/unhide geometry
for focused work. - Brushes to know: Draw, Clay Strips, Clay, Crease, Inflate, Blob, Smooth, Flatten,
Pinch, Grab, Elastic Deform (great for moving masses), Snake Hook (pull spikes/tendrils), Cloth brush
(fabric folds!), Pose brush (blocking poses), Move (drag topology). - Alphas: stamped texture detail
(pores, scales, skin) via brush texture; make your own or use texture libraries. -  Brush settings:
radius (F), strength (Shift-F), falloff curve, brush texture, symmetry, auto-masking (topology/face
sets). -  Face Sets: painted regions for organizing/isolating (eyes, mouth) and for masking/polish
passes. WORKFLOW (sculpt-first): blockout primitives → voxel remesh or multires → primary forms
→ secondary forms → tertiary detail → decimate/retopo (D23) → bake detail (D28) or use multires
directly (with care). PARAM: dyntopo detail size; voxel size; multires levels; brush strength/radius;
auto-smooth; tablet pressure (use a tablet!).  MIST: sculpting detail on unapproved primary forms
(wasted hours); symmetric final sculpt (lifeless); dyntopo for final meshes (unusable topology); too
much tertiary detail too early.  FAIL: mesh explosion (dyntopo runaway), remesh destroying detail
(remesh  size  too  large).  DIAG: undo/redo  history;  check  remesh  size  vs  brush  size.  FIX: save
incremental sculpt versions (D124); remesh progressively (coarse → fine); enable undo steps high for
sculpting.  PERF: dyntopo/remesh on millions of verts is slow — use decimation before heavy ops;
sculpt  with  multires  levels  for  speed;  hide  unneeded  parts.  EDGES: →  D23  retopology,  →  D24
topology, → D28 baking, → D19/D20 modeling.
Deep chain — Sculpting → Detail hierarchy → Micro-detail
Primary forms → silhouette approval → secondary forms → anatomy approval → tertiary → pores/scales/
wrinkles → alphas → skin detail Brush → falloff curve → strength → radius → texture(alphas) → stroke
method (anchored/drag/airbrush) → auto-masking
D23 — RETOPOLOGY [SIT]
DEF: Rebuilding a clean, low-poly, animation-friendly mesh on top of a sculpt (or dense mesh). WHY:
Sculpts (especially dyntopo) are not animatable: messy topology, billions of triangles. Retopology
produces the cage that rigs deform and textures use. It is where modeling quality meets animation
performance. HOW (in Blender): 1. Prep: decimate the sculpt if huge (Decimate modifier, collapse,
0.2–0.5 ratio) — only for retopo reference; keep the original for baking. 2. Retopo tools: use Snap
to Face + Shrinkwrap modifier so new verts stick to the sculpt; draw with the Poly Build tool
(fastest for quads), or B-Spline/curves → convert, or the RetopoFlow-style add-ons (external). 3.
Topology plan first: decide loop paths from the deformation map (D24): joint loops, facial loops,
muscle bands. Retopo is drawing the topology , not "covering the surface." 4. Density map: dense
where detail/deformation demands (face, hands, joints), sparse elsewhere (back, thighs, torso core).
CHAPTER 3 — MODELING, ANATOMY, SCULPTING, RETOPOLOGY, TOPOLOGY

5.  Check: subdiv  preview  to  confirm  smoothness;  pole  placement  check;  non-manifold  check;
mirrored half → mirror + weld. PARAM: target poly count; quad dominance; loop paths; density map;
snap settings (face, 0.01 offset); mirror axis. MIST: retopo without a plan (random quads); uniform
density everywhere (wasted polys, bad deformation); ignoring joint areas.  FAIL: subdiv artifacts
(pinch) from bad loops; non-manifold edges.  DIAG: Select → All by Trait → Non-Manifold; Mesh
Analysis overlay. FIX: redo the offending region — retopo is cheap to redo locally, expensive to redo
globally; always retopo with the rig in mind. EDGES: → D24 topology, → D48 rig, → D25 UV, → D28
baking.
D24 — TOPOLOGY [REQ]
DEF: The arrangement of vertices/edges/faces — the circuit board of a mesh. Good topology = clean
deformation, clean subdivision, clean UVs, good performance.  WHY: T opology is the single most
underestimated determinant of animation quality. The same surface shape can deform beautifully or
shatter depending on edge flow.  Core rules:  1.  Quads are the unit.  Quad-dominant meshes
subdivide cleanly, deform predictably, and map/rig predictably. Triangles/ngons are allowed in flat,
undeformed, un-subdivided areas (eyes of a blade, flat panels). 2. Loops follow form.  Edge loops
should run along creases, muscle bands, and joint flex lines. Loops across a bend direction = pinching
when bent. 3. Poles (3- and 5-edge junctions) redirect flow. Use them to turn loops (e.g., at the
armpit, elbow, mouth corner). Place poles in low-deformation, low-visibility spots. 4. Even spacing
along flex zones. A joint needs evenly distributed loops so the bend doesn't "crumple" — 3–5 loops
around elbow/knee/finger. 5.  Density follows need:  face/hands/joints dense; torso/back sparse;
never more geometry than needed (render + performance cost). Deformation topology (the key
patterns): - Elbow/knee: 3–5 concentric loops around the joint; a pole on the outside of the bend
redirects the fold. -  Shoulder: loop over the deltoid cap; armpit pole (5-pole) lets the arm swing
without tearing the chest. - Hip: loop around the leg socket; fold line across the groin. - Spine/torso:
vertical  loops  (10–14)  that  can  bend  forward/back/side;  belly  crease  loops  for  sitting.  -  Neck:
horizontal loops so the neck can tilt; jaw loop separating head/neck. Facial topology (the crown
jewel): - Eye: complete ring loop around each eye (16–24 verts) so blinks deform the ring; radial
loops from the ring. - Mouth: complete ring around the mouth (24+ verts) for lip shapes; corner pole
where upper/lower lip loops meet (the mouth corner must "hinge"). - Brow: horizontal loops over the
brow for raising/furrowing. - Cheek/nose: loops following the smile muscle path (from mouth corner
up the cheek). - Jaw: loop along the jawline separating face from neck. Mesh density & LOD: - LOD
(Level of Detail): several versions (high/mid/low) with decimated or remade geometry; use for far
objects / realtime. - Polygon budgets (D14) are set per asset class; film characters 50k–250k triangles
(with subdiv), realtime 5k–50k.  MIST: uniform grid topology (ignores deformation); poles at joint
bends; triangles in the face; over-modeling (every surface a million verts).  DIAG: bend-test every
joint in a quick rig; subdiv-preview for pinching; use the Mesh Analysis overlay for ngons/triangles.
FIX: re-topo the failing region; never "fix" deformation by adding weight paint on bad topology (it's
treating the symptom). EDGES: → D23 retopology, → D48 rig, → D58 deformation, → D25 UV.
Deep chain — Topology → Region → Pattern → Detail
Joint loop → elbow → outer pole → inner fold loops → spacing → density Face → eye ring → blink loops →
brow loops → mouth ring → corner pole → cheek fan → jaw loop Transition → loop reduction → pole
placement → hidden zones → subdiv preview → bend test
CHAPTER 3 — MODELING, ANATOMY, SCULPTING, RETOPOLOGY, TOPOLOGY
