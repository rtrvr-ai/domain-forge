"""
Configuration: built-in defaults, layered over an optional JSON config file,
the environment, CLI flags, and interactive answers.

Resolution order (lowest -> highest precedence):
    built-in DEFAULTS  <  config file  <  CLI flags / wizard answers

A `.env` file in the working directory (if present) is loaded first so API
keys are picked up without exporting them by hand.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field

DEFAULT_CONFIG_FILE = "domainforge.config.json"

# Built-in defaults — the "press Enter through everything" experience.
DEFAULTS: dict = {
    "brief": "",
    "base_words": [],          # one or two seed words from the founder
    "categories": [],          # empty -> all curated categories
    "tlds": ["com", "ai"],
    "use_affixes": True,
    "use_blends": True,
    "count": 10000,            # target size of the generated candidate pool
    "check": 3000,             # max names to availability-check (cost cap)
    "per_category": 8,         # Datamuse seeds expanded per category
    "max_workers": 5,          # availability check concurrency (be polite)
    "provider": "auto",        # auto | claude | openai | gemini | openrouter | none
    "model": "",               # blank -> provider default
    "llm_seeds": 120,          # how many LLM seed words to request
    "llm_coinages": 80,        # how many LLM coinages to request
    "shortlist": 25,           # size of the final ranked shortlist
    "outdir": "domainforge_out",
}


def load_dotenv(path: str = ".env") -> None:
    """Minimal .env loader (no dependency). Does not overwrite existing env."""
    if not os.path.exists(path):
        return
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                k, v = k.strip(), v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass


@dataclass
class Config:
    brief: str = ""
    base_words: list = field(default_factory=list)
    categories: list = field(default_factory=list)
    tlds: list = field(default_factory=lambda: ["com", "ai"])
    use_affixes: bool = True
    use_blends: bool = True
    count: int = 10000
    check: int = 3000
    per_category: int = 8
    max_workers: int = 5
    provider: str = "auto"
    model: str = ""
    llm_seeds: int = 120
    llm_coinages: int = 80
    shortlist: int = 25
    outdir: str = "domainforge_out"

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: str = DEFAULT_CONFIG_FILE) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)


def load_config(path: str = DEFAULT_CONFIG_FILE) -> Config:
    """Start from DEFAULTS, overlay a config file if present."""
    data = dict(DEFAULTS)
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data.update({k: v for k, v in json.load(f).items() if k in DEFAULTS})
        except Exception as e:  # noqa: BLE001
            print(f"  ! could not read {path}: {e} (using defaults)")
    return Config(**data)
