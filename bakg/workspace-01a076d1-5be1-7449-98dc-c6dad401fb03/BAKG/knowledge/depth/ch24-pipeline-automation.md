# Depth Chapter 24 — Pipeline Automation: Python, USD, Export, Render Farms

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 170–172 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 24 — PIPELINE AUTOMATION:
PYTHON, USD, EXPORT, RENDER FARMS
Expands  D122–D125,  D136,  D128.  The  meta-tools  of  production:  scripting  the  repetitive,
standardizing  interchange,  and  distributing  the  heavy  lifting.  Automation  is  what  separates  "a
hobbyist with Blender" from "a pipeline."
24.1 THE BLENDER PYTHON API (bpy) — ESSENTIALS
Why: everything in Blender is scriptable — naming, importing, exporting, reports, render queues,
asset audits. A 30-line script replaces hours of clickwork, and scripts are repeatable (the same quality
every time).
The data model (learn the map):  - bpy.context  — current state (active object, scene, view layer).
- bpy.data  — all data blocks (objects, meshes, materials, armatures, actions, scenes). - bpy.ops  —
operators  (do  what  buttons  do:  bpy.ops.object.select_all(action='SELECT') ).  -  bpy.types  —  class
definitions  (when  writing  add-ons).  -  Property  access:  obj.location.x ,  mat.use_nodes , 
mesh.vertices[i].co ;  collections:  bpy.data.collections ,  obj.users_collection .  -  Execute  in  the
Scripting workspace or T ext Editor → Run Script.
Ten script recipes (copy-adapt-run):  1. Batch rename: iterate bpy.data.objects , apply naming
regex  (fix  "Cube.001"  chaos).  2.  Name validation:  report  objects  violating  the  naming  legend
(D123) — run before handoffs. 3. Batch import: loop a folder of FBX/glTF/OBJ, place into collections,
set import options consistently. 4. Batch export: export selected/all assets to glTF/USD with fixed
settings + output path — the "export button" of the pipeline. 5.  Texture audit: list all materials,
their image nodes, and missing file paths (catches broken links before render, D123). 6.  Orphan
cleaner: report/delete unused data blocks (D15) — safe version with a report first. 7.  Render
queue: iterate scenes/shots, set output paths, render each (frame ranges, formats) — a mini render
farm in one script (D121). 8. Asset cataloger: mark assets, assign catalogs, set metadata from a
CSV (D84/D122). 9. Collection sweeper: move all objects into properly named collections from a
naming convention table. 10. Cache report: list sim caches and their disk sizes (D88/D124) — finds
the 40 GB surprise.
Safety rules:  run  report-only first; work on copies; use  bpy.ops  with context overrides carefully;
wrap  destructive  ops  with  undo  (bpy.ops.ed.undo_push);  document  scripts  in  the  pipeline  docs
(D123).
DEPTH CHAPTER 24 — PIPELINE AUTOMATION: PYTHON, USD, EXPORT, RENDER FARMS

24.2 ADD-ON STRUCTURE (the 30-line skeleton)
bl_info = {"name": "My Pipeline Tool", "blender": (4, 0, 0), "category": "Pipeline"}
import bpy
class MyOperator(bpy.types.Operator):
    bl_idname = "pipeline.do_thing"; bl_label = "Do Thing"
    def execute(self, context):
        # ... work ...
        return {"FINISHED"}
def menu_func(self, context):
    self.layout.operator("pipeline.do_thing")
def register():
    bpy.utils.register_class(MyOperator)
    bpy.types.VIEW3D_MT_object.append(menu_func)
def unregister():
    bpy.utils.unregister_class(MyOperator)
    bpy.types.VIEW3D_MT_object.remove(menu_func)
if __name__ == "__main__": register()
Install as .zip; keep add-ons in the project's documented list (D129 — archiving needs the add-on
manifest!).
24.3 USD — THE UNIVERSAL INTERCHANGE (Blender 4.x)
What: Pixar's USD (Universal Scene Description) — a scene-graph format for interchange between
DCCs  (Blender,  Maya,  Houdini,  Katana,  game  engines).  Why: USD  preserves  instancing,  layers,
variants, and relationships  — not just meshes. For studios and complex pipelines it beats FBX/OBJ.
Blender support (4.x):  USD export/import (File → Export/Import → Universal Scene Description):
meshes,  materials  (via  USD  Preview  Surface),  cameras,  lights,  animation  (limited),  instancing,
variants (selectable model variants — e.g., "armor on/off"),  purpose (render vs guide geometry).
Workflow: author in Blender → export USD → import into engine/other DCC → edit → round-trip; use
USD layers for non-destructive variant sets (e.g., a creature's fur density variants). When to use:
cross-tool  teams,  game  engines,  variant-heavy  productions,  studio  pipelines.  When  not: solo
Blender-only work — .blend linking (D122) is simpler and richer.
24.4 glTF, FBX, OBJ (the interchange quick-reference)
Format Best for Preserves Watch out for
glTF 2.0 (GLB/
glTF)
web, engines, AR/VR,
real-time
PBR materials, skeletons,
animations, cameras
No NURBS/custom nodes; limited
shaders
FBX Unity/Unreal, Maya
interchange
skeletons, animation, blendshapes Units + axis (set to match!),
scale, tangents
OBJ simple geometry
interchange
mesh + UV + material refs No animation, no skeleton, no
PBR (Mtl only)
USD see 24.3 most complete version/plugin compatibility
DEPTH CHAPTER 24 — PIPELINE AUTOMATION: PYTHON, USD, EXPORT, RENDER FARMS

Export discipline: set scale (cm/m per target — engines differ!), axis (Y-up vs Z-up — Blender is Z-
up, many engines Y-up; exporters handle it —  verify by importing into the target),  forward axis, 
tangent space, and animation bake (bake constraints/drivers before export — engines don't run
Blender drivers!). T est-import a character into the target engine before building 50 assets to it.
24.5 RENDER FARMS & DISTRIBUTED RENDERING (D136)
Local farm: multiple machines render different frames (Blender's built-in network render (File
→ Render → Start Render Slave) or render-management add-ons); split the frame range across
machines.
Cloud render: services (Sheepit — free distributed; paid: RenderStreet, Flamenco (Blender
Studio's open tool)); upload project, farm renders frames, download EXRs.
Batch discipline: render to EXR per frame (crash-safe — D112); a failed frame = re-render one
frame, not the shot; collect a render log (frame, time, status) for QC (D127).
Flamenco (Blender's own): self-hosted render farm manager — the professional open-source
choice for a studio.
Economics: always render tests first (low res, few frames) → then final. Farms render what you
give them — an untested scene costs farm-hours.
24.6 VERSION CONTROL FOR BLENDER PROJECTS
File-based (standard): the versioning system of D124 (save-as _v01, _v02) + backups; works
everywhere, zero setup.
Git + LFS (advanced): track .blend files with Git LFS (large file storage); works for text/config/
scripts great; .blend diffs are binary (no merge) — treat as "save versions in git," not "merge."
The blend-file reality: Blender files are single binary blobs — the pipeline (linked assets, D122)
is what makes them composable, not the version system.
24.7 THE AUTOMATION CHECKLIST (what to script first)
Naming validation script (run at every handoff gate, D127).
T exture/path audit script (before every render batch).
Batch export (glTF/USD) with verified settings.
Render queue for shot scenes (D121).
Asset cataloger (D84/D122).
Cache/disk report (D124). Write them once, run them forever — that is the "pipeline."
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
6. 
DEPTH CHAPTER 24 — PIPELINE AUTOMATION: PYTHON, USD, EXPORT, RENDER FARMS
