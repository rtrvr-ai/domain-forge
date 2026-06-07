"""
The orchestrator: brief/seeds -> candidate pool -> score -> availability ->
rank -> CSV/MD artifacts.

`run(config, llm_client)` performs the whole flow and returns a small summary
dict. It prints human-readable progress as it goes.
"""

from __future__ import annotations

import os

from . import generate, output, score, seeds
from .availability import check_words
from .config import Config
from .llm import LLMClient


def _hr(title: str) -> None:
    print(f"\n\033[1m▶ {title}\033[0m", flush=True)


def build_candidate_pool(cfg: Config, llm: LLMClient | None) -> dict[str, set[str]]:
    """Assemble {word: categories} from curated seeds + LLM + expansion +
    affixes + blends, capped at cfg.count by brandability score."""
    # 1. Curated seeds (subset by category if requested).
    pool = seeds.select(cfg.categories)
    print(f"  curated seeds: {len(pool)}")

    # 2. LLM seed-gen + coinages (optional).
    llm_seed_words: list[str] = []
    if llm and cfg.brief:
        _hr("LLM: generating on-theme seeds + coinages")
        gen = llm.generate_seeds(cfg.brief, cfg.llm_seeds)
        coin = llm.invent_coinages(cfg.brief, cfg.llm_coinages)
        llm_seed_words = gen + coin
        for w in llm_seed_words:
            cw = seeds.clean(w)
            if cw:
                pool.setdefault(cw, set()).add("llm")
        print(f"  LLM added: {len(gen)} seeds + {len(coin)} coinages")

    # 3. Datamuse expansion across seeds + base words (stops early at target).
    _hr(f"Expanding via Datamuse word graph (target pool: {cfg.count})")

    def _prog(pool_size, target, cat, expanded):
        tgt = f"/{target}" if target else ""
        print(f"  expanded {expanded} seeds — pool {pool_size}{tgt} "
              f"(latest: {cat})", flush=True)

    pool = generate.expand_seeds(
        pool, per_category=cfg.per_category, base_words=cfg.base_words,
        target=cfg.count, progress=_prog,
    )
    print(f"  pool after expansion: {len(pool)}")

    # 4. Combinations.
    if cfg.use_blends and cfg.base_words:
        _hr("Blending base words with the pool")
        partners = list(pool.keys())
        blends = generate.blend_words(cfg.base_words, partners)
        for w in blends:
            pool.setdefault(w, set()).add("blend")
        print(f"  blends added: {len(blends)}")

    if cfg.use_affixes:
        _hr("Minting affix variants")
        # Apply affixes to the strongest words to keep the morphs brandable.
        strong = sorted(pool.keys(), key=lambda w: -score.domain_score(w))[:300]
        variants = generate.affix_variants(strong)
        for w in variants:
            pool.setdefault(w, set()).add("affix")
        print(f"  affix variants added: {len(variants)}")

    return pool


def score_and_rank_pool(pool: dict[str, set[str]], cfg: Config) -> list[dict]:
    """Turn the pool into scored rows, sorted best-first, capped to cfg.count."""
    rows = []
    for word, cats in pool.items():
        tier = score.freq_tier(word)
        rows.append(
            {
                "word": word,
                "length": len(word),
                "syllables": score.count_syllables(word),
                "score": score.domain_score(word),
                "tier": tier,
                "zipf": score.zipf(word),
                "source": "seed" if cats & set(seeds.category_names()) else "expanded",
                "categories": "|".join(sorted(cats)),
            }
        )

    # Sort: prefer registrable tiers, then higher brandability score, shorter.
    tier_rank = {"invented": 0, "distinctive": 1, "rare": 2, "unknown": 2,
                 "familiar": 3, "generic": 4}
    rows.sort(key=lambda r: (tier_rank.get(r["tier"], 3), -r["score"], r["length"]))
    return rows[: cfg.count]


def run(cfg: Config, llm: LLMClient | None) -> dict:
    print("\n\033[1mDomainForge\033[0m — finding available, brandable domains\n")
    if llm:
        print(f"  intelligence: {llm.provider} ({llm.model})")
    else:
        print("  intelligence: none (pure algorithmic — set an API key to enable)")
    if not score.has_wordfreq():
        print("  note: install `wordfreq` for frequency tiering (better filtering)")

    # 1-4. Build + score the candidate pool.
    _hr("Building candidate pool")
    pool = build_candidate_pool(cfg, llm)
    rows = score_and_rank_pool(pool, cfg)
    print(f"\n  scored pool: {len(rows)} candidates (capped at {cfg.count})")

    # 5. Availability check on the top `check` candidates (floor: never more
    #    than the pool actually holds).
    to_check = [r["word"] for r in rows[: cfg.check]]
    _hr(f"Checking availability of top {len(to_check)} across {cfg.tlds}")
    est_min = max(1, round(len(to_check) * len(cfg.tlds) / cfg.max_workers / 120))
    print(f"  ~{est_min} min at {cfg.max_workers} workers — grab a coffee. "
          "Lower --check to go faster.", flush=True)
    results = check_words(to_check, cfg.tlds, max_workers=cfg.max_workers)

    # Merge statuses back into the candidate rows for candidates.csv.
    status_by_word = {res.word: res.statuses for res in results}
    for r in rows:
        if r["word"] in status_by_word:
            r["statuses"] = status_by_word[r["word"]]

    meta = {r["word"]: r for r in rows}

    # 6. Rank the available names (LLM if present, else by score).
    available = [(res.word, res.available_tlds()) for res in results if res.any_available()]
    _hr(f"Curating shortlist from {len(available)} available names")
    shortlist = _build_shortlist(available, cfg, llm, meta)

    # 7. Write artifacts.
    _hr("Writing output")
    cand_path = output.write_candidates(cfg.outdir, rows, cfg.tlds)
    avail_path = output.write_available(cfg.outdir, results, cfg.tlds, meta)
    sl_csv, sl_md = output.write_shortlist(cfg.outdir, shortlist)

    summary = {
        "candidates": len(rows),
        "checked": len(to_check),
        "available": len(available),
        "shortlist": len(shortlist),
        "files": {
            "candidates": cand_path,
            "available": avail_path,
            "shortlist_csv": sl_csv,
            "shortlist_md": sl_md,
        },
    }
    _print_summary(summary, shortlist)
    return summary


def _build_shortlist(available, cfg: Config, llm: LLMClient | None,
                     meta: dict[str, dict]) -> list[dict]:
    if not available:
        return []

    if llm:
        ranked = llm.rank(available, cfg.brief, cfg.shortlist)
        # Keep only words that are genuinely available; backfill if the LLM
        # returned fewer than requested.
        avail_set = {w for w, _ in available}
        avail_tlds = {w: t for w, t in available}
        out: list[dict] = []
        seen = set()
        for item in ranked:
            w = item["word"]
            if w in avail_set and w not in seen:
                tld = item.get("tld") or (avail_tlds[w][0] if avail_tlds[w] else "")
                if tld not in avail_tlds[w] and avail_tlds[w]:
                    tld = avail_tlds[w][0]
                m = meta.get(w, {})
                out.append({"word": w, "tld": tld, "reason": item.get("reason", ""),
                            "score": m.get("score", ""), "tier": m.get("tier", "")})
                seen.add(w)
        if len(out) >= cfg.shortlist:
            return out[: cfg.shortlist]
        # Backfill from score ranking.
        backfill = _score_ranked(available, cfg, meta, exclude=seen)
        return (out + backfill)[: cfg.shortlist]

    return _score_ranked(available, cfg, meta)[: cfg.shortlist]


def _score_ranked(available, cfg: Config, meta: dict[str, dict],
                  exclude: set | None = None) -> list[dict]:
    exclude = exclude or set()
    items = []
    for word, tlds in available:
        if word in exclude:
            continue
        m = meta.get(word, {})
        items.append(
            {
                "word": word,
                "tld": tlds[0] if tlds else "",
                "reason": "",
                "score": m.get("score", 0),
                "tier": m.get("tier", ""),
            }
        )
    items.sort(key=lambda x: (-(x["score"] or 0), len(x["word"])))
    return items


def _print_summary(summary: dict, shortlist: list[dict]) -> None:
    print("\n\033[1m✅ Done.\033[0m")
    print(f"   candidates generated : {summary['candidates']}")
    print(f"   names checked        : {summary['checked']}")
    print(f"   available found      : {summary['available']}")
    print(f"   shortlist            : {summary['shortlist']}")
    print("\n   files:")
    for label, path in summary["files"].items():
        print(f"     {label:<14} {path}")
    if shortlist:
        print("\n\033[1m   Top picks:\033[0m")
        for i, item in enumerate(shortlist[:10], 1):
            domain = f"{item['word']}.{item['tld']}" if item.get("tld") else item["word"]
            reason = f"  — {item['reason']}" if item.get("reason") else ""
            print(f"     {i:>2}. {domain:<22}{reason}")
