# Part 2D — Depth Supplements S-01…S-18

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 41–47 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

PART 2D — DEPTH SUPPLEMENTS (base-only
domains, S-01…S-18)
The  18  domains  that  are  covered  at  base-chapter  depth  get  their  practical  depth  here.  Each
supplement is a compact node card: parameters, workflows, mistakes, fixes — the same depth
standard as the full chapters, sized to the domain.
S-01 — CHARACTER CONCEPT DEPTH (D03)
DEF: The personality/role/ability contract that drives design, rig, and acting.  The concept sheet
(fields): role in story · 3–5 personality adjectives · temperament (calm/volatile) · energy level (1–10)
· physical capability (strength/speed/agility scores) · movement style (fluid/mechanical/predatory/
weightless) · age · social status · flaw · secret · signature gesture (Ch 29.6). Personality → physical
translation table: | Personality | Posture | T empo | Gesture | Design cue | |---|---|---|---|---| | Confident
| open, tall, expanded | slow-medium | decisive | wide stance, strong silhouette | | Anxious | closed,
shoulders up | fast, twitchy | fidgety | small, tight shapes | | Lazy | slouched, low COM | very slow |
minimal | soft, round shapes | | Stern | rigid, upright | measured | clipped | angular, vertical | | Playful
| springy, off-balance | fast, bouncy | large | round, bouncy forms | | Old | bent, careful | slow,
deliberate | careful | worn, textured design | | Predatory | low, coiled, level head | still→explosive |
minimal, focused | sharp, low silhouette | | Regal | tall, still, chin up | ceremonial | measured, raised |
vertical, symmetrical |
MIST: designing the body before the personality (pretty but lifeless); contradictory cues (child's face
+ brutal posture); no movement style (animators guess). FIX: answer the sheet before any drawing;
the design (D04), rig (D48), and acting (D75) all read the same sheet. EDGES: → D03 → D04/D05 →
D48 → D75 (the personality must survive the whole pipeline).
S-02 — REFERENCE DEVELOPMENT DEPTH (D07)
DEF: Curated external reference (photo/video/anatomy/material/gait) that protects the design from
memory errors. The board structure per asset: (1) Anatomy/structure (bones, muscles, proportion
grids); (2) Surface & material (macro + micro — the texture story); (3) Lighting conditions (how the
surface looks in key/side/back light); (4) Motion (video loops of gaits, gestures — D12); (5) T echnical/
historical (props, armor, era); (6) Style (other art — what feel you're matching). Curation rules: 10–
50 images per board; label sources; motion reference as video (loops, 3 angles); mark the 2–3 hero
references per asset (the ones that define it) — the rest are context.  The study ritual:  before
modeling/animating, redraw from memory, compare to the board, correct. Memory errors are the #1
realism killer; the ritual fixes them.  Tools: PureRef (free, external) or Blender image planes in a
reference scene; video planes (movie texture) in the viewport for motion ref. MIST: one tiny photo for
a whole creature; no motion ref for movement-heavy shots; boards without labels (lost context);
reference that contradicts the world bible (D02).  FIX: keep boards per asset in the project docs
(D123); update when the design changes (the board is the design's evidence).
PART 2D — DEPTH SUPPLEMENTS (base-only domains, S-01…S-18)

S-03 — CHARACTER SHEETS DEPTH (D08)
DEF: The formal 2D spec that is the contract between design and every 3D discipline. The sheet set
(minimum): turnaround (front/side/back/3-quarter, same height line) · proportion sheet (head-unit
grid + key measurements) · expression sheet (6–12 states) · detail sheets (hands, feet, face features)
· scale sheet (vs. environment + other characters) · color/texture callouts (swatches + material
notes). Turnaround technique: lock the height line and proportions across all views; draw front +
side first (from the design's core silhouette), then back and 3/4 by projection; the views must agree
(the side's nose depth matches the front's nose width).  Blender usage:  import as background
images (front/side views) with matching scale (D14); use the scale sheet to calibrate the blockout
(D16); animators use the expression + proportion sheets for posing (D64). MIST: front-only sheets
(profile  invented  in  3D  →  rework);  expression  sheet  at  different  proportions;  no  scale  sheet
(characters wander in size); no material callouts (modelers guess).  FIX: treat the sheet as a legal
document — model/rig/animation sign off against it (D127).
S-04 — PREVISUALIZATION DEPTH (D11)
DEF: Rough 3D staging that verifies the spatial story before modeling investment. The previs kit:
per shot — a camera with the planned lens (D102); stand-in blocks for characters (scaled to the
sheets, D16); primitive masses for sets; Grease Pencil camera paths (draw the move on a plane —
D107); the animatic's audio for timing (D10). The previs questions (answer all):  can the camera
see the action? Do the characters fit the sets? Do the sets fit the shots? Do the lenses (D105)
produce the intended framing? Does the blocking (D64) time out to the animatic? Workflow: place
cameras from boards → block stand-ins → rough key poses → animate camera moves → render
Workbench/EEVEE captures → cut in VSE → review → iterate.  Previs is cheap chaos; final is
expensive order — find the chaos here. MIST: previs at final quality (waste); previs without the
animatic's timing (drift); no camera in previs (fights appear in production). FIX: keep stand-ins at 2–
20 primitive faces; lock the previs before blockout (D16) — it is the blockout's parent.
S-05 — MOTION REFERENCE DEPTH (D12)
DEF: Filmed/video reference of the exact motions needed — the animator's ground truth. Shooting
setup: phone/tripod, 3 angles (front/side/3/4 — matching the shot's camera, D106); 60 fps+ for slow-
mo study; film the whole action plus variations; for creatures, gather animal footage (D68); for acting,
film yourself multiple takes of the emotional beat.  Use in Blender:  video planes in the viewport
(movie texture on a plane, or the "Background/Image as plane" trick) beside the character; scrub
frame-by-frame; exaggerate 10–30% from reference  (reference is physics, animation is performance
— D65). The reference→animation bridge: identify the key poses in the footage (contact, passing,
anticipation) → block them (D64) → then deviate stylistically. Never copy frames; translate  logic
(weight, timing, force) into your character's anatomy (D69). MIST: one low-quality clip for a nuanced
performance; animating from imagination for complex actions (gait errors guaranteed); reference
that fights the character's design (a 2 m beast moving like a rabbit). FIX: reference library per action
type (walk, run, fight, sit, lift) in the project docs (D123) — the animator's palette.
PART 2D — DEPTH SUPPLEMENTS (base-only domains, S-01…S-18)

S-06 — BLENDER FUNDAMENTALS DEPTH (D13)
DEF: The  load-bearing  skills  every  advanced  system  builds  on.  The  core-20  skills  checklist
(master  these  before  anything  else): 1.  Navigation  (orbit/pan/zoom/views)  2.  Selection  &
transforms (G/R/S + axes) 3. Object vs Edit mode 4. The data model (objects vs data blocks) 5.
Origins & transforms (apply!) 6. Modifiers (the stack) 7. Materials & the Shader Editor basics 8. UV
basics 9. Keyframes & the timeline 10. The Outliner & collections 11. Snapping & proportional editing
12. Normals (recalculate!) 13. The 3D cursor 14. Scenes & view layers 15. Rendering basics (F12,
output  settings)  16.  The  Properties  panels  map  17.  The  search  menu  (F3)  18.  Save/versioning
discipline (D124) 19. Undo & autosave recovery 20. The workspace system (customize your own).
Beginner blockers (fix these first):  objects moving "wrong" (origin misplaced — Set Origin +
Apply); parts disappearing (collections visibility/hide); textures black (missing paths); transforms not
applying (Ctrl-A); viewport too slow (D126). Learning path: 20 skills → one small project (a cube → a
prop → a character) → the graph's Part 1 journey with one small shot. Do not skip to advanced
systems with weak fundamentals — every advanced failure traces back to one of the 20.
PROD: set up your own startup file (workspaces, shortcuts, GPU settings — Preferences → Save
Preferences) — it's a production asset (D13).
S-07 — SCENE ORGANIZATION DEPTH (D15)
DEF: The  naming/grouping/structure  rules  that  keep  a  production  navigable.  The  collection
taxonomy (adopt): Assets/Characters/<name>  · Assets/Props/<set>  · Assets/Sets/<location>  · Rigs  ·
Lights  · Cameras  · Fx  · Scratch  · Shots/<shot>  · Reference . Nested collections allowed; color-tag by
category. The naming legend (write it down, enforce it): TYPE_Name_Detail_V##  — CHR_Hero_v03 , 
SET_City_Street ,  LT_Key ,  CAM_S01_012 ,  FX_Rain ,  PRP_Lantern_01 .  No  spaces;  _  or  - ;  lowercase;
version suffix (D124).  Scenes & view layers:  one scene per shot (linked assets — D122) or a
master + shot scenes; view layers for foreground/background separation (render control, D115).
Discipline rules:  link shared assets (never duplicate — D122); clean orphans (File → Clean Up);
audit missing files before render (D123); the Outliner's search/filter is your friend. MIST: one giant
"Collection" (chaos); renaming linked files (breaks links — D122); every shot a full copy of the world
(viewport death).  FIX: enforce the legend at every handoff gate (D127); document it in  00_docs
(D123).
S-08 — BLOCKOUT DEPTH (D16)
DEF: Proxy geometry at final scale for the whole scene — the  contract for modeling.  Stand-in
technique: primitives for volumes; blockmen (head cube + torso + limbs at sheet proportions —
D08) for characters; box masses for sets; the scale master cube (1 m, D14) always present.  The
blockout checklist: (1) world scale correct (door heights, stairs, creature clearances — D16); (2)
every shot's camera framing works (previs, D11); (3) proportions read against the sheets; (4) staging
supports the story beats (D104); (5) the blockout  approval gate  is signed (D127).  Blockout →
modeling handoff: the approved blockout becomes the modeling reference (D19/D20); characters
get  re-blocked  as  detailed  proxies  at  rig-test  time  (D48).  MIST: detailing  the  blockout  (waste);
skipping scale checks (the classic "can't fit through the door"); approving before cameras are set.
FIX: keep blockouts ugly and fast; the gate is the point — re-stage cheap now, never expensive later.
PART 2D — DEPTH SUPPLEMENTS (base-only domains, S-01…S-18)

S-09 — HARD-SURFACE MODELING DEPTH (D18)
DEF: Mechanical/angular forms with bevel logic, precise dimensions, and thickness.  The modifier
stack (order matters):  Mirror  →  Bevel  (weight  or  angle)  →  Solidify  (thickness)  →  Subdivision
(optional; usually off for hard surface — bevels replace it) → Shrinkwrap (conform to hulls). Test after
each modifier. Bevel logic: hard edges need bevels (0.5–2 mm for props, larger for stylized); bevel
weights (Ctrl-E → Bevel Weight) for selective sharpness; angle-based bevels (the modifier's "Angle"
limit) automate sharp-vs-soft. Boolean discipline: booleans (modifier or GN) create n-gons/artifacts
— always clean up (merge by distance, re-topo the cut region, fix normals); prefer exact solver for
CAD-like precision;  plan booleans  (cut after bevel, before solidify).  Normals & shading:  hard
surface =  flat shading + auto smooth  (or beveled edges with smooth); check Face Orientation
overlay (blue front/red back) before textures. Greebles & detail: GN instancing for repeated panels/
pipes/vents (D85); detail budget by silhouette (D04 — greebles read as noise beyond mid-shot).
Thickness rule: every wall needs thickness (Solidify) — paper-thin surfaces catch light wrong and
break booleans. MIST: booleans without cleanup; bevel after subdiv; no thickness; uniform detail (no
focal hierarchy). FIX: keep a modifier-stack template (start file) for mechanical assets; test the mesh
in the render engine early (D113).
S-10 — PROPS DEPTH (D42)
DEF: Held/handled objects: the most-rigged simple objects in a production.  Prop classes:  held
(weapons, tools, cups — need hand-attach) · set (furniture, fixtures — static but dressed) · interactive
(doors, levers, books — need motion) · simulated (flags, chains, cloth props — D39/D89). The hand-
attach system: each prop gets a handle (empty/bone at the grip); hands snap to it via constraints
(Child Of — D53) or the prop parents to the hand bone; the "grab" switch (28.11 space switching)
transfers the prop between world and hand mid-shot. Scale discipline (D16):  props are designed
against the character's  hand/foot (a 6-legged creature's cup is a bucket — D05); check with the
blockman.  Reuse (D84):  build props as library assets (handle + materials + LOD); a good prop
library is the fastest way to dress sets (D83).  MIST: props merged into the character mesh (can't
swap); no handle (hands float); props at wrong scale; props without LOD (background soup). FIX: the
prop pipeline = model → handle → material → asset catalog (D122) → dress (D83).
S-11 — PHYSICS INFRASTRUCTURE DEPTH (D88)
DEF: The shared sim infrastructure: gravity, force fields, collision, caching, scale.  The force-field
catalog (the invisible hands): | Field | Behavior | Use | |---|---|---| | Force | linear push | gusts, jets,
magic propulsion | | Wind | directional, gusty (noise) | cloth/hair/vegetation (D99) | | T urbulence |
chaotic | smoke, dust, leaves, magic | | Vortex | swirling | tornadoes, portals, drains | | Magnetic |
attract/repel | metal debris, magnetic creatures (4.3!) | | Harmonic | oscillating | jiggle, waves | |
Charge/Curve guide | follow a curve | particle streams, portals |
Collision setup: cloth/hair/soft need a Collision modifier on colliders (or the "Collision" collection);
rigid bodies need rigid-body participants; collision proxies (low-poly stand-ins) are the standard for
performance (D88).  Caching (the discipline):  every sim bakes to a cache (memory or disk in
cache/ , D123); bake to disk for production  (replay stability + speed + versioning, D124); name
caches per shot+version. Scale is physics:  gravity assumes meters (D14) — a 1-unit=1-cm scene
simulates 100× wrong; always check scene scale before simming.  MIST: no colliders (objects fall
through); scale wrong (sims explode); never baking (sims change between sessions); force fields at
PART 2D — DEPTH SUPPLEMENTS (base-only domains, S-01…S-18)

absurd strengths. FIX: the sim checklist: scale → gravity → colliders → force fields → quality → bake →
verify (D127).
S-12 — SOFT BODIES DEPTH (D90)
DEF: Deformable-object physics: jelly, flesh, balloons, "organic" solids.  The key control — the
goal: a goal vertex group sets how strongly each vertex returns to rest (1.0 = rigid, 0 = free). Soft
body = goal + stiffness + damping + (optional) pressure.  Settings map:  Goal weight (0.3–0.9
typical for jelly; 0 for pure free) · Stiffness (edge/face stiffness — how solid) · Damping (settle speed) ·
Plasticity (permanent deformation — clay, dough) · Pressure (balloon/inflatable) · Collision (soft-body
collision settings; edge collision for thin meshes).  Use cases:  creature belly jiggle (subtle!), jelly/
gelatinous monsters (D100), balloons, soft props, secondary motion (D77) —  never use soft body
where cloth (D91) or a weighted rig (D57) is the right tool. MIST: full-res meshes (slow — use a low-
poly + subdiv after); no goal (mesh collapses); soft body for fabric (use cloth).  FIX: low-poly sim
mesh + subdiv display; bake (D88); add a small goal for stability.
S-13 — RENDERING SETTINGS CHEAT SHEET (D112)
The render settings quick-reference (Cycles/EEVEE):  | Setting | Cycles value | EEVEE value |
Note | |---|---|---|---| | Samples | 32–128 (+denoise) | n/a (real-time) | adaptive sampling ON | | Denoise
| ON (OIDN/OptiX) | n/a | the #1 speed/quality lever (D114) | | Light bounces | 4–8 total; limit
transmission/volume | n/a | glass-heavy scenes: cap transmission | | Caustics | OFF unless needed | n/
a | expensive | | Motion blur | ON (2–8% shutter) | ON | sells motion (D112) | | DoF | render OR comp
(D117) | render (fast) | comp is cheaper for big scenes | | Color management | AgX, exposure per
scene | AgX | the modern standard (D112) | | Output | EXR multilayer (frames) | EXR/PNG | never
final-to-compressed-video (D128) | | Resolution | final 100% / WIP 25–50% | same | — | | GPU | enable
in Preferences | — | the single biggest speed factor | The iterate loop: WIP at 25–50% + denoise +
low samples → approve → final at 100% + full quality → QC (D127). Never iterate at final settings.
S-14 — SHOT MANAGEMENT DEPTH (D121)
DEF: The  shot-tracking  state  machine  that  keeps  a  film  from  losing  shots.  The  shot  record
(spreadsheet): shot  ID  (naming  legend,  D123)  ·  status  ·  owner  ·  notes  ·  version  (D124)  ·
dependencies (assets/sims) · deadline · render order.  Status ladder:  planned → blocked (D64) →
splined → animated → sim'd → lit → rendered → comped → approved. Each status change = a review
point (D127). The render queue:  render in dependency order (comp needs renders; shots sharing
assets batch together); render EXR per frame (crash-safe, D112); monitor failures; re-render only
failed frames. MIST: no status system ("almost done" forever); shot names that collide; rendering out
of order; no owner (nobody accountable). FIX: one spreadsheet, updated at every gate (D127); the
shot list from the animatic (D10) is the master.
S-15 — QUALITY CONTROL DEPTH (D127)
DEF: Scheduled looking — technical + creative review at every gate, and the final full-film check.
The technical checklist (per asset/shot):  non-manifold (D31.8) · missing textures/paths (D123) ·
PART 2D — DEPTH SUPPLEMENTS (base-only domains, S-01…S-18)

scale vs. master (D16) · weights/rig sign-off (Ch 6) · sim caches baked (D88) · render errors (black
frames, noise, z-fighting, missing passes) · audio sync (Ch 23) · color consistency (D119).  The
creative review method:  per gate, 3 questions — (1) does it serve the beat? (2) does it read at
small size / from the shot camera? (3) does it match the world bible & style rules (D138)? Notes: shot
+ issue + owner + due .  The final QC watch:  watch the whole film at final quality, in order, with
sound: continuity (D103), color matching (D119), audio sync, frame errors, emotional flow.  Never
ship with known errors. MIST: no gates; no notes; "fix in comp" (rarely true); skipping the final
watch. FIX: gates are scheduled (D125); the checklists live in A.4 — run them, don't improvise.
S-16 — ARCHIVING DEPTH (D129)
DEF: Preserving the project so it can be re-opened, re-cut, re-rendered, or learned from. The archive
contents  (checklist): (1)  final  masters  (D128);  (2)  final  project  files  (.blend  final  versions  +
versions.md, D124); (3) all sources (textures, HDRI, audio, reference, concept, sheets — D123); (4)
sim caches  if re-render planned (else settings only); (5) the decision record (world bible, shot list,
naming legend, pipeline notes); (6) the add-on manifest (which add-ons/versions — so it reopens
on a new machine); (7) README index. Format & verification: one folder (or zip/tar) with README;
store on 2+ media (drive + cloud); write a checksum manifest (hash each file — verify at archive
time and before any restore); date it; keep backups (D124).  MIST: archiving only the video (can't
revisit); no README (future-you can't navigate); one copy only; no add-on manifest (reopen fails).
FIX: archive at project milestones (D125), not just at the end; the archive is the final version of D124.
S-17 — MATCH MOVING DEPTH (D132)
DEF: Camera tracking: extracting a 3D camera from real footage so CG integrates into live-action.
The workflow (Blender's Motion Tracking):  (1) import footage (Clip editor); (2) detect/solve —
auto-track features (or manual markers), solve the camera (Camera Solve panel: keyframes, refine,
focal length from metadata); (3) check the solve error (reprojection error < 0.5 px is good; > 1.5 px
= re-track); (4) set scene scale & ground plane (place 3D markers on real-world measurements —
the floor, a door — to fix scale/orientation, D14); (5) test with a stand-in  (a cube on the ground
must not slide); (6) build/render CG against the solved camera; (7) integrate with matching lens
(D105) + lighting (D108) + grain/grades (D119). Tricks: track high-contrast static features; lock the
ground plane early; use lens distortion data (Solver → Distortion) for wide lenses; add motion blur +
grain to CG to match the footage (D112/D119). MIST: ignoring solve error (wobbly CG); no ground
plane (floating); lens mismatch; CG too clean (no grain/mb).  FIX: track in passes (background →
foreground); refine with more keyframes; the test-cube rule before any real CG.
S-18 — ADD-ONS & ASSET LIBRARIES DEPTH (D134)
The  honest  catalog  (what  genuinely  earns  its  keep): |  Category  |  Add-on/tool  |  What  it
accelerates | |---|---|---| | Modeling | HardOps/BoxCutter (paid) | hard-surface (D18) | | Sculpting |
(tablet + custom brushes) | D22 | | Retopology | RetopoFlow / Quad Remesher (paid) | D23/D31 | |
Rigging | Rigify (built-in), Auto-Rig Pro (paid) | D48/D20 | | Hair/fur | (GP/curves built-in) | D43–D46 | |
T errain | ANT Landscape (built-in), Gaea (external) | D80 | | Trees | Sapling (built-in) | D82 | |
Destruction | Cell Fracture (built-in) | D97 | | Mocap | Rokoko/Move.ai (external) | D131 | | Concepts |
ComfyUI/A1111  (external)  |  D06/D39  |  |  Reference  |  PureRef  (external,  free)  |  D07  |  |  Assets  |
BlenderKit, Poly Haven (free) | D84 | | Color/edit | DaVinci Resolve (free) | D119/D128 | | Farm |
PART 2D — DEPTH SUPPLEMENTS (base-only domains, S-01…S-18)

Flamenco (Blender's own) | D136 | Rules: (1) learn the system first, add the speed tool second (the
graph is the system); (2)  document the manifest  (D129 — a project must reopen); (3) built-in >
add-on where capability is equal (fewer moving parts); (4) license-check every external asset (D129).
MIST: add-on soup (dependencies break, performance dies); buying speed before skill; unlicensed
assets (legal risk).
PART 2D — DEPTH SUPPLEMENTS (base-only domains, S-01…S-18)
