"""Build release assets into dist/:
    english_widget.ankiaddon      the add-on (double-click to install into Anki)
    English_Trainer.apkg          the deck (also kept in the repo root for the installers)
    English-Trainer-Setup.zip     install.cmd + install.ps1 + install.sh + add-on + deck
Run:  python tools/make_release.py 3.1.0   (the version of this release; needs: pip install genanki)
"""
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADDON = ROOT / "addon" / "english_widget"
DIST = ROOT / "dist"
SKIP = {"__pycache__", "user_files", "meta.json"}


def addon_files():
    for p in sorted(ADDON.rglob("*")):
        if p.is_file() and not (set(p.relative_to(ADDON).parts) & SKIP) and p.suffix != ".pyc":
            yield p


def main():
    # the release version: python tools/make_release.py 3.1.0 — written into the add-on (updater.py compares it
    # with GitHub) and into the deck (cards on the phone show "a new version is out")
    if len(sys.argv) > 1:
        (ADDON / "VERSION").write_text(sys.argv[1].lstrip("v") + chr(10), encoding="utf-8")
    subprocess.check_call([sys.executable, str(ROOT / "deck" / "build.py"), "--no-autofill"])
    DIST.mkdir(exist_ok=True)
    with zipfile.ZipFile(DIST / "english_widget.ankiaddon", "w", zipfile.ZIP_DEFLATED) as z:
        for p in addon_files():
            z.write(p, p.relative_to(ADDON).as_posix())   # .ankiaddon: files at the zip root
    shutil.copy(ROOT / "English_Trainer.apkg", DIST / "English_Trainer.apkg")
    with zipfile.ZipFile(DIST / "English-Trainer-Setup.zip", "w", zipfile.ZIP_DEFLATED) as z:
        base = "English-Trainer-Setup/"
        for name in ("install.cmd", "install.ps1", "install.sh", "English_Trainer.apkg", "README.md", "LICENSE"):
            z.write(ROOT / name, base + name)
        for p in addon_files():
            z.write(p, base + "addon/english_widget/" + p.relative_to(ADDON).as_posix())
    for f in sorted(DIST.iterdir()):
        print(f"{f.name:32} {f.stat().st_size // 1024:>6} KB")


if __name__ == "__main__":
    main()
