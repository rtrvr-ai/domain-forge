# Example output

These files are **real output** from a quick `--fast` run, committed so you can
see what DomainForge produces without running anything:

```bash
domainforge --fast --base "rune,forge" --check 40 --tlds com,ai -y
```

| File | What it is |
|------|------------|
| `shortlist.md` | The headline deliverable — top available domains, ranked. (With an LLM key connected, the **Why** column fills in with one-line rationales.) |
| `shortlist.csv` | Same shortlist, as CSV. |
| `available.csv` | Every name with at least one available TLD, with score + tier. |

A full default run (`domainforge`) generates **10,000** candidates and checks the
top **3,000** — these examples are a small slice.

> `demo.gif` is generated from [`../demo.tape`](../demo.tape) with
> [`vhs`](https://github.com/charmbracelet/vhs): `vhs demo.tape`.

Availability reflects instantdomainsearch's view at the time of the run — always
confirm at your registrar before buying.
