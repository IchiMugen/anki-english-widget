"""Validate deck/units.jsonl against deck/words.csv and write DATA_QUALITY_REPORT.md.

    .venv\\Scripts\\python.exe tests\\check_units.py          (exit 1 on errors)

Errors (must be fixed): broken links, missing targets, duplicates, empty translations in rich units.
Warnings (listed in the report for a human look): long sentences, few examples, doubtful items.
"""
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402
import units  # noqa: E402

STOP = {"to", "a", "an", "the", "sb", "sth", "smb", "smth", "someone", "something", "one's", "be"}
PARTICLES = {"up", "down", "off", "on", "out", "in", "over", "back", "away", "around", "through", "across",
             "along", "about", "into", "for", "with", "by", "after", "forward", "together", "apart"}


def head_words(en: str) -> list[str]:
    return [w for w in re.split(r"[\s/]+", build.norm(en, "en")) if w and w not in STOP]


def check(rows, U):
    errors, warns, per = [], [], {}
    guids = [build.note_guid(r) for r in rows]
    gset = set(guids)
    for g in U:
        if g not in gset:
            errors.append(f"unit {g} «{U[g].get('en')}»: нет в words.csv")
    all_sent = collections.defaultdict(list)
    for r, g in zip(rows, guids):
        u = U.get(g)
        info = {"en": r["English"], "level": next((t[7:] for t in r["Tags"].split() if t.startswith("level::")), "—"),
                "status": "—", "meanings": 0, "examples": 0, "with_ru": 0, "review": 0, "issues": []}
        per[g] = info
        if not u:
            errors.append(f"«{r['English']}»: нет записи в units.jsonl")
            info["issues"].append("нет записи")
            continue
        info["status"] = u.get("status", "?")
        ms = u.get("meanings", [])
        mids = {m.get("id") for m in ms}
        info["meanings"] = len(ms)
        if not ms or any(not m.get("ru") for m in ms):
            errors.append(f"«{r['English']}»: значение без перевода")
        exs = u.get("examples", [])
        ids = [e.get("id") for e in exs]
        if len(ids) != len(set(ids)):
            errors.append(f"«{r['English']}»: повторяются id примеров")
        seen = set()
        particles = [w for w in head_words(r["English"])[1:] if w in PARTICLES]
        for e in exs:
            tag = f"«{r['English']}» {e.get('id')}"
            key = build.norm(e.get("en", ""))
            if key in seen:
                errors.append(f"{tag}: пример повторяется")
            seen.add(key)
            all_sent[key].append(r["English"])
            if e.get("m") not in mids:
                errors.append(f"{tag}: ссылка на несуществующее значение {e.get('m')}")
            if e.get("st") == "review":
                info["review"] += 1
                continue
            info["examples"] += 1
            if e.get("ru"):
                info["with_ru"] += 1
            if e.get("src") == "legacy" and not e.get("t"):
                continue
            t = e.get("t", "")
            if not t:
                errors.append(f"{tag}: нет целевой формы (t)")
            elif not units.target_in(e["en"], t):
                errors.append(f"{tag}: «{t}» нет в предложении: {e['en']}")
            else:
                tw = build.norm(t).split()
                missing = [p for p in particles if p not in tw]
                if missing:
                    errors.append(f"{tag}: пропуск оставляет подсказку «{' '.join(missing)}» вне пропуска: {t}")
            if u.get("status") == "rich" and not e.get("ru"):
                errors.append(f"{tag}: нет перевода примера")
            if len(e.get("en", "").split()) > 18:
                warns.append(f"{tag}: длинное предложение ({len(e['en'].split())} слов)")
        if u.get("status") == "rich":
            need = units.MIN_EXAMPLES_COMPLEX if units.is_complex(u) else units.MIN_EXAMPLES
            if info["examples"] < need:
                errors.append(f"«{r['English']}»: {info['examples']} примеров, нужно не меньше {need}")
            for m in ms:
                if not any(e.get("m") == m["id"] and e.get("st") != "review" for e in exs):
                    errors.append(f"«{r['English']}»: у значения {m['id']} нет примеров")
            if not u.get("forms"):
                errors.append(f"«{r['English']}»: нет форм (forms)")
        for d in u.get("doubts", []):
            info["issues"].append(d)
            warns.append(f"«{r['English']}»: сомнение — {d}")
        if info["review"]:
            info["issues"].append(f"{info['review']} пример(ов) на проверке")
    for key, owners in all_sent.items():
        if len(set(owners)) > 1:
            warns.append(f"одно предложение у разных слов ({', '.join(sorted(set(owners)))}): {key}")
    return errors, warns, per


def report(rows, U, errors, warns, per) -> str:
    total = len(rows)
    rich = sum(1 for i in per.values() if i["status"] == "rich")
    ex_all = sum(i["examples"] for i in per.values())
    ex_ru = sum(i["with_ru"] for i in per.values())
    poly = sum(1 for i in per.values() if i["meanings"] > 1)
    review = sum(i["review"] for i in per.values())
    lines = [
        "# Отчёт о качестве данных — English Trainer",
        "",
        "Создаётся `tests/check_units.py` из `deck/words.csv` + `deck/units.jsonl`. Руками не править.",
        "",
        "Статусы: **rich** — значения, 5+ примеров (6+ для фразовых глаголов и многозначных) с переводом, формы; "
        "**migrated** — только старые данные (один пример, одно значение), ещё не обработано.",
        "Все примеры написаны для колоды (сгенерированы, это не цитаты) и проверены автоматически: "
        "целевая форма есть в предложении, пропуск не оставляет подсказку, есть перевод, нет повторов. "
        "**Ни один пример не помечен как проверенный человеком**; сомнительное — в разделе ниже.",
        "",
        "## Итог",
        "",
        f"| | |",
        f"|---|---|",
        f"| Учебных единиц (слова и выражения) | {total} |",
        f"| Обработано (rich) | {rich} ({100 * rich // max(total, 1)}%) |",
        f"| Ещё не обработано (migrated) | {total - rich} |",
        f"| Примеров в карточках | {ex_all} (с переводом: {ex_ru}) |",
        f"| Многозначных единиц | {poly} |",
        f"| Примеров отложено на проверку | {review} |",
        f"| Ошибок | {len(errors)} |",
        f"| Предупреждений | {len(warns)} |",
        "",
    ]
    if errors:
        lines += ["## Ошибки", ""] + [f"- {e}" for e in errors] + [""]
    if warns:
        lines += ["## Нужно посмотреть человеку", ""] + [f"- {w}" for w in warns] + [""]
    lines += ["## По каждой единице", "", "| # | English | Уровень | Статус | Значений | Примеров | С переводом | Заметки |",
              "|---|---|---|---|---|---|---|---|"]
    for n, (r) in enumerate(rows, 1):
        i = per[build.note_guid(r)]
        notes = "; ".join(i["issues"]).replace("|", "/")
        lines.append(f"| {n} | {r['English'].replace('|', '/')} | {i['level']} | {i['status']} | {i['meanings']} | "
                     f"{i['examples']} | {i['with_ru']} | {notes} |")
    return "\n".join(lines) + "\n"


def main():
    rows = build.read_rows(build.WORDS)
    U = units.load()
    errors, warns, per = check(rows, U)
    (ROOT.parent / "DATA_QUALITY_REPORT.md").write_text(report(rows, U, errors, warns, per), encoding="utf-8")
    rich = sum(1 for i in per.values() if i["status"] == "rich")
    print(f"units: {len(rows)}, rich: {rich}, examples: {sum(i['examples'] for i in per.values())}, "
          f"errors: {len(errors)}, warnings: {len(warns)} -> DATA_QUALITY_REPORT.md")
    for e in errors[:40]:
        print("ERROR", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
