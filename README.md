# DomainForge 🛠️

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.9-blue.svg)](pyproject.toml)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#contributing)
[![Bring your own LLM](https://img.shields.io/badge/LLM-Claude%20%7C%20OpenAI%20%7C%20Gemini%20%7C%20OpenRouter-8A2BE2.svg)](#bring-your-own-model)

**Find brandable domain names that are actually available — end to end.**

![DomainForge demo](examples/demo.gif)

Squatters have hoovered up the obvious `.com` and `.ai` names. DomainForge
brute-forces *creativity* instead: it takes a vibe (a brief and/or one or two
seed words), expands it into thousands of candidates, scores them for
brandability, checks **real availability** across the TLDs you care about, and
hands you a ranked shortlist.

It works with zero configuration (press Enter through everything) and with zero
API keys (pure-algorithmic). Plug in your own LLM — **Claude, OpenAI, Gemini, or
OpenRouter** — for a smarter seed pool and a curated shortlist with rationales.

> This grew out of a real hunt that turned up new domains for me. The fragmented scripts behind those finds are now one clean tool.

---

## How it works

```
brief + base words + categories + knobs
   │
   ├─ curated corpus  (~75 categories, 2,600+ words: mythology, science, world
   │                   languages, food, water bodies, animals, plants, mountains,
   │                   neighborhoods, pop culture, constellations, alchemy, coinages…)
   ├─ LLM seed-gen + invented coinages         (optional — your model)
   ├─ Datamuse word graph  (semantic neighbours, synonyms, triggers, spelling)
   ├─ affix variants  (get-, -ly, -ify, vowel endings…)
   └─ two-word blends  (multiple + verse → multiverse…)
        │
        ▼  score: length · syllables · vowel-ending · pronounceability · rarity
        ▼  availability: instantdomainsearch over your TLDs (threaded, retrying)
        ▼  rank: LLM-curated shortlist with rationale (or score-ranked fallback)
        │
        ▼  candidates.csv  ·  available.csv  ·  shortlist.csv + shortlist.md
```

No API keys are required for generation (Datamuse) or availability checks
(instantdomainsearch) — both are free, public services.

---

## Install

**As a CLI** (gives you a `domainforge` command anywhere):

```bash
cd domainforge
pipx install ".[recommended]"        # isolated, recommended
# or:  pip install ".[recommended]"
```

Then just run `domainforge`. Add LLM support with extras:

```bash
pipx install ".[recommended,llm]"    # all providers
# or pick one:  ".[recommended,claude]" / "[...,openai]" / "[...,gemini]"
```

**Or run without installing:**

```bash
pip install -r requirements.txt      # core + recommended (wordfreq, certifi)
python3 -m domainforge               # same tool, module form
```

Add a key (optional) by copying `.env.example` to `.env` and filling in one
provider, or just `export ANTHROPIC_API_KEY=...` in your shell.

> **`python` vs `python3`:** modern macOS/Linux ship only `python3` (there's no
> bare `python`). The examples below use the installed **`domainforge`** command
> so it just works everywhere. Didn't install? Swap in `python3 -m domainforge`
> (Windows: `py -m domainforge`).

---

## Quickstart

**Guided wizard** (Enter accepts every default):

```bash
domainforge
```

**One-liner, no LLM** — blend two seed words and check `.com`/`.ai`:

```bash
domainforge --base "rune,forge" --check 200 -y
```

**Full power with a brief + extra TLDs:**

```bash
domainforge \
  --brief "an autonomous web agent that does multi-step workflows for you" \
  --base "multiple" \
  --tlds com,ai,io,co \
  --count 10000 --check 3000 \
  --shortlist 30
```

> **Defaults are big on purpose:** generate **10,000** candidates and
> availability-check the top **3,000**. Generation is fast and free; checking
> is the slow part (~10–20 min at the default polite concurrency). Lower
> `--check` for a quick pass, or raise it for an exhaustive sweep.

Outputs land in `domainforge_out/`:

| File | What it is |
|------|------------|
| `shortlist.md` / `shortlist.csv` | **Start here.** Top available domains, ranked, with reasons. |
| `available.csv` | Every name with ≥1 available TLD. |
| `candidates.csv` | The full scored pool with per-TLD status. |

See [`examples/`](examples/) for committed sample output.

### Presets

Two shortcuts set the volume knobs for you (explicit flags still override):

```bash
domainforge --fast      --base "rune,forge"   # quick scan: count 2500, check 500, ~2-4 min
domainforge --thorough  --brief "..."          # deep sweep: count 15000, check 6000
```

---

## Options

| Flag | Default | Meaning |
|------|---------|---------|
| `--brief` | — | Company/vibe description; powers LLM seed-gen & ranking. |
| `--base` | — | One or two seed words (comma/space separated). |
| `--categories` | all | Curated categories to draw from (`--list-categories` to see them). |
| `--tlds` | `com,ai` | TLDs to check (`com,ai,io,co,xyz,app,dev,so,…`). |
| `--count` | 10000 | Target size of the candidate pool (generation stops early once reached). |
| `--check` | 3000 | Max names to availability-check, top-ranked first (cost/time cap). |
| `--shortlist` | 25 | Size of the final ranked shortlist. |
| `--provider` | auto | `auto` / `claude` / `openai` / `gemini` / `openrouter` / `none`. |
| `--model` | — | Override the provider's default model. |
| `--fast` / `--thorough` | — | Volume presets (quick scan / deep sweep). |
| `--no-affixes`, `--no-blends` | off | Turn off a combination strategy. |
| `--workers` | 5 | Availability-check concurrency (keep modest — be polite). |
| `--outdir` | `domainforge_out` | Output directory. |
| `-y`, `--non-interactive` | off | Skip the wizard; use defaults + flags + config. |
| `--save-config` | off | Persist resolved settings to `domainforge.config.json`. |

Everything is also configurable via `domainforge.config.json` (copy the
`.example`). Resolution order: built-in defaults → config file → flags/wizard.

---

## Bring your own model

DomainForge auto-detects the first API key it finds (preference order: Claude →
OpenAI → Gemini → OpenRouter) and uses it for three things:

1. **Seed generation** — turns your brief into on-theme words across many
   domains of knowledge most lists miss.
2. **Coinage** — invents brandable made-up words tuned to your brief.
3. **Ranking** — curates the available list into a shortlist with one-line
   rationales.

| Provider | Env key | Default model | Override |
|----------|---------|---------------|----------|
| Claude | `ANTHROPIC_API_KEY` | `claude-opus-4-8` | `--model` |
| OpenAI | `OPENAI_API_KEY` | `OPENAI_MODEL` (best-effort) | env / `--model` |
| OpenRouter | `OPENROUTER_API_KEY` | `OPENROUTER_MODEL` | env / `--model` |
| Gemini | `GEMINI_API_KEY` | `GEMINI_MODEL` | env / `--model` |

The Claude path uses the official SDK with adaptive thinking. The non-Claude
default model IDs are best-effort — if one 404s, set the matching `*_MODEL` env
var (or `--model`) to your account's current model.

**No key? No problem.** Every step that needs an LLM is skipped and the pipeline
runs fully algorithmically; the shortlist is ranked by the brandability score
instead.

---

## Notes & caveats

- **Availability ≠ purchased.** Results reflect instantdomainsearch's DNS/registry
  view. Always confirm at your registrar before buying.
- DomainForge does **not** register domains — it finds candidates.
- Datamuse and instantdomainsearch are free, rate-limited public services. Keep
  `--workers` modest; the checker already backs off on 429/503.
- `wordfreq` is optional but recommended — it powers the rarity tier that
  separates registrable gems from always-taken generic words.

## Project layout

```
domainforge/
  seeds.py         curated corpus + category selection
  generate.py      Datamuse expansion, affixes, blends
  score.py         brandability score + frequency tier
  availability.py  instantdomainsearch checker (any TLD)
  llm.py           Claude / OpenAI / Gemini / OpenRouter abstraction
  config.py        layered config + .env loader
  pipeline.py      orchestration
  output.py        CSV / Markdown writers
  cli.py           flags + interactive wizard
```

## Share your finds

Found a gem? **Post it.** Screenshot your `shortlist.md`, tag the domain you
grabbed, and link back so other founders can dig too. The best names are the
ones nobody else thought to generate — show people what the long tail looks like.

## Contributing

PRs welcome — especially new seed categories (the more obscure, the better),
extra TLDs, and additional LLM providers. Open an issue with ideas, or send a
PR adding a category to `domainforge/seeds.py`.

---

MIT-licensed (see [LICENSE](LICENSE)). Built for founders, by founders.
