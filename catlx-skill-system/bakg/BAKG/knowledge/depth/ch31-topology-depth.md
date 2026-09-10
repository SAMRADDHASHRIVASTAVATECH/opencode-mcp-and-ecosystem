# Depth Chapter 31 — Topology & Retopology Depth: The Deformation Atlas

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 195–198 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 31 — TOPOLOGY &
RETOPOLOGY DEPTH: THE DEFORMATION
ATLAS
Expands D23, D24. The exhaustive loop-pattern catalog — every joint and facial region, its topology
pattern, vertex counts, and pole placement — plus retopology tooling, density budgets, mesh health,
and deformation testing.
31.1 THE DEFORMATION ATLAS (joint-by-joint loop
patterns)
Region Pattern Vertex/loop
guidance Why
Elbow 3–5 concentric loops around the joint; pole
on the outside of the bend
~16–24 verts per
ring
bends fold cleanly; the outer
pole redirects the fold
Knee 3–5 rings; kneecap gets its own loop arc;
hamstring bulge zone behind
rings follow the
patella arc
cap tracks; back folds
Shoulder loop over the deltoid cap; 5-pole at the
armpit
armpit pole high,
hidden
arm swings without tearing the
chest
Hip/groin loop around the leg socket; fold line across
the groin; 5-pole at the hip crease
fold line = 1 clear
loop row
sitting/standing folds land on
the line
Wrist 3 transition rings between forearm and
hand
rings match the
wrist crease
bend without "popeye" bulges
Ankle 2–3 rings; Achilles line rings match the
ankle crease
foot roll (28.1) needs clean
rings
Fingers 3–4 segments per finger (MCP/PIP/DIP);
knuckle loops
~8–12 verts per ring knuckle bulge via the loop +
corrective
T oes same as fingers, simpler 3 segments typical foot push-off
Spine/torso 10–14 vertical loops (ribcage → pelvis); belly
crease row
even spacing for
flexion
bends forward/back/side
cleanly
Neck horizontal loops; separate jaw loop ~16 verts per ring tilt without "cable"
compression
Armpit/
underside
pole + fan 1 hidden pole the classic problem zone
T ail/tentacle even loop distribution, no sudden
compression
rings every ~2–4
verts of length
undulation (D16.11)
Wing fold fan rows along the fold line (D45) per-feather-row
loops
fold like a fan (28.7)
DEPTH CHAPTER 31 — TOPOLOGY & RETOPOLOGY DEPTH: THE DEFORMATION ATLAS

31.2 THE FACIAL TOPOLOGY ATLAS (the crown jewel)
Region Pattern Vertices Behavior
Eye full ring around the eye 16–24 blink deforms the ring (D63)
Eye → cheek
fan
loops radiate from the ring down the
cheek
— smile pulls the cheek fan
Mouth full ring around the mouth 24+ (up to 40 for
detail)
all phonemes (D62)
Mouth corner pole where upper/lower lip loops meet 1 pole per corner the corner "hinges" for smiles/
frowns
Brow horizontal loops over the brow 2–3 rows raise/furrow
Nose loops wrap the nose bridge; alar rings — nostrils flare
Cheek diagonal loops following the smile
muscle
— the smile path (zygomatic)
Jaw loop along the jawline separating face/
neck
1 clear row jaw opens without pulling the
neck
Forehead horizontal loops; 5-pole hidden at the
hairline
— wrinkles
Ears separate loop spiral (or separate mesh) — detail heavy; often retopo'd
separately
Rules recap: quads everywhere on deformable areas; poles in low-deformation, low-visibility zones
(behind the ear, at the hairline, under the armpit); even spacing along flex zones; density follows
need (face/hands dense, torso/back sparse).
31.3 POLE PLACEMENT & TRANSITION PATTERNS
5-pole redirects a loop stream (turns the flow 90°) — place at armpit, hip crease, mouth corner.
3-pole terminates a loop stream (converges) — place at the back of the knee, elbow outside,
hairline.
Loop reduction patterns: a 4-loop stream → 2-loop stream via a 5-pole + 3-pole pair (the
standard "reduce" pattern); a 2-loop stream → 1 via a single 3-pole. Never reduce loops across a
flex zone.
The golden check: after any transition, subdivide-preview (subdiv modifier) — pinching =
transition placed wrong; move it off the flex zone.
• 
• 
• 
• 
DEPTH CHAPTER 31 — TOPOLOGY & RETOPOLOGY DEPTH: THE DEFORMATION ATLAS

31.4 DENSITY BUDGET TABLE (polygons by region and
target)
Asset Film hero (tri) Realtime (tri) Notes
Face region 20k–50k 3k–8k the detail budget lives here
Hand (per hand) 10k–20k 1.5k–3k acting shots show hands
Full body 50k–150k (pre-subdiv) 8k–30k subdiv ×4 for render
Hair strands n/a (curves) cards/low-poly see Ch 33
Clothing (sim) 10k–50k 2k–6k sim cost scales with verts (D34)
Prop 1k–10k 200–2k budget by screen time
Environment hero 100k–1M+ 20k–100k LODs (Ch 26)
Background silhouettes/impostors 100–2k never full detail
31.5 RETOPOLOGY TOOLING
Tool How Best for Notes
Poly Build (Edit Mode) click-drag quads with
snapping
the workhorse — fastest
manual retopo
snap to face + Shrinkwrap
Shrinkwrap modifier surface-conform a
rough cage
quick clean cages use with snapping off
B-Surface / Grease Pencil
retopo
draw loops with GP,
convert to mesh
stylized/curved
topologies
advanced
Auto remesh (Instant
Meshes / Quad Remesher)
algorithm quad
remesh
fast clean-ish results retopo by hand for heroes;
auto for background
RetopoFlow (external) guided retopo toolset professional speed paid/community
Decimate reduce existing mesh LOD/quick drafts not a topology solution
The workflow: snap (Face, ~0.01 offset) → Poly Build from the biggest forms (torso → limbs → face)
→ follow the atlas (31.1/31.2) → mirror half → weld center → subdiv-preview → bend test (31.9).
31.6 RETOPOLOGY WORKFLOW (step-by-step)
Prep: decimate the sculpt to a reference density (0.3–0.5 ratio) — keep the original for baking.
Plan on paper: draw the loop paths (from the atlas) before drawing vertices.
Build the cage: rough low-poly with correct proportions (this is the shape pass).
Add loop structure: the joint/facial loops from the atlas (this is the deformation pass).
Subdiv preview (view 2 levels): fix pinches and poles.
Mirror + weld: finalize one half, mirror, merge by distance.
Bend test (31.9) — with a quick armature or in edit mode.
UV later (D32) — retopo and UV plans are linked; keep seams in mind during retopo.
1. 
2. 
3. 
4. 
5. 
6. 
7. 
8. 
DEPTH CHAPTER 31 — TOPOLOGY & RETOPOLOGY DEPTH: THE DEFORMATION ATLAS

31.7 DECIMATION & LOD (production detail)
Decimate modifier: Collapse ratio (0.2–0.5 typical), or Planar (for hard surfaces). Use for LOD1/
LOD2 and drafts — never for final heroes.
LOD construction (Ch 26.2): LOD0 = hero mesh; LOD1 = decimated 50%; LOD2 = decimated
20% (silhouette preserved); LOD3 = impostor/billboard. Build LODs by hand for heroes (auto-
decimate then clean).
Silhouette-first rule: far LODs must keep the silhouette and lose only interior detail.
31.8 MESH HEALTH CHECKS (run before rigging)
Non-manifold: Select → All by Trait → Non-Manifold — fix every hit (D24).
Zero-area faces / degenerate: Mesh Analysis overlay (area) — remove.
Normals: Shift-N recalculate; check flipped (Face orientation overlay — blue front/red back).
Interior faces: Select interior faces (Select → All by Trait → Interior Faces) — delete.
Overlapping verts: Merge by Distance (Alt-M) after mirroring.
Consistent scale: Ctrl-A apply transforms; check against the scale master (D14).
31.9 DEFORMATION TESTING (the rig-readiness gate)
Quick bind: add a rough armature (or use your planned skeleton, D49) → automatic weights.
Pose the extremes: elbow 140°, knee 130°, arm overhead, sit, crouch, twist, reach behind.
Watch the silhouette at each extreme: pinch = bad loop placement; tear = missing loops;
bulge = pole in the fold.
Fix in topology, not weights (D24 rule): adjust loops/poles, re-test.
Dynamic test: scrubbing the pose back-and-forth — popping = corrective needed later (D59),
but topology should be clean first.
31.10 TOPOLOGY FAILURE MODES & FIXES
Symptom Cause Fix
Pinching under subdiv pole/loop in high-curvature zone move pole, re-route loops (31.3)
Crumple at joint no joint loops add 3–5 rings (31.1)
Face won't emote facial loops missing (no eye ring / mouth ring) rebuild face to atlas (31.2)
Mesh "shatters" on bend triangles/ngons in flex zone retopo quads
Seams visible later retopo ignored UV plan plan seams at retopo (D32)
Weight fixes don't help bad topology fix topology first (always)
• 
• 
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
DEPTH CHAPTER 31 — TOPOLOGY & RETOPOLOGY DEPTH: THE DEFORMATION ATLAS
