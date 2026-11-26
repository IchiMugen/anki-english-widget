// node tests/test_core.js
var assert = require('assert');
var C = require('../src/core.js');

var n = 0;
function t(name, fn) { fn(); n++; console.log('ok -', name); }

t('norm: case, spaces, punctuation, ё', function () {
  assert.strictEqual(C.norm('  Жёсткий!  ', 'ru'), 'жесткий');
  assert.strictEqual(C.norm('Come   UP with.', 'en'), 'come up with');
  assert.strictEqual(C.norm('to come up with', 'en'), 'come up with');
  assert.strictEqual(C.norm('don’t', 'en'), "don't");
});

t('checkTyped: correct ignoring case/spaces/"to"', function () {
  assert.strictEqual(C.checkTyped('  Come up  with ', ['to come up with'], 'en').status, 'correct');
  assert.strictEqual(C.checkTyped('RELUCTANT', ['reluctant'], 'en').status, 'correct');
});

t('checkTyped: any Russian alternative is accepted', function () {
  assert.strictEqual(C.checkTyped('понять', ['разобраться', 'понять', 'выяснить'], 'ru').status, 'correct');
  assert.strictEqual(C.checkTyped('жесткий', ['жёсткий'], 'ru').status, 'correct');
});

t('checkTyped: similar text is NOT accepted, but flagged as near', function () {
  var r = C.checkTyped('reluctent', ['reluctant'], 'en');
  assert.strictEqual(r.status, 'wrong');
  assert.strictEqual(r.near, true);
  var r2 = C.checkTyped('relevant', ['reluctant'], 'en');
  assert.strictEqual(r2.status, 'wrong');
  assert.strictEqual(r2.near, false);
});

t('checkTyped: empty input', function () {
  assert.strictEqual(C.checkTyped('   ', ['x'], 'en').status, 'empty');
});

t('buildOptions: 4 unique, exactly one correct, no copies of answer', function () {
  for (var k = 0; k < 200; k++) {
    var o = C.buildOptions(['reluctant'], ['relevant', 'Relevant ', 'reluctant', 'resilient', 'redundant', 'robust'], 'en');
    assert.strictEqual(o.length, 4);
    assert.strictEqual(o.filter(function (x) { return x.ok; }).length, 1);
    var keys = o.map(function (x) { return C.norm(x.text, 'en'); });
    assert.strictEqual(new Set(keys).size, 4);
  }
});

t('buildOptions: does not pad when few distractors', function () {
  assert.strictEqual(C.buildOptions(['a1'], ['b1'], 'en').length, 2);
  assert.strictEqual(C.buildOptions(['a1'], [], 'en').length, 1);
  assert.strictEqual(C.buildOptions(['понять', 'разобраться'], ['разобраться', 'узнать'], 'ru').length, 2);
});

t('buildOptions: shuffles positions', function () {
  var pos = {};
  for (var k = 0; k < 400; k++) {
    var o = C.buildOptions(['A'], ['B', 'C', 'D'], 'en');
    pos[o.findIndex(function (x) { return x.ok; })] = 1;
  }
  assert.strictEqual(Object.keys(pos).length, 4);
});

t('diff marks extra and missing chars', function () {
  var d = C.diff('reluctent', 'reluctant');
  var bad = d.typed.filter(function (c) { return !c[1]; }).map(function (c) { return c[0]; }).join('');
  var miss = d.expected.filter(function (c) { return !c[1]; }).map(function (c) { return c[0]; }).join('');
  assert.strictEqual(bad, 'e');
  assert.strictEqual(miss, 'a');
});

t('maskExample hides the target word and its forms', function () {
  var m = C.maskExample('She was reluctant to admit it.', ['reluctant']);
  assert.ok(m.indexOf('reluctant') < 0 && m.indexOf('et-mask') > 0);
  var m2 = C.maskExample('We need to come up with a better plan.', ['to come up with']);
  assert.ok(!/come|with/.test(m2.replace(/<[^>]+>/g, '')));
  assert.ok(/need to/.test(m2), 'unrelated "to" stays');
  var m3 = C.maskExample('Let me figure it out.', ['to figure out']);
  assert.ok(!/figure|out/.test(m3.replace(/<[^>]+>/g, '')));
});

t('splitText / brToSep', function () {
  assert.deepStrictEqual(C.splitText(C.brToSep('a<br>b; c | d')), ['a', 'b', 'c', 'd']);
});

t('esc prevents HTML injection in option text', function () {
  assert.strictEqual(C.esc('<b>"x"</b>'), '&lt;b&gt;&quot;x&quot;&lt;/b&gt;');
});

t('context card: the form used in the sentence is accepted', function () {
  var rx = C.targetRegex(['to look for']);
  var surface = "I'm looking for my glasses.".match(rx).join(' ');
  assert.strictEqual(surface, 'looking for');
  assert.strictEqual(C.checkTyped('looking for', ['to look for', surface], 'en').status, 'correct');
  assert.strictEqual(C.checkTyped('look for', ['to look for', surface], 'en').status, 'correct');
});

/* ---------- v2: Vocabulary Units ---------- */
function seq(vals) { var i = 0; return function () { var v = vals[i % vals.length]; i++; return v; }; }
var UNIT = C.parseData(JSON.stringify({ v: 1,
  m: [{ id: 'm1', ru: ['наткнуться'] }, { id: 'm2', ru: ['производить впечатление'] }],
  x: [{ id: 'e1', en: 'I came across an old photo.', ru: 'Я наткнулся на старое фото.', t: 'came across', m: 'm1' },
      { id: 'e2', en: 'He comes across as rude.', ru: 'Он кажется грубым.', t: 'comes across', m: 'm2' },
      { id: 'e3', en: 'Have you come across this word?', ru: '', t: 'come across', m: 'm1' }],
  f: ['came across', 'comes across', 'come across'], c: [{ en: 'run into', ru: 'встретить' }] }));

t('parseData: bad or empty field -> null, lists always present', function () {
  assert.strictEqual(C.parseData(''), null);
  assert.strictEqual(C.parseData('{oops'), null);
  var d = C.parseData('{"v":1}');
  assert.deepStrictEqual([d.m, d.x, d.f, d.c], [[], [], [], []]);
});

t('findTarget / maskTarget: exact form, whole phrase hidden, no particle left as a hint', function () {
  var t1 = C.findTarget('She came across some useful information.', 'came across', ['to come across']);
  assert.strictEqual(t1.text, 'came across');
  var masked = C.maskTarget('She came across some useful information.', 'came across', ['to come across']);
  assert.ok(masked.indexOf('across') < 0 && masked.indexOf('came') < 0, masked);
  // the target must be a whole word: "act" is not found inside "actually"
  assert.strictEqual(C.findTarget('I actually agree.', 'act', ['to act']), null);
});

t('maskTarget: old notes without a stored target fall back to inflection matching', function () {
  var m = C.maskTarget('He gave up smoking.', '', ['to give up']);
  assert.ok(m.indexOf(' up') < 0, m);
});

t('pickExample: never the last shown, prefers weak ones, respects "needs translation"', function () {
  for (var i = 0; i < 20; i++) assert.notStrictEqual(C.pickExample(UNIT.x, { last: ['e1'] }).id, 'e1');
  assert.strictEqual(C.pickExample(UNIT.x, { last: [], weak: ['e3'] }, seq([0.1, 0.5])).id, 'e3');
  for (var j = 0; j < 20; j++) assert.notStrictEqual(C.pickExample(UNIT.x, { need: 'ru' }).id, 'e3');
  // only one example: it is shown even if it was the last one
  assert.strictEqual(C.pickExample([UNIT.x[0]], { last: ['e1'] }).id, 'e1');
});

t('acceptFor: dictionary form, listed forms and the form in the sentence are accepted', function () {
  var acc = C.acceptFor(['to come across'], UNIT.f, 'came across');
  ['come across', 'came across', 'comes across', 'to come across'].forEach(function (w) {
    assert.strictEqual(C.checkTyped(w, acc, 'en').status, 'correct', w);
  });
  assert.strictEqual(C.checkTyped('come over', acc, 'en').status, 'wrong');
  assert.strictEqual(C.checkTyped('across', acc, 'en').status, 'wrong');
});

t('meaningOptions: the meaning of THIS sentence is right, the other meaning is a distractor', function () {
  var o = C.meaningOptions(UNIT, 'm2', ['отменить', 'терпеть']);
  var right = o.filter(function (x) { return x.ok; });
  assert.strictEqual(right.length, 1);
  assert.strictEqual(right[0].text, 'производить впечатление');
  assert.ok(o.some(function (x) { return x.text === 'наткнуться' && !x.ok; }));
});

t('pickKind: the ladder follows the card interval; new words always start with choice', function () {
  var caps = { ru: true, t: true, c: true, listen: true };
  ['ru-en', 'en-ru', 'ctx'].forEach(function (d) {
    assert.strictEqual(C.pickKind(d, { type: 0, ivl: 0 }, caps, seq([0.9])), 'choice');
    assert.strictEqual(C.pickKind(d, null, caps, seq([0.9])), 'choice');
  });
  assert.strictEqual(C.pickKind('ru-en', { type: 2, ivl: 10 }, caps, seq([0.9])), 'type');
  assert.strictEqual(C.pickKind('ru-en', { type: 2, ivl: 10 }, caps, seq([0.1])), 'situation');
  assert.strictEqual(C.pickKind('en-ru', { type: 2, ivl: 30 }, caps, seq([0.9])), 'type');
  assert.strictEqual(C.pickKind('ctx', { type: 2, ivl: 30 }, caps, seq([0.1])), 'listen');
  assert.strictEqual(C.pickKind('ru-en', { type: 2, ivl: 90 }, caps, seq([0.1])), 'sentence');
  // nothing to build an exercise from: plain typing
  assert.strictEqual(C.pickKind('ru-en', { type: 2, ivl: 30 }, {}, seq([0.1])), 'type');
});

t('pickKind: a weak skill borrows the turn (adaptive), a relearning card does not', function () {
  var caps = { ru: true, t: true };
  assert.strictEqual(C.pickKind('ctx', { type: 2, ivl: 10, m: { meaning: 'weak' } }, caps, seq([0.1])), 'meaning');
  assert.strictEqual(C.pickKind('en-ru', { type: 2, ivl: 10, m: { retrieval: 'weak' } }, caps, seq([0.1])), 'situation');
  assert.strictEqual(C.pickKind('ctx', { type: 3, ivl: 10, m: { meaning: 'weak' } }, caps, seq([0.1])), 'choice');
});

console.log('\n' + n + ' tests passed');
