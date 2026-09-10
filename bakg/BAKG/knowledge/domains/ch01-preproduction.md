# Chapter 1 — Pre-Production (D01–D12, D130)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 48–53 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 1 — PRE-PRODUCTION: STORY,
WORLD, CONCEPT, DESIGN, REFERENCE,
BOARDING [SIT→REQ]
Domains D01–D12 plus D130 (Grease Pencil boarding). Pre-production decides what the film means
and what it needs. Every hour spent here saves days of rework — and every skipped decision
surfaces later as a costly ambiguity.
D01 — STORY & SCRIPT [SIT]
DEF: The narrative spine: what happens, to whom, why it matters, and how it resolves.  WHY:
Animation communicates emotion and idea through sequenced intent. Without a story, shots have no
reason to exist; audiences feel "pretty but empty." HOW: Classic structures (three-act, hero's journey,
or minimal setups for loops) decompose into beats (moments of change). Each beat = 1–3 shots. The
beat list becomes the shot list becomes the asset list. USE: Any film with duration, narrative, or an
emotional  point.  AVOID: For  a  single  looping  turntable/effect  shot  —  a  "micro-story"
(setup→action→payoff) is enough.  PARAM: logline; protagonist/goal/obstacle/stakes; beats; pacing
(beats  per  minute);  POV;  theme;  ending  emotion.  MIST: overwriting  (a  2-min  film  ≠  a  novel);
characters with no goal; no payoff; no emotional change; forgetting the audience's experience. FAIL:
story requires impossible shots → production collapse. DIAG: if any beat cannot be boarded simply,
simplify the beat. FIX: cut the story to its emotional core; move complexity to visuals. EDGES: → D09
storyboard, → D10 animatic, → D120 editing, → D133 sound.
Node card — The Beat
DEF: the smallest unit of story change (a look, a step, a reveal).
PARAM: type (setup/turn/payoff), emotion, information delivered, shot count needed.
PROD: 1 beat ≈ 1–3 seconds for loops, 5–15 s for narrative shorts. Board every beat.
Deep chain — Story → Structure → Beat → Shot → Moment
Beat → emotional change → action required → camera distance (D106) → duration → staging → animation
intensity → edit rhythm
D02 — WORLDBUILDING & LORE [SIT]
DEF: The rules and fabric of the story's world: physics, climate, tech/magic level, culture, history,
economics.  WHY: Consistency  is  what  makes  fantasy  believable.  A  rainy  city  (cloaks,  puddles,
reflections, moss, damp materials) vs a desert fortress (dust, dry cloth, harsh light) changes every
downstream system: D37 clothing, D79 environment, D108 lighting, D94 water, D99 weather. HOW:
Write a "world bible" of 1–3 pages: setting, climate/weather, time of day, tech/magic rules, palette,
culture cues. Distill into design constraints per asset. PARAM: setting list; climate & seasons; tech/
magic system with explicit limits; palette & light rules; economy (what materials exist); scale (city
size, travel times). MIST: magic with no rules (kills stakes); mismatched tech (anachronism); palette
without logic; overbuilding lore no one sees.  FAIL: audience confusion.  FIX: surface one rule per
• 
• 
• 
CHAPTER 1 — PRE-PRODUCTION: STORY, WORLD, CONCEPT, DESIGN, REFERENCE, BOARDING [SIT→REQ]

scene, show don't tell. EDGES: → D83 world building (visual), → D80 terrain, → D81 architecture, →
D108 lighting.
D03 — CHARACTER CONCEPT [SIT]
DEF: Who the character is: personality, role, backstory, abilities, movement style — before any
drawing. WHY: The concept fixes the physical language (posture, tempo, energy) that design (D04),
rig (D48) and animation (D75 acting) all serve.  HOW: Build a concept sheet: role in story; 3–5
personality  adjectives;  temperament  (calm/volatile);  energy  level;  physical  capability  (strength,
speed,  agility);  movement  style  (fluid,  mechanical,  predatory);  age;  social  role;  flaw.  PARAM:
silhouette  keywords;  posture;  base  tempo;  gesture  vocabulary;  facial  default  expression;  color/
lighting  affinity.  MIST: designing  the  body  before  the  personality  (result:  pretty  but  lifeless);
conflicting cues (childlike face + brutal posture). EDGES: → D04 design, → D05 creature design, →
D75 acting, → D66 locomotion.
D04 — CHARACTER DESIGN [REQ]
DEF: The visual realization of concept: silhouette, shape language, proportions, palette, and detail
hierarchy. WHY: The audience must read personality at a glance  — from silhouette first, then color,
then detail. Design decisions are the cheapest high-impact decisions in the whole pipeline.  HOW
(workflow): 1. Thumbnails: 10–20 rough silhouettes per character (black shapes on white). Pick 3–
5.  2.  Shape  language: choose  primary  shapes  (round=soft/friendly,  angular=aggressive,
vertical=authority, horizontal=stability/weight). 3.  Refine: build the chosen silhouette with clear
values (light/dark zones). 4.  Palette: 2–3 dominant colors + 1 accent; avoid equal-value colors
(mud). 5. Detail hierarchy: decide where the eye should land (face/hands/emblem); put the most
detail there. 6. Turnaround & callouts: front/side/back + material notes (see D08). PARAM (per
body): head/body ratio (see proportions below); shoulder:hip width; limb length/thickness; silhouette
complexity (detail budget); asymmetry notes. Key proportion decisions: - Realistic human: ~7–8
heads tall; head/body ≈ 1:7.5; shoulders ≈ 1.5–2 heads wide. - Stylized/cartoon: 2–5 heads tall; big
head, short limbs for cuteness; tiny head + long limbs for elegance/uncanny. - Heroic: 8–9 heads,
wide  shoulders,  tapered  waist,  strong  V-torso.  -  Chibi/cute: 1–2  heads  body  ratio,  huge  eyes,
minimal nose. MIST: designing only the front view (side profile breaks); too much detail everywhere
(no focal point); color everywhere (no hierarchy); ignoring silhouette readability at small size; no
material callouts (modeler guesses). DIAG: blur your thumbnail — if the character isn't recognizable
as itself, silhouette fails.  FIX: iterate silhouettes until readable; then lock. Never "fix it in 3D."
EDGES: → D08 sheets, → D19/D20 modeling, → D48 rig, → D37 clothing, → D43 hair.
Deep chain — Design → Shape language → Silhouette → Readability
Silhouette → value contrast → negative space → focal detail → hierarchy → color → texture callout →
material plan Proportions → head ratio → limb ratio → center of mass → posture → weight feel → motion
implication
D05 — CREATURE DESIGN [SIT]
DEF: Design  of  non-human  life  with  internal  logic:  anatomy  must  support  the  silhouette,  and
behavior must support the anatomy.  WHY: Audiences forgive fantasy only when the creature is
CHAPTER 1 — PRE-PRODUCTION: STORY, WORLD, CONCEPT, DESIGN, REFERENCE, BOARDING [SIT→REQ]

internally consistent — bones, muscles, joints, and motion all agree. Inconsistent creatures read as
"broken 3D," consistent ones as "real." HOW: Start from a real-world anchor (the "it's like a ___ but
___" rule: e.g., "a crocodile with a mantis's head and an owl's wings"), then extend logically. Build a
creature  spec  sheet:  -  Locomotion  class: biped  /  quadruped  /  multi-legged  (n)  /  limbless
(serpentine) / flying / swimming / climbing / burrowing. - Mass & center of mass: where weight sits
drives posture and gait (D69). - Skeleton logic: spine curvature, limb joint count (never more joints
than the animation can support unless rigged mechanically), digit structure, tail as counterweight. -
Surface: skin/scales/fur/feathers/chitin/plates — each implies material, grooming, and sim cost (D32/
D44/D45). - Sensory organs: eyes (predator forward / prey side), ears, antennae — they drive the
head's design and the facial rig. -  Extras: horns, antlers, mandibles, gills, spikes — decorative vs
functional; functional extras get rigs. Believability checks: (1) Could it stand? (2) Could it breathe/
eat? (3) Does every decoration have a function or a story? (4) Would its gait match its mass? If "no,"
fix the design, not the animation. PARAM: limb count; joint scheme; spine type; weight class (light/
medium/heavy); speed class; environment adaptations. MIST: wings on an elephant (mass says no);
head bigger than the neck can hold; 8 legs animated like 2 pairs; no reference anchor → mush.
EDGES: → D20 creature modeling, → D22 sculpting, → D69–D73 movement, → D45 feathers, → D44
fur, → D36 claws.
Node card — The Creature Spec Sheet
DEF: the contract between design and every downstream system.
FIELDS: locomotion class; mass; skeleton sketch; surface plan; sensory plan; special systems
(venom, camo, flight, bioluminescence); behavior notes; scale vs. environment.
PROD: hand this sheet to modeler, rigger, animator, and lookdev — everyone works from the
same logic.
D06 — AI CONCEPT DEVELOPMENT [OPT]
DEF: Using  local  image-generation  models  (Stable  Diffusion,  SDXL,  and  derivatives)  to  explore
concepts, variations, and style before/during 2D design. WHY: AI is a concept engine: it produces 100
explorations in the time a human draws 3. Speed and breadth of iteration, especially for creature/
environment  ideas  and  color/style  variants.  HOW  (Blender-centered  workflow): 1.  Prompt
construction: subject + action + setting + style + lighting + lens + quality tags . Negative prompt
removes common artifacts (extra limbs, text, watermarks, bad anatomy). 2.  Checkpoints: base
models defining the style (photoreal, anime, painterly). Choose the checkpoint that matches target
style. 3.  LoRAs: small style/subject adapters (e.g., "creature concept art LoRA") that bias output
without changing the base. 4.  ControlNet — the key to  useful images: control the composition: -
Canny/line: force line-art structure (great for turnaround lines). - Depth: force depth/pose structure
(great for posing a concept). - Pose (OpenPose): exact skeleton pose — ideal for exploring a character
in a specific stance. -  Normal/scribble: structure without strict lines. 5.  img2img: restyle/refine an
existing sketch;  inpainting: edit a region (e.g., "change cloak to crystal armor");  outpainting:
extend the canvas. 6. Character consistency: use a fixed seed + consistent prompt skeleton + a
character LoRA; generate expression sheets and outfit variants from one base; beware consistency
drift — re-ground with ControlNet pose + inpaint fixes. 7. Turnaround generation: generate front/
side/back from one concept (ControlNet depth/canny + careful prompts); treat results as proposals,
then redraw cleanly for the final sheet.  Critical rule (the user's own framing):  AI images are
CONCEPT / REFERENCE / EXPLORATION / DESIGN DEVELOPMENT  — not production assets. An
AI image is flat, inconsistent, and un-topologized. The concept must be  translated into a real 3D
model by a human pipeline: - choose the best variant → redraw as a clean character sheet (D08) →
resolve proportions/consistency → then D19/D20 modeling. PARAM: model/checkpoint; LoRA stack;
• 
• 
• 
CHAPTER 1 — PRE-PRODUCTION: STORY, WORLD, CONCEPT, DESIGN, REFERENCE, BOARDING [SIT→REQ]

sampler & steps (typically 20–40); CFG/guidance (4–12); resolution (SDXL ≈ 1024); seed; ControlNet
preprocessor + weight; img2img denoise strength (0.3–0.7 for edits, 0.7–1.0 for full restyle). MIST:
using AI output directly as final concept (inconsistency, wrong anatomy, no seams); spending hours
fighting prompts for what a 5-minute sketch fixes; ignoring negative prompts; no design intent (AI
without art direction is noise). PRO: extreme iteration speed; style exploration; ideation for creatures/
environments;  inspiration  when  blocked.  CON: anatomy/proportion  errors;  inconsistency  across
views; style soup; no ownership of the decision. PERF (local): run locally with GPU (ComfyUI/A1111);
CPU-only is slow — cap resolution, use 2× upscale pass. PROD: use AI in the ideation phase only;
always keep the human design hand as the gate (D08 sheets are human-cleaned). EDGES: → D04
design, → D07 reference, → D08 sheets.
D07 — REFERENCE DEVELOPMENT [REQ]
DEF: The  deliberate  collection  and  study  of  external  reference:  photos,  video,  anatomy  plates,
material samples, fabric studies, animal gaits. WHY: Every surface, joint, gait, and material already
exists in reality or in the great library of art. Reference protects the artist from "memory errors" — the
main reason 3D looks fake. HOW: 1. Per-asset reference boards (use PureRef — free — or Blender
image planes in a reference scene). 2. Categories: anatomy/structure; material & surface (macro +
micro); lighting conditions; motion (video/loops); historical/technical (for props/armor); style reference
(other art). 3.  Study ritual:  before modeling, sketch/draw the reference from memory; compare;
correct. Before animating, act it out; film it (D12).  PARAM: board per asset; label sources; keep
motion refs as video loops.  MIST: designing from memory; one tiny reference photo for a whole
creature;  no  motion  reference  for  movement-heavy  shots.  EDGES: →  D04/D05  design,  →  D21
anatomy, → D12 motion reference.
D08 — CHARACTER SHEETS [SIT — required for any
character]
DEF: The formal 2D specification of a character: turnaround, expressions, proportions, callouts. WHY:
It is the  contract: modelers need proportions, riggers need joint logic, animators need proportions
and expression ranges. Without it, each discipline invents its own version. Contents: - Turnaround:
front,  side  (both  sides),  back,  three-quarter  views  —  same  height  line,  same  proportions.  -
Proportion sheet:  head-unit grid overlay (e.g., "7.5 heads tall"), key measurements labeled. -
Expression sheet: 6–12 expressions (neutral, joy, anger, fear, sadness, surprise, disgust, contempt
+  character-specific).  -  Detail  sheets: hands,  feet,  face  features,  accessories,  materials  (with
roughness/color  samples).  -  Scale  sheet: character  next  to  environment  reference  and  other
characters. - Color/texture callouts: swatches + notes (e.g., "cloak: wet wool, desaturated blue").
Blender usage: import sheets as image planes/empties in a reference scene (background images);
use them as modeling reference.  MIST: front-only sheet (side profile invented later → topology
rework); expression sheet at different proportions; no scale sheet. EDGES: → D19 modeling, → D48
rig, → D43 hair, → D37 clothing.
D09 — STORYBOARD [SIT]
DEF: Shot-by-shot drawings: framing, staging, action, camera angle, and timing notes per shot.
WHY: The cheapest place to fix staging and shot flow. Boards turn beats into  camera decisions . 
CHAPTER 1 — PRE-PRODUCTION: STORY, WORLD, CONCEPT, DESIGN, REFERENCE, BOARDING [SIT→REQ]

HOW: Per shot draw: frame (what camera sees), camera notation (size/angle/move — see D106),
character staging, action arrows, timing notes, dialogue/audio notes. Use Grease Pencil in Blender
(D130) or paper/external tools; import to Blender for the animatic. PARAM: shot number; shot size
(D106);  angle;  camera  move;  action;  duration  (seconds/frames);  audio  cue.  MIST: no  camera
notation (animators guess); boarding the "nice" shot instead of the story shot; too many cuts (muddy
pacing). EDGES: → D10 animatic, → D106 shot design, → D104 composition.
D10 — ANIMATICS [SIT]
DEF: Storyboard images cut to audio with rough timing — the film's first watchable version. WHY: It
validates pacing, shot count, and audio before any 3D cost . If the story is boring at the animatic
stage, no amount of 3D will save it.  HOW (in Blender):  Video Sequencer (VSE): import boarded
images + scratch audio/sound; cut to timing; add camera-move suggestions as note strips; iterate.
For 2D→3D, use Grease Pencil boards or previs renders. PARAM: frame rate (see below); duration per
shot; total film duration; audio sync points.  Frame rate decisions:  24 fps (film standard), 25 fps
(PAL), 30/60 fps (web/game). Pick ONE and set it in Render Properties before any animation.
MIST: boarding without audio (timing drifts); polishing the animatic (it's a sketch); skipping it on
multi-shot films. EDGES: → D11 previs, → D120 editing, → D121 shot management.
D11 — PREVISUALIZATION (PREVIS) [SIT]
DEF: Rough 3D staging of the film: camera layout, blocking stand-ins, basic timing.  WHY: Verifies
spatial story — can the camera see the action? Do sets fit the shots? Do characters fit the sets? —
before modeling investment. HOW: In Blender: place cameras from boards; use primitive stand-ins
(blocks for characters, cubes for sets, Grease Pencil strokes for camera paths ); animate rough
blocking (D64) for timing; render with Workbench or EEVEE viewport captures; cut in VSE. PARAM:
camera per shot; stand-in scale; shot duration; motion timing. MIST: previs without the animatic's
timing; previs at final quality (waste); skipping previs on complex sets. EDGES: → D16 blockout, →
D15 scene organization, → D106 shot design.
D12 — MOTION REFERENCE [SIT]
DEF: Filmed/video reference of the exact motions needed: gaits, weight shifts, actions, acting beats.
WHY: Animation  reads  as  alive  only  when  grounded  in  real  motion  logic  (timing,  weight,
anticipation). Even stylized animation needs real logic as its base. HOW: Film yourself performing the
action  (phone  camera,  tripod,  3  angles);  record  reference  for:  gait  cycles,  weight  transfers,
anticipation/reaction,  facial  expressions  for  dialogue,  animal  footage  (for  creatures),  fabric/hair
motion in wind. PARAM: camera angle matching your shot; frame rate 60 fps+ for slow-mo study;
loop the action. PROD: keep motion ref as video planes in the Blender viewport (background/empty
with video texture) or side-by-side viewer; scrub frame-by-frame. MIST: animating from imagination
for complex actions; one low-quality clip for a nuanced performance. EDGES: → D64 animation, →
D66 locomotion, → D75 acting.
CHAPTER 1 — PRE-PRODUCTION: STORY, WORLD, CONCEPT, DESIGN, REFERENCE, BOARDING [SIT→REQ]

D130 — GREASE PENCIL / 2D ANIMATION [OPT]
DEF: Blender's 2D drawing/animation system (Grease Pencil 3 in 4.3+): strokes, fills, onion skinning,
2D layers.  WHY: Inside Blender for storyboarding, animatics, 2D overlays, motion sketches, and
hybrid 2D-3D shots. HOW: Draw on 2D layers in 3D space; animate stroke frames in the Dope Sheet;
use onion skin; combine with 3D objects in the same scene; render via EEVEE/Cycles. USE: boards
(D09), animatic (D10), 2D characters, effect overlays, cleanup sketches. AVOID: replacing a full 3D
pipeline for projects that need 3D. EDGES: → D09, D10, D120 editing, D100 VFX overlays.
PRE-PRODUCTION → PRODUCTION HANDOFF CHECKLIST
[ ] Logline + emotional goal written
[ ] World bible (climate, tech/magic rules, palette) exists
[ ] Character sheets (turnaround + expressions + scale) approved
[ ] Creature spec sheets (locomotion, mass, surface) approved
[ ] Reference boards per asset complete
[ ] Storyboard + animatic cut to audio, pacing approved
[ ] Previs camera layout done for every shot
[ ] Shot list → asset list → pipeline plan written (D14)
[ ] Frame rate, resolution, render engine, naming convention committed
• 
• 
• 
• 
• 
• 
• 
• 
• 
CHAPTER 1 — PRE-PRODUCTION: STORY, WORLD, CONCEPT, DESIGN, REFERENCE, BOARDING [SIT→REQ]
