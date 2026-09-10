# Depth Chapter 29 — Animation Depth: The Performance Masterclass

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 186–190 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 29 — ANIMATION DEPTH: THE
PERFORMANCE MASTERCLASS
Expands D64–D78. The complete animation craft: pipeline, graph-editor mastery, timing tables, the
12 principles in Blender practice, footwork, acting technique, NLA reuse, and polish. This is the
chapter that turns "keyframes" into performance.
29.1 THE PROFESSIONAL ANIMATION PIPELINE (blocking
deep-dive)
Step 1 — Shot breakdown:  read the beat (D01), the shot brief (D106), the audio marks (D10).
Write: what the character wants, the key poses that tell it, the emotional arc within the shot. Draw 5–
15 thumbnail poses (fast, silhouette-first). This 20-minute step saves hours.  Step 2 — Stepped
blocking: with  Stepped interpolation  (Graph Editor → Keys → Interpolation → Constant, or the
keying menu), key the story poses at the right frames (2–8 frames apart per motion size).  No in-
betweens  yet. Review:  does  the  story  read  in  silhouette?  Iterate  here  —  it's  free.  Step  3  —
Breakdowns: add the transition poses (the mid-points that define arcs and weight transfer — the
"down" of a step, the passing pose, the anticipation extremes). Still stepped.  Step 4 — Splining
(per-part, in order): convert to Bezier. The professional order: pelvis/root → spine/chest → head/
neck → arms → hands/fingers → legs/feet → face → secondary.  Do each pass over the whole
shot (don't finish the arm before starting the leg). At each pass, fix contacts and arcs.  Step 5 —
Polish passes: (1) timing & spacing per motion; (2) arcs (motion paths); (3) weight & balance; (4)
overlap/follow-through (D77); (5) facial + eyes (D61–D63); (6) silhouette check every frame; (7)
cleanup (29.9). Layering rules: body leads, then extremities, then face — the face is last because it
depends on everything. Never key the face first.  Review cadence: show the stepped blocking to
eyes early; iterate cheap; lock the blocking before splining (splining to a bad pose plan = re-splining).
29.2 GRAPH EDITOR MASTERY (the animator's
instrument)
The three reads: (1) Pose read — the 3D view at any frame; (2) Timing read — the Dope Sheet
(when keys exist); (3)  Spacing read  — the Graph Editor (how values change between keys). A
professional checks all three constantly.
Interpolation types (T menu):  | T ype | Behavior | Use | |---|---|---| | Constant | no interpolation
(hold) | blocking, holds, stepped work | | Linear | straight lines | mechanical, exact rates, cutting keys
| | Bezier | smooth curves | default for organic motion | | Easing presets (Ease In/Out, Back, Bounce,
Elastic…) | styled curves | quick feel; use sparingly, hand-tune | | Auto clamped | bezier without
overshoot | safe default (avoids unwanted dips) |
Handle  types  (V  menu): Auto  (smooth),  Vector  (straight),  Aligned  (both  sides  align),  Free
(independent) — break handles for asymmetry (impacts: fast in, slow out). Editing essentials: box-
select keys; G/R/S slide/scale in time or value; Shift-E ease in/out of selection; Alt-O (Graph Editor →
Key → Clean Channels) removes redundant keys; F-curve modifier Noise (add subtle camera/look
noise — D107/D63);  Cycles (loop walk cycles);  Smooth/Denoise filters  (clean mocap, D20.5).
Motion Paths: (Viewport: Object → Animation → Motion Paths) — visualize arcs and spacing in 3D;
DEPTH CHAPTER 29 — ANIMATION DEPTH: THE PERFORMANCE MASTERCLASS

the #1 arc-checking tool. Spacing how-to: on a position curve, vertical segments = fast (big value
change per frame); horizontal = slow/holds. Slow-in = handle flattens as it enters the key; slow-out =
flattens as it leaves. Even spacing = uniform motion (boring); eased spacing = alive. Keying
discipline: use Keying Sets (custom property sets — body, face, hand) so a single I keys exactly
what you want; Auto-Keying ON during blocking, OFF while inspecting.
29.3 TIMING & SPACING TABLES (frames at 24 fps)
Action duration table: | Action | Frames | Notes | |---|---|---| | Blink | 2–4 | 1 down + 1 up + hold | |
Eye dart | 1–2 | then settle 2–4 | | Head turn (45°) | 6–10 | eyes lead by 2–4 | | Gesture (point/raise) |
8–16 | gesture = prep 2–4 + move 4–8 + settle 4 | | Sit down | 12–24 | anticipation 4–6, descent,
settle | | Stand up | 12–24 | lean-in, rise, settle | | Walk step | 12–16 | per step (slow 18, brisk 10) | |
Run step | 8–10 | flight phase | | Sprint step | 4–6 | full flight | | Jump: anticipation | 4–8 | crouch | |
Jump: air | 8–14 | hang at apex | | Jump: landing settle | 6–12 | absorb, settle | | Punch | 3–5 (strike) |
+ anticipation 4–8, impact hold 2–4, recover 6–12 | | Throw | 8–16 | wind-up, release, follow-through |
| Reaction (surprise) | 2–4 | freeze first! then respond | | Sad turn-away | 12–20 | slow, heavy | | Laugh
| each "ha" 4–8 | rhythm | | Breath | 24–48 | cycle; hold at tension |
Weight class → timing multiplier: feather-light ×0.7 (snappy) · light ×0.85 · medium ×1.0 · heavy
×1.3 · massive ×1.6. Apply to all the above.
Easing table: linear = mechanical/robotic; ease-out = gravity/launch; ease-in = braking/catch; ease-
in-out = organic pendulums; exponential = impacts, power-ups; back = overshoot (cartoon). Every
motion gets an easing decision — defaulting to ease-in-out everywhere is the #1 amateur tell.
29.4 THE 12 PRINCIPLES IN BLENDER PRACTICE
Principle Blender execution Failure to avoid
Squash & Stretch global stretch rig (Ch 19 r7) + per-bone weights; volume
preserved
deforming without volume (squash
that flattens)
Anticipation key: hold → anticipation (counter-move) → action; 2–6
frames
action without wind-up (teleport)
Staging camera (Ch 21) + pose silhouette; one idea per shot competing focal points
Pose-to-pose vs
straight
pose-to-pose for characters (blocking); straight-ahead
for chaos (fx, hair)
straight-ahead for everything (no
control)
Follow-through &
overlap
chain lag: hands trail arms, head trails spine; key the
lead, let parts lag 2–4 frames
everything moving simultaneously
Slow in/out handle flattening (29.2) linear everything
Arcs motion paths check; curve handles in graph straight-line paths
Secondary action cloth/hair sims (D39/D47) + jiggle (28.10) secondary that distracts
Timing 29.3 tables uniform timing
Exaggeration push poses 10–30% past reference (style lever) exaggeration without base
Solid posing line of action, contrapposto, weight leg, silhouette symmetric, dead vertical poses
Appeal character-specific gesture vocabulary; readability generic "pretty" motion
DEPTH CHAPTER 29 — ANIMATION DEPTH: THE PERFORMANCE MASTERCLASS

29.5 FOOTWORK & LOCOMOTION DEPTH
Walk cycle frame map (14-frame step at 24 fps, both steps = 28):  | Frame | Pose | Body state
| |---|---|---| | 0 | Contact | heel strikes, weight starts transfer; opposite arm forward; hips at lowest-ish
| | 4 | Down | weight fully on foot, knee bends, body lowest | | 7 | Passing | support leg straight,
body highest, other leg passes underneath | | 11 | Up/toe-off | push off ball+toe, body lifts, rear leg
starts forward | | 14 | Contact (other) | other heel strikes |
Hip mechanics: lateral shift toward the support leg (~2–5 cm at passing); pelvic tilt (front hip up on
the passing leg's side); slight rotation (hips counter-rotate to shoulders). Head level: in real walks
the head stays level — test by tracking the head in motion paths; if it bobs like a spring, remove the
bounce from the root. Foot roll (with the 28.1 rig):  heel contact (pivot = heel) → flat (foot rocker)
→ ball (pivot = ball) → toe push-off (pivot = toe). The pivot switching is the foot roll — do it per phase,
not once. Run vs walk:  run has flight (both feet off: 2–6 frames); contact is shorter (foot strikes
more under the body); bounce bigger; arms bent higher; torso leans forward. Sprint: more lean, arms
pump, knees drive up.  Stairs/slopes/uneven: stairs = exaggerated knee lift + hip rise per step;
slopes  =  weight  shifts  forward  (up)  or  back  (down),  stride  shortens;  uneven  =  adaptive foot
placement (test in the pose phase, don't fake in spline). Turnarounds: the turn is a 3-beat: (1) head
leads (eyes look first — D63), (2) shoulders/hips follow in sequence, (3) weight transfers through the
new stance. T urning in place = pivot on the ball of one foot.
29.6 ACTING TECHNIQUE FOR ANIMATORS (D75 in
practice)
The question per shot:  what does the character want, what blocks them, what's their emotional
state at each beat? Write it on the shot's notes.  Thought-before-action: every decision has a
micro-beat of thinking (eyes shift, breath, tiny settle) before the action — the difference between a
puppet and a person. 2–6 frames, sometimes just the eyes. Status & power: status shows in height
(high status = tall, expanded), pace (low status = fast/nervous or slow/deferential), eye contact
(dominant  holds  gaze;  submissive  breaks),  personal  space.  Changing  status  mid-scene  =  story.
Subtext: body says one thing, words another (a character saying "I'm fine" while shrinking). The
body is the truth channel — animate the body to the subtext, the mouth to the line (D62). Gesture
vocabulary: each character gets 3–5 signature gestures (the scholar pushes glasses, the thief
checks  pockets).  Design  these  at  D03/D04;  reuse  them  so  the  audience  learns  the  character's
language. Breath: chest/abdomen rise (Ch 19 r6) + the pause at emotional beats; holding breath =
tension; sigh = release. Breath is the cheapest way to make any shot alive. Dialogue acting: listen-
then-speak (the listener reacts 2–6 frames before answering); emphasize  keywords (body/head hit
the important words); the voice leads, the body supports — don't punch every syllable.  Eyes &
micro-motion: D63 in performance: eye darts precede head turns; blinks land on emphasis; the
eyes deliver the truth while the mouth delivers the line.
29.7 CAMERA-RELATIVE ANIMATION & SCREEN
PERFORMANCE
Screen space vs world: a walk that reads in world space can fail in frame — check framing
(headroom, lookroom, D104) and screen direction (D103) as you block.
Parallax & layering: animate the body so the camera sees depth (a turn shows the profile
passing through frame); avoid "stuck to the background" flatness.
• 
• 
DEPTH CHAPTER 29 — ANIMATION DEPTH: THE PERFORMANCE MASTERCLASS

Eyelines: characters look toward the camera's subject (D103 eyeline match); in close-ups the
eyes track the other character's position in screen space, not the world.
The "camera test": render a low-res playblast through the shot camera — if the story reads at
50% scale on a phone, it reads everywhere.
29.8 NLA, ACTIONS & RE-USE (production speed)
Actions: each motion lives in an Action (the Action Editor); a walk cycle is a looped Action (D66).
Push Down to NLA: convert an Action to an NLA strip; then blend strips (walk + wave = wave
while walking) via the NLA track mixer — the "motion layering" system.
Action constraints: a rig bone can play an Action on a control (pose libraries — D64); the Pose
Library (Asset Browser) stores poses/expressions as reusable assets (D84).
Motion library discipline: name actions CHAR_Action_Description  (D123); version them; a good
library is the studio's accumulated vocabulary.
Non-destructive: NLA strips keep the original actions editable — tweak the cycle once, all uses
update (but re-bake sims, D88).
29.9 POLISH & CLEANUP (the professional bar)
Jitter/pops: select all curves, look for spikes (single-frame deviations) — fix with handle
smoothing or key cleanup.
Foot/contact slide: play at 12.5% — any slide = fix contacts first (D66).
Arcs: motion paths on wrists/ankles/head — flatten or wobble = curve fix.
Overlap: check hands/head/cloth lag 2–4 frames behind their leads.
Silhouette check: every frame should read the pose — pause at random frames, blur eyes, re-
check.
Weight: does the body respond to its own mass (D76)? A 500 kg character can't hop.
Facial pass: eyes, brows, mouth complete (D61–D63) — last, always.
Frame-accurate to the edit: the shot's beats land on the animatic's sync frames (D120).
• 
• 
• 
• 
• 
• 
• 
1. 
2. 
3. 
4. 
5. 
6. 
7. 
8. 
DEPTH CHAPTER 29 — ANIMATION DEPTH: THE PERFORMANCE MASTERCLASS

29.10 ANIMATION FAILURE MODES & FIXES
Symptom Cause Fix
Motion feels floaty no contact, even spacing plant feet/hands; add easing + holds
Motion feels robotic everything eases the same; no
overlap
vary easing; add 2–4 frame lags
Character "teleports" between
poses
no anticipation/transition add wind-ups and breakdowns
Feet slide contacts broken fix contact keys first (D66)
Jitter/shake spiky curves smooth handles, clean channels
Arms feel like noodles no structure/weight pose with line of action + weight logic
Expressionless face face keyed first or last wrongly / no
eyes
face last; eyes lead everything (D63)
Secondary motion chaos too many elements moving pick 2–3 elements (D77)
Everything is mid-motion no holds/stillness stillness is emphasis — hold 4–12
frames
Polish took forever no gates lock blocking; timebox passes (D127)
DEPTH CHAPTER 29 — ANIMATION DEPTH: THE PERFORMANCE MASTERCLASS
