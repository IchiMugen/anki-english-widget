"""The learner's level — asked once at the first start, changed any time in Tools.

    beginner — A1-A2 words first, B1-B2 after them, advanced (B2-C1) only once ~30% of the base is learned;
    medium   — the deck order, advanced words 15% → 50% as the base is learned;
    advanced — B1-B2 before A1-A2, advanced words 35% → 60%.

Only the ORDER of not-yet-seen cards changes (pacing.py, Anki's own "reposition new cards"); studied cards,
intervals and FSRS are never touched. Several people on one computer: each Anki profile has its own deck and
progress, the level is per add-on (choose it again when switching to a child's profile — Tools menu).
On a phone without the add-on the level is the file chosen at install (English_Trainer_beginner.apkg …).
"""
from __future__ import annotations

from aqt import gui_hooks, mw
from aqt.qt import QAction, QMessageBox, QTimer

NAMES = {"beginner": "начальный", "medium": "средний", "advanced": "продвинутый"}
PKG = __name__.split(".")[0]


def current() -> str:
    cfg = mw.addonManager.getConfig(PKG) or {}
    return cfg.get("level") or "medium"


def _save(level: str) -> None:
    cfg = mw.addonManager.getConfig(PKG) or {}
    cfg["level"] = level
    mw.addonManager.writeConfig(PKG, cfg)


def ask(first: bool = False) -> None:
    box = QMessageBox(mw)
    box.setWindowTitle("English Trainer — уровень")
    box.setText("С какого уровня начинать?" if first else f"Сейчас: {NAMES[current()]}. Выберите уровень:")
    box.setInformativeText(
        "Начальный — сначала самые простые слова (A1-A2), сложные появятся, когда освоите базу. Для детей и "
        "для тех, кто начинает с нуля.\n\n"
        "Средний — простые и средние вперемешку, сложные понемногу с самого начала.\n\n"
        "Продвинутый — простые слова в конце, больше слов уровня B2-C1.\n\n"
        "Порядок новых слов подстраивается и дальше — по тому, как идут повторения. Прогресс не меняется.")
    buttons = {}
    for key in ("beginner", "medium", "advanced"):
        buttons[box.addButton(NAMES[key].capitalize(), QMessageBox.ButtonRole.AcceptRole)] = key
    box.exec()
    chosen = buttons.get(box.clickedButton())
    if not chosen:
        return
    _save(chosen)
    try:
        from . import pacing
        pacing.apply(mw.col, chosen)
        mw.reset()
    except Exception as e:
        print("English Trainer level:", e)


def _on_open() -> None:
    cfg = mw.addonManager.getConfig(PKG) or {}
    if not cfg.get("level"):
        QTimer.singleShot(1500, lambda: ask(first=True))


act = QAction("English Trainer: уровень…", mw)
act.triggered.connect(lambda: ask())
mw.form.menuTools.addAction(act)
gui_hooks.profile_did_open.append(_on_open)
