"""Updates in one click — or none: the deck and the add-on follow the latest GitHub release.

* When Anki opens (and the setting "auto_update" is on, default) the add-on asks GitHub for the latest
  release of REPO. If it is newer than what is installed, it downloads English_Trainer.apkg and
  english_widget.ankiaddon, imports the deck with the right options (deck_update: words and templates
  updated, your progress kept) and installs the new add-on (active after the next Anki start).
* Tools → «English Trainer: проверить обновления» does the same on demand and says when all is current.
* Nothing is uploaded; one small request to api.github.com per Anki start.
"""
from __future__ import annotations

import json
import os
import tempfile
import threading
import urllib.request

from aqt import mw
from aqt.qt import QAction, QTimer
from aqt.utils import showInfo, tooltip

from . import deck_update

REPO = "IchiMugen/anki-english-widget"
API = f"https://api.github.com/repos/{REPO}/releases/latest"
HERE = os.path.dirname(os.path.abspath(__file__))
USER = os.path.join(HERE, "user_files")
STATE = os.path.join(USER, "installed_release.json")


def _ver(tag: str) -> tuple:
    out = []
    for p in tag.lstrip("vV").split("."):
        n = "".join(ch for ch in p if ch.isdigit())
        out.append(int(n) if n else 0)
    return tuple(out)


def bundled() -> str:
    try:
        with open(os.path.join(HERE, "VERSION"), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "0"


def installed() -> str:
    """The release whose deck is in the collection (written after each update; a fresh install = the
    release the add-on came from)."""
    try:
        with open(STATE, encoding="utf-8") as f:
            return json.load(f).get("deck") or bundled()
    except (OSError, ValueError):
        return bundled()


def _save(tag: str) -> None:
    os.makedirs(USER, exist_ok=True)
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump({"deck": tag}, f)


def _get(url: str, dest: str | None = None):
    req = urllib.request.Request(url, headers={"User-Agent": "english-trainer-anki-addon",
                                               "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    if dest:
        with open(dest, "wb") as f:
            f.write(data)
        return dest
    return json.loads(data.decode("utf-8"))


def check(manual: bool = False) -> None:
    def work():
        try:
            rel = _get(API)
            tag = rel.get("tag_name", "")
            if not tag or _ver(tag) <= _ver(installed()):
                mw.taskman.run_on_main(lambda: manual and showInfo(
                    f"English Trainer: у вас последняя версия ({installed()})."))
                return
            assets = {a["name"]: a["browser_download_url"] for a in rel.get("assets", [])}
            tmp = tempfile.mkdtemp(prefix="et-update-")
            apkg = assets.get("English_Trainer.apkg") and _get(assets["English_Trainer.apkg"],
                                                               os.path.join(tmp, "English_Trainer.apkg"))
            addon = None
            if _ver(tag) > _ver(bundled()) and assets.get("english_widget.ankiaddon"):
                addon = _get(assets["english_widget.ankiaddon"], os.path.join(tmp, "english_widget.ankiaddon"))
            mw.taskman.run_on_main(lambda: _apply(tag, apkg, addon))
        except Exception as e:  # offline, GitHub limits… — never break Anki
            if manual:
                mw.taskman.run_on_main(lambda: showInfo(f"English Trainer: не удалось проверить обновления ({e})."))

    threading.Thread(target=work, daemon=True).start()


def _apply(tag: str, apkg: str | None, addon: str | None) -> None:
    note = ""
    if addon:
        from aqt.addons import InstallOk
        res = mw.addonManager.install(addon)
        note = " Новая версия дополнения заработает после перезапуска Anki." if isinstance(res, InstallOk) else ""
    if apkg:
        def done(log) -> None:
            _save(tag)
            tooltip(f"English Trainer обновлён до {tag}: новых слов {len(log.new)}, "
                    f"обновлено {len(log.updated)}. Прогресс сохранён.{note}", period=8000)
            mw.reset()
        deck_update.update_deck(apkg, on_done=done)
    elif note:
        _save(tag)
        tooltip(f"English Trainer {tag}:{note}", period=8000)


def _on_open() -> None:
    cfg = mw.addonManager.getConfig(__name__.split(".")[0]) or {}
    if cfg.get("auto_update", True):
        QTimer.singleShot(4000, lambda: check(manual=False))


act = QAction("English Trainer: проверить обновления", mw)
act.triggered.connect(lambda: check(manual=True))
mw.form.menuTools.addAction(act)

from aqt import gui_hooks  # noqa: E402

gui_hooks.profile_did_open.append(_on_open)
