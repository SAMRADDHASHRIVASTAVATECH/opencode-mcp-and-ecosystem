# Chapter 2 — Blender Foundations & 3D Planning (D13–D16)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 54–56 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 2 — BLENDER FOUNDATIONS & 3D
PLANNING [REQ]
Domains D13–D16. These are the load-bearing walls of every project: knowing the tool, planning the
3D production, organizing the scene, and blocking out.
D13 — BLENDER FUNDAMENTALS [REQ]
DEF: Working knowledge of Blender's interface, navigation, selection, transforms, modes, and data
model  —  the  prerequisite  for  everything  else.  WHY: Every  advanced  system  (rigging,  shaders,
geometry  nodes,  compositing)  is  built  from  these  basics.  Weak  fundamentals  make  every  later
domain 10× slower. HOW (core map): - Interface regions: 3D Viewport, Outliner, Properties editor
(the vertical icon column), Timeline/Dope Sheet, Shader/Node editors, UV editor, etc. Workspaces
(Layout, Modeling, Sculpting, UV Editing, T exture Paint, Shading, Animation, Rendering, Compositing,
Geometry Nodes, Scripting) rearrange editors for the task. - Navigation: MMB orbit, Shift-MMB pan,
scroll  zoom,  Numpad  views  (1/3/7  front/right/top,  0  camera,  5  ortho/persp),  Numpad  .  =  focus
selection, Home = frame all. - Selection & transforms: LMB select (Shift adds), A select-all, B/box,
C/circle; G/R/S with axis locks (X/Y/Z), numeric input, Shift for precise, Ctrl for snapping; right-click or
Alt-G etc. to reset. - Object vs Edit Mode:  Object mode transforms whole objects; Edit mode edits
vertices/edges/faces  (1/2/3  vert/edge/face  selection).  T ab  toggles.  -  The  data  model: Objects
reference data blocks (mesh, material, armature, scene, image). Multiple objects can share one mesh
(linked  duplicates).  Data  blocks  are  Blender's  memory  and  file  units  —  understanding  them  =
understanding linking (D123), drivers, and performance. - Modes: Object, Edit, Sculpt, T exture Paint,
Vertex  Paint,  Weight  Paint,  Pose,  and  editor-specific  modes  (UV,  node,  curve,  grease  pencil).  -
Transform orientations & pivot:  global/local/normal/gimbal/view; pivot point (median, 3D cursor,
individual origins). - Snapping: to grid/vertices/edges/faces/increment; absolute snap; rotation snap.
-  Undo & history:  Ctrl-Z (undo history persists via "Undo" settings; undo  steps can be raised). -
Viewport shading: Solid (with/without color), Material preview, Rendered; overlays, wireframe, X-
ray, matcap, cavity. Key concepts to master early:  local vs world coordinates; 3D cursor; origins
(transform = around origin; armatures rely on it); collections (D15); the Properties panels (Render,
Output, View Layer, Scene, World, Object, Modifiers, Physics, Constraints, Shading, Geometry Nodes).
PARAM/SETTINGS: Preferences:  keymap  (Blender  4.x  default),  theme,  navigation  (turntable  vs
trackball), undo steps, GPU compute; Save Preferences; startup file & preferences are the user's own
"base  pipeline."  MIST: ignoring  the  Outliner  (data  chaos);  editing  origins  accidentally  (broken
transforms); not using snapping; mouse-only workflows (no hotkeys); fighting the tool instead of
learning one mode at a time.  FAIL: corrupted transforms/origins → rigs break, models misalign.
DIAG: check origin display; check object scale (Ctrl-A apply). FIX: Apply all transforms (Ctrl-A) after
modeling;  set  origins  deliberately  (Right-click  →  Set  Origin).  PERF: enable  GPU  subdivision  in
preferences if available; use Solid viewport for heavy scenes; hide/isolate (Numpad /) while editing.
PROD: a strong personal hotkey/workspace setup is a genuine production asset; invest once.
Deep chain — Fundamentals → Data model → Object → Mesh →
Component
Object → data block → mesh → verts/edges/faces → loops → selection → edit transform → normals → UVs →
vertex groups → shape keys Object transform → location/rotation/scale → origin → parenting → local
space → constraints (D53)
CHAPTER 2 — BLENDER FOUNDATIONS & 3D PLANNING [REQ]

D14 — 3D PLANNING [REQ]
DEF: The pre-production math of the 3D build: units/scale, budgets (polygons, memory, render time),
asset/shot breakdown, and the plan of record. WHY: Blender has no "right" unit; your project defines
scale. Wrong scale breaks physics (gravity, cloth, fluids), sims, and lighting falloff. Budgets prevent
the "one huge scene" death spiral. HOW: 1. Units & scale: Scene Properties → Unit System (Metric/
Imperial); set Unit Scale (1 m default). Decide the master unit (meters for characters; centimeters for
jewelry;  kilometers  for  worlds).  Use  real-world  sizes —  Blender's  physics  and  lights  behave
realistically at real scale. A "1 unit = 1 m" character: ~1.7–1.8 m tall. 2. Scene scale planning: for
large worlds, keep the  hero scene small (the shot area) and put distant stuff in separate scenes/
linked files. 3.  Budgets (write them down):  per-asset polygon budget (characters: 20k–200k for
film, 10k–100k for realtime); texture budget (2k/4k/8k per asset class); render time budget per frame;
memory budget (viewport). 4. Shot/asset breakdown: from the animatic: table of shots × assets
needed (characters, sets, props, fx) → build order (what must exist first). 5.  Milestones: blockout
date, modeling lock, rig lock, animation lock, sim lock, final render start, final delivery. Lock dates
prevent infinite polish. PARAM: unit system & scale; fps; render resolution & aspect (1920×1080,
3840×2160,  aspect  1.78,  2.39  for  cinemascope);  polygon  budgets;  texture  budgets;  sim  cache
budgets; render budget per frame; deadlines. MIST: mixing unit scales (tiny character in giant world
→ physics chaos); no budgets (scene dies in the viewport); no lock dates (polish forever).  DIAG:
physics/sim behaving weirdly? Check scale (a 1-unit cube "1 m" vs "1 cm" changes cloth/fluid results
massively). FIX: standardize on meters; rebuild mis-scaled assets early; keep a SCALE MASTER — a
1 m cube / reference character always present in scenes. EDGES: → D16 blockout, → D125 pipeline,
→ D126 performance.
D15 — SCENE ORGANIZATION [REQ]
DEF: The  rules  for  naming,  grouping,  and  structuring  scenes/collections  so  a  production  stays
navigable and linkable. WHY: A 500-object scene without structure is unworkable; with structure it is
searchable, linkable, and reusable. Organization is the difference between "production" and "chaos."
HOW: 1.  Collections = the folder system.  Group by  function:  Assets/Characters/Hero ,  Assets/
Props/MainStreet ,  Sets/City/RainDistrict ,  Fx/Rain ,  Lights ,  Cameras ,  Rigs ,  Scratch .  Nested
collections  allowed.  2.  Naming  conventions  (D123): assetType_name_variant_##  e.g.,
CHR_HeroKnight_01 , SET_CityMain_Street_02 , PRP_Lantern_Wall_01 , LT_Key_01 , CAM_Shot03A . Use a name
delimiter system  and  a  documented  legend.  Blender  4.x  supports  renaming  with  find/replace
(search all data blocks). 3. Scenes & view layers: a Blender file can hold many scenes; each scene
can  have  multiple  view  layers (render  different  object  sets  per  layer  —  e.g.,  foreground  vs
background). Use scenes for shots (one scene per shot, linked assets — D123) or a master scene +
shot  scenes.  4.  Outliner  usage: filter  by  type,  search,  isolation  (eye  icon),  viewport  visibility
(monitor icon), holdout (X-ray icon = disable render), collections with color tags. 5. Linked assets vs
local: production-consistent assets live in their own .blend files and are linked (File → Link / Append,
or the Asset Browser) into shot scenes (see D122/D123). Edit once, update everywhere (library
overrides for per-shot tweaks). 6. Orphan cleanup: File → Clean Up → Recursive Unused Data-Blocks
keeps files lean. PARAM: naming legend; collection hierarchy; scene-per-shot policy; asset-file policy
(one asset per file vs per group); render layers policy.  MIST: everything in one collection named
"Collection"; no naming legend (case/code drift); building all shots in one giant scene (viewport
death, no parallel work); duplicating the same character mesh in every shot file instead of linking.
FAIL: broken links after renames (renaming a linked file breaks it — version/rename carefully);
missing objects in render (hidden in a view layer).  FIX: before render, audit: view layer contents,
CHAPTER 2 — BLENDER FOUNDATIONS & 3D PLANNING [REQ]

collection visibility, linked library path integrity (File → External Data → Report Missing Files). EDGES:
→ D122 asset management, → D123 file organization, → D124 versioning, → D126 performance.
D16 — BLOCKOUT [REQ]
DEF: Every asset exists as a low-detail proxy at final scale and position; the whole scene is laid out in
volume,  not  detail.  WHY: Validates  scale,  proportion,  composition,  and  camera  in  3D  before
expensive modeling. Catches the most expensive error class (scale/space) at the cheapest time.
HOW: 1.  Stand-ins: use  primitives  (cubes,  cylinders,  UV  spheres)  or  blocky  low-poly  meshes;
characters as scaled block-men (head cube + torso + limbs) at true proportions from the character
sheet; props as volume boxes; sets as floor/volume masses. 2. Reference planes: import character
sheets and set photos as background images/planes to check proportions in 3D. 3. Layout cameras:
place shot cameras from the animatic; check framing against stand-ins; adjust staging (this IS previs,
D11). 4.  Scale check: walk a "blockman" through the set; check door heights, stair pitches, prop
reachability. 5.  Approve: the blockout is the  contract for modeling ; render turntables/screenshots
and  get  sign-off.  PARAM: stand-in  fidelity  (keep  it  low  —  detail  here  is  waste);  world  scale
correctness; camera framing per shot.  MIST: detailing the blockout (waste); skipping scale check
(character can't fit through the door — a classic); approving before cameras are set. DIAG: if a shot
composition fails in blockout it will fail later 100× more expensively. FIX: re-stage now. EDGES: →
D11 previs, → D19 modeling, → D79 environment, → D102 camera.
Deep chain — Blockout → Stand-in → Proxy → Final
Blockout proxy → scale validation → camera validation → composition validation → approval gate → final
modeling begins
CHAPTER 2 — BLENDER FOUNDATIONS & 3D PLANNING [REQ]
