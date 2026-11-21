"""Build the English Trainer deck: deck/words.csv -> English_Trainer.apkg (repo root)

Usage:
    python build.py                    # needs: pip install genanki
    python build.py --no-autofill      # don't auto-generate wrong options

One word list, one deck, one note type: every word inherits the same
templates, behaviour and settings (src/config.js). Row order = learning order.
Levels and parts of speech are tags (level::A1-A2, pos::verb, ...).

Needs: pip install genanki
"""
import csv
import difflib
import html
import json
import re
import sys
from pathlib import Path

import genanki

ROOT = Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT / "dist"

# Fixed IDs: re-importing an updated package updates the same note type / deck
# instead of creating duplicates. Do not change them.
MODEL_ID = 1_764_331_101
DECK_ID = 1_764_331_102
MODEL_NAME = "English Trainer"

DECK_NAME = "English Trainer"
WORDS = ROOT / "words.csv"
OUT = "English_Trainer.apkg"

FIELDS = ["English", "Russian", "Example", "Audio", "WrongEN", "WrongRU", "Explanation", "Hint"]
DIRECTIONS = [("ru-en", "RU → EN"), ("en-ru", "EN → RU"), ("ctx", "Контекст")]
FRONT_AUDIO = {
    "ru-en": "",  # the English sound would give the answer away
    "en-ru": "{{#Audio}}{{Audio}}{{/Audio}}{{^Audio}}{{tts en_US:English}}{{/Audio}}",
    "ctx": "",  # the sentence is the question; audio only on the answer side
}


# ---------------------------------------------------------------- templates
def load_sources():
    read = lambda n: (SRC / n).read_text(encoding="utf-8")
    js = read("core.js") + "\n" + read("ui.js")
    config = read("config.js")
    css = read("style.css")
    front = read("front.html").replace("%%CONFIG%%", config)
    example_audio = not re.search(r"exampleAudio\s*:\s*false", config)
    back = (read("back.html").replace("%%CONFIG%%", config)
            .replace("%%EXAMPLE_AUDIO%%", "{{#Example}}{{tts en_US:Example}}{{/Example}}" if example_audio else ""))
    for name, text in (("core.js/ui.js", js), ("config.js", config), ("style.css", css)):
        if "{{" in text:
            raise SystemExit(f"{name} contains '{{{{' which Anki would treat as a field tag")
    return js, css, front, back


def build_templates(js, front, back):
    out = []
    for d, name in DIRECTIONS:
        q = front.replace("%%DIR%%", d).replace("%%FRONT_AUDIO%%", FRONT_AUDIO[d]).replace("%%SCRIPT%%", js)
        if d == "ctx":  # only words with an example get a context card (empty front = no card)
            q = "{{#Example}}\n" + q + "\n{{/Example}}"
        a = back.replace("%%DIR%%", d).replace("%%SCRIPT%%", js)
        out.append({"name": name, "qfmt": q, "afmt": a})
    return out


# ---------------------------------------------------------------- data
def norm(s, lang=None):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = html.unescape(s).replace(" ", " ").lower().replace("ё", "е")
    s = re.sub(r"[’‘`´]", "'", s)
    s = re.sub(r"[“”«»\"]", "", s)
    s = re.sub(r"[.,!?;:()\[\]…]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if lang == "en":
        s = re.sub(r"^(to|a|an|the) ", "", s)
    return s


def alts(s):
    return [p.strip() for p in re.split(r"[;\n|]", s or "") if p.strip()]


def read_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in FIELDS + ["Tags", "GUID"]:
            r[k] = (r.get(k) or "").strip()
    return [r for r in rows if r["English"] and r["Russian"]]


def autofill(rows):
    """Fill empty WrongEN/WrongRU from *other words in the list*.

    Picks look-alike entries of the same shape (single word vs phrase,
    same leading verb for phrasal verbs). Never invents words; if nothing
    fits, the field stays short and the card shows fewer options.
    """
    filled = 0
    for r in rows:
        need_en, need_ru = not r["WrongEN"], not r["WrongRU"]
        if not (need_en or need_ru):
            continue
        en = norm(r["English"], "en")
        ru_set = {norm(a) for a in alts(r["Russian"])}
        words = en.split()

        def score(o):
            oen = norm(o["English"], "en")
            ow = oen.split()
            s = difflib.SequenceMatcher(None, en, oen).ratio()
            if (len(ow) > 1) == (len(words) > 1):
                s += 0.5
            if len(words) > 1 and ow and ow[0] == words[0]:
                s += 0.5
            return s

        cands = [o for o in rows if o is not r and norm(o["English"], "en") != en]
        cands = [o for o in cands if not ({norm(a) for a in alts(o["Russian"])} & ru_set)]
        cands.sort(key=score, reverse=True)
        cands = [o for o in cands if score(o) >= 0.5][:3]
        if not cands:
            continue
        if need_en:
            r["WrongEN"] = "; ".join(alts(o["English"])[0] for o in cands)
        if need_ru:
            r["WrongRU"] = "; ".join(alts(o["Russian"])[0] for o in cands)
        filled += 1
    return filled


# ---------------------------------------------------------------- preview
SVG_PLAY = ('<a class="replay-button soundLink" href="#"><svg class="playImage" viewBox="0 0 64 64">'
            '<circle cx="32" cy="32" r="29"/><path d="M56.502,32.301l-37.502,20.101l0.329,-40.804l37.173,20.703Z"/>'
            '</svg></a>')


def render_mustache(tpl, note):
    def sect(m):
        neg, name, body = m.group(1) == "^", m.group(2), m.group(3)
        present = bool(note.get(name, "").strip())
        return body if present != neg else ""

    prev = None
    while prev != tpl:
        prev = tpl
        tpl = re.sub(r"\{\{([#^])(\w+)\}\}(.*?)\{\{/\2\}\}", sect, tpl, flags=re.S)
    tpl = re.sub(r"\{\{tts [^:}]+:(\w+)\}\}", lambda m: SVG_PLAY, tpl)
    return re.sub(r"\{\{(\w+)\}\}", lambda m: note.get(m.group(1), ""), tpl)


PREVIEW_SEED = """<script>
(function(){
  var P = new URLSearchParams(location.search);
  if (P.get('night')) document.body.className += ' nightMode night_mode';
  if (P.get('still')) document.write('<style>*,*::before{animation:none!important;transition:none!important}</style>');
  if (P.get('desktop')) window.pycmd = function(c){ console.log('pycmd', c); };
  if (P.get('mode')) { try { localStorage.setItem('et-mode', P.get('mode')); } catch(e){} }
  if (P.get('state')) { window.__et = {}; var s = JSON.parse(P.get('state')); s.t = Date.now(); window.__et[%(key)s] = s; }
  window.__etPreview = { correct: %(correct)s, act: P.get('act') || '' };
})();
</script>"""

PREVIEW_ACT = """<script>
setTimeout(function(){
  var a = window.__etPreview.act, c = window.__etPreview.correct;
  if (!a) return;
  var opts = [].slice.call(document.querySelectorAll('.et-opt'));
  if (a === 'right' || a === 'wrong') {
    var b = opts.filter(function(o){ return (o.querySelector('.et-opt-text').textContent === c) === (a === 'right'); })[0];
    if (b) b.click();
  } else if (a.indexOf('type:') === 0) {
    var i = document.getElementById('et-input'); i.value = a.slice(5); document.getElementById('et-check').click();
  } else if (a === 'skip') { document.getElementById('et-skip').click(); }
}, 50);
</script>"""


def write_preview(rows, templates, css, pdir=None):
    pdir = pdir or DIST / "preview"
    pdir.mkdir(parents=True, exist_ok=True)
    links = []
    for i, note in enumerate(rows):
        en_key = norm(";".join(alts(note["English"])), "en")
        for t, (d, _) in zip(templates, DIRECTIONS):
            correct = alts(note["English"] if d == "ru-en" else note["Russian"])[0]
            seed = PREVIEW_SEED % {"key": json.dumps(f"et:{d}:{en_key}"), "correct": json.dumps(correct)}
            for side, tpl in (("front", t["qfmt"]), ("back", t["afmt"])):
                body = render_mustache(tpl, note)
                page = (f'<!doctype html><html><head><meta charset="utf-8">'
                        f'<meta name="viewport" content="width=device-width, initial-scale=1">'
                        f'<title>{i}-{d}-{side}</title><style>{css}</style></head>'
                        f'<body class="card card1">{seed}{body}{PREVIEW_ACT}</body></html>')
                fn = f"{i:02d}_{d}_{side}.html"
                (pdir / fn).write_text(page, encoding="utf-8")
                links.append(f'<li><a href="{fn}">{html.escape(note["English"])} — {d} — {side}</a></li>')
    (pdir / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>English Trainer preview</title>'
        '<p>Параметры: ?mode=choice|type|recall, &act=right|wrong|type:текст|skip, &night=1, &desktop=1, '
        '&state={"status":"wrong","mode":"type","given":"..."}</p><ul>' + "".join(links) + "</ul>",
        encoding="utf-8")


# ---------------------------------------------------------------- main
def note_guid(r):
    # Stable id: keeps progress on re-import. Explicit GUID column wins
    # (existing words); new words get one derived from the English text.
    return r.get("GUID") or genanki.guid_for("english-trainer", norm(r["English"], "en"))


def main(argv):
    js, css, front, back = load_sources()
    templates = build_templates(js, front, back)
    model = genanki.Model(MODEL_ID, MODEL_NAME, fields=[{"name": f} for f in FIELDS],
                          templates=templates, css=css, sort_field_index=0)
    rows = read_rows(WORDS)
    guids = [note_guid(r) for r in rows]
    if len(set(guids)) != len(guids):
        raise SystemExit("Дубликаты слов в words.csv — запусти tests/check_deck.py")
    if "--no-autofill" not in argv:
        n = autofill(rows)
        if n:
            print(f"autofill: wrong options generated for {n} notes")
    deck = genanki.Deck(DECK_ID, DECK_NAME)
    for i, (r, guid) in enumerate(zip(rows, guids)):
        tags = [t for t in re.split(r"[\s,]+", r.get("Tags") or "") if t]
        # due = row order: new cards come in the order of the list (most useful first)
        deck.add_note(genanki.Note(model=model, fields=[r[f] for f in FIELDS], tags=tags, due=i, guid=guid))
    DIST.mkdir(exist_ok=True)
    out = ROOT.parent / OUT          # next to install.cmd
    genanki.Package(deck).write_to_file(str(out))

    tdir = DIST / "templates"
    tdir.mkdir(exist_ok=True)
    for t, (d, _) in zip(templates, DIRECTIONS):
        (tdir / f"{d}_front.html").write_text(t["qfmt"], encoding="utf-8")
        (tdir / f"{d}_back.html").write_text(t["afmt"], encoding="utf-8")
    (tdir / "styling.css").write_text(css, encoding="utf-8")
    write_preview(rows, templates, css)
    n_cards = 2 * len(rows) + sum(1 for r in rows if r["Example"])
    print(f"OK: {out}  ({len(rows)} words, {n_cards} cards)")


if __name__ == "__main__":
    main(sys.argv[1:])
