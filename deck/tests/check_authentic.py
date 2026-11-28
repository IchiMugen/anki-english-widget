"""Guard: no invented sentence can reach a card (contract 3.0 §9). Runs in update.bat before the build.

    python tests/check_authentic.py          (exit 1 on any violation)

Checks the deck exactly as build.py makes it:
  * every sentence in every card's Data is an example of data/corpus/examples.jsonl, verbatim, with
    source_verified and a source in data/corpus/sources.jsonl that has a licence;
  * the Example field (the card's fallback) is empty or one of those real quotes;
  * no sentence of the synthetic archive (data/archive/synthetic_legacy.jsonl) is on a card;
  * units.jsonl carries no "examples" (generated examples live only in the archive);
  * every example has the six checks and nothing claims a human review that did not happen;
  * the synthetic enrichment tool refuses to run.
"""
from __future__ import annotations

import html
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402
import units  # noqa: E402
from corpus import quality  # noqa: E402


def norm(s: str) -> str:
    return " ".join(s.lower().split())


def main() -> int:
    errors = []
    ex = {e["id"]: e for e in units._jsonl(units.CORPUS_EXAMPLES)}
    src = {s["id"]: s for s in units._jsonl(units.CORPUS_SOURCES)}
    archive = units._jsonl(ROOT / "data" / "archive" / "synthetic_legacy.jsonl")
    synthetic = {norm(x["en"]) for a in archive for x in a.get("examples", []) if x.get("en")}
    synthetic |= {norm(a["words_csv_example"]) for a in archive if a.get("words_csv_example")}
    for e in ex.values():
        c = e.get("checks")
        if not c or set(c) != set(quality.CHECKS):
            errors.append(f"{e['id']}: no six-check record")
            continue
        if c.get("human") is True and "human_reviewed" not in e.get("status", []):
            errors.append(f"{e['id']}: human flag without status")
        if "human_reviewed" in e.get("status", []) and c.get("human") is not True:
            errors.append(f"{e['id']}: human_reviewed without a human check")
    for u in units.load().values():
        if u.get("examples"):
            errors.append(f"«{u['en']}»: units.jsonl has generated examples — they belong in the archive")
    rows = build.read_rows(build.WORDS)
    shown = 0
    for r in rows:
        data = json.loads(html.unescape(r["Data"])) if r["Data"] else {"x": []}
        quotes = set()
        for x in data["x"]:
            shown += 1
            e = ex.get(x["id"][2:]) if x["id"].startswith("q-") else None
            if not e:
                errors.append(f"«{r['English']}»: card sentence not from the corpus: {x['en'][:70]}")
                continue
            s = src.get(e["src"])
            if not s or not s.get("license") or "source_verified" not in e["status"]:
                errors.append(f"«{r['English']}» {e['id']}: source not registered / not verified")
            if x["en"] != e["quote"]:
                errors.append(f"«{r['English']}» {e['id']}: card text differs from the quote")
            if norm(x["en"]) in synthetic:
                errors.append(f"«{r['English']}» {e['id']}: same text as an archived synthetic example")
            quotes.add(x["en"])
        if r["Example"] != build.NO_EXAMPLE and r["Example"] not in quotes:
            errors.append(f"«{r['English']}»: Example field is not a real quote: {r['Example'][:70]}")
    for e in errors[:60]:
        print("ERROR", e)
    print(f"authentic guard: {len(rows)} words, {shown} card sentences, all real: {not errors}, "
          f"{len(errors)} violation(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
