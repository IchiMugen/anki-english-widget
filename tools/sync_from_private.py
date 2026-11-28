"""Bring the public repo level with the maintainer's private English Trainer (code + words + real examples).

    python tools/sync_from_private.py "C:/English/Anki Trainer"

Copies the card templates (deck/src), the deck build (build.py, units.py), the corpus checks and the
tests, adapting the paths to this repo's layout (deck/…), then refreshes the words, units and the
real-example corpus with tools/import_words.py. Run deck/tests/* and tools/make_release.py afterwards.
The add-on (addon/english_widget) is ported by hand: its names and menus differ from the private one.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / "deck"


# public deck only: the cards on a phone check the latest GitHub release once a day (src/ui.js updateBanner)
UPDATE_DEF = '''# public deck: cards compare their version with the latest GitHub release (src/ui.js updateBanner)
_VER = (ROOT.parent / "addon" / "english_widget" / "VERSION").read_text(encoding="utf-8").strip()
UPDATE_JS = "\\nwindow.ET_UPDATE = {repo: 'IchiMugen/anki-english-widget', version: '" + _VER + "'};\\n"
'''


def put(dst: Path, text: str) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8"))


def sub(text: str, pairs) -> str:
    for a, b in pairs:
        if a not in text:
            raise SystemExit(f"не найдено при адаптации: {a[:70]}")
        text = text.replace(a, b)
    return text


def main(priv: Path) -> None:
    rd = lambda p: (priv / p).read_text(encoding="utf-8").replace("\r\n", "\n")  # noqa: E731
    for f in sorted((priv / "src").iterdir()):
        if f.is_file():
            put(DECK / "src" / f.name, rd(f"src/{f.name}"))
    put(DECK / "build.py", sub(rd("build.py"), [
        ('"""Build the single English Trainer deck: data/words.csv -> dist/English_Trainer.apkg',
         '"""Build the English Trainer deck: deck/words.csv (+ deck/units.jsonl, deck/corpus) -> English_Trainer.apkg'),
        ("    python build.py                    # (or update.bat)", "    python build.py                    # needs: pip install genanki"),
        ("MODEL_ID = 1_731_906_001", "MODEL_ID = 1_764_331_101"),
        ("DECK_ID = 1_731_906_002", "DECK_ID = 1_764_331_102"),
        ('WORDS = ROOT / "data" / "words.csv"', 'WORDS = ROOT / "words.csv"'),
        ("    out = DIST / OUT\n", "    out = ROOT.parent / OUT          # next to install.cmd\n"),
        ('    config = read("config.js")\n', '    config = read("config.js") + UPDATE_JS\n'),
        ("NO_EXAMPLE = ", UPDATE_DEF + "NO_EXAMPLE = "),
    ]))
    put(DECK / "units.py", sub(rd("units.py"), [
        ('UNITS = ROOT / "data" / "units.jsonl"', 'UNITS = ROOT / "units.jsonl"'),
        ('CORPUS_EXAMPLES = ROOT / "data" / "corpus" / "examples.jsonl"', 'CORPUS_EXAMPLES = ROOT / "corpus" / "examples.jsonl"'),
        ('CORPUS_SOURCES = ROOT / "data" / "corpus" / "sources.jsonl"', 'CORPUS_SOURCES = ROOT / "corpus" / "sources.jsonl"'),
    ]))
    put(DECK / "corpus" / "__init__.py", "")
    put(DECK / "corpus" / "quality.py", rd("corpus/quality.py"))
    for t in ("kinds_sim.py", "test_core.js"):
        put(DECK / "tests" / t, rd(f"tests/{t}"))
    put(DECK / "tests" / "check_deck.py", sub(rd("tests/check_deck.py"), [
        ('main(sys.argv[1:] or ["data/words.csv"])', 'main(sys.argv[1:] or [str(Path(__file__).resolve().parent.parent / "words.csv")])')]))
    put(DECK / "tests" / "check_units.py", sub(rd("tests/check_units.py"), [
        ('(ROOT / "DATA_QUALITY_REPORT.md").write_text', '(ROOT.parent / "DATA_QUALITY_REPORT.md").write_text')]))
    auth = rd("tests/check_authentic.py")
    a = auth.index("    out = subprocess.run(")
    b = auth.index("    for e in errors[:60]:")
    put(DECK / "tests" / "check_authentic.py", auth[:a] + auth[b:])   # no units_import tool here
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "import_words.py"), str(priv / "data" / "words.csv")])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(Path(sys.argv[1]))
