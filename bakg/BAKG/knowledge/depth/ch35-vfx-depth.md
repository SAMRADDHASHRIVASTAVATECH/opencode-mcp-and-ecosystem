# Depth Chapter 35 — VFX & Effects Depth

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 210–213 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 35 — VFX & EFFECTS DEPTH
Expands D100, D101, D87, D95–D98. The complete effects craft: the layered-effect method, particle-
system recipes, fire/smoke/fluid tuning tables, magic-system design, and how effects integrate with
lighting, compositing, and the story.
35.1 THE LAYERED-EFFECT METHOD (the professional
effects recipe)
Every screen effect is 4–7 layers that fire in a designed sequence.  Design the layers before
building anything:
Layer What it is Sells Examples
1. Core the essential
element
the effect's identity the bolt, the flash, the fireball
2. Volume/mass the bulk weight & substance smoke puff, glow cloud, expanding ring
3. Debris/
secondary
the fragments energy & chaos sparks, chips, droplets, embers
4. Light the illumination integration (lights the
scene!)
flash light, emissive core, bounce
5. Trail the motion history speed & arc light streak, spark arc, dust wake
6. Interaction the world's response realism (grounding) scorch mark, debris scatter, wet
splashes
7. Composite the film layer polish glow, flare, chromatic aberration,
streaks
Sequence per beat (D100): anticipation (build 2–6 frames) → burst (impact 2–6 frames, hit-stop) →
dissipation (smoke/embers/settle, 10–60 frames). Each layer has its own timing in the sequence —
core is instant, volume lags 2–4 frames, debris arcs outward, trail fades.
DEPTH CHAPTER 35 — VFX & EFFECTS DEPTH

35.2 PARTICLE-SYSTEM RECIPES (the GN way, D85/D87)
Effect Recipe Key parameters
Sparks GN: points → velocity (radial + gravity) →
instance small emissive cones
count 200–2000; speed 5–20 m/s; lifetime 0.5–2 s;
drag 0.1–0.5
Embers points with turbulence force (D88) + emissive,
rising
speed up 1–3; turbulence 0.5–2; flicker via material
pulse
Dust motes low-density points + turbulence in light shafts count 500–5000; size 0.5–3 cm; slow drift
Rain streak instances (elongated) with gravity +
wind
speed 15–30 m/s; angle = wind (D99); splashes on
impact (interaction layer)
Snow drifting points with sine sway + slight
turbulence
slow fall 1–3 m/s; sway amplitude
Debris
(impact)
points with radial blast + gravity + spin count 30–300; blast 5–15 m/s; lifetime 1–3 s
Leaf/wing
flutter
curves or planes with noise-driven rotation rotation noise; flutter amp; wind dir
Magic
sparkles
points with attract/repel force fields (magnetic!)
+ emissive + fade
force field at the hand; lifetime short; color =
magic palette (D101)
Crowd instanced character variants (Ch 20.4) on a grid
with bobbing
count by distance culling (Ch 26)
The GN pattern:  distribute points (mask) → randomize transform → instance → animate attributes
(position/rotation via fields/noise) → (optionally) realize for deformation.  Always instance, never
duplicate (Ch 26.1).
35.3 FIRE & SMOKE TUNING TABLE (Mantaflow — D95/
D96)
Effect Divisions Fuel/Temp Turbulence Notes
Candle flame 32–64 low fuel, low temp low small domain; short life
T orch 64–128 medium fuel medium add flicker light (D54)
Campfire 128–192 medium fuel medium-
high
embers layer + glow
Explosion (quick) 128–256 high fuel, instant very high expand fast; add debris + light
Smoke plume
(chimney)
64–128 high fuel, low temp (no
fire)
low-medium buoyancy low, steady
Dust cloud 96–192 no fire, low temp medium dissipate; no flame
Dragon breath 128–256 high fuel stream high fire + soot + heat distortion
(comp)
The rules: adaptive domain ON  (D95 — the #1 fire/smoke perf lever); temperature drives rise;
unburnt fuel = soot (dark smoke); flame color = temperature ramp (white core → yellow → orange →
red — connect the "Fire" attribute to emission via ColorRamp); render fire/smoke as a separate pass
(D115) and composite (35.6).
DEPTH CHAPTER 35 — VFX & EFFECTS DEPTH

35.4 MAGIC & ENERGY SYSTEMS (D101 in full)
The system-first rule (D02):  every magic system has a color language, a motion language, and a
cost. Write the rules, then every spell obeys them:
Magic type Color Motion signature Cost visual
Fire magic red/orange/gold flicker, spread, upward heat shimmer, soot
Ice magic cyan/white crystallize, stop, shatter frost growth, sudden stillness
Light magic white/gold clean, linear, radiant glow bloom, lens flare
Shadow magic purple/black absorb, creep, dissolve darkness pooling, silhouette erasure
Nature magic green/brown grow, curl, bloom vines, petals, pollen
Storm magic electric blue/violet jagged, arc, crackle lightning branches, ozone glow
Blood magic red/dark throb, bind, sacrifice veins, runes, drain
Arcane/neutral teal/purple geometric, precise, layered rune circles, glyphs, sigils
Spell recipes: - Energy bolt: emissive sphere core + trail curve (emissive profile, fading alpha) +
particles + light flash + impact burst (35.1 layers 1–7). The cast gesture (D74/D75) is half the effect.
- Shield/ward: shell shader (fresnel rim glow — Ch 17 recipe 10) + pulse driver + orbiting particles
+ light;  shatter = pre-fractured shell pieces (D97) launched outward. -  Portal: emissive ring +
inward swirl (particles following a spiral curve) + distortion (comp) + light shaft + sound (Ch 23). -
Runes/circles: emissive  glyph  planes  (alpha  mask)  +  slow  rotation  +  pulse  +  ground  light.  -
Healing: green motes rising (particles with attract field) + gentle glow + warm light;  no sharp
motion. - Telekinesis: the object drifts with weight  (float + sway, never perfectly still — D101) +
subtle aura + dust disturbed. - Lightning: jagged curve (animated, branched) + emissive + flicker
(noise driver) + glow + crackle sound; strike = 3–6 frames of white flash then the bolt.
Every spell gets:  its own light (the integration layer), its own sound (Ch 23), and its effect on the
world (interaction layer — scorch, frost, vines, debris) — magic that doesn't touch the world reads as
fake.
35.5 IMPACT & DESTRUCTION EFFECTS (D97/D98 in full)
The impact formula (recap D74/D100): anticipation → strike (2–6 frames) → hit-stop (2–4 frames
of near-freeze — sells force) → burst (sparks + debris + flash) → dissipation (dust/smoke + settle).
Impact layers by material:  | T arget | Burst | Debris | Dust | Sound | |---|---|---|---|---| | Stone | rock
chips | chunks (D98) | gray dust cloud | crack + rumble | | Metal | sparks (bright, sharp) | none/minor
| none | clang + ring | | Wood | splinters | shards | light dust | crack + thud | | Glass | shard planes
(pre-fractured) | glitter | none | shatter + tinkle | | Water | spray droplets | foam | splash ring | splash
+ drip | | Flesh | blood/flesh particles | — | none | thud + wet | | Snow | white puff | clumps | snow
spray | whoomph |
Destruction choreography (D97):  pre-fracture (Cell Fracture / GN Voronoi — D97) → glue shards
with rigid-body constraints (breaking force set) → impactor (rigid or keyed) → simulate → layer dust +
sparks + debris →  "break the wall in a separate sim, then place the broken version"  (the
production trick — reuse states).
DEPTH CHAPTER 35 — VFX & EFFECTS DEPTH

35.6 COMPOSITING INTEGRATION (making effects sit in
the shot)
Render effects as separate passes (D115): FX pass (emissive/particles) + beauty. Grade,
glow, and streak the FX pass alone — never bake glow into the beauty.
Glow (Glare node): Fog Glow or Streak — threshold to the bright emissive only; keep it subtle (a
hint, not a haze) unless the style demands bloom (toon — Ch 18.7).
Motion blur: add to fast effects (Vector Blur in comp or render MB, D112) — unblurred fast
particles look like floating dots.
Heat distortion: displace the background with noise (comp) behind fire/energy — the classic
cheap realism trick.
Color: effects should sit in the palette (D02/D119) — a white-hot core, saturated mid, cool falloff;
never out-of-palette colors.
Light integration: the effect's light must exist in the scene (a real light or baked contribution) —
the character should be lit by the spell they cast.
35.7 VFX FAILURE MODES & FIXES
Symptom Cause Fix
Effect looks pasted on no light layer / no interaction add the flash light + world response
Particles look like dots no motion blur / no size falloff blur + taper size + trail
Glow everywhere Glare threshold too low threshold to emissive only; reduce
Fire looks flat no temperature ramp / no soot ColorRamp on Fire attribute + soot
Smoke is gray soup no turbulence / no dissipation turbulence + dissipation settings (D95)
Destruction looks clean no dust/debris layers add D98 debris + dust volume
Effect out of palette no color rules enforce the magic color language (35.4)
Effect too slow/heavy full-res sims everywhere adaptive domain + separate pass + LOD (Ch 26)
Spell doesn't feel magical no sound / no gesture add sound (Ch 23) + cast gesture (D74)
1. 
2. 
3. 
4. 
5. 
6. 
DEPTH CHAPTER 35 — VFX & EFFECTS DEPTH
