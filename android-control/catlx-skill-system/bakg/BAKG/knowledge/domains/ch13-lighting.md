# Chapter 13 — Lighting, Shadows, Atmosphere, Volumetrics (D108–D111)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 104–106 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 13 — LIGHTING, SHADOWS,
ATMOSPHERE, VOLUMETRICS
Domains D108–D111. Lighting is 50% of "rendered look": it creates mood, sculpts form, and tells the
audience when and where. Shadow, atmosphere, and volumetrics are its supporting cast.
D108 — LIGHTING [REQ]
DEF: Placing and configuring lights to reveal form, set mood, direct the eye, and establish time/place.
WHY: Lighting makes materials (D30) and models look real or fake; it's the fastest way to change a
scene's  emotion  (same  set,  different  light  =  different  film).  Great  lighting  is  designed,  like
composition  (D104).  Light  types  (Blender): -  Sun: directional,  parallel  rays;  the  daylight/
workhorse; position = angle, strength + angle determine shadow length. -  Area: soft, controllable
(size  =  softness);  the  standard  for  studio/hero  light.  -  Point: omnidirectional  (bulbs,  candles,
practicals). -  Spot: cone light (stage, shafts, focus). -  HDRI/World: the environment light (sky,
reflections) — always a good base for lookdev. - Emissive surfaces: geometry with emission shader
becomes light (neon, fire, screens) — important for realism (lighting matches the visible source). The
classic 3-point + system:  - Key light: the main light (defines form and mood); position by angle
(45° up/side typical; harder angles = drama). -  Fill light: softens shadows (opposite the key, low
intensity);  darkness  of  fill  =  mood  (no  fill  =  noir).  -  Rim/back  light: separates  subject  from
background (edge glow); critical for readable silhouettes. - Practical/bounce lights: sources in the
scene that explain the light (a lamp, a window, fire) — realism anchor. - Lighting the background
separately (environment light, accent lights) — the set is a character. Lighting design process: 1.
Mood & time (from D02/D01): define the emotional light (sunrise hope, midnight danger, overcast
melancholy). 2. HDRI/sun base → key → fill → rim → practicals → accents. 3. Check in order: form
readability → mood → continuity (lighting continuity across shots — same sun angle in the same
scene!) → integration (shadows fall correctly, contact shadows present). Color temperature: warm
(2800–3500  K:  candle,  sunset)  vs  cool  (5500–6500+  K:  daylight  shade,  night,  moonlight);  color
contrast (warm key + cool fill = the cinematic standard); white balance consistency. PARAM: light
type; strength; color/temperature; size (softness); distance falloff; angle; shadow settings (D109);
volumetric involvement (D111).  MIST: no fill (crushed blacks by accident); flat light (no key/rim
separation); lights that don't match the practicals in the scene; over-brightening (everything 1.0
strength — expose properly!); ignoring the world/HDRI. DIAG: render a gray-sphere/character test;
check shadow direction consistency; use viewport "Render preview" + exposure. FIX: build light by
light (add one, evaluate, add next); use light linking (Blender 4.x Light Linking — a light affects only
chosen objects — the pro tool for control); render light groups for comp (D115). EDGES: → D109, →
D111, → D112 render, → D30 materials, → D104 composition.
Deep chain — Lighting → Setup → Light → Contribution
Key (form+mood) → fill (shadow control) → rim (separation) → practicals (anchors) → accents (set) →
light linking → color temp → exposure → integration
CHAPTER 13 — LIGHTING, SHADOWS, ATMOSPHERE, VOLUMETRICS

D109 — SHADOWS [REQ]
DEF: Shadow design: direction, softness, contact, and color — the silent form-giver. WHY: Shadows
anchor objects to the world (contact shadows = "it's really there"), reveal time of day, and create
composition (D104). Wrong shadows = floating, wrong-time, wrong-place.  Shadow properties:  -
Direction: from the light (sun = long shadows morning/evening, short noon); consistent across the
shot/scene. -  Softness: penumbra from light  size (area light = soft, sun = sharp but softened by
distance/atmosphere);  softness  sells  scale  (tiny  light  =  hard  shadow).  -  Contact  shadow: the
darkening where object meets surface — the #1 grounding cue; without it, objects float (in Blender:
AO pass, D115, or a tiny contact shadow via ambient occlusion in render/compositing). -  Shadow
color: not black — picks up environment color (bounce); shadow  density adjustable per light (for
stylized, lighter shadows). -  Cast vs received:  objects can cast and/or receive; hero control per
object (light linking again).  Blender settings:  per-light Shadow (softness via size, ray visibility);
render shadow passes (D115: Shadow pass for compositing); AO (World → Ambient Occlusion; or the
AO render pass) — always render AO for grounding. MIST: no contact shadows; pure black shadows
everywhere;  shadows  pointing  different  ways  in  the  same  scene;  disabling  shadow  casting  on
everything (flat). EDGES: → D108, → D115 passes, → D117 comp (AO), → D110 (shadows through
atmosphere).
D110 — ATMOSPHERE [SIT]
DEF: The air itself: fog, haze, mist, aerial perspective — the depth cue layer. WHY: Atmosphere is the
mood and the  depth: it separates near/far planes (aerial perspective: far things are lighter, bluer,
lower contrast), softens distance, and instantly sells weather (D02's rainy city = damp haze). How to
add atmosphere: 1. Aerial perspective (the cheap, standard way):  in compositing (D117) or
materials: fade distant objects toward the fog color (mix by distance — in Cycles use a "Fog"/"Aerial
Perspective" via mist pass: Render → Mist pass (World) → combine in comp). The Mist pass (camera
distance → gradient) is the professional tool: far plane = full mist. 2. Volumetric fog (D111): true
volume — light shafts, god-rays, glowing fog (expensive, for hero shots). 3. Fog objects: a giant low-
poly box/plane with a fog volume shader (cheap fake volumetrics). 4.  Particle haze: dust motes
(D87/D99) in light shafts. PARAM: fog density; fog color (from palette/lighting); start/end distance;
mist pass settings. MIST: fog that kills the subject (too dense at hero distance); fog color that ignores
the lighting (white fog in a blue scene). EDGES: → D111, → D104 (depth in composition), → D117
comp.
D111 — VOLUMETRICS [SIT]
DEF: Volumetric light and fog: light interacting with particles in the air — shafts, beams, glowing
haze.  WHY: Volumetrics are the  money shot  of atmosphere: light through rain, god-rays through
trees, spot beams through smoke. They sell weather and scale like nothing else — at a render cost.
HOW (Blender): World → Volume → Principled Volume  (density, anisotropy, color) makes the
whole scene volumetric (global fog); or use  Volume on a domain object for localized fog; lights
inside/through volume create beams (spot/area lights with volume); for  light shafts: a spot light +
volumetric  world/box.  Key  settings: density  (0.01–0.1  for  subtle,  higher  for  thick);  anisotropy
(forward scatter: 0–0.5 makes light beam); color (fog tint); temperature for fire/smoke interplay (D95/
D96).  The trick of control:  full-scene volume is expensive — limit density, use  localized volume
boxes  near  the  camera/hero,  and  composite  the  rest  (D117:  render  volume  pass  and  grade  it
CHAPTER 13 — LIGHTING, SHADOWS, ATMOSPHERE, VOLUMETRICS

separately). PARAM: density; anisotropy; color; domain bounds; sampling; light involvement. MIST:
volumetric everything (bake times ×10); density too high (fog soup); ignoring that volumes need
light (a volume in a dark scene does nothing — put lights through it).  PERF: low-res volume +
denoise; separate volume pass; limit volume domain size; use EEVEE's volumetrics (fast, real-time)
for preview. EDGES: → D110, → D95/D96 (smoke/fire are volumes), → D112, → D117.
CHAPTER 13 — LIGHTING, SHADOWS, ATMOSPHERE, VOLUMETRICS
