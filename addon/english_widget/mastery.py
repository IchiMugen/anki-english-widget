"""Vocabulary mastery: four skills per word, kept apart from Anki's schedule.

    meaning      — knows what it means            (EN → RU card, "what does it mean here")
    recognition  — recognises it in new sentences  (context card: gaps, contrast, listening)
    retrieval    — brings it up from memory        (RU → EN card: typing, gaps with a Russian situation)
    production   — uses it in a sentence of one's own (self-checked translation / own sentence)

Speed: only the time the card itself measures (question shown -> answer given, desktop log);
Anki's own answer time also counts reading the result and the audio, so it is not used for speed.

Sources (newest first, last few events per skill):
  * Anki's review log — every scheduled answer on any device (ease + answer time);
  * the exercise log — desktop answers with details (exercise, example, typo, time), and
    Reinforcement ("Закрепление") results. It lives in the collection config, one small key per
    word ("etLog:<guid>"), so it syncs through AnkiWeb with the rest of the collection.

Reinforcement results only count AGAINST a skill (a mistake marks it weak); a right answer
there never makes a skill "strong" — extra practice must not inflate the progress.
Nothing here changes intervals: FSRS keeps scheduling the three cards as before.
"""
from __future__ import annotations

import time

NOTETYPE = "English Trainer"
SKILL_OF_ORD = {0: "retrieval", 1: "meaning", 2: "recognition"}
KIND_SKILL = {"meaning": "meaning", "situation": "retrieval", "contrast": "recognition", "listen": "recognition",
              "produce": "production", "sentence": "production"}
DIR_SKILL = {"ru-en": "retrieval", "en-ru": "meaning", "ctx": "recognition"}
SLOW_MS = {"choice": 7000, "meaning": 9000, "contrast": 9000}   # anything else (typing): 14 s
SLOW_DEFAULT_MS = 14000
LOG_KEEP = 40
LOG_PREFIX = "etLog:"


def skill_of(direction: str, kind: str) -> str:
    return KIND_SKILL.get(kind) or DIR_SKILL.get(direction, "retrieval")


def is_slow(kind: str, ms: int) -> bool:
    return bool(ms) and ms > SLOW_MS.get(kind, SLOW_DEFAULT_MS)


# ---------------------------------------------------------------- exercise log (collection config)
def log_get(col, guid: str) -> list:
    try:
        return list(col.get_config(LOG_PREFIX + guid, []) or [])
    except Exception:
        return []


def log_add(col, guid: str, entry: dict, source: str) -> None:
    """entry: {d, k, x, s, near, ms, e} from the card; source: 's' scheduled, 'p' practice."""
    ok = 1 if entry.get("s") in ("correct",) or (entry.get("s") == "self" and int(entry.get("e", 0)) >= 3) else 0
    if entry.get("near") and int(entry.get("e", 0)) == 2:
        ok = 2                                    # typo, accepted
    rec = [int(time.time()), str(entry.get("d", ""))[:5], str(entry.get("k", ""))[:10], str(entry.get("x", ""))[:6],
           ok, int(entry.get("ms") or 0), source, 1 if entry.get("near") else 0]
    log = log_get(col, guid)
    log.append(rec)
    col.set_config(LOG_PREFIX + guid, log[-LOG_KEEP:])


# ---------------------------------------------------------------- state
def _level(events: list[tuple[int, int, str, str]]) -> str:
    """events newest first: (ok, ms, kind, source). ok: 1 right, 2 typo, 0 wrong."""
    if not events:
        return "none"
    recent = events[:4]
    fails = sum(1 for ok, _, _, _ in recent if ok == 0)
    if fails >= 2 or (len(recent) >= 2 and recent[0][0] == 0 and recent[1][0] == 0):
        return "weak"
    scheduled = [e for e in events if e[3] != "p"]
    good = [e for e in scheduled[:5] if e[0] == 1]
    slow = [e for e in good if is_slow(e[2], e[1])]
    if len(good) >= 3 and len(slow) * 2 >= len(good):
        return "weak"                              # right, but slowly most of the time: not automatic yet
    if len(scheduled) >= 3 and all(e[0] == 1 for e in scheduled[:3]) and not slow:
        return "strong"
    return "ok"


def note_state(col, nid: int, guid: str) -> dict:
    """{'m': {skill: level}, 'exw': [weak example ids], 'exs': [seen example ids]}"""
    per: dict[str, list] = {s: [] for s in ("meaning", "recognition", "retrieval", "production")}
    # scheduled answers from every device (Anki's review log)
    rows = col.db.all(
        "select r.id, c.ord, r.ease, r.time from revlog r join cards c on c.id = r.cid "
        "where c.nid = ? and r.type in (0, 1, 2, 3) and r.ease > 0 order by r.id desc limit 60", nid)
    log = log_get(col, guid)
    # desktop details replace the plain review-log line of the same answer (same second ± 5 s)
    detailed = {rec[0] for rec in log if rec[6] == "s"}
    for rid, ord_, ease, ms in rows:
        ts = rid // 1000
        if any(abs(ts - d) <= 5 for d in detailed):
            continue
        # Anki's answer time includes reading the result and waiting for the audio: not a recall time
        per[SKILL_OF_ORD.get(ord_, "retrieval")].append((ts, 1 if ease > 1 else 0, 0, "", "s"))
    for ts, d, k, x, ok, ms, src, *_ in log:
        per[skill_of(d, k)].append((ts, ok, ms, k, src))
    m = {}
    for skill, evs in per.items():
        evs.sort(key=lambda e: -e[0])
        m[skill] = _level([(ok, ms, k, src) for _, ok, ms, k, src in evs])
    # examples: which ones failed lately, which were seen
    last_by_x: dict[str, list] = {}
    for ts, d, k, x, ok, ms, src, *_ in sorted(log, key=lambda r: -r[0]):
        if x:
            last_by_x.setdefault(x, []).append(ok)
    exw = [x for x, oks in last_by_x.items() if 0 in oks[:2]]
    return {"m": m, "exw": exw, "exs": list(last_by_x)}


def card_info(col, card) -> dict:
    info = {"type": card.type, "ivl": card.ivl, "lapses": card.lapses}
    try:
        note = card.note()
        info.update(note_state(col, note.id, note.guid))
    except Exception as e:
        print("English Trainer mastery:", e)
    return info
