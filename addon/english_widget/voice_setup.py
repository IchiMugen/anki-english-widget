"""Download the offline voice (Piper + one voice model) from inside Anki.

Tools → «English Trainer: скачать голос». install.cmd / install.sh do the same thing for you;
this menu item is for the «add-on only» way of installing. Windows, Linux and macOS.
"""
from __future__ import annotations

import os
import platform
import shutil
import stat
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

from aqt import mw
from aqt.operations import QueryOp
from aqt.qt import QAction
from aqt.utils import askUser, showInfo, showWarning, tooltip

PIPER_RELEASE = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/"
VOICE_BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/"
VOICE_PATHS = {
    "en_US-lessac-high": "en_US/lessac/high/",
    "en_US-ryan-high": "en_US/ryan/high/",
    "en_GB-cori-high": "en_GB/cori/high/",
}
ADDON = __name__.split(".")[0]
USER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_files")
PIPER_DIR = os.path.join(USER, "piper")
VOICES = os.path.join(USER, "voices")


def piper_exe() -> str:
    return os.path.join(PIPER_DIR, "piper.exe" if sys.platform == "win32" else "piper")


def piper_archive() -> str:
    m = platform.machine().lower()
    if sys.platform == "win32":
        return "piper_windows_amd64.zip"
    if sys.platform == "darwin":
        return "piper_macos_aarch64.tar.gz" if m in ("arm64", "aarch64") else "piper_macos_x64.tar.gz"
    return {"aarch64": "piper_linux_aarch64.tar.gz", "arm64": "piper_linux_aarch64.tar.gz",
            "armv7l": "piper_linux_armv7l.tar.gz"}.get(m, "piper_linux_x86_64.tar.gz")


def _download(url: str, dest: str) -> None:
    tmp = dest + ".part"
    req = urllib.request.Request(url, headers={"User-Agent": "anki-english-widget"})
    with urllib.request.urlopen(req, timeout=60) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, 1 << 20)
    os.replace(tmp, dest)


def install_voice(voice: str) -> str:
    """Runs in a background thread. Returns a short report."""
    done = []
    if not os.path.exists(piper_exe()):
        with tempfile.TemporaryDirectory() as tmp:
            arc = os.path.join(tmp, piper_archive())
            _download(PIPER_RELEASE + piper_archive(), arc)
            if arc.endswith(".zip"):
                with zipfile.ZipFile(arc) as z:
                    z.extractall(tmp)
            else:
                with tarfile.open(arc) as t:
                    t.extractall(tmp)
            if os.path.exists(PIPER_DIR):
                shutil.rmtree(PIPER_DIR)
            shutil.move(os.path.join(tmp, "piper"), PIPER_DIR)
        exe = piper_exe()
        os.chmod(exe, os.stat(exe).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        done.append("Piper")
    os.makedirs(VOICES, exist_ok=True)
    for ext in (".onnx.json", ".onnx"):
        dest = os.path.join(VOICES, voice + ext)
        if not os.path.exists(dest):
            _download(VOICE_BASE + VOICE_PATHS[voice] + voice + ext, dest)
    done.append(voice)
    return ", ".join(done)


def _on_menu() -> None:
    cfg = mw.addonManager.getConfig(ADDON) or {}
    voice = cfg.get("voice", "en_US-lessac-high")
    if voice not in VOICE_PATHS:
        showWarning(f"Неизвестный голос «{voice}». Доступны: " + ", ".join(VOICE_PATHS))
        return
    have = os.path.exists(piper_exe()) and os.path.exists(os.path.join(VOICES, voice + ".onnx"))
    if have and not askUser("Голос уже скачан. Скачать заново?"):
        return
    if have:
        shutil.rmtree(PIPER_DIR, ignore_errors=True)
        for ext in (".onnx", ".onnx.json"):
            try:
                os.remove(os.path.join(VOICES, voice + ext))
            except OSError:
                pass
    if not askUser(f"Скачать офлайн-голос {voice} (около 135 МБ)? Нужно один раз, дальше работает без интернета."):
        return
    tooltip("Скачиваю голос… Можно заниматься, это идёт в фоне.", period=6000)
    QueryOp(parent=mw, op=lambda col: install_voice(voice),
            success=lambda r: showInfo(f"Голос готов ({r}). Английский теперь звучит офлайн.")
            ).failure(lambda e: showWarning(f"Не получилось скачать голос: {e}")
                      ).without_collection().run_in_background()


act = QAction("English Trainer: скачать голос", mw)
act.triggered.connect(_on_menu)
mw.form.menuTools.addAction(act)
