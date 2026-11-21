"""Wrong options for notes added right in Anki.

When you add an «English Trainer» note and leave WrongEN / WrongRU empty, three look-alike
words from your own collection are filled in (verbs with verbs, single word vs phrase, same
leading verb for phrasal verbs). Never invents words; with too few notes the card simply switches to
typing mode.
"""
from __future__ import annotations

import difflib
import re

from anki import hooks

NOTETYPE = "English Trainer"
STOP = ("to ", "a ", "an ", "the ")


def _norm(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "").strip().lower()
    for p in STOP:
        if s.startswith(p):
            s = s[len(p):]
    return s


def _alts(s: str) -> list[str]:
    return [a.strip() for a in (s or "").split(";") if a.strip()]


def _fill(col, note) -> None:
    if note.note_type()["name"] != NOTETYPE or (note["WrongEN"] and note["WrongRU"]):
        return
    en = _norm(note["English"])
    if not en:
        return
    words = en.split()
    is_verb = note["English"].strip().lower().startswith("to ")
    ru_own = {a.lower() for a in _alts(note["Russian"])}
    rows = col.db.all("select flds from notes where mid = ?", note.mid)
    cands = []
    for (flds,) in rows:
        f = flds.split("\x1f")
        o_en, o_ru = _norm(f[0]), _alts(f[1])
        if not o_en or o_en == en or not o_ru or o_ru[0].lower() in ru_own:
            continue
        ow = o_en.split()
        s = difflib.SequenceMatcher(None, en, o_en).ratio()
        if (len(ow) > 1) == (len(words) > 1):
            s += 0.5
        if len(words) > 1 and ow[0] == words[0]:
            s += 0.5
        if f[0].strip().lower().startswith("to ") == is_verb:
            s += 1.0  # same part of speech: verbs with verbs
        cands.append((s, f[0].strip(), o_ru[0]))
    cands.sort(reverse=True)
    pick = cands[:3]
    if len(pick) < 3:
        return
    note["WrongEN"] = "; ".join(p[1] for p in pick)
    note["WrongRU"] = "; ".join(p[2] for p in pick)


def _on_add(col, note, deck_id) -> None:
    try:
        _fill(col, note)
    except Exception as e:  # never block adding a note
        print("English Trainer autofill:", e)


hooks.note_will_be_added.append(_on_add)
