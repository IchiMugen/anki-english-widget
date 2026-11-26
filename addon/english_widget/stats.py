"""Progress by level on the deck overview screen (Anki Desktop).

A word (note) counts as
  * learned  — all its cards have an interval of >= 21 days (long-term memory)
  * started  — at least one card has been studied
Levels come from tags level::<name>, so new levels appear automatically.
"""
from __future__ import annotations

import html

from aqt import gui_hooks, mw
from aqt.qt import QTimer

from . import pacing

NOTETYPE = "English Trainer"
MATURE_DAYS = 21
LABELS = {"A1-A2": "Базовый", "B1-B2": "Продвинутый", "B2-C1": "Высокий", "C1-C2": "Свободный", "Pro": "Профессия"}


def level_stats(col) -> list[dict]:
    """[{level, total, started, learned}] for every level:: tag on English Trainer notes."""
    nt = col.models.by_name(NOTETYPE)
    if not nt:
        return []
    rows = col.db.all(
        "select n.id, n.tags, c.type, c.ivl from notes n join cards c on c.nid = n.id where n.mid = ?", nt["id"])
    notes: dict[int, dict] = {}
    for nid, tags, ctype, ivl in rows:
        n = notes.setdefault(nid, {"tags": tags, "studied": False, "mature": True})
        n["studied"] |= ctype != 0
        n["mature"] &= ctype == 2 and ivl >= MATURE_DAYS
    levels: dict[str, dict] = {}
    for n in notes.values():
        lv = next((t.split("::", 1)[1] for t in n["tags"].split() if t.lower().startswith("level::")), "—")
        s = levels.setdefault(lv, {"level": lv, "total": 0, "started": 0, "learned": 0})
        s["total"] += 1
        s["started"] += n["studied"]
        s["learned"] += n["mature"]
    return [levels[k] for k in sorted(levels)]


def render(stats: list[dict]) -> str:
    if not stats:
        return ""
    total = sum(s["total"] for s in stats)
    learned = sum(s["learned"] for s in stats)
    rows = ""
    for s in stats:
        t = max(s["total"], 1)
        lp = 100 * s["learned"] / t
        sp = 100 * (s["started"] - s["learned"]) / t
        name = LABELS.get(s["level"], "")
        title = f"{html.escape(name)} <span style='opacity:.6'>{html.escape(s['level'])}</span>" if name else html.escape(s["level"])
        rows += (
            "<div style='margin:10px 0'>"
            "<div style='display:flex;justify-content:space-between;gap:12px'>"
            f"<span>{title}</span>"
            f"<span style='opacity:.75'>{s['learned']} выучено · {s['started'] - s['learned']} в изучении · {s['total']}</span>"
            "</div>"
            "<div style='height:8px;border-radius:99px;background:rgba(128,128,128,.22);overflow:hidden;display:flex;margin-top:5px'>"
            f"<div style='width:{lp:.1f}%;background:#16a34a'></div>"
            f"<div style='width:{sp:.1f}%;background:rgba(22,163,74,.38)'></div>"
            "</div></div>"
        )
    return (
        "<div style='max-width:440px;margin:22px auto 6px;text-align:left;font-size:14px'>"
        "<div style='display:flex;justify-content:space-between;font-weight:700;margin-bottom:4px'>"
        f"<span>Прогресс по уровням</span><span>{learned} / {total} слов</span></div>"
        f"{rows}"
        f"<div style='opacity:.6;font-size:12px'>Выучено — интервал повторения {MATURE_DAYS}+ дней у обоих направлений.</div>"
        "</div>"
    )


HARD_TAG = "et::hard"
HARD_LAPSES = 3          # forgotten this many times -> "hard word"
OPTIMIZE_AFTER = 1000    # reviews before a personal FSRS model makes sense


def hard_words(col, limit=12) -> list[tuple[str, int]]:
    nt = col.models.by_name(NOTETYPE)
    if not nt:
        return []
    rows = col.db.all(
        "select n.flds, max(c.lapses) l from notes n join cards c on c.nid = n.id "
        "where n.mid = ? and (n.tags like '%et::hard%' or n.tags like '%leech%') "
        "group by n.id order by l desc limit ?", nt["id"], limit)
    return [(f.split("\x1f", 1)[0], l) for f, l in rows]


def tag_hard_words(col) -> int:
    """Tag notes with any card forgotten HARD_LAPSES+ times (covers reviews done on the phone)."""
    nt = col.models.by_name(NOTETYPE)
    if not nt:
        return 0
    nids = col.db.list(
        "select distinct n.id from notes n join cards c on c.nid = n.id "
        "where n.mid = ? and c.lapses >= ? and n.tags not like ?", nt["id"], HARD_LAPSES, f"%{HARD_TAG}%")
    if nids:
        col.tags.bulk_add(nids, HARD_TAG)
    return len(nids)


def fsrs_hint(col, deck_id) -> str:
    conf = col.decks.config_dict_for_deck_id(deck_id)
    if conf.get("fsrsParams6") or conf.get("fsrsParams5"):
        return ""
    nt = col.models.by_name(NOTETYPE)
    revs = col.db.scalar(
        "select count() from revlog r join cards c on c.id = r.cid join notes n on n.id = c.nid where n.mid = ?",
        nt["id"]) if nt else 0
    if revs < OPTIMIZE_AFTER:
        return (f"<div style='opacity:.6;font-size:12px;margin-top:6px'>FSRS учится на твоих ответах: "
                f"{revs} из {OPTIMIZE_AFTER} повторений до личной настройки.</div>")
    return ("<div style='margin-top:10px;padding:8px 10px;border-radius:10px;background:rgba(245,166,35,.15)'>"
            "<b>Пора обучить FSRS под тебя:</b> Параметры колоды → FSRS → <b>Оптимизировать</b>. "
            "Повторяй раз в месяц.</div>")


def render_pacing(p) -> str:
    if not p or not p["order"]:
        return ""
    text = (f"Сложные слова (B2-C1): примерно каждое {p['every']}-е новое. "
            "Будет чаще по мере того, как выучишь базу" if not p["braked"] else
            f"Сложные слова (B2-C1) сейчас даются тяжело — новых меньше: примерно каждое {p['every']}-е. "
            "Вернётся, когда повторения пойдут легче")
    return f"<div style='opacity:.6;font-size:12px;margin-top:6px'>{text}.</div>"


def render_hard(words) -> str:
    if not words:
        return ""
    items = " · ".join(f"{html.escape(w)} <span style='opacity:.55'>×{l}</span>" for w, l in words)
    return ("<div style='margin-top:14px'><div style='font-weight:700;margin-bottom:4px'>Трудные слова</div>"
            f"<div style='line-height:1.7'>{items}</div>"
            "<div style='opacity:.6;font-size:12px'>На карточке помечены «трудное». "
            "Пришли список — придумаю ассоциации-подсказки (поле Hint).</div></div>")


def _on_overview(overview, content) -> None:
    try:
        deck = mw.col.decks.current()
        if not mw.col.find_cards(f'did:{deck["id"]} "note:{NOTETYPE}"'):
            return
        block = render(level_stats(mw.col))
        from . import practice
        extra = (render_pacing(pacing.plan(mw.col)) + practice.overview_button()
                 + render_hard(hard_words(mw.col)) + fsrs_hint(mw.col, deck["id"]))
        if extra:
            block = block[: -len("</div>")] + extra + "</div>"
        content.table += block
    except Exception as e:  # never break the overview screen
        print("English Trainer stats:", e)


def _tag_all() -> None:
    try:
        if mw.col:
            tag_hard_words(mw.col)
    except Exception as e:
        print("English Trainer hard words:", e)


def _pace() -> None:
    """Re-balance the order of new cards (only when not in the middle of a review)."""
    try:
        if mw.col and mw.state != "review":
            pacing.apply(mw.col)
    except Exception as e:
        print("English Trainer pacing:", e)


_pace_timer = QTimer(mw)
_pace_timer.timeout.connect(_pace)
_pace_timer.start(60 * 60 * 1000)


def _on_answer(reviewer, card, ease) -> None:
    try:
        if card.lapses >= HARD_LAPSES and card.note_type()["name"] == NOTETYPE:
            note = card.note()
            if not note.has_tag(HARD_TAG):
                mw.col.tags.bulk_add([note.id], HARD_TAG)
    except Exception as e:
        print("English Trainer hard words:", e)


gui_hooks.overview_will_render_content.append(_on_overview)
gui_hooks.profile_did_open.append(_tag_all)
gui_hooks.sync_did_finish.append(_tag_all)
gui_hooks.profile_did_open.append(_pace)
gui_hooks.sync_did_finish.append(_pace)
gui_hooks.reviewer_did_answer_card.append(_on_answer)
