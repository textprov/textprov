import test from 'node:test';
import { request } from 'node:http';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ConversationWorkspace } from './conversation.mjs';
import { UISession } from './ui-session.mjs';
import { createUI } from './ui-server.mjs';
import { portableRange, visibleEdit } from './editor.mjs';
function fixture(t) {
  const dir = mkdtempSync(join(tmpdir(), 'textprov-ui-test-'));
  const db = join(dir, 'capture.sqlite');
  const made = spawnSync(process.env.TEXTPROV_PYTHON || 'python3', [fileURLToPath(new URL('fixture_chronicle.py', import.meta.url)), db, '--small'], { encoding: 'utf8' });
  assert.equal(made.status, 0, made.stderr);
  const workspace = new ConversationWorkspace(join(dir, 'conversation.loro'));
  workspace.importSelected({ database: db, provider: 'claude', session: 'selected', agent: null });
  t.after(() => { workspace.close(); rmSync(dir, { recursive: true, force: true }); });
  return { workspace, db };
}
function select(session) {
  const m = session.state().messages[0];
  return session.execute({ operation: 'select', selections: [{ message: m.identity, start: 0, end: m.visible.length }] });
}
test('UI selection, human and simulated AI edits, sync, portable paste and checkpoint retain attribution', t => {
  const { workspace, db } = fixture(t), session = new UISession(workspace);
  t.after(() => session.close());
  const captured = readFileSync(db), saved = readFileSync(workspace.path);
  let state = select(session);
  const command = (operation, replica, extra = {}) => session.execute({ operation, replica,
    expectedHash: session.state().replicas[replica].reviewHash, ...extra });
  command('edit', 0, { start: 0, end: 0, text: 'Intro ', actor: 'human' });
  command('edit', 1, { start: state.replicas[1].text.length, end: state.replicas[1].text.length, text: ' New prose.', actor: 'assistant' });
  state = session.execute({ operation: 'sync' });
  assert.deepEqual(state.replicas[0], state.replicas[1]);
  assert.equal(state.replicas[0].tokens[0].state, null);
  const raw = command('copy', 0, { start: 0, end: state.replicas[0].text.length }).portable;
  const decoded = session.execute({ operation: 'decode', text: raw });
  assert.deepEqual(decoded, state.replicas[0].tokens);
  assert.equal(portableRange(decoded, 0, state.replicas[0].text.length), raw);
  assert.ok(decoded.some(t => t.state === 'ai'));
  const len = state.replicas[0].text.length;
  command('edit', 0, { start: len, end: len, text: raw });
  assert.deepEqual(session.state().replicas[0].tokens.slice(decoded.length), decoded);
  const checkpoint = command('checkpoint', 0);
  const restored = new UISession(workspace); t.after(() => restored.close());
  assert.deepEqual(restored.execute({ operation: 'restore', saved: checkpoint }).replicas[0], session.state().replicas[0]);
  assert.deepEqual(readFileSync(db), captured);
  assert.deepEqual(readFileSync(workspace.path), saved);
  assert.throws(() => session.execute({ operation: 'edit', replica: 0, expectedHash: 'stale', start: 0, end: 1, text: '' }), /changed/);
});
test('UI conflict pauses export and edits until explicit review', t => {
  const { workspace } = fixture(t), session = new UISession(workspace); t.after(() => session.close());
  select(session);
  for (const replica of [0, 1]) session.execute({ operation: 'edit', replica,
    expectedHash: session.state().replicas[replica].reviewHash, start: 0, end: 5, text: replica ? 'Second' : 'First' });
  const state = session.execute({ operation: 'sync' });
  assert.ok(state.replicas[0].conflicts.length);
  assert.throws(() => session.execute({ operation: 'copy', replica: 0, expectedHash: state.replicas[0].reviewHash, start: 0, end: 1 }), /review/);
  session.execute({ operation: 'resolve', replica: 0, expectedHash: state.replicas[0].reviewHash,
    text: state.replicas[0].tokens.map(t => t.raw).join('') });
  assert.deepEqual(session.execute({ operation: 'sync' }).replicas[1].conflicts, []);
});
test('visible editing and portable copying refuse split graphemes', () => {
  assert.deepEqual(visibleEdit('a\u0301b', 'a\u0301Xb'), { start: 2, end: 2, text: 'X' });
  assert.throws(() => portableRange([{ visible: 'a\u0301', raw: 'a\u0301', state: null }], 0, 1), /whole/);
});
test('loopback UI requires session token, same origin and exact Host', async t => {
  const { workspace } = fixture(t), { server } = createUI(workspace);
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  try {
    const base = `http://127.0.0.1:${server.address().port}`;
    const page = await (await fetch(base)).text();
    const token = page.match(/name="textprov-token" content="([a-f0-9]+)"/)[1];
    assert.equal((await fetch(base + '/api/state')).status, 403);
    assert.equal((await fetch(base + '/api/state', { headers: { 'x-textprov-token': token, Origin: 'https://example.com' } })).status, 403);
    const hostStatus = await new Promise((resolve, reject) => {
      const req = request(base, { headers: { Host: 'example.com' } }, res => { res.resume(); resolve(res.statusCode); });
      req.on('error', reject); req.end();
    });
    assert.equal(hostStatus, 403);
    const state = await (await fetch(base + '/api/state', { headers: { 'x-textprov-token': token } })).json();
    assert.ok(state.messages.length);
    assert.equal((await fetch(base + '/ui.mjs')).headers.get('content-type'), 'text/javascript; charset=utf-8');
  } finally { await new Promise(resolve => server.close(resolve)); }
});

test('local library reopens both unsynchronized replicas after restart without reading captures', async t => {
  const { LocalDraftStore } = await import('./local-drafts.mjs');
  const { workspace, db } = fixture(t);
  const directory = mkdtempSync(join(tmpdir(), 'textprov-ui-library-'));
  let store = new LocalDraftStore(directory), session = new UISession(workspace, { store });
  t.after(() => { session.close(); store.close(); rmSync(directory, { recursive: true, force: true }); });
  const source = readFileSync(db), conversation = readFileSync(workspace.path);
  let state = select(session);
  for (const replica of [0, 1]) session.execute({ operation: 'edit', replica, expectedHash: session.state().replicas[replica].reviewHash,
    start: 0, end: 0, text: replica ? 'AI addition ' : 'Human addition ', actor: replica ? 'assistant' : 'human' });
  state = session.execute({ operation: 'save', title: 'My local draft' });
  const { id } = state.persistence;
  assert.equal(state.persistence.error, null); assert.equal(state.savedDrafts[0].title, 'My local draft');
  const before = state.replicas;
  session.close(); store.close();
  store = new LocalDraftStore(directory); session = new UISession(workspace, { store });
  assert.deepEqual(session.execute({ operation: 'open', id }).replicas, before);
  const synced = session.execute({ operation: 'sync' });
  assert.deepEqual(synced.replicas[0], synced.replicas[1]);
  assert.deepEqual(readFileSync(db), source); assert.deepEqual(readFileSync(workspace.path), conversation);
});
test('save failure retains live edits, blocks switching and recovers on retry', async t => {
  const { LocalDraftStore } = await import('./local-drafts.mjs');
  const { workspace } = fixture(t), directory = mkdtempSync(join(tmpdir(), 'textprov-ui-save-fail-'));
  let fail = false;
  const store = new LocalDraftStore(directory, { beforeCommit: () => { if (fail) throw new Error('disk full'); } });
  const session = new UISession(workspace, { store });
  t.after(() => { session.close(); store.close(); rmSync(directory, { recursive: true, force: true }); });
  let state = select(session); fail = true;
  state = session.execute({ operation: 'edit', replica: 0, expectedHash: state.replicas[0].reviewHash, start: 0, end: 0, text: 'Retain me ' });
  assert.match(state.persistence.error, /disk full/); assert.match(state.replicas[0].text, /^Retain me/);
  assert.throws(() => session.execute({ operation: 'new' }), /could not be saved/);
  fail = false; state = session.execute({ operation: 'save' });
  assert.equal(state.persistence.error, null);
  assert.match(store.read(state.persistence.id).payload.replicas[0].snapshot, /.+/);
});

async function until(condition) {
  const end = Date.now() + 12000;
  while (!condition()) {
    if (Date.now() > end) throw new Error('local simulator did not reach expected state');
    await new Promise(resolve => setTimeout(resolve, 10));
  }
}
test('local stream cancellation, alternatives and original context survive saved reopening', async t => {
  const { LocalDraftStore } = await import('./local-drafts.mjs');
  const { workspace, db } = fixture(t), directory = mkdtempSync(join(tmpdir(), 'textprov-ui-stream-'));
  const store = new LocalDraftStore(directory);
  let session = new UISession(workspace, { store, simulationDelay: 5 });
  t.after(() => { session.close(); store.close(); rmSync(directory, { recursive: true, force: true }); });
  const capture = readFileSync(db), conversation = readFileSync(workspace.path);
  let state = select(session);
  state = session.execute({ operation: 'response-start', replica: 0, expectedHash: state.replicas[0].reviewHash,
    prompt: 'Please explain this.', simulatedText: 'This is a longer response that can be cancelled after its first local chunk.' });
  const first = state.responses[0].id;
  await until(() => session.responses.inspect(first).nextSequence > 0);
  state = session.execute({ operation: 'response-cancel', id: first });
  const cancelled = state.responses[0]; assert.equal(cancelled.status, 'cancelled');
  await new Promise(resolve => setTimeout(resolve, 30));
  assert.equal(session.responses.inspect(first).portable, cancelled.portable);
  assert.ok(cancelled.tokens.some(t => t.state === 'ai'));
  state = session.execute({ operation: 'edit', replica: 0, expectedHash: state.replicas[0].reviewHash,
    start: 0, end: 0, text: 'Changed context. ' });
  state = session.execute({ operation: 'response-regenerate', id: first, replica: 0, expectedHash: state.replicas[0].reviewHash,
    simulatedText: 'Alternative.', useCurrentContext: false });
  const originalAlternative = state.responses[1].id;
  await until(() => session.responses.inspect(originalAlternative).status === 'completed');
  assert.deepEqual(session.responses.inspect(first).context, session.responses.inspect(originalAlternative).context);
  assert.throws(() => session.execute({ operation: 'response-insert', id: originalAlternative, replica: 0,
    expectedHash: session.state().replicas[0].reviewHash }), /context changed/);
  state = session.execute({ operation: 'response-regenerate', id: first, replica: 0, expectedHash: session.state().replicas[0].reviewHash,
    simulatedText: 'Current.', useCurrentContext: true });
  const current = state.responses[2].id;
  await until(() => session.responses.inspect(current).status === 'completed');
  assert.notEqual(session.responses.inspect(first).context.reviewHash, session.responses.inspect(current).context.reviewHash);
  session.execute({ operation: 'response-insert', id: current, replica: 0, expectedHash: session.state().replicas[0].reviewHash });
  const savedId = session.savedId, before = session.responses.snapshot(); session.close();
  session = new UISession(workspace, { store });
  state = session.execute({ operation: 'open', id: savedId });
  assert.deepEqual(session.responses.snapshot(), before); assert.equal(state.responses.length, 3);
  assert.deepEqual(readFileSync(db), capture); assert.deepEqual(readFileSync(workspace.path), conversation);
});
test('reopening an unfinished local stream marks it interrupted and never schedules late chunks', async t => {
  const { LocalDraftStore } = await import('./local-drafts.mjs');
  const { workspace } = fixture(t), directory = mkdtempSync(join(tmpdir(), 'textprov-ui-interrupt-'));
  const store = new LocalDraftStore(directory); let session = new UISession(workspace, { store, simulationDelay: 5 });
  t.after(() => { session.close(); store.close(); rmSync(directory, { recursive: true, force: true }); });
  const state = select(session);
  session.execute({ operation: 'response-start', replica: 0, expectedHash: state.replicas[0].reviewHash,
    prompt: 'A prompt', simulatedText: 'An unfinished answer to keep for later inspection and regeneration.' });
  const id = session.savedId, attempt = session.responses.list()[0].id;
  await until(() => session.responses.inspect(attempt).nextSequence === 1);
  const partial = session.responses.inspect(attempt).portable;
  session.close(); session = new UISession(workspace, { store });
  session.execute({ operation: 'open', id });
  assert.equal(session.responses.inspect(attempt).status, 'interrupted');
  assert.equal(session.responses.inspect(attempt).portable, partial);
  assert.equal(session.timers.size, 0);
});

test('publication previews and exports pin a selected replica without modifying saved work or captures', async t => {
  const { LocalDraftStore } = await import('./local-drafts.mjs');
  const { workspace, db } = fixture(t), directory = mkdtempSync(join(tmpdir(), 'textprov-ui-publication-'));
  const store = new LocalDraftStore(directory), session = new UISession(workspace, { store });
  t.after(() => { session.close(); store.close(); rmSync(directory, { recursive: true, force: true }); });
  let state = select(session);
  state = session.execute({ operation: 'edit', replica: 1, expectedHash: state.replicas[1].reviewHash,
    start: 0, end: 0, text: '# Reader title\n\nA human introduction.\n\n' });
  const privateAttempt = session.responses.start(session.replicas[0], { prompt: 'PRIVATE_PROMPT_NOT_FOR_PUBLICATION' });
  session.responses.appendChunk(privateAttempt.id, 0, 'PRIVATE_ALTERNATIVE_NOT_FOR_PUBLICATION');
  session.save();
  const dbBytes = readFileSync(db), conversation = readFileSync(workspace.path), library = readFileSync(store.path(session.savedId));
  const live = session.state();
  const snapshot = session.execute({ operation: 'publication-preview', replica: 1, expectedHash: live.replicas[1].reviewHash, title: 'Reader draft' });
  assert.equal(snapshot.portable, session.replicas[1].portable());
  assert.equal(snapshot.hash, live.replicas[1].reviewHash);
  assert.equal(snapshot.counts.total, snapshot.counts.ai + snapshot.counts.human + snapshot.counts.unmarked);
  assert.ok(snapshot.preview.html.includes('<h1>'));
  assert.deepEqual(Object.keys(snapshot).sort(), ['format', 'id', 'draftId', 'title', 'version', 'hash', 'portable', 'text', 'tokens', 'counts', 'preview'].sort());
  assert.ok(!JSON.stringify(snapshot).includes('PRIVATE_PROMPT')); assert.ok(!JSON.stringify(snapshot).includes('PRIVATE_ALTERNATIVE'));
  assert.ok(!('sources' in snapshot)); assert.ok(!('responses' in snapshot));
  assert.deepEqual(readFileSync(db), dbBytes); assert.deepEqual(readFileSync(workspace.path), conversation);
  assert.deepEqual(readFileSync(store.path(session.savedId)), library);
  const original = snapshot.portable;
  snapshot.portable = 'client mutation';
  const exported = session.execute({ operation: 'publication-export', id: snapshot.id, hash: snapshot.hash });
  assert.deepEqual(Buffer.from(exported.portable, 'utf8'), Buffer.from(original, 'utf8'));
  assert.equal(exported.mediaType, 'text/plain;charset=utf-8');
  session.execute({ operation: 'edit', replica: 1, expectedHash: session.state().replicas[1].reviewHash,
    start: 0, end: 0, text: 'Later draft change.\n' });
  assert.equal(session.execute({ operation: 'publication-export', id: snapshot.id, hash: snapshot.hash }).portable, original,
    'export uses the reviewed revision rather than a changed live draft');
  assert.throws(() => session.execute({ operation: 'publication-export', id: snapshot.id, hash: 'wrong' }), /preview changed/);
  session.execute({ operation: 'new' });
  assert.throws(() => session.execute({ operation: 'publication-export', id: snapshot.id, hash: snapshot.hash }), /preview changed/);
});
test('publication selection refuses stale hashes, conflicts and superseded preview IDs', t => {
  const { workspace } = fixture(t), session = new UISession(workspace); t.after(() => session.close());
  const state = select(session);
  assert.throws(() => session.execute({ operation: 'publication-preview', replica: 0, expectedHash: 'stale' }), /changed/);
  const first = session.execute({ operation: 'publication-preview', replica: 0, expectedHash: state.replicas[0].reviewHash });
  session.execute({ operation: 'publication-preview', replica: 1, expectedHash: state.replicas[1].reviewHash });
  assert.throws(() => session.execute({ operation: 'publication-export', id: first.id, hash: first.hash }), /preview changed/);
  for (const replica of [0, 1]) session.execute({ operation: 'edit', replica,
    expectedHash: session.state().replicas[replica].reviewHash, start: 0, end: 5, text: replica ? 'Second' : 'First' });
  const conflicted = session.execute({ operation: 'sync' });
  assert.throws(() => session.execute({ operation: 'publication-preview', replica: 0, expectedHash: conflicted.replicas[0].reviewHash }), /review/);
});
