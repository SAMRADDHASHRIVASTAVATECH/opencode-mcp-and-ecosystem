# Depth Chapter 38 — Story, Storyboard & Animatic Depth

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 220–222 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 38 — STORY, STORYBOARD &
ANIMATIC DEPTH
Expands D01, D09, D10, D120, D130. The complete pre-visual craft: story structures, beat sheets,
boarding technique, shot design, the animatic as the film's contract, and the Grease Pencil boarding
workflow.
38.1 STORY STRUCTURES (the catalog)
Structure What it is Use
Three-act setup (25%) / confrontation (50%) / resolution
(25%)
the standard narrative short/film
Hero's journey call → trials → crisis → return mythic/epic
In medias res start mid-action, backfill hooks, action films
Framed story story within a story (bookends) epics, nostalgia
Loop/cycle end returns to the start (changed) art films, philosophical shorts
Micro-story (loop
content)
setup → action → payoff in seconds social loops, turntables, VFX
shots
Nonlinear out-of-order reveals mystery, experimental
Multi-thread parallel stories intersecting ensemble, world-building films
Anti-structure no traditional arc — mood/theme driven experimental, poetic
The beat sheet (D01): list every beat (moment of change) with: type (setup/turn/payoff), emotion,
information, and the shot(s) it needs. 1 beat ≈ 1–3 s (loops) or 5–15 s (shorts). The beat sheet is the
shot list's ancestor (D10).
38.2 THE ANIMATIC AS CONTRACT (why pre-visualization
is the budget)
The animatic (D10) is not a sketch — it's the production contract: every shot, its timing, its audio
sync points, its camera. Consequences: - Shot count → asset list: every animatic shot demands its
assets (sets, props, characters, FX). Lock the animatic before modeling anything expensive (D14). -
Timing → animation: the animatic's frame numbers are the sync contract (D120) — final animation
lands beats on the animatic's frames. - Pacing → edit: the animatic is the rough edit; the final edit
(D120) refines it, it doesn't redesign it. - The rule: if the story is boring at the animatic stage, no 3D
will save it. Fix it in the animatic (cheap), not in the render (expensive).
38.3 STORYBOARD TECHNIQUE (making boards that
work)
The board contains:  frame (what the camera sees), shot size + angle + move (D106/D107),
staging (who's where), action arrows, timing notes (frames), dialogue/audio notes, and the  intent
DEPTH CHAPTER 38 — STORY, STORYBOARD & ANIMATIC DEPTH

(what the audience should feel). Thumbnails first: 5–15 tiny roughs per shot (silhouette-level) —
pick the staging that reads; then clean boards.  Boarding rules:  1.  One idea per shot  (D104
staging) — if a shot does two things, split it. 2.  The camera is the storyteller  (Ch 21): size =
emotion, angle = power, move = emphasis. 3. Show, don't tell (Ch 27.2): boards should visualize
the story, not illustrate the script. 4. Continuity from the start: 180° line (D103), screen direction,
eyelines — board with the rules, not against them. 5. Readability test: blur your eyes — does the
action still read? Boards that fail at thumbnail size fail on screen.
38.4 SHOT DESIGN FOR STORY (the size/angle/move
decision table)
Beat type Default size Angle Move
Opening/location Extreme wide → wide high/level crane in or dolly
Dialogue (neutral) Medium/OTS eye-level none or subtle push
Emotional turn Close-up level/slight low slow dolly in
Revelation Close-up → insert level push on the detail
Threat/villain Low angle medium low slow push/orbit
Victim/weakness High angle high none/descend
Action Wide/medium dynamic (dutch ok) tracking/handheld
Chase Wide + close alternates dutch tracking + shake
Comedy beat Medium → close on reaction level hold (let the acting play)
Horror Wide (empty) → close (threat) level/low slow creep, then smash cut
Contemplation Wide with negative space level very slow or none
Montage Varies varies matching moves (Ch 21)
The anti-default rule:  the  default (medium, eye-level, static) is the fallback, never the plan —
every shot justifies its size/angle/move from the beat (D106).
38.5 THE ANIMATIC WORKFLOW (Blender VSE)
Audio first: import the dialogue/music/scratch track into the VSE (D120); mark sync points (Ch
23.6).
Board import: boards as image strips (or Grease Pencil boards, D130) placed on the timeline at
the animatic's timing.
Cut to the beats: trim strips to the beat timing; add note strips (camera moves, FX notes,
sounds).
Add scratch camera moves: render previs camera moves (D11) or mark them as annotations.
Review loop: watch with sound; re-cut; the animatic is done when every beat lands and the
pacing works — then lock it.
Handoff: the locked animatic → shot list (D121), asset list (D14), and the sync contract for
animation (D120).
1. 
2. 
3. 
4. 
5. 
6. 
DEPTH CHAPTER 38 — STORY, STORYBOARD & ANIMATIC DEPTH

38.6 GREASE PENCIL BOARDING (D130 in the pre-pro
pipeline)
Grease Pencil 3 (4.3+): draw boards as GP layers in a 2D scene; animate strokes (onion skin)
for moving boards (the "moving storyboard" — boards with camera pans/zooms) — a cheap,
powerful upgrade over static boards.
GP layers & materials: one GP object per shot (layers per element); material strokes (black line,
gray fill, color notes).
Rendering GP: EEVEE renders GP strokes crisply (Ch 18.7-adjacent); export as images for the
VSE animatic, or keep GP in the scene.
The 2D-3D hybrid (D130): GP boards in 3D space on camera-facing planes — previs characters/
sets as GP drawings over 3D blocks (D11) — the fastest way to test staging before modeling.
38.7 STORY & BOARD FAILURE MODES & FIXES
Symptom Cause Fix
Story feels thin no goal/obstacle/stakes re-write the beat sheet with the three questions (D01)
Pacing drags too many setup beats cut setups, keep payoffs (D120)
Shots feel random no shot-design reasoning apply the table (38.4) per beat
Boards don't read over-detail, no staging clarity thumbnail + silhouette test (38.3)
Animatic ignored skipped/fast-forwarded treat it as the contract (38.2)
Continuity breaks later boarding without 180°/eyelines board with the rules (38.3)
Audio never syncs no sync marks audio-first workflow (38.5)
• 
• 
• 
• 
DEPTH CHAPTER 38 — STORY, STORYBOARD & ANIMATIC DEPTH
