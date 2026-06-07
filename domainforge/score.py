"""
Brandability scoring.

`domain_score(word)` -> 0..10 heuristic favouring short, pronounceable,
vowel-ending words (the shape that reads well as `name.ai` / `name.com`).

`freq_tier(word)` -> a registrability tier derived from corpus frequency
(via the optional `wordfreq` package). Rare / invented words are far more
likely to be available; generic words are almost always taken. If `wordfreq`
isn't installed, the tier is "unknown" and scoring still works.
"""

from __future__ import annotations

_VOWELS = "aeiou"

# Optional dependency: wordfreq. Degrade gracefully if absent.
try:  # pragma: no cover - exercised by environment, not unit tests
    from wordfreq import zipf_frequency as _zipf

    _HAS_WORDFREQ = True
except Exception:  # pragma: no cover
    _HAS_WORDFREQ = False

    def _zipf(word: str, lang: str) -> float:  # type: ignore[misc]
        return 0.0


def has_wordfreq() -> bool:
    return _HAS_WORDFREQ


def count_syllables(word: str) -> int:
    """Cheap vowel-group syllable estimate. Always >= 1."""
    word = word.lower()
    count = 0
    prev_vowel = False
    for ch in word:
        is_vowel = ch in "aeiouy"
        if is_vowel and not prev_vowel:
            count += 1
        prev_vowel = is_vowel
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def max_consonant_run(word: str) -> int:
    mx = cur = 0
    for c in word.lower():
        cur = cur + 1 if c not in _VOWELS else 0
        mx = max(mx, cur)
    return mx


def domain_score(word: str) -> int:
    """0..10 brandability heuristic. Higher = better domain candidate."""
    if not word:
        return 0
    score = 0
    n = len(word)
    syl = count_syllables(word)

    # Length: 5-7 is the sweet spot for a memorable brand.
    if 5 <= n <= 7:
        score += 4
    elif 4 <= n <= 8:
        score += 3
    elif n <= 9:
        score += 2
    elif n <= 11:
        score += 1

    # Syllables: 1-3 say-it-once names win.
    if 1 <= syl <= 2:
        score += 3
    elif syl == 3:
        score += 2
    elif syl == 4:
        score += 1

    # Ends in a vowel -> flows into ".ai" and reads softer.
    if word[-1] in _VOWELS:
        score += 1

    # Pronounceability: avoid consonant pile-ups.
    run = max_consonant_run(word)
    if run <= 2:
        score += 2
    elif run == 3:
        score += 1

    return min(score, 10)


# Zipf frequency bands -> registrability tier.
#   0      -> "invented"    (not in any corpus; highly registrable)
#   < 2.2  -> "rare"        (obscure real word; likely available)
#   < 3.6  -> "distinctive" (real but not overused; the sweet spot)
#   < 5.0  -> "familiar"    (recognizable; harder to register)
#   >=5.0  -> "generic"     (too common; almost always taken)
def freq_tier(word: str) -> str:
    if not _HAS_WORDFREQ:
        return "unknown"
    z = _zipf(word, "en")
    if z == 0:
        return "invented"
    if z < 2.2:
        return "rare"
    if z < 3.6:
        return "distinctive"
    if z < 5.0:
        return "familiar"
    return "generic"


def zipf(word: str) -> float:
    """Raw Zipf frequency (0.0 if wordfreq unavailable or unknown word)."""
    return round(_zipf(word, "en"), 2) if _HAS_WORDFREQ else 0.0


# Tiers we consider "worth checking" by default (registrable end of the scale).
REGISTRABLE_TIERS = {"invented", "rare", "distinctive", "unknown"}


def is_registrable_tier(tier: str) -> bool:
    return tier in REGISTRABLE_TIERS
