"""Quality checks for a word list (run before building / after adding words).

    python tests/check_deck.py [words.csv ...]
The first file is checked; the others are only used to report overlaps.
Exit code 1 if there are errors.
"""
import collections
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from build import alts, norm  # noqa: E402

STOP = {"a", "an", "the", "to", "sb", "sth", "smb", "smth", "someone", "something", "one's"}


def target_regex(answers):
    """Python port of ETCore.targetRegex (src/core.js)."""
    parts = []
    for a in answers:
        for w in norm(a, "en").split(" "):
            if not w or w in STOP:
                continue
            if len(w) >= 4 and w.endswith("e"):
                r = re.escape(w[:-1]) + "(?:e|es|ed|ing|er)"
            elif len(w) >= 3:
                r = re.escape(w) + "(?:s|es|ed|d|ing|ly|er|est)?"
            else:
                r = re.escape(w)
            if r not in parts:
                parts.append(r)
    return re.compile(r"\b(?:" + "|".join(parts) + r")\b", re.I) if parts else None


def load(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# --- transliteration guard: a Russian variant that just spells the English answer gives it away
_TR = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
               ["a", "b", "v", "g", "d", "e", "e", "g", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r",
                "s", "t", "u", "f", "h", "ts", "ch", "sh", "sh", "", "y", "", "e", "yu", "ya"]))
# real Russian words of the same origin (the only natural translation) — allowed
COGNATES = {"проблема", "интересный", "приоритет", "интерес", "штат", "секунда", "форма", "термин",
             "партия", "история", "эффект", "период", "момент",
             "школа", "план", "студент", "новости",
             "популярный", "брат", "сестра", "огород",
             "ферма", "лифт", "коллега", "плюс", "секрет", "странный"}


def _skel(s):
    s = s.lower()
    for a, b in (("dzh", "g"), ("dg", "g"), ("j", "g"), ("ph", "f"), ("ck", "k"), ("c", "k"),
                 ("q", "k"), ("x", "ks"), ("th", "t"), ("w", "v")):
        s = s.replace(a, b)
    return "".join(ch for ch in s if ch.isalpha() and ch not in "aeiouyh")


def translit_of(en, ru):
    if ru.lower() in COGNATES or not any("а" <= ch <= "я" for ch in ru.lower()):
        return False
    words = [w for w in re.split(r"[\s-]+", en.lower()) if w not in STOP]
    a, b = _skel("".join(_TR.get(ch, ch) for ch in ru.lower())), _skel("".join(words))
    return len(a) >= 3 and len(b) >= 3 and (a.startswith(b) or b.startswith(a) or a[:4] == b[:4])


def main(paths):
    rows = load(paths[0])
    errors, warns = [], []
    seen = {}
    for i, r in enumerate(rows, start=2):
        en, ru = r["English"].strip(), r["Russian"].strip()
        tag = f"line {i} «{en}»"
        if not en or not ru:
            errors.append(f"{tag}: пустое English/Russian")
            continue
        key = norm(en, "en")
        if key in seen:
            errors.append(f"{tag}: дубликат строки {seen[key]}")
        seen[key] = i
        en_alts, ru_alts = alts(en), alts(ru)
        for v in ru_alts:
            if translit_of(en, v):
                errors.append(f"{tag}: «{v}» — транслит английского, выдаёт ответ (термины не переводим)")
        wen, wru = alts(r["WrongEN"]), alts(r["WrongRU"])
        if len(wen) < 3 or len(wru) < 3:
            errors.append(f"{tag}: нужно 3 неправильных варианта (EN {len(wen)}, RU {len(wru)})")
        if len(wen) != len(wru):
            warns.append(f"{tag}: WrongEN и WrongRU разной длины")
        ans_en = {norm(a, "en") for a in en_alts}
        ans_ru = {norm(a) for a in ru_alts}
        for w in wen:
            if norm(w, "en") in ans_en:
                errors.append(f"{tag}: WrongEN «{w}» совпадает с ответом")
        for w in wru:
            if norm(w) in ans_ru:
                errors.append(f"{tag}: WrongRU «{w}» совпадает с переводом")
        if len({norm(w, 'en') for w in wen}) != len(wen) or len({norm(w) for w in wru}) != len(wru):
            errors.append(f"{tag}: повторы среди неправильных вариантов")
        is_verb = en.lower().startswith("to ")
        if any(w.lower().startswith("to ") != is_verb for w in wen):
            errors.append(f"{tag}: неправильные варианты другой формы (to + глагол)")
        if any("(" in a for a in ru_alts):
            errors.append(f"{tag}: скобки в Russian мешают проверке ввода — пояснение в Explanation")
        ex = r["Example"].strip()
        if not ex:
            warns.append(f"{tag}: нет примера")
        else:
            rx = target_regex(en_alts)
            if not rx or not rx.search(ex):
                errors.append(f"{tag}: пример не содержит слово в узнаваемой форме — маска не сработает: {ex}")
            if len(ex.split()) > 12:
                warns.append(f"{tag}: длинный пример ({len(ex.split())} слов)")

    others = set()
    for p in paths[1:]:
        others |= {norm(r["English"], "en") for r in load(p)}
    overlap = sorted(k for k in seen if k in others)

    tags = collections.Counter(r.get("Tags", "") for r in rows)
    print(f"{paths[0]}: {len(rows)} слов  " + ", ".join(f"{k or '—'}: {v}" for k, v in tags.most_common()))
    if overlap:
        print(f"пересечения с другими колодами (это отдельные записи, конфликта нет): {', '.join(overlap)}")
    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} ошибок")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or [str(Path(__file__).resolve().parent.parent / "words.csv")]))
