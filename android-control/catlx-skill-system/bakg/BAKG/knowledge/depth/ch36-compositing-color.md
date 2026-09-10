# Depth Chapter 36 — Compositing & Color Depth

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 214–216 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 36 — COMPOSITING & COLOR
DEPTH
Expands  D115–D119.  The  complete  finishing  craft:  the  compositor  node  cookbook,  pass-based
relighting, scopes mastery, the grading workflow, film looks, LUT s, and shot matching.
36.1 THE COMPOSITOR NODE COOKBOOK (production
node recipes)
Recipe Nodes Use
The standard film
comp
Render Layers → Mix(AO×) → Mix(mist) → Defocus(Z) → Color grade →
Glare(emission) → Grain → Vignette → Output
the base pipeline
(D117)
Contact-shadow fix AO pass → Mix (multiply, 0.6–0.9) onto combined grounding (D109)
Aerial perspective Mist pass → ColorRamp (fog color) → Mix onto combined by distance depth (D110)
DoF in comp Z pass → Defocus (f-stop, bokeh) or Bokeh Blur cheap DoF (D117)
Glow only on FX Emission pass → Glare → Add over combined effects sit in shot
(35.6)
Vector blur Vector pass → Vector Blur → Mix (0.5–1) cheap motion blur
(D112)
Grade in a group Node group "MASTER GRADE" (exposure/contrast/balance/LUT) reuse across shots
(D119)
Sky replacement Cryptomatte (sky) → separate grade or replace with image day-for-night,
stylized skies
Film grain Noise → scale to resolution → Mix (screen/overlay, 2–6%) unify + hide
banding
Vignette Radial gradient → Multiply (dark corners 10–25%) focus, mood
Chromatic
aberration
Split RGB → offset R/B slightly → combine stylized effects,
cyberpunk
Day-for-night Grade blue/cool + lower exposure + moonlight rim (Ch 22) cheap night (use
wisely)
Glow pulse Emission pass → Glare → driven by a time-based ramp (frame) magic breathing
(D101)
36.2 PASS-BASED RELIGHTING (paint with passes)
The pro skill: adjust light in comp, not in render.  - Shadow pass: multiply (darken 0.8–1.0) or
tint (warm/cool) — control shadow mood per shot. - Diffuse pass: relight the base (multiply a color)
—  "repaint"  the  scene.  -  Glossy/reflection  pass: boost  reflections  on  the  hero,  dampen  the
background. -  AO pass: strengthen contact (grounding) or weaken (stylized flat). -  Light groups
(D108): render key/fill/rim groups separately →  grade each group independently  — the film-
industry standard (the key gets warmth, the rim gets pop, the fill gets pushed down). - Cryptomatte
masking: isolate sky/character/effects/props for targeted grades — the #1 time-saver over hand
masks.
DEPTH CHAPTER 36 — COMPOSITING & COLOR DEPTH

36.3 SCOPES MASTERY (see before you grade)
Scope What it shows What to check
Waveform luma (Y) per horizontal
position
exposure: skin ~ 60–70 IRE; highlights not crushed (unless style);
consistent across shots
Vectorscope hue/saturation color casts (skin should sit on the skin line); palette discipline (D138)
Histogram tonal distribution black/white points; clipping
Parade RGB channels separately white balance (neutral grays equal); channel clipping
The workflow: correct with scopes (D118) → grade with eyes + scopes (D119). Never grade "by
feel" alone — scopes catch what the eye adapts to (skin that's drifted green, exposure that crept up
between shots).
36.4 THE GRADING WORKFLOW (shot → sequence → film)
Per-shot correction (D118): exposure normalization, white balance, black/white points — make
every shot neutral and consistent.
Sequence grade: apply the master grade (D119) to every shot (node group or LUT) — the film's
look.
Shot matching: with scopes, match each shot to its neighbors (skin tone, exposure, hue) — the
audience never notices a matched cut, and always notices a mismatched one.
Secondary grades: Cryptomatte isolates → push the sky, warm the skin, cool the shadows,
boost the magic (D101).
Final pass: grain, vignette, any global texture (film emulation, 36.5).
Render: to the delivery format (D128) — grade AFTER the edit (D119), never before.
36.5 FILM LOOKS & LUTs (the catalog)
Look Recipe Use
T eal-orange (blockbuster) shadows → teal (hue shift), highlights → warm/
orange
hero films, readability
Lifted blacks (modern/indie) black point up (0.02–0.05), low contrast contemporary drama,
commercials
Crushed blacks (noir) black point down, high contrast, desaturate noir, horror, drama
Bleach bypass (desaturated +
contrast)
desaturate 20–40%, contrast up, slight cyan
shadows
war films, gritty
Warm nostalgia warm tint (lift), reduced saturation, soft highlights,
grain
memory, period
Cool clinical cool tint, clean whites, slight cyan sci-fi, labs, dystopia
Vintage (teal shadows + warm
skin)
split-tone period dramas
Anime pop saturated, clean whites, no grain, bright midtones stylized animation (Ch 18)
Muted fantasy desaturated, earthy, warm shadows epic fantasy
Horror dread green-ish shadows, crushed blacks, desaturated,
vignette strong
horror (4.6)
1. 
2. 
3. 
4. 
5. 
6. 
DEPTH CHAPTER 36 — COMPOSITING & COLOR DEPTH

LUTs (Look-Up Tables): load film-emulation LUT s (ACES/AgX pipelines) — a LUT is a baked grade;
apply as the final stage of the master grade.  Build your own LUT:  grade a reference shot, then
export the grade as a LUT (external tools; Blender comp can approximate via curves groups) — the
house look (D138) shared across the film.
36.6 STYLIZED GRADING (matching the shading — Ch 18)
Toon/cel: clean, saturated, no grain (or minimal), no vignette (or light), no chromatic aberration;
grade keeps the flat bands in gamut (AgX/sRGB, no clipping).
Anime: bright midtones, clean whites, saturated accent colors, soft glow on magic only.
Painterly: add canvas/paper texture (noise + blur mask), soft contrast, desaturated edges
(vignette as "canvas falloff").
Horror: heavy vignette + grain are features — use them.
The rule: the grade must respect the shading system — a toon grade that crushes blacks kills the
ramp bands.
36.7 COMPOSITING FAILURE MODES & FIXES
Symptom Cause Fix
Skin looks wrong no scopes / bad WB vectorscope skin-line check; correct WB first
Cuts feel jumpy in color no shot matching scope-match neighbors (36.4)
Banding in skies/gradients 8-bit + hard grade 16-bit EXR, dither/grain
DoF looks fake wrong Z range / no bokeh shape check Z pass range; use Bokeh Blur
Glow over everything Glare threshold too low threshold to emission only
Effects float no FX pass separation render FX pass, grade/glow it alone (35.6)
Grade looks flat no secondary passes Cryptomatte separates + push
Grain looks digital wrong grain scale/speed match grain to resolution; animated noise
Day-for-night looks fake sky still bright sky isolate + grade + moon rim (Ch 22)
• 
• 
• 
• 
• 
DEPTH CHAPTER 36 — COMPOSITING & COLOR DEPTH
