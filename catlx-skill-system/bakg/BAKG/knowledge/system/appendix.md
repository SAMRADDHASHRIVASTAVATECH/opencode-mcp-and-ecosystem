# Appendix — Glossary, Hotkeys, Templates, Checklists, Extension Points

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 132–135 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

APPENDIX — GLOSSARY, HOTKEYS,
TEMPLATES, CHECKLISTS, EXTENSION POINTS
A.1 GLOSSARY (the graph's vocabulary, 120 terms)
3-point lighting — key + fill + rim system (D108). 180° rule — camera stays on one side of the
action line (D103). AOV — arbitrary output variable; custom render pass (D116). AgX — Blender 4.x
default  view  transform;  filmic  HDR  rolloff  (D112).  Albedo —  base  color  without  lighting  (D26).
Animatic —  timed  storyboard  cut  to  audio  (D10).  Anticipation —  wind-up  before  action  (D65).
Armature — Blender's skeleton object (D48).  Asset Browser — library for reusable assets (D84/
D122). BBone (Bendy Bone) — bone with segments that curves (D50). Blendshape / Shape key
— stored mesh deformation (D59/D60).  Blocking — stepped key pose stage (D64).  Blockout —
proxy  geometry  layout  (D16).  Boolean —  add/subtract  mesh  operation  (D18).  Bounce —  light
reflection  limit  in  render  (D114).  BVH —  ray  acceleration  structure  (D114).  Cache —  stored
simulation results (D88).  Cell Fracture — built-in fracture add-on (D97).  Child Of  — constraint;
animatable parenting (D53). Cloth — fabric simulation modifier (D39/D91). Collection — grouping
system (D15).  Color management  — view transform/exposure pipeline (D112).  Compositor —
node-based  post-processing  (D117).  Constraint —  rule  linking  objects/bones  (D53).  Contact
shadow — darkening where objects touch (D109).  Control rig — animator-facing layer of the rig
(D48/D55).  Corrective shape  — pose-fix blendshape (D59).  Cryptomatte — automatic object/
material masks (D115). Custom shape — controller visual (D55). Cycles — raytraced render engine
(D113). Deform bone — bone that moves mesh (D48/D50). Denoise — noise removal post-process
(D114).  Displacement — geometric offset from a map (D26/D80).  Dope Sheet  — keyframe list
(D64). Driver — value computed from another value (D54). Dyntopo — dynamic topology sculpting
(D22).  EEVEE — real-time render engine (D113).  Edge flow  — loop direction in topology (D24).
Emissive — self-luminous material (D30). Envelope — bone influence without weights (D56). EXR
— OpenEXR float image format (D112/D115).  F-curve — animation curve in Graph Editor (D64).
Falloff — brush/force influence curve (D22/D88).  Field — geometry-nodes attribute computation
(D85).  FK — forward kinematics (D52).  Force field — physics influence (wind, turbulence) (D88).
Fracture — pre-breaking geometry for destruction (D97). Fresnel — view-angle reflectance (edge
glow) (D101). Gimbal lock — rotation axis collapse (D49). GN (Geometry Nodes)  — node-based
procedural system (D85). Graph Editor — curve editing for animation (D64). Grooming — styling
hair/fur  guides  (D46).  HDRI —  high-dynamic-range  environment  image  (D108).  Hair curves  —
modern strand-based hair (D43). Holdout — hide from render (D15). IK — inverse kinematics (D51).
Instancing — repeated objects without copies (D85).  IOR — index of refraction (D30).  Island —
connected UV region (D25). Library override — local edits to linked data (D122). Light linking —
light affects chosen objects (D108).  LOD — level of detail variants (D24).  Mantaflow — Blender's
fluid/smoke/fire  solver  (D93/D95/D96).  Mask —  value  region  selection  (D26/D29).  Matcap —
viewport  material  capture  shading  (D13).  Mist  pass —  camera-distance  gradient  (D110/D115).
Modifier — non-destructive geometry operation (D18/D24).  Multires — multiresolution sculpting
(D22). NLA — non-linear animation strips (D64). Node group — reusable node subgraph (D29/D86).
Non-manifold — geometry error (D24). Normal map — fake-relief texture (D26). Ocean modifier
— wave displacement generator (D94). Overlap — parts moving at different times (D65/D77). PBR
— physically-based rendering (D30).  Pinning — fixed cloth vertices (D38/D39).  Pole — 3/5-edge
topology junction (D24).  Pole vector/target  — IK bend-direction control (D51).  Pose library  —
stored poses (D64). Principled BSDF — universal PBR shader (D30). Rig — control system (D48).
Rigid body — hard-object physics (D89). Roll — bone's axial orientation (D49). Saccade — quick
eye jump (D63). Seam — UV cut (D25). Sewing spring — cloth seam force (D38). Shape language
APPENDIX — GLOSSARY, HOTKEYS, TEMPLATES, CHECKLISTS, EXTENSION POINTS

— design shapes conveying personality (D04). Shrinkwrap — surface-conforming projection (D18/
D23).  Silhouette — outline readability (D04).  Skinning — mesh-to-skeleton binding (D57).  Soft
body — deformable-object physics (D90). Spacing — distribution of motion over time (D65). Spline
— smooth interpolation (D64).  SSS — subsurface scattering (D32).  Subdiv — subdivision surface
(D17/D24).  Texel  density —  texture  resolution  per  surface  (D25).  Topology —  edge/vertex
arrangement (D24). Transmission — light passing through (D30/D33). UDIM — multi-tile UVs (D25).
UV — texture coordinates (D25). Vertex group — weighted vertex set (D56). View layer — render
subset of a scene (D15/D115).  Viseme — mouth shape for a phoneme (D62).  Voxel remesh —
uniform-density remeshing (D22). Weights — vertex-bone influence values (D56). Z-buffer/Z-pass
— depth map (D115).
A.2 ESSENTIAL BLENDER HOTKEYS (4.x defaults)
Global: T ab (modes) · Shift-A (add) · M (move to collection) · N (sidebar) · F3 (search menu — the #1
power  key)  ·  Ctrl-S  (save)  ·  Ctrl-Alt-S  (save  as)  ·  F2  (rename  data  block)  ·  Ctrl-Shift-S  (save
incremental with version). Viewport: MMB orbit · Shift-MMB pan · Scroll zoom · Numpad 1/3/7 (views)
· Numpad 0 (camera) · Numpad 5 (ortho) · Numpad . (focus) · Home (frame all) · / (local view) · Z
(shading pie) · Shift-Z (render preview). Object/Edit: G/R/S (transform) · Shift-D (duplicate) · Alt-D
(linked duplicate) · X (delete) · E (extrude) · I (inset) · K (knife) · Ctrl-R (loop cut) · O (proportional edit)
· Ctrl-A (apply) · Shift-N (recalculate normals) · M (merge) · P (separate) · Ctrl-J (join) · Alt-M (merge by
distance).  Sculpt: F (brush size) · Shift-F (strength) · Ctrl (invert) · Shift (smooth).  Animation: I
(insert keyframe) · Alt-I (delete keyframe) · Shift-E (set keyframe type) · T (interpolation menu in
Graph Editor) · V (handle type) · N (keying panel). Pose Mode: W (flip) · Shift-W (copy/clear pose) ·
Ctrl-C/Ctrl-V (copy/paste pose) · Alt-G/R/S (clear transforms). Node editors: Ctrl-Shift (drag node) ·
F12 (render). UV: U (unwrap menu) · P (pin) · Alt-M (merge).
A.3 THE NODE CARD TEMPLATE (for extending the graph)
Use this template when adding any new node to the graph (the graph is designed to be extended):
### [NODE NAME]  [STATUS: REQ/OPT/SIT/ADV]
**DEF:** one-sentence definition
**WHY:** why it exists
**HOW:** mechanism (2–4 lines)
**USE:** when to use / **AVOID:** when not to
**OPT:** available options
**ALT:** alternatives
**PRO / CON:** advantages / disadvantages
**PRE:** prerequisites · **DEP:** dependencies
**AFF:** what it affects · **AFF-BY:** what affects it
**PARAM:** key parameters/settings
**FLOW:** workflow steps
**MIST:** common mistakes
**FAIL:** failure modes · **DIAG:** how to diagnose · **FIX:** fixes
**PERF:** optimization
**BEG / INT / ADV:** level knowledge
**PROD:** production considerations
**EDGES:** related nodes (inbound/outbound)
APPENDIX — GLOSSARY, HOTKEYS, TEMPLATES, CHECKLISTS, EXTENSION POINTS

A.4 MASTER CHECKLIST (print this for any production)
PRE-PRODUCTION (D01–D12): logline · world bible · character sheets · creature specs · reference
boards · storyboard · animatic (locked!) · previs · frame rate/resolution/engine/naming committed.
PLANNING (D13–D16): budgets written · scale master · collections/naming set · blockout approved.
MODELING (D17–D24): proportions locked · topology plan · bend tests · LOD plan. LOOKDEV (D25–
D36): UV plan · maps complete · materials built · hero close-up approved. COSTUME/GROOM (D37–
D47): garment plan · sim budget · groom approved in motion.  RIG (D48–D63): skeleton named/
oriented · controls shaped · sign-off test passed (D60 chapter). ANIMATION (D64–D78): references ·
blocking review · spline clean · shot sign-off (D78 chapter).  WORLD (D79–D86): hero/background
split · set dressing · procedural systems built. SIM/VFX (D87–D101): caches baked · effects designed
per beat · integration tested. CAMERA/LIGHT (D102–D111): shot design per beat · lighting continuity
· atmosphere.  RENDER (D112–D116): passes set · denoise · EXR output · test frames approved.
COMP/COLOR (D117–D119): master grade · scopes · grain · shot matching. EDIT/OUTPUT (D120–
D129): locked edit · master encode · loudness · QC watch · archive. SCOPE AUDIT (Part 0, AC-1…
AC-6): breadth complete · depth to L3–L7 · variations enumerated · connectivity verified · Ultimate
T est passed on the project's idea · no topic omitted for brevity.
A.5 EXTENSION POINTS (how to grow this graph)
The binding rule (Non-Negotiable Scope Requirement, Part 0): every extension must add
depth or breadth ; none may shorten or summarize existing knowledge. Completeness over
brevity applies to every extension, exactly as to every revision.
New domains: use the template (A.3) and register them in the D-numbering (D139+).
New depth chapters: continue the numbering from chapter 29 (Part 2B); every base domain
that lacks a depth-chapter counterpart is a candidate (the register is never closed).
New creatures/anatomy: add to D05's spec library (locomotion class, surface, senses) and to
Depth Chapter 16's libraries — every original organism is a new leaf on existing branches.
New styles: extend the style matrix (3.8) and the NPR systems (Depth Chapter 18) with new
rows (pixel-art, 2.5D, watercolor…).
New Blender versions: update version-specific notes (4.x → future) in D13/D22/D43/D85/D113
and the version notes (A.6).
New add-ons/tools: add to D134 with a note on which graph node they accelerate.
Per-project checklists: fork A.4 per project type (Part 1 table) — the graph stays stable; the
checklists adapt.
Scope audit (AC-1…AC-6): before declaring any revision complete, re-run the acceptance
criteria — breadth, depth, variation, connectivity, the Ultimate T est, and the "no omission for
brevity" rule.
A.6 VERSION NOTES (Blender 4.x features referenced)
Bone Collections replaced bone groups (D49); Library Overrides replace proxies (D122).
EEVEE Next default in 4.2+ — raytracing support (D113).
Grease Pencil 3 rewrite in 4.3 (D130).
1. 
2. 
3. 
4. 
5. 
6. 
7. 
8. 
• 
• 
• 
APPENDIX — GLOSSARY, HOTKEYS, TEMPLATES, CHECKLISTS, EXTENSION POINTS

AgX default view transform (D112).
Curves-based hair standard; legacy particle hair still available (D43).
Cryptomatte native (D115); Light Linking in 4.x (D108).
Geometry Nodes: simulation zones (4.x) for per-frame stateful setups (D85/D99).
Feature names/shortcuts may shift between releases; the concepts in this graph are version-stable.
• 
• 
• 
• 
APPENDIX — GLOSSARY, HOTKEYS, TEMPLATES, CHECKLISTS, EXTENSION POINTS
