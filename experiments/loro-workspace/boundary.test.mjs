import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { mkdtempSync, readFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { AttributedText, decode } from './boundary.mjs';

const pythonRoot = fileURLToPath(new URL('../../python', import.meta.url));
function mark(text, state = 'ai', mode = 'vs') {
  const ran = spawnSync(process.env.TEXTPROV_PYTHON || 'python3', ['-c',
    'import json,sys; from textprov import mark; print(json.dumps(mark(*json.load(sys.stdin))))'], {
    input: JSON.stringify([text, state, mode]), encoding: 'utf8',
    env: { ...process.env, PYTHONPATH: pythonRoot },
  });
  assert.equal(ran.status, 0, ran.stderr);
  return JSON.parse(ran.stdout);
}
function body(t, source = '') {
  const value = new AttributedText(source);
  t.after(() => value.close());
  return value;
}
function states(value) { return value.tokens().map(t => [t.visible, t.state]); }

test('exact mixed Unicode round trip, including VS, PUA, whitespace and Markdown', t => {
  const source = '# Heading\r\n' + mark('Human e\u0301 👩🏽‍💻', 'human') + '\n' +
    mark('AI text') + mark('PUA!', 'ai', 'pua') + '\n`code` [link](https://example.test)\n';
  const value = body(t, source);
  assert.equal(value.portable(), source);
  assert.equal(value.copy(), source);
  assert.ok(value.tokens().some(t => t.state === null));
  const pasted = body(t, JSON.parse(JSON.stringify(value.copy())));
  assert.equal(pasted.portable(), source);
});

test('unmarked draft insertion never inherits AI at left, inside, or right', t => {
  for (const at of [0, 1, 2]) {
    const value = body(t, mark('AB'));
    value.replace(at, at, 'x');
    assert.deepEqual(states(value), [...'AB'.slice(0, at)].map(c => [c, 'ai'])
      .concat([['x', null]], [...'AB'.slice(at)].map(c => [c, 'ai'])));
  }
});

test('chat speaker defaults preserve pasted attribution in either direction', t => {
  for (const actor of ['human', 'assistant']) {
    const value = body(t);
    const pasted = mark('H', 'human') + mark('A') + 'x';
    value.replace(0, 0, pasted, { actor, destination: 'chat' });
    assert.deepEqual(states(value), [['H', 'human'], ['A', 'ai'], ['x', actor === 'human' ? 'human' : 'ai']]);
  }
});

test('human draft paste preserves marks but leaves new input unmarked', t => {
  const value = body(t, mark('AI'));
  const pasted = mark('H', 'human') + mark('A') + 'x';
  value.replace(1, 1, pasted);
  assert.equal(value.copy(1, 4), pasted);
  assert.deepEqual(states(value).slice(1, 4), [['H', 'human'], ['A', 'ai'], ['x', null]]);
});

test('AI replacement keeps original marks when proposed text omits them', t => {
  const original = mark('Human words.', 'human') + '\nEditor text.\nOld ending.\n';
  const value = body(t, original);
  value.replace(0, value.visible().length, 'Human words.\nEditor text.\nNew ending.\n', { actor: 'assistant' });
  assert.ok(value.portable().startsWith(mark('Human words.', 'human') + '\nEditor text.\n'));
  assert.ok(value.portable().endsWith(mark('New') + ' ending.\n'));
});

test('assistant edits honor full Markdown context, including fenced code', t => {
  const value = body(t, '# Title\n\n```js\nold\n```\n\nOld prose.');
  const at = value.visible().indexOf('old');
  value.replace(at, at + 3, 'new', { actor: 'assistant' });
  assert.ok(value.portable().includes('```js\nnew\n```'));
  const prose = value.visible().indexOf('Old prose.');
  value.replace(prose, prose + 10, 'New prose.', { actor: 'assistant' });
  assert.ok(value.portable().endsWith(mark('New') + ' prose.'));
});

test('undo and redo restore exact text and attribution as one edit', t => {
  const original = mark('Human', 'human') + ' editor ' + mark('AI');
  const value = body(t, original);
  value.replace(6, 12, 'changed', { actor: 'assistant' });
  const changed = value.portable();
  assert.notEqual(changed, original);
  assert.equal(value.undo(), true);
  assert.equal(value.portable(), original);
  assert.equal(value.redo(), true);
  assert.equal(value.portable(), changed);
  value.replace(0, 0, 'x');
  value.undo();
  assert.equal(value.portable(), changed);
});

test('selections reject split surrogate, emoji, combining sequence and CRLF', t => {
  const value = body(t, 'e\u0301👩🏽‍💻\r\n');
  const original = value.portable();
  for (const at of [1, 3, 4, value.visible().length - 1, -1, 100, 0.5]) {
    assert.throws(() => value.replace(at, at, 'x'), /grapheme/);
    assert.throws(() => value.copy(0, at), /grapheme/);
    assert.equal(value.portable(), original);
  }
});

test('invalid actors, unsupported and conflicting encodings fail before edits', t => {
  const value = body(t, mark('keep'));
  const before = value.portable();
  for (const bad of ['x\u{E0102}', '\u{E0101}', 'x\u{E0100}\u{E0101}', '\u{100100}', '\ud800']) {
    assert.throws(() => value.replace(0, 0, bad));
    assert.equal(value.portable(), before);
  }
  assert.throws(() => value.replace(0, 0, 'x', { actor: 'robot' }), /actor/);
  assert.throws(() => value.replace(0, 0, 'x', { destination: 'other' }), /destination/);
  assert.equal(value.portable(), before);
});

test('tampered span metadata refuses export instead of guessing attribution', t => {
  const value = body(t, mark('A'));
  value.text.insert(1, 'x');
  value.doc.commit();
  assert.throws(() => value.portable(), /metadata|boundaries/);
});

test('plain editor and JSON round trips retain exact encoding and new unmarked text', t => {
  const value = body(t, mark('H', 'human') + mark('A', 'ai', 'pua'));
  const dir = mkdtempSync(join(tmpdir(), 'textprov-loro-'));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  const file = join(dir, 'draft.md');
  writeFileSync(file, JSON.parse(JSON.stringify(value.copy())), 'utf8');
  const edited = readFileSync(file, 'utf8') + ' new';
  writeFileSync(file, edited, 'utf8');
  const reimported = body(t, edited);
  assert.equal(reimported.portable(), edited);
  assert.ok(reimported.tokens().slice(-4).every(t => t.state === null));
  assert.deepEqual(decode(value.portable()), value.tokens());
});

test('an insertion that joins an existing grapheme is refused without mutation', t => {
  const value = body(t, mark('A'));
  const original = value.portable();
  assert.throws(() => value.replace(1, 1, '\u0301'));
  assert.equal(value.portable(), original);
  assert.equal(value.history.canUndo(), false);
});

test('deletion and mixed pasted replacement undo without reclassifying retained text', t => {
  const original = mark('HH', 'human') + ' xx ' + mark('AA');
  const value = body(t, original);
  value.replace(2, 6, '');
  assert.equal(value.portable(), mark('HH', 'human') + mark('AA'));
  value.undo();
  assert.equal(value.portable(), original);
  const pasted = mark('P', 'human') + mark('Q', 'ai', 'pua') + 'r';
  value.replace(3, 5, pasted);
  assert.equal(value.copy(3, 6), pasted);
  value.undo();
  assert.equal(value.portable(), original);
});
