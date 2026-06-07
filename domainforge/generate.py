"""
Candidate generation.

Three sources, all funneling through `clean()` + dedupe:

  1. Datamuse expansion  — each seed pulls semantic neighbours, synonyms,
     triggers, and (for base words) spelling-prefix matches. Free, no key.
  2. Affix morphing      — prefix/suffix tweaks on strong words (get-, -ly,
     -ify, vowel endings) to mint near-words.
  3. Two-word blends     — concatenations and portmanteaus, the primary path
     when the founder supplies one or two base words.

Network calls (Datamuse) are best-effort: failures are swallowed so a flaky
connection degrades the pool rather than crashing the run.
"""

from __future__ import annotations

import time
from typing import Iterable

import requests

from .seeds import clean

DATAMUSE = "https://api.datamuse.com/words"

# Curated affixes. Kept short so morphs stay pronounceable / brandable.
PREFIXES = ["get", "try", "go", "my", "hey"]
SUFFIXES = ["ly", "ify", "io", "hq", "labs", "ai", "app", "kit", "hub"]
VOWEL_ENDINGS = ["a", "o", "ia", "us", "ix", "yx", "on"]


def datamuse_expand(word: str, max_results: int = 30,
                    include_spelling: bool = False) -> set[str]:
    """Pull related words for one seed via several Datamuse relations."""
    found: set[str] = set()
    endpoints = [
        f"ml={word}&max={max_results}",       # means-like (semantic)
        f"rel_syn={word}&max={max_results}",  # synonyms
        f"rel_trg={word}&max={max_results}",  # "triggered by" associations
        f"rel_jjb={word}&max=15",             # adjectives describing the noun
        f"rel_jja={word}&max=15",             # nouns the adjective describes
    ]
    if include_spelling:
        endpoints.append(f"sp={word}*&max={max_results}")  # starts-with
    for ep in endpoints:
        try:
            r = requests.get(f"{DATAMUSE}?{ep}", timeout=7)
            if r.ok:
                for item in r.json():
                    w = clean(item.get("word", ""))
                    if w:
                        found.add(w)
        except Exception:
            pass  # best-effort; a dropped endpoint just narrows the net
        time.sleep(0.08)  # be polite to the free API
    return found


def expand_seeds(seeds: dict[str, set[str]], per_category: int = 8,
                 base_words: Iterable[str] | None = None,
                 target: int | None = None, progress=None) -> dict[str, set[str]]:
    """Expand a {word: cats} seed map into a larger {word: cats} pool.

    Strategy:
      - Base words first (with spelling matches) — the founder's strongest
        signal.
      - Then round-robin across categories: round *r* expands the r-th seed of
        every category, up to `per_category` rounds. This spreads the net
        evenly across themes instead of exhausting one category first.
      - If `target` is given, stop **early** the moment the pool reaches it —
        with ~75 categories a few rounds is plenty, and this avoids needless
        Datamuse traffic on big-default runs.
    """
    pool: dict[str, set[str]] = {w: set(c) for w, c in seeds.items()}

    # Base words first — strongest founder signal, expanded most aggressively.
    for base in (base_words or []):
        b = clean(base)
        if not b:
            continue
        pool.setdefault(b, set()).add("base")
        for w in datamuse_expand(b, max_results=50, include_spelling=True):
            pool.setdefault(w, set()).add("base")

    # Group seeds by category for round-robin sampling.
    by_cat: dict[str, list[str]] = {}
    for w, cats in seeds.items():
        for c in cats:
            by_cat.setdefault(c, []).append(w)
    cat_names = list(by_cat.keys())

    expanded = 0
    reached = False
    for r in range(per_category):
        if reached:
            break
        for cat in cat_names:
            words = by_cat[cat]
            if r >= len(words):
                continue
            for w in datamuse_expand(words[r]):
                pool.setdefault(w, set()).add(cat)
            expanded += 1
            if progress and expanded % 20 == 0:
                progress(len(pool), target or 0, cat, expanded)
            if target and len(pool) >= target:
                reached = True
                break

    return pool


def affix_variants(words: Iterable[str], limit: int = 600) -> set[str]:
    """Mint near-words by attaching curated prefixes/suffixes/vowel endings."""
    out: set[str] = set()
    for w in words:
        if len(out) >= limit:
            break
        for p in PREFIXES:
            cw = clean(p + w)
            if cw:
                out.add(cw)
        for s in SUFFIXES:
            cw = clean(w + s)
            if cw:
                out.add(cw)
        # Vowel-ending morph: drop a trailing consonant cluster, add a vowel.
        for v in VOWEL_ENDINGS:
            cw = clean(w + v)
            if cw:
                out.add(cw)
    return out


def _portmanteau(a: str, b: str) -> set[str]:
    """A couple of natural blends of two words."""
    out: set[str] = set()
    # head of a + tail of b around the midpoint
    out.add(a[: max(2, len(a) // 2 + 1)] + b[len(b) // 2:])
    out.add(a + b[len(b) // 2:])
    out.add(a[: len(a) // 2 + 1] + b)
    return {c for c in (clean(x) for x in out) if c}


def blend_words(base_words: list[str], partners: Iterable[str],
                limit: int = 800) -> set[str]:
    """Combine each base word with partner words (concat + portmanteau).

    This is the main lever when the founder gives one or two seed words:
    `multiple` + `verse` -> `multiverse`, `multo`, etc.
    """
    out: set[str] = set()
    bases = [b for b in (clean(x) for x in base_words) if b]
    if not bases:
        return out
    partner_list = [p for p in (clean(x) for x in partners) if p]
    for base in bases:
        for p in partner_list:
            if len(out) >= limit:
                return out
            for combo in (base + p, p + base):
                cw = clean(combo)
                if cw:
                    out.add(cw)
            out |= _portmanteau(base, p)
        # base + base pair blends (only if two distinct bases supplied)
        for other in bases:
            if other != base:
                out |= _portmanteau(base, other)
                cw = clean(base + other)
                if cw:
                    out.add(cw)
    return out
