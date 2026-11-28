"""Validate the library (words.csv + units.jsonl + corpus) and write DATA_QUALITY_REPORT.md —
the migration report of contract 3.0 (§11): per word and in total, only real examples.

    .venv\\Scripts\\python.exe tests\\check_units.py          (exit 1 on errors)

Errors: unit missing / not in words.csv, meaning without translation, a card example whose target is not
in the quote or whose gap would leave a particle as a hint, a meaning added from the corpus with fewer
than 2 examples from 2 different sources (one doubtful line is not a dictionary meaning).
"""
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402
import units  # noqa: E402
from corpus import quality  # noqa: E402

STOP = {"to", "a", "an", "the", "sb", "sth", "smb", "smth", "someone", "something", "one's", "be"}
PARTICLES = {"up", "down", "off", "on", "out", "in", "over", "back", "away", "around", "through", "across",
             "along", "about", "into", "for", "with", "by", "after", "forward", "together", "apart"}
TYPES_RU = {"talk": "TED", "film": "фильмы", "series": "сериалы", "book": "книги", "essay": "нон-фикшн",
            "news": "новости"}
STATE_RU = {"full": "обеспечено", "partial": "частично", "insufficient_authentic_data": "нет материала"}


def head_words(en: str) -> list[str]:
    return [w for w in re.split(r"[\s/]+", build.norm(en, "en")) if w and w not in STOP]


def check(rows, U):
    errors, warns, per = [], [], {}
    guids = [build.note_guid(r) for r in rows]
    gset = set(guids)
    for g in U:
        if g not in gset:
            errors.append(f"unit {g} «{U[g].get('en')}»: нет в words.csv")
    allx = {e["id"]: e for e in units._jsonl(units.CORPUS_EXAMPLES)}
    src = {s["id"]: s for s in units._jsonl(units.CORPUS_SOURCES)}
    Q = units.load_corpus()
    for r, g in zip(rows, guids):
        u = U.get(g)
        info = {"en": r["English"], "level": next((t[7:] for t in r["Tags"].split() if t.startswith("level::")), "—"),
                "state": "insufficient_authentic_data", "meanings": 0, "confirmed": 0, "examples": 0,
                "sources": 0, "spoken": 0, "written": 0, "review": 0, "rejected": 0, "ru_source": 0,
                "ru_model": 0, "no_ru": 0, "thin": [], "notes": []}
        per[g] = info
        if not u:
            errors.append(f"«{r['English']}»: нет записи в units.jsonl")
            continue
        ms = u.get("meanings", [])
        info["meanings"] = len(ms)
        if not ms or any(not m.get("ru") for m in ms):
            errors.append(f"«{r['English']}»: значение без перевода")
        q = Q.get(g, [])
        full = [allx[x["id"][2:]] for x in q]
        info["state"] = quality.coverage(q, ms)
        info["examples"] = len(q)
        info["sources"] = len({e["src"] for e in full})
        info["confirmed"] = len({e["m"] for e in full})
        info["thin"] = [m["id"] for m in ms if m["id"] not in {e["m"] for e in full}]
        info["notes"] = u.get("corpus", {}).get("notes", [])
        info["rejected"] = len(u.get("corpus", {}).get("rejected", []))
        for e in full:
            reg = src.get(e["src"], {}).get("register", "")
            info["spoken" if reg.startswith("spoken") else "written"] += 1
            info["review"] += "needs_review" in e["status"]
            if not e.get("ru"):
                info["no_ru"] += 1
            elif e.get("ru_by") == "source":
                info["ru_source"] += 1
            else:
                info["ru_model"] += 1
        particles = [w for w in head_words(r["English"])[1:] if w in PARTICLES]
        for x in q:
            tag = f"«{r['English']}» {x['id']}"
            if not units.target_in(x["en"], x["t"]):
                errors.append(f"{tag}: «{x['t']}» нет в цитате")
            tw = build.norm(x["t"]).split()
            missing = [p for p in particles if p not in tw]
            if missing:
                errors.append(f"{tag}: пропуск оставляет подсказку «{' '.join(missing)}»: {x['t']}")
            if x["m"] not in {m["id"] for m in ms}:
                errors.append(f"{tag}: значение {x['m']} не существует")
        for m in ms:
            if m.get("from") == "corpus":
                ev = [e for e in full if e["m"] == m["id"]]
                if len(ev) < 2 or len({e["src"] for e in ev}) < 2:
                    errors.append(f"«{r['English']}»: значение {m['id']} добавлено по корпусу, но подтверждено "
                                  f"меньше чем 2 примерами из 2 источников")
        if info["state"] == "insufficient_authentic_data":
            warns.append(f"«{r['English']}»: реальных примеров нет (insufficient_authentic_data)")
    return errors, warns, per


def report(rows, U, errors, warns, per) -> str:
    allx = units._jsonl(units.CORPUS_EXAMPLES)
    src = {s["id"]: s for s in units._jsonl(units.CORPUS_SOURCES)}
    archive = units._jsonl(ROOT / "data" / "archive" / "synthetic_legacy.jsonl")
    n_syn = sum(len(a.get("examples", [])) + bool(a.get("words_csv_example")) for a in archive)
    total = len(rows)
    states = collections.Counter(i["state"] for i in per.values())
    shown = sum(i["examples"] for i in per.values())
    active_ids = {x["id"][2:] for v in units.load_corpus().values() for x in v}
    active = [e for e in allx if e["id"] in active_ids]
    types = collections.Counter(TYPES_RU.get(src.get(e["src"], {}).get("type"), "?") for e in active)
    by_check = {k: collections.Counter(str(e["checks"].get(k) or "нет") for e in active) for k in quality.CHECKS}
    processed = sum(1 for u in U.values() if u.get("corpus", {}).get("batch"))
    L = [
        "# Отчёт о данных — English Trainer (контракт 3.0: сначала реальный язык)",
        "",
        "Создаётся `tests/check_units.py`. Руками не править. Метрики по партиям корпуса — `data/corpus/reports/`.",
        "",
        "**Принцип:** каждое предложение в карточке — реальная цитата (TED, фильмы и сериалы, книги, новости) "
        "с зарегистрированным источником и лицензией. Придуманных предложений в карточках нет: "
        "`tests/check_authentic.py` останавливает обновление, если такое появится. Старые синтетические "
        "примеры лежат в архиве `data/archive/synthetic_legacy.jsonl` и не используются.",
        "",
        "**Кто что проверял.** «script» — цитата найдена в скачанном источнике дословно. «model» (Claude) — "
        "прочитала контекст и сравнила значение / перевод. «auto-ru» — в русском переводе самого источника есть "
        "перевод этого значения слова (это сигнал, не проверка). «auto-pos» — теггер частей речи согласен. "
        "**Человеком не проверено ничего.**",
        "",
        "## Итог",
        "",
        "| | |", "|---|---|",
        f"| Слов в библиотеке | {total} |",
        f"| Обработано корпусом | {processed} из {total} |",
        f"| Полностью обеспечено (≥5 примеров, все значения, ≥2 типа источников) | {states['full']} |",
        f"| Частично обеспечено | {states['partial']} |",
        f"| Недостаточно данных (insufficient_authentic_data) | {states['insufficient_authentic_data']} |",
        f"| Реальных примеров в карточках | {shown} |",
        f"| Уникальных источников | {len({e['src'] for e in active})} |",
        "| Источники по типам | " + ", ".join(f"{k} — {v}" for k, v in types.most_common()) + " |",
        f"| Разговорных / письменных примеров | {sum(i['spoken'] for i in per.values())} / "
        f"{sum(i['written'] for i in per.values())} |",
        f"| Перевод из источника / перевод модели / без перевода | {sum(i['ru_source'] for i in per.values())} / "
        f"{sum(i['ru_model'] for i in per.values())} / {sum(i['no_ru'] for i in per.values())} |",
        f"| Примеров с непроверенным переводом | {sum(1 for e in active if 'translation_verified' not in e['status'])} |",
        f"| Примеров, требующих проверки (needs_review) | {sum(1 for e in active if 'needs_review' in e['status'])} |",
        f"| Синтетических примеров вне активной библиотеки (архив) | {n_syn} |",
        f"| Проверено человеком | {sum(1 for e in active if 'human_reviewed' in e['status'])} |",
        f"| Ошибок | {len(errors)} |",
        "",
        "## Проверки по видам (активные примеры)",
        "",
        "| Проверка | Кто / результат |", "|---|---|",
    ] + [f"| {quality.STATUS[k]} | " + ", ".join(f"{a} — {b}" for a, b in c.most_common()) + " |"
         for k, c in by_check.items()] + [""]
    if errors:
        L += ["## Ошибки", ""] + [f"- {e}" for e in errors] + [""]
    L += ["## По каждому слову", "",
          "| # | Слово | Уровень | Состояние | Примеров | Источников | Значений (подтв./всего) | Разг./письм. "
          "| На проверке | Отклонено | Значения без материала | Заметки |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, r in enumerate(rows, 1):
        i = per[build.note_guid(r)]
        L.append(f"| {n} | {r['English'].replace('|', '/')} | {i['level']} | {STATE_RU[i['state']]} | {i['examples']} | "
                 f"{i['sources']} | {i['confirmed']}/{i['meanings']} | {i['spoken']}/{i['written']} | {i['review']} | "
                 f"{i['rejected']} | {', '.join(i['thin']) or '—'} | {'; '.join(i['notes']).replace('|', '/')} |")
    return "\n".join(L) + "\n"


def main():
    rows = build.read_rows(build.WORDS)
    U = units.load()
    errors, warns, per = check(rows, U)
    (ROOT.parent / "DATA_QUALITY_REPORT.md").write_text(report(rows, U, errors, warns, per), encoding="utf-8")
    st = collections.Counter(i["state"] for i in per.values())
    print(f"units: {len(rows)}, full: {st['full']}, partial: {st['partial']}, "
          f"insufficient: {st['insufficient_authentic_data']}, card examples: {sum(i['examples'] for i in per.values())}, "
          f"errors: {len(errors)} -> DATA_QUALITY_REPORT.md")
    for e in errors[:40]:
        print("ERROR", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
