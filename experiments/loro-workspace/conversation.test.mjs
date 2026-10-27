import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync, rmSync, existsSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ConversationWorkspace, readConversation } from './conversation.mjs';
import { decode } from './boundary.mjs';

function setup(t) {
  const dir = mkdtempSync(join(tmpdir(), 'textprov-loro-import-'));
  t.after(() => rmSync(dir, { recursive: true, force: true }));
  const database = join(dir, 'capture.sqlite');
  const ran = spawnSync(process.env.TEXTPROV_PYTHON || 'python3',
    [fileURLToPath(new URL('./fixture_chronicle.py', import.meta.url)), database], { encoding: 'utf8' });
  assert.equal(ran.status, 0, ran.stderr);
  const ids = JSON.parse(ran.stdout);
  const selection = { database, provider: 'claude', session: 'selected', agent: null };
  return { dir, database, ids, selection, workspacePath: join(dir, 'conversation.loro') };
}

test('scoped paged import preserves mixed attribution, partial captures and unavailable placeholders', t => {
  const f = setup(t);
  const before = readFileSync(f.database);
  const batch = readConversation(f.selection);
  assert.equal(batch.items.length, 111);
  assert.equal(batch.skipped_nonchat, 1);
  assert.equal(batch.items[0].metadata.observation_id, f.ids.human);
  assert.ok(batch.items.every(i => i.metadata.provider === 'claude' &&
    i.metadata.session_id === 'selected' && i.metadata.agent_id === null));
  for (const key of ['expired', 'missing']) {
    const item = batch.items.find(i => i.metadata.observation_id === f.ids[key]);
    assert.equal(item.portable, null);
    assert.equal(item.availability, 'unavailable');
  }
  assert.equal(batch.items.find(i => i.metadata.observation_id === f.ids.answer).metadata.completeness, 'partial');
  assert.ok(decode(batch.items[0].portable).some(t => t.state === 'ai'));
  assert.ok(decode(batch.items[0].portable).some(t => t.state === 'human'));
  assert.deepEqual(readFileSync(f.database), before, 'source bytes, including expired cache, unchanged');
});

test('replay and restart do not duplicate captures or overwrite independent revisions', t => {
  const f = setup(t);
  const before = readFileSync(f.database);
  let w = new ConversationWorkspace(f.workspacePath);
  try {
    const first = w.importSelected(f.selection);
    assert.equal(first.added, 111);
    assert.equal(first.placeholders, 2);
    assert.equal(w.messages().filter(m => m.visible === 'Same words').length, 2, 'same text is not event identity');
    const firstMessage = w.messages()[0];
    const revisionId = w.revise(firstMessage.identity, firstMessage.visible + ' changed');
    assert.ok(decode(w.revisions()[revisionId].portable).some(t => t.state === 'ai'),
      'unchanged pasted AI marks survive human revision even when selectors are omitted');
    const child = w.revise(firstMessage.identity, firstMessage.visible + ' changed again', { baseRevision: revisionId });
    assert.equal(w.revisions()[child].parentRevision, revisionId);
    assert.throws(() => w.revise(firstMessage.identity, 'changed', { baseRevision: 'missing' }), /revision base/);
    const revisions = w.revisions();
    assert.equal(w.importSelected(f.selection).added, 0);
    assert.equal(w.messages().length, 111);
    assert.deepEqual(w.revisions(), revisions);
    w.close(); w = new ConversationWorkspace(f.workspacePath);
    assert.equal(w.importSelected(f.selection).duplicates, 111);
    assert.equal(w.messages()[0].portable, firstMessage.portable);
    assert.deepEqual(w.revisions(), revisions);
    assert.equal(statSync(f.workspacePath).mode & 0o777, 0o600);
  } finally { w.close(); }
  assert.deepEqual(readFileSync(f.database), before);
});

test('different scopes require a separate workspace; cross-agent inclusion is explicit', t => {
  const f = setup(t);
  const w = new ConversationWorkspace(f.workspacePath);
  try {
    w.importSelected(f.selection);
    const before = readFileSync(f.workspacePath);
    assert.throws(() => w.importSelected({ ...f.selection, cross_agent: true }), /selection differs/);
    assert.deepEqual(readFileSync(f.workspacePath), before);
    const batch = readConversation({ ...f.selection, cross_agent: true });
    assert.ok(batch.items.some(i => i.metadata.observation_id === f.ids['other-agent']));
    const worker = readConversation({ ...f.selection, agent: 'worker' });
    assert.equal(worker.items.length, 1);
    assert.equal(worker.items[0].metadata.observation_id, f.ids['other-agent']);
  } finally { w.close(); }
});

test('changed hash under an existing observation identity aborts without changing the workspace', t => {
  const f = setup(t);
  const w = new ConversationWorkspace(f.workspacePath);
  try {
    w.importSelected(f.selection);
    const before = readFileSync(f.workspacePath);
    // Deliberately corrupt only the retained workspace reference, not a capture.
    const first = w.doc.getMap('messages').get(w.messages()[0].identity);
    const item = first.get('capture');
    first.set('capture', { ...item, metadata: { ...item.metadata, content_hash: 'changed' } });
    w.doc.commit();
    assert.throws(() => w.importSelected(f.selection), /changed hash or metadata/);
    assert.deepEqual(readFileSync(f.workspacePath), before);
  } finally { w.close(); }
});

test('missing selections, missing files and bounded imports fail without creating capture files', t => {
  const f = setup(t);
  const bad = join(f.dir, 'missing.sqlite');
  assert.throws(() => readConversation({ ...f.selection, database: bad }), /existing/);
  assert.equal(existsSync(bad), false);
  const { agent, ...withoutAgent } = f.selection;
  assert.throws(() => readConversation(withoutAgent));
  assert.throws(() => readConversation({ ...f.selection, max_observations: 2 }), /exceeds/);
  const fake = join(f.dir, 'not-a-database');
  writeFileSync(fake, 'not sqlite');
  assert.throws(() => readConversation({ ...f.selection, database: fake }));
});

test('failed save leaves no in-memory import or cursor; a competing writer is refused', t => {
  const f = setup(t);
  const w = new ConversationWorkspace(f.workspacePath);
  try {
    assert.throws(() => new ConversationWorkspace(f.workspacePath), /EEXIST/);
    // A directory cannot be atomically replaced by the new snapshot file.
    const original = w.path;
    w.path = f.dir;
    assert.throws(() => w.importSelected(f.selection), /regular file/);
    assert.equal(w.messages().length, 0);
    assert.equal(w.doc.getMap('config').get('lastImport'), undefined);
    w.path = original;
    assert.equal(w.importSelected(f.selection).added, 111);
  } finally { w.close(); }
});

test('later cache expiry preserves retained messages and only new capture IDs append', t => {
  const f = setup(t);
  const w = new ConversationWorkspace(f.workspacePath);
  try {
    w.importSelected(f.selection);
    const first = w.messages()[0];
    // Alter only the disposable fixture to simulate expiry and a later capture.
    const script = `import sys,time,json
sys.path.insert(0,sys.argv[2])
from textprov.chronicle import Chronicle
with Chronicle(sys.argv[1],clock=lambda:time.time()+7200) as c: c.status()
with Chronicle(sys.argv[1]) as c:
 print(json.dumps(c.observe(provider='claude',adapter='fixture',session_id='selected',delivery_key='later',event_kind='submission',channel='user',visibility='stored',text='A later message')))
`;
    const ran = spawnSync(process.env.TEXTPROV_PYTHON || 'python3', ['-c', script,
      f.database, fileURLToPath(new URL('../../python', import.meta.url))], { encoding: 'utf8' });
    assert.equal(ran.status, 0, ran.stderr);
    const before = readFileSync(f.database);
    const result = w.importSelected(f.selection);
    assert.equal(result.added, 1);
    assert.equal(result.duplicates, 111);
    assert.equal(w.messages()[0].portable, first.portable);
    assert.equal(w.messages().at(-1).metadata.observation_id, JSON.parse(ran.stdout));
    assert.equal(w.messages().at(-1).visible, 'A later message');
    assert.deepEqual(readFileSync(f.database), before);
  } finally { w.close(); }
});

test('selecting a capture database as the workspace fails without altering it', t => {
  const f = setup(t);
  const before = readFileSync(f.database);
  assert.throws(() => new ConversationWorkspace(f.database));
  assert.deepEqual(readFileSync(f.database), before);
  assert.equal(existsSync(f.database + '.lock'), false);
});
