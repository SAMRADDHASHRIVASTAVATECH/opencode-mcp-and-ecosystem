# Chapter 11 — VFX: Impacts, Magic, Energy, Effects Design (D100–D101)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 99–100 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 11 — VFX: IMPACTS, MAGIC, ENERGY,
AND EFFECTS DESIGN
Domains D100–D101. Visual effects are the theater of a film: the impact frame, the magic spell, the
energy trail. VFX must read instantly, sit in the shot believably, and never out-shout the story.
D100 — VFX [SIT]
DEF: Designed visual effects: impacts, explosions, sparks, trails, elementals, and environment effects
— built from particles, geometry, shaders, sims, and compositing.  WHY: VFX are  choreographed
illusion: every effect has a story beat (the hit, the spell, the reveal) and must read in 2–6 frames. The
discipline is  designing the effect, not just piling on particles.  The VFX design method:  1.  Beat
definition: what is the effect for? (sell the hit / sell the power / sell the scale). The effect's shape
should match the story: an impact bursts outward (from the point), a portal sucks inward, a shield is a
surface. 2. Layering (every good effect is 4+ layers): - Core (the essential element: the flash, the
bolt, the flame). -  Volume (the mass: smoke puff, glow, cloud — sells weight). -  Debris/secondary
(chips, sparks, droplets — sells energy). - Light (a light or emissive flash that lights the scene — sells
integration!). - Trail (the motion history — arc of sparks, light streak). - Composite (glow, lens flare,
chromatic aberration, motion blur — the "film" layer, D117). 3.  Impact formula (recap D74):
anticipation (build) → impact (2–6 frame burst, hit-stop) → dissipation (smoke/embers/settle). 4. Style
discipline: realistic vs stylized — stylized effects use bold shapes + strong colors + clear silhouettes;
realistic effects use physics + subtlety. Match the film's style (D138) — a cartoon shouldn't get
photoreal smoke.  Blender toolkit for VFX:  -  Particles (D87) / GN (D85)  for sparks, debris,
embers, swarms. - Quick Effects (built-in menu): Quick Smoke, Quick Explode, Quick Fur — instant
starts. -  Emissive materials + EEVEE bloom / Cycles glow  (D30 emission). -  Light flashes:
animate an area/point light's power + color (the light layer). - Sims (D95/D96/D97) for fire/smoke/
destruction. - Curves for trails, lightning, energy arcs (add emissive profile to a curve — the "beam"
trick). - Compositing (D117) for glow, streaks, chromatic aberration — half the effect is added in
comp. PARAM: layer list; effect duration (frames); burst size; color palette; light involvement; trail
style; sound cue sync (D133). MIST: effect without a beat (random particles = noise); no light layer
(effect looks pasted on); every effect the same (no palette discipline); effects that obscure the action.
DIAG: watch the effect at 25% speed — the core should read first, then layers resolve. EDGES: →
D101 magic, → D87/D95–D98, → D117 comp, → D74 impacts.
Deep chain — VFX → Effect → Layers → Beat
Beat (anticipation → burst → dissipation) → core element → volume → debris → light → trail → comp
(glow/flare/CA)
D101 — MAGIC / ENERGY EFFECTS [SIT]
DEF: Supernatural  effects:  spells,  auras,  energy  bolts,  runes,  portals,  elementals,  telekinesis,
shapeshifting glows.  WHY: Magic effects must feel  systematic (world rules, D02: what does this
magic  look  like,  how  does  it  move?)  and  integrated (light  the  scene,  interact  with  materials).
Signature recipes:  -  Energy bolt/projectile:  core  emissive  sphere/streak  +  trail  (curve  with
emissive profile + fading alpha) + glow (comp) + impact burst (D100) + the casting animation (the
CHAPTER 11 — VFX: IMPACTS, MAGIC, ENERGY, AND EFFECTS DESIGN

character's gesture — D74/D75). Trail color follows the magic's palette. - Aura/shield: transparent
shell shader (transmission + fresnel edge glow — "rim glow" via fresnel → emission) + subtle pulse
(driver on emission, D54) + particles orbiting. -  Portal: ring + inward swirl (particles following a
curve spiral, D87) + distortion (comp or shader trick) + glow + light. -  Lightning/arcs: animated
curves (jagged, with branches) with emissive profile + flicker (noise driver on emission) + glow;
sound sells it (D133). - Runes/circles: emissive plane/curve glyphs (alpha mask) + slow rotation +
pulse + light. - Elementals (fire/water/earth/air beings): a creature made of the element: fire =
flame sim shaped by a rig (D96 + mesh follow); water = fluid + fresnel shader; earth = rock particles
+ rubble body; air = dust + wind streaks. - Telekinesis: object floating (animated, D65 easing) +
subtle aura + weight (the object sways, drifts — never floats perfectly still). System rules (from
D02): every  spell  has  a  color  language (healing  =  green,  necromancy  =  purple...),  a  motion
language (fire magic flickers, ice magic crystallizes — sudden stops, light magic is clean/linear), and a
cost (casting effort in the character — D75).  PARAM: palette; motion style; glow strength; light
involvement; particle density; duration; sound cues. MIST: all magic = generic blue glow; no system
(every spell different art style); effects that don't interact with the world (no light, no reaction from
surfaces — wet stone should reflect the glow!). EDGES: → D100, → D02 world rules, → D31 shaders,
→ D117 comp, → D74.
CHAPTER 11 — VFX: IMPACTS, MAGIC, ENERGY, AND EFFECTS DESIGN
