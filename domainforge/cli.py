"""
Command-line interface: flags + an interactive wizard.

Run bare (`python -m domainforge`) for the guided wizard where Enter accepts
every default. Pass any flag to override; pass `--non-interactive` (or `-y`)
to skip the wizard entirely and run on defaults + flags + config file.
"""

from __future__ import annotations

import argparse
import sys

from . import llm
from .config import Config, DEFAULT_CONFIG_FILE, load_config, load_dotenv
from .pipeline import run


def _split_csv(value: str) -> list[str]:
    return [v.strip() for v in value.replace(",", " ").split() if v.strip()]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="domainforge",
        description="Find brandable, available domain names end to end.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--brief", help="company / vibe description (powers LLM seed-gen)")
    p.add_argument("--base", help="one or two seed words, comma/space separated")
    p.add_argument("--categories", help="curated categories to use (default: all)")
    p.add_argument("--tlds", help="TLDs to check, comma/space separated (e.g. com,ai,io)")
    p.add_argument("--count", type=int, help="target size of the candidate pool")
    p.add_argument("--check", type=int, help="max names to availability-check")
    p.add_argument("--per-category", type=int, dest="per_category",
                   help="Datamuse seeds expanded per category")
    p.add_argument("--workers", type=int, dest="max_workers",
                   help="availability-check concurrency")
    p.add_argument("--shortlist", type=int, help="size of the final ranked shortlist")
    p.add_argument("--provider", choices=["auto", "claude", "openai", "gemini",
                                          "openrouter", "none"],
                   help="LLM provider (auto-detects from env keys)")
    p.add_argument("--model", help="override the provider's default model")
    p.add_argument("--outdir", help="output directory")
    p.add_argument("--no-affixes", action="store_true", help="disable affix variants")
    p.add_argument("--no-blends", action="store_true", help="disable two-word blends")
    speed = p.add_mutually_exclusive_group()
    speed.add_argument("--fast", action="store_true",
                       help="quick-scan preset (count 2500, check 500, workers 6)")
    speed.add_argument("--thorough", action="store_true",
                       help="deep-sweep preset (count 15000, check 6000)")
    p.add_argument("--config", default=DEFAULT_CONFIG_FILE, help="config file path")
    p.add_argument("--save-config", action="store_true",
                   help="save the resolved settings back to the config file")
    p.add_argument("-y", "--non-interactive", action="store_true",
                   help="skip the wizard; use defaults + flags + config")
    p.add_argument("--list-categories", action="store_true",
                   help="print available seed categories and exit")
    return p


# Speed presets — applied BEFORE explicit flags so a flag like `--count 99`
# still overrides the preset.
PRESETS = {
    "fast": {"count": 2500, "check": 500, "max_workers": 6},
    "thorough": {"count": 15000, "check": 6000},
}


def apply_preset(cfg: Config, args: argparse.Namespace) -> Config:
    name = "fast" if getattr(args, "fast", False) else (
        "thorough" if getattr(args, "thorough", False) else None)
    if name:
        for k, v in PRESETS[name].items():
            setattr(cfg, k, v)
    return cfg


def apply_flags(cfg: Config, args: argparse.Namespace) -> Config:
    if args.brief is not None:
        cfg.brief = args.brief
    if args.base is not None:
        cfg.base_words = _split_csv(args.base)
    if args.categories is not None:
        cfg.categories = _split_csv(args.categories)
    if args.tlds is not None:
        cfg.tlds = _split_csv(args.tlds)
    if args.count is not None:
        cfg.count = args.count
    if args.check is not None:
        cfg.check = args.check
    if args.per_category is not None:
        cfg.per_category = args.per_category
    if args.max_workers is not None:
        cfg.max_workers = args.max_workers
    if args.shortlist is not None:
        cfg.shortlist = args.shortlist
    if args.provider is not None:
        cfg.provider = args.provider
    if args.model is not None:
        cfg.model = args.model
    if args.outdir is not None:
        cfg.outdir = args.outdir
    if args.no_affixes:
        cfg.use_affixes = False
    if args.no_blends:
        cfg.use_blends = False
    return cfg


# ── Interactive wizard ───────────────────────────────────────────────
def _ask(prompt: str, default):
    shown = default if not isinstance(default, list) else ", ".join(default)
    raw = input(f"{prompt} [{shown}]: ").strip()
    return raw if raw else None


def _ask_bool(prompt: str, default: bool) -> bool:
    d = "Y/n" if default else "y/N"
    raw = input(f"{prompt} [{d}]: ").strip().lower()
    if not raw:
        return default
    return raw.startswith("y")


def wizard(cfg: Config) -> Config:
    print("\n\033[1mDomainForge setup\033[0m  (press Enter to accept each default)\n")

    v = _ask("Brief — describe your company/vibe (optional)", cfg.brief or "(none)")
    if v and v != "(none)":
        cfg.brief = v

    v = _ask("Base word(s) — one or two seeds, optional", cfg.base_words or "(none)")
    if v and v != "(none)":
        cfg.base_words = _split_csv(v)

    v = _ask("TLDs to check", cfg.tlds)
    if v:
        cfg.tlds = _split_csv(v)

    v = _ask("Categories (blank = all). Type 'list' to see them", "all")
    if v == "list":
        from .seeds import category_names
        print("   " + ", ".join(category_names()))
        v = _ask("Categories (blank = all)", "all")
    if v and v != "all":
        cfg.categories = _split_csv(v)

    cfg.use_blends = _ask_bool("Use two-word blends?", cfg.use_blends)
    cfg.use_affixes = _ask_bool("Use affix variants (get-, -ly, -ify, ...)?", cfg.use_affixes)

    v = _ask("Target candidate pool size", cfg.count)
    if v and v.isdigit():
        cfg.count = int(v)

    v = _ask("Max names to availability-check", cfg.check)
    if v and v.isdigit():
        cfg.check = int(v)

    # Provider — show what's detected and let the user choose.
    cfg = _wizard_provider(cfg)

    v = _ask("Output directory", cfg.outdir)
    if v:
        cfg.outdir = v

    return cfg


def _wizard_provider(cfg: Config) -> Config:
    detected = llm.detect_providers()
    if detected:
        print(f"\n  Detected API key(s): {', '.join(detected)} "
              f"(default: {detected[0]})")
        v = _ask("LLM provider — 'auto', a name, or 'none'", "auto")
        cfg.provider = v.lower() if v else "auto"
    else:
        print("\n  No LLM API key detected in the environment.")
        print("  Set one of: ANTHROPIC_API_KEY, OPENAI_API_KEY, "
              "GEMINI_API_KEY, OPENROUTER_API_KEY")
        print("  (in your shell or a local .env file) for smarter results.")
        if _ask_bool("Continue WITHOUT an LLM (pure algorithmic)?", True):
            cfg.provider = "none"
        else:
            print("  Add a key and re-run. Exiting.")
            sys.exit(0)
    return cfg


def resolve_llm(cfg: Config):
    if cfg.provider == "none":
        return None
    provider = None if cfg.provider == "auto" else cfg.provider
    client = llm.build_client(provider=provider, model=(cfg.model or None))
    if client is None and cfg.provider not in ("auto", "none"):
        print(f"  ! provider '{cfg.provider}' has no API key set — "
              "continuing without an LLM.")
    return client


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_dotenv()  # pick up keys from a local .env

    if args.list_categories:
        from .seeds import category_names
        print("Available categories:\n  " + "\n  ".join(category_names()))
        return 0

    cfg = load_config(args.config)
    cfg = apply_preset(cfg, args)   # preset first…
    cfg = apply_flags(cfg, args)    # …explicit flags win over it

    if not args.non_interactive:
        cfg = wizard(cfg)

    if args.save_config:
        cfg.save(args.config)
        print(f"  saved settings to {args.config}")

    llm_client = resolve_llm(cfg)

    try:
        run(cfg, llm_client)
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
