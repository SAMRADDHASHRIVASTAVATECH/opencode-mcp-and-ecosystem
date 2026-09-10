# Chapter 8 — Animation: Principles, Locomotion, Creatures, Acting, Polish (D64–D78)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 83–89 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 8 — ANIMATION: PRINCIPLES,
LOCOMOTION, CREATURES, ACTING, POLISH
Domains D64–D78. Animation is the soul of the medium: turning keyframes into performance. This
chapter covers the complete animation system — from the 12 principles to multi-legged gaits and
cinematic acting.
D64 — CHARACTER ANIMATION [REQ]
DEF: The full process of animating a character: planning → blocking → splining → polish, in Blender's
animation tools. WHY: A professional pipeline, not random keyframing, is what makes animation fast,
editable, and high-quality. The pipeline is: pose the story, then add the motion. HOW (the pipeline):
1.  Plan: shot brief, motion reference (D12), poses breakdown (which poses carry the story). 2.
Blocking (stepped): pose key poses as stepped keys (no interpolation); every 8–24 frames a story
pose. Story first. Review; iterate cheaply. 3. Breakdowns: add the transition poses (the mid-points
that define arcs and weight) — still stepped. 4.  Splining: convert to spline interpolation (T key);
refine timing curves in the Graph Editor; fix spacing (D65), arcs, overlap, follow-through. 5. Polish:
secondary  motion  (D77),  micro-motion,  facial  pass  (D61),  cleanup  of  jitter  (D78).  Blender
animation tools (master these):  - Dope Sheet (Action Editor):  all keyframes in one list; strip/
action management; the NLA (Non-Linear Animation) for action strips (walk cycle as a reusable strip
— D84/loops). - Graph Editor: F-curves per property; interpolation modes (constant/linear/bezier);
Auto Clamped  (default, avoids overshoot); editing handles, adding/removing keys, scale/offset in
time and value; curve types (Ease In/Out, Exponential, Elastic…) — the feel of motion lives here. -
Pose Library:  save poses (and entire expressions) as assets (D122) — the pose library is the
animator's vocabulary. - Time & playback: timeline scrubbing; auto-keying; playback range; onion-
skin-like ghosting via "Mocap" display? (no — use the NLA/sync); keying sets. PARAM: frame range;
fps (D10); interpolation defaults; auto-key settings. MIST: jumping straight to splines (no blocking —
rework loops); keying every frame (no spacing, no control); ignoring the Graph Editor (bad curves =
bad motion); no pose library. FAIL: jitter (popping keys); foot sliding (bad contacts). DIAG: watch the
motion  silhouette;  check  F-curve  for  spikes.  FIX: block  properly;  use  stepped  keyframes;  clean
curves; animate in passes (body, then face).  EDGES: → D65 principles, → D66 locomotion, → D75
acting, → D77 secondary, → D78 polish.
Deep chain — Animation → Blocking → Breakdown → Spline
Key poses → stepped keys → breakdowns → spline → timing curves → spacing → arcs → overlap → polish
D65 — ANIMATION PRINCIPLES [REQ]
DEF: The 12 classic principles (Disney; Thomas & Johnston) plus modern extensions — the grammar
of believable motion. WHY: Every "alive" animation — realistic or stylized — obeys these. They are
physics of perception: how motion communicates weight, force, and life. The 12 (+extensions): 1.
Squash  &  Stretch: volume-preserving  deformation  on  impact/acceleration;  sells  weight  and
elasticity. (Style lever: cartoon = big, realism = subtle.) 2.  Anticipation: the wind-up before the
action (crouch before jump, pull back before throw) — tells the eye  what's coming . 3.  Staging:
presenting the idea clearly — composition, focus, timing so the audience sees the right thing at the
CHAPTER 8 — ANIMATION: PRINCIPLES, LOCOMOTION, CREATURES, ACTING, POLISH

right time (D104). 4.  Straight ahead vs pose to pose:  either continuous drawing or key-pose
workflow; Blender = pose-to-pose with blocking; straight-ahead for organic chaos (fluids, hair). 5.
Follow-through & overlapping action: parts keep moving after the main body stops; parts move
at different times (cloak, hair, tail — D77). 6. Slow in / slow out (easing):  motion accelerates and
decelerates — nothing starts or stops instantly; the basis of F-curve editing. 7. Arcs: natural motion
follows curved paths (a wrist thrown across the body moves in an arc, not a line) — check in the
Graph Editor/3D view. 8. Secondary action: supporting motion that enriches the primary (a sigh, a
glance, cloth) — supports, never distracts. 9.  Timing: number of frames per action = weight and
mood (heavy = slow, light = fast; 2–4 frames = snappy, 12+ = ponderous). 10. Exaggeration: push
poses beyond reality to communicate (style-dependent; subtle for realism, huge for cartoon). 11.
Solid drawing/posing: clear silhouettes, readable weight, balanced poses (D104/D76). 12. Appeal:
the character is interesting/attractive/compelling — design + motion charm.  Modern extensions:
weight & balance (D76); intent (every motion serves a goal — D75); contact/friction (feet don't slide);
inertia & momentum; anticipation of  emotional action (a pause before a decision).  PARAM (per
motion): anticipation frames; contact frames; settle frames; overshoot amount; easing type. MIST:
all  motions  with  the  same  easing;  no  anticipation  (motion  "teleports");  arcs  as  straight  lines;
exaggeration without a base (looks random).  DIAG: watch with the sound off, then with only the
silhouette;  check  arcs  per  F-curve.  FIX: return  to  the  principles  as  a  checklist  —  90%  of  "off"
animation is a violated principle. EDGES: → every animation domain.
D66 — LOCOMOTION [REQ]
DEF: How characters move from place to place: walks, runs, sprints, crawls — the most-performed
animation task.  WHY: Locomotion is ubiquitous and unforgiving: audiences instantly  feel a wrong
gait. Mastery = understanding weight transfer, contact, and rhythm. Walk cycle anatomy (biped):
8 key poses across 2 steps: Contact (heel strikes, opposite arm forward) → Down (weight accepts,
knee bends) → Passing (support leg straight, body at highest) → Up/Toe-off (push-off, weight lifts) →
Contact (other foot) → repeat. Key parameters: - Timing: walk ≈ 0.5–0.7 s per step (24 fps: 12–16
frames/step); run ≈ 8–10; sprint ≈ 6–8; add 1–2 frames for heaviness, subtract for lightness. -
Vertical motion: body rises at passing, dips at contact/down (bounce amplitude ≈ 2–5 cm walk,
more for run). - Weight transfer: weight moves between feet; the passing foot has no weight; the
hips shift laterally toward the support leg. -  Counter-rotation: hips and shoulders counter-rotate;
arms swing opposite the legs; head stabilizes (in real walks the head stays level — a great test). -
Stride & foot roll:  heel strike → foot flat → toe push-off (foot roll, D51 foot controller). Run cycle:
flight phase (both feet off); contact shorter; bounce bigger; arms bent; lean forward. Speed map (24
fps): slow stroll 14–18 f/step; normal 12–14; brisk 10–12; jog 8–10; run 6–8; sprint 4–6. Quadruped
basics (see D70): 4-beat walk (LF, RH, RF, LH), 2-beat trot (diagonals), 3-beat canter, 4-beat gallop.
WORKFLOW: reference (D12) → block the contact poses → breakdowns (passing, down, up) → loop-
able cycle (NLA strip, D84) → blend into shot with variation (never cycle-identical steps in a real shot
— vary stride/timing). MIST: feet sliding (contact broken); hips level (no weight shift); head bobbing
(unrealistic); arms stiff; cycle loops with no variation. DIAG: play the cycle in a loop at 12.5% speed;
check contacts against the floor (add a floor grid). FIX: fix contacts first (all other errors cascade);
then timing, then bounce, then arms. EDGES: → D67 human, → D68–D73 creature locomotion, → D51
foot IK.
Deep chain — Walk cycle → Phase → Detail
Contact → down → passing → up → contact(alt) → foot roll → hip shift → counter-rotation → head level →
arms → timing → spacing → overlap → secondary → polish
CHAPTER 8 — ANIMATION: PRINCIPLES, LOCOMOTION, CREATURES, ACTING, POLISH

D67 — HUMAN MOVEMENT [SIT]
DEF: The biomechanics of human motion beyond gait: transitions, weight shifts, reaching, sitting,
standing, lifting, turning.  WHY: Characters do more than walk; the  transitions between states are
where motion reads as real or robotic. Key systems: balance (center of mass over support base — a
falling body reacts); momentum (turn = wind-up + transfer); weight of parts (head ~5 kg, arm ~4 —
heavy feels heavy); transitions (walk → stop = deceleration + settle; sit = anticipation crouch +
controlled descent); reaching (shoulder leads, elbow follows, wrist last — an arc); lifting (knees bend,
spine stays aligned, weight registers in the face/breath). MIST: frozen transitions (pose → pose with
no physics); weightless gestures; symmetric everything. EDGES: → D66, → D76 physical acting, →
D75 acting.
D68 — ANIMAL MOVEMENT [SIT]
DEF: Motion logic for real animals: quadrupeds, birds, reptiles, fish — the foundation for creatures
(D69). WHY: Real animals show the full range of nature's solutions (spines that undulate, gaits with
suspension, tails as counterweights). Creatures borrow from these proven systems. Key patterns:
quadruped spine undulation (the back flexes with the stride); digitigrade vs plantigrade stance; tail
counter-swing; head stabilization (galloping horses keep heads fairly level); birds' wing cycles (D72);
snakes' lateral undulation (wave travels head→tail); fish's S-curve propulsion (D73). EDGES: → D70
quadruped, → D72 flying, → D73 swimming, → D69 creatures.
D69 — CREATURE MOVEMENT [SIT]
DEF: Inventing believable motion for original anatomies: from the creature spec (D05) to actual gaits
and behaviors. WHY: An original creature has no reference video — the animator derives its motion
from anatomy logic (mass, joints, spine) + analogous real animals + physics. This is the heart of
creature animation. HOW (the derivation method): 1. Mass & center of mass: heavy creature =
slow acceleration, high inertia, grounded gait; light = springy, arcing. Place the COM from the spec;
every stance must balance it. 2. Spine logic: long flexible spine = undulation (adds propulsion, looks
alive); rigid spine = stiff torso (bears weight, less organic). 3. Joint scheme: joint count → degrees of
freedom → possible gaits. Digitigrade = spring-loaded (bounding); plantigrade = weight-bearing;
extra joints = unusual, define their logic. 4. Locomotion class → gait family: see D70 (quadruped),
D71 (multi-leg), D72 (flight), D73 (swim), D66 (biped). 5. Analogous-animal mashup: "six-legged
crystal  creature"  →  combine:  insect  tripod  gait  (D71)  +  mammalian  spine  +  bird-like  head
stabilization + heavy-mass inertia (stone body) + cloak physics (D39). The mashup is the animator's
creative superpower. 6. Behavior: idle, threat, curiosity, pain — motion reveals temperament (D03):
a predator stalks (low, slow, level head), a prey animal skitters. MIST: animating a creature like a
human  in  a  costume;  ignoring  the  spec's  mass;  gaits  that  contradict  anatomy  (a  10-ton  beast
hopping). DIAG: the "does it weigh what it should" test; the "would a zoologist believe it" test. FIX:
ground in real analogs; test walk cycles early (blockout-rig tests, D16). EDGES: → D05 spec, → D66/
D70–D73, → D48 rig (creature rigs must support the gait).
CHAPTER 8 — ANIMATION: PRINCIPLES, LOCOMOTION, CREATURES, ACTING, POLISH

D70 — QUADRUPED ANIMATION [SIT]
DEF: Four-legged locomotion: walks, trots, canters, gallops, plus head/tail/spine coordination. WHY:
Quadrupeds (real and invented) are common creatures; their gaits are rhythmic and learnable — and
they teach spine and leg coordination for all creatures. The gaits (footfall order matters!): - Walk
(4-beat): LF → RH → RF → LH, evenly spaced; 3 feet on ground at once (stable); ~1–1.5 s per cycle. -
Trot (2-beat): diagonal pairs (LF+RH, RF+LH) — bouncy, efficient, ~0.5–0.8 s. - Canter (3-beat):
LF → (RH+LF diagonal) → RF; rocking, ~0.6 s; the "show" gait. - Gallop (4-beat): hind pair then front
pair  (suspension  phase,  both  front  off  ground);  the  only gait  with  full  suspension;  ~0.4–0.6  s.
Coordination: spine flexes (extend at suspension, compress at landing); head/neck counter-moves;
tail counter-sways; shoulders/hips rotate in opposite phase; the head dips at front-landing, rises at
push-off. Rig needs: 4 leg IK (D51), spine chain (BBone), neck/head, tail chain; foot roll on all 4; a
"gait" rig (auto foot cycling via drivers — advanced). WORKFLOW: reference real gaits (D12/D68) →
block the footfalls (foot prints on the floor!) → spine/head → tail → polish. Footprint planning (draw
the footfall pattern on the floor) is the #1 professional technique. MIST: wrong footfall order (looks
alien instantly); spine as a rigid bar; legs animating like human arms; no weight shift to diagonal
support.  DIAG: watch the footfall pattern; check that each foot plants and lifts cleanly (no drag).
EDGES: → D68, → D71, → D51.
D71 — MULTI-LEGGED CREATURES [SIT]
DEF: Locomotion for 6+ legs: insects, spiders, crabs, centipedes, and invented multi-leg designs.
WHY: Multi-leg creatures are a frequent fantasy request (including the user's six-legged example);
their gaits come from  stability mathematics , not instinct — and once learned, any leg count is
animatable.  The logic:  -  Tripod gait (6 legs — insects, the standard):  legs divide into two
alternating tripods — front+middle+rear of opposite sides move together (LF, RM, LR) then the other
three (RF, LM, LR...). Wait — correct: Tripod 1 = L-front, R-middle, L-rear; Tripod 2 = R-front, L-middle,
R-rear. Always 3 feet planted → stable statics; body stays level; legs lift in a metachronal wave for
speed. -  Metachronal wave (centipedes/millipedes):  legs lift in sequence from rear to front (a
wave  traveling  forward);  many  legs  =  continuous  wave;  speed  =  wave  frequency.  -  8+  legs
(spiders/crabs): alternating groups (tetrapod for 8: 4 legs per phase); crabs move laterally (side-
stepping with the leading side pulling). - Stability rule: at any moment, the center of mass must be
inside the polygon of planted feet — this  defines the gait for any leg count. N legs → minimum
planted = ceil(N/2) + 1-ish for alternating patterns (tripod gives 3 for 6 legs).  Body mechanics:
body height stays level; slight pitch with the wave; each leg: lift (stumble-free clearance) → swing
(arc forward) → plant → stance (push body) → lift. Stance phase pushes the body, swing phase moves
the leg. Rig needs: each leg a full IK chain (D51) with a pole; "gait driver" systems (advanced: an
empty moving along a path drives leg target positions automatically — big time-saver for many legs).
MIST: animating legs in pairs (insects don't); no tripod logic (legs collide mid-air); body bobbing like a
mammal (multi-leg = stable platform).  DIAG: check 3-planted-feet rule per frame; watch for leg
crossing. EDGES: → D69, → D05, → D51.
Deep chain — Multi-leg gait → Tripod → Phase
Tripod A → lift/swing/plant → stance push → tripod B → overlap → body level → speed → metachronal wave
CHAPTER 8 — ANIMATION: PRINCIPLES, LOCOMOTION, CREATURES, ACTING, POLISH

D72 — FLYING CREATURES [SIT]
DEF: Flight animation: wings, body pitch, gliding, takeoff/landing, and the illusion of lift. WHY: Flight
is 90% illusion: audiences read weight and air from wing speed, body angle, and secondary effects —
not from physics simulation. The animation must sell  aerodynamic logic.  Wing cycle:  the  flap =
downstroke (power, wing tips move forward-down, body rises slightly) + upstroke (recovery, wing tips
trail, body settles); wing tip path = a figure-8 or ellipse  (not a flat arc). Flap frequency scales with
mass: hummingbird 50 Hz (blur), sparrow 10–15, crow 3–5, big pterosaur/dragon ~1–2, and huge
creatures glide (rarely flap).  Flight states: -  Flapping (cruise): rhythmic, efficient; body slightly
nose-up; wings flex (elbow/wrist joints) on downstroke, fold on upstroke. - Gliding: wings extended,
slight dihedral; body pitches to steer; the "soaring" state. - Soaring (thermal): gentle spiral, wings
locked, minimal motion. - Takeoff: deep low flaps, strong push (or drop-and-glide from height); legs
tuck. - Landing: flare (wings flare, body rotates up, stall moment), wings sweep forward, legs reach;
feet touch, wings fold — the most difficult to sell.  Body integration: tail acts as rudder/elevator
(yaw/pitch);  head  stabilizes;  wing  fold at  rest  (the  wing  must  have  fold  topology/rig  —  D45);
secondary  feathers  flutter  at  wingtip.  Rig needs:  wing  bones  with  elbow  +  wrist  +  finger-fan
hierarchy (D45 feather rows), IK for wing tips, wing fold controls, tail bones, and "feather spread"
controls.  Wind & speed cues:  speed lines (VFX, D100), cloth/hair streaming (D77/D47), wingtip
vortices  in  heavy  stylization.  MIST: flat  "paddling"  wing  arcs  (no  figure-8,  no  flex);  wrong  flap
frequency for the mass; no takeoff/landing logic; wings that don't fold at rest. DIAG: silhouette test —
does the wing tip trace a figure-8? Does the body feel suspended on air, not pinned to a rig? EDGES:
→ D45 feathers, → D69, → D100 VFX trails.
D73 — SWIMMING CREATURES [SIT]
DEF: Motion through water: undulation, propulsion, buoyancy, drag. WHY: Water's density changes
everything: motion is slower, weight is neutralized (buoyancy), and propulsion comes from pushing
water (undulation, not limb-stroke — mostly).  Propulsion modes:  anguilliform (eel: whole-body
wave); carangiform (fish: rear-third wave); thunniform (tuna: tail only, stiff body); oscillatory (whales/
dolphins: vertical tail fluke beats — mammals use vertical, fish use horizontal!); jet (cephalopods);
limb-driven (otters, penguins). The rules: the wave travels head to tail (amplitude grows toward the
tail); the head stays relatively stable (steering happens at the tail/pectoral fins); body pitch via fins/
flippers; buoyancy = neutral (a swimming creature doesn't sink/rise unless diving — manage with
subtle depth changes); drag = everything decelerates smoothly (no instant stops).  Underwater
"acting": slow,  graceful,  weightless;  hair/cloth  float  (D77  with  reduced  gravity  feel);  bubbles/
particles as speed cues (D100). MIST: fish swimming like a snake wriggling in air (head thrashing);
fins animating like wings; no drag (instant acceleration). EDGES: → D69, → D94 water (interaction), →
D77.
D74 — FIGHTING [SIT]
DEF: Combat choreography: strikes, blocks, dodges, impacts, and the story of the fight. WHY: Fights
are pure visual storytelling — every hit must  read (anticipation → strike → impact → reaction).
Readability beats realism; weight beats speed.  The strike formula:  wind-up (anticipation, shift
weight back) → lunge/strike (fast, 3–5 frames, follow the arc) → impact (contact pose, the "hit stop" —
2–4 frames of near-freeze sells force) →  reaction (the victim's body responds; the striker recovers/
regains balance) →  follow-through (weapon/limb continues, cloth/hair lags).  Key techniques:  hit-
CHAPTER 8 — ANIMATION: PRINCIPLES, LOCOMOTION, CREATURES, ACTING, POLISH

stop (freeze frames at impact — the #1 trick); impact reaction sells the hit more than the strike itself;
telegraphing (audience must see the hit coming); spacing (fighters maintain range, lunge in, retreat
out); counter-weights (a punch transfers weight into the target — the striker steps through); stamina
(fights slow down as fighters tire). Weapon fights: the weapon is an extension of the arm (follows
the wrist arcs); weight of the weapon (heavy = two-hand swings, arcs, momentum carries); sheathe/
draw transitions. MIST: both fighters moving at the same speed (no rhythm); hits that don't connect
visually (reaction missing); no anticipation (teleporting strikes); fights as random fast motion (no
story beats). DIAG: storyboard the fight (D09); does every beat read at 1× speed? Slow it down —
every hit must have setup → payoff. EDGES: → D76 physical acting, → D65 principles, → D100 VFX
impacts.
D75 — ACTING [SIT]
DEF: The  performance  layer:  intent,  emotion,  subtext,  and  character  voice  expressed  through
motion. WHY: Motion without intent is exercise; acting is meaning. The audience should read what
the character  wants even with the sound off.  How to think:  every shot answers:  What does the
character want? What is their obstacle? What is their emotional state at each beat?  Then express
through: posture (D03/D04), gesture vocabulary, timing (thought → decision → action), eyes (D63),
and the pause (the pause before an action is where acting lives). Technique: subtext (say one thing,
body says another); status (who dominates the scene — height, expansion, pace); thought-before-
action (a beat of thinking precedes every decision); energy (high/medium/low per character and per
beat); the "inner monologue" (the face reflects internal speech during dialogue).  MIST: characters
that always face the camera; constant motion (no stillness = no emphasis); expressions that don't
match the intent (smiling while lying — subtext missing). EDGES: → D03 concept, → D61 facial, →
D63 eyes, → D76.
D76 — PHYSICAL ACTING [SIT]
DEF: Selling  physics through  performance:  weight,  balance,  momentum,  force,  effort.  WHY:
Audiences instantly know whether a character weighs 5 kg or 500 kg. Physical acting is the actor's
body reading as  mass in gravity .  The rules:  center of mass over the support base (lean = fall);
momentum  carries  (a  heavy  object  keeps  moving);  effort  shows  (straining  =  slower,  breath,
trembling); balance recovery (recovering balance is a performance, not an instant); weight of held
objects  (a  crate  changes  posture);  inertia  on  start/stop  (acceleration  and  deceleration,  D65).
Technique: the "heavy walk" (slow, deliberate, low COM, wide stance); the "light walk" (springy, high
COM, quick); pushing/pulling (feet plant, body leans into the force); lifting (knees, core, face registers
strain); impacts (D74). MIST: same motion vocabulary for all weights; no effort in the face/breath;
characters that stop on a dime. EDGES: → D66/D67, → D74, → D65.
D77 — SECONDARY ANIMATION [SIT]
DEF: The  reactive motion that follows the primary action: cloth, hair, fat jiggle, accessories, and
"settle" — everything that keeps moving after the body stops.  WHY: Secondary motion is what
separates "animated" from "alive." A head-turn with trailing hair and a settling cloak reads as real;
without, it's a puppet.  The hierarchy of needs:  follow-through (parts continue past the stop) →
overlap (parts move at different times — the classic "wave" through a chain) → drag (loose parts lag
behind the leading edge) → settle (everything decelerates to rest with small oscillations) → jiggle (soft
CHAPTER 8 — ANIMATION: PRINCIPLES, LOCOMOTION, CREATURES, ACTING, POLISH

tissue/weighted  parts  oscillate  —  subtle!).  Blender  methods: hand-keyed  follow-through  (the
professional  standard  for  character secondary  motion  —  cloth/hair  simulated handles  the  rest);
simulated cloth (D39) for garments; hair dynamics (D47) for hair/fur; jiggle via drivers/soft-body-lite
or "jiggle bones" (D50/BBone with damped drivers — advanced); for creatures: tails are  always a
secondary-motion playground. MIST: no settle (motion ends abruptly); all parts stopping together (no
overlap); jiggle everywhere (chaos — pick the 2–3 secondary elements that matter); simulating what
should be hand-keyed and vice versa.  DIAG: pause at motion end — if everything froze at once,
secondary is missing. EDGES: → D39/D47 sims, → D65 principles, → D78 polish.
D78 — ANIMATION POLISH [OPT]
DEF: The final pass: fixing curves, spacing, arcs, footwork, and micro-detail until motion is  clean. 
WHY: Polish is where "good enough" becomes "professional" — and where most student work dies (it
stops at splining). Polish checklist: (1) curves clean (no spikes — Graph Editor); (2) spacing reads
(slow in/out on every motion); (3) arcs correct (check in 3D); (4) feet/hands planted (no slide — use
the "footprint test"); (5) overlap/follow-through present; (6) weight feels right (body reacts to its own
mass); (7) facial pass complete (D61); (8) no pops or glitches (play at all speeds); (9) silhouettes
readable at any frame (pause test); (10) secondary motion present but not distracting; (11) timing
serves the story beat (frame-accurate to the edit). PROD: polish with the final rig  only; polish with
audio and edit timing (D120); render test frames at 12.5% and 100% speed; get a second set of eyes
(D127 QC). EDGES: → D64, → D65, → D77, → D127.
ANIMATION SHOT SIGN-OFF
[ ] Story beat reads (sound off test)
[ ] Principles checklist passed (D65)
[ ] Contacts/planting clean, no sliding (D66)
[ ] Locomotion/gait correct for the anatomy (D66–D73)
[ ] Acting intent readable; eyes + face complete (D61–D63)
[ ] Secondary motion present, subtle, not noisy (D77)
[ ] Curves clean, no jitter (D78)
[ ] Sim passes (cloth/hair/fur) baked and approved (D39/D47)
• 
• 
• 
• 
• 
• 
• 
• 
CHAPTER 8 — ANIMATION: PRINCIPLES, LOCOMOTION, CREATURES, ACTING, POLISH
