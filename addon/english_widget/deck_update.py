"""Tools → «English Trainer: обновить колоду…» — import a newer English_Trainer.apkg correctly.

A double-click on the .apkg uses Anki's default import options: when the card structure changed
(e.g. a new field), Anki may skip every existing note or create a second note type. This menu
imports with the options the deck needs:
  * merge note types (the same "English Trainer" note type is updated, no copy);
  * always update notes and templates (the file is the source of the words);
  * keep your scheduling (intervals, history, FSRS) — the package carries none.
"""
from __future__ import annotations

from anki.collection import ImportAnkiPackageOptions, ImportAnkiPackageRequest
from anki.import_export_pb2 import ImportAnkiPackageUpdateCondition
from aqt import mw
from aqt.operations import CollectionOp
from aqt.qt import QAction, QFileDialog
from aqt.utils import showInfo

ALWAYS = ImportAnkiPackageUpdateCondition.IMPORT_ANKI_PACKAGE_UPDATE_CONDITION_ALWAYS


def update_deck(path: str | None = None) -> None:
    if not path:
        path, _ = QFileDialog.getOpenFileName(mw, "English_Trainer.apkg", "", "Anki deck (*.apkg)")
    if not path:
        return
    req = ImportAnkiPackageRequest(package_path=path, options=ImportAnkiPackageOptions(
        with_scheduling=False, merge_notetypes=True, update_notes=ALWAYS, update_notetypes=ALWAYS))

    def done(out) -> None:
        log = out.log
        showInfo(f"Колода обновлена: новых слов {len(log.new)}, обновлено {len(log.updated)}. "
                 "Прогресс сохранён.\n\nЕсли Anki попросит полную синхронизацию — на компьютере "
                 "выберите «Отправить в AnkiWeb», затем на телефоне «Загрузить из AnkiWeb».")

    CollectionOp(parent=mw, op=lambda col: col.import_anki_package(req)).success(done).run_in_background()


act = QAction("English Trainer: обновить колоду…", mw)
act.triggered.connect(lambda: update_deck())
mw.form.menuTools.addAction(act)
