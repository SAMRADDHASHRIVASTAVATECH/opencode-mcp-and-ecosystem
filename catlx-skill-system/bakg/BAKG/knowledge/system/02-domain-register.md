# Part 2 — Master Domain Register (D01–D138)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 24–30 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

PART 2 — MASTER DOMAIN REGISTER
Every domain in the graph, numbered, with status, one-line definition, main prerequisites (PRE) and
feeds (→). Domains are the L1 nodes. The register is a table of contents; detail lives in the chapters
that follow.
Status: [REQ]=required · [OPT]=optional · [SIT]=situational · [ADV]=advanced
PART 2 — MASTER DOMAIN REGISTER

# Domain Status Definition PRE Feeds →
D01 Story & Script SIT Narrative structure, beats, dialogue,
pacing
Idea Boarding, Editing
D02 Worldbuilding &
Lore
SIT Setting, rules, climate, culture,
magic/tech systems
Idea Design,
Environment
D03 Character Concept SIT Personality, role, abilities,
movement style
Story Design, Rig,
Acting
D04 Character Design REQ Look, silhouette, shape language,
palette
Concept, Refs Modeling, Rigging
D05 Creature Design SIT Non-human anatomy logic,
believability, biomechanics
Concept, Refs Creature Modeling
D06 AI Concept
Development
OPT SD/SDXL/LoRA/ControlNet
exploration for concepts
Design sketches Character Sheets
D07 Reference
Development
REQ Photo/video/anatomy reference
collection & study
Idea All visual stages
D08 Character Sheets SIT T urnarounds, expressions,
proportions, callouts
Design Modeling, Rig,
Anim
D09 Storyboarding SIT Shot-by-shot framing and staging
drawings
Story, World Animatic
D10 Animatics SIT Timed storyboard cut to audio Storyboard Previs, Shot list
D11 Previsualization SIT 3D camera layout with stand-ins Animatic,
Blockout
Blockout, Layout
D12 Motion Reference SIT Filmed reference for gait/action/
acting
Animatic Animation
D13 Blender
Fundamentals
REQ UI, navigation, selection, transforms,
modes
— Everything
D14 3D Planning REQ Scale, units, budgets, asset/shot
breakdown
Animatic Blockout, Pipeline
D15 Scene Organization REQ Collections, naming, scenes, view
layers, links
Fundamentals All production
D16 Blockout REQ Proxy geometry, layout, proportion
validation
Planning Modeling, Previs
D17 Organic Modeling SIT Smooth, curved, living forms via
subdiv/box modeling
Fundamentals Character/
Creature
D18 Hard-Surface
Modeling
SIT Mechanical, angular, manufactured
forms
Fundamentals Props, Robots,
Armor
D19 Character Modeling REQ Human/humanoid base geometry,
topology
Design, Anatomy Rig, T exturing
D20 Creature Modeling SIT Original/non-human geometry from
creature design
Design, Anatomy Rig, T exturing
D21 Anatomy SIT Skeleton/muscle/fat logic;
proportions
Reference Modeling,
Sculpting
D22 Sculpting SIT High-poly detail:
primary→secondary→tertiary
Modeling,
Anatomy
Retopology
D23 Retopology SIT Clean low-poly cage from sculpt Sculpting Rig, UV
D24 T opology REQ Edge flow for deformation, loops,
poles, density
Modeling Rig, Deformation
PART 2 — MASTER DOMAIN REGISTER

# Domain Status Definition PRE Feeds →
D25 UV Mapping REQ 3D→2D unwrap, seams, islands,
packing
Model T exturing
D26 T exture Creation SIT Image textures: painted, photo,
generated
UV Materials
D27 T exture Painting OPT Direct 3D/2D painting of maps UV Materials
D28 T exture Baking OPT Detail transfer high→low, map
baking
High poly, UV Materials, Perf
D29 Procedural
T exturing
OPT Node-based, resolution-independent
textures
Shaders Materials
D30 Materials REQ Surface properties: color, roughness,
metalness
T extures, Shaders Rendering
D31 Shaders REQ Node graphs; Principled BSDF;
custom shading
Materials Materials, Render
D32 Skin SIT SSS, pore detail, tint maps, wet/dry Shaders, T extures Character
Lookdev
D33 Eyes SIT Cornea, iris, sclera, refraction,
caustics
Shaders Character
Lookdev
D34 T eeth SIT Enamel/dentin shading,
translucency
Shaders Character
Lookdev
D35 T ongue SIT Wet organic translucency, form Shaders Facial work
D36 Nails / Claws SIT Keratin shading, hardness,
subsurface
Shaders Creature Lookdev
D37 Clothing SIT Garment construction, patterns,
panels, seams
Character Model Rig/Sim
D38 Cloth Construction SIT Garment modeling techniques
(tailoring in 3D)
Clothing Cloth Sim
D39 Cloth Simulation SIT Cloth physics, collision, pinning,
caching
Cloth
Construction
Animation
D40 Accessories SIT Belts, straps, jewelry, gear Design Rig, Sim
D41 Armor SIT Rigid plates on flexible base, weight
logic
Design, Hard-
surface
Rig, Animation
D42 Props SIT Held/handled objects, interaction
design
Design Rig, Animation
D43 Hair SIT Curves-based hair, grooming,
materials
Model Hair Dynamics
D44 Fur SIT High-density short hair; procedural/
curves
Model Hair Dynamics
D45 Feathers SIT Feather construction, layering, flight
surfaces
Creature Design Rig/Sim
D46 Grooming SIT Guides, clumps, styling workflow Hair/Fur Hair Dynamics,
Render
D47 Hair Dynamics SIT Simulation of hair/fur/feather motion Groom Animation, Render
D48 Rigging REQ Control systems, hierarchy,
constraints
Model, T opology Animation
PART 2 — MASTER DOMAIN REGISTER

# Domain Status Definition PRE Feeds →
D49 Skeleton Design REQ Joint placement, bone orientation,
naming
Rigging Skinning
D50 Bone Systems REQ Bone types: deforming, control,
mechanical
Skeleton Deformation
D51 IK SIT Inverse kinematics for limbs Bones Limb Controls
D52 FK REQ Forward kinematics, natural arcs Bones Limb Controls
D53 Constraints REQ Copy/limit/track/transform
constraints
Rigging All rigs
D54 Drivers ADV Scripted/baked value automation Constraints Facial, Mechanical
D55 Controllers REQ Control bones, custom shapes, UX Rigging Animation
D56 Weight Painting REQ Vertex weights, paint workflow, auto
weights
Skeleton Skinning
D57 Skinning REQ Binding mesh to skeleton; weights &
envelopes
Rigging Deformation
D58 Deformation REQ How mesh bends; joint correction
needs
Skinning Animation
D59 Corrective Shapes ADV Shape-key / bone-driven fixes for
deformations
Deformation Polish
D60 Facial Rigging SIT Face controls: jaw, brows, eyes, lips,
blendshapes
Rigging Facial Animation
D61 Facial Animation SIT Expressions, micro-motion, eye
darts
Facial Rig Acting
D62 Lip Sync SIT Mouth shapes, visemes, phoneme
timing
Facial Rig Dialogue
D63 Eye Systems SIT Gaze, focus, blink, pupil; the soul of
acting
Facial Rig Facial Animation
D64 Character
Animation
REQ Full performance pipeline
(blocking→polish)
Rig Shot Production
D65 Animation
Principles
REQ The 12 principles + modern
extensions
Fundamentals All animation
D66 Locomotion REQ Walks/runs/gait mechanics Principles Creature/
Character
D67 Human Movement SIT Human biomechanics, weight,
balance
Locomotion Acting
D68 Animal Movement SIT Quadruped/bird/reptile gaits Locomotion Creature
Animation
D69 Creature
Movement
SIT Original anatomy → invented-but-
believable motion
Locomotion,
Design
Creature
Animation
D70 Quadruped
Animation
SIT 4-legged gaits, spine undulation Animal
Movement
Creature
Animation
D71 Multi-Legged
Creatures
SIT 6/8+ leg gaits, tripod/stability logic Creature
Movement
Creature
Animation
D72 Flying Creatures SIT Wings, flight physics illusion, takeoff/
land
Animal/Creature Creature
Animation
PART 2 — MASTER DOMAIN REGISTER

# Domain Status Definition PRE Feeds →
D73 Swimming
Creatures
SIT Fluid body motion, drag, undulation Creature
Movement
Creature
Animation
D74 Fighting SIT Combat choreography, impact,
anticipation
Acting, Timing Action shots
D75 Acting SIT Performance, intent, emotion
through body
Animation
Principles
Character
Animation
D76 Physical Acting SIT Weight, force, momentum
readability
Acting Character
Animation
D77 Secondary
Animation
SIT Follow-through, overlap, cloth/hair
response
Animation Polish
D78 Animation Polish OPT Splining refinement, arcs, spacing
cleanup
Animation Final animation
D79 Environment
Creation
SIT Full environments from blockout to
detail
World, Blockout Rendering
D80 T errain SIT Ground forms: sculpting,
displacement, heightmaps
Environment Environment
D81 Architecture SIT Buildings, structures, hard-surface
env assets
Hard-surface Environment
D82 Nature SIT Vegetation, rocks, water bodies,
organic env
Geometry Nodes Environment
D83 World Building SIT Environmental storytelling, set
dressing
Worldbuilding Environment
D84 Props & Assets SIT Reusable asset systems, asset
browser
Design All shots
D85 Geometry Nodes SIT Procedural modeling/instancing/
scattering
Fundamentals Env, VFX, Anim
D86 Procedural
Systems
SIT Parameterized generators, node
groups
Geometry Nodes Env, VFX
D87 Particles SIT Particle systems, emitters, point
scattering
Fundamentals VFX, Groom
D88 Physics SIT Core physics sim infrastructure Fundamentals Sims
D89 Rigid Bodies SIT Hard object collisions, destruction Physics VFX
D90 Soft Bodies SIT Squishy deformable objects Physics VFX
D91 Cloth Physics SIT Fabric sim (see also D39) Physics Clothing
D92 Hair Physics SIT Strand dynamics (see also D47) Physics Groom
D93 Fluids SIT Liquid simulation (Mantaflow) Physics VFX, Water
D94 Water SIT Ocean, puddles, splashes, foam Fluids Environment
D95 Smoke SIT Smoke sim, pyro, billowing Physics VFX
D96 Fire SIT Fire sim, flames, ignition Physics VFX
D97 Destruction SIT Fracture, rigid body breaks Rigid Bodies VFX
D98 Debris SIT Chunks, dust, secondary fragments Destruction VFX
D99 Environmental
Simulation
SIT Weather, rain, leaves, ambient
motion
Sims Environment
PART 2 — MASTER DOMAIN REGISTER

# Domain Status Definition PRE Feeds →
D100 VFX SIT Effects design: impacts, energy,
elementals
Sims, Particles Compositing
D101 Magic / Energy
Effects
SIT Glows, trails, arcs, runes, auras VFX Compositing
D102 Camera REQ Camera object, lens, sensor, depth
of field
Fundamentals Cinematography
D103 Cinematography REQ Shot language, coverage, continuity Camera Editing
D104 Composition REQ Framing, balance, focal point, rule of
thirds
Camera Shot Design
D105 Lens & Perspective SIT Focal length, distortion, perspective
logic
Camera Shot Design
D106 Shot Design SIT Shot sizes, angles, staging per story
beat
Cinematography Storyboard,
Lighting
D107 Camera Movement SIT Dolly, crane, handheld, shake;
motivated moves
Camera Shot Design
D108 Lighting REQ Light setup, mood, key/fill/rim, color
temp
Camera, Scene Rendering
D109 Shadows REQ Shadow design, softness, contact,
raytraced
Lighting Rendering
D110 Atmosphere SIT Fog, haze, depth cues, aerial
perspective
Lighting Rendering
D111 Volumetrics SIT Volumetric light shafts, fog volumes Lighting Rendering
D112 Rendering REQ Image generation, engines, settings Materials,
Lighting
Compositing
D113 Render Engines REQ Cycles, EEVEE, Workbench: choice &
tradeoffs
Rendering Render Settings
D114 Render
Optimization
REQ Samples, denoise, batching,
memory control
Rendering Production
D115 Render Passes SIT Split render into passes for
compositing
Rendering Compositing
D116 AOVs ADV Arbitrary output variables, custom
data
Rendering Compositing
D117 Compositing REQ Node compositor: passes, masks,
color, effects
Rendering Final image
D118 Color Correction REQ Exposure, contrast, balance fixes Compositing Grading
D119 Color Grading SIT Look development: LUT s, film
emulation, mood
Color Correction Final image
D120 Editing REQ VSE/EDL: cutting, pacing, transitions Shots Final film
D121 Shot Management SIT Shot naming, states, tracking,
render queue
Pipeline Production
D122 Asset Management SIT Asset browser, libraries, reuse,
linking
Pipeline Production
D123 File Organization REQ Folder conventions, naming, linked
files
Pipeline Production
PART 2 — MASTER DOMAIN REGISTER

# Domain Status Definition PRE Feeds →
D124 Versioning REQ Save versions, incrementing,
backups
File Organization Production
D125 Production Pipeline REQ People/workflow ordering,
dependencies
All Production
D126 Performance
Optimization
REQ Viewport/render performance
strategy
Pipeline Production
D127 Quality Control REQ Reviews, checks, error catching Everything Final output
D128 Final Output REQ Deliverable formats, codecs,
masters
Editing Delivery
D129 Archiving SIT Long-term storage of project +
assets
Final Output Preservation
EXTRA DOMAINS BEYOND THE 129 (added for
completeness)
# Domain Status Definition
D130 Grease Pencil / 2D Animation OPT 2D drawing, storyboard, and hybrid 2D-3D inside Blender
D131 Motion Capture ADV MoCap data, retargeting, cleanup
D132 Match Moving ADV Camera tracking for live-action integration
D133 Sound & Music Design SIT Audio for timing, emotion, and final sync
D134 Asset Libraries & Add-ons OPT BlenderKit, add-ons, community systems
D135 Character Base Meshes OPT Base human/creature models as starting points
D136 Render Farm & Distributed Rendering ADV Network rendering, render management
D137 Real-time & Interactive SIT EEVEE real-time pipelines, game/interactive output
D138 Style Guides & Art Direction SIT The visual ruleset that keeps a production coherent
These 138 domains are the L1 nodes. Each chapter below expands a group of domains to L3–L7
depth with node cards, parameter tables, mistake/fix tables, and cross-domain edges.
Beyond the register: the Master Depth Register (Part 2B) maps 25 master-depth chapters (16–
40)  that  expand  these  domains  to  their  extreme  practical  depth  —  exhaustive  choice  libraries,
parameter  encyclopedias,  and  system  masterclasses  (anatomy  &  proportions,  the  materials
encyclopedia, stylized/NPR shading, shape keys & drivers, procedural rigs & mocap, cinematography
&  editing  theory,  lighting  &  mood  encyclopedia,  sound  design,  pipeline  automation,  real-time
pipelines, the optimization masterclass, worldbuilding & storytelling, advanced rigging, animation
depth,  sculpting  depth,  topology  &  retopology  depth,  UV/texture/baking  depth,  hair/fur/feathers
depth, cloth/costume depth, VFX & effects depth, compositing & color depth, environment & terrain
depth, story & storyboarding depth, AI concept-development depth, and Grease Pencil & hybrid 2D
depth). Every domain in this register has a depth-chapter counterpart where its numbers and recipes
live.
PART 2 — MASTER DOMAIN REGISTER
