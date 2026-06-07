"""
Output writers.

Three artifacts per run:
  - candidates.csv : every generated word with scores + per-TLD status
  - available.csv  : only words with >=1 available TLD
  - shortlist.csv / shortlist.md : the headline deliverable — top picks,
    LLM-ranked with rationale when a model is connected, otherwise
    score-ranked.
"""

from __future__ import annotations

import csv
import os

from .availability import DomainResult


def _ensure_dir(outdir: str) -> None:
    os.makedirs(outdir, exist_ok=True)


def write_candidates(outdir: str, rows: list[dict], tlds: list[str]) -> str:
    """rows: dicts with word, length, syllables, score, tier, zipf, source,
    categories, and (optionally) a `statuses` {tld: status} dict."""
    _ensure_dir(outdir)
    path = os.path.join(outdir, "candidates.csv")
    base_cols = ["word", "length", "syllables", "score", "tier", "zipf",
                 "source", "categories"]
    status_cols = [f"{t}_status" for t in tlds]
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(base_cols + status_cols)
        for r in rows:
            statuses = r.get("statuses") or {}
            wr.writerow(
                [r.get(c, "") for c in base_cols]
                + [statuses.get(t, "") for t in tlds]
            )
    return path


def write_available(outdir: str, results: list[DomainResult], tlds: list[str],
                    meta: dict[str, dict]) -> str:
    """Only words with at least one available TLD. `meta[word]` -> score info."""
    _ensure_dir(outdir)
    path = os.path.join(outdir, "available.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["word", "score", "tier"]
                    + [f"{t}_available" for t in tlds]
                    + ["available_domains"])
        for res in results:
            if not res.any_available():
                continue
            m = meta.get(res.word, {})
            avail = res.available_tlds()
            wr.writerow(
                [res.word, m.get("score", ""), m.get("tier", "")]
                + ["yes" if t in avail else "" for t in tlds]
                + [" ".join(f"{res.word}.{t}" for t in avail)]
            )
    return path


def write_shortlist(outdir: str, shortlist: list[dict]) -> tuple[str, str]:
    """shortlist: ordered list of {word, tld, reason, score, tier}.

    Writes both a CSV and a friendly Markdown file (great for a launch post).
    """
    _ensure_dir(outdir)
    csv_path = os.path.join(outdir, "shortlist.csv")
    md_path = os.path.join(outdir, "shortlist.md")

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["rank", "domain", "word", "tld", "score", "tier", "reason"])
        for i, item in enumerate(shortlist, 1):
            domain = f"{item['word']}.{item['tld']}" if item.get("tld") else item["word"]
            wr.writerow([i, domain, item["word"], item.get("tld", ""),
                         item.get("score", ""), item.get("tier", ""),
                         item.get("reason", "")])

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# DomainForge shortlist\n\n")
        f.write("Top available domains, ranked. Verify at your registrar before buying.\n\n")
        f.write("| # | Domain | Score | Tier | Why |\n")
        f.write("|---|--------|-------|------|-----|\n")
        for i, item in enumerate(shortlist, 1):
            domain = f"{item['word']}.{item['tld']}" if item.get("tld") else item["word"]
            reason = (item.get("reason") or "").replace("|", "\\|")
            f.write(
                f"| {i} | **{domain}** | {item.get('score', '')} | "
                f"{item.get('tier', '')} | {reason} |\n"
            )
    return csv_path, md_path
