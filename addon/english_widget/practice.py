"""Reinforcement («Закрепление»): extra practice on today's material, any time, outside the schedule.

* Looks at today's answers (Anki's review log + the exercise log): mistakes, slow right answers,
  typos, meaning errors, a word that was right in one sentence and wrong in another.
* Builds a session where each problem gets a DIFFERENT way of checking it:
      not sure what it means         → "what does it mean here" in a new sentence   (EN → RU card)
      knows it, can't bring it up    → gap with a Russian situation / typing        (RU → EN card)
      typo / wrong form              → typing in other sentences (other forms)       (context card)
      one sentence only              → a new context                                 (context card)
      confused with a similar word   → contrast with similar expressions             (context card)
  Wrong → the word comes back later with another exercise; right and quick → done.
* Nothing is sent to Anki's scheduler: no grades, no interval changes, no new cards.
  Results go to the exercise log marked "practice" — a mistake there marks the skill weak,
  a right answer never inflates it (see mastery.py).
"""
from __future__ import annotations

import json
import random
import time

from aqt import gui_hooks, mw
from aqt.qt import QAction, QDialog, QHBoxLayout, QLabel, QPushButton, Qt, QVBoxLayout
from aqt.utils import tooltip
from aqt.webview import AnkiWebView

from . import mastery

NOTETYPE = "English Trainer"
ORD = {"ru-en": 0, "en-ru": 1, "ctx": 2}
MAX_ATTEMPTS = 3
EXTENDED = 8          # no problems today: this many words get new contexts

PROBLEM_TEXT = {
    "retrieval": ("вспомнить слово", "situation", "ru-en"),
    "meaning": ("понять значение", "meaning", "en-ru"),
    "form": ("форма / написание", "type", "ctx"),
    "context": ("новый контекст", "type", "ctx"),
    "confusion": ("похожие слова", "contrast", "ctx"),
    "speed": ("вспоминать быстрее", "type", "ru-en"),
}


# ---------------------------------------------------------------- what to practise
def today_start_ms(col) -> int:
    return (col.sched.day_cutoff - 86400) * 1000


def plan(col) -> tuple[list[dict], dict, bool]:
    """Problems of today -> [{nid, cid, problem, kind}], counts by problem, extended?"""
    nt = col.models.by_name(NOTETYPE)
    if not nt:
        return [], {}, False
    since = today_start_ms(col)
    rows = col.db.all(
        "select c.nid, c.ord, r.ease, r.time, r.id from revlog r join cards c on c.id = r.cid "
        "join notes n on n.id = c.nid where n.mid = ? and r.id >= ? and r.ease > 0 order by r.id", nt["id"], since)
    problems: dict[int, set] = {}
    answered: set[int] = set()
    for nid, ord_, ease, ms, _ in rows:
        answered.add(nid)
        p = problems.setdefault(nid, set())
        if ease == 1:
            p.add({0: "retrieval", 1: "meaning", 2: "context"}.get(ord_, "retrieval"))
        elif ease == 2:
            p.add("form")
    # details from the exercise log (desktop): typos, kinds, example-level contradictions
    day_s = since // 1000
    for nid in list(answered):
        guid = col.db.scalar("select guid from notes where id = ?", nid)
        log = [r for r in mastery.log_get(col, guid) if r[0] >= day_s]
        p = problems.setdefault(nid, set())
        by_x: dict[str, set] = {}
        for ts, d, k, x, ok, ms, src, *rest in log:
            near = rest[0] if rest else 0
            if near:
                p.add("form")
            if ok == 1 and src == "s" and mastery.is_slow(k, ms):
                p.add("speed")           # right, but slowly (time measured by the card itself)
            if ok == 0 and k == "meaning":
                p.add("meaning")
            if ok == 0 and k == "contrast":
                p.add("confusion")
            if x:
                by_x.setdefault(x, set()).add(ok)
        if any(0 in v for v in by_x.values()) and any(1 in v for v in by_x.values()):
            p.add("context")
    items = []
    for nid, ps in problems.items():
        for problem in sorted(ps):
            _, kind, direction = PROBLEM_TEXT[problem]
            cid = col.db.scalar("select id from cards where nid = ? and ord = ?", nid, ORD[direction])
            if cid is None:   # no context card (word without an example): use RU → EN
                cid = col.db.scalar("select id from cards where nid = ? and ord = 0", nid)
                kind = "situation"
            if cid:
                items.append({"nid": nid, "cid": cid, "problem": problem, "kind": kind, "tries": 0})
    counts: dict[str, int] = {}
    for it in items:
        counts[it["problem"]] = counts.get(it["problem"], 0) + 1
    extended = False
    if not items and answered:
        extended = True
        for nid in random.sample(sorted(answered), min(EXTENDED, len(answered))):
            cid = col.db.scalar("select id from cards where nid = ? and ord = 2", nid)
            if cid:
                items.append({"nid": nid, "cid": cid, "problem": "context", "kind": "type", "tries": 0})
        counts = {"context": len(items)}
    random.shuffle(items)
    # the same word not twice in a row
    out, last = [], None
    pool = items[:]
    while pool:
        pick = next((it for it in pool if it["nid"] != last), pool[0])
        pool.remove(pick)
        out.append(pick)
        last = pick["nid"]
    return out, counts, extended


def summary_text(counts: dict, extended: bool) -> str:
    if not counts:
        return "Сегодня ещё нечего закреплять — сначала пройди занятие."
    if extended:
        return f"Ошибок сегодня не было. Закрепим {counts['context']} слов в новых предложениях."
    parts = [f"{n} — {PROBLEM_TEXT[p][0]}" for p, n in sorted(counts.items(), key=lambda kv: -kv[1])]
    return "Отработаем: " + ", ".join(parts) + "."


# ---------------------------------------------------------------- the session window
PAGE = """<style>%(css)s</style>
<div id="qa"></div>
<script>
document.body.classList.add('card');
window.etShow = function (html) {
  var qa = document.getElementById('qa');
  qa.innerHTML = html;
  [].slice.call(qa.querySelectorAll('script')).forEach(function (s) {
    var n = document.createElement('script'); n.text = s.text; s.parentNode.replaceChild(n, s);
  });
  window.scrollTo(0, 0);
};
</script>"""

NEXT_KIND = {"situation": "type", "type": "situation", "meaning": "choice", "choice": "meaning", "contrast": "type"}


class Session(QDialog):
    def __init__(self, items: list[dict], counts: dict, extended: bool) -> None:
        super().__init__(mw)
        self.setWindowTitle("Закрепление — English Trainer")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.items, self.counts, self.extended = items, counts, extended
        self.total = len(items)
        self.done_ok = 0
        self.current: dict | None = None
        self.card = None
        self.started = time.time()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        self.info = QLabel(summary_text(counts, extended))
        self.info.setWordWrap(True)
        lay.addWidget(self.info)
        self.web = AnkiWebView(parent=self)
        self.web.set_bridge_command(self.on_cmd, self)
        lay.addWidget(self.web, 1)
        row = QHBoxLayout()
        self.progress = QLabel("")
        row.addWidget(self.progress, 1)
        stop = QPushButton("Закончить")
        stop.clicked.connect(self.close)
        row.addWidget(stop)
        lay.addLayout(row)
        self.resize(430, 700)
        css = mw.col.models.by_name(NOTETYPE)["css"]
        self.web.stdHtml(PAGE % {"css": css}, context=self)
        self.web.loadFinished.connect(lambda _ok: self.next_item())

    # -- flow
    def next_item(self) -> None:
        if not self.items:
            self.finish()
            return
        self.current = self.items.pop(0)
        self.card = mw.col.get_card(self.current["cid"])
        left = len(self.items) + 1
        self.progress.setText(f"Осталось: {left}  ·  верно с первого раза: {self.done_ok}")
        self.show_side("q")

    def show_side(self, side: str) -> None:
        c = self.card
        text = c.question(reload=side == "q") if side == "q" else c.answer()
        text = mw.prepare_card_text_for_display(text)
        info = mastery.card_info(mw.col, c)
        prefix = ("<script>window.ET_CARD=%s;window.ET_PRACTICE=%s;</script>"
                  % (json.dumps(info, ensure_ascii=False),
                     json.dumps({"kind": self.current["kind"], "problem": self.current["problem"]})))
        self.web.eval("etShow(%s);" % json.dumps(prefix + text))
        tags = c.question_av_tags() if side == "q" else c.answer_av_tags()
        from aqt.sound import av_player
        av_player.play_tags(tags)

    def on_cmd(self, cmd: str):
        from . import say, prefetch
        if cmd == "ans":
            self.show_side("a")
        elif cmd.startswith("et_practice:"):
            self.record(json.loads(cmd[12:]))
        elif cmd.startswith("et_say:"):
            say(cmd[7:])
        elif cmd.startswith("et_prefetch:"):
            prefetch(cmd[12:])
        elif cmd.startswith("play:"):
            from aqt.sound import av_player
            try:
                _, side, idx = cmd.split(":")
                tags = self.card.question_av_tags() if side == "q" else self.card.answer_av_tags()
                av_player.play_tags([tags[int(idx)]])
            except Exception:
                pass
        return None

    def record(self, entry: dict) -> None:
        it = self.current
        if not it:
            return
        it["tries"] += 1
        try:
            mastery.log_add(mw.col, self.card.note().guid, entry, "p")
        except Exception as e:
            print("English Trainer practice log:", e)
        ok = entry.get("s") == "correct" or (entry.get("s") == "self" and int(entry.get("e", 0)) >= 3)
        slow = ok and mastery.is_slow(entry.get("k", ""), int(entry.get("ms") or 0))
        if ok and it["tries"] == 1 and not slow:
            self.done_ok += 1
        elif it["tries"] < MAX_ATTEMPTS:
            # comes back later, checked another way (and in another sentence — the card picks it)
            again = dict(it, kind=NEXT_KIND.get(it["kind"], it["kind"]))
            self.items.insert(min(len(self.items), 3), again)
        self.current = None
        from aqt.qt import QTimer
        QTimer.singleShot(250, self.next_item)

    def finish(self) -> None:
        mins = max(1, round((time.time() - self.started) / 60))
        self.progress.setText("")
        self.info.setText(f"Готово: {self.total} заданий за ~{mins} мин, с первого раза — {self.done_ok}. "
                          "Расписание Anki не менялось.")
        self.web.eval("etShow('<div class=\"et\" style=\"padding:40px 16px;text-align:center;font-size:17px\">"
                      "Закрепление окончено. Можно закрыть окно.</div>');")
        _save_session(self.total, self.done_ok, self.counts)


def _save_session(total: int, ok: int, counts: dict) -> None:
    try:
        hist = list(mw.col.get_config("etPracticeSessions", []) or [])
        hist.append({"t": int(time.time()), "n": total, "ok": ok, "p": counts})
        mw.col.set_config("etPracticeSessions", hist[-30:])
    except Exception as e:
        print("English Trainer practice:", e)


_session: Session | None = None


def start() -> None:
    global _session
    if not mw.col:
        return
    items, counts, extended = plan(mw.col)
    if not items:
        tooltip(summary_text(counts, extended), parent=mw)
        return
    if _session is not None:
        try:
            _session.close()
        except Exception:
            pass
    _session = Session(items, counts, extended)
    _session.show()
    _session.raise_()
    _session.activateWindow()


def overview_button() -> str:
    """A button for the deck screen (shown under the progress)."""
    return ("<div style='margin-top:12px'><button onclick=\"pycmd('et_practice_start')\" "
            "style='padding:7px 14px;border-radius:10px;cursor:pointer'>Закрепить сегодняшнее</button>"
            "<span style='opacity:.6;font-size:12px;margin-left:8px'>не влияет на расписание</span></div>")


def _on_js(handled, message: str, context):
    if message == "et_practice_start":
        start()
        return (True, None)
    return handled


gui_hooks.webview_did_receive_js_message.append(_on_js)


def _add_menu() -> None:
    act = QAction("Закрепить сегодняшнее", mw)
    act.triggered.connect(start)
    mw.form.menuTools.addAction(act)


_add_menu()
