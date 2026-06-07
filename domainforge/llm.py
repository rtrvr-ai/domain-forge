"""
Optional LLM intelligence — connect your own model.

Supported providers (auto-detected from env keys):
  - Claude      ANTHROPIC_API_KEY      (official `anthropic` SDK)
  - OpenAI      OPENAI_API_KEY         (official `openai` SDK)
  - OpenRouter  OPENROUTER_API_KEY     (`openai` SDK pointed at OpenRouter)
  - Gemini      GEMINI_API_KEY / GOOGLE_API_KEY  (`google-generativeai`)

The LLM does three things to widen surface area and raise hit-rate:
  1. generate_seeds(brief)    — on-theme real/evocative seed words
  2. invent_coinages(brief)   — brandable made-up words (high availability)
  3. rank(candidates, brief)  — curate the available list with rationale

Everything here is optional. With no key (or no provider SDK installed),
`build_client()` returns None and the pipeline runs fully algorithmically.
Provider SDKs are imported lazily so the base install stays light.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

# Default models per provider. Claude's ID is pinned (verified current).
# The others are best-effort defaults — override with the matching *_MODEL
# env var if your account exposes a different latest model.
DEFAULT_MODELS = {
    "claude": "claude-opus-4-8",
    "openai": os.getenv("OPENAI_MODEL", "gpt-5.1"),
    "openrouter": os.getenv("OPENROUTER_MODEL", "openai/gpt-5.1"),
    "gemini": os.getenv("GEMINI_MODEL", "gemini-2.5-pro"),
}

ENV_KEYS = {
    "claude": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

# Preference order when several keys are present.
PREFERENCE = ["claude", "openai", "gemini", "openrouter"]


def detect_providers() -> list[str]:
    """Return providers (in preference order) that have an API key set."""
    found = []
    for p in PREFERENCE:
        env = ENV_KEYS[p]
        if os.getenv(env):
            found.append(p)
        elif p == "gemini" and os.getenv("GOOGLE_API_KEY"):
            found.append(p)
    return found


def _get_key(provider: str) -> str | None:
    key = os.getenv(ENV_KEYS[provider])
    if not key and provider == "gemini":
        key = os.getenv("GOOGLE_API_KEY")
    return key


# ── Robust JSON extraction (models sometimes wrap JSON in prose/fences) ──
def _extract_json(text: str):
    if not text:
        return None
    text = text.strip()
    # Strip ```json ... ``` fences.
    fence = re.search(r"```(?:json)?\s*(.+?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    # Try whole-string parse, then the first [...] / {...} span.
    for candidate in (text, _first_span(text, "[", "]"), _first_span(text, "{", "}")):
        if not candidate:
            continue
        try:
            return json.loads(candidate)
        except Exception:
            continue
    return None


def _first_span(text: str, open_ch: str, close_ch: str) -> str | None:
    start = text.find(open_ch)
    end = text.rfind(close_ch)
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1]
    return None


def _as_word_list(parsed) -> list[str]:
    """Coerce a parsed JSON value into a clean lowercase word list."""
    if parsed is None:
        return []
    if isinstance(parsed, dict):
        # Accept {"words": [...]} or first list value.
        for v in parsed.values():
            if isinstance(v, list):
                parsed = v
                break
        else:
            return []
    out: list[str] = []
    for item in parsed:
        if isinstance(item, str):
            w = item.strip().lower()
        elif isinstance(item, dict):
            w = str(item.get("word", "")).strip().lower()
        else:
            continue
        w = re.sub(r"[^a-z]", "", w)
        if 3 <= len(w) <= 14:
            out.append(w)
    return list(dict.fromkeys(out))


@dataclass
class LLMClient:
    provider: str
    model: str
    _key: str

    # ── Public capabilities ──────────────────────────────────────────
    def generate_seeds(self, brief: str, n: int = 120) -> list[str]:
        sys = (
            "You are a world-class startup naming strategist with deep "
            "knowledge of mythology, science, world languages, nature, art, "
            "and culture. You surface evocative words most people would miss."
        )
        user = (
            f"Brief about the company / vibe:\n{brief}\n\n"
            f"Produce {n} single words (lowercase, 3-12 letters, no spaces, "
            "letters only) that thematically resonate with this brief. Draw "
            "from MANY categories: mythology, dead and living languages, "
            "science, nature, gemstones, feelings, places, food. Favor "
            "distinctive, beautiful, or surprising words over common ones. "
            "Return ONLY a JSON array of strings, no commentary."
        )
        return _as_word_list(_extract_json(self._complete(sys, user)))[:n]

    def invent_coinages(self, brief: str, n: int = 80) -> list[str]:
        sys = (
            "You invent brandable company names — short, pronounceable, "
            "made-up words with the polish of names like Stripe, Vercel, "
            "Twilio, Notion, Figma."
        )
        user = (
            f"Brief about the company / vibe:\n{brief}\n\n"
            f"Invent {n} ORIGINAL coined words (not real dictionary words), "
            "4-8 letters, easy to say and spell, that evoke this brief. They "
            "should feel like premium .com/.ai brands and be likely to be "
            "registrable. Return ONLY a JSON array of lowercase strings."
        )
        return _as_word_list(_extract_json(self._complete(sys, user)))[:n]

    def rank(self, available, brief: str, n: int = 25) -> list[dict]:
        """Rank available domains. `available` = list of (word, [tlds]).

        Returns a list of {word, tld, reason} best-first.
        """
        listing = "\n".join(
            f"- {w} (available: {', '.join('.' + t for t in tlds)})"
            for w, tlds in available
        )
        sys = (
            "You are a startup naming strategist. You judge brand names on "
            "memorability, pronounceability, spelling-on-first-hearing, "
            "distinctiveness, and fit to the brief."
        )
        user = (
            f"Brief:\n{brief or '(no brief given — judge on general brand quality)'}\n\n"
            f"These domains are AVAILABLE to register:\n{listing}\n\n"
            f"Pick the {n} best and rank them best-first. For each, choose the "
            "single strongest TLD to recommend. Return ONLY a JSON array of "
            'objects: [{"word": "...", "tld": "...", "reason": "<8 words why>"}].'
        )
        parsed = _extract_json(self._complete(sys, user))
        out: list[dict] = []
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict) and item.get("word"):
                    out.append(
                        {
                            "word": str(item["word"]).strip().lower(),
                            "tld": str(item.get("tld", "")).strip().lstrip("."),
                            "reason": str(item.get("reason", "")).strip(),
                        }
                    )
        return out[:n]

    # ── Provider dispatch ────────────────────────────────────────────
    def _complete(self, system: str, user: str) -> str:
        try:
            if self.provider == "claude":
                return self._complete_claude(system, user)
            if self.provider in ("openai", "openrouter"):
                return self._complete_openai(system, user)
            if self.provider == "gemini":
                return self._complete_gemini(system, user)
        except Exception as e:  # noqa: BLE001 - never crash the run on LLM error
            print(f"  ! LLM call failed ({self.provider}): {e}")
        return ""

    def _complete_claude(self, system: str, user: str) -> str:
        import anthropic  # lazy import

        client = anthropic.Anthropic(api_key=self._key)
        # Opus 4.8: adaptive thinking, effort high, NO temperature/top_p.
        resp = client.messages.create(
            model=self.model,
            max_tokens=8000,
            system=system,
            thinking={"type": "adaptive"},
            output_config={"effort": "high"},
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text")

    def _complete_openai(self, system: str, user: str) -> str:
        from openai import OpenAI  # lazy import

        base_url = "https://openrouter.ai/api/v1" if self.provider == "openrouter" else None
        client = OpenAI(api_key=self._key, base_url=base_url)
        resp = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content or ""

    def _complete_gemini(self, system: str, user: str) -> str:
        import google.generativeai as genai  # lazy import

        genai.configure(api_key=self._key)
        model = genai.GenerativeModel(self.model, system_instruction=system)
        resp = model.generate_content(user)
        return getattr(resp, "text", "") or ""


def build_client(provider: str | None = None, model: str | None = None) -> LLMClient | None:
    """Construct an LLMClient, or return None if no usable provider.

    `provider=None` auto-selects the first detected key (preference order).
    """
    if provider is None:
        detected = detect_providers()
        provider = detected[0] if detected else None
    if not provider:
        return None
    key = _get_key(provider)
    if not key:
        return None
    chosen_model = model or DEFAULT_MODELS.get(provider, "")
    return LLMClient(provider=provider, model=chosen_model, _key=key)
