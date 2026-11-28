/* English Trainer for Anki — card logic.
 * Plain ES5, no dependencies, no AnkiDroid/Anki collection APIs.
 * Scheduling is never touched: grading is done with Anki's own buttons.
 */
var ETCore = (function () {
  'use strict';

  function clean(s) {
    return String(s == null ? '' : s).replace(/\u00a0/g, ' ').replace(/\s+/g, ' ').trim();
  }

  // "<br>", block tags, newlines, ";" and "|" all separate list items.
  function brToSep(html) {
    return String(html || '')
      .replace(/<br\s*\/?>/gi, ';')
      .replace(/<\/(div|p|li)>/gi, ';');
  }

  function splitText(s) {
    var out = [];
    String(s || '').split(/[;\n|]/).forEach(function (p) {
      p = clean(p);
      if (p) out.push(p);
    });
    return out;
  }

  // Normalisation for comparing answers: case, ё/е, quotes, punctuation, spaces.
  // For English a leading "to"/article is optional ("to come up with" == "come up with").
  function norm(s, lang) {
    s = clean(s).toLowerCase()
      .replace(/ё/g, 'е')
      .replace(/[\u2019\u2018`\u00b4]/g, "'")
      .replace(/[\u201c\u201d\u00ab\u00bb"]/g, '')
      .replace(/[.,!?;:()\[\]\u2026]/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();
    if (lang === 'en') s = s.replace(/^(to|a|an|the) /, '');
    return s;
  }

  function lev(a, b) {
    var m = a.length, n = b.length, i, j, prev, cur;
    if (!m) return n;
    if (!n) return m;
    prev = [];
    for (j = 0; j <= n; j++) prev[j] = j;
    for (i = 1; i <= m; i++) {
      cur = [i];
      for (j = 1; j <= n; j++) {
        cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
      }
      prev = cur;
    }
    return prev[n];
  }

  function shuffle(arr, rnd) {
    rnd = rnd || Math.random;
    var a = arr.slice(), i, j, t;
    for (i = a.length - 1; i > 0; i--) {
      j = Math.floor(rnd() * (i + 1));
      t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  // One correct answer + up to (max-1) unique distractors. Never pads with junk:
  // if there are fewer good distractors, fewer buttons are shown.
  function buildOptions(answers, wrongs, lang, max, rnd) {
    max = max || 4;
    var seen = {}, pool = [], opts;
    answers.forEach(function (a) { seen[norm(a, lang)] = 1; });
    wrongs.forEach(function (w) {
      var k = norm(w, lang);
      if (!k || seen[k]) return;
      seen[k] = 1;
      pool.push(w);
    });
    pool = shuffle(pool, rnd).slice(0, max - 1);
    opts = [{ text: answers[0], ok: true }];
    pool.forEach(function (w) { opts.push({ text: w, ok: false }); });
    return shuffle(opts, rnd);
  }

  function checkTyped(input, answers, lang) {
    var n = norm(input, lang), best = answers[0], bestD = Infinity, i, k, d;
    if (!n) return { status: 'empty' };
    for (i = 0; i < answers.length; i++) {
      k = norm(answers[i], lang);
      if (k === n) return { status: 'correct', expected: answers[i] };
      d = lev(n, k);
      if (d < bestD) { bestD = d; best = answers[i]; }
    }
    var len = norm(best, lang).length;
    return { status: 'wrong', expected: best, distance: bestD, near: bestD <= (len >= 8 ? 2 : 1) };
  }

  // Character diff (LCS). Returns arrays of [char, matched] for typed and expected.
  function diff(a, b) {
    a = clean(a); b = clean(b);
    var A = a.split(''), B = b.split(''), n = A.length, m = B.length, i, j, dp = [];
    function key(c) { return c.toLowerCase().replace('ё', 'е'); }
    for (i = 0; i <= n; i++) { dp[i] = []; for (j = 0; j <= m; j++) dp[i][j] = 0; }
    for (i = n - 1; i >= 0; i--) {
      for (j = m - 1; j >= 0; j--) {
        dp[i][j] = key(A[i]) === key(B[j]) ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
      }
    }
    var ta = [], tb = [];
    i = 0; j = 0;
    while (i < n && j < m) {
      if (key(A[i]) === key(B[j])) { ta.push([A[i], 1]); tb.push([B[j], 1]); i++; j++; }
      else if (dp[i + 1][j] >= dp[i][j + 1]) { ta.push([A[i], 0]); i++; }
      else { tb.push([B[j], 0]); j++; }
    }
    while (i < n) ta.push([A[i++], 0]);
    while (j < m) tb.push([B[j++], 0]);
    return { typed: ta, expected: tb };
  }

  function escRe(s) { return s.replace(/[.*+?^$()|[\]\\]/g, '\\$&').replace(/[{}]/g, '\\$&'); }

  // Regex that finds the target English word/phrase (with simple inflections) in an example.
  function targetRegex(answers) {
    var parts = [];
    answers.forEach(function (a) {
      norm(a, 'en').split(' ').forEach(function (w) {
        if (!w || /^(a|an|the|to|sb|sth|smb|smth|someone|something|one's)$/.test(w)) return;
        var r;
        if (w.length >= 4 && /e$/.test(w)) r = escRe(w.slice(0, -1)) + '(?:e|es|ed|ing|er)';
        else if (w.length >= 3) r = escRe(w) + '(?:s|es|ed|d|ing|ly|er|est)?';
        else r = escRe(w);
        if (parts.indexOf(r) < 0) parts.push(r);
      });
    });
    if (!parts.length) return null;
    return new RegExp('\\b(?:' + parts.join('|') + ')\\b', 'gi');
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function maskExample(text, answers) {
    var re = targetRegex(answers), h = esc(text);
    return re ? h.replace(re, '<span class="et-mask"></span>') : h;
  }

  function highlightExample(text, answers) {
    var re = targetRegex(answers), h = esc(text);
    return re ? h.replace(re, '<mark>$&</mark>') : h;
  }

  /* ================= Vocabulary Unit (hidden "Data" field, see units.py) ================= */

  // {m: meanings, x: examples, f: forms, c: contrast, d: definition} or null for old notes
  function parseData(text) {
    var d;
    try { d = JSON.parse(clean(text) || 'null'); } catch (e) { return null; }
    if (!d || typeof d !== 'object') return null;
    d.m = d.m || []; d.x = d.x || []; d.f = d.f || []; d.c = d.c || [];
    return d;
  }

  // The exact words to hide in a sentence: the stored target if it is really there,
  // otherwise whatever the inflection regex finds (old single-example notes).
  function findTarget(sentence, target, answers) {
    if (target) {
      var re = new RegExp("(^|[^A-Za-z'])(" + escRe(target) + ')(?![A-Za-z])', 'i'), m = re.exec(sentence);
      if (m) return { start: m.index + m[1].length, text: m[2] };
    }
    var rx = targetRegex(answers || []);
    if (!rx) return null;
    var all = [], mm;
    rx.lastIndex = 0;
    while ((mm = rx.exec(sentence))) all.push({ start: mm.index, text: mm[0] });
    if (!all.length) return null;
    var last = all[all.length - 1];   // phrasal verbs: hide the whole span "came ... across"
    return { start: all[0].start, text: sentence.slice(all[0].start, last.start + last.text.length), parts: all };
  }

  function maskTarget(sentence, target, answers) {
    var t = findTarget(sentence, target, answers);
    if (!t) return esc(sentence);
    if (t.parts && t.parts.length > 1) return maskExample(sentence, answers);
    return esc(sentence.slice(0, t.start)) + '<span class="et-mask"></span>' + esc(sentence.slice(t.start + t.text.length));
  }

  function markTarget(sentence, target, answers) {
    var t = findTarget(sentence, target, answers);
    if (!t) return esc(sentence);
    if (t.parts && t.parts.length > 1) return highlightExample(sentence, answers);
    return esc(sentence.slice(0, t.start)) + '<mark>' + esc(t.text) + '</mark>' + esc(sentence.slice(t.start + t.text.length));
  }

  /* Pick an example for this showing.
   * - never the one shown last time (opts.last: id or list of ids) when there is another one;
   * - prefer examples that failed before (opts.weak), then ones not seen yet (opts.seen);
   * - opts.need: 'ru' (needs a translation), 't' (needs the target in the sentence);
   * - opts.meaning: only this meaning. */
  function pickExample(xs, opts, rnd) {
    rnd = rnd || Math.random;
    opts = opts || {};
    var last = [].concat(opts.last || []), weak = opts.weak || [], seen = opts.seen || [];
    var pool = xs.filter(function (x) {
      if (!x || !x.en) return false;
      if (opts.need === 'ru' && !x.ru) return false;
      if (opts.meaning && x.m && x.m !== opts.meaning) return false;
      return true;
    });
    if (!pool.length) return null;
    var fresh = pool.filter(function (x) { return last.indexOf(x.id) < 0; });
    if (fresh.length) pool = fresh;
    var w = pool.filter(function (x) { return weak.indexOf(x.id) >= 0; });
    if (w.length && rnd() < 0.7) pool = w;
    else {
      var u = pool.filter(function (x) { return seen.indexOf(x.id) < 0; });
      if (u.length) pool = u;
    }
    // easiest first (x.d from tools/coverage.py: 10 per word not in the deck + 1 per deck word learnt later):
    // a sentence where only the studied word is new comes before one full of unknown words
    var dmin = Infinity;
    pool.forEach(function (x) { if (typeof x.d === 'number' && x.d < dmin) dmin = x.d; });
    if (dmin < Infinity) pool = pool.filter(function (x) { return typeof x.d !== 'number' || x.d === dmin; });
    return pool[Math.floor(rnd() * pool.length)];
  }

  // Typed answers accepted for a gap: dictionary forms + listed forms + the form in this sentence.
  function acceptFor(answers, forms, inSentence) {
    var out = answers.slice();
    (forms || []).concat(inSentence ? [inSentence] : []).forEach(function (f) {
      if (f && out.map(function (a) { return norm(a, 'en'); }).indexOf(norm(f, 'en')) < 0) out.push(f);
    });
    return out;
  }

  // "What does it mean here?": the right meaning + other meanings of the same word + wrong options.
  function meaningOptions(data, meaningId, wrongRu, rnd) {
    var right = null, others = [];
    (data.m || []).forEach(function (m) {
      if (!m.ru || !m.ru.length) return;
      if (m.id === meaningId) right = m.ru[0]; else others.push(m.ru[0]);
    });
    if (!right) return null;
    return buildOptions([right], others.concat(shuffle(wrongRu || [], rnd)), 'ru', 4, rnd);
  }

  /* Which exercise this card shows (mode "auto").
   *   dir:  'ru-en' (retrieval), 'en-ru' (meaning), 'ctx' (recognition in context)
   *   info: {type, ivl} of the card (Anki); info.m: skills from the add-on {meaning|retrieval|recognition|production: 'weak'|'ok'|'strong'}
   *   caps: {ru: examples with a translation, t: examples with the target, c: contrast items, listen: can play any sentence}
   * The card's own interval sets the ladder; a weak skill (from all three cards' history) can borrow the turn. */
  function pickKind(dir, info, caps, rnd) {
    rnd = rnd || Math.random;
    caps = caps || {};
    var ivl = info && info.type === 2 ? info.ivl : -1;   // -1: new / learning / relearning
    var M = (info && info.m) || {}, r = rnd();
    if (ivl >= 4) {
      if (M.meaning === 'weak' && dir !== 'en-ru' && caps.t && r < 0.5) return 'meaning';
      if (M.retrieval === 'weak' && dir === 'en-ru' && caps.ru && r < 0.5) return 'situation';
      if (M.recognition === 'weak' && dir === 'ru-en' && caps.t && r < 0.4) return 'meaning';
      r = rnd();
    }
    if (dir === 'ru-en') {
      if (ivl < 4) return 'choice';
      if (ivl < 21) return caps.ru && r < 0.5 ? 'situation' : 'type';
      if (ivl >= 60 && r < 0.15) return 'sentence';
      if (caps.ru && r < 0.5) return 'situation';
      if (caps.ru && r < 0.7) return 'produce';
      return 'type';
    }
    if (dir === 'en-ru') {
      if (ivl < 0) return 'choice';
      if (ivl < 21) return caps.t && r < (ivl < 4 ? 0.4 : 0.5) ? 'meaning' : 'choice';
      return caps.t && r < 0.5 ? 'meaning' : 'type';
    }
    // ctx
    if (ivl < 4) return 'choice';
    if (ivl < 21) return caps.c && r < 0.25 ? 'contrast' : 'type';
    if (caps.listen && r < 0.2) return 'listen';
    if (caps.c && r < 0.4) return 'contrast';
    return 'type';
  }

  return {
    clean: clean, brToSep: brToSep, splitText: splitText, norm: norm, lev: lev,
    shuffle: shuffle, buildOptions: buildOptions, checkTyped: checkTyped, diff: diff,
    targetRegex: targetRegex, esc: esc, maskExample: maskExample, highlightExample: highlightExample,
    parseData: parseData, findTarget: findTarget, maskTarget: maskTarget, markTarget: markTarget,
    pickExample: pickExample, acceptFor: acceptFor, meaningOptions: meaningOptions, pickKind: pickKind
  };
})();

if (typeof module !== 'undefined' && module.exports) module.exports = ETCore;

