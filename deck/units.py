"""Vocabulary Units (data/units.jsonl) and the only door from the corpus to the cards.

PRINCIPLE (contract 3.0, permanent): real language first, then the unit, then the exercise.
Every sentence a card shows is a real quote from data/corpus/examples.jsonl with a registered source
(data/corpus/sources.jsonl). Generated sentences are never shown: the old ones are archived in
data/archive/synthetic_legacy.jsonl (status synthetic_legacy) and nothing in the build reads them.

data/words.csv stays the master list: one row = one Anki note (GUID, English, Russian, wrong options,
explanation, hint, tags, order; its old Example column is archived, not used). units.jsonl extends a
row by GUID — meanings, forms, contrasts, collocations, mistakes:

    {"guid": "...", "en": "to come across", "pos": "phrasal", "status": "full",
     "meanings": [{"id": "m1", "ru": ["наткнуться", "случайно найти"], "def": "...", "grammar": "come across sth"},
                  {"id": "m2", "ru": ["производить впечатление"], "def": "...", "from": "corpus"}],
     "forms": [...], "contrast": [...], "colloc": [...], "mistakes": [...],
     "corpus": {"batch": "pilot01", "examples": [...], "notes": [...], "rejected": [...]}}

status = authentic coverage (corpus/quality.py coverage): "full" / "partial" /
"insufficient_authentic_data" (no real example yet: the word stays, the card has no sentence — it is
never filled with an invented one). legacy_status = the old v2 enrichment status (rich / migrated).
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
UNITS = ROOT / "units.jsonl"
CORPUS_EXAMPLES = ROOT / "corpus" / "examples.jsonl"
CORPUS_SOURCES = ROOT / "corpus" / "sources.jsonl"
MIN_EXAMPLES = 5            # rich unit
MIN_EXAMPLES_COMPLEX = 6    # phrasal verbs, idioms, several meanings


def load(path: Path = UNITS) -> dict[str, dict]:
    units = {}
    if path.exists():
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                u = json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path.name}:{n}: {e}")
            units[u["guid"]] = u
    return units


def save(units: dict[str, dict], order: list[str], path: Path = UNITS) -> None:
    """One unit per line, in words.csv order (stable diffs)."""
    seen = set()
    lines = []
    for g in order + [g for g in units if g not in order]:
        if g in units and g not in seen:
            seen.add(g)
            lines.append(json.dumps(units[g], ensure_ascii=False, separators=(",", ":")))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def split_alts(s: str) -> list[str]:
    return [p.strip() for p in re.split(r"[;\n|]", s or "") if p.strip()]


def pos_of(row: dict) -> str:
    tags = row.get("Tags", "")
    m = re.search(r"pos::(\w+)", tags)
    if m:
        return m.group(1)
    return "verb" if row["English"].lower().startswith("to ") else "other"


def migrate(row: dict, guid: str) -> dict:
    """A unit built only from the words.csv row. No example: real ones come from the corpus."""
    return {"guid": guid, "en": row["English"], "pos": pos_of(row), "status": "insufficient_authentic_data",
            "meanings": [{"id": "m1", "ru": split_alts(row["Russian"])}]}


def is_complex(u: dict) -> bool:
    return u.get("pos") in ("phrasal", "idiom") or len(u.get("meanings", [])) > 1


def target_in(sentence: str, target: str) -> bool:
    return bool(target) and re.search(r"(?<![A-Za-z'])" + re.escape(target) + r"(?![A-Za-z])",
                                      sentence, re.I) is not None


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def source_label(s: dict | None) -> str:
    """Short attribution shown under a quote on the card."""
    if not s:
        return ""
    t, a, ti, d = s.get("type"), s.get("author") or "", s.get("title") or "", s.get("date") or ""
    yr = f" ({d[:4]})" if d[:4].isdigit() else ""
    if t == "talk":
        return f"TED · {a}" if a else f"TED · {ti}"
    if t in ("film", "series"):
        return ("сериал · " if t == "series" else "фильм · ") + ti + yr
    if t in ("book", "essay"):
        return f"книга · {a}, «{ti}»{yr}"
    if t == "news":
        return "новости · Wikinews" + (f", {d[-4:]}" if d[-4:].isdigit() else "")
    return ti


class SyntheticExampleError(ValueError):
    """A sentence without a verified real source tried to reach a card."""


def load_corpus(public: bool = False) -> dict[str, list[dict]]:
    """guid -> authentic examples for the card — the ONLY source of card sentences.
    An example qualifies only with: source_verified, a source id present in the Source Registry with a
    licence, not synthetic, not rejected, no open doubt. public=True also requires a source that may be
    redistributed (public domain / CC BY / CC BY-SA)."""
    src = {s["id"]: s for s in _jsonl(CORPUS_SOURCES)}
    out: dict[str, list[dict]] = {}
    for e in _jsonl(CORPUS_EXAMPLES):
        s = src.get(e.get("src", ""))
        st = e.get("status", [])
        if (not s or not s.get("license") or "not resolved" in (s.get("title") or "")   # unknown work = no attribution
                or "source_verified" not in st or "rejected" in st
                or e.get("origin") == "synthetic" or e.get("doubt")
                or (public and not s.get("public"))):
            continue
        out.setdefault(e["guid"], []).append({"id": "q-" + e["id"], "en": e["quote"], "ru": e.get("ru", ""),
                                              "t": e["t"], "m": e.get("m", "m1"), "s": source_label(s)})
    return out


def card_data(u: dict | None, corpus: list[dict] | None = None) -> str:
    """The compact JSON for the hidden Data field (HTML-escaped).
    corpus = the word's authentic examples from load_corpus — nothing else can become a card sentence."""
    if not u:
        return ""
    xs = list(corpus or [])
    for x in xs:
        if not str(x.get("id", "")).startswith("q-") or not x.get("s"):
            raise SyntheticExampleError(f"«{u.get('en')}»: example without a verified source: {x.get('en', '')[:60]}")
    d = {"v": 1, "m": [{k: v for k, v in (("id", m["id"]), ("ru", m.get("ru", [])), ("def", m.get("def", "")),
                                          ("g", m.get("grammar", ""))) if v}
                       for m in u.get("meanings", [])],
         "x": xs}
    for k_in, k_out in (("forms", "f"), ("def", "d"), ("colloc", "co")):
        if u.get(k_in):
            d[k_out] = u[k_in]
    if u.get("contrast"):
        d["c"] = [{k: v for k, v in (("en", c["en"]), ("ru", c.get("ru", "")), ("n", c.get("note", ""))) if v}
                  for c in u["contrast"]]
    return html.escape(json.dumps(d, ensure_ascii=False, separators=(",", ":")), quote=False)
