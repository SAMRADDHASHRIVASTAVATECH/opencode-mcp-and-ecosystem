"""Language & accent registry for realtime multilingual calls.

Two honest roles:
  1. KNOWLEDGE: enumerate the world's spoken languages, with full coverage of
     India's 22 scheduled languages and the world's major languages, plus the
     country/region they map to. Auto-detect the likely language(s) + accent from
     the number being called.
  2. STEERING: hand the chosen language + accent to the realtime voice backend so
     its ASR listens in that language and its TTS speaks in that language/accent.

It does NOT generate speech. Whether a language/accent is actually usable in real
time depends entirely on the connected STT/LLM/TTS provider supporting it. This
module reports the requested language; the provider reports what it can do.

Languages are written in their own script where practical, with an ISO 639 code
and an English name, so profiles are precise and never a caricature.
"""

from __future__ import annotations

from .policy import normalize_number

# ISO 639-1/3 code -> {name (English), native, script}
LANGUAGES = {
    # ---- India (22 scheduled languages) ----
    "hi":  {"name": "Hindi",      "native": "हिन्दी",        "script": "Devanagari", "regions": ["IN"]},
    "bn":  {"name": "Bengali",    "native": "বাংলা",         "script": "Bengali",    "regions": ["IN", "BD"]},
    "ta":  {"name": "Tamil",      "native": "தமிழ்",         "script": "Tamil",      "regions": ["IN", "LK", "SG", "MY"]},
    "te":  {"name": "Telugu",     "native": "తెలుగు",        "script": "Telugu",     "regions": ["IN"]},
    "mr":  {"name": "Marathi",    "native": "मराठी",         "script": "Devanagari", "regions": ["IN"]},
    "gu":  {"name": "Gujarati",   "native": "ગુજરાતી",       "script": "Gujarati",   "regions": ["IN"]},
    "kn":  {"name": "Kannada",    "native": "ಕನ್ನಡ",         "script": "Kannada",    "regions": ["IN"]},
    "ml":  {"name": "Malayalam",  "native": "മലയാളം",        "script": "Malayalam",  "regions": ["IN"]},
    "pa":  {"name": "Punjabi",    "native": "ਪੰਜਾਬੀ",        "script": "Gurmukhi",   "regions": ["IN", "PK"]},
    "ur":  {"name": "Urdu",       "native": "اردو",          "script": "Arabic",     "regions": ["IN", "PK"]},
    "or":  {"name": "Odia",       "native": "ଓଡ଼ିଆ",          "script": "Odia",       "regions": ["IN"]},
    "as":  {"name": "Assamese",   "native": "অসমীয়া",        "script": "Bengali",    "regions": ["IN"]},
    "mai": {"name": "Maithili",   "native": "मैथिली",        "script": "Devanagari", "regions": ["IN"]},
    "sat": {"name": "Santali",    "native": "ᱥᱟᱱᱛᱟᱲᱤ",        "script": "Ol Chiki",   "regions": ["IN"]},
    "ks":  {"name": "Kashmiri",   "native": "कॉशुर",         "script": "Arabic",     "regions": ["IN"]},
    "ne":  {"name": "Nepali",     "native": "नेपाली",         "script": "Devanagari", "regions": ["IN", "NP"]},
    "sd":  {"name": "Sindhi",     "native": "سنڌي",          "script": "Arabic",     "regions": ["IN", "PK"]},
    "kok": {"name": "Konkani",    "native": "कोंकणी",        "script": "Devanagari", "regions": ["IN"]},
    "doi": {"name": "Dogri",      "native": "डोगरी",         "script": "Devanagari", "regions": ["IN"]},
    "mni": {"name": "Manipuri",   "native": "মৈতৈলোন্",       "script": "Bengali",    "regions": ["IN"]},
    "bho": {"name": "Bhojpuri",   "native": "भोजपुरी",        "script": "Devanagari", "regions": ["IN"]},
    "sa":  {"name": "Sanskrit",   "native": "संस्कृतम्",      "script": "Devanagari", "regions": ["IN"]},
    # ---- World major languages ----
    "en":  {"name": "English",    "native": "English",       "script": "Latin",     "regions": ["US","GB","IN","AU","CA","SG","NZ","ZA"]},
    "es":  {"name": "Spanish",    "native": "Español",       "script": "Latin",     "regions": ["ES","MX","AR","CO","PE","VE","CL","US"]},
    "fr":  {"name": "French",     "native": "Français",      "script": "Latin",     "regions": ["FR","CA","BE","CH","SN","CI"]},
    "de":  {"name": "German",     "native": "Deutsch",       "script": "Latin",     "regions": ["DE","AT","CH"]},
    "it":  {"name": "Italian",    "native": "Italiano",      "script": "Latin",     "regions": ["IT","CH"]},
    "pt":  {"name": "Portuguese", "native": "Português",     "script": "Latin",     "regions": ["PT","BR","AO","MZ"]},
    "ru":  {"name": "Russian",    "native": "Русский",       "script": "Cyrillic",  "regions": ["RU","KZ","BY"]},
    "ar":  {"name": "Arabic",     "native": "العربية",        "script": "Arabic",    "regions": ["SA","EG","AE","IQ","MA","DZ","JO"]},
    "zh":  {"name": "Mandarin",   "native": "中文",           "script": "Han",       "regions": ["CN","SG","TW"]},
    "yue": {"name": "Cantonese",  "native": "廣東話",         "script": "Han",       "regions": ["HK","CN","SG"]},
    "ja":  {"name": "Japanese",   "native": "日本語",         "script": "Japanese",  "regions": ["JP"]},
    "ko":  {"name": "Korean",     "native": "한국어",         "script": "Hangul",    "regions": ["KR"]},
    "id":  {"name": "Indonesian", "native": "Bahasa Indonesia", "script": "Latin",  "regions": ["ID"]},
    "ms":  {"name": "Malay",      "native": "Bahasa Melayu", "script": "Latin",     "regions": ["MY","SG","BN"]},
    "th":  {"name": "Thai",       "native": "ไทย",            "script": "Thai",      "regions": ["TH"]},
    "vi":  {"name": "Vietnamese", "native": "Tiếng Việt",    "script": "Latin",     "regions": ["VN"]},
    "tr":  {"name": "Turkish",    "native": "Türkçe",        "script": "Latin",     "regions": ["TR"]},
    "nl":  {"name": "Dutch",      "native": "Nederlands",    "script": "Latin",     "regions": ["NL","BE"]},
    "pl":  {"name": "Polish",     "native": "Polski",        "script": "Latin",     "regions": ["PL"]},
    "uk":  {"name": "Ukrainian",  "native": "Українська",    "script": "Cyrillic",  "regions": ["UA"]},
    "sv":  {"name": "Swedish",    "native": "Svenska",       "script": "Latin",     "regions": ["SE"]},
    "el":  {"name": "Greek",      "native": "Ελληνικά",      "script": "Greek",     "regions": ["GR","CY"]},
    "he":  {"name": "Hebrew",     "native": "עברית",         "script": "Hebrew",    "regions": ["IL"]},
    "fa":  {"name": "Persian",    "native": "فارسی",         "script": "Arabic",    "regions": ["IR","AF"]},
    "sw":  {"name": "Swahili",    "native": "Kiswahili",     "script": "Latin",     "regions": ["TZ","KE","UG"]},
    "am":  {"name": "Amharic",    "native": "አማርኛ",          "script": "Ge'ez",     "regions": ["ET"]},
    "yo":  {"name": "Yoruba",     "native": "Yorùbá",        "script": "Latin",     "regions": ["NG"]},
    "ha":  {"name": "Hausa",      "native": "Hausa",         "script": "Latin",     "regions": ["NG","NE"]},
    "ig":  {"name": "Igbo",       "native": "Igbo",          "script": "Latin",     "regions": ["NG"]},
    "zu":  {"name": "Zulu",       "native": "isiZulu",       "script": "Latin",     "regions": ["ZA"]},
    "fil": {"name": "Filipino",   "native": "Filipino",      "script": "Latin",     "regions": ["PH"]},
    "ta-LK": {"name": "Tamil (Sri Lanka)", "native": "தமிழ்", "script": "Tamil",   "regions": ["LK"]},
}

# India's 22 scheduled languages in ISO 639 order (for the tool output).
INDIA_LANGUAGES = ["as", "bn", "bho", "doi", "gu", "hi", "kn", "ks", "kok",
                   "mai", "ml", "mni", "mr", "ne", "or", "pa", "sa", "sat",
                   "sd", "ta", "te", "ur"]

# Country calling code prefix -> (country, region label, default/prominent languages).
CC = {
    "91":  ("IN", "india", ["hi", "en", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa", "ur", "or", "as"]),
    "1":   ("US", "global", ["en", "es"]),          # +1 US/Canada
    "44":  ("GB", "global", ["en"]),
    "61":  ("AU", "global", ["en"]),
    "81":  ("JP", "global", ["ja"]),
    "82":  ("KR", "global", ["ko"]),
    "86":  ("CN", "global", ["zh"]),
    "852": ("HK", "global", ["yue", "zh", "en"]),
    "65":  ("SG", "global", ["en", "zh", "ms", "ta"]),
    "60":  ("MY", "global", ["ms", "zh", "ta", "en"]),
    "62":  ("ID", "global", ["id"]),
    "66":  ("TH", "global", ["th"]),
    "84":  ("VN", "global", ["vi"]),
    "90":  ("TR", "global", ["tr"]),
    "7":   ("RU", "global", ["ru"]),
    "49":  ("DE", "global", ["de"]),
    "33":  ("FR", "global", ["fr"]),
    "34":  ("ES", "global", ["es"]),
    "39":  ("IT", "global", ["it"]),
    "351": ("PT", "global", ["pt"]),
    "55":  ("BR", "global", ["pt"]),
    "52":  ("MX", "global", ["es"]),
    "54":  ("AR", "global", ["es"]),
    "57":  ("CO", "global", ["es"]),
    "56":  ("CL", "global", ["es"]),
    "20":  ("EG", "global", ["ar"]),
    "966": ("SA", "global", ["ar"]),
    "971": ("AE", "global", ["ar"]),
    "964": ("IQ", "global", ["ar"]),
    "98":  ("IR", "global", ["fa"]),
    "234": ("NG", "global", ["en", "yo", "ha", "ig"]),
    "233": ("GH", "global", ["en"]),
    "254": ("KE", "global", ["sw", "en"]),
    "255": ("TZ", "global", ["sw"]),
    "27":  ("ZA", "global", ["en", "zu", "af"]),
    "880": ("BD", "global", ["bn"]),
    "977": ("NP", "global", ["ne"]),
    "94":  ("LK", "global", ["ta", "en", "si"]),
    "63":  ("PH", "global", ["fil", "en"]),
    "972": ("IL", "global", ["he"]),
    "31":  ("NL", "global", ["nl"]),
    "48":  ("PL", "global", ["pl"]),
    "380": ("UA", "global", ["uk"]),
    "46":  ("SE", "global", ["sv"]),
    "30":  ("GR", "global", ["el"]),
    "92":  ("PK", "global", ["ur", "en", "sd", "pa"]),
    "3510":"PT",  # placeholder to keep dict clean; ignored by longest-match
}

# Region label -> friendly name (for tool output).
REGION_LABELS = {"india": "India", "global": "Worldwide"}


def code_for_number(number: str) -> str | None:
    """Return the international calling prefix for a number (without leading 0).

    A bare 10-digit number (no '+' and no country code) is treated as a domestic
    (India, in this deployment) local number -> 91. Numbers with a leading '+'
    are matched to a country calling code; 10-digit strings are never matched to
    a foreign code to avoid misreading e.g. 9876543210 as +98 (Iran)."""
    n = normalize_number(number)
    if not n:
        return None
    if n.startswith("+"):
        n = n[1:]
    else:
        # Local/direct dialling: 10 digits with no country code is domestic.
        if n.isdigit() and len(n) == 10:
            return "91"
    best = None
    for _len in (3, 2, 1):
        for cc in CC:
            if len(cc) == _len and n.startswith(cc):
                best = cc
        if best:
            return best
    return None


def region_for_number(number: str) -> str:
    cc = code_for_number(number)
    if cc and cc in CC:
        return CC[cc][1]
    return "global"


def suggest_languages(number: str) -> list:
    """Default/prominent languages for a number, best language first."""
    cc = code_for_number(number)
    if cc and cc in CC:
        return list(CC[cc][2])
    # A bare 10-digit number (no intl prefix) is treated as India/local.
    n = normalize_number(number)
    if n and n.isdigit() and len(n) == 10:
        return ["hi", "en"]
    return ["en"]


def default_accent(number: str) -> str:
    """A plain-language accent hint, derived from the number's country."""
    cc = code_for_number(number)
    if cc and cc in CC:
        country, region = CC[cc][0], CC[cc][1]
        if region == "india":
            return "Indian English"
        return f"{LANGUAGES.get(CC[cc][2][0], {}).get('name', 'English')} ({country})"
    return "Neutral/standard"


def display(code: str) -> str:
    lang = LANGUAGES.get(code, {})
    if lang:
        return f"{lang['name']} ({code}) · {lang['native']}"
    return code
