# Conversation styles, languages & accents — the "way of talking"

This governs how the AI *speaks* on calls. It does **not** produce audio itself —
accent, language and voice timbre come from the connected realtime voice / TTS
provider. What it does is attach an explicit **conduct + register + language + accent
contract** to each AI call so the agent adapts to Indian callers (across India's many
languages) and to worldwide professional vs. casual settings.

## Multilingual (India + world)

The system ships a language registry (`src/olcap/languages.py`) covering **India's 22
scheduled languages** (Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada,
Malayalam, Punjabi, Urdu, Odia, Assamese, Maithili, Santali, Kashmiri, Nepali, Sindhi,
Konkani, Dogri, Manipuri, Bhojpuri, Sanskrit) plus **~50 major world languages** (English,
Spanish, French, German, Portuguese, Arabic, Mandarin, Japanese, Korean, Russian, ...).

* `phone.list_languages` — enumerate them (all, or `india_only=true`).
* `phone.detect_language` — auto-pick the likely language + accent + country from a
  number (e.g. Indian `+91` → Hindi/English/regional; `+1` → English; `+81` → Japanese;
  `+234` → English + Nigerian languages).
* `phone.start_ai_voice_session(call_id, ..., language="ta", accent="Tamil")` — ask the
  realtime provider to listen & speak that language/accent. Each AI session records the
  chosen language; the conduct brief carries it to the LLM/voice backend.
* Languages are stored in their own script and are never a caricature.

## Two moving parts

1. **`src/olcap/communication.py`** — defines the registers and culture context, the
   named styles, per-register guidance, and a `summary_for_agent()` prompt fragment.
2. **Call records & sessions** — a call stores its `style_profile`; the AI-voice backend
   or an LLM receives the conduct brief before speaking.

## The honest boundary (read this)

* **The "actual speaking + understanding in any language in real time" is the job of the
  realtime voice backend (STT/ASR → LLM → TTS).** This layer cannot conjure an engine. It
  *knows* the languages and *requests* the right language + accent from the provider.
* **Whether a given language/accent is actually usable depends on that provider's ASR/TTS
  support.** Hindi/Tamil/etc. and the major world languages are widely supported by modern
  realtime providers, but coverage varies. The system reports the *requested* language; the
  provider reports what it can actually do. It is honest if a language isn't supported by
  the connected engine, and falls back to English rather than guessing.
* Real-time interpretation across languages likewise depends on the connected LLM/ASR; the
  system steers it but cannot create it.
* These rules are *guidelines*, not a guarantee of perfect accent imitation — and they
  deliberately avoid faking a local accent or stereotyping. Indian code-switching to
  Hinglish/regional languages is recommended only when the contact does it naturally.
* The simulated provider only stores the language/accent for testing.

## Registers

| Register | Use |
|---|---|
| `professional` | formal business / strangers / gatekeepers |
| `semi_formal` | everyday business (India + global default) |
| `friendly` | established contacts / family |

## Context auto-detection from number

When no style is chosen, the system picks a context from the destination number:

* `+91…`, `91…`, or a bare 10-digit number → **india**
* anything else (US `+1`, UK `+44`, JP `+81`, …) → **global**

Detected number | default register
|---|---
| +91 / India | `india_semi_formal` (warm business; natural Hinglish if mirrored) |
| worldwide | `global_semi_formal` |

You can always override with an explicit `style`.

## Named styles (`phone.list_speaking_styles`)

`india_professional`, `india_business_default`, `india_casual`,
`global_professional`, `global_semi_formal`, `global_casual`.

Each carries: language guidance, a suggested opening, etiquette do's and avoid's, and
self-identification policy (identify as the user's AI assistant where appropriate).

## Examples

```jsonc
// Ask a Mumbai contact to confirm a slot - warm, natural, business-appropriate.
{ "tool": "phone.start_ai_voice_session",
  "args": { "call_id": "...", "objective": "Confirm Friday 4 PM works.",
            "style": "india_business_default" } }

// A formal call to an international client
{ "style": "global_professional" }

// Relaxed follow-up with an existing friend/contact
{ "style": "india_casual" }
```

`phone.get_call_conduct(call_id)` returns the resolved style profile plus the plain-text
`conduct` fragment you can feed to a voice/LLM backend. `phone.get_call_summary` also
reports which style was used.
