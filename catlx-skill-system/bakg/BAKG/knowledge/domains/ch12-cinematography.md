# Chapter 12 — Camera, Cinematography, Shot Design, Camera Movement (D102–D107)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 101–103 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 12 — CAMERA, CINEMATOGRAPHY,
SHOT DESIGN, CAMERA MOVEMENT
Domains D102–D107. The camera is the audience's eye: it decides what they see, when, from where,
and how they feel about it. Cinematography is the grammar of that eye.
D102 — CAMERA [REQ]
DEF: The Blender camera object: lens, sensor, framing, and output configuration. WHY: The camera
defines the view — focal length changes the whole mood and geometry of a shot; sensor and aspect
set the frame; the camera is where cinematography (D103) meets rendering (D112). HOW (camera
object essentials): - Lens & focal length: 15–24 mm (wide: space, drama, distortion), 35–50 mm
(normal, neutral, "human eye"), 85–135 mm (tele: compression, intimacy, flattering close-ups). Focal
length is a creative decision, not an accident — see D105. - Sensor: physical sensor size (36×24 mm
full-frame typical) × Aspect Ratio (16:9, 2.39:1 cinematic, 1.85:1, 4:3) and resolution (D14). A larger
sensor = wider view at same focal length (full-frame vs phone-sensor crop). -  FOV: field of view
(derived from focal length + sensor); in Blender, set Focal Length (mm) directly. -  Depth of field
(DoF): camera → Depth of Field: enable, set Focus Distance (or target object) + Aperture (F-stop):
lower f-stop (f/1.4) = shallow DoF (bokeh); higher (f/8) = deep focus. DoF is  expensive in Cycles
(defocus) — render DoF in compositing (D117) for big scenes. - Clipping: near/far clip — set far clip
big enough for the scene (or objects vanish!). - Camera rig: parent the camera to a rig (empty) for
controlled  moves  (D107);  or  use  constraints  (Track  T o  a  target).  PARAM: focal  length;  sensor;
aperture/focus; clipping; resolution/aspect; motion blur (in render settings, D112). MIST: default 50
mm for everything (boring coverage); DoF at render that should be comp; far clip cutting the scene;
no camera rig for moves. EDGES: → D105 lens, → D107 movement, → D112 render, → D117 comp
DoF .
D103 — CINEMATOGRAPHY [REQ]
DEF: The language of shots: how coverage (which shots, which order) tells the story visually. WHY:
The same scene cut differently tells different stories; cinematography is  meaning through shots .
Mastery = knowing what each shot does to the audience. Core shot grammar: - Establishing shot
(wide): where we are. Medium: who is here. Close-up: how they feel. Extreme close-up: what
they feel about it. - Shot/reverse-shot: conversation coverage (A over B's shoulder, B over A's) —
the dialogue standard. -  Insert: the detail that matters (a hand, a note) — used to  emphasize. -
Cutting logic (D120 editing):  match on action, eyeline match, cut on motion — cuts should feel
invisible. -  Coverage plan:  for each beat: master shot + close-up + inserts; the editor (D120)
assembles. - Continuity (the 180° rule):  keep the camera on one side of the action line (the 180°
line between characters); crossing it flips screen direction and disorients. (Cross  deliberately for
effect — never accidentally.) - Screen direction: characters moving left stay moving left across cuts
(unless the story says turn around).  PARAM per shot:  shot size (D106); angle; lens; movement;
duration; eyeline match; continuity of screen direction. MIST: random coverage (no plan); no master
shot (editing has nothing to cut to); breaking the 180° line accidentally; coverage that doesn't serve
the beat. EDGES: → D106 shot design, → D120 editing, → D104 composition.
CHAPTER 12 — CAMERA, CINEMATOGRAPHY, SHOT DESIGN, CAMERA MOVEMENT

D104 — COMPOSITION [REQ]
DEF: The arrangement of visual elements inside the frame: balance, focal point, leading lines, and
negative space.  WHY: Composition directs the eye to the story and creates emotion  before the
content registers. It's the static art of the moving image. Core tools: - Rule of thirds:  place the
subject on third-lines/intersections (Blender: camera view → overlay "Thirds" guide). -  Focal point
hierarchy: one clear subject; support elements arranged to lead to it (lines, contrast, focus). -
Balance: visual  weight  (size,  contrast,  position)  —  asymmetric  balance  is  more  dynamic  than
symmetric.  -  Leading lines:  roads,  edges,  gaze,  light  shafts  (D111)  pointing  at  the  subject.  -
Headroom & look room: space in front of the character's face/gaze; too little = claustrophobic, too
much  =  lost.  -  Negative  space: emptiness  as  a  compositional  element  (loneliness,  scale,
anticipation). - Foreground/mid/background layers: depth in composition — a foreground element
(branch, arch)  frames the subject and adds scale. -  Rule of odds, golden ratio, triangles  —
refinements beyond thirds. The composition checklist per shot: What is the eye supposed to land
on first? Are there competing focal points? Do lines support or fight the subject? Is the frame alive
(layers, depth)? Does it serve the beat (D01)?  MIST: centering everything (static); no foreground
depth (flat); competing elements; headroom errors.  EDGES: → D106, → D104→D110 (atmosphere
adds depth), → D108 lighting (light as composition).
D105 — LENS & PERSPECTIVE [SIT]
DEF: How focal length + camera position create perspective: wide-angle exaggeration, telephoto
compression, and the math of depth.  WHY: Perspective  is emotion: wide lenses make spaces feel
huge and characters heroic or trapped; telephotos flatten and isolate. Understanding the look of each
lens lets you design it. The lens table: | Focal (FF) | Name | Look | Use | |---|---|---|---| | 14–24 mm |
Ultra-wide | Exaggerated perspective, near-far stretch, barrel-ish | Establishing, action, epic scale,
cramped spaces | | 28–35 mm | Wide | Slight exaggeration | Wide shots, environment + character
together | | 40–55 mm | Normal | Neutral, "human" | Dialogue, reality feel, most versatile | | 70–100
mm | Short tele | Mild compression, flattering faces | Portraits, close-ups, intimacy | | 135–200+ |
T elephoto | Strong compression (background flattened onto subject), shallow DoF | Isolating subjects,
distant action, crowds | | Macro | — | Extreme close, tiny DoF | Inserts, details | The compression
trick: telephoto compresses distance between planes (mountains stack); wide separates planes. Use
tele for "wall of people" and "closing gap" tension; wide for "empty vastness."  Camera height &
angle  (also  D106): eye-level  =  neutral;  low  angle  =  power/hero;  high  angle  =  vulnerability/
overview; Dutch (tilted horizon) = unease/energy. MIST: zooming with the camera instead of dollying
(zoom  distorts  perspective  —  only  dolly  changes  perspective;  zoom  only  crops  —  know  the
difference!); mixing lens looks across a conversation (jarring). EDGES: → D102, → D104, → D107.
D106 — SHOT DESIGN [SIT]
DEF: Choosing the right shot (size, angle, lens, movement) for each story beat — the bridge between
storyboard (D09) and camera. WHY: The shot is the unit of audience experience; the wrong shot kills
the beat no matter how good the animation. Shot sizes (the ladder):  Extreme Wide (landscape/
context) → Wide (character in environment) → Full (full body) → Medium (waist/knees up) → Medium
Close-up (chest up) → Close-up (face) → Extreme Close-up (eyes/mouth/detail). Over-the-shoulder
(OTS): dialogue standard (see D103). Angles: eye-level, low, high, bird's-eye, worm's-eye, Dutch —
each an emotional statement (D105). Movement: static (stillness = weight/gravity), pan/tilt (reveal),
CHAPTER 12 — CAMERA, CINEMATOGRAPHY, SHOT DESIGN, CAMERA MOVEMENT

dolly (approach/retreat), crane (rise/fall), orbit (encircling = tension), handheld (energy/unrest —
D107). Duration: shots breathe with the beat: action = 1–3 s, tension = hold, emotion = linger. The
shot design method: for each beat: (1) what must the audience feel? (2) what must they see? (3)
pick size+angle+lens+movement that does both; (4) storyboard it (D09) and check in previs (D11).
MIST: defaulting to medium shots for everything; shots that contradict the beat (a wide for an
intimate secret); unmotivated camera moves. EDGES: → D09, → D103, → D104, → D107.
D107 — CAMERA MOVEMENT [SIT]
DEF: The motion of the camera: physical moves (dolly, crane, steadicam) and their meanings;
handheld energy; the "motivated" camera.  WHY: Camera movement is  emotion in motion : it can
reveal, follow, emphasize, or destabilize. The rule: every move needs a reason (motivated by story
or character). Moves and meanings: - Dolly in: intrusion, intimacy, focus ("push in" = emphasis). -
Dolly out: reveal, isolation, release. - Tracking (lateral): following motion, discovery (often with the
subject moving). -  Crane/rise: revelation of scale, ascension, triumph;  crane down:  diminishing,
discovery.  -  Pan: scanning,  revealing  space;  tilt: revealing  vertical  (a  tower,  a  face).  -  Orbit:
encircling = entrapment or celebration (360 around a hero). -  Handheld: documentary energy,
unease, intimacy;  camera shake:  impact, weight (earthquake, hit). -  Focal moves:  rack focus
(D102) — shifting focus between planes  as a storytelling move.  Technique (Blender): -  Camera
rig: parent  camera  to  an  empty  chain  (rig)  and  animate  the  empty(s)  —  separates  path  from
pointing.  -  Curves: camera  path  =  a  curve  with  a  "Track  T o"  empty  along  it  (the  professional
standard: animate the empty on the curve, camera tracks the target). - Easing: every camera move
needs slow-in/slow-out (D65 — cameras obey the principles!); hard stops = weight. - Handheld: add
subtle noise (noise modifier on the camera's location/rotation F-curves — small amplitude, high
frequency) + breathing (slow drift). -  Shake: quick keyed shakes (3–6 frames each) on impact; or
noise with high amplitude decaying.  PARAM: move type; duration; easing; amplitude (shake); rig
structure.  MIST: unmotivated moves (camera that never stops = seasick); moves without easing
(jerky); dolly instead of zoom confusion (D105); handheld noise as a constant (nausea). EDGES: →
D102, → D106, → D65 (principles apply to cameras!), → D117 (stabilization/camera pass).
CHAPTER 12 — CAMERA, CINEMATOGRAPHY, SHOT DESIGN, CAMERA MOVEMENT
