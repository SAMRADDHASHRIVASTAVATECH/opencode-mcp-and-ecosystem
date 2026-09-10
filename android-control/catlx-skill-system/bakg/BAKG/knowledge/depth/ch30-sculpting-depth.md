# Depth Chapter 30 — Sculpting Depth: Brushes, Workflows & Detail Transfer

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 191–194 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 30 — SCULPTING DEPTH:
BRUSHES, WORKFLOWS & DETAIL TRANSFER
Expands  D22.  The  complete  sculpting  craft:  the  brush  encyclopedia,  brush-settings  mastery,
topology-strategy decisions (dyntopo vs voxel vs multires), the three-form workflow, alphas, masks,
and how detail becomes a renderable asset.
30.1 THE BRUSH ENCYCLOPEDIA (Blender Sculpt Mode)
Brush What it does Key settings Best for
Draw pushes geometry along
normal
strength 0.3–0.6,
falloff
general blocking, primary masses
Clay Strips adds flat strips of clay large size, low
strength
building volumes (the #1 form brush)
Clay adds soft clay strength 0.3 secondary forms, flesh
Crease digs a sharp groove strength 0.5–0.8,
rake
wrinkles, lips, brows, armor seams
Inflate pushes outward (volume) low strength fat pads, lips, nostrils
Blob adds rounded lumps small blobby/creature textures, noses
Smooth averages the surface strength 0.5 cleanup, after every pass
Flatten flattens a region strength 0.5 bone landmarks, flat planes
Pinch pulls toward the cursor small radius sharp creases, detail definition
Grab drags a region (whole
surface)
large moving masses, blockout, posing
Elastic Deform stretches a region like rubber large organic reshaping, "silly putty" form
edits
Snake Hook pulls spikes/tendrils out small hair spikes, tendrils, claws
Cloth simulates cloth folds strength 0.3–0.6 fabric folds, sagging skin
Pose poses a region (rotate/
translate)
— blocking poses, limb rotation in sculpt
Mask paints a mask (protected
region)
— isolating work zones
Multires
displacement
stamps detail from a texture — scale detail, pores, leather
Anchored/Stamp places a texture stamp once texture + scale alphas: scales, pores, bark
Fill/Deepen raises/lowers to a level — uniform panels, armor plates
30.2 BRUSH-SETTINGS MASTERY (the difference between
"sculpting" and "smearing")
Falloff curve (radius profile): the shape of the brush's influence. Smooth curve = soft forms;
sharp curve = defined edges. Adjust per brush: forms want smooth falloff, details want sharp.
• 
DEPTH CHAPTER 30 — SCULPTING DEPTH: BRUSHES, WORKFLOWS & DETAIL TRANSFER

Strength & radius: F = radius, Shift-F = strength. Rule: big radius + low strength for forms;
small radius + high strength for detail. Most beginners sculpt too strong — halve your strength.
Brush texture: a texture modulates the stroke (paper, speckle) — the texture makes skin/pores/
scales. Set per brush (e.g., Crease with a soft speckle = organic wrinkles).
Stroke method: Drag (anchored stamp), Airbrush (continuous), Anchored (press once), Line/
Curve (drawn strokes). Airbrush for smooth continuous work; Anchored for stamps.
Auto-masking (the pro feature): T opology (protect mesh boundary), Face Sets (protect other
sets), Cavity (protect high-frequency detail — sculpt in cavities without destroying detail), Angle,
Front Faces. Cavity masking is the #1 way to add detail over existing detail.
Symmetry & mirror: sculpt with X-symmetry for the base; turn it off for the final pass —
organic life is asymmetric (D22).
Persistent: accumulates the stroke's effect (for building consistent layers).
Accumulate: stroke strength accumulates with repeats (airbrush building).
30.3 TOPOLOGY STRATEGY — DYNTOPO vs VOXEL vs
MULTIRES
Method What it is Strengths Weaknesses Use when
Dyntopo dynamic
topology on
demand
free-form, no base mesh
needed; infinite detail in one
mesh
messy topology, can't
retopo cleanly,
performance tanks
concept sculpts,
exploration, creature
ideation
Voxel
Remesh
uniform-
density
remesh
clean-enough uniform mesh;
predictable density
uniform = wasteful on
large forms; loses detail if
size wrong
the workhorse for
organic sculpting from
primitives
Multires subdiv levels
on a base
mesh
clean base preserved; sculpt
at levels; displacement from
levels; retopo-friendly
topology-locked (edit base
first); subdiv artifacts on
bad topology
professional character/
creature workflow (sculpt
low, detail high)
The professional recipe: start from primitives/blockout → Voxel Remesh at coarse size → primary
forms → remesh finer → secondary forms → remesh finer (or multires switch) → tertiary detail. Each
remesh is a stage gate: don't detail before the form is right. For final assets: sculpt with Multires on
a  clean  base  (level  1–2  forms,  level  3–5  detail)  →  retopo  (D23)  or  use  multires  directly  with
displacement (D28).
30.4 THE THREE-FORM WORKFLOW (with time budgets)
Stage What Time
share Gate
Primary
forms
silhouette masses (head sphere, torso block, limb
cylinders); proportions from the sheet (D08/Ch 16)
30% silhouette approval — the
shape must read in 1 second
Secondary
forms
anatomy: muscle masses, bone landmarks, fat pads
(Ch 16.6); asymmetry begins
40% anatomy approval — structure
reads from all angles
Tertiary
details
pores, wrinkles, scales, scars, skin texture (alphas),
micro-detail
30% detail approval — only after
forms locked
Never detail an unapproved form.  The three-stage gate is what separates professional sculpts
from "hours spent polishing a wrong shape." Use the Pose brush during blocking to test the model
in stance before detailing.
• 
• 
• 
• 
• 
• 
• 
DEPTH CHAPTER 30 — SCULPTING DEPTH: BRUSHES, WORKFLOWS & DETAIL TRANSFER

30.5 REGION WORKFLOWS (what to sculpt where, in
order)
Head/face: skull mass → brow ridge → zygomatic → jaw → eye sockets → nose → lips → ears →
neck. Face sculpting is bone-first (Ch 16.4 landmarks), then muscle (Ch 16.6), then skin. Eyes:
sculpt the socket, not the eyeball (eyeballs are separate assets, D33).
Torso: ribcage mass → spine furrow → chest (pectorals) → abs/obliques → shoulders (deltoids/
traps) → back (lats). Female/male/stylized differences per Ch 16.
Limbs: shoulder cap → upper arm → elbow (olecranon) → forearm → wrist; hip mass → thigh →
knee (patella + tendon) → calf → ankle. Flex-and-extend poses to check silhouette (muscles
change shape!).
Hands/feet: palm fat pads → thumb saddle → finger segments → knuckles; sole arch → heel →
toes. Hands are detail-heavy — budget topology accordingly (D31).
Creatures: follow the spec sheet (D05): mass primitives → spine/limb logic → surface (scales via
alphas, fur base via texture strokes, chitin plates via flatten+crease) → species features (horns,
mandibles — sculpted then hard-surface if rigid, D18).
30.6 ALPHAS & CUSTOM BRUSHES (the detail engine)
Making an alpha: paint a grayscale image (black = no effect, white = full effect); load via Brush →
T exture  →  Image.  Pro alpha library:  pores  (dot  clusters),  skin  wrinkles  (line  patterns),  scales
(hexagon/overlap),  bark,  leather,  cracks,  cloth  weave,  fingerprints,  blood  vessels.  Stamping
technique: Crease/Stamp brush + alpha → stroke along a path (scales follow the body direction);
vary size/rotation along the stroke for naturalism; never stamp uniformly (nature doesn't). Custom
brush saving: adjust a brush → Header → Active T ool → "Brush" → save as a named brush asset (D84
asset libraries — reusable across projects).
30.7 MASKS & FACE SETS
Masks protect regions: paint masks (Mask brush), Box/Lasso masks, and invert (Ctrl-I) to work
the complement. Use for: protecting the face while sculpting the neck, keeping a clean jawline.
Face Sets (auto or painted): colored region groups — use for: isolating the eye area, applying
different materials per region (later), hiding regions (hide/unhide per face set — H/Alt-H), and 
Face Set masks for auto-masking.
Workflow: sculpt the whole → mask the finished zones → sculpt the rest — detail flows without
destroying neighbors.
• 
• 
• 
• 
• 
• 
• 
• 
DEPTH CHAPTER 30 — SCULPTING DEPTH: BRUSHES, WORKFLOWS & DETAIL TRANSFER

30.8 DETAIL TRANSFER (making the sculpt a usable
asset)
Path How Use
Retopo + bake
(professional default)
retopo the sculpt (D31) → bake normal/AO/
displacement maps (D28/32)
the standard film/game path:
low-poly + maps
Multires displacement keep multires levels; render with displacement
(micro-displacement, D26)
film-only, high-end; expensive
Decimate + sculpt Decimate modifier to reduce, then re-sculpt
cleanup
quick drafts, not final
Instant/auto remesh Quad Remesher/Instant Meshes for quick clean-ish
quad results
game/background assets, quick
turnarounds
Bake setup essentials (D28 recap + D32): low-poly with UVs active; high-poly selected; cage/ray
distance correct; margin 2–8 px; bake at 2× final then downscale; normal maps: OpenGL (+Y green
up) for Blender.
30.9 PERFORMANCE & MEMORY
Poly counts: viewport sculpting is smooth up to ~1–4M verts on GPU; dyntopo beyond that = lag
— use multires levels or remesh size discipline.
Remesh size logic: remesh size ≈ smallest detail you need × 2; fine remesh on the whole model
wastes 90% — use localized remesh (mask + remesh selection) where possible.
Levels & undo: raise undo steps for sculpting (Preferences); save incremental versions before
risky passes (D124).
Hide/unhide huge regions while working; viewport subdivision (Simplify) to keep the view
interactive.
30.10 SCULPTING FAILURE MODES & FIXES
Symptom Cause Fix
Mesh explodes/shatters dyntopo runaway; remesh size too coarse
for brush
undo; smaller remesh; lower strength
Detail lost on remesh remesh size too large finer remesh; remesh before detail, not after
Sculpt looks "blobby" no secondary forms (anatomy) add bone landmarks + muscle masses (Ch
16.6)
Symmetric doll look symmetry left on final asymmetry pass with symmetry off
Pinch artifacts
everywhere
brush strength too high / no smooth
passes
halve strength; smooth between passes
Can't retopo the sculpt dyntopo mess decimate to a manageable density, then
retopo (D31)
Wrinkle details pop in
render
sculpt detail not in normal map bake at 2×, proper cage; check normal
strength
Performance death millions of verts from dyntopo switch to multires/voxel discipline; hide
regions
• 
• 
• 
• 
DEPTH CHAPTER 30 — SCULPTING DEPTH: BRUSHES, WORKFLOWS & DETAIL TRANSFER
