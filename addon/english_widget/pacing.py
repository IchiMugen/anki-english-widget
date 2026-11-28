"""Adaptive share of advanced (B2-C1) words among NEW cards.

Advanced words come rarely at first and more often as the base (A1-A2, B1-B2, Pro) is learned:

    share = 15% + 35% x (learned base words / all base words)      -> 15% ... 50%
    halved while advanced words are hard: > 20% "Again" on their reviews in the last 14 days

Only the ORDER of not-yet-seen cards changes (Anki's own "reposition new cards"). Studied cards,
intervals and FSRS are never touched. Inside each group the order stays as it was (deck order).

Level (add-on setting "level", chosen at the first start — level.py) changes the curve and the base order:
    beginner — A1-A2 words first, B1-B2 after them; advanced words only once 30% of the base is learned,
               then 0% ... 35%;
    medium   — as above (15% ... 50%), base in deck order;
    advanced — B1-B2 / Pro words before A1-A2; advanced words 35% ... 60% from the start.

Pure module (no aqt): called by stats.py on profile open, after sync and hourly.
"""
from __future__ import annotations

import time

NOTETYPE = "English Trainer"
ADVANCED = ("level::b2-c1", "level::c1-c2")
MATURE_DAYS = 21          # same as "выучено" on the deck screen
SHARE_MIN, SHARE_MAX = 0.15, 0.50
BRAKE_DAYS, BRAKE_MIN_ANSWERS, BRAKE_FAIL = 14, 15, 0.20


LEVELS = {"beginner": (0.0, 0.35, 0.30), "medium": (SHARE_MIN, SHARE_MAX, 0.0), "advanced": (0.35, 0.60, 0.0)}


def _tier(tags: str) -> int:
    return 0 if "level::a1-a2" in tags.lower() else 1


def _is_advanced(tags: str) -> bool:
    return any(t.lower() in ADVANCED for t in tags.split())


def plan(col, level: str = "medium") -> dict | None:
    """Current pacing numbers + the new-card order it implies (list of card ids)."""
    nt = col.models.by_name(NOTETYPE)
    if not nt:
        return None
    rows = col.db.all(
        "select c.id, c.nid, c.ord, c.type, c.ivl, c.due, n.tags from cards c "
        "join notes n on n.id = c.nid where n.mid = ?", nt["id"])
    notes: dict[int, dict] = {}
    for cid, nid, ord_, ctype, ivl, due, tags in rows:
        n = notes.setdefault(nid, {"adv": _is_advanced(tags), "tier": _tier(tags), "mature": True, "new": [], "pos": 10**9})
        n["mature"] &= ctype == 2 and ivl >= MATURE_DAYS
        if ctype == 0:
            n["new"].append((ord_, cid, due))
            n["pos"] = min(n["pos"], due)
    base = [n for n in notes.values() if not n["adv"]]
    progress = sum(n["mature"] for n in base) / max(len(base), 1)
    lo, hi, start = LEVELS.get(level, LEVELS["medium"])
    share = 0.0 if progress < start else lo + (hi - lo) * (progress - start) / max(1 - start, 1e-9)

    since = int((time.time() - BRAKE_DAYS * 86400) * 1000)
    adv_cids = [cid for cid, nid, *_ in rows if notes[nid]["adv"]]
    answers = fails = 0
    if adv_cids:
        answers, fails = col.db.first(
            "select count(), coalesce(sum(ease = 1), 0) from revlog where type = 1 and id > ? and cid in "
            f"({','.join(map(str, adv_cids))})", since)
    braked = answers >= BRAKE_MIN_ANSWERS and fails / answers > BRAKE_FAIL
    if braked:
        share /= 2

    def queue(adv):
        key = {"beginner": lambda n: (n["tier"], n["pos"]),
               "advanced": lambda n: (-n["tier"], n["pos"])}.get(level, lambda n: n["pos"])
        return sorted((n for n in notes.values() if n["adv"] == adv and n["new"]), key=key)

    b, a = queue(False), queue(True)
    order, acc = [], 0.0
    while b or a:
        acc += share
        take_adv = a and (acc >= 1 or not b)
        if take_adv and acc >= 1:
            acc -= 1
        n = (a if take_adv else b).pop(0)
        order += [cid for _, cid, _ in sorted(n["new"])]
    current = [cid for cid, _ in sorted(
        ((cid, due) for n in notes.values() for _, cid, due in n["new"]), key=lambda x: (x[1], x[0]))]
    return {
        "progress": progress, "share": share, "braked": braked,
        "every": round(1 / share) if share else 0, "level": level,
        "recent": (answers, fails), "order": order, "changed": order != current,
    }


def apply(col, level: str = "medium") -> dict | None:
    """Reposition new cards by plan(); does nothing when the order is already right."""
    p = plan(col, level)
    if p and p["changed"] and p["order"]:
        col.sched.reposition_new_cards(p["order"], starting_from=0, step_size=1,
                                       randomize=False, shift_existing=False)
    return p
