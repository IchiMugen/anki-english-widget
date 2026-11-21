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

  return {
    clean: clean, brToSep: brToSep, splitText: splitText, norm: norm, lev: lev,
    shuffle: shuffle, buildOptions: buildOptions, checkTyped: checkTyped, diff: diff,
    targetRegex: targetRegex, esc: esc, maskExample: maskExample, highlightExample: highlightExample
  };
})();

if (typeof module !== 'undefined' && module.exports) module.exports = ETCore;

