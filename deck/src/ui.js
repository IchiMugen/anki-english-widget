/* English Trainer — card UI.
 * Front: the exercise. After an answer the card flips to the answer side
 * immediately; the answer side renders the very same picture (no flash) and
 * sends the grade in the background through Anki's own answer action:
 *   Desktop:   pycmd('ans') / pycmd('easeN')        -> Reviewer._answerCard (V3 + FSRS)
 *   AnkiDroid: JS API 0.0.3 ankiShowAnswer() / ankiAnswerEaseN() -> flipOrAnswerCard(Rating)
 * Intervals are never computed or written here.
 *
 * Each card of a word trains one skill and picks its exercise ("auto" mode, ETCore.pickKind):
 *   RU → EN   retrieval:   choice → type the word → fill a gap with the Russian situation →
 *                          translate a sentence → own sentence (self-checked)
 *   EN → RU   meaning:     choice → "what does it mean here" (a new sentence) → type the meaning
 *   Контекст  recognition: gap in a sentence (a different example every time) → contrast with
 *                          similar expressions → listening (desktop)
 * Grades stay Anki's own: right = Good, wrong = Again, typo = Hard/Again, self-checked = the user's choice.
 * Practice mode (window.ET_PRACTICE, the add-on's "Закрепление") renders the same exercises but sends
 * the result to the add-on instead of Anki — the schedule is not touched.
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
  var TO_EN = DIR !== 'en-ru';      // the card's own answer is English (ru-en and ctx)
  var esc = C.esc;
  var AUTO = CFG.autoGrade !== false;
  var CORRECT_DELAY = typeof CFG.correctDelay === 'number' ? CFG.correctDelay : 3000;
  // the user's own switch on the card (per device): after a correct answer go on by itself, or wait for «Дальше»
  function autoNext() { try { return localStorage.getItem('et-autonext') !== '0'; } catch (e) { return true; } }
  function setAutoNext(on) { try { localStorage.setItem('et-autonext', on ? '1' : '0'); } catch (e) {} }
  var BACK_TOKEN = 0, QUIET = false;
  var RETRY = CFG.retryAfterError !== false;
  var PRACTICE = window.ET_PRACTICE || null;

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
  if (!EN.length) EN = ['—'];
  if (!RU.length) RU = ['—'];
  var DATA = C.parseData(htmlToText(fhtml('data')));
  var LEGACY_EX = ftext('ex');
  var NO_EX = '\u2014';
  // examples: the unit's set, or the single old example
  // real quotes only (Data); the Example field is just the card's existence flag ('—' = no real example yet)
  var XS = DATA ? DATA.x : (LEGACY_EX && LEGACY_EX !== NO_EX ? [{ id: 'e1', en: LEGACY_EX, ru: '', t: '', m: 'm1' }] : []);
  var NOEX = CTX && !XS.length;      // context card of a word without real material: honest notice, no sentence
  var WEN = flist('wen'), WRU = flist('wru');
  var D = {
    lang: TO_EN ? 'en' : 'ru',
    a: TO_EN ? EN : RU,
    wrong: TO_EN ? WEN : WRU,
    expl: C.clean(fhtml('expl')),
    hint: C.clean(fhtml('hint'))
  };
  var TAGS = ' ' + htmlToText(fhtml('tags')).toLowerCase() + ' ';
  var HARD = / (et::hard|leech) /.test(TAGS);
  var NOTE = C.norm(EN.join(';'), 'en');

  /* ---------- storage (front -> back) ----------
   * Desktop keeps one page for both sides (window object survives);
   * AnkiDroid reloads the page for the answer (sessionStorage survives). */
  var KEY = 'et:' + DIR + ':' + NOTE;
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

  var MODES = ['choice', 'type', 'recall'];        // the switch's manual exercises
  var SETTINGS = ['auto'].concat(MODES);            // what the switch can be set to
  // 'et-mode2': the switch got "auto" (default); old manual choices under 'et-mode' are not carried over.
  function getSetting() {
    var m = lsGet('et-mode2') || (ssGet('et-mode2') || {}).m || CFG.defaultMode || 'auto';
    return SETTINGS.indexOf(m) >= 0 ? m : 'auto';
  }
  function setMode(m) { lsSet('et-mode2', m); ssSet('et-mode2', { m: m }); }
  // which switch button an exercise belongs to
  var BASE = { choice: 'choice', meaning: 'choice', contrast: 'choice', type: 'type', situation: 'type',
    listen: 'type', produce: 'recall', sentence: 'recall', recall: 'recall' };

  // examples shown lately for this word (all its cards): the next showing picks another one
  function recentEx() { try { return JSON.parse(lsGet('et-x:' + NOTE) || '[]'); } catch (e) { return []; } }
  function rememberEx(id) {
    var r = recentEx().filter(function (x) { return x !== id; });
    r.unshift(id);
    lsSet('et-x:' + NOTE, JSON.stringify(r.slice(0, 2)));
  }

  // Desktop: the add-on puts window.ET_CARD into the card HTML. AnkiDroid: JS API (async).
  // Anything else (AnkiMobile, preview): no info -> the easiest exercise.
  var EXTRA = false;   // shown in a temporary (filtered) deck: extra practice that counts in the main progress
  function cardInfo(cb) {
    if (window.ET_CARD) { cb(window.ET_CARD); return; }
    var api = host() === 'ankidroid' ? ankiDroid() : null;
    if (!api || typeof api.ankiGetCardType !== 'function' || typeof api.ankiGetCardInterval !== 'function') { cb(null); return; }
    var done = false;
    function once(v) { if (!done) { done = true; cb(v); } }
    function val(r) { return r && typeof r === 'object' && 'value' in r ? r.value : r; }
    setTimeout(function () { once(null); }, 600);
    // a temporary deck (AnkiDroid «Дополнительное обучение» = Anki custom study): the same cards, answers go
    // into their own history and schedule, i.e. the main progress — the card only says where it is shown
    try {
      var dn = typeof api.ankiGetDeckName === 'function' ? api.ankiGetDeckName() : null;
      var mark = function (n) { n = val(n); EXTRA = !!n && String(n) !== 'English Trainer'; };   // «Ещё занятие» or custom study
      if (dn && typeof dn.then === 'function') dn.then(mark, function () {}); else if (dn) mark(dn);
    } catch (e) {}
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
  var ADDON = host() === 'desktop' && !!(window.ET_CARD || PRACTICE);   // our add-on is there
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
  // auto: the add-on answers only after the word and example audio finished.
  // Practice: the result goes to the add-on, never to Anki's scheduler.
  function sendGrade(ease, auto, st, noLog) {
    var h = host();
    if (h === 'desktop' && ADDON && !noLog) {
      window.pycmd((PRACTICE ? 'et_practice:' : 'et_log:') + JSON.stringify(logEntry(st, ease)));
      if (PRACTICE) return;
    }
    if (h === 'desktop') window.pycmd((auto && ADDON ? 'et_auto_ease' : 'ease') + ease);
    else if (h === 'ankidroid') adCall('ankiAnswerEase' + ease, 'answer_ease' + ease);
  }
  function logEntry(st, ease) {
    st = st || {};
    return { d: DIR, k: st.kind || '', x: st.x || '', s: st.status || '', near: !!st.near, ms: st.ms || 0, e: ease };
  }
  // any sentence aloud: desktop — the add-on's voice (Piper); AnkiDroid — its TTS
  function say(text) {
    if (!text) return;
    var h = host();
    if (h === 'desktop' && ADDON) { window.pycmd('et_say:' + text); return; }
    var api = h === 'ankidroid' ? ankiDroid() : null;
    try {
      if (api && typeof api.ankiTtsSpeak === 'function') {
        if (typeof api.ankiTtsSetLanguage === 'function') api.ankiTtsSetLanguage('en_US');
        api.ankiTtsSpeak(text, 1);   // 1 = add to the queue (after the word)
      }
    } catch (e) {}
  }
  var CAN_SAY = ADDON || (host() === 'ankidroid' && !!ankiDroid() && typeof ankiDroid().ankiTtsSpeak === 'function');
  function prefetch(text) { if (ADDON && text) window.pycmd('et_prefetch:' + text); }

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
  var PLAY = '<svg class="playImage" viewBox="0 0 64 64"><circle cx="32" cy="32" r="29"/><path d="M56.502,32.301l-37.502,20.101l0.329,-40.804l37.173,20.703Z"/></svg>';

  function altsHtml(list) {
    return list.map(function (s) { return '<span class="et-alt">' + esc(s) + '</span>'; })
      .join('<span class="et-dot"> · </span>');
  }
  function chip() {
    return '<span class="et-chip">' + (CTX ? 'КОНТЕКСТ' : TO_EN ? 'RU <i>→</i> EN' : 'EN <i>→</i> RU') + '</span>' +
      (HARD ? '<span class="et-chip et-chip-hard" title="Часто забываешь это слово">трудное</span>' : '') +
      (PRACTICE ? '<span class="et-chip et-chip-practice" title="Не влияет на расписание">закрепление</span>' : '') +
      (EXTRA ? '<span class="et-chip et-chip-practice" title="Временная колода: ответы идут в основной прогресс">доп. занятие</span>' : '');
  }
  function mountAudio(slotId, srcId) {
    var src = document.getElementById(srcId || 'et-audio-src');
    var slot = document.getElementById(slotId);
    if (!src || !slot) return;
    while (src.firstChild) slot.appendChild(src.firstChild);
  }
  function sayBtn(text, cls) {
    if (!CAN_SAY || !text) return '';
    return '<span class="et-audio-slot et-audio-inline ' + (cls || 'et-audio-small') + '"><a class="replay-button et-say" href="#" data-say="' +
      esc(text) + '">' + PLAY + '</a></span>';
  }
  function bindSay() {
    each('.et-say', function (b) {
      b.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); say(b.getAttribute('data-say')); });
    });
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
  function exById(id) { for (var i = 0; i < XS.length; i++) if (XS[i].id === id) return XS[i]; return null; }
  function meaningOf(x) {
    var ms = (DATA && DATA.m) || [];
    for (var i = 0; i < ms.length; i++) if (ms[i].id === (x && x.m)) return ms[i];
    return ms[0] || null;
  }

  /* ---------- the exercise: kind + example + what counts as the answer ---------- */
  var K = null;   // {kind, x, lang, a, accept, wrong, target, opts?, self?}

  function caps() {
    var withT = XS.filter(function (x) { return !!C.findTarget(x.en, x.t, EN); });
    return {
      ru: XS.some(function (x) { return !!x.ru && !!C.findTarget(x.en, x.t, EN); }),
      t: withT.length > 0 && !!(DATA && DATA.m.length),
      c: !!(DATA && DATA.c.length),
      listen: CAN_SAY && withT.length > 0
    };
  }

  // kinds a card can show; anything that does not fit this word falls back to the card's basic exercise
  function setupKind(kind, xId, info) {
    var cp = caps(), x = null, need = null;
    if ((kind === 'situation' || kind === 'produce') && !cp.ru) kind = 'type';
    if (kind === 'meaning' && !cp.t) kind = 'choice';
    if (kind === 'contrast' && !cp.c) kind = 'type';
    if (kind === 'listen' && !cp.listen) kind = 'type';
    if (kind === 'situation' || kind === 'produce') need = 'ru';
    if (xId) x = exById(xId);
    if (!x) {
      var opts = { last: recentEx(), need: need, weak: (info && info.exw) || [], seen: (info && info.exs) || [] };
      var pool = XS.filter(function (e) { return !!C.findTarget(e.en, e.t, EN); });
      x = C.pickExample(pool.length ? pool : XS, opts);
    }
    var found = x ? C.findTarget(x.en, x.t, EN) : null;
    var k = { kind: kind, x: x, target: found ? found.text : '' };
    var forms = (DATA && DATA.f) || [];
    if (kind === 'meaning') {
      var m = meaningOf(x);
      k.lang = 'ru';
      k.a = m && m.ru ? m.ru : RU;
      k.opts = C.meaningOptions(DATA, m && m.id, WRU);
      if (!k.opts || k.opts.length < 2) { kind = k.kind = 'choice'; k.opts = null; }
    }
    if (kind === 'contrast') {
      k.lang = 'en';
      k.a = EN;
      k.opts = C.buildOptions(EN, DATA.c.map(function (c) { return c.en; }), 'en');
    }
    if (!k.lang) {
      var toEn = TO_EN || kind === 'situation';
      k.lang = toEn ? 'en' : 'ru';
      k.a = toEn ? EN : RU;
    }
    k.wrong = k.lang === 'en' ? WEN : WRU;
    // a sentence with a gap: the options are words of the same kind learnt before this one (Data.w), not unseen
    // look-alikes — otherwise the one familiar word gives the answer away
    if ((CTX || kind === 'situation') && k.lang === 'en' && DATA && DATA.w && DATA.w.length >= 2) k.wrong = DATA.w;
    k.accept = k.lang === 'en' ? C.acceptFor(EN, forms, k.target) : k.a.slice();
    k.self = kind === 'produce' || kind === 'sentence';
    if (kind === 'produce' && x) k.a = [x.en];
    return k;
  }

  /* ---------- shared view: the same on both sides ---------- */
  // auto: "Авто" is on and the exercise it picked is marked softly (is-auto)
  function segHtml(mode) {
    var h = '', setting = PRACTICE ? 'auto' : getSetting(), base = BASE[mode] || mode;
    SETTINGS.forEach(function (m) {
      var cls = m === setting ? 'is-on' : (setting === 'auto' && m === base ? 'is-auto' : '');
      h += '<button type="button" data-mode="' + m + '" class="' + cls + '"' + (PRACTICE ? ' disabled' : '') + '>' +
        IC[m] + '<span>' + MODE_LABEL[m] + '</span></button>';
    });
    return '<div class="et-seg" role="tablist">' + h + '</div>';
  }
  var LABEL = {
    meaning: 'Что значит выделенное здесь?',
    situation: 'Вставь слово по смыслу',
    produce: 'Переведи предложение',
    sentence: 'Составь своё предложение',
    contrast: 'Какое выражение подходит?',
    listen: 'Послушай и впиши пропущенное'
  };
  function revealsHtml(items) {
    if (!items.length) return '';
    return '<div class="et-reveals">' + items.map(function (it) {
      return '<button type="button" class="et-reveal" data-reveal="' + it[0] + '">' + it[1] + '</button>';
    }).join('') + '</div>' + items.map(function (it) {
      return '<div class="et-hidden" data-for="' + it[0] + '"' + (it[3] ? ' lang="' + it[3] + '"' : '') + '>' + it[2] + '</div>';
    }).join('');
  }
  var MARKED = '';
  function promptHtml() {
    var kind = K.kind, x = K.x, back = SIDE === 'back';
    var hint = D.hint && (HARD || CTX) && !back ? [['hint', 'Подсказка', esc(D.hint)]] : [];
    // ONE rule for every card: before the answer the word is a gap, after it the word is highlighted.
    // A sentence where the word cannot be found is never shown before the answer (it would give it away).
    var found = x && C.findTarget(x.en, x.t, EN);
    var sentenceMarked = x ? '<span class="et-sent">' + C.markTarget(x.en, x.t, EN) + '</span>' : '';
    var sentenceMasked = found ? '<span class="et-sent">' + C.maskTarget(x.en, x.t, EN) + '</span>' : '';
    MARKED = sentenceMarked;
    var head = '<section class="et-glass et-prompt et-in"><div class="et-label">' + chip() + (LABEL[kind] ||
      (CTX ? 'Вставь пропущенное' : TO_EN ? 'Переведи на английский' : 'Переведи на русский')) + '</div>';

    if (kind === 'meaning') {
      return head + '<div class="et-word et-word-ctx" lang="en">' + sentenceMarked + '</div>' +
        sayBtn(x.en) + revealsHtml(hint) + '</section>';
    }
    if (kind === 'situation') {
      return head + '<div class="et-situation" lang="ru">' + esc(x.ru) + '</div>' +
        '<div class="et-word et-word-ctx" lang="en">' + (back ? sentenceMarked : sentenceMasked) + '</div>' +
        (back ? sayBtn(x.en) : '') + revealsHtml(hint) + '</section>';
    }
    if (kind === 'produce') {
      return head + '<div class="et-word et-word-ctx" lang="ru">' + esc(x.ru) + '</div>' +
        '<div class="et-hint">Используй: <b lang="en">' + esc(EN[0]) + '</b></div>' + '</section>';
    }
    if (kind === 'sentence') {
      return head + '<div class="et-word" lang="en">' + altsHtml(EN) + '</div>' +
        '<div class="et-hint" lang="ru">' + altsHtml(RU) + '</div></section>';
    }
    if (kind === 'listen') {
      return head + (back ? '<div class="et-word et-word-ctx" lang="en">' + sentenceMarked + '</div>'
        : '<div class="et-listen-note">Предложение звучит — текста нет, как в жизни.</div>') +
        sayBtn(x.en, 'et-audio-big') + '</section>';
    }
    if (NOEX) {
      return head + '<div class="et-noex">Реального примера для этого слова пока нет — придуманные предложения '
        + 'в колоду не берём. Вспомни слово по переводу.</div>' +
        '<div class="et-word" lang="ru">' + altsHtml(RU) + '</div>' + revealsHtml(hint) + '</section>';
    }
    if (CTX || kind === 'contrast') {
      var tr = x && x.ru ? esc(x.ru) : altsHtml(RU);
      var rv = back ? [] : [['ru', 'Перевод', tr, 'ru']].concat(hint);
      return head + '<div class="et-word et-word-ctx" lang="en">' + (x ? (back ? sentenceMarked : sentenceMasked || '—') : '—') + '</div>' +
        (back && x ? sayBtn(x.en) : '') + revealsHtml(rv) + '</section>';
    }
    // RU → EN / EN → RU word cards: the word, and a sentence for context under it
    var under = '';
    var shown = TO_EN && !back ? sentenceMasked : sentenceMarked;
    if (x && shown) under = '<div class="et-hint" lang="en">' + shown + '</div>';
    var rvw = D.hint && HARD && !back ? [['hint', 'Подсказка', esc(D.hint)]] : [];
    return head + '<div class="et-word" lang="' + (TO_EN ? 'ru' : 'en') + '">' + altsHtml(TO_EN ? RU : EN) + '</div>' +
      (TO_EN ? '' : '<div class="et-audio-slot" id="et-audio-q"></div>') + under + revealsHtml(rvw) + '</section>';
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
      h += '<button type="button" class="' + cls + '" style="animation-delay:' + (i * 45) + 'ms" lang="' + K.lang + '"' +
        (chosen >= 0 ? ' disabled' : '') + '><span class="et-opt-key">' + key + '</span><span class="et-opt-text">' +
        esc(o.text) + '</span></button>';
    });
    return h + '</div>';
  }
  function typeHtml(value, cls, done, multi) {
    var ph = K.kind === 'sentence' ? 'Твоё предложение по-английски…' : K.kind === 'produce' ? 'Предложение по-английски…'
      : K.lang === 'en' ? 'Напиши по-английски…' : 'Напиши по-русски…';
    var attrs = ' class="et-input' + (multi ? ' et-input-multi' : '') + (cls ? ' ' + cls : '') + '" lang="' + K.lang + '"' +
      ' autocomplete="off" autocorrect="off" autocapitalize="none" spellcheck="false" enterkeyhint="done"' +
      ' placeholder="' + ph + '"' + (done ? ' readonly' : '');
    var field = multi ? '<textarea id="et-input" rows="2"' + attrs + '>' + esc(value || '') + '</textarea>'
      : '<input id="et-input" type="text"' + attrs + ' value="' + esc(value || '') + '">';
    return '<div class="et-glass et-type et-in">' + field +
      '<div class="et-row">' +
        '<button type="button" class="et-btn et-btn-primary" id="et-check"' + (done ? ' disabled' : '') + '>' +
          (multi ? 'Сравнить' : 'Проверить') + '</button>' +
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
  var answered = false, shownAt = Date.now();

  /* ---------- the learner's level (public deck only — window.ET_UPDATE; owner, 2026-11-28) ----------
   * Chosen once with one tap on the first card: beginner / medium / advanced. Stored on this device.
   *  - exercises: the auto mode moves to typing later (beginner, interval ×0.4) or sooner (advanced, ×2);
   *  - new words (phone, no add-on): a new word above the level (beginner: B2-C1 until 150 new words, B1-B2
   *    until 40; advanced: A1-A2 until 400) is buried till tomorrow with AnkiDroid's own «bury» — it comes later;
   *  - computer with the add-on: the level goes to the add-on, which reorders the new cards for real (pacing.py)
   *    and the card buries nothing. */
  var LEVELS = [['beginner', 'Начальный', 'самые простые слова сначала, больше подсказок'],
                ['medium', 'Средний', 'простые и средние вперемешку'],
                ['advanced', 'Продвинутый', 'больше сложных слов, сразу ввод']];
  function getLevel() {
    if (window.ET_CARD && typeof window.ET_CARD.level === 'string' && window.ET_CARD.level) return window.ET_CARD.level;
    try { return localStorage.getItem('et-level') || ''; } catch (e) { return ''; }
  }
  // a small «Уровень: …» under the card: one tap opens the three choices again
  function levelLink() {
    if (!levelOn() || !getLevel() || PRACTICE || document.getElementById('et-lvl')) return;
    var name = ''; LEVELS.forEach(function (l) { if (l[0] === getLevel()) name = l[1]; });
    var b = document.createElement('button');
    b.id = 'et-lvl'; b.type = 'button'; b.className = 'et-autotoggle';
    b.textContent = 'Уровень: ' + name + ' — поменять';
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      try { localStorage.removeItem('et-level'); } catch (err) {}
      if (window.ET_CARD) window.ET_CARD.level = '';
      b.parentNode.removeChild(b);
      levelPicker(function () { SIDE === 'back' ? renderBack() : renderFront(); levelLink(); });
    });
    root.parentNode.appendChild(b);
  }
  function levelOn() { return !!(window.ET_UPDATE && window.ET_UPDATE.repo); }
  function tierOf() { return / level::a1-a2 /.test(TAGS) ? 0 : / level::(b2-c1|c1-c2) /.test(TAGS) ? 2 : 1; }
  function newSeen() { return sessLoad().filter(function (x) { return x.n; }).length + (+(localStorage.getItem('et-new0') || 0)); }
  function scaleInfo(info) {
    var lv = levelOn() ? getLevel() : '';
    if (!info || info.type !== 2 || !lv || lv === 'medium') return info;
    var o = {}; for (var k in info) o[k] = info[k];
    o.ivl = lv === 'beginner' ? Math.floor(info.ivl * 0.4) : info.ivl * 2;
    return o;
  }
  function levelPicker(done) {
    root.innerHTML = '<section class="et-glass et-level et-in"><div class="et-level-title">Ваш уровень английского?</div>' +
      '<div class="et-level-sub">Под него подстроятся уроки. Поменять можно в любой момент — внизу карточки.</div>' +
      LEVELS.map(function (l) {
        return '<button type="button" class="et-level-btn" data-level="' + l[0] + '"><b>' + l[1] + '</b><span>' + l[2] + '</span></button>';
      }).join('') + '</section>';
    each('[data-level]', function (b) {
      b.addEventListener('click', function () {
        var lv = b.getAttribute('data-level');
        try { localStorage.setItem('et-level', lv); } catch (e) {}
        if (host() === 'desktop' && typeof window.pycmd === 'function') window.pycmd('et_level:' + lv);
        done();
      });
    });
  }
  // a new word above the chosen level on a phone: bury it till tomorrow (it comes back later), say why
  function deferIfAboveLevel(info) {
    var lv = getLevel(), api = host() === 'ankidroid' ? ankiDroid() : null;
    if (!levelOn() || !lv || lv === 'medium' || !info || info.type !== 0 || !api || typeof api.ankiBuryCard !== 'function') return false;
    var t = tierOf(), n = newSeen();
    var later = lv === 'beginner' ? (t === 2 && n < 150) || (t === 1 && n < 40) : (t === 0 && n < 400);
    if (!later) return false;
    root.innerHTML = '<section class="et-glass et-in"><div class="et-noex">Это слово ' +
      (lv === 'beginner' ? 'посложнее — придёт, когда освоите базовые' : 'простое — придёт позже') + '.</div></section>';
    try { api.ankiBuryCard(); } catch (e) {}
    return true;
  }

  function renderFront() {
    if (levelOn() && !getLevel() && !PRACTICE) { levelPicker(renderFront); return; }
    if (PRACTICE) { cardInfo(function (info) { drawFront(PRACTICE.kind || 'choice', PRACTICE.x, info); }); return; }
    var setting = getSetting();
    var tok = window.__etTok;
    cardInfo(function (info) {
      if (window.__etTok !== tok) return;   // Desktop already moved to another card
      if (deferIfAboveLevel(info)) return;
      var kind = setting === 'auto' ? C.pickKind(DIR, scaleInfo(info), caps()) : setting;
      drawFront(kind, null, info);
    });
  }

  function drawFront(kind, xId, info) {
    CARD_NEW = !!(info && info.type === 0);
    K = setupKind(kind, xId, info);
    window.__etK = K;   // read by the browser tests (tests/kinds_sim.py)
    if (K.x) { rememberEx(K.x.id); prefetch(K.x.en); }
    root.innerHTML = segHtml(K.kind) + promptHtml() +
      '<section id="et-ex" class="et-ex"></section><section id="et-fb" class="et-fb" aria-live="polite"></section>';
    mountAudio('et-audio-q');
    bindReveals();
    bindSay();
    each('.et-seg button', function (b) {
      b.addEventListener('click', function () {
        if (answered || PRACTICE) return;
        var m = b.getAttribute('data-mode');
        setMode(m);
        if (m === 'auto') { renderFront(); return; }
        drawFront(m, K.x && K.x.id, info);
      });
    });
    renderExercise();
    if (K.kind === 'listen') later(function () { say(K.x.en); }, 150);   // after renderExercise's bump()
  }

  function renderExercise() {
    var ex = document.getElementById('et-ex');
    document.getElementById('et-fb').innerHTML = '';
    bump();
    answered = false;
    shownAt = Date.now();
    var kind = K.kind, opts = K.opts, notice = '';
    if (kind === 'choice') {
      opts = C.buildOptions(K.a, K.wrong, K.lang);
      if (opts.length < 2) {
        kind = K.kind = 'type';
        notice = '<div class="et-notice">У этой карточки нет вариантов ответа — напиши перевод.</div>';
      }
    }
    saveResult({ status: 'pending', kind: kind, x: K.x && K.x.id, t: Date.now() });
    if (opts && (kind === 'choice' || kind === 'meaning' || kind === 'contrast')) frontChoice(ex, opts);
    else if (kind === 'recall') frontRecall(ex);
    else frontTyping(ex, notice, K.self);
  }

  // Result is decided: remember it and move to the answer side, which shows the same picture.
  function finish(st, delay) {
    answered = true;
    st.n = CARD_NEW;
    revealSentence();
    st.t = Date.now();
    st.kind = K.kind;
    st.x = K.x && K.x.id;
    st.ms = Date.now() - shownAt;
    saveResult(st);
    if (host()) {
      later(flip, delay);
      later(function () { inlineFallback(st); }, delay + 2500); // flip did not happen (API unavailable)
    } else {
      inlineFallback(st);
    }
  }

  // the answer is known: the gap in the prompt becomes the highlighted word at once (same as the back side)
  function revealSentence() {
    if (MARKED) each('.et-prompt .et-sent', function (el) { el.outerHTML = MARKED; });
  }

  function inlineFallback(st) {
    var fb = document.getElementById('et-fb');
    if (!fb) return;
    var kind = st.status === 'correct' ? 'ok' : st.status === 'recall' || st.status === 'self' ? 'skip' : st.status === 'skipped' ? 'skip' : 'bad';
    var title = st.status === 'correct' ? 'Верно' : st.status === 'recall' || st.status === 'self' ? 'Ответ' : 'Правильно: ' + esc(K.a[0]);
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

  function frontTyping(ex, notice, self) {
    ex.innerHTML = (notice || '') + typeHtml('', '', false, self);
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
      if (!C.clean(input.value)) {
        input.classList.remove('is-shake');
        void input.offsetWidth;
        input.classList.add('is-shake');
        input.focus();
        return;
      }
      lock();
      if (self) {   // a whole sentence: compared with a model by the user, not by string matching
        finish({ status: 'self', mode: 'type', given: input.value }, 200);
        return;
      }
      var r = C.checkTyped(input.value, K.accept, K.lang);
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
      if ((e.key === 'Enter' || e.keyCode === 13) && !(self && e.shiftKey)) { e.preventDefault(); e.stopPropagation(); check(); }
    });
    if (CFG.autoFocus !== false) setTimeout(function () { try { input.focus(); } catch (e) {} }, 60);
  }

  function frontRecall(ex) {
    saveResult({ status: 'recall', kind: 'recall', x: K.x && K.x.id, t: Date.now() });
    ex.innerHTML = recallHtml();
    ex.querySelector('[data-act="reveal"]').addEventListener('click', function () {
      if (answered) return;
      finish({ status: 'recall', mode: 'recall' }, 0);
    });
  }

  /* =================== BACK =================== */
  var graded = false;

  var autoPending = false;   // auto answer sent, the add-on is waiting for the audio
  function grade(st, ease, auto) {
    if (graded && !(autoPending && !auto)) return;   // a click while waiting answers at once
    var first = !graded;
    if (first && !PRACTICE) sessAdd(ease, st);
    graded = true;
    autoPending = !!auto;
    if (st) { st.graded = true; saveResult(st); }
    if (!auto) root.classList.add('is-leaving');
    if (first || !PRACTICE) sendGrade(ease, auto, st, !first);
  }

  /* ---------- the lesson report (owner's wife, 2026-11-28): per session, at the end of the lesson ----------
   * Every answer goes into a small log on this device (localStorage et-sess). A session = answers without a
   * pause longer than 30 min. On the last card of the lesson (Anki says nothing is left) the back side shows
   * the session: cards, correct, new words, time, the words with mistakes. Nothing is sent anywhere. */
  var CARD_NEW = false, SESS_GAP = 30 * 60 * 1000;
  function sessLoad() { try { return JSON.parse(localStorage.getItem('et-sess') || '[]') || []; } catch (e) { return []; } }
  function sessAdd(ease, st) {
    var log = sessLoad();
    var n = st && typeof st.n === 'boolean' ? st.n : CARD_NEW;
    log.push({ t: Date.now(), w: EN[0], e: ease, n: n ? 1 : 0, k: CTX ? 'c' : TO_EN ? 'r' : 'e' });
    try { localStorage.setItem('et-sess', JSON.stringify(log.slice(-400))); } catch (e) {}
  }
  function sessCurrent(extra) {
    var log = sessLoad().concat(extra ? [extra] : []), out = [];
    for (var i = log.length - 1; i >= 0; i--) {
      if (out.length && out[0].t - log[i].t > SESS_GAP) break;
      out.unshift(log[i]);
    }
    if (out.length && Date.now() - out[out.length - 1].t > SESS_GAP) return [];
    return out;
  }
  function remaining(cb) {
    if (window.ET_CARD && typeof window.ET_CARD.left === 'number') { cb(window.ET_CARD.left); return; }
    var api = host() === 'ankidroid' ? ankiDroid() : null;
    if (!api || typeof api.ankiGetNewCardCount !== 'function') { cb(null); return; }
    function val(r) { return r && typeof r === 'object' && 'value' in r ? r.value : r; }
    try {
      var p = [api.ankiGetNewCardCount(), api.ankiGetLrnCardCount(), api.ankiGetRevCardCount()];
      if (p[0] && typeof p[0].then === 'function') {
        Promise.all(p).then(function (r) { cb(+val(r[0]) + +val(r[1]) + +val(r[2])); }, function () { cb(null); });
      } else cb(+val(p[0]) + +val(p[1]) + +val(p[2]));
    } catch (e) { cb(null); }
  }
  function plural(n, one, few, many) {
    var m10 = n % 10, m100 = n % 100;
    return n + ' ' + (m10 === 1 && m100 !== 11 ? one : m10 >= 2 && m10 <= 4 && (m100 < 10 || m100 >= 20) ? few : many);
  }
  function reportHtml(xs) {
    if (!xs.length) return '';
    var ok = xs.filter(function (x) { return x.e >= 3; }).length;
    var words = {}, newW = {}, bad = {};
    xs.forEach(function (x) { words[x.w] = 1; if (x.n) newW[x.w] = 1; if (x.e < 3) bad[x.w] = 1; });
    var mins = Math.max(1, Math.round((xs[xs.length - 1].t - xs[0].t) / 60000));
    var best = 0, run = 0;
    xs.forEach(function (x) { run = x.e >= 3 ? run + 1 : 0; if (run > best) best = run; });
    var badList = Object.keys(bad);
    return '<section class="et-report et-in"><div class="et-report-title">Урок пройден — ура!</div>' +
      '<div class="et-report-grid">' +
      '<div><b>' + xs.length + '</b><span>' + plural(xs.length, 'карточка', 'карточки', 'карточек').replace(/^\d+ /, '') + '</span></div>' +
      '<div><b>' + Math.round(ok * 100 / xs.length) + '%</b><span>верно с первого раза</span></div>' +
      '<div><b>' + Object.keys(newW).length + '</b><span>новых слов</span></div>' +
      '<div><b>' + mins + '</b><span>мин</span></div>' +
      '</div>' +
      (best >= 3 ? '<div class="et-report-line">Лучшая серия: ' + plural(best, 'верный ответ', 'верных ответа', 'верных ответов') + ' подряд</div>' : '') +
      (badList.length ? '<div class="et-report-line">Повторить: ' + badList.slice(0, 12).map(esc).join(', ') +
        (badList.length > 12 ? ' и ещё ' + (badList.length - 12) : '') + '</div>'
        : '<div class="et-report-line">Без единой ошибки!</div>') +
      '</section>';
  }
  function showReportIfLast(st) {
    if (PRACTICE || !st || !(st.status === 'correct' || st.status === 'self' || st.status === 'recall')) return;
    remaining(function (left) {
      if (left === null || left > 1) return;
      var fb = root.querySelector('.et-fb');
      if (!fb || root.querySelector('.et-report')) return;
      var cur = st.graded ? null : { t: Date.now(), w: EN[0], e: 3, n: CARD_NEW ? 1 : 0 };
      fb.insertAdjacentHTML('afterbegin', reportHtml(sessCurrent(cur)));
    });
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

  function section(title, body, cls) {
    return '<section class="et-glass et-section et-in' + (cls ? ' ' + cls : '') + '">' + (title ? '<h4>' + title + '</h4>' : '') + body + '</section>';
  }
  // a real quote carries its source (x.s): "TED · Al Gore", "фильм · Title (1999)"…
  function srcLine(x) {
    return x && x.s ? '<div class="et-src">— ' + esc(x.s) + '</div>' : '';
  }
  function exampleRow(x) {
    return '<div class="et-example-row"><div class="et-example" lang="en">' + C.markTarget(x.en, x.t, EN) +
      (x.ru ? '<div class="et-example-ru" lang="ru">' + esc(x.ru) + '</div>' : '') + srcLine(x) + '</div>' + sayBtn(x.en) + '</div>';
  }
  // one more context, only on request (never all examples at once)
  function moreExamplesHtml(n) {
    var cur = K.x && K.x.id, others = XS.filter(function (x) { return x.id !== cur && C.findTarget(x.en, x.t, EN); });
    if (!others.length) return '';
    others = C.shuffle(others).slice(0, n || 2);
    return '<div class="et-reveals"><button type="button" class="et-reveal" data-reveal="more">Ещё пример</button></div>' +
      '<div class="et-hidden" data-for="more">' + others.map(exampleRow).join('') + '</div>';
  }

  // Wrong answer: write the correct word once — active recall instead of just reading it.
  function retryHtml() {
    var en = K.lang === 'en';
    return '<div class="et-glass et-type et-retry et-in">' +
      '<div class="et-retry-label">' + (en ? 'Напиши слово по-английски, чтобы запомнить'
        : 'Напиши перевод по-русски, чтобы запомнить') + '</div>' +
      '<input id="et-retry" class="et-input" type="text" lang="' + K.lang + '" autocomplete="off" autocorrect="off"' +
      ' autocapitalize="none" spellcheck="false" enterkeyhint="done" placeholder="' + (en ? 'по-английски…' : 'по-русски…') + '">' +
      '<div class="et-row">' +
        '<button type="button" class="et-btn et-btn-primary" data-act="retry">Проверить</button>' +
        '<button type="button" class="et-btn et-btn-ghost" data-ease="1">Пропустить</button>' +
      '</div></div>';
  }

  function detailsHtml(brief) {
    var h = '', x = K.x, kind = K.kind;
    var hint = D.hint ? section('Ассоциация', '<div class="et-expl">' + esc(D.hint) + '</div>') : '';
    var meaningCard = kind === 'meaning' || (!TO_EN && kind !== 'situation');
    var m = meaningOf(x);
    // what the word means (in this sentence, if it has several meanings)
    var sense = '';
    if (DATA && DATA.m.length > 1 && m) sense = '<div class="et-expl"><b>Здесь:</b> ' + esc(m.ru.join(' · ')) +
      (m.g ? ' <span class="et-muted">(' + esc(m.g) + ')</span>' : '') + '</div>';
    if (kind === 'contrast' && DATA && DATA.c.length) {
      h += section('Разница', DATA.c.map(function (c) {
        return '<div class="et-expl"><b lang="en">' + esc(c.en) + '</b>' + (c.ru ? ' — ' + esc(c.ru) : '') +
          (c.n ? '<div class="et-muted">' + esc(c.n) + '</div>' : '') + '</div>';
      }).join(''));
    }
    if (CTX || kind === 'situation' || kind === 'listen' || kind === 'meaning' || kind === 'contrast') {
      // the sentence is already on screen; show its translation (and the word's meaning)
      var tr = (x && x.ru ? '<div class="et-expl" lang="ru">' + esc(x.ru) + '</div>' : '') + srcLine(x) +
        '<div class="et-expl" lang="ru">' + (meaningCard ? '' : '<b lang="en">' + esc(EN[0]) + '</b> — ') + altsHtml(RU) + '</div>' + sense;
      if (brief) return section('Перевод', tr) + (HARD ? hint : '');
      h += section('Перевод', tr) + hint;
    } else {
      if (x) h += section(brief ? '' : 'Пример', exampleRow(x) + sense);
      if (brief) return h + (HARD ? hint : '');
      h += hint;
    }
    if (D.expl) h += section('Пояснение', '<div class="et-expl">' + D.expl + '</div>');
    return h + moreExamplesHtml(2);
  }

  function resHtml(kind, title, body) {
    return '<div class="et-res et-res-' + kind + ' et-in"><div class="et-res-head"><span class="et-res-ico">' + IC[kind] +
      '</span><span class="et-res-title">' + title + '</span>' +
      (K.lang === 'en' && !K.self ? '<span class="et-audio-slot et-audio-inline" id="et-audio-a"></span>' : '') +
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

  // own sentence / translation: show models, the user decides (an automatic check would either
  // reject good paraphrases or accept broken grammar)
  function selfCheckHtml(st) {
    var given = C.clean(st.given || ''), used = false;
    var forms = C.acceptFor(EN, (DATA && DATA.f) || [], K.target);
    forms.forEach(function (f) { if (C.findTarget(given, f, [f])) used = true; });
    if (!used && C.findTarget(given, '', EN)) used = true;
    var models = K.kind === 'produce' && K.x ? [K.x] : XS.filter(function (x) { return C.findTarget(x.en, x.t, EN); }).slice(0, 2);
    return resHtml('skip', K.kind === 'produce' ? 'Сравни с образцом' : 'Сравни с примерами',
      '<div class="et-expl"><span class="et-muted">Ты:</span> ' + esc(given || '—') + '</div>' +
      (given ? '<div class="et-expl ' + (used ? 'et-ok-note' : 'et-warn-note') + '">' +
        (used ? '✓ «' + esc(EN[0]) + '» есть в твоём ответе' : 'Нет «' + esc(EN[0]) + '» — проверь, использовано ли нужное слово') + '</div>' : '')) +
      section('Образец', models.map(exampleRow).join(''));
  }

  function renderBack() {
    var st = loadResult();
    var status = st ? st.status : 'none';
    if (st && st.graded) status = 'graded';
    K = setupKind(st && st.kind ? st.kind : PRACTICE ? PRACTICE.kind : TO_EN ? 'type' : 'choice', st && st.x, window.ET_CARD);
    var mode = K.kind;
    var answer = '<b>' + altsHtml(K.kind === 'produce' ? EN : K.a) + '</b>';
    var body = '', result = '', actions = '', primary = null, auto = false, retry = false, details = '', toggle = '';
    var token = ++BACK_TOKEN;   // a re-render (the auto switch) cancels the timers of the previous one

    if (st && st.opts && (mode === 'choice' || mode === 'meaning' || mode === 'contrast')) body = optionsHtml(st.opts, st.chosen);
    else if (st && st.mode === 'type') body = typeHtml(st.given, st.cls || '', true, K.self);

    if (status === 'self') {
      result = selfCheckHtml(st);
      primary = 3;
      actions = actionsHtml([{ ease: 1, label: 'Не вышло' }, { ease: 2, label: 'Почти' }, { ease: 3, label: 'Получилось', primary: true }]);
      details = (D.expl ? section('Пояснение', '<div class="et-expl">' + D.expl + '</div>') : '');
    } else if (status === 'correct') {
      result = resHtml('ok', 'Верно' + (st.mode === 'type' && K.a.length > 1 ? ' · ' + answer : ''));
      if (AUTO && host() && autoNext()) auto = true;
      else { primary = 3; actions = actionsHtml([{ ease: 3, label: 'Дальше', primary: true }]); }
      details = detailsHtml(true);
      if (AUTO && host()) toggle = '<button type="button" class="et-autotoggle" data-act="autotoggle">' +
        (auto ? 'Не листать самому — дочитать' : 'Листать самому после верного ответа') + '</button>';
    } else if (status === 'wrong' && st.near) {
      result = resHtml('warn', 'Похоже на опечатку', diffHtml(st.given, st.expected || K.a[0]));
      actions = actionsHtml([{ ease: 2, label: 'Засчитать', primary: true }, { ease: 1, label: 'Это ошибка' }]);
      details = detailsHtml(false);
    } else if (status === 'wrong' || status === 'skipped') {
      result = status === 'wrong'
        ? resHtml('bad', 'Правильно: ' + answer, st.mode === 'type' ? diffHtml(st.given, st.expected || K.a[0]) : '')
        : resHtml('skip', 'Ответ: ' + answer);
      primary = 1;
      if (RETRY && host() && !K.self) retry = true;
      else actions = actionsHtml([{ ease: 1, label: 'Дальше', primary: true }]);
      details = detailsHtml(false);
    } else {
      // recall, unknown state (e.g. preview) or already graded: show the answer, user decides
      result = resHtml('skip', answer);
      actions = actionsHtml([{ ease: 1, label: 'Не вспомнил' }, { ease: 3, label: 'Вспомнил', primary: true }]);
      details = detailsHtml(false);
    }

    if (auto) actions = '<div class="et-flip-hint">Нажми в любом месте, чтобы перейти сразу</div>';
    root.className += ' et-static';
    root.innerHTML = segHtml(mode) + promptHtml() + '<section class="et-ex">' + body + '</section>' +
      '<section class="et-fb">' + result + (retry ? retryHtml() : '') + details + actions + toggle + '</section>';
    mountAudio(TO_EN ? 'et-audio-a' : 'et-audio-q');
    bindReveals();
    bindSay();
    each('.et-seg button', function (b) { b.disabled = true; });
    showReportIfLast(st);
    // the sentence of this exercise aloud, after the word (Anki plays the word itself)
    if (K.x && status !== 'graded' && CFG.exampleAudio !== false && !QUIET) say(K.x.en);
    QUIET = false;

    each('[data-ease]', function (b) {
      b.addEventListener('click', function () { grade(st, +b.getAttribute('data-ease')); });
    });
    each('[data-act="autotoggle"]', function (b) {
      b.addEventListener('click', function (e) {
        e.stopPropagation();
        setAutoNext(!auto);
        QUIET = true;
        renderBack();   // the same answer, now with (or without) the automatic step (no audio replay)
      });
    });

    if (retry) {
      var inp = document.getElementById('et-retry');
      var check = function () {
        if (graded) return;
        var r = C.checkTyped(inp.value, K.accept, K.lang);
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
          // a Russian answer but Latin letters (or the other way round): say what is expected
          var lbl = root.querySelector('.et-retry-label');
          var latin = /[a-z]/i.test(inp.value) && !/[а-яё]/i.test(inp.value);
          var cyr = /[а-яё]/i.test(inp.value) && !/[a-z]/i.test(inp.value);
          if (lbl && ((K.lang === 'ru' && latin) || (K.lang === 'en' && cyr))) {
            lbl.textContent = K.lang === 'ru' ? 'Нужен перевод по-русски — переключи раскладку'
              : 'Нужно слово по-английски — переключи раскладку';
            lbl.classList.add('is-warn');
          }
        }
      };
      root.querySelector('[data-act="retry"]').addEventListener('click', check);
      inp.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.keyCode === 13) { e.preventDefault(); e.stopPropagation(); check(); }
      });
      setTimeout(function () { try { inp.focus({ preventScroll: true }); } catch (e) {} }, 60);
    }

    if (auto) {
      // Correct: let the result and the audio (word, then sentence) play, then Good in the background.
      var exWords = K.x && CAN_SAY ? K.x.en.split(/\s+/).length : 0;
      // Desktop with the add-on: it waits for the audio itself, so only the minimum pause here.
      var waitsForAudio = ADDON && !PRACTICE;
      var delay = waitsForAudio ? CORRECT_DELAY : Math.max(CORRECT_DELAY, exWords ? 1500 + exWords * 380 : 0);
      later(function () { if (token === BACK_TOKEN) grade(st, 3, waitsForAudio); }, delay);
      root.addEventListener('click', function (e) {
        if (token !== BACK_TOKEN) return;
        if (!e.target.closest || !e.target.closest('.replay-button, .et-reveal, .et-autotoggle')) grade(st, 3);
      });
    } else if (host() && !retry) {
      keyTrap(function (k) {
        if (/^[1-4]$/.test(k)) { grade(st, +k); return true; }
        if (k === 'Enter' || k === ' ') { if (primary) grade(st, primary); return true; }
        return false;
      });
    }
  }

  // Public deck only (window.ET_UPDATE is added by its build): where the add-on cannot update the deck
  // (phone, Anki without the add-on) the card checks the latest GitHub release once a day and, when it is
  // newer, shows one link to the new English_Trainer.apkg — opening it imports the update, progress stays.
  function verTuple(t) {
    return String(t || '').replace(/^v/i, '').split('.').map(function (p) { return parseInt(p, 10) || 0; });
  }
  function newer(a, b) {
    var x = verTuple(a), y = verTuple(b);
    for (var i = 0; i < Math.max(x.length, y.length); i++) {
      if ((x[i] || 0) !== (y[i] || 0)) return (x[i] || 0) > (y[i] || 0);
    }
    return false;
  }
  function updateBanner() {
    var U = window.ET_UPDATE;
    if (!U || !U.repo || ADDON || typeof fetch !== 'function') return;
    var day = new Date().toISOString().slice(0, 10), st = null;
    try { st = JSON.parse(localStorage.getItem('et-upd') || 'null'); } catch (e) { st = null; }
    function show(s) {
      // only this repo's release files (also re-checked for the cached state in localStorage)
      var prefix = 'https://github.com/' + U.repo + '/releases/download/';
      if (!s || String(s.url || '').indexOf(prefix) !== 0 || /[\s"'<>]/.test(s.url) || !newer(s.tag, U.version) ||
          document.getElementById('et-upd')) return;
      var a = document.createElement('a');
      a.id = 'et-upd';
      a.className = 'et-update';
      a.href = s.url;
      a.textContent = 'Вышла новая версия колоды ' + s.tag + ' — обновить (откроется файл: выбери Anki)';
      root.parentNode.appendChild(a);
    }
    if (st && st.day === day) { show(st); return; }
    fetch('https://api.github.com/repos/' + U.repo + '/releases/latest').then(function (r) {
      return r.ok ? r.json() : null;
    }).then(function (rel) {
      if (!rel) return;
      var url = '';
      var asset = 'English_Trainer' + (U.level ? '_' + U.level : '') + '.apkg';   // the same level as installed
      (rel.assets || []).forEach(function (a) { if (a.name === asset) url = a.browser_download_url; });
      var s = { day: day, tag: rel.tag_name || '', url: url };
      try { localStorage.setItem('et-upd', JSON.stringify(s)); } catch (e) {}
      show(s);
    })['catch'](function () {});
  }

  try {
    if (SIDE === 'back') renderBack();
    else renderFront();
  } catch (err) {
    root.innerHTML = '<div class="et-error">English Trainer: ошибка шаблона — ' + esc(err && err.message) + '</div>';
  }
  try { updateBanner(); } catch (e) {}
  try { levelLink(); } catch (e) {}
})();
