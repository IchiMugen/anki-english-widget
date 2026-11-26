"""Vocabulary Units: the rich data behind each word (deck/units.jsonl).

deck/words.csv stays the master list: one row = one Anki note (GUID, English, Russian, wrong options,
explanation, hint, tags, order). deck/units.jsonl extends a row by GUID — one JSON object per line:

    {"guid": "...", "en": "to come across", "pos": "phrasal", "status": "rich",
     "def": "to find or meet by chance",
     "forms": ["come across", "comes across", "came across", "coming across"],
     "meanings": [{"id": "m1", "ru": ["наткнуться", "случайно найти"], "def": "...", "grammar": "come across sth"},
                  {"id": "m2", "ru": ["производить впечатление"], "def": "...", "grammar": "come across as + adj"}],
     "examples": [{"id": "e1", "en": "I came across an old photo.", "ru": "Я наткнулся на старое фото.",
                   "t": "came across", "m": "m1", "ctx": "home", "gp": "past simple", "lvl": 1,
                   "src": "generated", "st": "auto"}],
     "contrast": [{"en": "run into", "ru": "случайно встретить", "note": "run into — о людях"}],
     "colloc": ["come across a problem"], "mistakes": ["..."], "pron": "/.../", "doubts": ["..."]}

status:  "migrated" — only what words.csv had (one legacy example, one meaning);
         "rich"     — meanings, 5+ examples with Russian translations, forms (target: 6–8 for phrasal/polysemous).
example st: "legacy" (from words.csv), "auto" (generated + passed automatic checks),
            "review" (doubtful — kept out of the cards until fixed). Nothing is marked as checked by a human.
src is always "generated" or "legacy": examples are written for the deck, they are not quotes.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
UNITS = ROOT / "units.jsonl"
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
    """A unit built only from the words.csv row (status "migrated")."""
    u = {"guid": guid, "en": row["English"], "pos": pos_of(row), "status": "migrated",
         "meanings": [{"id": "m1", "ru": split_alts(row["Russian"])}], "examples": []}
    ex = (row.get("Example") or "").strip()
    if ex:
        u["examples"].append({"id": "e1", "en": ex, "ru": "", "t": "", "m": "m1",
                              "src": "legacy", "st": "legacy"})
    return u


def is_complex(u: dict) -> bool:
    return u.get("pos") in ("phrasal", "idiom") or len(u.get("meanings", [])) > 1


def target_in(sentence: str, target: str) -> bool:
    return bool(target) and re.search(r"(?<![A-Za-z'])" + re.escape(target) + r"(?![A-Za-z])",
                                      sentence, re.I) is not None


def card_data(u: dict | None) -> str:
    """The compact JSON for the hidden Data field (HTML-escaped). Doubtful examples stay out."""
    if not u:
        return ""
    xs = [{"id": e["id"], "en": e["en"], "ru": e.get("ru", ""), "t": e.get("t", ""), "m": e.get("m", "m1")}
          for e in u.get("examples", []) if e.get("st") != "review"]
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
