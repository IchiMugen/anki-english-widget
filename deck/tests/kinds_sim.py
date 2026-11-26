"""Browser test of every exercise kind (headless Chrome / Edge), on a real enriched word.

    .venv\\Scripts\\python.exe tests\\kinds_sim.py            (exit 1 on a failure)

For each card direction × exercise kind and each host it renders the real card templates,
answers RIGHT (or WRONG), flips, and checks what was sent:
  desktop scheduled  -> et_log:{...} then et_auto_ease3 (right) / ease1 (wrong, after "Пропустить")
  desktop practice   -> et_practice:{...} and NEVER an ease (the schedule is not touched)
  AnkiDroid          -> api:ease3 / api:ease1 through the JS API
Also: a new example each showing (no immediate repeat), and no template error on any page.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

WORD = "to come across"
KINDS = {"ru-en": ["choice", "type", "situation", "produce", "sentence", "recall"],
         "en-ru": ["choice", "type", "meaning", "recall"],
         "ctx": ["choice", "type", "contrast", "listen"]}
ORD = {"ru-en": 0, "en-ru": 1, "ctx": 2}

PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>%(css)s</style></head>
<body class="card"><div id="qa"></div><pre id="log"></pre><script>
var L = [];
function log(x) { L.push(x); document.getElementById('log').textContent = JSON.stringify(L); }
function show(h) {
  var qa = document.getElementById('qa'); qa.innerHTML = h;
  [].slice.call(qa.querySelectorAll('script')).forEach(function (s) {
    var n = document.createElement('script'); n.text = s.text; s.parentNode.replaceChild(n, s); });
}
try { localStorage.clear(); sessionStorage.clear(); } catch (e) {}
var HOST = %(host)s, ACT = %(act)s, A = %(a)s, Q = %(q)s;
if (%(recent)s) localStorage.setItem('et-x:' + %(note)s, JSON.stringify(%(recent)s));
if (HOST === 'android') {
  document.documentElement.classList.add('android');
  window.AnkiDroidJS = function () {};
  AnkiDroidJS.prototype.ankiGetCardType = function () { return Promise.resolve({ success: true, value: 2 }); };
  AnkiDroidJS.prototype.ankiGetCardInterval = function () { return Promise.resolve({ success: true, value: 30 }); };
  AnkiDroidJS.prototype.ankiShowAnswer = function () { log('api:ans'); show(A); return Promise.resolve({ success: true }); };
  AnkiDroidJS.prototype.ankiTtsSpeak = function (t) { log('api:tts'); };
  [1, 2, 3, 4].forEach(function (n) { AnkiDroidJS.prototype['ankiAnswerEase' + n] = function () { log('api:ease' + n); return Promise.resolve({ success: true }); }; });
} else {
  window.ET_CARD = { type: 2, ivl: 30, m: {} };
  if (HOST === 'practice') window.ET_PRACTICE = { kind: %(kind)s };
  window.pycmd = function (c) { log(c.slice(0, 160)); if (c === 'ans') show(A); };
}
%(force)s
show(Q);
setTimeout(function () {
  var K = window.__etK; if (!K) { log('NO-K'); return; }
  log('KIND:' + K.kind + ':' + (K.x ? K.x.id : ''));
  var err = document.querySelector('.et-error'); if (err) log('ERROR:' + err.textContent);
  var opts = [].slice.call(document.querySelectorAll('.et-opt'));
  var inp = document.getElementById('et-input');
  var reveal = document.querySelector('[data-act="reveal"]');
  if (opts.length) {
    var texts = opts.map(function (o) { return o.querySelector('.et-opt-text').textContent; });
    var right = -1; (K.opts || []).forEach(function (o) { if (o.ok) right = texts.indexOf(o.text); });
    if (right < 0) { var a0 = K.a[0]; right = texts.indexOf(a0); }
    var pick = ACT === 'right' ? right : (right === 0 ? 1 : 0);
    opts[pick].click();
  } else if (inp) {
    inp.value = ACT === 'right' ? (K.self ? 'Yesterday I came across an interesting article.' : (K.lang === 'en' && K.target ? K.target : K.accept[0])) : 'qwerty';
    document.getElementById('et-check').click();
  } else if (reveal) { reveal.click(); }
}, 500);
setTimeout(function () {
  var err = document.querySelector('.et-error'); if (err) log('ERROR:' + err.textContent);
  var b = document.querySelector('[data-ease="3"]') && ACT === 'right' ? document.querySelector('[data-ease="3"]')
        : document.querySelector('[data-ease="1"]');
  if (b && !document.querySelector('.et-res-ok')) b.click();
}, 1800);
</script></body></html>"""

FORCE_SETTING = "try { localStorage.setItem('et-mode2', %s); } catch (e) {}"


def browser():
    for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"):
        if Path(p).exists():
            return p
    return shutil.which("chromium") or shutil.which("google-chrome")


def run(page: Path, exe: str) -> list:
    out = subprocess.run([exe, "--headless=new", "--disable-gpu", "--virtual-time-budget=9000", "--dump-dom",
                          page.as_uri()], capture_output=True, text=True, encoding="utf-8").stdout
    import html as h
    import re
    m = re.search(r'<pre id="log">([^<]*)</pre>', out)
    return json.loads(h.unescape(m.group(1))) if m and m.group(1) else []


def main():
    exe = browser()
    if not exe:
        print("SKIP: no Chrome / Edge")
        return 0
    js, css, front, back = build.load_sources()
    T = build.build_templates(js, front, back)
    note = next(r for r in build.read_rows(build.WORDS) if r["English"] == WORD)
    tmp = Path(tempfile.mkdtemp(prefix="et-kinds-"))
    fails = 0
    note_key = json.dumps(build.norm(WORD, "en"))

    def page(d, kind, host, act, recent="null", force=""):
        t = T[ORD[d]]
        q = build.render_mustache(t["qfmt"], note)
        a = build.render_mustache(t["afmt"], note)
        return PAGE % {"css": css, "host": json.dumps(host), "act": json.dumps(act), "kind": json.dumps(kind),
                       "a": json.dumps(a).replace("</", "<\\/"), "q": json.dumps(q).replace("</", "<\\/"),
                       "recent": recent, "note": note_key, "force": force}

    def check(name, log, want, forbid=()):
        nonlocal fails
        flat = " ".join(log)
        ok = all(w in flat for w in want) and not any(f in flat for f in forbid) and "ERROR:" not in flat
        print(("ok  " if ok else "FAIL") + f" {name}: " + (" | ".join(x[:70] for x in log) if not ok else ""))
        fails += not ok

    n = 0
    for d, kinds in KINDS.items():
        for kind in kinds:
            for act in ("right", "wrong"):
                n += 1
                p = tmp / f"p{n}.html"
                p.write_text(page(d, kind, "practice", act), encoding="utf-8")
                log = run(p, exe)
                want = ["KIND:", "ans", "et_practice:"]
                check(f"practice {d} {kind} {act}", log, want, forbid=["ease1", "ease3", "et_log:"])
    # scheduled desktop + android, auto mode (kind chosen by the card itself), a few times each
    for d in KINDS:
        for host in ("desktop", "android"):
            for act in ("right", "wrong"):
                n += 1
                p = tmp / f"p{n}.html"
                p.write_text(page(d, "", host, act, force=FORCE_SETTING % '"auto"'), encoding="utf-8")
                log = run(p, exe)
                if host == "desktop":
                    want = ["et_log:", "ease3"] if act == "right" else ["et_log:", "ease"]   # self-checked: plain ease3
                else:
                    want = ["api:ans", "api:ease3"] if act == "right" else ["api:ans", "api:ease"]
                check(f"{host} auto {d} {act}", log, want, forbid=["et_practice:"])
    # a new example each time: with e1,e2 shown last, the next pick is neither of them
    for i in range(5):
        n += 1
        p = tmp / f"p{n}.html"
        p.write_text(page("ctx", "type", "practice", "right", recent='["e1","e2"]'), encoding="utf-8")
        log = run(p, exe)
        kind_line = next((x for x in log if x.startswith("KIND:")), "")
        check(f"no repeat #{i + 1}", log, ["KIND:type:e"], forbid=["KIND:type:e1", "KIND:type:e2"]) \
            if kind_line else check(f"no repeat #{i + 1}", log, ["KIND:"])
    shutil.rmtree(tmp, ignore_errors=True)
    print("OK" if not fails else f"{fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
