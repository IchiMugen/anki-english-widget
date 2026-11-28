"""English Trainer for Anki — floating study widget, offline neural voice, progress by level.

* Voice: Piper (piper binary + a voice model, downloaded once by install.cmd / install.sh or
  Tools → «English Trainer: скачать голос» into user_files/). Takes over English {{tts}} tags
  on this computer; no Python needed. Windows, Linux, macOS. One Piper process per
  Anki session, requests in a priority queue (the word on screen first), audio cached as .wav.
* Widget, tray and lessons: trainer.py. Progress by level on the deck screen: stats.py.
* Wrong options for new notes added in Anki are picked automatically: autofill.py.
"""
from __future__ import annotations

import hashlib
import html
import itertools
import json
import os
import queue
import re
import subprocess
import threading
import time
from concurrent.futures import Future

from anki.sound import AVTag, TTSTag
from aqt import gui_hooks, mw
from aqt.operations import QueryOp
from aqt.qt import QTimer
from aqt.sound import OnDoneCallback, av_player
from aqt.tts import TTSProcessPlayer, TTSVoice

from . import mastery

ADDON_DIR = os.path.dirname(os.path.abspath(__file__))
USER = os.path.join(ADDON_DIR, "user_files")
CACHE = os.path.join(USER, "cache")
PIPER = os.path.join(USER, "piper", "piper.exe" if os.name == "nt" else "piper")
VOICES = os.path.join(USER, "voices")
NOTETYPE = "English Trainer"
NOW, NEXT, BACKGROUND = 0, 1, 5  # priorities


def _cfg() -> dict:
    return mw.addonManager.getConfig(__name__) or {}


def _model() -> str:
    return os.path.join(VOICES, _cfg().get("voice", "en_US-lessac-high") + ".onnx")


def _ready() -> bool:
    return bool(_cfg().get("voice_enabled", True)) and os.path.exists(PIPER) and os.path.exists(_model())


def _cache_path(text: str) -> str:
    key = f"{os.path.basename(_model())}|{_cfg().get('speed', 1.0)}|{text}"
    return os.path.join(CACHE, hashlib.sha1(key.encode("utf-8")).hexdigest()[:20] + ".wav")


def _is_en(tag) -> bool:
    return isinstance(tag, TTSTag) and tag.lang.lower().startswith("en")


def speakable(text: str) -> str:
    t = re.sub(r"<[^>]+>", " ", text or "")
    t = html.unescape(t).replace(" ", " ")
    parts = [p for p in re.split(r"[;\n|]", t) if p.strip()]
    if parts and all(len(p.split()) <= 5 for p in parts):
        t = parts[0]                       # a list of alternatives: say the first one
    t = re.sub(r"(^|\s)[—–-](?=\s)", " ", t)  # dialogue dashes in examples
    t = re.sub(r"\bsth\b", "something", t)
    t = re.sub(r"\b(sb|smb)\b", "somebody", t)
    return re.sub(r"\s+", " ", t).strip() or "."


class Engine:
    """Persistent piper.exe (--json-input) + priority queue (one worker thread)."""

    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None
        self._q: queue.PriorityQueue = queue.PriorityQueue()
        self._seq = itertools.count()
        self._waiting: dict[str, threading.Event] = {}
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None

    def request(self, text: str, prio: int) -> tuple[str, threading.Event]:
        path = _cache_path(text)
        with self._lock:
            ev = self._waiting.get(path)
            if ev is None:
                ev = threading.Event()
                if os.path.exists(path):
                    ev.set()
                    return path, ev
                self._waiting[path] = ev
            self._q.put((prio, next(self._seq), text, path))  # a better priority jumps ahead
            if not self._thread or not self._thread.is_alive():
                self._thread = threading.Thread(target=self._loop, name="et-piper", daemon=True)
                self._thread.start()
        return path, ev

    def _start(self) -> None:
        os.makedirs(CACHE, exist_ok=True)
        speed = float(_cfg().get("speed", 1.0)) or 1.0
        self._proc = subprocess.Popen(
            [PIPER, "--model", _model(), "--json-input", "--length_scale", f"{1.0 / speed:.3f}",
             "--sentence_silence", "0.1", "--quiet"],
            cwd=os.path.dirname(PIPER), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8", bufsize=1,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

    def _loop(self) -> None:
        while True:
            _prio, _n, text, path = self._q.get()
            if not os.path.exists(path):
                try:
                    if self._proc is None or self._proc.poll() is not None:
                        self._start()
                    tmp = path[:-4] + ".part.wav"
                    self._proc.stdin.write(json.dumps({"text": speakable(text), "output_file": tmp},
                                                      ensure_ascii=False) + "\n")
                    self._proc.stdin.flush()
                    reply = self._proc.stdout.readline().strip()  # piper prints the file it wrote
                    if reply and os.path.exists(tmp):
                        os.replace(tmp, path)
                    else:
                        print("English Trainer voice: piper stopped")
                        self.shutdown()
                except Exception as e:  # restart on the next job
                    print("English Trainer voice:", e)
                    self.shutdown()
            with self._lock:
                ev = self._waiting.pop(path, None)
            if ev:
                ev.set()

    def shutdown(self) -> None:
        p, self._proc = self._proc, None
        if p and p.poll() is None:
            try:
                p.kill()
            except Exception:
                pass


ENGINE = Engine()


class PiperPlayer(TTSProcessPlayer):
    _path: str | None = None

    def get_available_voices(self) -> list[TTSVoice]:
        return [TTSVoice(name="Piper", lang=lang) for lang in ("en_US", "en_GB")]

    def rank_for_tag(self, tag: AVTag) -> int | None:
        return 50 if _is_en(tag) and _ready() else None  # beats the Windows voices

    def _play(self, tag: AVTag) -> None:
        assert isinstance(tag, TTSTag)
        path, ev = ENGINE.request(tag.field_text, NOW)
        ev.wait(30)
        self._path = path

    def _on_done(self, ret: Future, cb: OnDoneCallback) -> None:
        if ret.exception() or not self._path or not os.path.exists(self._path) or self._terminate_flag:
            if ret.exception():
                print("English Trainer voice:", ret.exception())
            cb()
            return
        av_player.current_player = None
        av_player.insert_file(self._path)


# ---------------------------------------------------------------- auto-advance waits for the audio
# After a correct answer the card sends "et_auto_easeN" instead of "easeN": the answer is given
# only when Anki's audio queue (word, then example) has finished, so nothing is cut off.
# A click / key press still answers at once (the card sends plain "easeN" then).
AUTO_PREFIX = "et_auto_ease"
AUTO_MAX_WAIT = 20.0   # seconds: never wait forever (e.g. a broken voice)


def _audio_busy() -> bool:
    return av_player.current_player is not None or bool(getattr(av_player, "_enqueued", None))


def _auto_answer(card_id: int, ease: int, started: float, idle: int = 0) -> None:
    from aqt.reviewer import Reviewer  # noqa: F401  (only to be sure the reviewer exists)
    r = mw.reviewer
    if mw.state != "review" or not r.card or r.card.id != card_id:
        return                                  # the user already moved on
    busy = _audio_busy() and time.time() - started < AUTO_MAX_WAIT
    idle = 0 if busy else idle + 1
    if idle < 2:                                # idle twice in a row: no gap between two sounds
        QTimer.singleShot(150, lambda: _auto_answer(card_id, ease, started, idle))
        return
    r._answerCard(ease)


def say(text: str) -> None:
    """Any English sentence aloud, after whatever is playing (the word first, then the sentence)."""
    text = (text or "").strip()[:400]
    if text:
        av_player.append_tags([TTSTag(field_text=text, lang="en_US", voices=[], speed=1.0, other_args=[])])


def prefetch(text: str) -> None:
    if _ready() and text:
        ENGINE.request(text.strip()[:400], NEXT)


def _on_js_message(handled, message: str, context):
    """Card → add-on: et_say:<text>, et_prefetch:<text>, et_log:<json>, et_autonext:0|1, et_auto_easeN."""
    from aqt.reviewer import Reviewer
    if message.startswith("et_say:"):
        say(message[7:])
        return (True, None)
    if message.startswith("et_prefetch:"):
        prefetch(message[12:])
        return (True, None)
    if message.startswith("et_level:"):          # the level chosen on the first card (src/ui.js levelPicker)
        try:
            from . import level
            level.set_level(message[9:])
        except Exception as e:
            print("English Trainer level:", e)
        return (True, None)
    if message.startswith("et_autonext:"):       # the card's switch «листать самому» — kept in the config for good
        try:
            cfg = mw.addonManager.getConfig(__name__.split(".")[0]) or {}
            cfg["auto_next"] = message[12:] == "1"
            mw.addonManager.writeConfig(__name__.split(".")[0], cfg)
        except Exception as e:
            print("English Trainer auto-next:", e)
        return (True, None)
    if message.startswith("et_log:"):
        if isinstance(context, Reviewer) and context.card:
            try:
                mastery.log_add(mw.col, context.card.note().guid, json.loads(message[7:]), "s")
            except Exception as e:
                print("English Trainer log:", e)
        return (True, None)
    if not message.startswith(AUTO_PREFIX):
        return handled
    if isinstance(context, Reviewer) and context.card:
        try:
            ease = int(message[len(AUTO_PREFIX):])
            _auto_answer(context.card.id, ease, time.time())
        except Exception as e:
            print("English Trainer auto-advance:", e)
    return (True, None)


gui_hooks.webview_did_receive_js_message.append(_on_js_message)


# ---------------------------------------------------------------- card state for the "auto" mode
def _card_state(text: str, card, kind: str) -> str:
    """Give the card template the card's state (window.ET_CARD): the auto mode picks
    choice / typing from it. Read-only: nothing about scheduling changes."""
    try:
        if card.note_type()["name"] == NOTETYPE and not kind.startswith("clayout"):
            info = mastery.card_info(mw.col, card)
            try:   # cards left in this lesson (the template shows the lesson report on the last one)
                info["left"] = sum(mw.col.sched.counts())
            except Exception:
                pass
            try:   # the learner's level chosen in the add-on (the card uses it instead of its own memory)
                from . import level
                info["level"] = (mw.addonManager.getConfig(level.PKG) or {}).get("level") or ""
            except Exception:
                pass
            try:   # the switch «листать самому после верного ответа», remembered across restarts
                an = (mw.addonManager.getConfig(__name__.split(".")[0]) or {}).get("auto_next")
                if isinstance(an, bool):
                    info["autonext"] = an
            except Exception:
                pass
            state = json.dumps(info, ensure_ascii=False)
            return f"<script>window.ET_CARD={state};</script>" + text
    except Exception as e:
        print("English Trainer card state:", e)
    return text


gui_hooks.card_will_show.append(_card_state)


# ---------------------------------------------------------------- prefetch / pre-generation
def _prefetch_card(card) -> None:
    """Card on screen: get its audio ready while the question is being answered."""
    if not _ready():
        return
    try:
        for tag in card.question_av_tags() + card.answer_av_tags():
            if _is_en(tag):
                ENGINE.request(tag.field_text, NEXT)
    except Exception as e:
        print("English Trainer voice prefetch:", e)


def _collect_texts(col) -> list[str]:
    texts = []
    for nid in col.find_notes(f'"note:{NOTETYPE}"'):
        for card in col.get_note(nid).cards()[:1]:
            texts += [t.field_text for t in card.answer_av_tags() if _is_en(t)]
    return texts


def _pregenerate() -> None:
    if not _ready() or not mw.col:
        return

    def queue_missing(texts: list[str]) -> None:
        for t in dict.fromkeys(texts):
            if not os.path.exists(_cache_path(t)):
                ENGINE.request(t, BACKGROUND)

    QueryOp(parent=mw, op=_collect_texts, success=queue_missing).run_in_background()


_timer: QTimer | None = None


def _schedule_pregenerate(delay_ms: int = 3000) -> None:
    """Debounced: many edits/imports in a row -> one scan."""
    global _timer
    if _timer is None:
        _timer = QTimer(mw)
        _timer.setSingleShot(True)
        _timer.timeout.connect(_pregenerate)
    _timer.start(delay_ms)


def _on_op(changes, handler) -> None:
    if getattr(changes, "note_text", False):
        _schedule_pregenerate()


av_player.players.append(PiperPlayer(mw.taskman))
gui_hooks.profile_did_open.append(lambda: _schedule_pregenerate(1000))
gui_hooks.sync_did_finish.append(lambda: _schedule_pregenerate(1000))
gui_hooks.operation_did_execute.append(_on_op)
gui_hooks.reviewer_did_show_question.append(_prefetch_card)
gui_hooks.profile_will_close.append(ENGINE.shutdown)


from . import voice_setup  # noqa: E402,F401  (Tools → download the voice)
from . import autofill  # noqa: E402,F401  (wrong options for notes added in Anki)
from . import stats  # noqa: E402,F401  (progress by level on the deck screen)
from . import trainer  # noqa: E402,F401  (floating widget, tray, lessons)
from . import practice  # noqa: E402,F401  (Reinforcement: extra practice outside the schedule)
from . import deck_update  # noqa: E402,F401  (Tools → update the deck with the right import options)
from . import updater  # noqa: E402,F401  (one-click / automatic update from the GitHub release)
from . import level  # noqa: E402,F401  (the learner's level: asked at the first start, Tools menu)
from . import extra  # noqa: E402,F401  («Ещё занятие»: filtered sub-deck, filled once the lesson is done)
