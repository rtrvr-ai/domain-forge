"""
Domain availability checks via instantdomainsearch.com's query-dns endpoint
(the same call their website makes — no key, no browser).

Ported and generalized from the user's battle-tested csvreqs.py: the TLD list
is now a parameter, and the checker is exposed as a function that returns
structured results instead of writing CSVs directly.

  POST https://cloud.instantdomainsearch.com/services/query-dns
  body {"names":[{"name":"koji","hash":"<hashCode(name,42)>","tlds":["com","ai"]}]}
  resp {"results":[{"tld":"com","isRegistered":true|false|null}, ...]}

  isRegistered == False  -> "available"
  isRegistered == True   -> "taken"
  isRegistered == None    -> "unknown"  (the service itself was unsure)

Reliability features kept from the original: 429/503 backoff, retry, and an
SSL cert-failure fallback (macOS python.org builds often can't find system
roots).
"""

from __future__ import annotations

import json
import ssl
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

URL = "https://cloud.instantdomainsearch.com/services/query-dns"
SEED = 42
TIMEOUT = 25
MAX_RETRIES = 3

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "accept": "application/json",
    "content-type": "application/json",
    "Referer": "https://instantdomainsearch.com/",
    # Deliberately no Accept-Encoding -> server returns plain JSON.
}

# ANSI colors for the live progress print.
GREEN, RED, GREY, RESET = "\033[92m", "\033[91m", "\033[90m", "\033[0m"


def _make_ssl_context() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        try:
            return ssl.create_default_context()
        except Exception:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            return ctx


_SSL_CTX = _make_ssl_context()
_INSECURE_CTX = ssl.create_default_context()
_INSECURE_CTX.check_hostname = False
_INSECURE_CTX.verify_mode = ssl.CERT_NONE
_use_insecure = {"on": False}


def hash_code(s: str, seed: int = SEED) -> str:
    """Port of the site's hashCode(): 32-bit signed string hash, as a string."""
    r = seed
    for ch in s:
        r = (r << 5) - r + ord(ch)
        r &= 0xFFFFFFFF
        if r >= 0x80000000:
            r -= 0x100000000
    return str(r)


def query(name: str, tlds: list[str]) -> tuple[dict[str, object], str | None]:
    """Return ({tld: True|False|None}, error_str_or_None) for one name."""
    payload = {"names": [{"name": name, "hash": hash_code(name), "tlds": tlds}]}
    body = json.dumps(payload).encode()
    last_err = None
    for attempt in range(MAX_RETRIES):
        ctx = _INSECURE_CTX if _use_insecure["on"] else _SSL_CTX
        try:
            req = urllib.request.Request(URL, data=body, method="POST", headers=HEADERS)
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
                data = json.load(r)
            out: dict[str, object] = {}
            for x in data.get("results", []):
                out[x.get("tld")] = x.get("isRegistered")
            return out, None
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}"
            if e.code in (429, 503):
                time.sleep(1.5 * (attempt + 1))
                continue
            break
        except urllib.error.URLError as e:
            last_err = f"URLError: {e.reason}"
            if "CERTIFICATE_VERIFY_FAILED" in str(e.reason) and not _use_insecure["on"]:
                _use_insecure["on"] = True
                continue
            time.sleep(1.0 * (attempt + 1))
        except Exception as e:  # noqa: BLE001 - surface, don't crash the pool
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(1.0 * (attempt + 1))
    return {}, last_err


def status_from(reg: object) -> str:
    if reg is True:
        return "taken"
    if reg is False:
        return "available"
    return "unknown"


def _color(status: str) -> str:
    return {"available": GREEN, "taken": RED}.get(status, GREY)


@dataclass
class DomainResult:
    word: str
    statuses: dict[str, str] = field(default_factory=dict)  # tld -> status
    error: str | None = None

    def any_available(self) -> bool:
        return any(s == "available" for s in self.statuses.values())

    def available_tlds(self) -> list[str]:
        return [t for t, s in self.statuses.items() if s == "available"]


def check_words(words: list[str], tlds: list[str], max_workers: int = 5,
                quiet: bool = False) -> list[DomainResult]:
    """Check availability for many words across the given TLDs.

    Preserves input order in the returned list. Prints a colored progress line
    per word unless `quiet`.
    """
    total = len(words)
    done = {"n": 0}
    lock = threading.Lock()

    def check_one(word: str) -> DomainResult:
        label = "".join(word.lower().split())
        regs, err = query(label, tlds)
        res = DomainResult(word=word, error=err)
        for tld in tlds:
            res.statuses[tld] = status_from(regs.get(tld))

        with lock:
            done["n"] += 1
            n = done["n"]
        if not quiet:
            cells = "  ".join(
                f"{_color(res.statuses[t])}{(word[:12] + '.' + t):<18}"
                f"{res.statuses[t]:>10}{RESET}"
                for t in tlds
            )
            note = f"   {GREY}<- {err}{RESET}" if err else ""
            print(f"[{n:>4}/{total}] {cells}{note}", flush=True)
        return res

    results_map: dict[str, DomainResult] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(check_one, w): w for w in words}
        for fut in as_completed(futures):
            res = fut.result()
            results_map[res.word] = res

    # De-dupe while preserving first-seen order.
    return [results_map[w] for w in dict.fromkeys(words) if w in results_map]
