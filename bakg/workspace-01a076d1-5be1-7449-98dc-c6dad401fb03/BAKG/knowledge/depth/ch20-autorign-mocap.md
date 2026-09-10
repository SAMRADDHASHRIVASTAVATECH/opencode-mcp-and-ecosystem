# Depth Chapter 20 — Procedural Characters, Auto-Rigging, Mocap & Retargeting

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 157–159 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 20 — PROCEDURAL
CHARACTERS, AUTO-RIGGING, MOCAP &
RETARGETING
Expands D19, D20, D48, D131, D135. Production accelerators: base meshes, Rigify and other auto-
riggers, geometry-node character generators, and the motion-capture pipeline — with honest notes
on when each speeds you up and when it slows you down.
20.1 BASE MESHES (D135) — starting points, not
crutches
Base mesh source Best for Caveats
Blender's default human (Add →
Mesh → Human?)
Quick proportions study Basic topology; re-topo for production
Rigify's metarig + humanoid
sample
Standard humanoid + auto-rig Good base; topology is generic — needs re-
topo for hero characters
MakeHuman (external, free) Realistic human base with
morphs
Dense, quad-heavy mesh; retopo + re-UV for
film; export via glTF/FBX
Character Creator / DAZ (external) Stylized-to-realistic base +
mocap-ready rigs
Licensing + conversion cost; transfer quality
varies
Commercial base packs Production heroes Match topology to your rig plan (D24)
The  rule: a  base  mesh  saves  blockout  hours,  not  design  decisions.  Proportions,  topology  for
deformation, and facial loops are always your responsibility (D19/D24).
20.2 RIGIFY (built-in auto-rigger)
How it works:  you place a  metarig (a humanoid bone template) inside your model, scale/rotate
bones to fit, then Generate Rig — Rigify builds the full control rig (FK/IK arms & legs, spine, fingers,
face controls, twist, stretch options, custom shapes) on top of your deform bones. Workflow: (1) fit
metarig to model (position joints anatomically — D49); (2) generate; (3) parent mesh with automatic
weights (or your own weights); (4) customize (add custom properties, extra controls, face bones).
Strengths: fast standard humanoid rigs; excellent control set; face + fingers included; battle-tested.
Weaknesses: generic — it rigs a humanoid, not your character; non-human proportions/extra limbs/
unique  anatomy  need  manual  work;  heavy  bone  count  can  confuse.  When  to  use: standard
humanoids  where  speed  matters  (background  characters,  crowds,  game  characters,  quick
turnarounds). When not: hero characters needing bespoke deformation, creatures, characters with
non-human anatomy, extreme proportions — there, hand-build or heavily customize. Customizing
Rigify: add bones to the metarig with the "Rigify" bone layers/specials (def_ , ctrl_, etc.) — learn the
metarig naming (Rigify bones use .L/.R , ORG- , DEF- , MCH- , CTRL-  prefixes); regenerate keeps your
additions if marked correctly.
DEPTH CHAPTER 20 — PROCEDURAL CHARACTERS, AUTO-RIGGING, MOCAP & RETARGETING

20.3 OTHER AUTO-RIGGERS (external, when useful)
Auto Rig Pro (paid add-on): humanoid + quadrupeds, mocap retargeting built in, facial; faster for
quadrupeds than Rigify.
Blender rigify community add-ons: Rigify variants for quadrupeds (learn how the metarig
works — you can build a quadruped metarig manually).
Rokoko / Move.ai / Vicon (mocap, external): see 20.5.
Winged/tail/facial packs — niche.
The honest evaluation:  auto-riggers trade  control for  speed. For shots where the character just
needs to move correctly, they win. For performance/acting/deformation-critical heroes, the bespoke
rig (Ch 6) still wins. A strong studio pipeline uses both: auto-rig background, bespoke for heroes.
20.4 GEOMETRY-NODE CHARACTER & CREATURE
GENERATORS (D85 applied)
Character generator (parameterized): a GN modifier on a base mesh with group inputs: Height,
Width, Muscle, Limb Length, Head Size, Waist, etc. → implemented via bend/stretch deformations
(Simple Deform, scale by attribute) or shape keys (Ch 19.2 body morphs) driven by the inputs. Use
for:  crowds,  background  characters,  variant  armies,  player-customization  systems.  Creature
generator: a body-plan kit in GN: spine curve (length/arc) → instanced ribcage + pelvis → limb pairs
(count, length, joint angles) → head variant → surface (scales/fur via instancing, D44). The generator
instantiates anatomy from parameters — genuinely useful for ideation and crowds (D69's spec sheet
becomes the input panel). Rig automation with GN:  GN can output bone positions (generate an
armature from a curve!) — experimental but real: "curve-to-armature" generators for tails/tentacles/
spines (D50). Production-grade for simple chains. When to use: crowds, variants, procedural props-
carrying characters, ideation. When not: hero characters needing handcrafted topology/rigs — GN
outputs generic topology that still needs the full D19–D24 treatment.
20.5 THE MOCAP PIPELINE (D131)
Acquisition: -  Studio mocap (marker-based):  professional;  cleanest  data;  cost  high.  -  Suit-
based (Xsens/Rokoko): inertial; good for body, no fingers/face by default. - Camera-based (video
→ pose estimation): Move.ai, Rokoko, or Blender add-ons using ML (MediaPipe-based) — free/cheap
and good enough for body reference ; noisy on feet/hands. - Performance capture (face):  iPhone
ARKit blendshapes (face motion → blendshape values) — industry standard for facial (import via add-
ons as shape key values).
Import: BVH (motion-only) or FBX/glTF (with skeleton).  BVH→Blender: File → Import → Motion
Capture (BVH); Blender creates the armature + actions. glTF: File → Import → glTF 2.0 (imports with
"rest" pose).
Retargeting (the hard part):  1. Bone mapping: map source bones → target bones (Auto Rig Pro
does this visually; for Rigify, use its retargeter; for custom rigs, use constraint-based retargeting:
Copy Rotation/Location from source to target with correct space settings, or the NLA "push down"
workflow). 2.  Rest-pose alignment: source and target must have matching rest poses (or use a
"calibration" pose — T-pose/A-pose) — misalignment = twisted limbs. 3.  Scale: source meters →
target scale (D14); use a global scale factor on the constraint. 4. Cleanup: raw mocap is noisy: apply
smoothing (Graph Editor → Filter → Smooth, or the MoCap modifier on curves: Motion Tracking →
MoCap — smooths foot contact), remove spikes (denoise in Graph Editor), and fix foot contact: lock
• 
• 
• 
• 
DEPTH CHAPTER 20 — PROCEDURAL CHARACTERS, AUTO-RIGGING, MOCAP & RETARGETING

feet during stance (foot IK constraint with the mocap baked to the IK target, or floor-lock with
keyframes) — foot slide is the #1 giveaway. 5. NLA layering: push the retargeted motion down to
NLA; layer hand-keyed fixes on top (NLA tracks).
Hand-key vs mocap — the decision (also Part 5):  | Need | Use | |---|---| | Realistic human
locomotion/body  mechanics,  quick  turnaround  |  Mocap  (clean  +  fix  feet)  |  |  Stylized/cartoon/
exaggerated  performance  |  Hand-key  (mocap  reads  "real",  fights  cartoon)  |  |  Creature/creature-
analog motion | Hand-key from animal reference (D68) — no mocap of dragons | | Dialogue acting
close-ups | Hand-key face + eyes (mocap face = uncanny without careful cleanup) | | Hybrid | Mocap
body + hand-key face/eyes/hands (the industry standard) |
Mocap failure modes:  feet sliding (fix contacts); jitter/spikes (filter); retarget twist errors (roll
alignment); scale mismatch (limbs too short/long); "mocap look" (no exaggeration — apply 10–15%
pose exaggeration in splining, D78).
20.6 RETARGETING TO ANY RIG — THE GENERAL RECIPE
Source & target both in T/A-pose with same global scale (or scale applied).
For each chain (pelvis, spine, arms, legs, head): create a constraint from target bone → source
bone (Copy Rotation, world space, keep local rotation differences via an offset).
Bake (Animation → Bake Action, Visual Keying on).
Apply MoCap filter for smoothness.
Foot-contact pass; hand/face pass by hand.
The "same-skeleton" shortcut: if both rigs share a skeleton structure, copy the action directly
(Action → rename/duplicate) and re-map bone names via the "Bone Name Map" (edit mode
renaming).
1. 
2. 
3. 
4. 
5. 
6. 
DEPTH CHAPTER 20 — PROCEDURAL CHARACTERS, AUTO-RIGGING, MOCAP & RETARGETING
