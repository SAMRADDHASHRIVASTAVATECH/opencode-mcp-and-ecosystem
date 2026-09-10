# Chapter 14 — Rendering, Engines, Passes, Compositing, Color (D112–D119)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 107–110 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 14 — RENDERING, RENDER ENGINES,
PASSES, COMPOSITING, COLOR
Domains D112–D119. Rendering turns the scene into pixels; compositing turns pixels into the image
— color, depth, and the final film look. Half of "rendering quality" lives in the comp.
D112 — RENDERING [REQ]
DEF: Computing final images from the scene: resolution, samples, engines, output formats.  WHY:
Rendering is where everything converges — and where time and money are spent. Understanding the
settings (not just clicking Render) is what makes renders fast and correct. Core settings (Output
Properties + Render Properties): - Resolution & aspect (set at project start, D14): 1920×1080,
3840×2160 (4K), 2.39:1 cinemascope, etc.; 100% vs half preview renders (25%/50%/100% scale —
work at 50%, final at 100%). - Frame range & step: the shot's frame range (from D10); render step
(every frame or every N for preview). - Output format: PNG/EXR for frames (EXR = OpenEXR, the
production standard: 16/32-bit float, holds all passes/light data); FFmpeg video (H.264/ProRes) for
quick previews; never render final to compressed video  — render EXR frames, then encode (D128). -
Samples (Cycles): number of light samples per pixel; 32–128 typical with denoising (D114); more =
cleaner but slower; use  Denoise (OptiX/OpenImageDenoise). -  Render engines (D113):  Cycles
(physically-based, raytraced) vs EEVEE (real-time raster, fast) vs Workbench (solid preview). - Motion
blur & DoF: enable in render (Cycles) for film realism — motion blur transforms animation quality (2–
8% shutter); DoF often done in comp (D117). -  Color management (crucial!):  Render → Color
Management: View Transform: Filmic / AgX (the modern standard — handles HDR highlights, film-
like rolloff;  AgX is Blender 4.x default),  Exposure,  Look (contrast presets);  white balance and
exposure tuning happens here before comp .  PARAM: engine; samples; resolution; frame range;
format (EXR!); color management (AgX); motion blur; DoF; denoise; tile size (GPU: irrelevant in 4.x —
auto); GPU compute device (Preferences → System → Cycles render devices — enable your GPU!).
MIST: rendering final at compressed video; no denoise (noise everywhere) or over-denoise (waxy);
ignoring color management (sRGB default = blown highlights); rendering at 100% while iterating
(time  waste  —  25–50%  for  WIP).  DIAG: render  times  exploding?  →  samples/materials/volumes;
washed-out image → color management/exposure. FIX: iterate at low res + low samples + denoise;
final render clean. EDGES: → D113, → D114, → D115 passes, → D117 comp, → D128 output.
D113 — RENDER ENGINES [REQ]
DEF: The  rendering  backend:  Cycles  (raytraced  realism),  EEVEE  (real-time  raster),  Workbench
(viewport preview).  WHY: Engine choice shapes the whole pipeline (materials, lights, perf, look).
Choose once (D14), switch only deliberately.  Cycles: -  DEF: path-tracing renderer: simulates light
rays  (bounce,  scatter,  refract)  for  photorealistic  results.  -  PRO: physically  correct  (realistic  GI,
reflections, SSS, volumetrics); the film standard; consistent with PBR materials (D30). -  CON: slow
(samples × complexity); noisy without denoising; heavy for real-time. - USE: final renders, realistic/
film look, anything needing true reflections/refraction/SSS/volume. - PARAM: samples; bounces (max
light bounces; diffuse/glossy/transmission); caustics (off by default — expensive); denoise; GPU/CPU;
light tree; adaptive sampling. EEVEE (EEVEE Next in 4.2+):  - DEF: real-time rasterized renderer
with  approximations  of  the  same  PBR  look;  dramatically  faster;  supports  raytraced  reflections/
refraction/AA in EEVEE Next. - PRO: instant feedback; real-time lighting preview; interactive lookdev;
CHAPTER 14 — RENDERING, RENDER ENGINES, PASSES, COMPOSITING, COLOR

realtime-style films (D137). - CON: approximations (SSR, screen-space effects) can miss objects off-
screen; volumetrics/SSS cheaper-looking; light bounces limited. -  USE: previews, real-time style,
stylized films, rapid iteration, game-style pipelines. -  PARAM: ray-tracing (EEVEE Next), shadows
(soft via distance), volumetrics, bloom (compositor), AO, motion blur, SSR. Workbench: solid/simple
preview renderer — for blockout/animatic/previs captures (D11/D16).  Choosing: realism + time
budget → Cycles; speed + stylized → EEVEE; hybrid: EEVEE lookdev, Cycles final for hero shots;
render the same scene in both is fine if materials are PBR-clean (D30). MIST: mixing engines mid-
project without testing (materials/lighting differences); assuming EEVEE "isn't good" (it's a different
tool); Cycles with default settings (slow) when 10 minutes of tuning (D114) fixes it. EDGES: → D112,
→ D114, → D30 materials, → D137 real-time.
D114 — RENDER OPTIMIZATION [REQ]
DEF: Making renders fast without wrecking quality: sampling strategy, denoising, bounces, memory,
batching. WHY: Render time is production money; the same scene can render 10× faster with correct
settings  —  or  be  unusable  with  wrong  ones.  Optimization  is  a  strategy,  not  a  checkbox.  The
strategy (in order of impact):  1.  Denoising: enable denoise (OpenImageDenoise CPU / OptiX
GPU) → samples drop from 1000s to 32–128 with similar quality. The single biggest win. 2. Samples
& adaptive sampling:  adaptive sampling (noise threshold 0.01–0.05) spends samples only where
needed; set max samples generously (512) but let adaptive stop early. 3. Bounces: light bounces 4–
8 typical;  limit transmission/volume bounces  (glass-heavy scenes: set max transmission bounces
lower); disable caustics unless needed. 4. Light & geometry: use Light Linking (D108) to exclude
lights from irrelevant objects; avoid thousands of small lights (use emissive + fewer lights); keep
geometry sane (subdiv levels — render 3 vs view 2 is fine, but don't subdiv what you can't see). 5.
Volumes (D111): the #1 slow-motion: restrict density/domain; low-res volume; separate pass. 6.
SSS (D32): restrict to characters/hero; use BSSRDF cheap approximations. 7. Resolution & scale:
final at 100%, WIP at 25–50%. 8.  GPU: enable GPU (OptiX/CUDA/HIP) in preferences; GPU + CPU
combined; tile settings mostly auto in 4.x. 9. Batching & recovery: render frames in batches; save
EXR per frame (crash-safe); use render farms for huge projects (D136). 10. Proxy/LOD in scene: far
objects at low LOD (D24) — cuts BVH build + ray cost.  Memory: texture 8k everywhere = VRAM
death; use UDIM wisely; bake heavy procedural stuff when needed; watch viewport memory (D126).
MIST: cranking samples instead of using denoise; full-volume scenes; 8k textures on background
props; rendering WIP at final settings; ignoring GPU settings.  DIAG: identify the slow part: disable
features one at a time (volumes? SSS? transparent shadows? high samples?) and re-time. EDGES: →
D112, → D113, → D111, → D126, → D136.
D115 — RENDER PASSES [SIT]
DEF: Splitting the render into separate images (passes) — diffuse, glossy, shadow, AO, mist, etc. —
for compositing (D117). WHY: Passes give the compositor control: relight, change shadow intensity,
add AO, grade foreground vs background, all without re-rendering. The professional pipeline renders
passes + assembles in comp. Core passes (View Layer → Passes):  - Combined: the full image
(the baseline). - Diffuse & Glossy: direct vs indirect lighting (separate light layers). - Shadow: the
shadow layer (tint/reduce shadows in comp). - Ambient Occlusion (AO): contact-darkening layer —
essential for grounding (D109). - Mist: camera-distance gradient — for aerial perspective (D110). - Z
(depth): depth map — for DoF (D117) and fog. - Normal, Object/Material/UV indexes: selection
masks for targeted grading (e.g., darken only the background). - Emission: glow elements (magic,
D101)  separated  for  glow  comp.  -  Cryptomatte  (Blender  4.x  has  native  Cryptomatte):
CHAPTER 14 — RENDERING, RENDER ENGINES, PASSES, COMPOSITING, COLOR

automatic  object/material  masks  —  the  modern way  to  isolate  (grass,  characters,  sky)  without
manual passes.  Use Cryptomatte. Pass naming & format:  render passes to  EXR Multi-Layer
(one  file,  all  passes)  —  the  standard;  Blender  writes  all  enabled  passes  into  a  multilayer  EXR.
PARAM: pass list per view layer; format (multilayer EXR); color space (linear for data passes, filmic
for combined). MIST: rendering only "Combined" (no control in comp); disabling AO (floating look);
forgetting Z for DoF; using color-space "sRGB" for data passes (breaks math in comp).  EDGES: →
D117, → D116, → D112.
D116 — AOVs (ARBITRARY OUTPUT VARIABLES) [ADV]
DEF: Custom  render  outputs:  any  shader  value  written  as  a  pass  (e.g.,  "wetness,"  "emission
amount," "fake object index") — via Cryptomatte (auto) or custom AOVs in shader nodes. WHY: AOVs
unlock comp tricks that would otherwise require re-renders: a "wetness" pass to grade wet surfaces,
a "magic energy" pass to glow only the spell, a "health/heat" pass.  HOW: Shader Editor → Add →
Output →  Shader AOV (name it) → connect any value to it; enable in View Layer passes; render
multilayer EXR; use in comp.  USE: stylized comps, material-driven masks, character FX, relighting
systems. MIST: AOVs for everything (pass count = file size + render cost); forgetting to enable the
pass in the view layer. EDGES: → D115, → D117.
D117 — COMPOSITING [REQ]
DEF: The node-based Compositor: assembling render passes, adding effects (glow, DoF, color), and
producing the final image.  WHY: Compositing is where  renders become film : half the "cinematic"
quality is comp — DoF, glow, grain, color, and pass manipulation. It's also where fixes happen without
re-rendering (D114 principle). The Compositor (node editor, compositing workspace):  - Input:
Render  Layers  node  (all  passes);  Image  nodes  (external  plates,  textures).  -  Core  nodes: Mix
(combine), Color (Curves, Balance, Hue/Sat, Exposure, Gamma), Blur (Gaussian, Defocus for DoF),
Glare  (bloom  —  the  effect  layer),  Vector  Blur  (cheap  motion  blur),  Mask  (bitmap  mask  nodes),
Cryptomatte node (mask extraction), Map Range/Map Value, Math, Group (node groups — reusable
comp  recipes).  -  The  standard  film  comp  recipe: combined  +  passes  →  (AO  multiply  for
grounding) → (mist for depth) → (DoF from Z) → (color grade: exposure/contrast/color balance) →
(glow/glare on emission) → (grain) → (vignette) → (LUT/film look, D119) → output. Depth of field in
comp: use the Z pass + Defocus node (or "Bokeh Blur") — much cheaper than render DoF, fully
controllable.  Motion blur: vector pass + Vector Blur, or render MB (D112).  Grain: add film grain
(noise node masked) — unifies the image, kills banding. Pass-based relighting: multiply/colorize
shadow pass, adjust AO — "paint with passes." PARAM: node graph structure; color spaces (linear
workflow — set color management properly, D112); file output (EXR multi).  MIST: doing color in
render instead of comp (fix once, reuse); no grain (banding/plastic); DoF rendered instead of comped;
comp graphs without groups (unmaintainable).  EDGES: → D115, → D116, → D118/D119 color, →
D112.
D118 — COLOR CORRECTION [REQ]
DEF: Fixing color: exposure, contrast, white balance, and range — making the image correct before
grading.  WHY: Renders are raw material; correction normalizes them (consistent exposure across
shots, correct whites) so grading (D119) has a clean base. Tools (comp nodes): Exposure (global),
Curves (per-channel contrast), Color Balance (lift/gamma/gain per channel), Hue/Saturation/Value,
CHAPTER 14 — RENDERING, RENDER ENGINES, PASSES, COMPOSITING, COLOR

White Balance node; the  scopes (View → Sidebar → Scopes: waveform, vectorscope, histogram —
use them! the waveform shows exposure; vectorscope shows color cast). PARAM: target exposure;
black/white points; white balance; per-shot consistency values. MIST: grading before correcting; no
scopes (guessing); shot-to-shot exposure mismatch (audience notices cuts).  EDGES: → D119, →
D117.
D119 — COLOR GRADING [SIT]
DEF: The creative look: teal-orange, desaturated melancholy, warm nostalgia, stylized palettes —
meaning through color. WHY: Grading is the final emotional brush: it unifies the film's palette (D02/
D138) and pushes mood. It's also where style (anime vibrancy, film noir, fantasy richness) gets
finalized. How: after correction (D118): global look (LUT/curves/color balance), LUTs (Look-Up T ables:
load film emulation LUT s — ACES/AgX workflows),  shot matching (match every shot to the same
look — use scopes + node groups as a "master grade" applied to all shots),  secondary grades
(isolate sky/skin/background via Cryptomatte → grade separately — the pro skill). The film looks:
teal-orange (blockbuster contrast), lifted blacks (modern/indie), crushed blacks (noir), desaturated +
grain  (historical),  vibrant  (animation),  split-toning  (highlights/shadows  different  colors),  vignette
(focus).  Blender: do grading in the Compositor (node group "MASTER GRADE" linked into every
shot's comp — D123 linking!) or export EXR to an external grader (DaVinci Resolve — free, the
standard)  for  full  film  finishing  (D128).  PARAM: look  choice  (from  D02  palette);  LUT;  scopes
verification; shot-matching tolerance.  MIST: grading each shot differently (film feels broken); no
secondary grades (flat); crushing skin; grading with no reference to the story's palette. EDGES: →
D118, → D117, → D120 editing (grade after edit!), → D138.
CHAPTER 14 — RENDERING, RENDER ENGINES, PASSES, COMPOSITING, COLOR
