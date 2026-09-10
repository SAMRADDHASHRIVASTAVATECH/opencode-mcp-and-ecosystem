"""Conversation style & register adaptation (the "way of talking").

The AI-voice pipeline (a RealtimeVoiceProvider / LLM + TTS) produces the actual
speech. This module is the *conduct + style contract* handed to that pipeline so
conversations adapt to context - Indian conversational norms and worldwide
professional vs. casual registers - instead of speaking in one flat style.

It deliberately does NOT produce audio or claim an accent. Accent, language and
voice timbre come from the connected TTS / voice provider. What this defines is:

  * register/formality selection (formal business, semi-formal, friendly/casual)
  * culture-aware greeting & etiquette guidance
  * language guidance (English / Hinglish / Hindi and regional; keep it natural,
    not a caricature - code-switching is used naturally by real speakers)
  * respect markers and how the assistant identifies itself
  * what NOT to say (avoid presuming relationship, avoid overly familiar tone
    with strangers, don't fake a local accent)

The rules are practical and respectful, never stereotyped or mocking.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict

# Registers (formality).
PROFESSIONAL = "professional"       # formal business / strangers / gatekeepers
SEMI_FORMAL = "semi_formal"         # most everyday business in India & global
FRIENDLY = "friendly"               # established contact / informal / family
# Culture context.
CONTEXT_INDIA = "india"
CONTEXT_GLOBAL = "global"
CONTEXT_AUTO = "auto"

# Named, ready-to-use style profiles.
STYLES = {
    "india_professional": {
        "context": CONTEXT_INDIA, "register": PROFESSIONAL,
        "summary": "Warm, respectful Indian business English; clear and polite."},
    "india_business_default": {
        "context": CONTEXT_INDIA, "register": SEMI_FORMAL,
        "summary": "Everyday Indian professional - professional but warm, uses "
                   "natural English with light, natural Hinglish where the "
                   "contact is comfortable; respect forms like 'ji' only when "
                   "the contact does."},
    "india_casual": {
        "context": CONTEXT_INDIA, "register": FRIENDLY,
        "summary": "Friendly, informal Indian conversation for established "
                   "contacts/family."},
    "global_professional": {
        "context": CONTEXT_GLOBAL, "register": PROFESSIONAL,
        "summary": "Neutral international business English; concise, clear, "
                   "respectful across cultures."},
    "global_semi_formal": {
        "context": CONTEXT_GLOBAL, "register": SEMI_FORMAL,
        "summary": "Global semi-formal business register."},
    "global_casual": {
        "context": CONTEXT_GLOBAL, "register": FRIENDLY,
        "summary": "Friendly informal conversation for known contacts."},
}


def _pick(data: dict, ctx: str, reg: str):
    """Return the most specific matching entry, else best-effort."""
    regs = [reg]
    if reg == FRIENDLY:
        regs.insert(0, SEMI_FORMAL)
    # exact
    k = f"{ctx}_{reg}"
    if k in data:
        return data[k]
    # fall back within register family across context
    for r in regs:
        if f"{ctx}_{r}" in data:
            return data[f"{ctx}_{r}"]
        if f"{CONTEXT_GLOBAL}_{r}" in data:
            return data[f"{CONTEXT_GLOBAL}_{r}"]
    # generic
    return data.get("default", {})


@dataclass
class SpeakingStyle:
    """Conduct rules + language/accent the AI should follow on a call."""
    name: str = "india_business_default"
    context: str = CONTEXT_INDIA
    register: str = SEMI_FORMAL
    language: str = "en"               # ISO 639 code, e.g. hi, ta, te, bn, ...
    language_alt: str = ""             # secondary/fallback language
    accent: str = ""                   # e.g. "Indian English", "Spanish (MX)"
    language_guidance: str = ""
    greeting: str = ""
    etiquette: list = field(default_factory=list)
    dont: list = field(default_factory=list)
    identify_as_ai: str = "default"    # always|when_asked|per_policy|never

    @classmethod
    def from_profile(cls, profile: dict) -> "SpeakingStyle":
        ctx = profile.get("context", CONTEXT_AUTO)
        reg = profile.get("register", SEMI_FORMAL)
        if ctx == CONTEXT_AUTO:
            ctx = profile.get("hint", CONTEXT_INDIA)
        name = profile.get("name") or f"{ctx}_{reg}"
        rules = profile.get("rules", {})
        st = cls(name=name, context=ctx, register=reg)
        st.language = profile.get("language", "en") or "en"
        st.language_alt = profile.get("language_alt", "")
        st.accent = profile.get("accent", "")
        st.language_guidance = rules.get("language_guidance", "")
        st.greeting = rules.get("greeting", "")
        st.etiquette = list(rules.get("etiquette", []))
        st.dont = list(rules.get("dont", []))
        st.identify_as_ai = profile.get("identify_as_ai", "default")
        return st

    def dict(self):
        return asdict(self)


# Deterministic per-register conduct used to build full profiles. Expressed as
# clear, non-stereotyped guidance.
REGISTER_RULES = {
    # ---- India, professional (formal) ----
    "india_professional": {
        "language_guidance": "Clear, respectful English. Speak a little slower "
            "and articulate fully; many Indian business contacts are comfortable "
            "in English but appreciate clarity. Use Hindi/Hinglish only if the "
            "contact switches to it.",
        "greeting": "Good [morning/afternoon/evening], this is [assistant] from "
            "[user]'s office. Am I speaking with [name]?",
        "etiquette": ["Use first name only if invited; otherwise title + surname "
                      "or full name.", "Pause and confirm understanding "
                      "('Did I get that right?').", "Offer a call-back window in "
                      "the user's local time zone.", "Be concise; respect that "
                      "the other party may be busy."],
        "dont": ["Do not fake an accent or slip into forced Hindi.", "Do not "
                 "presume familiarity with a stranger.", "Do not over-apologise "
                 "or be overly deferential."],
    },
    # ---- India, semi-formal (default everyday business) ----
    "india_semi_formal": {
        "language_guidance": "Professional but warm English. Indian business "
            "conversation commonly code-switches into natural Hinglish (e.g. "
            "'aap ka time suited hai kya?') when rapport allows - mirror the "
            "contact, don't lead with it. Match energy.",
        "greeting": "Namaste / Hello [name], this is [assistant] calling on "
            "behalf of [user].",
        "etiquette": ["Warm, courteous tone.", "Respect the other party's time.",
                      "If the contact uses 'ji' or Hindi, it is fine to respond "
                      "in kind and warmly.", "Clarify numbers/dates carefully "
                      "('so that is 4 PM, is it?') to avoid miscommunication."],
        "dont": ["Don't assume everyone prefers Hindi.", "Don't be abrupt - a "
                 "brief pleasantry is expected before business."],
    },
    # ---- India, casual/friendly ----
    "india_friendly": {
        "language_guidance": "Relaxed and friendly. Natural mix of English and "
            "Hindi/Hinglish or regional language as the relationship allows. "
            "Short, warm sentences.",
        "greeting": "Hi [name]! It's [assistant], calling for [user]. How are "
            "you doing?",
        "etiquette": ["Be warm and easygoing.", "Acknowledge family/health "
                      "pleasantries if the contact offers them.", "Keep it light "
                      "but still get the point across."],
        "dont": ["Don't be overly formal or robotic with a known contact.",
                 "Don't presume to speak on behalf of family matters without "
                 "the user's authorisation."],
    },
    # ---- Global professional ----
    "global_professional": {
        "language_guidance": "Clear, neutral, concise international English. "
            "Avoid idioms, slang and cultural references. Speak at a moderate, "
            "steady pace.",
        "greeting": "Good [morning/afternoon/evening], this is [assistant] from "
            "[user]. May I speak with [name]?",
        "etiquette": ["State the purpose early.", "Be punctual with the other "
                      "party's time.", "Confirm time zones and spell out "
                      "numbers/emails.", "Remain neutral and professional."],
        "dont": ["Don't assume familiarity with a stranger.", "Don't use "
                 "colloquialisms a non-native listener may miss."],
    },
    # ---- Global semi-formal ----
    "global_semi_formal": {
        "language_guidance": "Friendly but professional English; light idioms are "
            "fine with an established contact.",
        "greeting": "Hello [name], this is [assistant] with [user]. Thanks for "
            "taking my call.",
        "etiquette": ["Warm but efficient.", "Adapt to the contact's formality "
                      "level."],
        "dont": ["Don't be presumptuous about titles."],
    },
    # ---- Global casual ----
    "global_friendly": {
        "language_guidance": "Relaxed, natural English between known contacts.",
        "greeting": "Hey [name]! [Assistant] here for [user]. Hope you're doing "
            "well.",
        "etiquette": ["Be easygoing.", "Keep it brief unless the other party "
                      "wants to chat."],
        "dont": ["Don't get too personal without the user's go-ahead."],
    },
}


def build_profile(style: str | None = None, *, context: str = CONTEXT_AUTO,
                  register: str | None = None, contact: str = "",
                  number: str = "", identify_as_ai: str = "default",
                  language: str = "", accent: str = "",
                  custom: dict | None = None) -> dict:
    """Resolve a full speaking-style profile from a named style or explicit
    context+register (optionally auto-detected from the destination), plus an
    explicit or auto-detected language & accent."""
    if style and style in STYLES:
        base = STYLES[style]
        return _assemble(base["context"], base["register"], identify_as_ai,
                         contact, number, language, accent)
    ctx = context
    if ctx == CONTEXT_AUTO:
        ctx = detect_context(number)
    reg = register or SEMI_FORMAL
    if custom:
        prof = dict(custom)
        prof.setdefault("context", ctx)
        prof.setdefault("register", reg)
        prof.setdefault("identify_as_ai", identify_as_ai)
        prof.setdefault("language", language or "en")
        prof.setdefault("accent", accent or "")
        return prof
    return _assemble(ctx, reg, identify_as_ai, contact, number, language, accent)


def _assemble(ctx, reg, identify_as_ai, contact, number, language="", accent=""):
    rules = _pick(REGISTER_RULES, ctx, reg)
    lang = detect_language_and_accent(number) if not language else {}
    profile = {
        "name": f"{ctx}_{reg}", "context": ctx, "register": reg,
        "identify_as_ai": identify_as_ai, "contact": contact or "",
        "number": number or "",
        "language": language or lang.get("language", "en"),
        "language_alt": lang.get("language_alt", ""),
        "accent": accent or lang.get("accent", ""),
        "rules": rules,
    }
    return profile


def detect_context(number: str = "") -> str:
    """Best-effort context hint from a number. Indian numbers +91 / 91 -> india;
    unknown/local -> india; otherwise global. Non-authoritative - the caller can
    override with an explicit style/context."""
    from .policy import normalize_number
    n = normalize_number(number)
    if not n:
        return CONTEXT_INDIA
    if n.startswith("+91") or n.startswith("91") or (n.isdigit() and len(n) == 10):
        return CONTEXT_INDIA
    return CONTEXT_GLOBAL


def detect_language_and_accent(number: str = "") -> dict:
    """Choose a language + accent for a number (auto). Returns a dict that can be
    merged into a style profile. The choice is a request to the voice backend;
    whether it is actually supported depends on that backend's ASR/TTS coverage."""
    from . import languages as L
    langs = L.suggest_languages(number)
    primary = langs[0] if langs else "en"
    return {
        "language": primary,
        "language_alt": langs[1] if len(langs) > 1 else "",
        "accent": L.default_accent(number),
        "context": L.region_for_number(number),
    }


def summary_for_agent(profile: dict) -> str:
    """A short prompt fragment to prepend to the LLM's system/objective for a
    call, turning the profile into actionable conduct instructions."""
    from . import languages as L
    sp = SpeakingStyle.from_profile(profile)
    lines = []
    lines.append(f"Communication style: {sp.name} ({sp.register} register, "
                 f"{sp.context} context).")
    lang_label = f"{L.display(sp.language)}"
    if sp.language_alt:
        lang_label += f" (fallback {L.display(sp.language_alt)})"
    lines.append(f"SPOKEN LANGUAGE: {lang_label}.")
    if sp.accent:
        lines.append(f"Preferred accent: {sp.accent}.")
    lines.append("Speak the contact's language naturally; switch/interpret in "
                 "real time as they do. If you cannot confidently speak the "
                 "detected language, tell them and use English rather than "
                 "guessing.")
    if sp.language_guidance:
        lines.append(f"Register guidance: {sp.language_guidance}")
    if sp.greeting:
        lines.append(f"Suggested opening: {sp.greeting}")
    if sp.etiquette:
        lines.append("Etiquette: " + " ".join(sp.etiquette))
    if sp.dont:
        lines.append("Avoid: " + " ".join(sp.dont))
    if profile.get("identify_as_ai") in ("always", "default"):
        lines.append("Identify yourself as the user's AI assistant where "
                     "appropriate (per policy).")
    return "\n".join(lines)
