# Depth Chapter 39 — AI Concept Development Depth

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 223–225 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 39 — AI CONCEPT
DEVELOPMENT DEPTH
Expands  D06.  The  complete  local-AI  concept  workflow:  model/checkpoint  selection,  prompt
engineering,  ControlNet  mastery,  img2img/inpainting/outpainting,  character-consistency  systems,
LoRA basics, style control, and the bridge from AI image to production 3D asset.
39.1 THE TOOLKIT (what to run locally)
Tool Role Notes
ComfyUI node-based SD/SDXL/FLUX
pipeline
the professional choice — full control, workflows as
files
Automatic1111/Forge UI-focused SD/SDXL friendlier, good for quick explorations
Stable Diffusion 1.5 base model (512/768 px) fast, huge ecosystem
SDXL newer base (1024 px) higher quality, better anatomy, slower
FLUX (if hardware
allows)
cutting-edge base best text/quality, heavy VRAM
Checkpoints style-tuned bases pick per target style (photoreal/anime/painterly)
LoRAs small style/subject adapters character/style consistency, low VRAM cost
ControlNet structure control the key to useful images (39.3)
IP-Adapter image-prompt conditioning match an existing image's style/content
39.2 PROMPT ENGINEERING (the structure)
The positive prompt skeleton (order matters): [subject] + [pose/action] + [setting] + [style/
medium] + [lighting] + [camera/lens] + [detail/quality tags]  Example: "six-legged crystal creature,
walking through a rainy fantasy city, cinematic concept art, volumetric lantern light, blue hour, low
angle, detailed facets, volumetric fog, artstation quality"
The negative prompt (what to suppress): extra limbs, mutated hands, fused fingers, bad anatomy,
watermark, text, logo, blurry, low quality, jpeg artifacts, duplicate  —  tuned  per  checkpoint.
Parameters: steps 20–40; CFG/guidance 4–12 (higher = stricter prompt, more artifacts); sampler
(Euler/DPM++/DDIM — try 2–3 per style); seed (fixed for iteration, random for exploration); resolution
(native per model — SD1.5 at 512–768, SDXL at 1024); denoise strength for img2img (0.3–0.7 edits,
0.7–1.0 full restyle).
DEPTH CHAPTER 39 — AI CONCEPT DEVELOPMENT DEPTH

39.3 CONTROLNET MASTERY (the "make it useful" layer)
ControlNet model What it controls Best for
Canny/Lineart edge structure exact composition, line work, turnarounds
Depth depth map structure posing a character in a scene, camera depth
OpenPose skeleton pose exact character pose — the concept-work staple
Normal surface normals form from a 3D base
Scribble loose structure quick ideation from sketches
SoftEdge/HED soft structure less rigid than canny, more artistic
IP-Adapter style/content matching match the character sheet's style
The pro workflow: (1) block a rough pose in Blender (or draw a stick figure) → (2) render OpenPose/
depth control maps → (3) run SD with ControlNet → (4) get on-model pose explorations. This is how
AI becomes a 3D workflow partner, not a random generator  — the structure comes from you,
the texture from the model.
39.4 CHARACTER CONSISTENCY (the hard problem,
solved)
Why it fails:  SD redraws the character differently each seed; consistency requires  anchors.  The
anchors: 1.  Fixed  prompt  skeleton —  the  character's  description  stays  identical  across
generations (same order, same wording). 2. Fixed seed + ControlNet pose — structure varies only
where you want it. 3. Character LoRA — train a small LoRA (15–50 images of the character in varied
poses) — the real solution for a recurring character; requires a GPU + training setup (Kohya/SD-
scripts; budget hours). 4. IP-Adapter — feed the character sheet image as an image-prompt to bias
every generation toward it. 5. Post-fix: consistency drift is expected — fix with img2img + inpaint
(re-ground the face, the outfit). The honest rule (D06):  AI gives you proposals; the final character
sheet (D08) is hand-cleaned. Consistency is a human job — AI accelerates the exploration, the artist
owns the canon.
39.5 img2img / INPAINT / OUTPAINT (the editing toolkit)
Tool What it does Use
img2img redraws an image with new prompt (denoise
controls fidelity)
restyle, refine, variation
Inpainting regenerates only a masked region fix anatomy, change one element ("crystal armor"
→ "chainmail")
Outpainting extends the canvas beyond the edges widen a concept, build environments
Upscale 2×/4× resolution (latent or ESRGAN-style
upscalers)
final concept resolution
Workflow example (the cloak redesign):  img2img the full concept at 0.5 denoise with "flowing
cloak" prompt → inpaint the cloak region for shape fixes → outpaint the full body → upscale → hand-
clean in 2D (D08).
DEPTH CHAPTER 39 — AI CONCEPT DEVELOPMENT DEPTH

39.6 STYLE CONTROL (making the art direction stick)
Style LoRA (anime/painterly/photoreal) + checkpoint = the base style.
Style reference via IP-Adapter: "make it look like this painting" — instant style matching to
your reference board (D07).
Prompt style vocabulary: medium (concept art, 3D render, oil painting, watercolor), lighting
(studio, golden hour, rim), palette ("desaturated teal and rust").
The style matrix discipline (D138): define the film's style rules first (palette, rendering, level
of detail); every AI generation must pass the style gate — if it doesn't match the house look, it's
exploration, not design.
39.7 FROM AI IMAGE TO 3D ASSET (the bridge — the
critical rule)
AI images are NOT production assets.  The bridge (D06/D08): 1.  Select the best variant (or
composite several — "this silhouette + that palette + this detail"). 2. Resolve inconsistencies: the AI
image has wrong anatomy, missing geometry, no clean symmetry — redraw/clean as a character
sheet (D08: front/side/back, proportions, callouts). 3.  Derive the spec  (D05): the sheet + the
creature spec (locomotion, mass, surface) becomes the modeling contract. 4.  Model in Blender
(D19/D20/D22)  with  the  sheet  as  reference  (background  images).  5.  Never  trace  pixels  for
topology — the AI image informs design, topology comes from the deformation atlas (D31/Ch 31).
39.8 AI CONCEPT FAILURE MODES & FIXES
Symptom Cause Fix
Extra limbs/bad anatomy prompt/model limits negative prompts, ControlNet pose, inpaint fixes
Same face every time seed/model bias seed variation, character LoRA (39.4)
Inconsistent character across shots no anchors anchors (39.4) + hand-clean sheets
Blurry/smeary detail denoise too high / low res lower denoise, upscale pass
"AI look" (uncanny gloss) no style rules style gate (39.6), match house look
Images don't match the 3D no bridge the sheet pipeline (39.7)
GPU too slow heavy models smaller model, tiled upscale, fewer steps
Prompt soup too many conflicting tags prompt structure (39.2), fewer, ordered
• 
• 
• 
• 
DEPTH CHAPTER 39 — AI CONCEPT DEVELOPMENT DEPTH
