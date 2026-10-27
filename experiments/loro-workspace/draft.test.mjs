import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ConversationWorkspace } from './conversation.mjs';
import { DraftReplica } from './draft.mjs';
import { decode } from './boundary.mjs';

function setup(t) {
  const dir = mkdtempSync(join(tmpdir(), 'textprov-draft-'));
  const replicas = [];
  let workspace;
  t.after(() => {
    replicas.reverse().forEach(r => r.close());
    workspace?.close();
    rmSync(dir, { recursive: true, force: true });
  });
  const database = join(dir, 'capture.sqlite');
  const ran = spawnSync(process.env.TEXTPROV_PYTHON || 'python3',
    [fileURLToPath(new URL('./fixture_chronicle.py', import.meta.url)), database, '--small'], { encoding: 'utf8' });
  assert.equal(ran.status, 0, ran.stderr);
  const workspacePath = join(dir, 'conversation.loro');
  workspace = new ConversationWorkspace(workspacePath);
  workspace.importSelected({ database, provider: 'claude', session: 'selected', agent: null });
  const messages = workspace.messages();
  const human = messages[0], assistant = messages.find(m => m.role === 'assistant');
  const selections = [human, assistant].map(m => ({ message: m.identity, start: 0, end: m.visible.length }));
  const track = r => { replicas.push(r); return r; };
  const a = track(DraftReplica.fromConversation(workspace, selections));
  return { a, b: track(a.fork()), track, workspace, workspacePath, database, human, assistant, selections };
}

function sync(a, b) {
  const av = a.version(), bv = b.version();
  const au = a.update(bv), bu = b.update(av);
  a.receive(bu); b.receive(au);
}

function equal(a, b) {
  assert.equal(a.visible(), b.visible());
  assert.deepEqual(a.inspect().tokens, b.inspect().tokens);
  assert.deepEqual(a.sources(), b.sources());
  assert.deepEqual(a.conflicts(), b.conflicts());
}

test('passage selection preserves exact marks and pins immutable source references', t => {
  const f = setup(t);
  const sourceBytes = readFileSync(f.database), savedBytes = readFileSync(f.workspacePath);
  assert.equal(f.a.portable(), f.human.portable + '\n\n' + f.assistant.portable);
  assert.equal(f.a.sources()[0].originalContentHash, f.human.metadata.content_hash);
  assert.equal(f.a.sources()[1].completeness, 'partial');
  assert.equal(f.a.sources()[0].coordinateSystem, 'visible-utf16-grapheme-boundaries');
  assert.notEqual(f.a.doc.peerIdStr, f.b.doc.peerIdStr);
  const refs = f.a.sources();
  f.workspace.revise(f.human.identity, 'A changed source revision');
  f.a.replace(0, 0, 'Editor addition.\n');
  assert.deepEqual(f.a.sources(), refs);
  assert.ok(f.a.visible().includes(f.human.visible));
  assert.deepEqual(readFileSync(f.database), sourceBytes);
  // Draft edits do not save or mutate the stage-two conversation snapshot.
  const revisedBytes = readFileSync(f.workspacePath);
  assert.notDeepEqual(revisedBytes, savedBytes);
  f.a.replace(0, 0, 'More ');
  assert.deepEqual(readFileSync(f.workspacePath), revisedBytes);
});

test('invalid selections, stale hashes and unavailable sources fail without altering captures', t => {
  const f = setup(t);
  const sourceBytes = readFileSync(f.database), savedBytes = readFileSync(f.workspacePath);
  const unavailable = f.workspace.messages().find(m => m.portable === null);
  for (const selection of [
    { ...f.selections[0], expectedHash: 'stale' },
    { ...f.selections[0], message: 'unknown' },
    { ...f.selections[0], message: unavailable.identity },
    { ...f.selections[0], start: 0, end: 0 },
    { ...f.selections[0], revision: 'unknown' },
  ]) assert.throws(() => DraftReplica.fromConversation(f.workspace, [selection]));
  assert.deepEqual(readFileSync(f.database), sourceBytes);
  assert.deepEqual(readFileSync(f.workspacePath), savedBytes);
});

test('selecting a specific revision pins its passage and rejects split Unicode graphemes', t => {
  const f = setup(t);
  const revision = f.workspace.revise(f.human.identity, 'e\u0301 👩🏽‍💻 revised');
  const portable = f.workspace.revisions()[revision].portable;
  const selected = { message: f.human.identity, revision, start: 0, end: 2 };
  const draft = f.track(DraftReplica.fromConversation(f.workspace, [selected]));
  assert.equal(draft.visible(), 'e\u0301');
  assert.equal(draft.sources()[0].revision, revision);
  assert.equal(draft.portable(), decode(portable)[0].raw);
  assert.throws(() => DraftReplica.fromConversation(f.workspace, [{ ...selected, end: 1 }]), /grapheme/);
});

test('independent human and AI edits converge in text and attribution across two replicas', t => {
  const f = setup(t);
  const { a, b } = f;
  a.replace(0, 0, 'Human editor.\n');
  const start = b.visible().indexOf('Partial');
  b.replace(start, start + 7, 'Updated', { actor: 'assistant' });
  sync(a, b);
  equal(a, b);
  assert.equal(a.conflicts().length, 0);
  assert.ok(a.portable().startsWith('Human editor.\n'));
  const updated = a.visible().indexOf('Updated');
  assert.ok(decode(a.copy(updated, updated + 7)).every(t => t.state === 'ai'));
  assert.ok(a.portable().includes(f.human.portable));
  assert.equal(a.visible(), 'Human editor.\nHuman pasted AI\n\nUpdated answer');
});

test('concurrent same-gap insertions retain both contributors without inherited attribution', t => {
  const { a, b } = setup(t);
  a.replace(0, 0, 'x');
  b.replace(0, 0, 'Y', { actor: 'assistant' });
  sync(a, b);
  equal(a, b);
  assert.deepEqual(new Set(a.visible().slice(0, 2)), new Set(['x', 'Y']));
  assert.equal(a.inspect().tokens.find(t => t.visible === 'x').state, null);
  assert.equal(a.inspect().tokens.find(t => t.visible === 'Y').state, 'ai');
  assert.equal(a.conflicts().length, 0);
});

test('out-of-order and duplicated updates preserve pending operations through a checkpoint', t => {
  const { a, b, track } = setup(t);
  const base = a.version();
  a.replace(0, 0, 'one ');
  const first = a.update(base);
  const middle = a.version();
  a.replace(0, 0, 'two ');
  const second = a.update(middle);
  assert.equal(b.receive(second).pending, true);
  const restored = track(DraftReplica.restore(b.checkpoint()));
  restored.receive(second);
  restored.receive(first);
  restored.receive(first);
  equal(a, restored);
  assert.equal(restored.portable(), a.portable());
});

test('local undo after sync preserves the other replica edit and synchronizes attribution', t => {
  const { a, b } = setup(t);
  a.replace(0, 0, 'mine ');
  b.replace(b.visible().length, b.visible().length, ' AI addition.', { actor: 'assistant' });
  sync(a, b);
  const remoteTail = b.copy(b.visible().indexOf(' AI addition.'));
  assert.equal(a.undo(), true);
  sync(a, b);
  equal(a, b);
  assert.ok(!a.visible().startsWith('mine '));
  assert.ok(a.portable().endsWith(remoteTail));
  assert.equal(a.redo(), true);
  sync(a, b);
  equal(a, b);
  assert.ok(a.visible().startsWith('mine '));
});

test('stale prepared AI edits remain proposals without overwriting remote changes', t => {
  const { a, b } = setup(t);
  const proposal = a.prepareEdit(0, 5, 'Replacement', { actor: 'assistant' });
  b.replace(0, 5, 'Edited by human');
  sync(a, b);
  const before = a.portable();
  const result = a.applyPrepared(proposal);
  assert.equal(result.applied, false);
  assert.equal(result.reason, 'stale-base');
  assert.deepEqual(result.proposal, proposal);
  assert.equal(a.portable(), before);
});

test('overlapping offline rewrites need an explicit reviewed resolution rather than unsafe undo', t => {
  const { a, b } = setup(t);
  a.replace(0, 5, 'First', { actor: 'assistant' });
  b.replace(0, 5, 'Second');
  const chosen = b.portable();
  sync(a, b);
  equal(a, b);
  assert.equal(a.conflicts().length, 1);
  assert.throws(() => a.copy(), /need review/);
  assert.throws(() => b.portable(), /need review/);
  assert.throws(() => a.undo(), /review overlapping/);
  assert.throws(() => a.resolve(chosen, { expectedHash: 'stale' }), /review the current/);
  a.resolve(chosen, { expectedHash: a.inspect().reviewHash });
  sync(a, b);
  equal(a, b);
  assert.equal(a.conflicts().length, 0);
  assert.equal(a.portable(), chosen);
});

test('concurrent different resolutions stay conflicted instead of silently choosing one', t => {
  const { a, b } = setup(t);
  a.replace(0, 5, 'First', { actor: 'assistant' });
  const first = a.portable();
  b.replace(0, 5, 'Second');
  const second = b.portable();
  sync(a, b);
  a.resolve(first, { expectedHash: a.inspect().reviewHash });
  b.resolve(second, { expectedHash: b.inspect().reviewHash });
  sync(a, b);
  equal(a, b);
  assert.ok(a.conflicts().length > 0);
  assert.throws(() => a.copy(), /need review/);
});

test('cross-draft and malformed attribution updates are refused without losing local undo', t => {
  const f = setup(t);
  const unrelated = f.track(DraftReplica.fromConversation(f.workspace, f.selections));
  assert.throws(() => f.a.receive(unrelated.update()), /another draft/);
  f.a.replace(0, 0, 'local ');
  f.b.body.text.insert(0, 'unattributed');
  f.b.doc.commit();
  const before = f.a.portable();
  assert.throws(() => f.a.receive(f.b.update()), /metadata|boundaries/);
  assert.equal(f.a.portable(), before);
  assert.equal(f.a.undo(), true);
  assert.equal(f.a.portable(), f.human.portable + '\n\n' + f.assistant.portable);
  f.b.undo();
  const header = f.b.doc.getMap('draft').get('header');
  f.b.doc.getMap('draft').set('header', { ...header, title: 'Changed source metadata' });
  f.b.doc.commit();
  assert.throws(() => f.a.receive(f.b.update()), /source references/);
  f.b.doc.getMap('draft').set('header', header);
  f.b.doc.getMap('edits').set('invalid-edit', { seen: 'not an array' });
  f.b.doc.commit();
  const retained = f.a.portable();
  assert.throws(() => f.a.receive(f.b.update()), /edit metadata/);
  assert.equal(f.a.portable(), retained);
});
