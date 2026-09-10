# Chapter 15 — Editing, Pipeline, Management, QC, Final Output (D120–D129)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 111–115 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 15 — EDITING, PRODUCTION
PIPELINE, MANAGEMENT, QC, FINAL OUTPUT
Domains D120–D129. The operations layer: cutting the film, organizing the production, keeping files
safe, checking quality, and delivering masters.
D120 — EDITING [REQ]
DEF: Cutting shots together in sequence: pacing, rhythm, transitions, and sound sync — the final
storytelling pass. WHY: Editing is the last writer: the same footage cut differently changes the story,
the pacing, the jokes, the emotion. The edit is where the animatic's promise (D10) becomes the film.
HOW (Blender's Video Sequencer — VSE):  import rendered frames/EXR (as image strips or
rendered  video),  audio  strips;  cut  (K),  ripple,  trim;  transitions (crossfade,  dip-to-black  —  use
sparingly); timing adjustments (a shot 4 frames shorter = snappier joke); sync to audio  (D133);
nested sequences (a sequence inside a sequence for organization); grade after the edit (D119 —
never  grade  per-shot  before  the  cut  is  final).  Editing principles:  cut  on  action/motion;  match
eyelines (D103); the 180° rule in the cut; rhythm follows the music/beat (D133); hold the reaction
shot (reactions are where comedy/emotion live); "show, don't tell" — cut out the setup, keep the
payoff;  less  is  more —  the  best  edit  removes  frames.  PARAM: frame  rate  (consistent,  D10);
resolution;  timeline  structure  (scene/chapter/shot);  audio  sync  points;  transitions.  MIST: editing
before all shots are rendered (lock the edit early, then render to the locked cut — re-cutting after
render = wasted renders); no audio in the edit (timing drifts); over-transitions.  EDGES: → D10, →
D103, → D119 (grade after edit), → D128 (encode from the edit).
D121 — SHOT MANAGEMENT [SIT]
DEF: The system for tracking shots through production: naming, statuses, ownership, render queue.
WHY: A  film  is  50+  shots;  without  tracking,  shots  get  lost,  double-worked,  or  forgotten.  Shot
management  is  the  production  state  machine.  HOW: per-shot  record:  name  (from  the  naming
convention: S01_Shot012_ ), status (blocked → anim → sim → light → render → comp → done), assigned
person, notes, version (D124). Track in a spreadsheet (or a shot-tracker; Blender add-ons exist) —
simple and effective; plus per-shot .blend files (D123). Render queue: render shots in dependency
order (comp needs renders; shots needing the same assets first); use the Render Queue add-ons or
render  in  batches;  monitor  for  failures  (D127).  PARAM: naming;  status  list;  ownership;  notes;
deadline; render order. MIST: no status system ("it's almost done" forever); shot names that collide;
rendering out of dependency order. EDGES: → D123, → D124, → D125.
D122 — ASSET MANAGEMENT [SIT]
DEF: The system for storing, versioning, linking, and reusing assets: the Asset Browser, libraries, and
linking discipline. WHY: Assets are built once and used in many shots; management decides whether
reuse is a  superpower (D84) or a mess (duplicated, unversioned, broken links).  HOW: -  Asset
libraries (Preferences → File Paths): folders of asset .blends (characters, props, materials, HDRI, node
groups, poses, brushes) with catalogs. - Mark as Asset + catalog metadata  in each asset file. -
CHAPTER 15 — EDITING, PRODUCTION PIPELINE, MANAGEMENT, QC, FINAL OUTPUT

Linking vs appending: link assets you want to stay in sync (edit once → all shots update); append
(copy) when you need local, un-synced copies;  library overrides (4.x) for per-instance tweaks of
linked data — the professional "instance with local changes" system. -  Dependency hygiene: an
asset file should reference only its own textures/dependencies (D123 file rules); missing-link audits
(File → External Data → Report Missing Files). PARAM: library folders; catalog naming; link/append
policy per asset type; versioning (D124). MIST: appending everything (no sync — fixing a character
means touching 50 files); renaming/moving files (breaks links); assets with external texture paths
that move (broken renders). EDGES: → D84, → D123, → D124.
D123 — FILE ORGANIZATION [REQ]
DEF: The folder + naming + file-type architecture of the whole project. WHY: On day 40, you must
find the character's final rig, the rain cache, the locked shot list — instantly. Organization is the
difference between finishing and abandoning. The standard project tree (adopt and adapt):
project/
  00_docs/          (story, world bible, sheets, shot list, naming legend, budgets)
  01_reference/     (D07 boards, motion refs)
  02_concept/       (2D/AI concepts, sheets)
  03_storyboard/    (boards, animatic)
  04_assets/        (per-asset: characters/, props/, sets/, fx/)
      characters/hero/
         hero_v01.blend   (model+sculpt)
         hero_rig_v03.blend
         textures/  (hero_face_basecolor.png ...)
         caches/    (cloth, hair)
  05_shots/         (per-shot .blend: S01_012.blend — linked assets)
  06_render/        (S01_012/exr/ …)
  07_comp/          (comp .blend or node files)
  08_edit/          (VSE project, final sequence)
  09_deliver/       (final masters)
  cache/            (sim caches, render temps)
  backup/           (snapshots, zips)
Naming  conventions  (write  them  down!):TYPE_Asset_Detail_V##  —  e.g.,  CHR_Hero_v03.blend , 
TEX_Hero_Face_BaseColor_4k.png , SHOT_S01_012_v02.blend , SIM_S01_012_Cloak_Cloth ; version suffix _v01 , 
_v02 …  (D124).  No spaces  in  file  names;  use  _  or  - ;  keep  lowercase  for  consistency  (case-
sensitive  systems!).  File  rules: one  character's  work  =  its  own  .blend(s)  (model  file,  rig  file
separate); shots link assets (D122); textures live in the asset's textures/ folder (pack or absolute-
relative paths — use //  relative paths!); caches to disk in cache/ (D88); every .blend self-contained
via  File → External Data → Pack  or verified relative paths.  PARAM: folder template; naming
legend; relative path rule ( // ); per-file content rules. MIST: "final_final_v3_really.blend" (no system);
all assets in one file; spaces/uppercase chaos; absolute paths to a machine-specific folder; textures
packed nowhere. EDGES: → D124, → D122, → D121, → D125.
D124 — VERSIONING [REQ]
DEF: Saving iterations so any state can be recovered: file versions, backups, and snapshots. WHY:
Every artist has "the save that saved the project." Versioning is insurance against corruption, wrong
directions, and lost work; it also makes comparison possible (v3 vs v7). HOW: - File versions: save
with _v01 , _v02 … at milestones (start of day, end of day, before a risky operation); Blender's Save
CHAPTER 15 — EDITING, PRODUCTION PIPELINE, MANAGEMENT, QC, FINAL OUTPUT

Versions preference auto-keeps N backups (1–32; set 5+) — automatic insurance. -  Incremental
saves: for long sessions, save as new version every hour or at checkpoints (make it a habit; the
"save early, save often, save as" rule). - Autosave: Blender autosaves to a temp folder; recover via
File → Recover (Auto Save) — know this before you need it. -  Snapshot/backup: nightly/zip the
project (or use a sync service); keep off-machine backups (cloud/drive) — machines die. - Version
metadata: a versions.md  or the naming convention encodes what changed (v02 = "fixed weights,"
v03  =  "new  facial  rig").  MIST: overwriting  the  same  file  forever;  saving  versions  with  no
documentation ("which v was the good one?"); no off-machine backup; deleting "old" versions (keep
them until the film is done!). EDGES: → D123, → D129 (archive = final version).
D125 — PRODUCTION PIPELINE [REQ]
DEF: The ordered flow of work and dependencies across the whole production: who/what/when, and
what gates quality (D127). WHY: The pipeline is the graph in action: every node's dependency (Part
3) defines legal order. A pipeline is a promise — "this stage's output feeds that stage" — and
respecting it is what finishes films.  The dependency spine (recap Part 1):  story → boards →
animatic → asset list → blockout → model → UV → texture → rig → anim → sim → light → render →
comp → edit → grade → master. Parallel tracks: environment/lighting track; VFX track; each with its
own dependencies on the character/animation track.  Gates (checkpoints with sign-off, D127):
blockout approval; modeling lock; rig sign-off (D60 chapter checklist); animation shot sign-off (D78
chapter checklist); sim lock; lookdev approval; final render approval. Roles (even solo, act like a
studio): pre-production lead, modeler, rigger, animator, lookdev, lighter, comp, editor — as passes
you do in sequence, with reviews between. PARAM: stage order; gates; review cadence; dependency
map (Part 3); contingency (what if a stage fails — D127 fixes).  MIST: skipping gates ("we'll fix in
comp"); parallel work on un-locked dependencies (animating before rig sign-off); no review culture.
EDGES: → Part 1, → D127, → D121.
D126 — PERFORMANCE OPTIMIZATION [REQ]
DEF: Keeping the viewport and workflow  fast: scene complexity management, display settings, and
iteration speed. WHY: A laggy viewport destroys iteration speed and morale; performance is a design
discipline (budgets, D14) applied continuously. The levers (in order):  1. Budgets (D14): polygon/
texture/instance budgets per asset class — the root fix. 2. LOD & proxies (D24):  far objects = low
LOD; viewport proxies for characters. 3.  Instancing (D85):  never duplicate, always instance. 4.
Viewport settings: viewport shading → Solid (fastest), disable overlays, viewport resolution scale,
limit  GPU  texture  size;  Simplify (Render/Viewport  properties:  max  subdiv,  texture  size,  child
particles) — the global perf switch. 5. Visibility discipline: collections hidden/isolated (D15); only
what's needed visible; local view (Numpad /) to focus. 6. Cache & bake heavy data (D88/D47/D39);
disable sims when not needed (playback). 7. File hygiene: clean unused data blocks (D15); keep
shot  files  small  (linked  assets,  D122).  8.  Hardware: GPU  compute  for  viewport  (Preferences),
dedicated  graphics  settings.  PARAM: simplify  settings;  display  limits;  texture  cache;  memory
monitoring. MIST: building the whole film in one scene (viewport death); 8k textures on everything;
full hair sims in the viewport; no simplify. DIAG: when slow, profile what's slow: geometry? textures?
sims? volumes? — fix the layer, not the symptom. EDGES: → D114 (render perf), → D15, → D14, →
D85.
CHAPTER 15 — EDITING, PRODUCTION PIPELINE, MANAGEMENT, QC, FINAL OUTPUT

D127 — QUALITY CONTROL [REQ]
DEF: The review + error-catching system: technical checks and creative reviews at every gate, and
the final full-film check. WHY: Errors found at the end are catastrophic (re-renders, re-sims); errors
caught at gates cost minutes. QC is  scheduled looking — the most underrated production system.
The QC layers:  1.  Technical checks per asset/shot:  non-manifold geometry; missing textures
(D123 audit); missing weights; scale errors; broken links; sim artifacts; render errors (black frames,
noise, z-fighting); audio sync. 2. Creative reviews at gates: blockout review, modeling lock review,
rig sign-off, animation dailies (D78 checklist), lookdev approval, lighting review, comp review — with
specific questions per gate (Part 1 checklists). 3. The final QC pass (the "QC watch"):  watch the
whole  film  at  final  quality,  in  order,  with  sound:  check  frame  errors  (flicker,  missing  frames),
continuity (D103), color consistency across shots (D119), audio/video sync, credits/intro/outro, and
emotional flow (the story still works). The review method:  "dailies" — regular short reviews with
the checklist; take  notes (shot number + issue + owner + due); fix, re-review;  never ship the
version with known errors  ("we'll fix it later" is the classic disaster).  Common render errors
checklist: black frames (failed render — re-render); noise (D114); z-fighting (coincident surfaces —
offset); light leaks; motion blur artifacts; AO missing (D115); color mismatch between shots (D119).
PARAM: gate list; checklist per gate; issue tracker; final QC checklist.  MIST: no gates; no issue
notes; final QC skipped ("we're out of time"); fixing errors by re-rendering the whole shot instead of
the failing frames. EDGES: → Part 1 gates, → D125, → D121.
D128 — FINAL OUTPUT [REQ]
DEF: Delivering  the  film:  master  formats,  codecs,  resolution/frame-rate  specs,  and  distribution
versions. WHY: The film isn't finished until it plays correctly everywhere it's supposed to play. Format
choices affect quality and compatibility. HOW: 1. Render masters: final frames as EXR (D112) →
edit (D120) →  encode. 2.  Encode from the edit/comp:  FFmpeg (Blender VSE render or ffmpeg
CLI): - Delivery master: ProRes 422 HQ / DNxHR (broadcast) or H.264/H.265 4:2:0 8-bit (web) — or
export an image sequence from the VSE and encode externally for max control. - Codec sanity:
H.264 (web), H.265/HEVC (smaller, newer), ProRes/DNx (edit-grade), AV1 (newest, web). - Bitrate:
20–50 Mbps for 1080p web; higher for 4K; CRF 18–23 for quality-based encoding. -  Frame rate:
match the project (D10) — 24/25/30/60; don't resample unless necessary. 3. Audio: mix (D133) →
AAC (web) or PCM (master); loudness normalization (-14 LUFS web standard) — check! 4. Versions:
distribution versions (web 1080p, social 9:16, trailer cut) from the master — never re-render for
formats; transcode. PARAM: master format (EXR frames → ProRes/H.265); resolution/fps; bitrate/CRF;
audio codec/loudness; version list.  MIST: rendering final directly to MP4 (generation loss, no pass
control); wrong frame rate (judder); over-compression (artifacts); loudness mismatch.  EDGES: →
D112, → D120, → D119, → D129.
D129 — ARCHIVING [SIT]
DEF: Preserving the project for the future: final files, sources, and the knowledge to reopen them.
WHY: Films get re-released, re-cut, re-rendered (4K remasters!). An un-archived project is a lost
asset;  archives  are  the  final  version of  the  pipeline  (D124).  The  archive  contents: 1.  Final
deliverable masters (D128) — the most important file. 2. Project files: all .blends (final versions
— prune WIP at archive time, keep the documented final versions + the versions.md). 3. Sources:
textures, HDRI, audio, reference, concept art, sheets — everything the project  depends on  (D123
CHAPTER 15 — EDITING, PRODUCTION PIPELINE, MANAGEMENT, QC, FINAL OUTPUT

tree). 4. Caches (if you want to re-render without re-simming — huge, often skipped; at least keep
the sim settings). 5. Docs: world bible, shot list, naming legend, pipeline notes, versions history —
the decision record (why was this done this way). 6. Add-on list (which add-ons/versions the project
needs — so it can be reopened on a new machine!). Archive format: a single folder (or zip/tar) with
a  README  index;  store  on  multiple media  (drive  +  cloud);  verify  (checksums  —  a  quick  hash
manifest); date it; keep backups (D124).  MIST: archiving only the final video (no sources — can't
revisit); no README (future-you can't navigate); one copy only; no add-on documentation. EDGES: →
D124, → D123, → D128.
PIPELINE HANDBOOK CLOSE-OUT
The 129 production domains are now mapped to their systems and methods. Part 3 draws the edges
between all of them (the dependency graph). Part 4 demonstrates navigation from arbitrary ideas.
Part 5 (appendix) holds decision trees, templates, and the glossary.
CHAPTER 15 — EDITING, PRODUCTION PIPELINE, MANAGEMENT, QC, FINAL OUTPUT
