# Depth Chapter 17 — Materials & Shaders Encyclopedia

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 142–149 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 17 — THE MATERIALS &
SHADERS ENCYCLOPEDIA
Expands D30–D36. 120+ materials with exact Principled BSDF settings, node recipes, and the map
set each material needs. Use the Principled BSDF (D30) as the base for everything; adjust these
values, then add maps (D26) for variation. "Roughness variation" is the #1 realism upgrade: few real
surfaces are a single value.
Legend: BC = base color · R = roughness · M = metallic · Sp = specular · IOR · Tr = transmission ·
SSS = subsurface (radius ≈ 0.1–0.3 × scale) · Cl = clearcoat · E = emission. All values are starting
points — light and context shift them.
17.1 THE PRINCIPLED PARAMETER REFERENCE (quick
master chart)
Input Range Typical Behavior
Base Color RGB albedo map The "paint" — never carry lighting
Roughness 0–1 0.1–0.9 0 = mirror, 1 = matte; never a single value — vary it
Metallic 0/1 0 or 1 Dielectric vs metal; keep binary
Specular 0–1 0.5 Reflection tint at normal incidence (skin 0.5, water 0.5, glass
0.5, diamond 0.5-ish)
IOR 1.0–2.5 1.45 (glass) Refractive index; drives Fresnel
Transmission 0–1 0/1 1 = transparent (glass/water); combine with IOR + roughness
Transmission
Roughness
0–1 0–0.1 Frosted glass/water surface
Subsurface 0–1 0–1 Translucency amount (skin 0.2–1, wax, milk)
Subsurface Radius RGB ~1, 0.25, 0.15 Scatter color mix — red-heavy for skin
Subsurface Color RGB reddish for skin The scattered light color
Subsurface Scale world
units
0.01–0.05
(chars)
How deep light penetrates
Emission RGB black = off Self-lit (magic, screens, fire)
Emission Strength 0–∞ 1–50 Nits-ish; fire/neon needs 5–50
Alpha 0–1 1 Clip/transparency (leaves, hair cards)
Sheen 0–1 0.5 (fabrics) Cloth velvet/wool glow
Coat 0–1 0.5–1 (paint/
varnish)
Clearcoat layer (car paint, lacquer, wet gloss)
Coat Roughness 0–1 0.05–0.3 Clearcoat micro-roughness
Anisotropic 0–1 0.5 (brushed) Directional highlight (brushed metal, silk)
Anisotropic Rotation 0–1 per-UV Anisotropy direction
DEPTH CHAPTER 17 — THE MATERIALS & SHADERS ENCYCLOPEDIA

17.2 METALS (M=1 always; BC = tint; vary R for wear)
Material Base color Roughness Anisotropic Notes
Polished gold #FFC34D → #8a5a00
gradient
0.05–0.2 0 Use a 2-tone BC gradient for
the classic gold look
Brushed gold #E8B45A 0.3–0.5 0.6–0.8 (rotated
90°)
Brush direction = anisotropic
rotation
Silver
(polished)
#D8DCE0 0.05–0.15 0 Cold white tint
Silver
(tarnished)
#9aa0a8 + dark grime
mask
0.3–0.7 0 Grime mask → roughness/BC
mix
Copper #C67C5A 0.1–0.3 0 Warm pink metal
Copper
(verdigris)
green-blue #4a9e8a
patches
0.3–0.6 0 Patina mask over copper
Brass #C9A94E 0.2–0.4 0 Yellow-ish; aged = darker +
green
Bronze #9C6B3E 0.2–0.5 0 Dark warm; statue look =
patina
Steel
(polished)
#B8BDC2 0.1–0.25 0 Neutral bright
Steel
(brushed)
#A9AEB4 0.35–0.5 0.5–0.7 Machinery
Stainless
(mirror)
#C9CED2 0.02–0.08 0 Chromey, cold
Rusted iron #6a4020 BC + orange
#B45A2A rust mask
0.5–0.8 (rust), 0.2
(metal)
0 T wo-material mix: metal ↔ rust
via mask
Cast iron #3a3d42 0.4–0.6 0 Matte dark, slight grit normal
Aluminum #C7CCD1 0.2–0.4 0 Light, slightly soft
Titanium #9aa0a6 0.2–0.35 0 Darker than steel, warm-
neutral
Chrome #D5DADF 0.02–0.06 0 Mirror finish; environment is
90% of the look
Blackened
steel
#1c1e22 0.3–0.5 0 Gunmetal
Damascus/
pattern
BC with streak normal 0.15–0.3 0.2 Pattern via normal/bump
streaks
Weathered
metal
BC + grime + scratches 0.1–0.7 (masked) optional The mask does the work —
always mask wear
DEPTH CHAPTER 17 — THE MATERIALS & SHADERS ENCYCLOPEDIA

17.3 ORGANIC SURFACES (skin, flesh, chitin, bone…)
Material BC R SSS Notes
Caucasian
skin
#C69C80 ± tint 0.4–
0.6
0.5–1, radius ~0.02–
0.04, color #E05A3A
Add freckle/vein masks; roughness
varies (forehead oily 0.3, cheeks 0.5)
Dark skin #5a3a2a – #2e1f14 0.35–
0.55
higher (deeper
scatter), color deep
red
Subsurface shows less; highlight
cooler
Wet skin skin + roughness × 0.3–
0.5, coat 0.5
0.1–
0.3
same Add a coat layer for the sheen (rain,
sweat)
Scar tissue desaturated BC +
roughness 0.7–0.9
0.7–
0.9
low Waxy, matte
Aged/
wrinkled skin
darker, more yellow 0.5–
0.7
reduced Pores/wrinkle normal does the heavy
lifting
Leather #5a3a24 0.4–
0.7
0.05 Grain normal; worn = roughness
variation
Wet leather #3a2412, R 0.2–0.4 0.2–
0.4
0 Slick, dark
Fur (guard
hair)
per-species, melanin-
driven
0.3–
0.6
0 (strand shader) Principled Hair BSDF (D43)
Feathers per-species 0.3–
0.5
0 + Coat 0.3–0.6 for iridescence; alpha
for gaps
Fish scales base + pattern normal 0.3–
0.6
0.1 + Coat 0.3; iridescence via coat color
Reptile scales base + scale normal 0.3–
0.6
0.1–0.2 Wet = R down + coat
Snake skin pattern BC 0.4–
0.6
0.1 Scale rows via normal
Chitin (insect) dark brown/black 0.2–
0.5
0 Hard gloss, slight iridescence (beetle:
coat + anisotropic)
Horn #d8c9a0 → #4a3a24
gradient
0.2–
0.4
0.05 Keratin; ridged normal
Bone #E6DCC0 0.3–
0.5
0.05 Porous — subtle; teeth are glossier
Ivory #F3EAD0 0.2–
0.3
0.05 Warm, smooth
T eeth
(enamel)
#F5F0E0 with #D9C9A0
dentin near gums
0.1–
0.2
0.05–0.1 (thin) Slight transmission; never pure white
T ongue #C97A7A 0.3–
0.5
0.3 (wet) + coat 0.3, R 0.2 for wet gloss
Coral #E08A7A / per species 0.4–
0.7
0.2 Porous normal; slight SSS for glow
Moss #5a7a3a 0.8–
1.0
0 Fuzzy — high roughness + alpha
detail
Wet organic
(slime)
green/gray, R 0.05–0.2,
Tr 0.2–0.5, SSS 0.5
0.05–
0.2
0.5 Transmission + SSS + strong specular
= slime
DEPTH CHAPTER 17 — THE MATERIALS & SHADERS ENCYCLOPEDIA

17.4 LIQUIDS
Material BC R IOR Tr Notes
Clear water near-white/transparent 0–0.1 1.33 1 Add absorption (deep = darker, blue)
Murky
water
brown/green tint 0.1–0.3 1.33 0.8–
1
Volume absorption carries the murk
Blood #6a1010 0.2–0.4 1.33 0.5 SSS red for pool edges; thick = higher viscosity
look (R down)
Oil #201a10, dark 0.05–
0.15
1.47 1 Rainbow iridescence: coat + thin-film trick
Mercury #D0D4D8 0.02 2.0 1 Metal-like liquid; R near 0
Lava #FF6A1A core →
#FFD24A
0.4–0.6 — 0 Emission 5–20 + glow; crust = dark rock with
emissive cracks
Slime/goo green, R 0.05–0.2 0.05–0.2 1.4 0.6–
1
+ SSS + coat; blobby displacement
Magic
liquid
any + emission 0.1 1.4 0.8 Emission + transmission (potion)
Ink #0a0a12 0.3 1.4 0.9 Very dark transmission
DEPTH CHAPTER 17 — THE MATERIALS & SHADERS ENCYCLOPEDIA

17.5 STONE, MINERALS & GEMS (most: M=0, high
roughness except gems)
Material BC R IOR Notes
Granite speckled gray 0.7–0.9 — Speckle normal + BC variation
Marble white/gray + vein
mask
0.2–0.4 — Veins via mask; polished = coat 0.5–0.8
Limestone/
sandstone
tan 0.8–1.0 — Porous; soft
Slate dark gray 0.5–0.7 — Layered normal
Concrete #9a9a94 0.9–1.0 — Grout/aggregate normal; never smooth
Brick red-brown, mortar
mask
0.7–0.9 — Mortar = recessed (bump)
Basalt/obsidian near-black 0.1–0.3 (obsidian), 0.5
(basalt)
1.5 Obsidian = glassy black, sharp normal
Quartz crystal white/clear 0.05–0.2 1.54 Tr 0.9–1 + faint tint; facets via normal
Amethyst purple tint 0.1–0.2 1.54 Tr 0.8 + SSS glow
Diamond near-white 0.02–0.05 2.42 High IOR = fire/rainbows; use caustics on/
off carefully (expensive)
Ruby/emerald/
sapphire
saturated color 0.05–0.15 1.76 Tr + SSS for deep color
Jade green 0.2–0.4 1.66 Tr 0.4–0.6 + SSS = the jade glow
Gold ore/rock gold patches on
stone
mixed — Metal mask: gold (M=1) vs rock (M=0)
Ice pale blue 0.02–0.1 1.31 Tr 1 + SSS (deep = bluer)
Frost white, R 0.6 0.6 — Tiny crystals normal; matte
Snow white 0.7–0.9 — Soft; fresh snow sparkles = specular 0.3–0.5
with fine normal
Salt flat crust white/beige 0.4–0.6 — Cracked polygon pattern normal
17.6 WOOD
Material BC R Notes
Oak (fresh) #9a6a3a 0.3–0.5 Grain normal along length
Oak (aged) #6a4a24 0.5–0.7 + wear mask
Pine #c9a66a 0.3–0.5 Lighter, knotty
Ebony #1a1210 0.15–0.3 Very dark, tight grain
Bamboo #d9c28a 0.3–0.5 Node ridges normal
Bark #4a3a2a 0.7–0.9 Deep ridges
Varnished wood + coat 0.5–0.8, coat R 0.1 0.1–0.3 The clearcoat sells the varnish
Wet wood R × 0.3 0.1–0.3 Rain!
Driftwood gray-beige 0.6–0.8 Bleached, smooth
DEPTH CHAPTER 17 — THE MATERIALS & SHADERS ENCYCLOPEDIA

17.7 FABRICS (Cl = coat where sheen matters; Sheen for
velvet/wool)
Material BC R Sheen Notes
Cotton per color 0.6–0.8 0 T will weave normal; soft
Denim blue, faded 0.7–0.9 0 Diagonal weave + wear
Silk per color 0.2–0.4 0 + Coat 0.3; anisotropic 0.5 (sheen shifts with UV)
Satin per color 0.1–0.3 0.3 Glossy surface, matte back — two materials
Velvet deep color 0.8–1.0 1.0 Sheen 1 + very dark; the classic velvet trick
Wool muted 0.7–0.9 0.3 Fuzzy normal; heavy drape (D39 stiffness)
Leather (see 17.3) — — — —
Linen off-white 0.7–0.9 0 Coarse weave
Mesh/net per color + alpha 0.6 0 Alpha texture does the holes
Wet cloth R × 0.3, darken BC 0.1–0.3 0 Rain/fabric — darken + gloss
Metal-thread brocade per pattern 0.3 0 Metallic mask on fabric (M=1 patches)
17.8 PLASTICS, RUBBER, GLASS, COMPOSITES
Material BC R IOR Notes
Glossy plastic per color 0.05–0.15 — + coat 0.5–0.8 (toy shine)
Matte plastic per color 0.4–0.6 — No coat
Rubber black/dark 0.7–1.0 — Tires, gaskets
Silicone pale 0.2–0.4 — + coat 0.3, soft
Clear glass transparent 0.02–0.1 1.45 Tr 1; edge tint via absorption (green for float glass)
Frosted glass transparent 0.2–0.4 1.45 Tr 1 + transmission roughness
Stained glass per pane color 0.1 1.5 Tr + emission at edges; lead lines via mask
Acrylic clear 0.05 1.49 Slightly blue edges
Ceramic per color 0.1–0.3 — + coat 0.6; glaze = coat
Porcelain white 0.05–0.15 — High gloss + coat
Carbon fiber black 0.1–0.3 — Anisotropic 0.8 + diagonal weave normal
DEPTH CHAPTER 17 — THE MATERIALS & SHADERS ENCYCLOPEDIA

17.9 EMISSIVE & PHENOMENA (E column = Emission
strength)
Material BC E Notes
Fire core #FFFFFF → #FF9A00 10–50 Emission + volume (D96)
Ember #FF6A00 5–20 Small + flicker driver
Neon saturated 5–15 + glow in comp (D117)
Magic aura any 3–10 + fresnel rim emission (D101)
Screen/display per UI 2–8 + slight glow, no SSS
Bioluminescent green/blue 3–10 + SSS for organic glow
Lightning #C8E4FF 20–100 Brief — animate strength (D101)
God-ray particles warm 2–5 Dust motes (D87/D111)
Eyes (creatures) amber/green 2–8 + coat; the "eyes in the dark"
17.10 TEN NODE RECIPES (Shader Editor, Principled
base)
Roughness variation (universal): Noise T exture (scale ~200) → ColorRamp (0.25→0.75) → Mix
(factor) between two roughness values. Cheap, massive realism.
Grunge mask: Voronoi (scale 50–500) → ColorRamp → used as Mix factor between clean & dirty
BC/R. 
Scratched metal: Noise stretched (mapping: X×100) → ColorRamp → Mix roughness 0.1 ↔ 0.6.
Two-tone metal wear: Mask (edge of geometry via AO / bevel mask) → Mix fresh metal ↔ rusted
metal.
Skin color variation: low-frequency Noise (scale 5) → subtle Mix on BC + roughness (red cheeks
mask via vertex paint or UV mask).
Wet surface driver: a custom property "wetness" (0–1) on the object → drivers on Mix factors:
BC darken (×0.6), roughness → ×0.3, coat → +0.5. One control wets anything (D99/D54).
Crystal/faceted: Transmission 1 + IOR 1.54 + noise-driven roughness + slight emission masked
to edges (fresnel → emission). The fantasy crystal (4.1 recipe).
Slime: Transmission 0.5 + SSS 0.5 (green) + coat 0.4 + roughness 0.1; add displacement noise
for blobs.
Toon 2-tone (see Ch 18): Shader to RGB → ColorRamp (2 stops) → mix with base color.
Magic rim: Fresnel (IOR ~1.4) → ColorRamp → Emission — an edge-glow that works on any object
(D101).
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
DEPTH CHAPTER 17 — THE MATERIALS & SHADERS ENCYCLOPEDIA

17.11 MAP REQUIREMENTS PER MATERIAL CLASS
(minimum viable set)
Class Minimum maps High-end set
Hero organic (skin) BC, R, Normal + SSS map, AO, pore normal, tint masks
Metal BC, R (masked) + Normal, AO, anisotropy direction, grime mask
Fabric BC, R, Normal (weave) + Sheen mask, wear mask, AO
Glass/water BC (tint), R + Absorption, normal (surface), AO
Stone BC, R, Normal + AO, displacement, moss/dirt masks
Emissive E color + strength mask (runes), fresnel mask
The universal truth:  BC without R variation = plastic. R without BC variation = clean lab. Normal
without AO = floating. AO without both = dead. The trio — BC variation + R variation + AO — is
90% of "realistic material." The rest is IOR/SSS/coat correctness.
DEPTH CHAPTER 17 — THE MATERIALS & SHADERS ENCYCLOPEDIA
