# Chapter 10 — Physics & Simulation (D87–D99)

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 94–98 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

CHAPTER 10 — PHYSICS & SIMULATION
Domains D87–D99. Physics simulation adds the natural world: falling, flowing, burning, tearing, and
weather. Sims are powerful, expensive, and error-prone — the discipline is knowing when to simulate,
what to fake, and how to cache.
D87 — PARTICLES [SIT]
DEF: Particle systems (legacy) and point/instancing systems (GN-based, D85): many small elements
(rain, sparks, dust, leaves) with motion rules.  WHY: Particles are the cheapest way to add  motion
texture: rain, snow, embers, sparks, crowds, swarms. HOW (the two systems): 1. Legacy Particle
System (modifier): emitter with physics (Newtonian/keyed/boids/fluid), render as Hair (strands) or
Object/Collection instances (rain drops, leaves). Fine for simple effects; being superseded by GN. 2.
Geometry Nodes particle workflow (the modern way): scatter points (D85) → animate via fields
(velocity/noise/curves) → instance objects — fully controllable, integrates with everything. PARAM:
count; lifetime; velocity (normal/random); gravity/wind/force fields (D88); collision; render type; seed.
MIST: particles as heavy geometry (instance, don't duplicate); 100k particles when 5k reads the
same; ignoring force fields (rain falling straight through a roof). EDGES: → D88 force fields, → D99
weather, → D100 VFX.
D88 — PHYSICS [SIT]
DEF: The physics infrastructure: rigid/soft/cloth/fluid/hair solvers, force fields, gravity, collisions, and
caching.  WHY: Every  simulation  type  shares  infrastructure:  scene  gravity  (Scene  →  Physics  →
Gravity), force fields, collision settings, and the cache system. Master the infrastructure once; every
sim type becomes manageable.  Core infrastructure:  -  Gravity: scene-level (9.81 m/s² default);
per-object override possible. Scale matters (D14): at wrong scene scale, gravity looks wrong. - Force
fields: the invisible hands: Force (linear push), Wind, T urbulence, Vortex, Magnetic, Harmonic, and
custom fields — used to add life (wind for cloth/hair, turbulence for smoke). - Collision: objects must
have a  Collision modifier (for cloth/hair/soft) or be rigid-body  participants (for rigid sim); collision
settings: distance, friction, damping, absorption. - Caching: every sim writes to a cache (memory or
disk in the project's cache folder — D123); baking = computing once and storing; always bake to disk
for production (replay stability + speed). - Time scale: sims can be baked at different time steps;
slow-motion = sim at 2× and retime, or use Time Scale in the scene.  PARAM: gravity; force field
strengths/falloff; collision distance/friction; cache location; simulation start/end frames; steps/quality
per solver. MIST: ignoring scale (sims explode/drift); forgetting force fields (windless cloth = dead);
never  baking  (sims  change  between  sessions);  collision  objects  missing.  FAIL: sim  exploding
(instability) — universally diagnosed by: too big steps, too small collision distance, extreme forces,
bad  scale.  FIX: reduce  step  size/raise  quality;  check  scale;  simplify  collision  meshes;  bake
progressively. EDGES: → D89–D99 all solvers, → D114 optimization.
D89 — RIGID BODIES [SIT]
DEF: Simulation of  hard objects: falling crates, tumbling rocks, sliding props — objects that don't
deform.  WHY: Rigid bodies are the workhorse of destruction (D97) and  prop interaction (a kicked
CHAPTER 10 — PHYSICS & SIMULATION

bucket); they're cheap, stable, and fast compared to other solvers. HOW: select object → Physics →
Rigid Body  (Active = moves, Passive = static) → set shape (Box/Sphere/Capsule/Cylinder/Convex
Hull/Mesh — simplify shapes: a convex hull of a crate is perfect, the full mesh is slow) → set mass →
run; collisions happen between objects with rigid body properties; connect parts with  Rigid Body
Constraints (hinge,  point,  slider,  motor  —  for  doors,  chains,  pistons).  PARAM: mass;  friction;
bounciness (restitution); shape; damping (linear/angular); collision groups/masks; constraints (type,
limits, motor).  MIST: full-mesh collision shapes (slow); too much bounce (restitution 1 = pogo);
objects asleep that should move; no passive floor (objects fall through the world).  FAIL: objects
sinking through the floor (collision shape mismatch); jitter at rest (low solver iterations).  FIX: use
simplified shapes; raise solver iterations; add small damping; check collision margin. PERF: convex
hulls everywhere; merge sleeping objects; cache the sim. EDGES: → D97 destruction, → D98 debris,
→ D42 props.
D90 — SOFT BODIES [SIT]
DEF: Simulation of  squishy deformable objects: jelly, flesh, balloons, cloth-like solids.  WHY: Soft
bodies  sell  materials  that  aren't  rigid (a  monster's  belly,  a  gelatinous  cube)  and  add  organic
secondary motion. HOW: Physics → Soft Body on a mesh (with a goal vertex group controlling how
strongly it tries to return to rest — the key control); options: stiffness, damping, plasticity (permanent
deformation), pressure (balloon/inflatable); collision via the Soft Body collision settings. PARAM: goal
weight; stiffness; damping; plasticity; pressure; vertex group for goal.  MIST: full mesh resolution
(slow); no goal group (mesh collapses); using soft body when cloth is the right tool. EDGES: → D88, →
D77 secondary motion, → D100 VFX (slimy monsters!).
D91 — CLOTH PHYSICS [SIT]
DEF: The cloth solver itself (the Cloth modifier, also used by D39 garments): gravity-driven fabric
with  bending,  stretching,  compression,  and  self-collision.  WHY: Cloth  is  the secondary-motion
workhorse  (D39/D77)  and  also  powers  flags,  curtains,  sails,  tents,  and  soft  props.  HOW: Cloth
modifier (D39 details) — the same solver for garments and environmental cloth; key settings recap:
Quality (steps), Mass, Air Damping, Bending Model (Linear = light fabrics; Angular = heavy/stiff;
Bending Model "Bending + Shearing" for woven fabrics), Stiffness, Self-Collision, Collision Object (with
distance/friction), Pinning (vertex group), Sewing Springs (D38). Bending model deep-dive: Linear
(fast, generic); Angular (bends around edges — crisper folds for heavier fabrics); Bending + Shearing
(best woven look, slower). Match the model to the fabric story (D37). PARAM: see D39 + quality/
solver iterations. EDGES: → D39, → D37/D38, → D99 wind.
D92 — HAIR PHYSICS [SIT]
DEF: The hair/strand solver: dynamics for hair, fur, feathers (curves-based in 4.x). WHY: D47 covers
the workflow; here: the solver — pins at the root, bending stiffness, damping, gravity, wind, collision.
Curves hair physics uses a "hair dynamics" simulation that treats strands as chains with stiffness per
strand. PARAM: pin vertex group (roots); stiffness (bending); damping; mass; collision distance; wind
fields; bake. EDGES: → D47, → D44, → D99.
CHAPTER 10 — PHYSICS & SIMULATION

D93 — FLUIDS [SIT]
DEF: Liquid simulation via Mantaflow: pouring, splashing, filling, waves, and viscous fluids.  WHY:
Water and other liquids are among the most visible simulation requests (the user's rainy city!); fluid
sims are heavy and require careful setup — or careful faking (a rain puddle can be a shader + ripple,
D94). HOW (Mantaflow, Blender 4.x):  Domain object (Physics → Fluid → Domain) + Flow objects
(fluid source) + Effectors (obstacles) → set resolution (divisions — the cost driver: 64–256 typical; 64
= coarse, 256 = heavy) → bake (data + mesh/particles). Mesh option generates a surface; particles
(spray/foam/bubble)  add  the  detail;  material  via  Prismatic  BSDF  (D30  water  settings).  PARAM:
resolution divisions; timesteps; viscosity; surface tension; gravity; flow velocity; domain size (keep
the domain tight around the action — the #1 perf lever); mesh resolution. MIST: domain bigger than
needed  (resolution  wasted);  high  resolution  everywhere  (bake  takes  days);  no  effecor  for  the
container (fluid falls through); simulating when a shader + particles would read the same.  FAIL:
exploding fluid (domain too small / steps too few); leaky container (effector without collision). FIX:
smaller domain, coarser bake first (preview), refine; use the spray/foam/bubble particles for realism
at lower mesh res. PERF: bake at low res for layout, high res for final; cache to disk; use the fluid
particles not the mesh where possible. EDGES: → D94 water, → D100 VFX, → D99 rain.
D94 — WATER [SIT]
DEF: Water in all its forms: oceans, lakes, puddles, rain, waterfalls, splashes — both simulated (D93)
and shaded (the 90% case). WHY: Most water on screen shouldn't be a fluid sim — it should be a
material + geometry trick : an ocean plane with an animated displacement shader (the  Ocean
modifier — built-in, spectral waves), a puddle with a ripple shader, a river as a scrolling shader over
terrain.  How to choose:  large bodies = Ocean modifier + water shader (cheap, beautiful); hero
splashes/pours = fluid sim (D93) or pre-made splash assets (D100); rain = particles (D87) + wetness
materials (D31 drivers).  Ocean modifier:  generate wave-displaced mesh (resolution, wave scale,
choppiness) — the standard for seas/oceans; add spray/foam via particles or shader (foam mask from
wave crests). Water material (recap D30):  transmission 1, IOR 1.33, roughness 0–0.05 (calm) to
0.3+ (rough sea), absorption (deep = dark), SSS-lite for shallow glow; wetness shader for surfaces
(darken + specular increase, driven by rain amount — D31 drivers). Interactions: characters in rain
(wet cloth/hair — D39/D47 with wetness), reflections (puddles reflect — D108/D112), splashes at feet
(particles or animated splash assets). MIST: fluid-sim for every puddle; water that doesn't reflect (flat
black); rain with no wet response (characters stay dry — the #1 missed detail in rainy scenes!).
EDGES: → D93, → D30/D31 materials, → D99 rain, → D108 lighting (water glints).
D95 — SMOKE [SIT]
DEF: Smoke/steam/mist simulation (Mantaflow smoke) — the volume part of pyro: billowing, density,
temperature-driven rise. WHY: Smoke adds atmosphere and weight to fires, explosions, chimneys,
and god-rays (D111); it's expensive but transformative. HOW: Domain (Physics → Fluid → Domain,
type Gas) + Flow (smoke source) + Effectors;  use the  adaptive domain option (4.x: "Adaptive
Domain" in the fluid settings) — it shrinks the domain to the smoke, a massive perf win; resolution
divisions 64–256;  temperature drives rise (fuel/heat settings); smoke color/density from the flow
material; render via a Volume shader (Principled Volume — density, anisotropy, color) or as density
pass to composite (D115).  PARAM: divisions; adaptive domain; buoyancy; dissipation; turbulence
(noise strength — extra detail); flow rate; fuel; temperature.  MIST: full-resolution domain for a
CHAPTER 10 — PHYSICS & SIMULATION

chimney (use adaptive); no turbulence (flat puffs); rendering volume directly instead of compositing
density (D117).  PERF: adaptive domain; coarse for layout; volume rendering with denoising; limit
viewport volume display. EDGES: → D96 fire, → D97 explosions, → D111 volumetrics, → D100 VFX.
D96 — FIRE [SIT]
DEF: Flame simulation: the  reacting part of pyro — fuel, heat, and the flame's distinctive shape
(Mantaflow gas with fire). WHY: Fire is iconic VFX (torches, dragons, explosions); the Mantaflow "fire"
option (fuel + temperature) generates flame color via the "Fire" field (rendered as emissive volume).
HOW: same domain as smoke (D95) with Fire (fuel-based) enabled: flow emits fuel; the solver burns
it → heat + flame; fire color via the "Fire Color" ramp (in the Principled Volume: connect "Fire"
attribute to Emission color via Color Ramp — blue core → yellow → orange → red); smoke is the
byproduct (unburnt fuel = soot — dark smoke for a big fire). PARAM: fuel; temperature; flame color
ramp; smoke settings; buoyancy; turbulence; adaptive domain. MIST: fire without soot (looks like a
neon sign); flame color set as plain orange (no ramp, no temperature logic); fire rendered without
motion blur. PERF: fire is even heavier than smoke — adaptive domain, coarse preview, composite
flame glow as a 2D element (D117) when possible. EDGES: → D95, → D97, → D100, → D111.
D97 — DESTRUCTION [SIT]
DEF: Breaking things: fracture (pre-fractured meshes) + rigid body dynamics (D89) + debris (D98) +
smoke/dust (D95) + VFX (D100). WHY: Destruction is the most choreographed sim: believable breaks
need pre-fracture planning, controlled forces, and layered debris — pure simulation rarely looks good.
HOW (the layered recipe):  1.  Pre-fracture: use the  Cell Fracture add-on (built-in: Object →
Quick Effects → Cell Fracture) or Voronoi fracture in Geometry Nodes to cut the object into shards
before the  sim  (shards  get  rigid  body  properties).  2.  Trigger: a  force  (rigid  body  collider  —  a
wrecking ball, an impactor) or an animated "impulse" (keyed rigid body motion) hits the structure. 3.
Simulate: rigid bodies on shards (D89); add constraints so the structure holds until impact (D89 rigid
body constraints between shards — the "glue" that breaks on force; or use "Breaking Constraints" —
advanced). 4. Layers: big chunks (rigid) + medium debris (D98) + dust (smoke D95 or particle dust)
+  sparks  (particles)  +  impact  flash  (D100).  PARAM: fracture  count/thickness;  impactor  mass/
velocity; constraint breaking force; sleep thresholds.  MIST: simming without pre-fracture (nothing
breaks); everything shattering into dust (no big chunks); no dust layer (breaks look dry and clean).
PERF: bake rigid sim; reuse shard states as pre-broken "variant" objects (break the wall in a separate
sim, then place the broken version in the shot — common production trick). EDGES: → D89, → D98, →
D95/D96, → D100.
D98 — DEBRIS [SIT]
DEF: The secondary fragments: small chunks, pebbles, dust motes, splinters that follow destruction
and impacts. WHY: Debris is what makes an impact read: a tower falls and the cloud of dust and
chips sells the mass. HOW: particles (D87) or GN instances for small fragments (rigid-lite: give them
rigid body with tiny mass and high damping, or just particle motion); dust = smoke (D95) or soft
particle billboards; pre-made debris systems  (a node group that scatters chips + dust + sparks on
impact) are the production pattern.  PARAM: count; size distribution; velocities (radial + gravity);
lifetime; collision. MIST: debris as an afterthought (adds nothing); heavy debris sims for background
events. EDGES: → D97, → D100.
CHAPTER 10 — PHYSICS & SIMULATION

D99 — ENVIRONMENTAL SIMULATION [SIT]
DEF: The ambient simulation layer of a world: rain, snow, wind, falling leaves, dust, fireflies, fog —
the background that's never still. WHY: Still environments feel dead; subtle ambient motion is what
makes a world feel inhabited and weather  felt (D02's rainy city needs rain, wind-blown cloaks,
dripping).  HOW (system layers):  1.  Weather system: rain/snow = particles (D87) or GN point
streams, plus  wetness propagation (drivers on materials — D31); wind = force field + turbulence
(D88) driving cloth (D39), hair (D47), vegetation sway (D85), and debris. 2. Ambient particle life:
dust  motes  in  light  shafts  (D111),  pollen,  embers,  leaves  —  low-density  particle  fields  with
turbulence. 3. Audio-visual sync: ambient motion sells the soundscape (D133). 4. Continuity: the
weather system must be consistent across shots (rain direction, intensity) — drive it from a global
"weather"  control  (custom  property  +  drivers,  D54).  PARAM: particle  density;  wind  direction/
strength; turbulence; wetness amount; fog density (D110).  MIST: rain with no wind angle (falls
perfectly vertical — unnatural); wet surfaces that don't darken (material disconnect); ambient motion
louder than the action (distracting). EDGES: → D87, → D88, → D110/D111, → D39/D47, → D85.
SIMULATION PRODUCTION RULES (the whole chapter in 8
lines)
Simulate only what the camera sees, only at the quality the shot needs.
Fake first (shader, particles, pre-made assets); simulate when faking is harder or worse.
Animation first, sim second — every sim is driven by final animation.
Bake everything to disk in the project cache folder (D123); never trust live sims in production.
Simplify collision meshes — collision proxies (low-poly stand-ins) are standard.
Preview coarse, render fine: layout at 25% resolution, final at 100%.
Seed discipline: fixed seeds → reproducible results.
Cache management: name caches by shot+version; clean unused caches (D124/D129).
1. 
2. 
3. 
4. 
5. 
6. 
7. 
8. 
CHAPTER 10 — PHYSICS & SIMULATION
