# Part 3 — Knowledge Relationship Map (Graph Edges)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 116–119 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

PART 3 — THE KNOWLEDGE RELATIONSHIP
MAP (GRAPH EDGES)
This part makes the "graph" explicit: every arrow between domains, with its type (DEPENDENCY = A
needs B; INFLUENCE = A changes how B is done; COST = A scales cost of B). Reading these edges is
how you plan a production and predict consequences.
3.1 EDGE TYPES
Edge type Meaning Example
→ NEEDS A cannot be done properly without B Rigging NEEDS T opology
→ DRIVES A produces the input for B Character Design DRIVES Modeling
→ AFFECTS A changes the quality/cost of B Model Complexity AFFECTS Render Cost
→ CONSTRAINS A sets limits B must respect Story CONSTRAINS Shot Design
⇄ FEEDBACK B's result should loop back to A Animation ⇄ Rig (animation test fixes rig)
3.2 THE MAIN PIPELINE SPINE
IDEA → Story (D01) → Worldbuilding (D02) → Character Concept (D03) → Design (D04/D05)
→ References (D07) → Character Sheets (D08) → Storyboard (D09) → Animatic (D10)
→ Previs (D11) → 3D Planning (D14) → Blockout (D16) → Modeling (D17–D20)
→ Topology (D24) → UV (D25) → Textures (D26–D29) → Materials (D30–D36)
→ Clothing/Groom (D37–D47) → Rigging (D48–D63) → Animation (D64–D78)
→ Environment (D79–D86) → Physics/VFX (D87–D101) → Camera (D102–D107)
→ Lighting (D108–D111) → Rendering (D112–D116) → Compositing/Color (D117–D119)
→ Editing (D120–D121) → QC (D127) → Final Output (D128) → Archive (D129)
3.3 THE CRITICAL EDGE SETS (dependency chains)
Chain 1 — Design → Geometry → Deformation (the character spine)
Character Design (D04) → Creature Design (D05) → Modeling (D19/D20) → Topology (D24)
→ UV (D25) → Texturing (D26) → Materials (D30) → Rigging (D48) → Skeleton (D49)
→ Skinning (D57) → Deformation (D58) → Correctives (D59) → Animation (D64)
Key implications: - Design decisions become deformation constraints : a wide neck means the
neck rig must handle a heavy head; a long tail needs loop topology (D24) before rigging. - Topology
mistakes  cannot  be  fixed  by  rigging (D24  rule):  modeling  lock  must  happen  before rig
investment. -  Rig quality gates animation quality  (D48): animation start requires rig sign-off
(D60/D78 checklists).
PART 3 — THE KNOWLEDGE RELATIONSHIP MAP (GRAPH EDGES)

Chain 2 — Performance → Secondary Motion → Simulation
Animation (D64) → Motion (D65–D78) → Secondary Motion (D77) → Cloth (D39) → Hair (D47)
→ Fur/Feathers (D44/D45) → Simulation (D87–D99) → Force Fields/Wind (D88/D99)
Implications: - Simulations need final animation (D88 rule #3): never sim before animation lock. -
Every secondary element adds cost : cloak + hair + fur on one creature = 3 sim systems × 3
caches. Budget secondary motion at design time  (D37/D43) — this is why the "flowing cloak" in
the user's example is a design decision, not just an effect.
Chain 3 — Camera → Light → Render → Comp (the image chain)
Camera (D102) → Shot Design (D106) → Cinematography (D103) → Composition (D104)
→ Lighting (D108) → Shadows (D109) → Atmosphere (D110) → Volumetrics (D111)
→ Rendering (D112) → Engine Choice (D113) → Passes/AOVs (D115/D116)
→ Compositing (D117) → Color Correction (D118) → Color Grading (D119)
Implications: -  Lighting decides render cost : volumes (D111), SSS (D32), many lights (D108)
multiply render time (D114). -  Passes are the contract with comp : decide the pass list (D115)
before the final render, not after. -  Grading after editing  (D119): the edit (D120) is final before
color.
Chain 4 — Story → Film (the meaning chain)
Story (D01) → Storyboard (D09) → Animatic (D10) → Shot List → Shot Design (D106)
→ Animation (D64–D78) → Editing (D120) → Sound (D133) → Final Film
Implication:  the animatic is the budget  — its shot count and complexity set every downstream
cost (D10).
3.4 COST RELATIONSHIPS (complexity × cost)
If you increase… It scales… Cost multiplier Control
Polygon count (D24) Rig time, sim time, render time,
memory
~linear Budgets (D14), LOD
(D24)
T exture resolution (D26) VRAM, render time, file size ~quadratic (8k = 4×
4k)
Budgets, UDIM
discipline
Strand/particle count (D43/
D44/D87)
Sim time, render time super-linear Density falloff, LOD
Light count & volumes (D108/
D111)
Render time super-linear Light linking, pass
split
SSS objects (D32) Render time high Hero-only SSS
Sim systems per character
(D39/D47)
Sim + cache + troubleshooting additive × each Design-time budget
Rig complexity (controls,
correctives)
Rig build + animation usability moderate Animator-test early
Shot count (D10) Every downstream stage linear Lock the animatic
Style fidelity (realism) All lookdev + sim + render high Style decision (D04)
PART 3 — THE KNOWLEDGE RELATIONSHIP MAP (GRAPH EDGES)

The master rule:  complexity in  design (D04/D05) is free; complexity in  3D is expensive.  Design
complexity into the 2D, budget it out of the 3D.
3.5 THE "WHAT AFFECTS WHAT" GRID (condensed)
Domain What it NEEDS What it AFFECTS
D04/D05 Design D03 concept, D07 refs D19/D20, D37, D43, D48, D69
D24 T opology D23 retopo D48, D58, D25, D56
D25 UV D24 D26–D28, D30, D28 baking
D30 Materials D26–D29 D108 (how light looks), D112
D39 Cloth D37/D38, D64 (final anim) D77, D112 (render), D126
D48 Rig D24, D21, D49 D64–D78, D56/D57
D60 Facial D24 facial topology, D54 D61–D63, D75
D64 Animation D48 sign-off, D12 refs D39/D47 (sim drivers), D107 (camera)
D79 Environment D02, D16, D14 D108, D110, D126
D85 Geometry Nodes D13 D82, D44, D86, D99, D100
D88 Physics D14 (scale!), D13 D89–D99
D102 Camera D14 D103–D107, D112, D117
D108 Lighting D02 (time/weather), D79 D109–D111, D112, D117, D32 (skin!)
D112 Rendering D30, D108, D113 D115–D117, D127, D128
D117 Compositing D115/D116 D118/D119, D128
D127 QC every stage's checklists D128 (final quality)
3.6 FEEDBACK LOOPS (edges that loop backward)
Animation ⇄ Rigging: every animation test informs rig fixes (D48); schedule a "rig test shot."
Rendering ⇄ Materials/Lighting: first real renders always reveal material/lighting issues
(D127); plan an early "lookdev shot."
Blockout ⇄ Previs: staging problems found in previs return to blockout (D11/D16).
Animatic ⇄ Storyboard: pacing problems return to boards (D10).
QC ⇄ Everything: the QC pass (D127) loops into any stage.
Editing ⇄ Animation: the edit's timing demands animation re-timing (D120) — lock the edit
before final animation polish.
Compositing ⇄ Rendering: comp needs that one pass you didn't render (D115) — plan passes
before render.
1. 
2. 
3. 
4. 
5. 
6. 
7. 
PART 3 — THE KNOWLEDGE RELATIONSHIP MAP (GRAPH EDGES)

3.7 PREREQUISITE LEVELS (what you must know before
X)
To master… You must already understand…
Retopology Subdivision modeling, topology rules
UV mapping T opology (seams follow loops)
Shaders Materials, math nodes, color spaces
Rigging T opology, anatomy basics, constraints
Weight painting Bone orientation, vertex groups
Correctives Drivers, shape keys, deformation
Facial animation Facial rig, acting basics, eyes
Cloth sim Scale/units, collision basics, animation timing
Geometry Nodes Fields/attributes, instancing, math
VFX Particles, shaders, compositing
Lighting Materials (how they react), camera
Compositing Passes, color spaces, scopes
Production pipeline Everything (it's the meta-system)
3.8 STYLE-DEPENDENT EDGES (edges that change with
style)
Edge Realistic film Stylized/anime Cartoon
Design → Modeling Anatomy-heavy (D21) Simplified anatomy Exaggerated shapes
T opology → Deformation Muscle correctives (D59) Clean silhouettes Squash & stretch (D65)
Skin shader (D32) SSS full SSS off/2-tone Flat/cel
Cloth (D39) Simulated Simulated or drawn Drawn/simple
Hair (D43) Groomed + sim Stylized groom Simple shapes
Lighting (D108) Physically-based Stylized 3-point Bold/emissive
Rendering (D113) Cycles EEVEE/Cycles EEVEE
Comp (D117) Subtle Bold looks Strong looks
The style decision (D04/D138) is the master switch that reconfigures these edges.
PART 3 — THE KNOWLEDGE RELATIONSHIP MAP (GRAPH EDGES)
