# Depth Chapter 28 — Advanced Rigging Systems

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 182–185 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 28 — ADVANCED RIGGING
SYSTEMS (FULL NODE CARDS)
Expands D48–D59. The professional rig subsystems, each as a complete node card with parameters,
workflows, failure modes, and fixes. These are the rigs that make animators fast.
28.1 THE FOOT ROLL SYSTEM [REQ for any serious foot]
DEF: A foot control that keeps the foot planted while allowing heel/ball/toe rock, pivot, and stretch —
the difference between "feet that slide" and "feet that walk."  HOW (the classic rig):  - Bones:
Foot_IK (master), Heel, Ball, T oe (child chain under Foot_IK), plus T oeTip (optional) and a stretch bone.
-  Pivot system:  the Foot_IK control's pivot must be  animatable — the standard method: three
empties (pivot at heel, at ball, at toe) with the foot's rotation parented via a space switch (Child Of
constraint with keyed influence, or drivers): when walking, pivot = heel (contact), then ball (push-off);
when balancing, pivot = center. - Ankle behavior: the ankle bone connects Foot_IK to the leg; its
roll/orientation matches the foot's angle so the leg chain solves cleanly (pole vector stable — D51). -
Heel/ball/toe rotation:  dedicated sub-controls or sliders on the foot control (custom properties):
Heel_Roll (rotate around heel), T oe_Roll (around ball), Rocker (rotation that follows the ground when
at edge — the "rocker" trick: ball-bone roll + heel-bone roll both constrained so the foot doesn't
pierce the floor). - Stretch: optional foot stretch (cartoon) via Stretch T o with a property. - PARAM:
pivot empties; space-switch influence; roll limits (heel 30°, toe 45°); stretch amount. - MIST: no pivot
switch (foot pivots at the toe — sliding heel); heel/ball not child-correct (flips); pole vector near the
foot (knee flips on roll). -  FAIL: foot clips the floor mid-roll.  FIX: floor-lock the ball during push-off
(constraint to the ground plane with influence); test the full gait (D66). - EDGES: D51 (IK), D53 (Child
Of space switch), D66 (gait).
28.2 THE HAND RIG [REQ for acting characters]
DEF: Full hand control: palm orientation, 4 fingers + thumb with FK/IK per finger, spread, cupping,
and a "grab" helper. HOW: - Palm bone (control) → wrist; fingers as chains (3 bones each: MCP/PIP/
DIP — D49), thumb 3–4 bones (articulated saddle joint). - Per-finger FK/IK: FK for individual curl; IK
(chain length 3) for "finger points at X" (rare, but for pointing/guitar); a global curl custom property
curls all fingers proportionally (the "grab" slider). -  Spread: fingers can spread (abduction) — a
spread control rotates each finger's MCP laterally. -  Cupping: a pose library (D64) with cup/grip/
point/flat poses is more practical than a driver system — the pose library is the hand control surface.
- Knuckle bulge: corrective shape key at MCP flexion (D59) — subtle. - PARAM: curl ranges (MCP
90°, PIP 100°, DIP 60° — Ch 16.5); spread limits; pose library entries. - MIST: no global curl (40 keys
per finger grab); thumb with no saddle (flat thumb); fingers sharing a bone (no individual curl). -
EDGES: D49, D64 pose library, D19 hand topology (3–4 segments per finger).
28.3 THE SPINE & TORSO SYSTEM [REQ]
DEF: A flexible spine that keeps volume, allows arcs, and carries the "core" of acting (D76). HOW
(choose by style): - FK spine (classic): 3–5 spine bones (pelvis → lumbar → thoracic → chest) with
FK controls; animator poses each; add a hip control (pelvis translation — the root of weight) and a
chest  control (the  leading  mass).  -  Ribbon  spine  (organic/realistic): a  spine  mesh  ribbon
DEPTH CHAPTER 28 — ADVANCED RIGGING SYSTEMS (FULL NODE CARDS)

deformed by a curve → bones follow the ribbon (constraints) — smooth, controllable curvature; used
in high-end character rigs. - BBone spine (stylized/simple): 1–2 bendy bones with segments (D50)
— cheapest, very smooth; great for cartoon and creatures. - Spine add-ons: auto-settle (drivers
blend spine back to neutral for micro-lag), stretch (global, Ch 19 recipe 7), counter-rotation (chest
counter-rotates hips in locomotion — automate subtly or leave to the animator). - Hip behavior: the
pelvis leads weight shifts (D76); the hip control should be the first thing an animator keys in a weight-
bearing pose. -  MIST: spine as one stiff bone (no flexion); chest/hip controls overlapping (can't
select); auto-settle fighting the animator (keep it optional). - EDGES: D50 (BBone), D49, D66 (spine
in gait), D76.
28.4 THE SHOULDER & CLAVICLE [REQ for realism]
DEF: The shoulder lift: when the arm rises past ~90°, the clavicle/scapula must move — the "auto-
clavicle" that makes arm raises read as real. HOW: - Bones: Clavicle (control + deform), UpperArm,
plus a scapula bone (deform) on the back for organic characters. - Auto-clavicle: driver: UpperArm
rotation (forward/up) → Clavicle rotation × 0.2–0.4 (arm up = clavicle up) — smooth, proportional;
also a slight  forward shift for forward raises. -  Scapula slide: the scapula bone follows the arm's
rotation with a fraction (0.15–0.25) and translates along the ribcage (constrained to the clavicle). The
back  should  move when  the  arm  moves  —  this  is  the  #1  realism  upgrade  for  topless/organic
characters. - PARAM: clavicle driver factor; scapula follow factor; limits (clavicle up 30°, fwd 15°). -
MIST: frozen shoulders (arm raises, clavicle static — "robot arm"); scapula unweighted (back doesn't
move); over-drive (clavicle pop at 90°). - EDGES: D54 (drivers), D49, D16.7 (quadruped scapula!).
28.5 FACIAL AUTOMATION RECIPES [ADV — see also Ch
19]
Auto-blink: a blink property + noise driver for idle (background characters); manual for acting
(D63).
Eyebrow follow: brows follow the head bone's pitch slightly (natural lag) with a driver fraction —
then the animator overrides for expression.
Jaw-lip lag: jaw opens → lips follow at 0.3× with 1–2 frame delay (drivers with frame  offset —
advanced: use a small action or a driver on the lip keys referencing the jaw key with a frame
offset via fcurve  lookup; simpler: animate lips with anticipation manually, D62).
Breathing: chest/abdomen scale loop (Ch 19 recipe 6) with amplitude per energy state
(character property "Energy" scales it).
Micro-saccade: eye control with a tiny noise on the look target (amplitude 0.5–1°) — subtle life
(D63).
The rule: automation for support motion; manual for performance. Never automate the emotion.
28.6 MECHANICAL RIGS (robots, machines, armor plates)
[SIT]
DEF: Rigs where bones  slide and rotate with constraints , not weights — pistons, hinges, gears,
tracks, and plate stacks.  HOW: -  Piston: a bone constrained to translate along an axis (Limit
Location + Transforms), driven by another bone's rotation (driver — Ch 19 recipe 8); the piston
cylinder follows (constraint), the rod stretches (Stretch T o). - Gears: bone rotation driven by a ratio +
direction (recipe 9); chain them. - Hinges/doors/hatches: Child Of / Limit Rotation on a hinge bone;
• 
• 
• 
• 
• 
• 
DEPTH CHAPTER 28 — ADVANCED RIGGING SYSTEMS (FULL NODE CARDS)

armatures per mechanism, or one armature with mechanical bones (D50). - Armor plates (D41):
plates parented to bones (no weights) with  staggered joints (pauldron lames overlap naturally via
each plate bone's limit); under-suit weighted normally. - Tracks: a curve + "follow path" empty with a
rotation driver → wheel rotation from distance traveled (the classic tank-track trick). - PARAM: axis
constraints;  driver  ratios;  limits  (mechanical  parts  need  hard limits  —  no  overshoot);  stretch/
compress ranges. - MIST: weighting mechanical parts (they should be rigid); no limits (pistons over-
extend); driving with free rotation (jitter) — use damped drivers. - EDGES: D50 (mechanical bones),
D53 (limits), D54 (drivers), D41.
28.7 WING RIGS [SIT — see also D45/D72]
DEF: Wing control: flap (shoulder), fold (elbow + wrist + finger-fan), feather spread, and gliding lock.
HOW: hierarchy: Shoulder → UpperArm → Elbow → Forearm → Wrist → FingerFan (4–6 finger bones in
a fan — the feather rows attach to them, D45) + FeatherSpread control (drives row rotation);  IK
wingtip (optional): the wingtip follows a target for expressive "reach" (dive, catch), with FK fallback
for flap arcs; fold logic: the wing folds like a fan — the fan bones each have limits so the fold stacks
cleanly; add a glide lock (allows the wing to hold angle without drift — a small spring/damp or just a
locked pose). PARAM: flap arc; fold limits per joint; feather spread range; IK/FK wingtip. MIST: one
solid wing bone (no fold); feathers weighted to the body (wing moves, feathers don't); no fold limits
(wing inverts). EDGES: D45 (feather rows), D72 (flight), D50.
28.8 TAIL & TENTACLE RIGS [SIT]
DEF: Flexible  appendages:  FK  chain  +  curve  controls,  BBone  smoothing,  stretch,  and  "follow"
automation. HOW: FK chain (6–12 bones — D16.11) with a curve control: a control curve that the
chain follows (constraints: each bone aims to the next point — "spline IK" style); or BBone chains (1–3
bones  with  segments,  D50)  —  the  cheapest  smooth  tail;  stretch for  whip;  follow-through:  a
"trailing" control that the animator  deliberately lags (D77) — or a driver-based damped follow for
background  tails;  tip  "aim"  (Track  T o)  for  expressive  tips  (prehensile).  PARAM: segment  count;
stiffness (BBone curve settings); stretch; tip aim. MIST: too few segments (angular tail); tip with no
aim (can't point); tails weighted to the spine (tail moves when body moves — actually desired
partially; weight to tail chain only). EDGES: D50 (BBone), D16.11, D77.
28.9 MULTI-LEG GAIT RIGS [ADV — for D71 creatures]
DEF: Automatic leg cycling for 6+ legs: a master "gait" control moves leg targets along a cycle so
the animator drives one dial instead of N legs. HOW (the tripod driver):  a control object moves
along a circle/path; each leg's target position = base + phase offset (driver:  sin(frame * speed +
phase_i) * amplitude  on the leg IK target); phases set by tripod logic (legs 1,3,5 vs 2,4,6 alternate —
D71); stride length + height per leg; the animator overrides individual legs when needed (per-leg
influence). When NOT: hero creature shots need hand-keyed character (the driver rig is a preview/
background tool); use it to generate reference and block, then hand-polish. EDGES: D71, D51, D54.
28.10 JIGGLE & SQUASH RIGS [SIT — cartoon & organic]
DEF: Secondary-motion rigs: fat/belly jiggle, soft tissue, cartoon squash —  rigged follow-through
without simulation (D77). HOW: (a) Jiggle bones: a bone with a damped driver chain (its rotation =
parent rotation smoothed via driver with lag — advanced expression or the built-in "spring" behavior
via constraints + damping) — moves after the main bone and oscillates; weight soft parts to it. (b)
DEPTH CHAPTER 28 — ADVANCED RIGGING SYSTEMS (FULL NODE CARDS)

Shape-key jiggle: a shape key driven by velocity ( var = bone.velocity  via driver — needs a velocity
variable; simpler: driven by the bone's position delta via frame  comparison — advanced; many rigs
use a  soft-body/rigid "jiggle" add-on  — commercial add-ons do this robustly). (c)  Squash &
stretch global (D65): a global scale with per-bone weights — the cartoon standard (Ch 19 recipe 7).
MIST: jiggle on everything (chaos — D77 rule: pick 2–3 elements); physics-like jiggle in a realistic
shot (uncanny). EDGES: D77, D54, D59.
28.11 SPACE SWITCHING (the hidden superpower) [ADV]
DEF: A control that changes its reference space (world/character/other object) mid-animation — the
difference between "good rig" and "professional rig." Examples: feet switch between world (planted)
and foot (rolls); hands switch between world and character (held props); props switch parents mid-
shot (a character grabs a sword and the sword switches from world to hand — the grab system, D53
Child Of with keyed influence). HOW: Child Of constraint with influence keyframes (or the "Space
Switching" add-on); each space = a target empty; key the influence 1→0→1 at the switch frame; the
switch frame must be exact  (a hand-off where both parent sets coincide).  MIST: switching at the
wrong  frame  (object  jumps);  no  matching  transform  at  the  switch  point  (pop);  over-switching
(confusing rig). EDGES: D53 (Child Of), D51 (IK/FK space), D42 (props).
RIG DEPTH CHECKLIST (the professional bar)
[ ] Foot roll with pivot switching (28.1) — test a full gait
[ ] Hand with global curl + pose library (28.2)
[ ] Spine with hip/chest controls; auto-settle optional (28.3)
[ ] Auto-clavicle + scapula (28.4) — test arms overhead
[ ] Facial automation supports (not replaces) performance (28.5)
[ ] Mechanical limits where parts are rigid (28.6)
[ ] Wings fold like fans; tails follow; multi-legs have gait preview (28.7–28.9)
[ ] Jiggle/squash only where style demands (28.10)
[ ] Space switching for feet/hands/props (28.11)
[ ] Animator sign-off test passed (Ch 6 checklist)
• 
• 
• 
• 
• 
• 
• 
• 
• 
• 
DEPTH CHAPTER 28 — ADVANCED RIGGING SYSTEMS (FULL NODE CARDS)
