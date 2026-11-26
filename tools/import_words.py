"""Refresh deck/words.csv from a bigger word list in the same format (the maintainer's own list).

    python tools/import_words.py path/to/words.csv

* words tagged domain::3d / techart / it / ai are left out (too narrow for everyone);
* words already in deck/words.csv keep their GUID (so people who imported the deck keep their progress),
  new words keep the GUID from the source list;
* words that are only in deck/words.csv stay, at the front of the queue;
* deck/units.jsonl (meanings, examples, forms…) is copied from the units.jsonl next to the source list;
* run deck/tests/check_deck.py and deck/build.py afterwards.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "deck" / "words.csv"
SKIP = {"domain::3d", "domain::techart", "domain::it", "domain::ai"}


def load(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        return rd.fieldnames, list(rd)


def key(en):
    return " ".join(en.lower().split())


def main(src):
    fields, current = load(DEST)
    _, source = load(src)
    cur = {key(r["English"]): r for r in current}
    out, seen = [], set()
    src_keys = {key(r["English"]) for r in source}
    for r in current:                               # public-only words first
        if key(r["English"]) not in src_keys:
            out.append(r)
            seen.add(key(r["English"]))
    skipped = 0
    for r in source:
        k = key(r["English"])
        if k in seen:
            continue
        if SKIP & set(r.get("Tags", "").split()):
            skipped += 1
            continue
        row = {f: r.get(f, "") for f in fields}
        if k in cur:
            row["GUID"] = cur[k]["GUID"]            # keep what people already have
        out.append(row)
        seen.add(k)
    with open(DEST, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out)
    print(f"deck/words.csv: {len(out)} words (was {len(current)}), left out {skipped} narrow-domain words")
    write_units(Path(src).with_name("units.jsonl"), out)


def write_units(src_units, rows):
    """deck/units.jsonl: the rich data of the same words (by English text), with this deck's GUIDs."""
    sys.path.insert(0, str(ROOT / "deck"))
    import build as deck_build
    import units as deck_units
    private = {}
    if src_units.exists():
        for line in src_units.read_text(encoding="utf-8").splitlines():
            if line.strip():
                u = json.loads(line)
                private[key(u["en"])] = u
    out, order, rich = {}, [], 0
    for r in rows:
        r = {k: (v or "").strip() for k, v in r.items()}
        guid = deck_build.note_guid(r)
        order.append(guid)
        u = private.get(key(r["English"]))
        if u:
            u = dict(u, guid=guid)
            rich += u.get("status") == "rich"
        else:
            u = deck_units.migrate(r, guid)
        out[guid] = u
    deck_units.save(out, order)
    print(f"deck/units.jsonl: {len(out)} units, {rich} enriched")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
