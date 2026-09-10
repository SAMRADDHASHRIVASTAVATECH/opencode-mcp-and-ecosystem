# Depth Chapter 16 — Anatomy & Proportions Libraries

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 136–141 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 16 — ANATOMY &
PROPORTIONS LIBRARIES
Expands  D21,  D04,  D05,  D67–D73.  The  numeric  backbone  of  every  believable  character  and
creature: proportions, joint ranges, muscle forms, and the toolkit for inventing new anatomies that
still read as "real."
16.1 HUMAN PROPORTIONS — THE MASTER TABLE (adult,
head = 1 unit ≈ 22–24 cm)
Landmark Male (7.5 h) Female (7.25 h) Notes
T otal height 7.5 7.25 Stylized ranges: cartoon 3–5, anime 5.5–
6.5, heroic 8–9
Chin 1.0 1.0 —
Nipples 2.0 2.0 (slightly lower +
wider apart)
—
Navel 3.0 3.0 (slightly lower) —
Pubic symphysis (mid-
point)
3.75 3.6 The true mid-point of the body
Fingertips (arms down) ~4.0 (mid-thigh) same Arms reach mid-thigh when relaxed
Wrist ~3.8 ~3.8 Wrist aligns with pubic symphysis
Knees 4.5–4.75 same Knee cap at ~4.75
Calf bulge ~5.5 ~5.5 —
Shoulder width 2.0 1.7–1.8 Male broader (the V-taper)
Hip width 1.5–1.7 1.8–2.0 Female wider (childbirth + fat)
Waist ~1.5 ~1.5–1.6 Male waist lower, female higher (narrower
ribcage)
Hand 0.9 0.9 Hand ≈ face height
Foot 1.0 1.0 Foot ≈ head height
Arm length ~3.4 ~3.4 Shoulder → wrist
Leg length ~4.0 ~4.0 Hip → heel
Neck 0.4–0.5 0.4–0.5 7 cervical vertebrae compressed into the
neck
Eye line ~0.5 (of head) same Eyes at vertical center of head
Head width 0.67 (of head
height)
same Face ≈ 5 eyes wide
Age proportion drift (heads tall): newborn 3.5–4 → toddler 4.5 → child 5.5 → tween 6 → teen 6.5–
7 → adult 7.25–7.5 → elderly 7 (compressed spine, bent posture). Big head + short limbs = young;
the head grows slowest, so adults have proportionally smaller heads — this is the single strongest
age cue in design.
DEPTH CHAPTER 16 — ANATOMY & PROPORTIONS LIBRARIES

16.2 BODY TYPE SPECTRA (numeric ranges for design)
Type Shoulder:hip
ratio
Waist
definition Mass feel Motion character
Slim/ectomorph 1.3–1.5 weak low light, quick, fragile
Average/
mesomorph
1.5–1.7 moderate medium neutral
Athletic 1.6–1.8 strong V medium-high powerful but fast
Muscular
(bodybuilder)
1.8–2.2 extreme V high deliberate, heavy
Heavy/endomorph 1.4–1.6 none–weak very high grounded, slow, soft
T all (elongated) 1.5–1.7 weak deceptive (looks light,
is heavy)
elegant, lanky
Short/compact 1.6–1.8 strong dense explosive, stable
Exaggerated
(stylized)
1.5–2.5 any any reads instantly — exaggeration
is readability
16.3 STYLIZED PROPORTION ARCHETYPES (the design
language of D04)
Archetype Heads
tall Key distortions What it communicates
Chibi/super-
deformed
1.5–2.5 Huge head, tiny body, big eyes Cute, comic, young, non-
threatening
Cartoon child 3–4 Large head, short limbs, soft forms Cute, energetic, silly
Cartoon adult 4–5 Slightly large head, exaggerated hands/feet Comedic, expressive, readable
Anime/shoujo 5.5–6.5 Large eyes, small nose/mouth, slim, long legs Emotional, idealized, elegant
Heroic 8–9 Broad shoulders, narrow waist, long limbs,
small-ish head
Power, ideal, dominance
Elegant/uncanny 9–10 Very long limbs, small head, thin Alien, refined, unsettling
Horror/thin 8–9 Emaciated, elongated neck/fingers, hollow Unsettling, starving, ghostly
Heavy/power 5–6 Short legs, massive torso, thick neck Strength, immovable, brute
The rule:  the  head:body ratio  is the strongest single style signal. Change it and you change the
genre; keep it consistent across a character's sheets (D08).
16.4 HEAD & FACE PROPORTION SYSTEMS
Realistic face grid: eyes at vertical center; eye spacing = one eye width; nose width ≈ eye width;
mouth corners align with the center of the pupils ; ears align with the brow-to-nose lines; hairline to
brow = brow to nose base = nose base to chin (thirds of the lower face). Five-eye width face rule.
The face is ~1/7 of the head width in profile (jaw recedes). Anime/cartoon grid: eyes enlarged and
dropped below the realistic center line; nose minimal (dot/line); mouth small; forehead large; chin
small — the "cute" proportions are realistic proportions with the lower face compressed and the eyes
scaled up. Aging on the face:  eyes/ears/nose keep growing slowly; lips thin; brow ridge thickens;
DEPTH CHAPTER 16 — ANATOMY & PROPORTIONS LIBRARIES

jowls/neck sag; wrinkles follow muscle lines (D16's "muscle form library" below); hairline recedes.
Cartoon aging compresses all of this into: bigger nose, droopier everything.
16.5 SKELETAL JOINT RANGE TABLE (degrees, realistic;
stylize by exaggeration)
Joint Flexion Extension Rotation Notes for rigging (D49)
Neck 60–80° fwd 50° back 80° each side, 40°
rotate
Spine curve; don't break the
head off
Shoulder
(ball)
180° (arm up) 45° back 90° rotation Clavicle lifts the last 60° — auto-
clavicle
Elbow 140–150° ~0° (5°
hyper)
none (1-axis hinge!) Hinge joint — never add roll
Wrist 70° 60° 20° radial/ulnar T wist lives in the forearm (twist
bones, D50)
Fingers 90–100° (MCP), 100° (PIP),
60° (DIP)
~0° spread ~30° Knuckle bulge at MCP
Hip 120° 20° 45° ext rot, 30° int Ball socket; pelvis tilts with flex
Knee 130–140° ~5° none (hinge) Patella tracks; hamstring bulge
on flex
Ankle 20° (dorsi) 50° (plantar) 10° each Foot roll system (D28/5.12)
Spine 90° total flex (mostly
lumbar)
30° 40° rotation
(thoracic)
3 curves; animate as 3 arcs
Jaw 40–50° open — 10° side Rotate at the joint, translate
slightly
Quadruped joint analogies (critical for creatures, D69):  the horse's "knee" = the human wrist;
the hock = the human ankle (digitigrade). A quadruped's front leg flexes backward (like an arm), the
hind leg bends forward at the stifle (knee). Misunderstanding these analogies is the #1 quadruped
rigging error.
DEPTH CHAPTER 16 — ANATOMY & PROPORTIONS LIBRARIES

16.6 MUSCLE FORM LIBRARY (surface forms that drive
sculpting, D22)
Region Forms to sculpt Direction/behavior notes
Neck Sternocleidomastoid (V from ear to collarbone), trapezius
slope
SCM rotates the head; trapezius bulges on
shoulder raise
Shoulder Deltoid (3 heads cap), rotator cuff crease Cap over the joint; the "shoulder pad" look
Chest Pectoralis (upper/lower), clavicle line, sternal groove Pectoral anchors at armpit; lower pec swings
on arm lift
Back Trapezius (diamond), lats (wings), erector columns,
rhomboids
Lats flare when arms lift; spine furrow center
Abdomen Rectus sheath (6-pack = 2×3), obliques (love handles),
serratus (ribs saw)
Abs compress on bend; obliques define waist
Arm Biceps (2 heads), triceps (3 heads, horseshoe),
brachioradialis (forearm), flexors/extensors
Biceps bulge on flex, triceps on extend;
forearm twist = radius/ulna crossing
Glutes Gluteus max (mass), medius (hip dip) The power of gait; hip dip = the "love
handle" crease
Leg front Quads (4 heads, VMO teardrop), patella, tibia crest Quads carry extension; VMO inner teardrop
Leg back Hamstrings (3), calf (gastrocnemius 2 heads + soleus) Calf raises on toe-off; hamstring bulge
behind knee on flex
Hands/
feet
Thenar/hypothenar pads, knuckles, Achilles, plantar arch Fat pads matter as much as muscle in hands/
feet
Sculpt order per region:  bone landmark → muscle masses → fat smoothing → skin fold/wrinkle →
micro detail. Muscles are soft masses under skin , not gym-cut anatomy, unless the style demands
definition.
16.7 QUADRUPED ANATOMY (D68/D70)
Stance types: plantigrade (whole foot: bears/raccoons/humans) · digitigrade (toes only: dogs/cats) ·
unguligrade (hoof tips: horses/deer) — each shifts the ankle/hock higher and lengthens the effective
leg. Digitigrade legs = springs (bounding gaits); plantigrade = weight and stability.
Proportions (body length:leg length) by family:  | Animal | Body type | Spine | Gait signature |
|---|---|---|---| | Horse | deep chest, long neck, high withers, ~1:1 leg/body | stiff mid-back, flexible loins
| 4-beat walk → 2-beat trot → 3-beat canter → 4-beat gallop; head nod up at suspension | | Dog |
flexible S-spine, deep chest | very flexible | all gaits + pacing; back flexes like a wave | | Cat/big cat |
long flexible spine, powerful hind | extremely flexible | gallop with extreme spine extension/flexion;
bounding | | Bear | massive, plantigrade, shoulder hump | stiff, thick | ambling walk, powerful, no
suspension | | Deer/antelope | slender, long digitigrade legs | stiff back | bounding/pouncing, huge
stride | | Reptile (croc/lizard) | sprawling limbs, tail | lateral undulation | legs splay outward, body
wriggles |
Quadruped skeleton map (for rigging, D49):  scapula (slides over ribcage —  not fused like
human!), humerus → elbow (high on the chest) → radius/ulna → wrist (the "knee") → pastern/hoof;
pelvis (elongated) → femur → stifle (knee) → tibia → hock (ankle) → metatarsal → paw/hoof. The front
legs attach at the scapula, which slides  — rig a scapula bone with weight so the withers move
believably (this is the classic quadruped rig failure: frozen shoulders).
DEPTH CHAPTER 16 — ANATOMY & PROPORTIONS LIBRARIES

16.8 AVIAN ANATOMY (D45/D72)
Wing = modified arm: humerus (short) → radius/ulna (forearm) → carpometacarpus + digits
(the hand). Primary flight feathers attach to the hand, secondaries to the forearm, coverts over
the top — three rows that fold like a fan (D45).
Keel (sternum): the massive chest muscle anchor — the keel shape is what makes bird torsos
"boat-shaped."
Feather map: contour (body), flight (wings), down (insulation), filoplumes (sensory). Feather
growth direction: head → tail, out from the spine.
Proportion examples: hummingbird ~ 30% of body length is beak+wings; swan long neck (20+
vertebrae vs 13 for most birds); owls = huge wingspan for body mass (silent slow flight); albatross
= 3.5 m wingspan, locks wings for gliding (no flap).
Flight mechanics for animation (D72): downstroke = power + lift (wingtip arcs forward-down);
upstroke = recovery (wingtips trail); the wrist and elbow flex differently each phase; gliding =
wings in slight dihedral, locked at the shoulder.
16.9 INSECT ANATOMY (D71)
Body plan: head – thorax – abdomen. All 6 legs + wings attach to the thorax; the abdomen is
pure digestive/reproductive mass. Legs on a creature → count the thorax segments.
Leg anatomy (per leg): coxa → femur → tibia → tarsus (foot). Joints: coxa-thorax (ball), femur-
tibia (hinge, the big fold), tibia-tarsus (hinge). The fold pattern: legs fold forward in stance phase, 
extend in swing (the metachronal wave, D71).
Locomotion classes: walking (tripod, D71), running (metachronal waves speed up), jumping
(grasshopper: huge femur = spring), flying (2 wings × flapping, or 2-pair with fore/hind coupling),
swimming (diving beetles: oar-legs).
Exoskeleton logic: hard plates (tergites/sternites) with flexible membranes at joints — model
segments as rigid plates with a soft connective (this is the armor-on-soft-body logic of D41,
applied to a whole creature).
Design lever for invented multi-legs: limb count → stability polygon (D71); insect-inspired =
tripod; spider-inspired = alternating tetrapods; centipede = waves. Match the gait to the anatomy
or it reads as wrong instantly.
16.10 AQUATIC ANATOMY (D73)
Body forms (the classic ichthyology set):  | Form | Shape | Speed | Examples / animation notes |
|---|---|---|---| | Fusiform (torpedo) | streamlined ellipse | fast, sustained | tuna, sharks, dolphins — the
default "fast swimmer" | | Compressed (deep) | tall, thin side | maneuverable | angelfish, discus —
fluttery,  turning  |  |  Elongated  |  long,  thin  |  wriggler  |  eels,  needlefish  —  whole-body  wave  |  |
Depressed (flat) | flat top/bottom | bottom dweller | rays, flounder — wing-like fin waves | | Globular |
round, stiff | slow, floaty | pufferfish, sunfish — hovering |
Fin map: pectoral (steering/braking), pelvic, dorsal (stability), anal, caudal (propulsion — shape tells
speed: forked = fast, rounded = slow).  Tail orientation: fish =  vertical fluke (side-to-side wave);
cetaceans (whales/dolphins) = horizontal fluke (up-down beat) — a vertical fluke on a mammal reads
wrong (D73). Squid/cephalopod: mantle + jet propulsion (rapid, then glide), arms trail; octopus =
limbed crawling + jetting.  Sea creatures for fantasy:  combine fish forms with mammal/surface
traits (mermaids = human torso + fish tail; the joint at the waist is the design decision).
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
DEPTH CHAPTER 16 — ANATOMY & PROPORTIONS LIBRARIES

16.11 LIMBLESS ANATOMY (snakes, worms, tentacles)
Snake: vertebra count 200–400; ribs along most of the body; locomotion modes: lateral
undulation (classic S-wave, head→tail), rectilinear (caterpillar — belly scales grip, for heavy
snakes), sidewinding (desert — diagonal coils), concertina (climbing — anchor and pull).
Animation rule: the wave always travels head→tail with increasing amplitude toward the tail; the
head leads and steers; never wiggle the whole body as one S (it should look like a traveling wave
— track a point on the body and it moves forward, not sideways).
Tentacles/limbs (D50): 3–6 segments minimum for convincing curl; taper; the base is thick and
stiff, the tip thin and whip-like; suckers/ridges as surface detail (alpha/bump).
Rigging: BBone chains (D50) with curvature; or FK chains with stretch; tentacle tips need "aim"
controls (D53 Track T o).
16.12 THE INVENTED CREATURE TOOLKIT (D05 + D69 in
practice)
Mashup matrix — combine a body plan (biped/quadruped/multi-leg/limbless/flying/swimming) × 
a surface (fur/feathers/scales/chitin/skin/crystal/metal) × a mass class (feather-light/light/medium/
heavy/massive) × a sensory head (predator/prey/forager/unknown). Every combination is a valid
creature if the parts agree with the physics rules below.
Physics rules (non-negotiable): - Center of mass must sit over the support polygon when
standing (D71/D76) — or the creature needs a reason to fall (and then it should fall). - Wings have
a maximum load: wing area × air density must plausibly lift the mass (heavy + tiny wings =
grounded; design the wings or change the mass — or give it magic, and say so in the world rules,
D02). - Each leg must be able to hold the body's weight: bone/strut thickness scales with mass (an
elephant leg is a column; a deer leg is a spring). - Joint count ≤ what the animation budget can
pose (D48 rule: every joint is animation time). - Spine flexibility = locomotion range (rigid spine =
stiff gait, flexible = undulation).
Believability checks (from D05): could it stand? breathe? eat? reproduce? Would a zoologist
ask "where does the muscle attach?" If a feature has no functional story, either give it one (crystal
plating = armor against the city's predators) or remove it.
Original locomotion derivation: pick the closest real class, study its gait (D68), then modify by
the creature's differences (more legs → D71 tripod math; heavier → slower timing + more planted
feet; floating → D72 glide logic + hover cues like drift and bobbing).
The "silhouette + motion" test: a stranger should be able to identify the creature's species/
mood from its silhouette at rest (D04) and from one second of motion (D69) — if both read, the
anatomy works.
• 
• 
• 
• 
1. 
2. 
3. 
4. 
5. 
DEPTH CHAPTER 16 — ANATOMY & PROPORTIONS LIBRARIES
