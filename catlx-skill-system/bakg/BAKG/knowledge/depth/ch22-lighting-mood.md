# Depth Chapter 22 — Lighting & Mood Encyclopedia

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 163–166 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 22 — THE LIGHTING & MOOD
ENCYCLOPEDIA
Expands D108–D111. Time-of-day and weather systems, 12 mood recipes with concrete setups,
lighting patterns, color theory for light, and the controls that make it all manageable.
22.1 TIME-OF-DAY LIGHTING TABLE (what "when" means
for light)
Time Sun
angle Color temp Shadow Character of light Notes
Dawn/dusk
golden hour
0–10° 2000–3500 K very long, soft warm, low contrast,
atmospheric
the "beauty light";
rim-heavy
Blue hour (after
sunset)
below
horizon
8000–12000 K
(ambient)
none (diffuse) cool, flat, saturated city lights pop;
romantic/mysterious
Morning (10°) 10–30° 3500–4500 K long warm-ish, clean fresh, active
Midday 45–80° 5500–6500 K short, harsh,
high-contrast
hard, vertical
shadows
harsh reality, desert,
oppressive
Afternoon 30–10° 4000–5000 K long again warm, mellow golden-ish toward
evening
Night (moon) — 6500–10000 K
(moonlight)
soft, cool low, blue, mysterious all light = practicals/
moon
Night (city) — mixed per practical colorful pools neon/lamps = the
palette (D02)
Underwater — 4000→deep blue none caustics + falloff depth tint, shafts
Interior (day) window
light
5000–6500 K soft, raked directional through
windows
light = geometry
(window shape)
Interior (night) lamps/fire 1800–3200 K warm pools intimate, contrasty practicals anchor
(D108)
22.2 WEATHER LIGHTING TABLE
Weather Light behavior Palette notes
Clear hard sun, blue sky fill, long shadows full contrast
Overcast giant softbox (clouds) — soft, directionless, low contrast muted, gray-blue, "flat" mood
Rain diffused + wet reflections (light multiplies) desaturated, glints on wet
Fog/mist light scattering, halos, shafts milky, volumetric (D111)
Snow overcast + high albedo bounce (everything reflects) bright, blue shadows
Storm dark sky, intermittent harsh light, lightning flashes (D101) extreme contrast
Dust storm warm haze, low visibility orange, gritty
Smoke (battle/fire) orange ambient, rim glow everywhere fire-lit
DEPTH CHAPTER 22 — THE LIGHTING & MOOD ENCYCLOPEDIA

22.3 TWELVE MOOD RECIPES (key → fill → rim → extras,
with ratios & temps)
Use "intensity ratios" (key=1) as a language; fine-tune per scene.
Heroic sunrise (epic): key warm sun 3200 K @ 1.0 low angle · cool sky fill 7000 K @ 0.15 ·
strong rim 3500 K @ 0.6 behind subject · lens glow, volumetric shaft. Ratio key:fill ≈ 6:1. Subject
rim-lit, background silhouette mountains.
Intimate candlelight: key = practical candle (point light 1800 K @ 0.8 near face) · no fill (or
0.05 cool bounce) · rim = faint cool 6000 K @ 0.1. High contrast, warm pools, black surroundings.
Mysterious night (moon): moon key 8000 K @ 0.4 high behind · cool fill 6500 K @ 0.2 ·
practical lamp 2400 K accent @ 0.3 · mist volume density 0.01. Blue + warm accent = the
cinematic standard.
Noir/hard-boiled: single hard key (spot, narrow, 4000 K) @ 1.0 from the side · no fill (or 0.02) ·
venetian-blind shadows (a masked light). Crushed blacks, harsh shadows, faces half-lit.
Horror: key from below (practical lantern at ground level, 2000 K @ 0.7) · deep black fill · rim
flicker (flicker driver on emission/light — D54) · haze volume 0.02 · shafts through cracks.
Melancholy overcast: giant area light (softbox sky, 6500 K) @ 0.8 from above-front · fill 7000 K
@ 0.4 · no rim · slight desaturation in grade (D119). Flat, gray, quiet.
Romance/golden: warm golden-hour key 3000 K @ 0.9 low back-side · warm fill 4500 K @ 0.3 ·
big soft rim 3500 K @ 0.5 · haze + lens glow. Everything glows; skin loves it.
Cyberpunk/neon: no key sun — practicals as keys: magenta/cyan area lights (6000 K cool +
15000 K magenta tint... use color not Kelvin) @ 0.7 each side · rim green @ 0.4 · wet floor
reflections. Colored light pools, deep blue ambient.
Fantasy magic: cool ambient 7000 K @ 0.3 · magic-emission light source (the spell itself as an
area light — D101) colored @ 0.8 near the caster · rim = spell color @ 0.5 · particles + glow.
Ancient ruin (reverent): single shaft: spot 4500 K through a window/opening @ 1.0 hitting dust
volume · ambient 6000 K @ 0.2 · long shadows, god-ray. Volume is the star.
Alien/surreal: two-tone hard lights (one cool 8000 K, one warm 2500 K) from odd angles (below
+ side) @ 0.8 each · no fill · fog volume, colored. Unnatural angles = unease.
Morning realism (slice of life): window key (area light mimicking a window, 5500 K @ 0.9, soft)
· room fill (bounce from walls) 4500 K @ 0.3 · practical lamp off · light rays through dust. Soft,
lived-in.
1. 
2. 
3. 
4. 
5. 
6. 
7. 
8. 
9. 
10. 
11. 
12. 
DEPTH CHAPTER 22 — THE LIGHTING & MOOD ENCYCLOPEDIA

22.4 LIGHTING PATTERNS (portrait/figure arrangements)
Pattern Setup Effect
Rembrandt key 45° side, raised; small triangle of light on the
shadow cheek
classic dramatic portrait
Butterfly
(Paramount)
key directly in front, above eye level glamour, idealized; nose shadow like a
butterfly
Split key at 90° side — half the face lit mystery, duality, noir
Loop key 30–45°, nose shadow loops onto cheek natural, flattering
Rim/silhouette subject between camera and key, key behind drama, anonymity, separation
Three-point key + fill + rim (D108) the universal base
Practical-only only in-scene sources realism, lived-in (D108)
Chiaroscuro strong key + deep shadows, single source painting-like, high drama
22.5 COLOR THEORY FOR LIGHT (palette decisions, D02/
D119)
Scheme Lights Effect Use
Complementary (warm/
cool)
warm key + cool fill (or
reverse)
the cinematic standard;
separation + energy
most film lighting
Split-complementary key + two adjacent-to-
complement fills
richer color, less harsh fantasy, stylized
Analogous all lights in one hue family unity, calm, cohesive mood natural scenes
Monochromatic one hue, varied intensity minimal, oppressive, elegant noir, alien
T emperature contrast warm practicals vs cool
ambient
depth + storytelling (inside/
outside)
interiors, night
scenes
Accent color small saturated light on one
element
focal point (D104) the map, the magic
item
Color temperature memory:  candle 1850 K · tungsten 2700–3200 K · halogen 3400 K · sunrise
3500 K · daylight fluorescent 4000–4500 K · noon sun 5500 K · electronic flash 5500–6000 K ·
overcast 6500 K · shade 7000 K · blue sky 10000 K · moonlight ≈ 4100 K  but perceived as cool
(moonlight = warm sunlight scattered — film convention treats it cool). Kelvin vs tint:  Kelvin sets
warm/cool;  tint (magenta/green) fixes sensor/logic casts — use both in the light color or grade
(D118).
22.6 CONTROLS & DISCIPLINE (making light manageable)
Light units & exposure: use physical light units (W for sun/area, lm for point/spot, cd/m²) and
set exposure in the render/color management — then light intensities are comparable across
shots (consistency!).
Light Linking (4.x): a light affects only listed objects — the pro tool for: excluding a light from
the background, adding a "face light" that only touches the hero, keying a prop without washing
the set. Use it liberally.
• 
• 
DEPTH CHAPTER 22 — THE LIGHTING & MOOD ENCYCLOPEDIA

Light groups: assign lights to groups → render as separate passes (D115) → relight in comp
(multiply/grade per group). The film-industry standard workflow, fully available in Blender.
IES profiles: real lamp intensity patterns (photometric web files) — instant realism for practicals
(streetlights, desk lamps); free IES libraries exist.
Shadow discipline (D109 recap): per-light shadow softness by size/distance; AO pass for
contact (never skip); shadow color from environment; light linking to keep hero shadows clean.
The lighting checklist: (1) mood/time set from D02; (2) HDRI/sun base; (3) key → fill → rim; (4)
practicals explain the light; (5) light linking for control; (6) light groups for comp; (7) exposure
normalized; (8) volumetric density budgeted (D111); (9) continuity across shots (same sun, same
temp); (10) test render in final color management.
• 
• 
• 
• 
DEPTH CHAPTER 22 — THE LIGHTING & MOOD ENCYCLOPEDIA
