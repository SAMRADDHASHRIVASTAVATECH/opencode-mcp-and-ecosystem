# Chapter 6 — Rigging, Skeletons, Skinning, Deformation (D48–D59)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 73–79 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 6 — RIGGING, SKELETONS,
SKINNING, DEFORMATION
Domains  D48–D59.  Rigging  turns  a  model  into  a  puppet:  a  skeleton  the  animator  controls,
deformation that behaves, and a control system that's a joy (not a chore) to use.
D48 — RIGGING [REQ]
DEF: Building the control system that animates a model: armature (skeleton), constraints, drivers,
controllers, and deformation setup. WHY: The rig is the interface between animator intent and mesh
motion. A great rig makes animation fast and expressive; a bad rig makes every shot a fight. Rig
quality is measured in animator hours. HOW (the rig architecture):
MESH ──(armature modifier, weights)──▶ DEFORMATION SKELETON (deform bones)
DEFORMATION SKELETON ◀──(constraints)── CONTROL RIG (controllers, IK/FK)
CONTROL RIG ◀──(bone parenting/constraints)── ROOT/MASTER controls
Deformation skeleton: bones that actually move the mesh (named with .def  or similar suffix).
Control rig: extra bones/empties the animator touches; they drive the deform bones via
constraints (D53) — never animate deform bones directly.
Master control: top-level control (root) for whole-character placement; then spine/chest/hip/
head; then limbs; then fingers; then face. Rig types:
Basic FK rig: bones parented in a chain; rotate each (D52) — simple, arcs naturally; good for
tails, spines, tentacles.
IK rig (D51): target-based limbs; hands/feet stay planted; the default for legs/arms.
IK/FK switch: both, blended by a control (the professional standard for limbs).
Mechanical rig: bone chains with constrained axes, pistons (D50/D53), no soft deformation.
Hybrid/organic: FK spine + IK limbs + dynamics blends (D54) — the "next-gen" standard. 
Design rules: 1. Name everything with a strict convention (D49) — rigs with random names
are unusable. 2. One control = one job; controls readable by shape (D55 custom shapes). 3. 
Scale-consistency: controllers in world/character space; avoid gimbal issues by orienting bones
correctly (D49). 4. Test rigs with animator poses (contact, extreme stretch, sitting) before
signing off — "rig approval" is a gate (Part 1). PARAM: bone hierarchy; constraint graph; control
shapes; IK/FK switches; stretch systems; facial rig (D60); custom properties (D54). MIST:
animating deform bones directly; no naming convention; controls with no custom shapes; IK/FK
switch missing; rigging before topology is right. FAIL: gimbal locks (bone orientation); constraint
loops; over-constrained controls (animator fights the rig). DIAG: pose test; try the rig in Pose
Mode; check for "dead" controls. FIX: iterative rig building with constant animation tests; keep
the rig file separate from animation files (D123). EDGES: → D49 skeleton, → D50 bones, → D51–
D55 systems, → D56/D57 skinning, → D60 facial.
Deep chain — Rigging → Hierarchy → Control → Deformation
Master → root → pelvis → spine → chest → neck → head  and  → shoulders → arms → hands → fingers
Control bone → constraint (copy/limit/track) → deform bone → vertex group weights → mesh
• 
• 
• 
• 
• 
• 
• 
• 
CHAPTER 6 — RIGGING, SKELETONS, SKINNING, DEFORMATION

D49 — SKELETON DESIGN [REQ]
DEF: The armature's bone layout: joint placement, bone orientation, hierarchy, and naming — the
anatomy of the rig. WHY: Joint placement = where the model bends; orientation = whether rotations
behave (gimbal-free); naming = whether anyone can work on the rig. All three are decided before
adding  controls.  HOW: 1.  Joint  placement  (edit  mode): match  real  anatomy  for  realistic
characters (D21): elbows at the true elbow, knees at the true knee, spine bones on the spine curve,
fingers at knuckles. For stylized, exaggerate  proportionally (big head = neck lower, etc.).  A joint
misplacement of 2 cm = a decade of "something feels off." 2. Bone orientation (the critical
skill): each bone's Y-axis (Blender: bones point +Y) should point along the limb toward the next joint;
the Z axis (roll) should be aligned so that limb flex happens around a clean axis. Use Roll (N panel /
R-R in edit mode) to set; test flex after each limb. Mismatched rolls → poles, gimbal chaos, weird
twisting. 3. Hierarchy (the tree): root → pelvis → spine chain → chest/neck/head; clavicles → arms →
forearms → hands → fingers; pelvis → legs → feet → toes. Bones parent down the chain; the root is the
whole  skeleton's  handle.  4.  Naming  convention  (adopt  one,  enforce  it):  -
[side]_[bone]_[purpose]  — e.g., L_UpperArm , R_Hand , or with .L / .R  suffix; Blender 4.x supports _L /
_R  symmetry  naming  (.L / .R  recognized  by  Symmetrize).  -  Suffixes:  .def  (deform),  .ctrl
(control),  .ik / .fk  (mode),  .mch  (mechanism/helper),  .jnt  (joint),  .end  (tip),  .root ,  .org
(original). - Example set: L_Foot_IK , L_Foot_FK , L_Foot.def , L_Toe.def , Spine_1..5 , Chest , Neck_1 , 
Head ,  Jaw . 5.  Bone collections (Blender 4.x, formerly bone groups): organize bones by function
(Deform, Controls, Face, Mechanics);  assign bones to collections  so you can toggle visibility in
Pose  Mode;  color-code  collections.  PARAM: joint  positions;  roll  angles;  hierarchy;  naming;  bone
collections. MIST: random rolls (the #1 rigging failure); joints off anatomical position; naming chaos;
everything in one bone collection. DIAG: bend each joint — if the limb flexes with unwanted twist/
rotation, the roll is wrong. FIX: fix rolls in Edit mode before weight painting; re-test; document the
naming legend in the project docs (D123). EDGES: → D48 rig, → D50 bones, → D56 weights, → D21
anatomy.
D50 — BONE SYSTEMS [REQ]
DEF: The catalog of bone types and their jobs inside a rig: deform, control, mechanism, mechanical,
helper. WHY: Every bone has a purpose; mixing purposes muddies the rig. Understanding bone types
= knowing what to add when a requirement appears (twist, stretch, mechanical piston, tail follow-
through).  Bone types:  -  Deform bone ( .def ): actually moves mesh (weighted). Keep deform
bones  simple — the mesh follows them directly. -  Control bone ( .ctrl ): animator-facing; drives
others via constraints; never weighted to the mesh (usually). - Mechanism bone ( .mch ): invisible
helper  between  control  and  deform  (computation  node:  e.g.,  an  IK/FK  blend  calculation).  -
Mechanical bone:  rigid,  axis-limited  (pistons  need  single-axis  translation);  for  robots/machines
(D18).  -  Helper/utility  bones: root,  pole  targets,  aim  targets,  look  targets,  props  handles.
Specialized systems (the deep stuff):  -  Twist bones: distribute forearm/thigh twist smoothly
(two twist bones with progressive influence) — prevents the "screwed-up forearm" deformation. -
Stretch/Squash system: a stretchy chain (with Stretch T o / IK stretch) lets limbs elongate (cartoon/
stylized squash & stretch, D65); controlled by a custom property (D54). - Bendy bones (BBone):
spline-interpolated chains — a  single bone can curve (great for tails, spines, tentacles, hair) via
segments  +  curve  settings  (Ease,  In/Out).  Powerful  and  cheap  —  master  BBones.  -  Piston/
mechanical: a bone constrained to slide along an axis; driven by another bone's rotation (drivers,
D54) for gears/pistons. - Ribbon/spine: chains of bones constrained along a curve or "ribbon" mesh
for organic spine motion. PARAM: bone lengths; segments (BBone); constraints; drivers; collections.
MIST: one giant bone for a flexible tail (needs segments/BBones); twist handled by a single rotating
CHAPTER 6 — RIGGING, SKELETONS, SKINNING, DEFORMATION

bone (mesh screws); no mechanism layer (rig gets tangled). EDGES: → D48–D49, → D51–D55, → D58
deformation.
D51 — IK (INVERSE KINEMATICS) [SIT]
DEF: A limb system where the end (hand/foot) is positioned directly and the chain solves the joint
angles (the opposite of FK). WHY: Feet must stay planted on the ground and hands must hold objects
while the body moves  — IK makes this trivial; FK would require solving every joint by hand. HOW
(Blender): IK constraint on the last bone of a chain, targeting a pole target (empty/bone) that
controls the knee/elbow bend direction; chain length defines how many bones solve.  Pole target
(pole vector) must be placed in the plane of the limb or the knee flips. Node card — IK: - DEF: end-
point-driven limb solving. - WHY: ground contact, object contact, ease of posing. - USE: legs, arms
(with hand props), mechanical arms, tentacles (chain IK), multi-leg creatures (D71). - AVOID: arcs (FK
arcs naturally), flailing motions, spines (usually FK/BBone), when pole flipping annoys more than it
helps. - PARAM: chain length; pole target; influence (0–1 for IK/FK blend); iterations; weight; target
space. - PRO: planted contacts; intuitive posing. CON: poles flip; arcs unnatural; less "organic" feel
by default. - MIST: pole target placed inside the limb plane (flips); no IK/FK switch (can't do arcs); IK
on the whole spine. - FAIL: pole flip (leg snaps to other side). DIAG: move the target past the pole —
flip = pole target wrong or chain solving oddly. - FIX: reposition pole target; add influence falloff; use
pole-vector constraint orientation. - EDGES: → D52 FK (blend), → D53 constraints, → D55 controls.
Deep chain — IK → Leg IK → Foot IK → Foot Controller
Foot controller → pivot (heel/toe/ball) → orientation → rotation limits → pole vector → ankle behavior
→ heel roll → toe roll → stretch → deformation → controller placement → animator usability → testing →
failure cases → corrections
D52 — FK (FORWARD KINEMATICS) [REQ]
DEF: A chain where you rotate each joint from the parent down (shoulder → elbow → wrist). WHY: FK
produces natural arcs and organic motion; it's the default for spines, tails, necks, fingers — and the
"arc mode" for limbs. HOW: plain bone parenting; rotate each bone; add FK control bones (one per
joint) driven by Copy Rotation or directly posed. PRO: natural arcs; predictable; no pole problems.
CON: every joint hand-posed (hard for contacts). USE: spines, tails, necks, wings (fold arcs), fingers,
secondary motion; AVOID: planted feet, held objects. EDGES: → D51 (blend), → D55 controls.
D53 — CONSTRAINTS [REQ]
DEF: Rules that make one object/bone follow, limit, or compute from another. The glue of every rig.
WHY: Without constraints, controls can't drive bones, feet can't stay planted, cameras can't track,
and props can't attach.  Constraint catalog (rig-relevant):  -  Transform: Copy Location / Copy
Rotation / Copy Transforms (a bone mirrors another — the standard control→deform link); Transforms
(map rotation→location for mechanical). - Tracking: Track T o / Damped Track (head looks at target —
the look system, D63); Aim (pole vectors). - Limit: Limit Location / Rotation / Scale (rotation ranges
for joints, mechanical limits); Limit Distance. -  Child Of:  parent that can be  animated (switching
parents — hand grabs a prop and lets go; the professional "grab" system). - IK (D51), Stretch To
(stretch  chains),  Floor (feet  stay  on  ground  plane),  Action (constraint-driven  pose  libraries),
CHAPTER 6 — RIGGING, SKELETONS, SKINNING, DEFORMATION

Transform Cache (bake constraint results), Armature (bone→bone). Key rig patterns:  - Control
drives mechanism drives deform: CTRL (Copy Transforms) → MCH → (chain) → DEF . Mechanism layer lets
you insert math without touching the control. -  IK/FK switch:  a custom property (D54) drives the
influence of two constraints (IK constraint influence + FK control visibility) — the standard limb setup.
- World/character/local space switching: a control's space can change (Child Of with keyed influence)
— feet switch from world to foot space for foot roll.  PARAM: space (world/local/pose); influence;
target; axis mapping; order (for stacked constraints). MIST: constraints in the wrong space (poles);
too many stacked constraints (unpredictable); ignoring constraint order; constraints with no fallback
(break the rig).  FAIL: constraint loops (Blender warns — cycles); target in wrong file (link breaks).
DIAG: constraint evaluation order (constraints stack top-to-bottom); disable/enable constraints to
isolate. EDGES: → D48–D52, → D54 drivers, → D55 controls.
D54 — DRIVERS [ADV]
DEF: Expressions (math) that automatically drive values from other values — e.g., "eye blink drives
eyelid shape key," "global speed drives cloak flutter," "piston rotation drives translation."  WHY:
Drivers create  automatic systems  — the difference between animating 30 values by hand and 3.
They  power  IK/FK  switches,  stretch  systems,  facial  automations,  mechanical  rigs,  and  shader
animation. HOW: right-click a property → Add Driver; use the Driver Editor (F-curve driven by a driver
variable);  variables  reference  other  properties  (bone  transforms,  custom  properties,  object
transforms);  write  expressions  in  Python-like  syntax  (var * 2 ,  clamp(var, 0, 1) );  add  custom
properties on the rig (Properties panel → custom properties) as the interface to drivers. Patterns:
switch  drivers  (value = (ik_fk > 0.5) ? ... );  scale-linked  drivers  (stretch);  rotation-to-location
(mechanical); driven shape keys (facial automation — D60); shader drivers (wetness, emissive pulse).
MIST: drivers on every value (rig becomes a black box, hard to debug); unreadable expressions;
missing variable paths after renames (drivers break silently). FAIL: driver errors (purple) — usually
broken variable paths.  DIAG: check driver editor for error; re-set variable target.  FIX: keep driver
expressions documented; prefer simple scripts over complex expressions; bake drivers to keyframes
before final render if risky (Animation → Bake Action). EDGES: → D53, → D55, → D60 facial, → D31
shaders.
D55 — CONTROLLERS [REQ]
DEF: The  visible,  selectable  controls  the  animator  poses  —  bones  with  custom  shapes  (and/or
empties).  WHY: Controllers are the  ergonomics of the rig: recognizable shapes (hand/foot/head/
spine), consistent color coding, correct pivots, and a "does what it looks like" philosophy.  HOW:
create  custom shapes  (Object → Relations → Custom Shape; or the Custom Shape dropdown in
bone properties): circles for rotation, arrows for translation, diamonds for FK/IK, etc.; align the shape's
origin to the bone; scale shapes so they're selectable but not obnoxious; assign colors via bone
collections (D49). Usability rules: (1) one control per task (don't stack 10 controls at the hip); (2)
controls visible in Pose Mode, deform bones hidden; (3) pivot = intuitive point (foot control pivots at
the heel, not the toe, with toe/ball sub-controls); (4) auto-selectable (click-through works); (5) naming
= shape logic. PARAM: shape mesh (circle, arrow, custom); shape scale; collection/color; visibility;
pivot placement. MIST: controllers with invisible/no shapes; all controls white circles (can't tell hand
from spine); pivot at the bone tail instead of the natural rotation point; controls that overlap (can't
select the one you want). DIAG: animator usability test — can a new animator pose a contact pose in
30 seconds without asking questions?  FIX: iterate shapes/pivots with real animation tests; keep a
"rig test scene" with standard poses. EDGES: → D48, → D51/D52, → D53.
CHAPTER 6 — RIGGING, SKELETONS, SKINNING, DEFORMATION

D56 — WEIGHT PAINTING [REQ]
DEF: Assigning how much each vertex is influenced by each deform bone (vertex groups = weights,
0–1). WHY: Weights decide deformation quality — the exact behavior at joints (bends, folds, bulges).
Even perfect topology + perfect rig fails with bad weights. HOW (Blender): select mesh + armature
→ Ctrl-P →  With Automatic Weights  (good starting point); then refine in  Weight Paint mode :
paint weights per bone (add/subtract/mix brushes), use vertex group selection (select the bone via
the armature in Pose Mode with "Selected Pose Bones" in the vertex group panel), smooth, and
Normalize (total influence should sum to ~1 where bones overlap). Key skills: weight gradients at
joints (blend zones, not hard edges); asymmetry awareness (mirror weights); adjusting influence
falloff (the "fold" width); using  Envelope influence as an alternative (bone envelope weights —
faster, less precise).  Weight-map anatomy (for a leg):  thigh bone owns upper leg (weight 1),
blends to shin bone around the knee with a smooth gradient; a small weight of the hip bone stabilizes
the  thigh  top;  the  knee  cap  region  needs  careful  distribution  to  avoid  the  "watermelon  knee."
PARAM: brush strength/radius; auto-normalize; mirror; vertex group per bone.  MIST: hard weight
boundaries (elbow crimps); weights that never normalize (double influence); painting while the mesh
is  deformed  (paint  on  rest  pose!);  ignoring  face/hand  weights.  FAIL: mesh  "shatters"  at  joints;
vertices fly off (a vertex has weight to a bone with zero bone, or an orphan weight). DIAG: pose the
armature; select the deforming vertex; inspect its vertex group values (Item panel).  FIX: smooth/
paint weights; use corrective shapes (D59) for stubborn spots; check bone envelope influence (it
adds  to  vertex  groups  —  confusing!).  EDGES: →  D57  skinning,  →  D58  deformation,  →  D59
correctives.
D57 — SKINNING [REQ]
DEF: Binding the mesh to the skeleton: the Armature modifier + weights (D56). Skinning = the
configuration of  deformation:  modifier  order,  weight  mode,  envelopes,  and  multi-object  binding.
HOW: Armature modifier (deform with vertex groups; envelopes optional); bind via Ctrl-P (Automatic
Weights / Envelope / Empty groups); for character with multiple meshes (body, eyes, teeth, clothes)
bind each (or use object parenting for rigid parts: teeth to head bone as a child object — no weights
needed).  PARAM: modifier order (Armature before other deformers? Usually armature last-ish, but
relative order with cloth/subdiv matters); preserve volume (on for most organic); vertex groups
mode.  MIST: rigid parts (teeth, armor plates) weight-painted (they should be parented to bones
instead);  armature  modifier  before  subdiv  (subdiv  after  armature  =  heavier  but  smoother
deformation — usually put subdiv  after armature for deforming meshes... actually order: armature
then subdiv gives smooth deformation; subdiv then armature is cheaper. For production: Armature →
Subdivision or Subdivision → Armature depending on budget). FAIL: mesh separates from skeleton
(missing weights). DIAG: bind pose reset; check modifier. EDGES: → D56, → D58.
D58 — DEFORMATION [REQ]
DEF: How the mesh changes shape when bones move: bending, twisting, stretching, bulging, folding
— the  visible result of skinning.  WHY: Deformation is where "CGI skeleton under skin" becomes
visible. The goal:  believable muscle/soft-tissue behavior, not rubber hose (unless style demands
hose).  Deformation toolkit (in order of sophistication):  1.  Weights (D56): the base layer —
joint blends. 2.  Bone shaping:  tweak bone  head/tail positions and roll  to shift deformation; use
CHAPTER 6 — RIGGING, SKELETONS, SKINNING, DEFORMATION

Envelope to influence without vertex groups. 3. Corrective shape keys (D59):  pose-driven mesh
corrections  —  the  standard  for  muscle  bulges,  knee  caps,  armpit  folds,  elbow  wrinkles,  mouth
corners. 4. Corrective bones: extra bones that move when the joint bends (driven by rotation) and
pull weights — e.g., knee cap bone, scapula slide bone, chest lift bone. (Bone-based correctives are
cheaper than shape keys in some pipelines.) 5. Twist bones (D50):  distribute rotation. 6. Bendy
bones (D50): smooth spine/tail curvature. 7. Simulated deformation: cloth for belly/chest, jiggle
bones (D77) — for secondary motion. Common problem zones & fixes:  elbow (needs 3–4 loops +
inner wrinkle corrective); knee (cap corrective + hamstring stretch); shoulder (deltoid pinch + armpit
fold); armpit (pole + corrective); hip/crotch (fold line); neck (no "cable" look — smooth gradient);
wrist/ankle (transition rings); fingers (knuckle bulges — subtle); face (D24 facial topology + D60).
PARAM: preserve volume; bone envelopes; corrective strength; twist distribution.  MIST: skipping
correctives (rubber hose everywhere); correctives that fight each other (shape key order); deforming
rigid parts. DIAG: pose extremes (sit, stretch, twist, crouch) and watch the silhouette — deformation
errors are silhouette errors first. FIX: weights first, then correctives; one corrective per problem; test
in motion (static extreme pose can hide dynamic popping). EDGES: → D24 topology, → D56/D57, →
D59, → D60.
D59 — CORRECTIVE SHAPES [ADV]
DEF: Shape keys (blendshapes) or corrective bones that automatically fix deformation at specific
poses — driven by joint rotation via drivers (D54). WHY: The mesh "should" look right everywhere,
but joints always need assistance: a muscle bulge, a wrinkle, a fold. Correctives are the final 20%
that makes deformation beautiful. HOW (shape-key route): (1) create the base shape key (Basis);
(2) pose the rig at the problem pose; (3) edit the mesh in that pose to fix the deformation (add the
bulge/wrinkle); (4) the shape key now contains the correction; (5) set its value to 0 at rest; (6) drive it
with the joint's rotation via a driver (e.g., elbow bend > 60° → wrinkle shape = 0→1). How (bone
route): add a small bone at the problem zone; give it weight over the bulge region; drive its location/
rotation with the joint's rotation (driver or constraints); it "pushes" the skin.  PARAM: driver curve
(smooth  on/off  —  no  pops);  strength;  influence  region;  combinations  (two-bone  correctives  for
crossing  folds).  MIST: correctives  that  pop  (hard  driver  transitions);  too  many  (rig  weight,
maintenance); sculpting correctives without testing in motion; shape keys fighting the armature (set
up with the rig in the rest position and only touch the pose during creation). FAIL: "exploding" mesh
when corrective activates (shape key edits moved verts that shouldn't move). DIAG: isolate by shape
key;  reset.  FIX: keep  corrective  edits  localized;  blend  curves  smooth;  bake  down  if  drivers
misbehave. EDGES: → D58, → D54 drivers, → D60 facial (facial correctives are the same technique at
scale).
RIG SIGN-OFF TEST (run before animation)
[ ] Every control poses intuitively (new animator test)
[ ] IK/FK switch works on all limbs; no pole flips in full range
[ ] Feet stay planted; foot roll works; no sliding under load
[ ] Spine/neck/head have natural arcs (BBone/FK)
[ ] Stretch system (if any) scales with global "stretch" property
[ ] Face: eyes, brows, jaw, mouth, tongue, blink all work (D60)
[ ] Deformation: sit/stretch/twist/crouch extremes pass silhouette test
[ ] Correctives don't pop; twist distribution is clean
• 
• 
• 
• 
• 
• 
• 
• 
CHAPTER 6 — RIGGING, SKELETONS, SKINNING, DEFORMATION

[ ] Naming/collections documented; rig file separated from shots (D123)• 
CHAPTER 6 — RIGGING, SKELETONS, SKINNING, DEFORMATION
