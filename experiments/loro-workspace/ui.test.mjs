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
