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

console.log('\n' + n + ' tests passed');
