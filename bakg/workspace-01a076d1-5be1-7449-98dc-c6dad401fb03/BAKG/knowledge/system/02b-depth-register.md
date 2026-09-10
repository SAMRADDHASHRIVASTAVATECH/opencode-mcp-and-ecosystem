# Part 2B — Master Depth Register (Ch 16–40)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 31–33 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

PART 2B — THE MASTER DEPTH REGISTER
Scope requirement (binding):  the base register (Part 2, D01–D138) maps every domain at
L1–L7. This register maps the  master depth chapters  that expand those domains to their
extreme  practical  depth:  exhaustive  choice  libraries,  parameter  encyclopedias,  and  system
masterclasses. Depth chapters are numbered 16–40, continuing after the 15 base chapters.
Under the  Non-Negotiable Scope Requirement  (Part 0), this register is  never closed: any
domain that a film project can touch that lacks a depth-chapter counterpart must be given one
(continuing from chapter 41) before the graph can be considered complete for that domain.
Status: [REQ]=required · [OPT]=optional · [SIT]=situational · [ADV]=advanced
PART 2B — THE MASTER DEPTH REGISTER

# Depth chapter Deepens
domains What it adds
16 Anatomy & Proportions
Libraries
D21, D04,
D05, D67–D73
Numeric proportion tables (human/stylized/quadruped/avian/
insect/aquatic/limbless), joint range tables, muscle form library,
invented-creature toolkit
17 Materials & Shaders
Encyclopedia
D30–D36 120+ material recipes with exact Principled settings; node
recipes; map requirements per material
18 Stylized & NPR Shading
Systems
D31, D30,
D113
Cel/toon, 2-tone/3-tone anime, outlines (4 methods), anime face
shadows, cartoon, painterly; render & comp for toon
19 Shape Keys, Blendshapes &
Driver Automation
D59, D60,
D54, D58
Shape-key system mastery, 60+ facial blendshape library, driver
language + 12 automation recipes
20 Procedural Characters,
Auto-Rigging, Mocap &
Retargeting
D19, D20,
D48, D131,
D135
Base meshes, Rigify, auto-riggers, GN character generators,
mocap acquisition/cleanup/retarget, hand-key hybrids
21 Cinematography & Editing
Theory
D102–D107,
D120
Full shot grammar tables, composition systems, continuity rules,
pacing theory, transitions, sync
22 Lighting & Mood
Encyclopedia
D108–D111 Time-of-day & weather lighting tables, 12 mood recipes with
setups, lighting patterns, color theory for light, exposure/IES/link
groups
23 Sound Design & Music D133, D62,
D120
Sound roles, dialogue/foley/ambience/music, recording, mixing &
loudness, VSE audio, music editing, sync
24 Pipeline Automation,
Python, USD, Render Farms
D122–D125,
D136
Blender Python API recipes, add-on structure, USD/glTF/FBX
pipelines, network/cloud rendering, version control
25 Real-Time & Interactive
Pipelines
D113, D137 EEVEE Next production settings, realtime animation, game/web
export, draw-call & texture discipline, limitations
26 The Optimization
Masterclass
D14, D24,
D26, D114,
D126
The full optimization ladder: LOD automation, proxies, textures,
instancing, viewport, memory, lightmaps, baking
27 Worldbuilding &
Environmental Storytelling
Masterclass
D02, D79,
D83
World-layer system with visual consequences, 10 environmental-
storytelling techniques, palette & weather systems, scale/map
design
28 Advanced Rigging Systems D48–D59 Full node cards: foot roll, hand, spine, shoulder, facial
automation, mechanical, wing, tail, multi-leg gait, jiggle/squash,
space switching
29 Animation Depth: The
Performance Masterclass
D64–D78 Professional blocking→spline pipeline, Graph Editor mastery,
timing/spacing tables, the 12 principles in Blender practice,
footwork, acting technique, NLA/pose libraries, polish & failure
modes
30 Sculpting Depth: Brushes,
Workflows & Detail
D22 Brush encyclopedia, brush-settings mastery, dyntopo/voxel/
multires decisions, three-form workflow with gates, alphas,
masks & face sets, detail transfer, performance
31 T opology & Retopology
Depth: The Deformation
Atlas
D23, D24 Joint-by-joint & facial topology atlases with vertex counts, pole/
transition patterns, density budgets, retopology tooling,
decimation/LOD, mesh health, bend testing
32 UV, T exture & Baking Depth D25–D29 UV strategy per asset class, seam planning, texel-density tables,
UDIMs, painting workflow, the full baking pipeline (normal/AO/
curvature/thickness), photo projection, procedural recipes,
artifacts
PART 2B — THE MASTER DEPTH REGISTER

# Depth chapter Deepens
domains What it adds
33 Hair, Fur & Feathers Depth D43–D47 Curves-hair full workflow, grooming brushes, strand materials,
styling patterns, GN fur recipes, feather construction, dynamics
tuning, budgets, stylized hair
34 Cloth, Costume & Wear
Depth
D37–D41, D91 Garment construction techniques, cloth-sim tuning masterclass,
fabric-behavior library, armor/accessory integration, aging &
wear, sim budgets & caching
35 VFX & Effects Depth D100, D101,
D87, D95–D98
The layered-effect method, particle/GN recipes, fire & smoke
tuning, magic-system design, impact & destruction layers,
compositing integration
36 Compositing & Color Depth D115–D119 Compositor node cookbook, pass-based relighting, scopes
mastery, grading workflow, film looks & LUT s, stylized grading,
failure modes
37 Environment & T errain
Depth
D79–D86 Environment pipeline, terrain generation systems, vegetation
ecosystems, modular architecture, water systems, lighting
integration, the hero/background split
38 Story, Storyboard &
Animatic Depth
D01, D09,
D10, D120,
D130
Story structures, the animatic as contract, boarding technique,
shot design for story, animatic workflow, Grease Pencil boarding
39 AI Concept Development
Depth
D06 Local AI toolkit, prompt engineering, ControlNet mastery,
character consistency, img2img/inpaint/outpaint, style control,
AI-to-3D bridge
40 Grease Pencil & Hybrid
2D-3D Depth
D130 GP3 object model, drawing/animation workflow, GP materials &
looks, 2D animation, hybrid 2D-3D pipelines, performance &
fixes
How to read the depth chapters
Each depth chapter is a masterclass in tables and recipes: where the base chapters explain what
a system is and when to use it , the depth chapters give you the numbers, parameters, and setups to
execute it — and the failure modes that come with each.
The depth chapters are style-agnostic unless stated: every table flags stylized vs realistic where
the choice matters. They also deliberately  cross-reference base domains (e.g., "see D51 (IK)")
instead of repeating them — read a depth chapter alongside its base domains.
The  register  is  extensible:  future  depth  chapters  continue  numbering  from  41  (the  standing
instruction — completeness over brevity — applies to every revision).
Completeness is measured, not asserted: Part 2C (Coverage Completeness Report)  audits
every  domain  D01–D138  against  the  corpus  (script  audit_coverage.py ),  and  Part  2D  (Depth
Supplements, S-01…S-18) supplies the practical depth for the domains that are base-covered only.
The measured result is 138/138 domains with practical depth.
PART 2B — THE MASTER DEPTH REGISTER
