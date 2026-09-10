# Chapter 7 — Facial Rigging, Facial Animation, Lip Sync, Eye Systems (D60–D63)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 80–82 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 7 — FACIAL RIGGING, FACIAL
ANIMATION, LIP SYNC, EYE SYSTEMS
Domains D60–D63. The face is 80% of performance. These systems convert a static head into an
instrument of emotion.
D60 — FACIAL RIGGING [SIT]
DEF: The control system for the face: jaw, lips, brows, cheeks, nose, eyelids, plus muscles-level
blendshapes — driven by bones, shape keys, or both. WHY: The face must produce every expression
(D08 expression sheet) with predictable controls. Facial rigging is where rigging art meets anatomy
(facial muscles) and acting. HOW (the two pillars): 1. Bone-driven facial rig: small bones for jaw,
brows, lips (each lip region), cheeks, nose, eyelids, ears. Cheap, deformable, style-agnostic; great for
stylized and for creatures. Uses the same constraint/driver machinery as the body (D48–D55). 2.
Shape-key (blendshape) facial rig:  30–100+ shape keys for phonemes (D62) and expressions,
driven by a control rig (bones or custom properties). The industry standard for realistic faces and lip
sync  (it  matches  facial  motion-capture  and  blendshape  pipelines).  Blender  supports  shape  keys
natively; the control rig drives them via drivers. The hybrid standard: bones for gross motion (jaw,
head) + shape keys for fine motion (lips, brows, cheeks) + corrective shape keys layered on top
(D59). Facial anatomy map (what the rig must cover): - Jaw: opens (rotate at the jaw joint near
the ear), side-shift (small). - Lips: 8–12 control points around the mouth ring (upper/lower × center/
quarter/corner) — must do  all phonemes (D62). -  Brows: inner/outer/center raises + furrow; each
brow independently (asymmetry = life). - Eyelids: upper/lower; blink; squint. - Cheeks: raise (smile),
puff (blow), hollow (suck). -  Nose: flare, wrinkle (subtle). -  Ears: wiggle (optional). -  Tongue: 3–6
bone chain (D35) for L/T/D sounds. -  Teeth: parented to jaw (lower teeth move with jaw).  Key
technique — the expression library:  build a library of  named expression shape keys  (Angry,
Happy, Sad, Fear, Surprise, Disgust, Contempt + character-specific) as  poses (Action constraints /
pose libraries or driven shape keys), so animators blend them like an actor's vocabulary.  PARAM:
control count; shape key count; driver mapping; blink system; expression library. MIST: facial rig with
no expression library (animator rebuilds expressions every shot); jaw as a single bone with no lips
(rubber); eyelids that don't follow the eye sphere; asymmetric controls missing (only symmetric
faces).  FAIL: shape key explosions (verts moved wrong); drivers broken after rename.  DIAG: test
every control at extremes; check the driver editor.  FIX: build face on top of  final facial topology
(D24); test each phoneme and expression against the sheet; iterate. EDGES: → D24 facial topology,
→ D59 correctives, → D54 drivers, → D61 facial animation.
Deep chain — Facial rig → Control map → Expression
Jaw → lips (8-12 pts) → brows (inner/outer) → eyelids → cheeks → nose → tongue → expression poses →
driven shape keys → blend map
D61 — FACIAL ANIMATION [SIT]
DEF: Animating the face: expressions, micro-motion, timing of emotion, and the sequence of facial
events. WHY: Faces are read subconsciously; audiences detect fake faces instantly. Facial animation
is acting (D75) at the smallest scale. Core principles: 1. Eyes lead: gaze direction and eye darts
CHAPTER 7 — FACIAL RIGGING, FACIAL ANIMATION, LIP SYNC, EYE SYSTEMS

precede and drive head motion (D63). 2.  Head leads body:  the head rotates  before or  with the
torso; expression changes usually start with the eyes/brows, then mouth. 3. Micro-motion: no facial
pose is held — subtle asymmetries, tiny shifts, breathing, blink cycles (every 3–8 s, faster under
stress). 4.  Expression change logic:  an emotion change = 3–6 frame transition (not instant);
eyebrows precede the mouth; the eyes register the truth, the mouth the social mask (acting nuance).
5. Blink choreography: blink on cut, on emphasis, on thought; avoid mid-movement blinks; squints
for strong emotion. 6.  Timing of poses:  primary pose (2–6 frames), settle/overshoot (2–4), hold;
never pose-to-pose without overlap (D65). WORKFLOW: block the big beats (expression states) →
add head/eye motion → add micro-motion → polish with asymmetry and breathing. MIST: symmetric
face (mirror everything); constant eye contact (no darts); expression "pop" (no transition); static
brows during dialogue. EDGES: → D75 acting, → D63 eyes, → D62 lip sync, → D64 animation.
D62 — LIP SYNC [SIT]
DEF: Mouth  animation  matched  to  dialogue:  phoneme  shapes  (visemes)  timed  to  the  audio
waveform. WHY: Bad lip sync destroys immersion instantly; good sync + good acting reads as a real
performance. Lip sync is 30% mouth shapes, 70% timing and jaw rhythm. HOW: 1. Audio analysis:
place the audio strip; mark phonemes (either by ear, or with Blender's built-in  sound-to-frames
(keyframes from audio amplitude via Graph Editor: Channel → Sound to Samples) for  broad jaw
emphasis; heavy-duty sync usually uses external tools or manual marking). 2.  Visemes (mouth
shapes): the ~12–14 canonical mouth shapes that cover all phonemes: A (ah), E (ee), I (ih), O (oh),
U (oo), M/B/P (closed), F/V (teeth-lip), TH (tongue-lip), L/T/D (tongue up), SH/CH/J (pucker), S/Z (teeth
together), NG/K/G (open back), Q/W (round), rest (neutral). 3. Key the shapes on the viseme shape
keys (or lip controls) with  anticipation: mouths open slightly  before the sound (2–4 frames), close
after; jaw drives most of it. 4.  The rhythm rule:  the mouth moves  with energy, not per-letter —
stress syllables with bigger shapes; unstressed syllables skip shapes (don't animate every phoneme;
animate the  beat). 5.  Combine with acting:  eyes/brows/head carry the emotion; the mouth only
does the sound. Never lip-sync in a vacuum.  PARAM: viseme set; anticipation frames (2–4); jaw
emphasis; blending curves.  MIST: animating every letter (robotic chatter); mouth shapes without
anticipation; no jaw rhythm; sync to the waveform instead of the meaning. DIAG: play with audio —
if the mouth is "behind" the sound, anticipation is missing; if "talking without meaning," acting is
missing. FIX: mark the strong syllables; animate jaw first, then shapes; test with eyes closed (mouth
alone should read). EDGES: → D60 facial rig, → D133 sound, → D75 acting.
Deep chain — Lip sync → Phoneme → Viseme → Mouth shape
Audio → phoneme stream → viseme keyframes → jaw rhythm → lip blends → anticipation → stress emphasis →
blending
D63 — EYE SYSTEMS [SIT]
DEF: Gaze control: look targets, eye bones, blinks, pupils, and focus logic. WHY: The eyes are the
single most powerful performance instrument. Gaze directs the audience; blink timing sells life; pupil
response  sells emotion.  HOW: 1.  Look rig: two eye bones (or one "eye group" with both) with a
Track To / Damped Track constraint to a look target (empty). A head-level empty + a gaze empty:
the head follows the gaze, the eyes lead. The classic  "eyes-lead-head-follows" hierarchy: Gaze
target → (looks) → eyes + head (head constrained with lower influence). 2.  Blink system: eyelid
shape keys or bones driven by a blink driver/control (a custom property "blink" that animator keys,
CHAPTER 7 — FACIAL RIGGING, FACIAL ANIMATION, LIP SYNC, EYE SYSTEMS

or automatic blinking via noise — usually manual for acting control). 3. Pupils: pupil dilation (shape
key or scale) driven by emotion/light (subtle). 4. Focus & eye darts: eyes saccade (jump) between
points;  darts  happen  before  head  turns;  focus  distance  affects  convergence (crossing  for  close
objects — real eyes converge; important for close-ups). Blink timing rules: normal blink every 2–10
s, 100–150 ms; stress → more; emphasis → blink on the downbeat; in conversation, blink during the
other person's turn; never blink mid-gaze-change. MIST: eyes that never look away (unsettling); no
convergence (both eyes parallel even in close-up — dead stare); blink as a single symmetric event
(rarely real); eyeball rotation instead of tracked gaze. DIAG: close-up test: does the character appear
to be looking at the target, or through it? EDGES: → D61 facial animation, → D60 facial rig, → D33
eye shader, → D75 acting.
Deep chain — Eye system → Gaze → Hierarchy
Gaze target → eye darts → head follows (lag) → convergence (focus distance) → blink (timing) → pupil
(emotion) → micro-motion
CHAPTER 7 — FACIAL RIGGING, FACIAL ANIMATION, LIP SYNC, EYE SYSTEMS
