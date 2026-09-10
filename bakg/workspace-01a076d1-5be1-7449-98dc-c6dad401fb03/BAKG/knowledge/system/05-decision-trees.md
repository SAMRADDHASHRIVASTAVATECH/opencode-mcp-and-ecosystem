# Part 5 — Decision Trees & Choice Libraries

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 126–131 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

PART 5 — DECISION TREES & CHOICE
LIBRARIES
Every serious choice in the graph, condensed into decision logic. Use these when a fork appears in
your traversal.
5.1 STYLE & LOOK DECISION (fires at D04)
Question → Go
Need physical realism (skin, water, glass,
believable humans)?
Realistic path: anatomy (D21), SSS (D32), Cycles (D113)
Cartoon/game/toon look, fast iteration? Stylized path: simplified anatomy, flat/cel or bold PBR, EEVEE
Anime look? Anime path: 2-tone shading (Shader-to-RGB D31), bold
palettes, EEVEE/Cycles
Abstract/experimental? Procedural path: GN (D85) + sims (D87–D99) + comp (D117)
Hybrid (realistic film + stylized characters)? Mixed: match the grounding (lighting/render) to the hero
element
The rule: decide at D04; every downstream edge reconfigures (3.8). Switching styles mid-production
= redoing lookdev.
5.2 RENDER ENGINE (D113)
Condition Engine
Final film, realism, refraction/SSS/volumes matter, render time available Cycles
Real-time look, interactive, stylized, fast preview, long film with tight
deadline
EEVEE
Realtime game pipeline EEVEE (or external game engines via
export)
Blockout/previs/animatic captures Workbench
Hybrid: iterate EEVEE, final hero shots Cycles Both (PBR-clean materials make this
painless)
The rule: commit early (D14); if you might switch, keep materials PBR-pure (D30) so the swap is a
settings change, not a re-lookdev.
PART 5 — DECISION TREES & CHOICE LIBRARIES

5.3 MODELING WORKFLOW (D19/D20)
Situation Workflow
Realistic human/creature, film Sculpt-first (D22) → retopo (D23) → bake (D28)
Stylized character, boxy/cute Box-model + subdiv (D17) or sculpt-first for organic
Hard-surface/mechanical Box + bevels + booleans + modifiers (D18)
City/environment/backgrounds Modular + procedural (D81/D85)
Original creature with anatomy Sculpt-first + spec sheet (D05)
Hero prop with detail Hybrid: box model + sculpt detail + bake
5.4 RIG TYPE (D48–D52)
Need Rig choice
Standard biped character FK/IK switch limbs + FK/BBone spine + stretch option
Quadruped 4× leg IK + spine BBone + neck + tail chain (D70)
6+ legs Per-leg IK + gait driver (D71)
Snake/tentacle/tail BBone chain or FK + stretch (D50)
Bird/dragon wings Feather-row hierarchy + IK wingtip + fold controls (D45/D72)
Mechanical/robot Constrained axis bones, pistons (D50/D53), no soft deform
Cartoon stretchy Stretch-to chains + squash/stretch global (D50/D65)
Realistic facial Shape-key blendshapes + bone control rig (D60)
Stylized facial Bone-driven face (D60)
Minimal/one-off prop Single bone/constraint (D53) — don't over-rig!
The rule:  rig only what the animation needs (D48: "one control = one job"); a simple creature
doesn't need a Hollywood face rig.
5.5 HAIR / FUR / FEATHERS (D43–D46)
Need System
Hero character hair, film Curves hair + manual grooming + dynamics (D43/D46/D47)
Stylized hair Curves + stylized groom, simple sim or driver sway
Mammal fur GN fur (D44) or curves + procedural noise; layers
Feathers GN feather instancing + wing hierarchy (D45)
Background creatures Low-density curves or alpha-card fur (D44)
Real-time game Cards/planes with alpha or low strand counts (D44)
PART 5 — DECISION TREES & CHOICE LIBRARIES

5.6 SIMULATION vs FAKE (D87–D99)
Effect Sim? Or fake with…
Cloak on hero character Sim (D39) —
Flag in distance — Vertex sway driver (D85)
Ocean — Ocean modifier (D94)
Puddle — Ripple shader (D94)
Hero splash/pour Sim (D93) Pre-made splash assets (D100)
Fire breath, stylized — Emissive curve + particles + glow (D101)
Fire, realistic Sim (D96) —
Explosion Sim (D97) + layers —
Rain — Particles (D87) + wetness (D31)
Dust motes — Particles (D87)
Falling debris Sim (D98) or particles —
Jiggle/secondary — Drivers/bones (D77) or soft body (D90)
The rule (D88 #2): fake first. Sim only when faking is harder or visibly worse.
5.7 DEPTH OF FIELD & MOTION BLUR (D112/D117)
Situation Approach
DoF, stylized or cheap Comp Defocus on Z pass (D117)
DoF, hero close-up realism Render DoF (D102)
Motion blur, fast action Render MB (D112, 2–8% shutter)
Motion blur, cheap Vector blur in comp (D117)
Both, heavy scene Comp both; render with MB off for speed
5.8 RENDER FORMAT & COLOR (D112/D128)
Purpose Format
Final frames from Cycles/EEVEE EXR multilayer (passes, D115)
Edit-grade master ProRes 422 HQ / DNxHR
Web delivery H.264/H.265, CRF 18–23
Social vertical 9:16 transcode from master
Color: default modern AgX view transform (D112)
Film emulation ACES/LUT s via comp (D119)
PART 5 — DECISION TREES & CHOICE LIBRARIES

5.9 PROJECT STRUCTURE (D123) — the "solo studio"
layout
project/
  00_docs/ 01_reference/ 02_concept/ 03_storyboard/
  04_assets/<type>/<asset>/  (blend, textures/, caches/)
  05_shots/<shot>.blend 06_render/<shot>/ 07_comp/ 08_edit/
  09_deliver/ cache/ backup/
5.10 THE "WHEN TO STOP" DECISION (D127/D78)
Signal Action
Animation: beats read, contacts clean, curves smooth, second-eyes approved Lock animation
Lookdev: hero materials approved under final lighting Lock lookdev
Sim: caches stable, no explosions, artist happy Lock sims
Render: test frames clean, budget met Lock render
Edit: pacing works, grade done, QC passed Deliver (D128)
The rule: locks are promises to stop polishing; honor them. (Infinite polish is the silent production
killer.)
5.11 ADD-ONS THAT GENUINELY HELP (D134)
Sapling Tree Gen (built-in) — trees.
Cell Fracture (built-in) — destruction (D97).
ANT Landscape (built-in) — terrain (D80).
BlenderKit / Poly Haven — free assets + HDRIs + materials (D84/D134).
Rigify (built-in) — auto-rigging humanoids (great base, learn to customize).
Auto-Rig Pro / Rigify variants (external) — pro auto-rigging.
PureRef (external, free) — reference boards (D07).
DaVinci Resolve (external, free) — color + edit finishing (D119/D128).
ComfyUI/A1111 (external) — local AI concept work (D06).
HardOps / BoxCutter (external) — hard-surface speed.
RetopoFlow / Quad Remesher (external) — retopology speed.
Every add-on is a lever, not a crutch: learn the underlying system (the graph) first, then add speed
tools.
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
• 
PART 5 — DECISION TREES & CHOICE LIBRARIES

5.12 FACIAL RIG METHOD (D60)
Situation Method
Realistic hero face + lip sync Shape-key blendshapes driven by a bone/custom-property control rig (Ch 19.2
library)
Stylized/cartoon face Bone-driven facial rig (brows, jaw, lips as bones) — simpler, deformable
Creature face (non-human) Bone-driven + a few shape keys for the species' expression set (mandibles, ears,
brow ridges)
Mocap face (ARKit) Blendshape rig matching ARKit key names (D20.5)
Minimal face (background) 3–5 shape keys (blink, smile, frown, jaw) — never over-build
T oon face with drawn
expressions
Shape keys per expression + GP overlay (D130)
5.13 SHADING STYLE (Ch 18 / D31)
Look System
Physical realism Principled + maps (D30)
Cel/toon Shader-to-RGB ramp + hull outline (18.2/18.4)
Anime 2–3 tone ramp + anime eye + face-shadow trick + selective outline (18.3)
Cartoon Bold 2-tone, black shapes, thick hull (18.5)
Painterly Displacement/UV-perturb noise + soft comp (18.5)
Game PBR + stylized PBR base + ramp-simplified shading (18.6)
Mixed (toon char in PBR world) T oon char shaders + PBR world — separate the ramp and grade (18.7)
5.14 MOCAP vs HAND-KEY (D20.5)
Need Choice
Realistic human body mechanics, fast Mocap + foot fixes
Stylized/cartoon/exaggerated Hand-key
Creatures (no human mocap) Hand-key from animal ref (D68)
Dialogue close-ups Hand-key face/eyes; mocap body if useful
Hybrid Mocap body + hand-key face/hands/eyes (industry standard)
5.15 OFFLINE vs REAL-TIME (D113/D137)
Target Engine
Film realism (refraction, SSS, GI, volumes) Cycles
Stylized film, fast iteration, long runtime EEVEE
Game engine / web / VR EEVEE for lookdev → export glTF/FBX/USD (Ch 25)
Realtime preview during production EEVEE viewport (regardless of final engine)
Interactive experience in Blender EEVEE + drivers/GN animation
PART 5 — DECISION TREES & CHOICE LIBRARIES

5.16 BASE MESH SOURCE (D20.1/D135)
Need Start
Realistic human hero MakeHuman/scan → retopo (or sculpt from scratch)
Standard humanoid + fast rig Rigify humanoid base
Stylized character Sculpt from primitive (D22)
Creature Sculpt from primitives + spec sheet (D05)
Crowd/background humans Base mesh + auto-rig + GN variants (Ch 20.4)
5.17 OUTLINE METHOD (18.4)
Need Method
Cartoon character, consistent thickness Inverted hull (18.4)
Vector-clean lines, technical Freestyle render pass
One-material toon, soft edges Fresnel emission outline
Hand-drawn animated line weight Grease Pencil overlay
Zero outlines (modern toon) None — rely on value contrast (18.6)
5.18 "SIM vs FAKE" — WEATHER EXTENSION (D87–D99)
Weather element Sim? Fake with
Rain (distant) — Particles + wetness (D87/D31)
Rain (hero close-up) Fluid for splashes (D93) Particle streaks + pre-made splash
Fog/haze — Mist pass + volume box (D110/D111)
Snow — Particles + drifting noise
Wind (cloth/hair) Cloth/hair sims (D39/D47) Vertex sway drivers (D85)
Lightning — Emissive flash + flicker driver (D101)
Flood/water level Fluid (D93) if hero Shader plane + edge foam (D94)
5.19 RIG BUILD ORDER (the checklist is the tree)
1. Skeleton: joints + orientation + naming (D49)  →  [FAIL: test bend every joint]
2. Deform bones + weights (D56/D57)  →  [FAIL: pose test]
3. Controls: FK/IK limbs, spine, head (D51/D52/D55)  →  [FAIL: animator usability test]
4. Foot/hand systems (28.1/28.2)  →  [FAIL: full gait test]
5. Shoulder/clavicle + spine add-ons (28.3/28.4)
6. Facial rig (D60)  →  [FAIL: expression sheet test]
7. Correctives + automation (D59/Ch 19)  →  [FAIL: extreme pose test]
8. Space switching + props (28.11/D42)  →  [FAIL: grab/release test]
9. Sign-off (Ch 6 checklist)  →  animation may begin
PART 5 — DECISION TREES & CHOICE LIBRARIES
