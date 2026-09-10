# Depth Chapter 23 — Sound Design & Music

> Source: The Ultimate Blender Animation Knowledge Graph v2.0 (Blender 4.x era)
> Pages 167–169 of 228
> This file preserves the operational knowledge of the source chapter for agent use.
> Completeness over brevity. Do not summarize away parameters, failure modes, or relationships.

---

DEPTH CHAPTER 23 — SOUND DESIGN &
MUSIC
Expands D133, D62, D120. Sound is half of film: it sets emotion, timing, and space. This chapter
covers the sound vocabulary, recording, mixing, music editing, and the Blender audio workflow —
enough to make your film sound as good as it looks.
23.1 THE SOUND VOCABULARY (what sound does)
Role Definition Example Production source
Dialogue character speech conversation, monologue recorded VO / scratch
Voice-over narration over picture storyteller, thoughts recorded
Foley character-made sounds footsteps, cloth rustle, cloak swish performed & recorded
Hard effects object sounds sword clash, door slam, explosion library / synthesized
Ambience (room tone) the space's baseline city hum, rain, forest wind recorded / library
Music emotional score theme, stingers, beats composed / library
UI/subliminal design extras heartbeat, whoosh synthesized
The layering rule: a scene usually has 4–6 simultaneous sound layers (dialogue + foley + effects +
ambience + music + maybe a design layer). One layer alone = empty; all layers = alive.
23.2 THE SOUND DESIGN PROCESS (for a shot/scene)
Watch with the animatic (D10) — mark sound moments per beat: what sounds must exist,
where the music enters, where silence matters.
Build ambience first — the space's baseline (rain, room tone). Ambience is the bed everything
sits on.
Add hard effects (footsteps, impacts, props) timed to the animation frames (sync discipline,
D120).
Add foley (cloth, breathing, subtle movement) — foley is what makes characters physical.
Design layer (whooshes, magic, transitions — D101 effects get sound here; a spell without sound
is dead).
Music — score to the emotion; stingers to beats; duck (lower) music under dialogue.
Mix (23.4) and sync check (watch the whole scene, listen for gaps).
23.3 RECORDING & SOURCING (practical)
Voice recording: a quiet room (closet + blanket = booth), a decent mic (USB condenser fine),
record at 48 kHz/24-bit, pop filter, 15–20 cm from mouth, consistent mic position per character.
Record performance takes (multiple reads) — the best read wins in the edit.
Foley recording: perform sounds while watching the animation; footsteps on the right surface
(gravel, wood, wet pavement); cloth = rub the actual fabric; the timing comes from the picture.
1. 
2. 
3. 
4. 
5. 
6. 
7. 
• 
• 
DEPTH CHAPTER 23 — SOUND DESIGN & MUSIC

Sound libraries: free: freesound.org (check licenses!), BBC Sound Effects, Blender Studio's own
assets; paid: Artlist, Epidemic, Sonniss GDC packs. Always log source + license (D129 archive
discipline).
Synthesis (no library): whooshes = filtered noise with pitch sweeps; impacts = low sine thump
+ noise burst; magic = reverse reverb + shimmer; rain = filtered white noise with random droplet
ticks. Blender's VSE + Audacity (free) cover most needs; learn Audacity basics (noise reduction,
EQ, normalize).
23.4 MIXING (making it all sit together)
Concept What it is Practical rule
Levels relative loudness dialogue −12 dB, music −20 dB under dialogue, effects −15 dB; duck music
during VO
Panning left/right
placement
match screen position (character on the left → voice slightly left)
EQ frequency
balance
cut mud (200–400 Hz) from dialogue, high-pass ambience, gentle presence boost
(2–5 kHz) on VO
Reverb space feel match the room: crypt = long dark reverb, closet = none; use per-sound reverb or
one scene reverb bus
Compression level smoothing light on VO (2:1–3:1), heavier on music bed
Loudness final level
standard
−14 LUFS (web), −23 LUFS (broadcast); true-peak ≤ −1 dBTP — normalize
the master
Headroom mix space mix at −6 dB peaks, master to target
Limiting final safety a limiter on the master bus catches overs
The mix hierarchy: dialogue/foley (story layer) > effects (action layer) > ambience (bed) > music
(mood layer, ducked). If you can't hear the dialogue, the mix failed.
23.5 BLENDER'S AUDIO WORKFLOW (VSE)
Import audio: VSE → Add → Sound; scrub with audio (timeline plays sound); audio strips show
waveforms (zoom to read syllables for lip sync).
Sound to Frames (D62): Graph Editor → Channel → Sound to Samples → creates keyframes
from amplitude — use for broad jaw emphasis, not precise phonemes.
Mix in the VSE: multiple audio channels, volume envelopes (F-curve per strip), fades (right-click
→ Fade), mute per strip; the VSE handles 4–6 layers fine for animation.
Export: render with audio (FFmpeg), or render video + audio separately and mux (ffmpeg CLI).
For heavy mixes, mix in Audacity/DaVinci and import the final track.
Sync discipline: sync to the animatic (D10) is the contract — every scene's audio starts from the
animatic's timeline; final animation must hold those sync frames (D120).
23.6 MUSIC EDITING (the emotional layer)
Beat matching: set VSE timeline to the music's BPM (48 kbps… no — frames per beat = 60 ×
fps / BPM); cut pictures on beats for energy scenes.
Stingers: an accent hit (cymbal crash, sub-drop) placed exactly on an emotional beat (the reveal,
the impact, the cut to black) — the #1 cheap way to add "film feel."
• 
• 
• 
• 
• 
• 
• 
• 
• 
DEPTH CHAPTER 23 — SOUND DESIGN & MUSIC

Fade in/out: music fades in under ambience (never hard-start music at full volume unless it's a
deliberate hit); fade out or cut on scene end (cut = abrupt = intentional).
Silence is a note: the drop-to-silence before a scare or a laugh is a deliberate mix move —
design silence like a sound.
Scoring basics (no composer): loop a mood track under the scene; layer a riser (crescendo
noise) before a beat; add a sub-bass hit on impact; use tempo = emotion (fast = tension, slow =
melancholy).
23.7 SOUND FAILURE MODES & FIXES
Symptom Cause Fix
Dialogue inaudible music too loud / no ducking Duck music −8 dB under VO; check levels
Muddy mix competing lows High-pass ambience at 80–120 Hz; EQ cuts
Footsteps float foley not timed to contacts Nudge foley to the contact frames (D66)
Boomy/echoey VO reverb too heavy for the
room
Shorten reverb; scene-matched decay
Loudness inconsistent across
scenes
no master normalization Normalize the whole film to −14 LUFS
Lip sync "off" audio drift Re-sync strips to the animatic's frame numbers
Effects feel generic no foley layer Add cloth/breath/step foley — the "physical"
layer
Music fights dialogue both at full level Duck music; give music its own bus
• 
• 
• 
DEPTH CHAPTER 23 — SOUND DESIGN & MUSIC
