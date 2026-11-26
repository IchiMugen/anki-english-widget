"""Persistent trainer: Anki is a floating widget by default and lives in the tray.

* View: "widget" (default) — the main window as a compact, frameless, always-on-top card of a
  fixed size; or "window" — normal Anki. Switch: tray menu, the ⧉ button on the widget,
  Tools → «Показать как виджет». The choice is remembered (add-on config "view").
* Closing hides Anki to the tray (real exit: tray menu «Выход»).
* Every minute: if English Trainer cards are due (Anki's own scheduler), you are at the
  computer and nothing runs fullscreen, a lesson starts in the widget (it pops up from the
  tray without taking focus; it doesn't interrupt the normal Anki window).
* During a lesson the window can't be closed, minimised or sent to the tray; leaving the
  review while cards are due (Esc…) goes straight back. A pop-up lesson hides itself when done.
* The widget never changes size: a taller card is scaled down to fit (no scrolling).

Grading, intervals and sync are Anki's own; this module only shows/hides the window.
"""
from __future__ import annotations

import ctypes
import html
import os
import sys
import time

from aqt import gui_hooks, mw
from aqt.qt import (QAction, QColor, QEvent, QHBoxLayout, QLabel, QMenu, QObject, QPainter,
                    QPainterPath, QPen, QRectF, QRegion, QSystemTrayIcon, Qt, QTimer, QWidget)

DECK = "English Trainer"
USER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_files")
TRAY_FLAG = os.path.join(USER, ".start_tray")   # written by the Windows autostart entry
LOG = os.path.join(USER, "trainer.log")
if sys.platform == "win32":
    AUTOSTART = os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Windows", "Start Menu",
                             "Programs", "Startup", "English Trainer (Anki).vbs")
elif sys.platform == "darwin":
    AUTOSTART = os.path.expanduser("~/Library/LaunchAgents/net.englishtrainer.anki.plist")
else:
    AUTOSTART = os.path.expanduser("~/.config/autostart/english-trainer-anki.desktop")


def _log(msg: str) -> None:
    try:
        if os.path.exists(LOG) and os.path.getsize(LOG) > 300_000:
            os.remove(LOG)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + msg + chr(10))
    except OSError:
        pass


def _safe(fn):
    """Hook/timer entry points never break Anki; errors go to user_files/trainer.log."""
    import functools
    import traceback

    @functools.wraps(fn)
    def wrapper(*a, **kw):
        try:
            return fn(*a, **kw)
        except Exception:
            _log(f"{fn.__name__}: " + traceback.format_exc())
            return a[1] if fn.__name__ == "on_js" and len(a) > 1 else None
    return wrapper

CHECK_MS = 60_000
IDLE_LIMIT = 60            # s without input = away from the computer
GAP_AFTER_LESSON = 10 * 60 # let a few learning cards gather before the next pop-up
SYNC_EVERY = 15 * 60       # background collection sync while in the tray
WIDGET_W, WIDGET_H = 380, 580   # card area; the header strip comes on top
RADIUS = 12
MIN_W = 300            # smaller is unreadable
HEADER_H = 30

# Compact layout for the widget only (scoped by html.et-w; phone and normal Anki unaffected)
WIDGET_CSS = """
html.et-w, html.et-w body { overflow: hidden !important; }
html.et-w ::-webkit-scrollbar { width: 5px; }
html.et-w ::-webkit-scrollbar-thumb { background: rgba(128,128,128,.35); border-radius: 3px; }
html.et-w ::-webkit-scrollbar-track { background: transparent; }
html.et-w body, html.et-w body.card { margin: 0 !important; padding: 0 !important; }
html.et-w #qa { margin: 0 !important; padding: 0 !important; }
html.et-w .et button { margin: 0 !important; }
html.et-w body:not(.isMac)::-webkit-scrollbar { width: 0 !important; }
html.et-w .et { padding: 6px 12px 14px !important; max-width: none !important; }
html.et-w .et-seg { margin-bottom: 8px !important; padding: 2px !important; border-radius: 11px !important; }
html.et-w .et-seg button { font-size: 12px !important; padding: 6px 4px !important; border-radius: 9px !important; }
html.et-w .et-seg button svg { width: 13px !important; height: 13px !important; }
html.et-w .et-glass { border-radius: 16px !important; }
html.et-w .et-prompt { padding: 12px 14px !important; margin-bottom: 8px !important; }
html.et-w .et-label { font-size: 11.5px !important; margin-bottom: 4px !important; }
html.et-w .et-chip { font-size: 10.5px !important; }
html.et-w .et-word { font-size: 22px !important; line-height: 1.22 !important; letter-spacing: -.01em !important; }
html.et-w .et-qline { font-size: 13px !important; margin-bottom: 4px !important; }
html.et-w .et-hint, html.et-w .et-mask { font-size: 14px !important; }
html.et-w .et-options { gap: 6px !important; }
html.et-w .et-opt { min-height: 42px !important; padding: 8px 12px !important; gap: 10px !important; border-radius: 13px !important; font-size: 15px !important; }
html.et-w .et-opt-text { font-size: 15px !important; font-weight: 600 !important; line-height: 1.25 !important; }
html.et-w .et-opt-key { width: 24px !important; height: 24px !important; border-radius: 8px !important; font-size: 11.5px !important; }
html.et-w .et-type, html.et-w .et-recall { padding: 12px !important; }
html.et-w .et-input { font-size: 17px !important; padding: 10px 12px !important; }
html.et-w .et-row { margin-top: 8px !important; gap: 8px !important; }
html.et-w .et-btn { font-size: 14px !important; padding: 9px 12px !important; }
html.et-w .et-btn-block { margin-top: 8px !important; }
html.et-w .et-kbd { display: none !important; }
html.et-w .et-section { padding: 10px 12px !important; margin-bottom: 8px !important; }
html.et-w .et-section h4 { font-size: 11px !important; margin-bottom: 4px !important; }
html.et-w .et-example { font-size: 15px !important; }
html.et-w .et-expl, html.et-w .et-fb-note { font-size: 13px !important; }
html.et-w .et-fb { margin-top: 8px !important; }
html.et-w .et-fb-line { font-size: 15px !important; }
html.et-w .et-res { padding: 10px 12px !important; }
html.et-w .et-audio-slot .replay-button svg { width: 34px !important; height: 34px !important; }
html.et-w .et.et-static .et-options { display: none !important; }  /* answer side: the result block says it all */
"""


# ---------- Windows helpers (no-ops elsewhere) ----------
def _idle_seconds() -> float:
    if sys.platform != "win32":
        return 0

    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint32)]

    li = LASTINPUTINFO(ctypes.sizeof(LASTINPUTINFO), 0)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(li)):
        return 0
    return (ctypes.windll.kernel32.GetTickCount() - li.dwTime) / 1000


def _fullscreen_app() -> bool:
    if sys.platform != "win32":
        return False
    from ctypes import wintypes
    u = ctypes.windll.user32
    hwnd = u.GetForegroundWindow()
    if not hwnd:
        return True  # locked screen
    cls = ctypes.create_unicode_buffer(64)
    u.GetClassNameW(hwnd, cls, 64)
    if cls.value in ("Progman", "WorkerW", "Shell_TrayWnd"):
        return False

    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT),
                    ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]

    r = wintypes.RECT()
    u.GetWindowRect(hwnd, ctypes.byref(r))
    mi = MONITORINFO(ctypes.sizeof(MONITORINFO))
    u.GetMonitorInfoW(u.MonitorFromWindow(hwnd, 2), ctypes.byref(mi))
    m = mi.rcMonitor
    return r.left <= m.left and r.top <= m.top and r.right >= m.right and r.bottom >= m.bottom


def _night() -> bool:
    try:
        from aqt.theme import theme_manager
        return theme_manager.night_mode
    except Exception:
        return True


def _round_corners(win) -> bool:
    """Windows 11 system-rounded corners (antialiased). False where unsupported (Windows 10)."""
    if sys.platform != "win32" or sys.getwindowsversion().build < 22000:
        return False
    try:
        pref = ctypes.c_int(2)  # DWMWCP_ROUND
        return ctypes.windll.dwmapi.DwmSetWindowAttribute(int(win.winId()), 33, ctypes.byref(pref), 4) == 0
    except Exception:
        return False


def _foreground() -> int:
    return ctypes.windll.user32.GetForegroundWindow() if sys.platform == "win32" else 0


def _give_focus_back(prev: int) -> None:
    """Keep typing in the window you were working in when the widget pops up."""
    if sys.platform != "win32" or not prev:
        return
    u = ctypes.windll.user32
    if u.GetForegroundWindow() == int(mw.winId()) and prev != int(mw.winId()) and u.IsWindow(prev):
        u.SetForegroundWindow(prev)


def _anki_shortcut() -> str | None:
    for base in (os.environ.get("ProgramData", r"C:\ProgramData"), os.environ.get("APPDATA", "")):
        menu = os.path.join(base, "Microsoft", "Windows", "Start Menu", "Programs")
        for root, _dirs, files in os.walk(menu):
            if "Anki.lnk" in files:
                return os.path.join(root, "Anki.lnk")
    return None


def _set_autostart(on: bool) -> None:
    """Start Anki hidden in the tray when you log in (tray menu toggle). Windows, Linux, macOS."""
    try:
        if not on:
            if os.path.exists(AUTOSTART):
                os.remove(AUTOSTART)
            return
        os.makedirs(USER, exist_ok=True)
        os.makedirs(os.path.dirname(AUTOSTART), exist_ok=True)
        if sys.platform == "win32":
            lnk = _anki_shortcut()
            if not lnk:
                from aqt.utils import showWarning
                showWarning("Не нашёл ярлык Anki в меню «Пуск» — автозапуск не настроен.")
                return
            text = ('Set fs = CreateObject("Scripting.FileSystemObject")\r\n'
                    f'fs.CreateTextFile("{TRAY_FLAG}", True).Write "1"\r\n'
                    f'CreateObject("WScript.Shell").Run """{lnk}"""\r\n')
            with open(AUTOSTART, "w", encoding="utf-16", newline="") as f:
                f.write(text)
            return
        flag = TRAY_FLAG.replace("'", "'\\''")
        if sys.platform == "darwin":
            cmd = f"touch '{flag}'; open -a Anki"
            text = ('<?xml version="1.0" encoding="UTF-8"?>\n'
                    '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
                    '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
                    '<plist version="1.0"><dict>\n'
                    '<key>Label</key><string>net.englishtrainer.anki</string>\n'
                    '<key>ProgramArguments</key><array><string>/bin/sh</string><string>-c</string>'
                    f'<string>{html.escape(cmd)}</string></array>\n'
                    '<key>RunAtLoad</key><true/>\n</dict></plist>\n')
        else:
            text = ("[Desktop Entry]\nType=Application\nName=English Trainer (Anki)\n"
                    f"Exec=sh -c \"touch '{flag}'; anki\"\nX-GNOME-Autostart-enabled=true\n")
        with open(AUTOSTART, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        _log(f"autostart: {e}")


def _set_bars_visible(on: bool) -> None:
    for bar in (mw.toolbarWeb, mw.bottomWeb):
        QWidget.setVisible(bar, on)  # plain Qt, bypassing Anki's animated hide()/show()
    if on:
        mw.toolbarWeb.show()
        mw.bottomWeb.show()


def _apply_mask(win) -> None:
    path = QPainterPath()
    path.addRoundedRect(QRectF(win.rect()), RADIUS, RADIUS)
    win.setMask(QRegion(path.toFillPolygon().toPolygon()))


class _ResizeGrip(QWidget):
    """A corner of the widget: drag it to make the whole widget bigger or smaller.
    Proportions are kept and the opposite corner stays where it is."""
    SIZE = 16
    CURSORS = {"tl": Qt.CursorShape.SizeFDiagCursor, "br": Qt.CursorShape.SizeFDiagCursor,
               "tr": Qt.CursorShape.SizeBDiagCursor, "bl": Qt.CursorShape.SizeBDiagCursor}

    def __init__(self, trainer, corner: str) -> None:
        super().__init__(mw)
        self.trainer, self.corner = trainer, corner
        self.setFixedSize(self.SIZE, self.SIZE)
        self.setCursor(self.CURSORS[corner])
        self.setToolTip("Потяни, чтобы изменить размер")
        self.start = None

    def paintEvent(self, event) -> None:
        if self.corner != "br":
            return  # the other corners work the same, just without the visible hatch
        pen = QPen(QColor(150, 152, 165, 150))
        pen.setWidthF(1.3)
        qp = QPainter(self)
        qp.setRenderHint(QPainter.RenderHint.Antialiasing)
        qp.setPen(pen)
        s = self.SIZE
        for k in (4, 8, 12):
            qp.drawLine(s - 3, s - 3 - k, s - 3 - k, s - 3)
        qp.end()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.start = (event.globalPosition().toPoint(), mw.geometry())

    def mouseMoveEvent(self, event) -> None:
        if not self.start:
            return
        origin, g0 = self.start
        d = event.globalPosition().toPoint() - origin
        sx = -1 if self.corner in ("tl", "bl") else 1   # pulling outwards = bigger
        sy = -1 if self.corner in ("tl", "tr") else 1
        ratio = g0.height() / g0.width()
        by_w, by_h = sx * d.x(), sy * d.y() / ratio
        dw = by_w if abs(by_w) >= abs(by_h) else by_h      # whichever way you pull more
        self.trainer.resize_from(self.corner, g0, (g0.width() + dw) / WIDGET_W)

    def mouseReleaseEvent(self, event) -> None:
        if self.start:
            self.start = None
            self.trainer.save_scale()


class _DragStrip(QWidget):
    """Top strip of the frameless widget: drag it to move the window."""

    def mousePressEvent(self, event) -> None:
        handle = self.window().windowHandle()
        if event.button() == Qt.MouseButton.LeftButton and handle:
            handle.startSystemMove()


FIT_JS = r'''<script>
document.documentElement.classList.add('et-w');
(function () {
  // The widget keeps a fixed size; a card taller than the window is scaled down to fit,
  // so nothing ever scrolls and the window never jumps.
  var t = null;
  function fit() {
    var et = document.querySelector('.et');
    if (!et) return;
    et.style.transform = ''; et.style.width = '';
    var h = et.offsetHeight, avail = window.innerHeight;
    if (h > avail + 1) {
      var s = avail / h;
      et.style.transformOrigin = 'top left';
      et.style.width = (100 / s) + '%';
      s = avail / et.offsetHeight;  // wider layout is a bit shorter — measure again
      et.style.width = (100 / s) + '%';
      et.style.transform = 'scale(' + s + ')';
    }
  }
  function soon() { clearTimeout(t); t = setTimeout(fit, 30); }
  new MutationObserver(soon).observe(document.documentElement,
    {childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'hidden']});
  window.addEventListener('resize', soon);
  window.addEventListener('load', soon);
})();
</script>'''


PAGE_FIT = r"""<style>
html, body { overflow: hidden !important; }
body { margin: 10px 12px !important; }
</style><script>
(function () {
  var t = null;
  function fit() {
    var b = document.body;
    if (!b) return;
    b.style.zoom = '';
    var s = Math.min(1, window.innerWidth / b.scrollWidth, window.innerHeight / b.scrollHeight);
    if (s < 1) b.style.zoom = s;
  }
  function soon() { clearTimeout(t); t = setTimeout(fit, 30); }
  new MutationObserver(soon).observe(document.documentElement, {childList: true, subtree: true});
  window.addEventListener('resize', soon);
  window.addEventListener('load', soon);
})();
</script>"""


# ---------- scheduler & settings ----------
def _deck_id():
    return mw.col.decks.id_for_name(DECK) if mw.col else None


def due_count() -> int:
    did = _deck_id()
    if not did:
        return 0
    for n in mw.col.sched.deck_due_tree().children:
        if n.deck_id == did:
            return n.new_count + n.learn_count + n.review_count
    return 0


ADDON = __name__.split(".")[0]


def _cfg() -> dict:
    return mw.addonManager.getConfig(ADDON) or {}


def _cfg_set(key, value) -> None:
    c = _cfg()
    c[key] = value
    mw.addonManager.writeConfig(ADDON, c)


def _when_ready(fn, tries: int = 200) -> None:
    """Run fn once the collection is loaded and no sync/progress dialog is busy."""
    if mw.col and not mw.progress.busy() and mw.state in ("deckBrowser", "overview", "review"):
        fn()
    elif tries > 0:
        QTimer.singleShot(300, lambda: _when_ready(fn, tries - 1))


class _HeaderButton(QLabel):
    def __init__(self, text: str, tip: str, slot) -> None:
        super().__init__(text)
        self.slot = slot
        self.setToolTip(tip)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setContentsMargins(6, 0, 6, 0)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.slot()


class Trainer(QObject):
    def __init__(self) -> None:
        super().__init__(mw)
        self.chrome = False        # main window currently dressed as the widget
        self.lesson = False        # a lesson is running (window can't be closed)
        self.popped = False        # the lesson was started by the timer, not by you
        self.quitting = False
        self.last_lesson_end = 0.0
        self.last_sync = time.time()
        self.saved_geometry = None
        self.widget_pos = None
        self.header: QWidget | None = None
        self.counts: QLabel | None = None
        self.btn_tray: QLabel | None = None
        self.tray: QSystemTrayIcon | None = None
        self.toggle_act: QAction | None = None
        self.use_mask = False
        self.filters_on_bars = False
        self.pending_open = False
        self.grips: list = []
        self.title: QLabel | None = None
        self.scale = 1.0
        self.timer = QTimer(mw)
        self.timer.timeout.connect(self.tick)
        mw.installEventFilter(self)
        # Windows logoff/shutdown: let Anki close normally
        mw.app.commitDataRequest.connect(lambda *_: setattr(self, "quitting", True))

    # ----- view mode: "widget" (default) or "window" -----
    @property
    def mode(self) -> str:
        return _cfg().get("view", "widget")

    @_safe
    def set_mode(self, mode: str) -> None:
        _cfg_set("view", mode)
        self.update_toggle_text()
        self.present(activate=True)

    @_safe
    def toggle_mode(self) -> None:
        self.set_mode("window" if self.mode == "widget" else "widget")

    def update_toggle_text(self) -> None:
        text = "Показать как окно" if self.mode == "widget" else "Показать как виджет"
        if self.toggle_act:
            self.toggle_act.setText(text)

    # ----- tray & menus -----
    @_safe
    def setup_menus(self) -> None:
        if self.tray or not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(mw.windowIcon(), mw)
        self.tray.setToolTip("Anki — English Trainer")
        menu = QMenu(mw)
        self.toggle_act = QAction("", menu)
        self.toggle_act.triggered.connect(self.toggle_mode)
        self.autostart_act = QAction("Запускать вместе с системой", menu)
        self.autostart_act.setCheckable(True)
        self.autostart_act.setChecked(os.path.exists(AUTOSTART))
        self.autostart_act.toggled.connect(_set_autostart)
        for item in (("Занятие сейчас", self.lesson_now), ("Закрепить сегодняшнее", self.practice_now),
                     ("Показать", self.show_ui), self.toggle_act,
                     ("Синхронизировать", self.sync_now), self.autostart_act, None, ("Выход", self.quit)):
            if item is None:
                menu.addSeparator()
            elif isinstance(item, QAction):
                menu.addAction(item)
            else:
                act = QAction(item[0], menu)
                act.triggered.connect(item[1])
                menu.addAction(act)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.on_tray_click)
        self.tray.show()
        # Anki's own menu (window mode): Tools → «Показать как виджет»
        act = QAction("Показать как виджет", mw)
        act.triggered.connect(lambda: self.set_mode("widget"))
        mw.form.menuTools.addAction(act)
        self.update_toggle_text()

    @_safe
    def practice_now(self) -> None:
        """Reinforcement: extra practice on today's material (does not touch the schedule)."""
        from . import practice
        self.present(activate=True)
        practice.start()

    def on_tray_click(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_ui()

    @_safe
    def show_ui(self) -> None:
        if due_count() > 0 and mw.state != "review":
            self.lesson_now()
        else:
            self.present(activate=True)

    def quit(self) -> None:
        self.quitting = True
        if self.tray:
            self.tray.hide()
        mw.close()  # Anki's normal exit: sync on close, backup, unload

    @_safe
    def hide_to_tray(self) -> None:
        if self.lesson:
            return
        mw.hide()
        self.sync()

    # ----- presenting the main window -----
    @_safe
    def present(self, activate: bool = True, lesson: bool = False) -> None:
        if self.mode == "widget" or lesson:
            self.apply_chrome(activate)
        else:
            self.remove_chrome()
            mw.showNormal()
        if activate:
            mw.activateWindow()
            mw.raise_()

    def apply_chrome(self, activate: bool) -> None:
        if not self.chrome:
            self.chrome = True
            if mw.isVisible():
                self.saved_geometry = mw.saveGeometry()
            mw.hide()
            mw.setWindowState(Qt.WindowState.WindowNoState)  # a maximised window ignores setGeometry
            # Anki's window, central area and web view all carry minimum sizes bigger than a small widget
            self.saved_mins = [(w, w.minimumSize()) for w in (mw, mw.form.centralwidget, mw.web)]
            for w, _ in self.saved_mins:
                w.setMinimumSize(1, 1)
            mw.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
            mw.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            mw.form.menubar.setVisible(False)
            _set_bars_visible(False)
            self.ensure_header().show()
            if not self.filters_on_bars:
                mw.bottomWeb.installEventFilter(self)
                mw.toolbarWeb.installEventFilter(self)
                self.filters_on_bars = True
            self.scale = self.clamp_scale(float(_cfg().get("widget_scale", 1.0)))
            area = mw.screen().availableGeometry()
            w, h = self.size_for(self.scale)
            x, y = self.widget_pos or (area.right() - w - 16, area.bottom() - h - 16)
            mw.setGeometry(x, y, w, h)
            self.apply_scale()
            self.show_grips(True)
            self.reload_page()
        prev = _foreground()
        mw.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, not activate)
        mw.showNormal() if mw.isMinimized() else mw.show()
        if not activate:  # Windows may still re-activate a window that was active before hiding
            for ms in (0, 150, 600):
                QTimer.singleShot(ms, lambda: _give_focus_back(prev))
        self.use_mask = not _round_corners(mw)  # Windows 10 has no system rounding -> window mask
        if self.use_mask:
            _apply_mask(mw)
        self.update_header()

    def remove_chrome(self) -> None:
        if not self.chrome:
            return
        self.chrome = False
        self.widget_pos = (mw.x(), mw.y())
        mw.hide()
        mw.clearMask()
        mw.setWindowFlag(Qt.WindowType.FramelessWindowHint, False)
        mw.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        mw.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
        mw.form.menubar.setVisible(True)
        _set_bars_visible(True)
        if self.header:
            self.header.hide()
        self.show_grips(False)
        mw.web.setZoomFactor(1.0)
        for w, size in getattr(self, "saved_mins", []):
            w.setMinimumSize(size)
        if self.saved_geometry:
            mw.restoreGeometry(self.saved_geometry)
        self.reload_page()

    def reload_page(self) -> None:
        """Re-render the current screen so its page gets / loses the widget styles."""
        if mw.state == "review":
            self.start_review(force=True)   # same card again (it hasn't been answered)
        elif self.lesson:
            return  # start_lesson opens the review itself — don't start a slow deck-screen render
        elif mw.state == "deckBrowser" and self.chrome:
            self.show_deck()
        elif mw.state in ("overview", "deckBrowser"):
            mw.moveToState(mw.state)

    # ----- size: one number scales the window and everything in it -----
    def clamp_scale(self, s: float) -> float:
        area = mw.screen().availableGeometry()
        max_s = min(area.width() / WIDGET_W, (area.height() - 32) / (WIDGET_H + HEADER_H))
        return max(MIN_W / WIDGET_W, min(s, max_s))

    def size_for(self, s: float) -> tuple[int, int]:
        return round(WIDGET_W * s), round((WIDGET_H + HEADER_H) * s)

    def resize_from(self, corner: str, g0, s: float) -> None:
        self.scale = self.clamp_scale(s)
        w, h = self.size_for(self.scale)
        x = g0.x() + g0.width() - w if corner in ("tl", "bl") else g0.x()   # opposite corner fixed
        y = g0.y() + g0.height() - h if corner in ("tl", "tr") else g0.y()
        area = mw.screen().availableGeometry()  # never off the screen
        x = max(area.left(), min(x, area.left() + area.width() - w))
        y = max(area.top(), min(y, area.top() + area.height() - h))
        mw.setGeometry(x, y, w, h)
        self.apply_scale()

    def apply_scale(self) -> None:
        s = self.scale
        mw.web.setZoomFactor(s)
        if self.header:
            self.header.setFixedHeight(round(HEADER_H * s))
            self.header.setStyleSheet(self.header_css(s))
        self.place_grip()

    def save_scale(self) -> None:
        cfg = _cfg()
        cfg["widget_scale"] = round(self.scale, 3)
        mw.addonManager.writeConfig(ADDON, cfg)

    def show_grips(self, on: bool) -> None:
        if on and not self.grips:
            self.grips = [_ResizeGrip(self, c) for c in ("tl", "tr", "bl", "br")]
            mw.web.loadFinished.connect(lambda *_: self.chrome and mw.web.setZoomFactor(self.scale))
        for g in self.grips:
            g.setVisible(on)
        self.place_grip()

    def place_grip(self) -> None:
        m, s = 1, _ResizeGrip.SIZE
        for g in self.grips:
            x = m if g.corner in ("tl", "bl") else mw.width() - s - m
            y = m if g.corner in ("tl", "tr") else mw.height() - s - m
            g.move(x, y)
            g.raise_()

    def header_css(self, s: float) -> str:
        bg, muted = ("#1a1a1c", "#8d92ad") if _night() else ("#f1f1f2", "#676c8a")
        return f"background:{bg}; color:{muted}; font-size:{12 * s:.1f}px; font-weight:600;"

    # ----- widget header: drag strip with counts and buttons -----
    def ensure_header(self) -> QWidget:
        if self.header:
            return self.header
        h = _DragStrip()
        h.setFixedHeight(HEADER_H)
        h.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        h.setStyleSheet(self.header_css(self.scale))
        lay = QHBoxLayout(h)
        lay.setContentsMargins(18, 0, 18, 0)
        lay.setSpacing(4)
        title = QLabel("English Trainer")
        title.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.counts = QLabel("")
        self.counts.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        lay.addWidget(title)
        lay.addStretch(1)
        lay.addWidget(self.counts)
        lay.addSpacing(6)
        lay.addWidget(_HeaderButton("⟳", "Синхронизировать", self.sync_now))
        lay.addWidget(_HeaderButton("⧉", "Показать как обычное окно Anki", lambda: self.set_mode("window")))
        self.btn_tray = _HeaderButton("—", "Спрятать в трей", self.hide_to_tray)
        lay.addWidget(self.btn_tray)
        mw.mainLayout.insertWidget(0, h)
        self.header = h
        return h

    def update_header(self) -> None:
        if self.btn_tray:
            self.btn_tray.setVisible(not self.lesson)  # no way out until the lesson is done
        if not self.counts:
            return
        try:
            if mw.state == "review":
                new, lrn, rev = mw.col.sched.counts()
                sep = '<span style="color:#666"> · </span>'
                self.counts.setText(f'<span style="color:#7aa2f7">{new}</span>{sep}'
                                    f'<span style="color:#ff6b70">{lrn}</span>{sep}'
                                    f'<span style="color:#3ddc97">{rev}</span>')
            else:
                self.counts.setText("")
        except Exception:
            pass

    # ----- window events -----
    def eventFilter(self, obj, event) -> bool:
        if self.chrome and obj in (getattr(mw, "bottomWeb", None), getattr(mw, "toolbarWeb", None)):
            if event.type() == QEvent.Type.Show:
                QTimer.singleShot(0, lambda: QWidget.setVisible(obj, False))  # re-shown by Anki
            return False
        if obj is not mw or self.quitting or not mw.col or not self.tray:
            return False
        et = event.type()
        if et == QEvent.Type.Close:
            event.ignore()
            self.hide_to_tray()  # during a lesson the window simply stays
            return True
        if et == QEvent.Type.WindowStateChange and self.lesson and mw.isMinimized():
            QTimer.singleShot(0, mw.showNormal)
        if et == QEvent.Type.Resize and self.chrome:
            if self.use_mask:
                _apply_mask(mw)
            self.place_grip()
        if et == QEvent.Type.Move and self.chrome and mw.isVisible():
            self.widget_pos = (mw.x(), mw.y())
        return False

    # ----- sync -----
    @_safe
    def sync_now(self) -> None:
        """Your click: sync right away, even mid-lesson (the lesson resumes after it)."""
        self.last_sync = time.time()
        mw.on_sync_button_clicked()

    @_safe
    def sync(self) -> None:
        try:
            if mw.col and mw.pm.sync_auth() and mw.state != "review":
                self.last_sync = time.time()
                mw.on_sync_button_clicked()
        except Exception:
            pass

    # ----- lessons -----
    @_safe
    def tick(self) -> None:
        try:
            if self.lesson or not mw.col or mw.progress.busy():
                return
            if mw.isVisible() and not self.chrome:
                return  # you're working in the normal Anki window — don't interrupt
            now = time.time()
            if now - self.last_lesson_end < GAP_AFTER_LESSON:
                return
            if _idle_seconds() > IDLE_LIMIT or _fullscreen_app():
                return
            if not mw.isVisible() and now - self.last_sync > SYNC_EVERY:
                self.sync()  # phone reviews first; due cards are checked on the next tick
                return
            if due_count() > 0:
                self.start_lesson(activate=False, popped=not mw.isVisible())
        except Exception:
            pass

    @_safe
    def lesson_now(self) -> None:
        if due_count() > 0:
            self.start_lesson(activate=True, popped=False)
        else:
            self.present(activate=True)

    @_safe
    def start_lesson(self, activate: bool, popped: bool) -> None:
        _log(f"lesson start (popped={popped}, state={mw.state}, due={due_count()})")
        self.lesson = True
        self.popped = popped
        self.present(activate=activate, lesson=True)
        self.start_review()
        self.update_header()

    @_safe
    def start_review(self, force: bool = False) -> None:
        if mw.state == "review" and not force:
            return  # already there — a second load would cut the first one off mid-way
        did = _deck_id()
        if not did:
            return
        mw.col.decks.select(did)
        mw.col.startTimebox()
        mw.moveToState("review")

    @_safe
    def on_state(self, new_state, old_state) -> None:
        _log(f"state {old_state} -> {new_state} (lesson={self.lesson}, chrome={self.chrome})")
        self.update_header()
        if self.chrome and new_state == "deckBrowser" and not self.lesson:
            QTimer.singleShot(0, self.show_deck)  # the widget shows our deck, not the deck list
            return
        if self.chrome and new_state == "review" and not self.lesson:
            self.lesson = True  # studying in the widget is a lesson: no way out until it's done
            self.popped = False
            self.update_header()
        if not self.lesson or new_state not in ("overview", "deckBrowser"):
            return
        if not mw.col or mw.progress.busy():
            return  # a sync is running — the lesson continues after it (on_sync_done)
        if due_count() > 0:
            # the lesson isn't over yet: back to the cards once the deck screen has rendered
            # (it renders asynchronously and would otherwise cover the cards) — see on_overview
            if new_state == "deckBrowser":
                QTimer.singleShot(0, self.show_deck)
            return
        self.lesson = False
        self.last_lesson_end = time.time()
        self.update_header()
        if self.popped:
            mw.hide()  # it came by itself — it leaves by itself
        elif self.mode == "window":
            self.present(activate=True)
        self.sync()

    @_safe
    def show_deck(self) -> None:
        did = _deck_id()
        if did and mw.state == "deckBrowser" and self.chrome:
            mw.col.decks.select(did)
            mw.moveToState("overview")

    @_safe
    def on_sync_done(self, *_args) -> None:
        if self.pending_open:
            self.pending_open = False
            _when_ready(self.show_ui)
        elif self.lesson and mw.state != "review":
            # via the deck screen: on_overview returns to the cards after it has rendered
            _when_ready(lambda: self.show_deck() if mw.state == "deckBrowser" else mw.moveToState("overview"))

    @_safe
    def on_overview(self, *_args) -> None:
        if self.lesson and mw.state == "overview" and due_count() > 0:
            QTimer.singleShot(0, self.start_review)

    @_safe
    def on_card_shown(self, *_args) -> None:
        if self.chrome:
            QTimer.singleShot(0, lambda: _set_bars_visible(False))
        self.update_header()

    @_safe
    def on_webview(self, web_content, context) -> None:
        kind = type(context).__name__
        if kind == "Reviewer":
            web_content.head += f"<style>{WIDGET_CSS}</style>"
            if self.chrome:
                web_content.head += FIT_JS
        elif kind in ("Overview", "DeckBrowser") and self.chrome:
            web_content.head += PAGE_FIT

    # ----- profile -----
    @_safe
    def on_open(self) -> None:
        self.quitting = False
        self.setup_menus()
        self.timer.start(CHECK_MS)
        background = False
        try:
            if os.path.exists(TRAY_FLAG):
                background = time.time() - os.path.getmtime(TRAY_FLAG) < 600
                os.remove(TRAY_FLAG)
        except OSError:
            pass
        if background:  # started with Windows: stay in the tray, the timer decides
            QTimer.singleShot(0, mw.hide)
            QTimer.singleShot(5000, self.tick)
        else:           # opened by you: lesson if cards are due, otherwise your chosen view
            try:
                will_sync = bool(mw.can_auto_sync())
            except Exception:
                will_sync = False
            if will_sync:
                self.pending_open = True  # on_sync_done takes over; fallback if it never comes
                QTimer.singleShot(20000, lambda: self.on_sync_done() if self.pending_open else None)
            else:
                _when_ready(self.show_ui)

    @_safe
    def on_close(self) -> None:
        self.timer.stop()
        self.lesson = False
        self.remove_chrome()


TRAINER = Trainer()
gui_hooks.profile_did_open.append(TRAINER.on_open)
gui_hooks.profile_will_close.append(TRAINER.on_close)
gui_hooks.state_did_change.append(TRAINER.on_state)
gui_hooks.reviewer_did_show_question.append(TRAINER.on_card_shown)
gui_hooks.reviewer_did_show_answer.append(TRAINER.on_card_shown)
gui_hooks.webview_will_set_content.append(TRAINER.on_webview)
gui_hooks.sync_did_finish.append(TRAINER.on_sync_done)
gui_hooks.overview_did_refresh.append(TRAINER.on_overview)
