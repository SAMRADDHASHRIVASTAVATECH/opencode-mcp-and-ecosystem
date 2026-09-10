# Depth Chapter 18 — Stylized & NPR Shading Systems

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 150–153 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 18 — STYLIZED & NPR
SHADING SYSTEMS
Expands D31, D30, D113, D138. How to build the non-photoreal looks: cel/toon, anime 2-tone/3-tone,
outlines, cartoon, painterly — and how to render/composite them so they look intentional, not broken.
18.1 THE NPR TOOLKIT (what makes stylized work)
Stylized shading is abstraction with rules: you reduce lighting to discrete steps, bold shapes, and
controlled color — but you must keep readability (silhouette, focal point, motion clarity). The toolkit:
Ramp quantization — turning continuous light into 2–4 tone bands (the core of cel shading).
Outlines — the graphic line that holds the shape (4 methods below).
Color logic — deliberate palettes, limited hue ranges, black or near-black shadow shapes.
Specular control — toon speculars (hard-edged, shaped) instead of physical ones.
Stylized materials — flat albedo + bold roughness contrast; no SSS, no complex Fresnel.
Render & comp discipline — the same look must survive the render pipeline (see 18.7).
18.2 CEL / TOON SHADING (the base system)
The shader-to-RGB method (Cycles & EEVEE):
Principled BSDF → Shader to RGB → (optional ramp) → mix with Base Color → Material Output
Shader to RGB converts the shaded result into a color you can remap.
ColorRamp with 2–3 hard steps quantizes light into tone bands: band 1 = lit color, band 2 =
midtone, band 3 = shadow color.
Set the ramp to Constant interpolation for hard bands; Ease for soft anime shading; B-spline
for a subtle stylized falloff.
Mix the remapped result back over the base color (or use the ramp itself as the shading).
Result: object lights in discrete bands; edges catch the shadow band — the classic cel look.
Toon specular: a separate node branch — Fresnel → ramp (hard) → Mix onto the base, or use a
"specular toon" via the ramp on the Shader-to-RGB with a narrow band. Keep highlights  shaped
(round or diagonal bands) — physical glints kill the cel look.
Rim light (anime & cel):  Fresnel → ColorRamp (thin band) → Add to color — a graphic rim that
separates the character from the background. This is the #1 "makes it look professional" trick.
2-tone vs 3-tone:  2-tone = lit + shadow (bold, cartoon); 3-tone = lit + mid + shadow (anime
standard, softer, more depth). Add a 4th "core shadow" band for high-contrast scenes.
18.3 ANIME SHADING SYSTEM (the full recipe)
Skin: 2–3 tone ramp; shadow color = skin color darkened + shifted toward a cool/warm accent
(not black — anime shadows are colored); a soft blush mask on cheeks (vertex paint or UV mask
→ mix).
1. 
2. 
3. 
4. 
5. 
6. 
• 
• 
• 
• 
• 
• 
DEPTH CHAPTER 18 — STYLIZED & NPR SHADING SYSTEMS

Hair: top-lit gradient: bright at the crown → dark at the tips; a top-down light trick: use a
gradient along the strand UV (or a "hair light" spot above); add 1–2 sharp highlight streaks
(anisotropic or masked emission).
Eyes: the signature: gradient iris (top dark → bottom light), big specular catchlight (two white
shapes — top-left + bottom-right), dark upper lash line; the eye is often emissive-ish bright.
Face shadow (the critical anime trick): shadows on the face fall in anime shapes, not physical
ones: a diagonal band across the face (from the brow), the "inverted eyebrow shadow," a nose
shadow as a tiny triangle, chin shadow crescent. Standard method: a shadow-casting sphere/
box above the head (a "shadow catcher" light-blocker) or a projected texture — shape-
controlled, not physically accurate.
Outline weight: black outlines (1–3 px) on the outside silhouette + no outline on inner detail (or
thin gray lines for folds). Outline color can tint (dark blue for night scenes).
Background: flat or gradient painted backgrounds (2D), or 3D with heavy stylization; the
character is often brighter than the environment (value separation).
18.4 OUTLINES — THE FOUR METHODS (pick per need)
Method How Cost Best for
Inverted hull Duplicate mesh, flip normals, scale along normals (or
solidify with thickness), black material, backface-
culled in front
cheap, fast Cartoon, most reliable
— the workhorse
Freestyle
(Blender render
pass)
Line style renderer: edge detection with thickness/
color/crease control
moderate Clean vector-style
lines, technical lines
Fresnel/emission
outline
Fresnel → ramp → emission on the same material cheapest, no
geometry
Soft fades, single-
material toon
Grease Pencil
overlay
2D strokes drawn over (D130) manual Hand-drawn feel,
animated line weight
Inverted hull details: solidify modifier (flip normals) → material black → on the original mesh add a
vertex-group mask so only the silhouette gets thickness (edges), keep inner geometry hull-less; scale
hull slightly; z-fighting avoided by backface culling + hull rendered in front via render pass ordering.
For stylized characters this is the standard pipeline; it also gives animated line weight via shape keys.
18.5 CARTOON (rubber-hose & classic) & PAINTERLY
Cartoon: bold 2-tone; shadows are black or very dark  with crisp, simplified shapes; outlines thick &
black; speculars are white blobs; the palette is bright and saturated; background often flat color or
simple gradient. Deformation leans on squash & stretch (D65) which the shading must survive (hull
outline follows deformations automatically — good). Painterly (concept-art look): base material +
heavy normal displacement (noise) + color variation via multiple large-scale noise layers; render
with low texture filtering (or use the "Brush" shader trick: perturb UVs with noise → paint-like smear);
blur/soften in comp; add canvas grain. Often combined with vertex-painted color blocks. Painterly is
the hardest to keep consistent — lock a brush vocabulary (D138) before painting.
• 
• 
• 
• 
• 
DEPTH CHAPTER 18 — STYLIZED & NPR SHADING SYSTEMS

18.6 STYLIZED MATERIAL VARIANTS (quick table)
Look Base Shadows Specular Outline
Cel cartoon flat BC 1 band, dark white blob black hull, thick
Anime flat BC + gradients 2–3 bands, colored streak/catchlight black, thin, selective
Modern toon (games) PBR base, simplified 2–4 bands via ramp toon-shaped fresnel or none
Graphic/comic flat + halftone hatch pattern mask none strong, varied weight
Watercolor soft BC bleed via blur mask none wobbly, thin
Doodle/scribble flat minimal none Grease Pencil, jittered
Photoreal-with-toon PBR full physical physical fresnel only
18.7 RENDERING & COMPOSITING FOR TOON (the part
everyone misses)
Engine: EEVEE is the natural home (fast, flat-shaded-friendly, no denoise noise); Cycles works too
(Shader-to-RGB in Cycles can be noisy — raise samples or use the "Light Path" tricks; many artists
do toon in EEVEE and composite).
Lighting for toon: fewer, bigger, harder lights than realism: 1 key + 1 rim is often enough; no
soft shadows (use sharp or none — toon shadows are often painted shapes, not raytraced);
ambient occlusion off (flattens the look); add light only where the ramp needs a new band.
Color management: keep the palette in gamut: use AgX or sRGB; avoid blown highlights (flat
colors don't clip well); grade in comp (D119) to push the intended palette.
Compositing for toon: no motion blur or DoF (or only subtle, hand-shaped); add grain lightly
(or none); glow only for magical elements (D101); vignette ok. The "clean vector" look = crisp
edges + flat colors + grain-free.
Anti-aliasing: EEVEE AA on; if edges look jaggy, render 2× and downscale, or add the hull at
1.25× thickness.
Consistency: toon lives or dies by style rules (D138): one ramp palette, one outline weight, one
specular shape — write them down, apply to every asset.
• 
• 
• 
• 
• 
• 
DEPTH CHAPTER 18 — STYLIZED & NPR SHADING SYSTEMS

18.8 STYLIZED-SHADING FAILURE MODES & FIXES
Symptom Cause Fix
Bands flicker in animation Ramp thresholds + noise in
shading
Increase sample/lighting stability; widen bands; lock light
angle
Outline z-fights Hull too tight Increase hull thickness; backface cull; separate render
pass
Looks "flat/boring" No rim, no color logic Add colored rim + value contrast between char & bg
Looks "dirty" Physical shadows/spec
leaking in
Remove extra lights; check for non-ramp materials
Grainy toon in Cycles Shader-to-RGB sampling Raise samples or use EEVEE; denoise only subtle
Outline breaks on
deformation
Hull mesh not following Rebuild hull after deform; use vertex-group thickness;
check shape keys
Palette mush All colors similar value Enforce value hierarchy: char brightest, bg dimmed
(D104)
DEPTH CHAPTER 18 — STYLIZED & NPR SHADING SYSTEMS
