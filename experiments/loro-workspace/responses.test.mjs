import test from 'node:test';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';
import { AttributedText, decode } from './boundary.mjs';
import { ResponseAttempts } from './responses.mjs';

function replica() {
  const body = new AttributedText('A draft.');
  return { body, header: { id: 'draft-1' }, portable: () => body.portable(),
    checkpoint: () => ({ snapshot: body.doc.export({ mode: 'snapshot' }), pending: body.doc.exportPendingUpdates() }),
    version: () => { const v = body.doc.version(); try { return v.encode(); } finally { v.free(); } },
    sources: () => [{ observationId: 'fixture-observation', portable: 'A draft.' }],
    inspect: () => ({ reviewHash: createHash('sha256').update(body.portable(), 'utf8').digest('hex') }),
  };
}

function fixture(t) {
  const r = replica(); t.after(() => r.body.close());
  return r;
}

test('response pins exact context and human prompt while draft changes remain separate', t => {
  const r = fixture(t), responses = new ResponseAttempts();
  const first = responses.start(r, { prompt: 'Please summarize.' });
  const context = structuredClone(first.context);
  assert.equal(responses.contextChanged(first.id, r), false);
  assert.ok(decode(first.prompt).some(token => token.state === 'human'));
  r.body.replace(0, 0, 'Edited ');
  assert.equal(responses.contextChanged(first.id, r), true);
  responses.appendChunk(first.id, 0, 'An answer.');
  const complete = responses.finish(first.id);
  assert.deepEqual(complete.context, context);
  assert.equal(complete.status, 'completed');
  assert.equal(complete.text, 'An answer.');
  assert.ok(complete.tokens.filter(token => token.visible.trim()).every(token => token.state === 'ai'));
  assert.equal(r.body.visible(), 'Edited A draft.');
  complete.context.portable = 'tampered';
  assert.equal(responses.inspect(first.id).context.portable, 'A draft.');
});

test('split surrogate, combining sequence and provenance selector join before publication', t => {
  const r = fixture(t), responses = new ResponseAttempts(), first = responses.start(r);
  responses.appendChunk(first.id, 0, 'a');
  assert.equal(responses.inspect(first.id).text, '');
  responses.appendChunk(first.id, 1, '\u0301 ');
  responses.appendChunk(first.id, 2, '\uD83D');
  responses.appendChunk(first.id, 3, '\uDE00 H\uDB40');
  responses.appendChunk(first.id, 4, '\uDD00'); // U+E0100: existing recorded-human mark.
  const completed = responses.finish(first.id);
  assert.equal(completed.text, 'a\u0301 😀 H');
  assert.equal(completed.tokens.find(token => token.visible === 'a\u0301').state, 'ai');
  assert.equal(completed.tokens.find(token => token.visible === 'H').state, 'human');
});

test('cancellation flushes accepted text, refuses late chunks and preserves alternatives', t => {
  const r = fixture(t), responses = new ResponseAttempts(), first = responses.start(r, { prompt: 'Question' });
  responses.appendChunk(first.id, 0, 'Partial');
  const stopped = responses.cancel(first.id);
  assert.equal(stopped.text, 'Partial');
  assert.equal(stopped.status, 'cancelled');
  const before = responses.snapshot();
  assert.throws(() => responses.appendChunk(first.id, 1, ' late'), /no longer streaming/);
  assert.deepEqual(responses.snapshot(), before);
  r.body.replace(0, 0, 'New ');
  const next = responses.regenerate(first.id);
  assert.deepEqual(next.context, first.context);
  assert.equal(next.parentId, first.id); assert.equal(next.rootId, first.id);
  const current = responses.regenerate(first.id, { replica: r, useCurrentContext: true });
  assert.equal(current.context.portable, 'New A draft.');
  assert.equal(responses.inspect(first.id).portable, stopped.portable);
});

test('sequence errors and malformed input do not advance or replace the response', t => {
  const r = fixture(t), responses = new ResponseAttempts(), first = responses.start(r);
  responses.appendChunk(first.id, 0, 'safe ');
  const saved = responses.snapshot();
  assert.throws(() => responses.appendChunk(first.id, 0, 'duplicate'), /out of order/);
  assert.throws(() => responses.appendChunk(first.id, 2, 'missing'), /out of order/);
  assert.throws(() => responses.appendChunk(first.id, 1, '\uDC00'), /surrogate/);
  assert.deepEqual(responses.snapshot(), saved);
  assert.equal(responses.fail(first.id, 'fixture failure').status, 'failed');
});

test('restart interrupts streaming without losing portable marks, pending text or context', t => {
  const r = fixture(t), responses = new ResponseAttempts();
  const complete = responses.start(r); responses.appendChunk(complete.id, 0, 'Complete'); responses.finish(complete.id);
  const streaming = responses.start(r); responses.appendChunk(streaming.id, 0, 'Pending\uD83D');
  const before = responses.inspect(streaming.id);
  const candidate = responses.clone();
  assert.equal(candidate.inspect(streaming.id).status, 'streaming');
  candidate.cancel(streaming.id);
  assert.equal(responses.inspect(streaming.id).status, 'streaming');
  const restored = new ResponseAttempts(JSON.parse(JSON.stringify(responses.snapshot())));
  const interrupted = restored.inspect(streaming.id);
  assert.equal(interrupted.status, 'interrupted');
  assert.equal(interrupted.portable, before.portable);
  assert.equal(interrupted.pendingText, before.pendingText);
  assert.deepEqual(interrupted.context, before.context);
  assert.equal(restored.inspect(complete.id).status, 'completed');
  assert.throws(() => restored.appendChunk(streaming.id, 1, '\uDE00'), /no longer streaming/);
  const malformed = responses.snapshot(); malformed.attempts[0].context.portable = 'wrong';
  assert.throws(() => new ResponseAttempts(malformed), /context/);
});

test('incomplete terminal surrogate cannot complete and cancellation retains its pending evidence', t => {
  const r = fixture(t), responses = new ResponseAttempts(), first = responses.start(r);
  responses.appendChunk(first.id, 0, 'Accepted\uD83D');
  assert.throws(() => responses.finish(first.id), /incomplete/);
  const cancelled = responses.cancel(first.id);
  assert.equal(cancelled.text, 'Accepted');
  assert.equal(cancelled.pendingText, '\uD83D');
});
