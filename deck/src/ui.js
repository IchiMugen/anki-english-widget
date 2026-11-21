/* English Trainer — card UI.
 * Front: the exercise. After an answer the card flips to the answer side
 * immediately; the answer side renders the very same picture (no flash) and
 * sends the grade in the background through Anki's own answer action:
 *   Desktop:   pycmd('ans') / pycmd('easeN')        -> Reviewer._answerCard (V3 + FSRS)
 *   AnkiDroid: JS API 0.0.3 ankiShowAnswer() / ankiAnswerEaseN() -> flipOrAnswerCard(Rating)
 * Intervals are never computed or written here.
 */
(function () {
  'use strict';
  if (typeof document === 'undefined') return;
  var root = document.getElementById('et-root');
  if (!root) return;

  var C = ETCore;
  var CFG = window.ET_CONFIG || {};
  var SIDE = root.getAttribute('data-side');
  var DIR = root.getAttribute('data-dir');
  var CTX = DIR === 'ctx';          // context card: sentence with a gap -> English word
  var TO_EN = DIR !== 'en-ru';      // the answer is English (ru-en and ctx)
  var esc = C.esc;
  var AUTO = CFG.autoGrade !== false;
  var CORRECT_DELAY = typeof CFG.correctDelay === 'number' ? CFG.correctDelay : 3000;
  var RETRY = CFG.retryAfterError !== false;

  /* ---------- fields ---------- */
  function fhtml(name) {
    var el = document.querySelector('#et-data [data-f="' + name + '"]');
    return el ? el.innerHTML : '';
  }
  function htmlToText(html) {
    var d = document.createElement('div');
    d.innerHTML = html;
    return d.textContent || '';
  }
  function ftext(name) { return C.clean(htmlToText(fhtml(name))); }
  function flist(name) { return C.splitText(htmlToText(C.brToSep(fhtml(name)))); }

  var EN = flist('en'), RU = flist('ru');
  var D = {
    q: TO_EN ? RU : EN,
    a: TO_EN ? EN : RU,
    lang: TO_EN ? 'en' : 'ru',
    wrong: flist(TO_EN ? 'wen' : 'wru'),
    example: ftext('ex'),
    expl: C.clean(fhtml('expl')),
    hint: C.clean(fhtml('hint'))
  };
  if (!D.q.length) D.q = ['—'];
  if (!D.a.length) D.a = ['—'];
  // accepted typed answers; on the context card also the exact form used in the sentence
  D.accept = D.a.slice();
  if (CTX && D.example) {
    var rx = C.targetRegex(EN), m = D.example.match(rx || /$^/);
    if (m && m.length) D.accept.push(m.join(' '));
  }
  var TAGS = ' ' + htmlToText(fhtml('tags')).toLowerCase() + ' ';
  var HARD = / (et::hard|leech) /.test(TAGS);

  /* ---------- storage (front -> back) ----------
   * Desktop keeps one page for both sides (window object survives);
   * AnkiDroid reloads the page for the answer (sessionStorage survives). */
  var KEY = 'et:' + DIR + ':' + C.norm(EN.join(';'), 'en');
  window.__et = window.__et || {};
  function ssGet(k) {
    try { var v = window.sessionStorage.getItem(k); if (v) return JSON.parse(v); } catch (e) {}
    return window.__et[k] || null;
  }
  function ssSet(k, v) {
    window.__et[k] = v;
    try { window.sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) {}
  }
  function lsGet(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { window.localStorage.setItem(k, v); } catch (e) {} }

  var MODES = ['choice', 'type', 'recall'];        // exercises
  var SETTINGS = ['auto'].concat(MODES);            // what the switch can be set to
  // 'et-mode2': the switch got "auto" (default); old manual choices under 'et-mode' are not carried over.
  function getSetting() {
    var m = lsGet('et-mode2') || (ssGet('et-mode2') || {}).m || CFG.defaultMode || 'auto';
    return SETTINGS.indexOf(m) >= 0 ? m : 'auto';
  }
  function setMode(m) { lsSet('et-mode2', m); ssSet('et-mode2', { m: m }); }
  function getMode() { var m = getSetting(); return m === 'auto' ? (window.__etAutoMode || 'choice') : m; }

  /* ---------- auto mode: the exercise gets harder as the card settles in memory ----------
   * new / learning / relearning (just forgotten) -> choice
   * review, interval >= AUTO.type days          -> typing the English word (ru-en, ctx)
   * review, interval >= AUTO.typeRu days        -> typing the Russian translation too (en-ru)
   * A mistake sends the card to relearning, so it drops back to choice by itself. */
  var AUTO = { type: 4, typeRu: 21 };
  function autoMode(info) {
    if (!info || info.type !== 2) return 'choice';
    return info.ivl >= (TO_EN ? AUTO.type : AUTO.typeRu) ? 'type' : 'choice';
  }
  // Desktop: the add-on puts window.ET_CARD into the card HTML. AnkiDroid: JS API (async).
  // Anything else (AnkiMobile, preview): no info -> choice.
  function cardInfo(cb) {
    if (window.ET_CARD) { cb(window.ET_CARD); return; }
    var api = host() === 'ankidroid' ? ankiDroid() : null;
    if (!api || typeof api.ankiGetCardType !== 'function' || typeof api.ankiGetCardInterval !== 'function') { cb(null); return; }
    var done = false;
    function once(v) { if (!done) { done = true; cb(v); } }
    function val(r) { return r && typeof r === 'object' && 'value' in r ? r.value : r; }
    setTimeout(function () { once(null); }, 600);
    try {
      var t = api.ankiGetCardType(), i = api.ankiGetCardInterval();
      if (t && typeof t.then === 'function') {
        Promise.all([t, i]).then(function (r) { once({ type: +val(r[0]), ivl: +val(r[1]) }); }, function () { once(null); });
      } else once({ type: +val(t), ivl: +val(i) });
    } catch (e) { once(null); }
  }
  function saveResult(st) { st.t = st.t || Date.now(); ssSet(KEY, st); }
  function loadResult() {
    var st = ssGet(KEY);
    if (!st || st.status === 'pending' || Date.now() - (st.t || 0) > 30 * 60 * 1000) return null;
    return st;
  }

  /* ---------- host ---------- */
  // NB: AnkiDroid declares `class AnkiDroidJS` at top level of js-api.js: that is a
  // global lexical binding, NOT window.AnkiDroidJS — so it must be referenced bare.
  var AD = null;
  function ankiDroid() {
    if (AD !== null) return AD;
    AD = false;
    try {
      if (typeof AnkiDroidJS === 'function') {
        AD = new AnkiDroidJS({ version: '0.0.3', developer: 'English Trainer card template' });
      }
    } catch (e) { AD = false; }
    return AD;
  }
  function isAndroid() {
    var html = document.documentElement;
    return (html && html.classList && html.classList.contains('android')) ||
      /AnkiDroid/i.test(navigator.userAgent || '') || !!ankiDroid();
  }
  function host() {
    if (typeof window.pycmd === 'function') return 'desktop';
    if (isAndroid()) return 'ankidroid';
    return null;
  }
  // AnkiDroid also understands "signal:" links (AbstractFlashcardViewer.filterUrl):
  // signal:show_answer, signal:answer_ease1..4 -> flipOrAnswerCard(Rating). Used only
  // when the JS API is missing or reports failure, so a card is never answered twice.
  function signal(name) {
    if (typeof window.__etSignal === 'function') { window.__etSignal(name); return; } // test hook
    try { window.location.href = 'signal:' + name; } catch (e) {}
  }
  function adCall(method, sig) {
    var api = ankiDroid();
    if (!api || typeof api[method] !== 'function') { signal(sig); return; }
    try {
      var p = api[method]();
      if (p && typeof p.then === 'function') {
        p.then(function (r) { if (r && r.success === false) signal(sig); }, function () { signal(sig); });
      }
    } catch (e) { signal(sig); }
  }
  function flip() {
    var h = host();
    if (h === 'desktop') window.pycmd('ans');
    else if (h === 'ankidroid') adCall('ankiShowAnswer', 'show_answer');
  }
  function sendGrade(ease) {
    var h = host();
    if (h === 'desktop') window.pycmd('ease' + ease);
    else if (h === 'ankidroid') adCall('ankiAnswerEase' + ease, 'answer_ease' + ease);
  }

  /* Timers never act on another card: Desktop keeps the page (and old timers)
   * across cards, so every render bumps a global token. */
  window.__etTok = (window.__etTok || 0) + 1;
  function bump() { return ++window.__etTok; }
  function later(fn, ms) {
    var tok = window.__etTok;
    return setTimeout(function () { if (window.__etTok === tok) fn(); }, ms);
  }

  /* ---------- icons & small helpers ---------- */
  var IC = {
    choice: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="4" width="18" height="6" rx="2"/><rect x="3" y="14" width="18" height="6" rx="2"/></svg>',
    type: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="2" y="6" width="20" height="12" rx="2.5"/><path d="M6 10h.01M10 10h.01M14 10h.01M18 10h.01M7 14h10"/></svg>',
    recall: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-3.5 10.9c.6.4 1 1.1 1 1.8V16h5v-.3c0-.7.4-1.4 1-1.8A6 6 0 0 0 12 3z"/></svg>',
    ok: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    bad: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    skip: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    warn: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"><path d="M12 7v6M12 17h.01"/></svg>'
  };
  IC.auto = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 18l5-6 4 3 7-9"/><path d="M15 6h5v5"/></svg>';
  var MODE_LABEL = { auto: 'Авто', choice: 'Выбор', type: 'Ввод', recall: 'Вспомнить' };

  function altsHtml(list) {
    return list.map(function (s) { return '<span class="et-alt">' + esc(s) + '</span>'; })
      .join('<span class="et-dot"> · </span>');
  }
  function chip() {
    return '<span class="et-chip">' + (CTX ? 'КОНТЕКСТ' : TO_EN ? 'RU <i>→</i> EN' : 'EN <i>→</i> RU') + '</span>' +
      (HARD ? '<span class="et-chip et-chip-hard" title="Часто забываешь это слово">трудное</span>' : '');
  }
  function mountAudio(slotId, srcId) {
    var src = document.getElementById(srcId || 'et-audio-src');
    var slot = document.getElementById(slotId);
    if (!src || !slot) return;
    while (src.firstChild) slot.appendChild(src.firstChild);
  }
  function diffHtml(typed, expected) {
    var d = C.diff(typed, expected);
    function row(tag, cells, cls) {
      var h = '';
      cells.forEach(function (c) {
        var ch = c[0] === ' ' ? '&nbsp;' : esc(c[0]);
        h += c[1] ? ch : '<span class="' + cls + '">' + ch + '</span>';
      });
      return '<div class="et-diff-row"><span class="et-diff-tag">' + tag + '</span><span class="et-diff-txt">' + h + '</span></div>';
    }
    return '<div class="et-diff">' + row('Ты', d.typed, 'd-bad') + row('Верно', d.expected, 'd-miss') + '</div>';
  }
  function each(sel, fn) { Array.prototype.forEach.call(root.querySelectorAll(sel), fn); }

  /* ---------- shared view: the same on both sides ---------- */
  // auto: "Авто" is on and the exercise it picked is marked softly (is-auto)
  function segHtml(mode) {
    var h = '', setting = getSetting();
    SETTINGS.forEach(function (m) {
      var cls = m === setting ? 'is-on' : (setting === 'auto' && m === mode ? 'is-auto' : '');
      h += '<button type="button" data-mode="' + m + '" class="' + cls + '">' +
        IC[m] + '<span>' + MODE_LABEL[m] + '</span></button>';
    });
    return '<div class="et-seg" role="tablist">' + h + '</div>';
  }
  function promptHtml() {
    var reveal = '';
    if (CTX && SIDE !== 'back') {
      // the sentence itself is the question; translation (and hint) only on request
      reveal += '<button type="button" class="et-reveal" data-reveal="ru">Перевод</button>';
    }
    if (SIDE !== 'back' && D.hint && (HARD || CTX)) {
      reveal += '<button type="button" class="et-reveal" data-reveal="hint">Подсказка</button>';
    }
    var hidden = (CTX ? '<div class="et-hidden" data-for="ru" lang="ru">' + altsHtml(RU) + '</div>' : '') +
      (D.hint ? '<div class="et-hidden" data-for="hint">' + esc(D.hint) + '</div>' : '');
    if (CTX) {
      var sentence = SIDE === 'back' ? C.highlightExample(D.example, EN) : C.maskExample(D.example, EN);
      return '<section class="et-glass et-prompt et-in">' +
        '<div class="et-label">' + chip() + 'Вставь пропущенное</div>' +
        '<div class="et-word et-word-ctx" lang="en">' + sentence + '</div>' +
        (SIDE === 'back' ? '<div class="et-audio-slot" id="et-audio-exslot"></div>' : '') +
        (reveal ? '<div class="et-reveals">' + reveal + '</div>' + hidden : '') +
        '</section>';
    }
    var hint = '';
    if (D.example) {
      hint = '<div class="et-hint" lang="en">' +
        (TO_EN ? C.maskExample(D.example, EN) : C.highlightExample(D.example, EN)) + '</div>';
    }
    return '<section class="et-glass et-prompt et-in">' +
      '<div class="et-label">' + chip() + (TO_EN ? 'Переведи на английский' : 'Переведи на русский') + '</div>' +
      '<div class="et-word" lang="' + (TO_EN ? 'ru' : 'en') + '">' + altsHtml(D.q) + '</div>' +
      (TO_EN ? '' : '<div class="et-audio-slot" id="et-audio-q"></div>') +
      hint +
      (reveal ? '<div class="et-reveals">' + reveal + '</div>' + hidden : '') +
      '</section>';
  }
  function bindReveals() {
    each('[data-reveal]', function (b) {
      b.addEventListener('click', function (e) {
        e.stopPropagation();
        var el = root.querySelector('[data-for="' + b.getAttribute('data-reveal') + '"]');
        if (el) el.classList.add('is-open');
        b.disabled = true;
      });
    });
  }
  function optionsHtml(opts, chosen) {
    var h = '<div class="et-options">';
    opts.forEach(function (o, i) {
      var cls = 'et-opt', key = String(i + 1);
      if (chosen >= 0) {
        if (o.ok) { cls += ' is-correct'; key = IC.ok; }
        else if (i === chosen) { cls += ' is-wrong'; key = IC.bad; }
        else cls += ' is-dim';
      }
      h += '<button type="button" class="' + cls + '" style="animation-delay:' + (i * 45) + 'ms" lang="' + D.lang + '"' +
        (chosen >= 0 ? ' disabled' : '') + '><span class="et-opt-key">' + key + '</span><span class="et-opt-text">' +
        esc(o.text) + '</span></button>';
    });
    return h + '</div>';
  }
  function typeHtml(value, cls, done) {
    return '<div class="et-glass et-type et-in">' +
      '<input id="et-input" class="et-input' + (cls ? ' ' + cls : '') + '" type="text" lang="' + D.lang + '"' +
      ' autocomplete="off" autocorrect="off" autocapitalize="none" spellcheck="false" enterkeyhint="done"' +
      ' placeholder="' + (TO_EN ? 'Напиши по-английски…' : 'Напиши по-русски…') + '"' +
      ' value="' + esc(value || '') + '"' + (done ? ' readonly' : '') + '>' +
      '<div class="et-row">' +
        '<button type="button" class="et-btn et-btn-primary" id="et-check"' + (done ? ' disabled' : '') + '>Проверить</button>' +
        '<button type="button" class="et-btn et-btn-ghost" id="et-skip"' + (done ? ' disabled' : '') + '>Не знаю</button>' +
      '</div></div>';
  }
  function recallHtml() {
    return '<div class="et-glass et-recall et-in">' +
      '<div class="et-recall-ico">' + IC.recall + '</div>' +
      '<p>Вспомни перевод про себя, потом открой ответ.</p>' +
      '<button type="button" class="et-btn et-btn-primary et-btn-block" data-act="reveal">Показать ответ</button>' +
      '</div>';
  }

  /* =================== FRONT =================== */
  var answered = false;

  function renderFront() {
    if (getSetting() !== 'auto') { drawFront(getSetting()); return; }
    var tok = window.__etTok;
    cardInfo(function (info) {
      if (window.__etTok !== tok) return;   // Desktop already moved to another card
      window.__etAutoMode = autoMode(info);
      drawFront(window.__etAutoMode);
    });
  }

  function drawFront(mode) {
    root.innerHTML = segHtml(mode) + promptHtml() +
      '<section id="et-ex" class="et-ex"></section><section id="et-fb" class="et-fb" aria-live="polite"></section>';
    mountAudio('et-audio-q');
    bindReveals();
    each('.et-seg button', function (b) {
      b.addEventListener('click', function () {
        if (answered) return;
        var m = b.getAttribute('data-mode');
        setMode(m);
        if (m === 'auto') { renderFront(); return; }
        each('.et-seg button', function (x) { x.className = x === b ? 'is-on' : ''; });
        renderExercise(m);
      });
    });
    renderExercise(mode);
  }

  function renderExercise(mode) {
    var ex = document.getElementById('et-ex');
    document.getElementById('et-fb').innerHTML = '';
    bump();
    answered = false;
    var opts = null, notice = '';
    if (mode === 'choice') {
      opts = C.buildOptions(D.a, D.wrong, D.lang);
      if (opts.length < 2) {
        mode = 'type';
        notice = '<div class="et-notice">У этой карточки нет вариантов ответа — напиши перевод.</div>';
      }
    }
    saveResult({ status: 'pending', mode: mode, t: Date.now() });
    if (mode === 'choice') frontChoice(ex, opts);
    else if (mode === 'type') frontTyping(ex, notice);
    else frontRecall(ex);
  }

  // Result is decided: remember it and move to the answer side, which shows the same picture.
  function finish(st, delay) {
    answered = true;
    st.t = Date.now();
    saveResult(st);
    if (host()) {
      later(flip, delay);
      later(function () { inlineFallback(st); }, delay + 2500); // flip did not happen (API unavailable)
    } else {
      inlineFallback(st);
    }
  }

  function inlineFallback(st) {
    var fb = document.getElementById('et-fb');
    if (!fb) return;
    var kind = st.status === 'correct' ? 'ok' : st.status === 'recall' ? 'skip' : st.status === 'skipped' ? 'skip' : 'bad';
    var title = st.status === 'correct' ? 'Верно' : st.status === 'recall' ? 'Ответ' : 'Правильно: ' + esc(D.a[0]);
    fb.innerHTML = '<div class="et-res et-res-' + kind + ' et-in"><div class="et-res-head"><span class="et-res-ico">' +
      IC[kind] + '</span><span>' + title + '</span></div></div>' +
      '<div class="et-flip-hint">Нажми «Показать ответ» внизу</div>';
  }

  function frontChoice(ex, opts) {
    ex.innerHTML = optionsHtml(opts, -1);
    var btns = Array.prototype.slice.call(ex.querySelectorAll('.et-opt'));
    btns.forEach(function (b, i) {
      b.addEventListener('click', function () {
        if (answered) return;
        var o = opts[i];
        btns.forEach(function (x, k) {
          x.disabled = true;
          if (opts[k].ok) { x.classList.add('is-correct'); x.querySelector('.et-opt-key').innerHTML = IC.ok; }
          else if (k !== i) x.classList.add('is-dim');
        });
        if (!o.ok) { b.classList.add('is-wrong'); b.querySelector('.et-opt-key').innerHTML = IC.bad; }
        finish({ status: o.ok ? 'correct' : 'wrong', mode: 'choice', opts: opts, chosen: i, given: o.text },
          o.ok ? 380 : 480);
      });
    });
  }

  function frontTyping(ex, notice) {
    ex.innerHTML = (notice || '') + typeHtml('', '', false);
    var input = document.getElementById('et-input');
    var bCheck = document.getElementById('et-check');
    var bSkip = document.getElementById('et-skip');
    function lock() {
      input.readOnly = true;
      bCheck.disabled = true;
      bSkip.disabled = true;
      input.blur();
    }
    function check() {
      if (answered) return;
      var r = C.checkTyped(input.value, D.accept, D.lang);
      if (r.status === 'empty') {
        input.classList.remove('is-shake');
        void input.offsetWidth;
        input.classList.add('is-shake');
        input.focus();
        return;
      }
      lock();
      var cls = r.status === 'correct' ? 'is-correct' : r.near ? 'is-near' : 'is-wrong';
      input.classList.add(cls);
      finish({ status: r.status, near: !!r.near, mode: 'type', given: input.value, expected: r.expected, cls: cls },
        r.status === 'correct' ? 380 : 480);
    }
    function skip() {
      if (answered) return;
      lock();
      finish({ status: 'skipped', mode: 'type', given: '' }, 150);
    }
    bCheck.addEventListener('click', check);
    bSkip.addEventListener('click', skip);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.keyCode === 13) { e.preventDefault(); e.stopPropagation(); check(); }
    });
    if (CFG.autoFocus !== false) setTimeout(function () { try { input.focus(); } catch (e) {} }, 60);
  }

  function frontRecall(ex) {
    saveResult({ status: 'recall', mode: 'recall', t: Date.now() });
    ex.innerHTML = recallHtml();
    ex.querySelector('[data-act="reveal"]').addEventListener('click', function () {
      if (answered) return;
      finish({ status: 'recall', mode: 'recall' }, 0);
    });
  }

  /* =================== BACK =================== */
  var graded = false;

  function grade(st, ease) {
    if (graded) return;
    graded = true;
    if (st) { st.graded = true; saveResult(st); }
    root.classList.add('is-leaving');
    sendGrade(ease);
  }

  // Desktop only: on views where Anki's own Space/Enter would mean "Good",
  // keep keyboard focus inside the card so Enter/Space do the right thing.
  // Digits 1–4 still grade manually; any Ctrl/Alt combo hands keys back to Anki.
  function keyTrap(onKey) {
    if (host() !== 'desktop') return;
    var t = document.createElement('input');
    t.className = 'et-keytrap';
    t.setAttribute('aria-hidden', 'true');
    t.setAttribute('tabindex', '-1');
    root.appendChild(t);
    var active = true;
    t.addEventListener('keydown', function (e) {
      if (e.ctrlKey || e.altKey || e.metaKey) { active = false; t.blur(); return; }
      if (onKey(e.key)) { e.preventDefault(); e.stopPropagation(); }
    });
    t.addEventListener('blur', function () {
      if (active) setTimeout(function () { if (active && document.body.contains(t)) try { t.focus({ preventScroll: true }); } catch (e) {} }, 0);
    });
    setTimeout(function () { try { t.focus({ preventScroll: true }); } catch (e) {} }, 30);
  }

  function exampleHtml(title) {
    return '<section class="et-glass et-section et-in">' + (title ? '<h4>' + title + '</h4>' : '') +
      '<div class="et-example-row"><div class="et-example" lang="en">' + C.highlightExample(D.example, EN) + '</div>' +
      '<span class="et-audio-slot et-audio-inline et-audio-small" id="et-audio-exslot"></span></div></section>';
  }

  // Wrong answer: write the correct word once — active recall instead of just reading it.
  function retryHtml() {
    return '<div class="et-glass et-type et-retry et-in">' +
      '<div class="et-retry-label">Напиши правильно, чтобы запомнить</div>' +
      '<input id="et-retry" class="et-input" type="text" lang="' + D.lang + '" autocomplete="off" autocorrect="off"' +
      ' autocapitalize="none" spellcheck="false" enterkeyhint="done" placeholder="' + esc(TO_EN ? 'по-английски…' : 'по-русски…') + '">' +
      '<div class="et-row">' +
        '<button type="button" class="et-btn et-btn-primary" data-act="retry">Проверить</button>' +
        '<button type="button" class="et-btn et-btn-ghost" data-ease="1">Пропустить</button>' +
      '</div></div>';
  }

  function detailsHtml(exampleOnly) {
    var h = '';
    var hint = D.hint ? '<section class="et-glass et-section et-in"><h4>Ассоциация</h4><div class="et-expl">' +
      esc(D.hint) + '</div></section>' : '';
    if (CTX) {
      // the sentence is already on screen (with its audio); show the translation instead
      var tr = '<section class="et-glass et-section et-in"><h4>Перевод</h4><div class="et-expl" lang="ru">' +
        altsHtml(RU) + '</div></section>';
      if (exampleOnly) return tr;
      h += tr + hint;
      if (D.expl) h += '<section class="et-glass et-section et-in"><h4>Пояснение</h4><div class="et-expl">' + D.expl + '</div></section>';
      return h;
    }
    if (exampleOnly) return (D.example ? exampleHtml('') : '') + (HARD ? hint : '');
    if (D.example) h += exampleHtml('Пример');
    h += hint;
    if (D.expl) h += '<section class="et-glass et-section et-in"><h4>Пояснение</h4><div class="et-expl">' + D.expl + '</div></section>';
    return h;
  }

  function resHtml(kind, title, body) {
    return '<div class="et-res et-res-' + kind + ' et-in"><div class="et-res-head"><span class="et-res-ico">' + IC[kind] +
      '</span><span class="et-res-title">' + title + '</span>' +
      (TO_EN ? '<span class="et-audio-slot et-audio-inline" id="et-audio-a"></span>' : '') +
      '</div>' + (body || '') + '</div>';
  }

  function actionsHtml(btns) {
    if (!host()) return '<div class="et-flip-hint">Оцени себя кнопками Anki внизу</div>';
    var h = '<div class="et-actions">';
    btns.forEach(function (b) {
      h += '<button type="button" class="et-btn ' + (b.primary ? 'et-btn-primary' : 'et-btn-ghost') + '" data-ease="' + b.ease + '">' +
        b.label + '</button>';
    });
    return h + '</div>';
  }

  function renderBack() {
    var st = loadResult();
    var mode = st ? st.mode : getMode();
    var status = st ? st.status : 'none';
    if (st && st.graded) status = 'graded';
    var answer = '<b>' + altsHtml(D.a) + '</b>';
    var body = '', result = '', actions = '', primary = null, auto = false, retry = false;

    if (mode === 'choice' && st && st.opts) body = optionsHtml(st.opts, st.chosen);
    else if (mode === 'type' && st) body = typeHtml(st.given, st.cls || '', true);

    if (status === 'correct') {
      result = resHtml('ok', 'Верно' + (mode === 'type' && D.a.length > 1 ? ' · ' + answer : ''));
      if (AUTO && host()) auto = true;
      else { primary = 3; actions = actionsHtml([{ ease: 3, label: 'Дальше', primary: true }]); }
    } else if (status === 'wrong' && st.near) {
      result = resHtml('warn', 'Похоже на опечатку', diffHtml(st.given, st.expected || D.a[0]));
      actions = actionsHtml([{ ease: 2, label: 'Засчитать', primary: true }, { ease: 1, label: 'Это ошибка' }]);
    } else if (status === 'wrong' || status === 'skipped') {
      result = status === 'wrong'
        ? resHtml('bad', 'Правильно: ' + answer, mode === 'type' ? diffHtml(st.given, st.expected || D.a[0]) : '')
        : resHtml('skip', 'Ответ: ' + answer);
      primary = 1;
      if (RETRY && host()) retry = true;
      else actions = actionsHtml([{ ease: 1, label: 'Дальше', primary: true }]);
    } else {
      // recall, unknown state (e.g. preview) or already graded: show the answer, user decides
      result = resHtml('skip', answer);
      actions = actionsHtml([{ ease: 1, label: 'Не вспомнил' }, { ease: 3, label: 'Вспомнил', primary: true }]);
    }

    var details = status === 'correct' ? detailsHtml(true) : detailsHtml();
    if (auto) actions = '<div class="et-flip-hint">Нажми в любом месте, чтобы перейти сразу</div>';
    root.className += ' et-static';
    root.innerHTML = segHtml(mode) + promptHtml() + '<section class="et-ex">' + body + '</section>' +
      '<section class="et-fb">' + result + (retry ? retryHtml() : '') + details + actions + '</section>';
    mountAudio(TO_EN ? 'et-audio-a' : 'et-audio-q');
    mountAudio('et-audio-exslot', 'et-audio-ex');
    each('.et-seg button', function (b) { b.disabled = true; });

    each('[data-ease]', function (b) {
      b.addEventListener('click', function () { grade(st, +b.getAttribute('data-ease')); });
    });

    if (retry) {
      var inp = document.getElementById('et-retry');
      var check = function () {
        if (graded) return;
        var r = C.checkTyped(inp.value, D.accept, D.lang);
        if (r.status === 'correct') {
          inp.readOnly = true;
          inp.classList.add('is-correct');
          inp.blur();
          later(function () { grade(st, 1); }, 700); // still Again: the word was not recalled the first time
        } else {
          inp.classList.remove('is-shake');
          void inp.offsetWidth;
          inp.classList.add('is-shake');
          if (r.status !== 'empty') inp.select();
        }
      };
      root.querySelector('[data-act="retry"]').addEventListener('click', check);
      inp.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.keyCode === 13) { e.preventDefault(); e.stopPropagation(); check(); }
      });
      setTimeout(function () { try { inp.focus({ preventScroll: true }); } catch (e) {} }, 60);
    }

    if (auto) {
      // Correct: let the result and the audio (word, then example) play, then Good in the background.
      var exWords = D.example && document.getElementById('et-audio-exslot') &&
        document.getElementById('et-audio-exslot').firstChild ? D.example.split(/\s+/).length : 0;
      var delay = Math.max(CORRECT_DELAY, exWords ? 1500 + exWords * 380 : 0);
      later(function () { grade(st, 3); }, delay);
      root.addEventListener('click', function (e) {
        if (!e.target.closest || !e.target.closest('.replay-button')) grade(st, 3);
      });
    } else if (host() && !retry) {
      keyTrap(function (k) {
        if (/^[1-4]$/.test(k)) { grade(st, +k); return true; }
        if (k === 'Enter' || k === ' ') { if (primary) grade(st, primary); return true; }
        return false;
      });
    }
  }

  try {
    if (SIDE === 'back') renderBack();
    else renderFront();
  } catch (err) {
    root.innerHTML = '<div class="et-error">English Trainer: ошибка шаблона — ' + esc(err && err.message) + '</div>';
  }
})();
