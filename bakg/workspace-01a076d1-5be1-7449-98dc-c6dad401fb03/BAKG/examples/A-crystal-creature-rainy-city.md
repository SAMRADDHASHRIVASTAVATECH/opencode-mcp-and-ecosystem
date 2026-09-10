# Example A — Six-legged crystal creature, flowing cloak, rainy fantasy city

Full traversal: `knowledge/system/04-ultimate-test.md` §4.1.

## Decompose
- Entity: six-legged crystal creature (hybrid organic/mineral, multi-leg, crystal surface)
- Costume: flowing cloak (cloth sim)
- Action: walking (locomotion, multi-leg gait)
- Setting: rainy fantasy city (architecture, weather, wet materials, mood lighting)

## Fired [SIT] (beyond REQ)
D05 creature design, D20 creature modeling, D21 anatomy (invented), D22 sculpt, D36 claws, D37–D39 cloak, D44 maybe not (crystal — no fur), D69/D71 multi-leg, D79–D83 city, D94/D99 rain & puddles, D108–D111 wet-city lighting, D110/D111 atmosphere.

## Key choices
- Style: fantasy — often hybrid (PBR creature + painterly city) → decision 5.1
- Modeling: sculpt-first creature + modular city (5.3)
- Rig: 6× leg IK + gait driver (5.4)
- Cloak: SIM (hero) (5.6)
- Rain: fake particles + wetness shader, not fluid (5.6 / 5.18)
- Engine: Cycles if refraction/crystal SSS matter; EEVEE if stylized deadline (5.2)

## Skill order
character-design → blender-foundations → sculpting-anatomy → modeling → lookdev → costume-groom → rigging → animation → environment → simulation (cloak + rain fake) → cinematography → lighting → render-comp → production-finishing

## Lesson
The cloak and the rain are the expensive edges. Fake rain. Sim only the hero cloak. Crystal materials from Ch 17 gems. Multi-leg gait from D71 + Ch 28.9.
