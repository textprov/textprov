import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ConversationWorkspace } from './conversation.mjs';
import { DraftReplica } from './draft.mjs';

const dir = mkdtempSync(join(tmpdir(), 'textprov-shared-draft-demo-'));
let workspace, a, b;
try {
  const database = join(dir, 'fixture.sqlite');
  const created = spawnSync(process.env.TEXTPROV_PYTHON || 'python3',
    [fileURLToPath(new URL('./fixture_chronicle.py', import.meta.url)), database, '--small'], { encoding: 'utf8' });
  if (created.status !== 0) throw new Error(created.stderr);
  workspace = new ConversationWorkspace(join(dir, 'conversation.loro'));
  workspace.importSelected({ database, provider: 'claude', session: 'selected', agent: null });
  const messages = workspace.messages();
  const human = messages[0], assistant = messages.find(m => m.role === 'assistant');
  const sourceBytes = readFileSync(database), workspaceBytes = readFileSync(workspace.path);
  a = DraftReplica.fromConversation(workspace, [human, assistant].map(m => ({
    message: m.identity, start: 0, end: m.visible.length,
  })));
  b = a.fork();
  a.replace(0, 0, 'Editor introduction.\n');
  const start = b.visible().indexOf('Partial');
  b.replace(start, start + 7, 'Revised', { actor: 'assistant' });
  const av = a.version(), bv = b.version();
  const au = a.update(bv), bu = b.update(av);
  a.receive(bu); b.receive(au); b.receive(au);
  assert.deepEqual(a.inspect(), b.inspect());
  assert.equal(a.portable(), b.portable());
  assert.deepEqual(readFileSync(database), sourceBytes);
  assert.deepEqual(readFileSync(workspace.path), workspaceBytes);
  if (process.argv.includes('--portable')) process.stdout.write(a.portable());
  else console.log(JSON.stringify({
    sources: a.sources().length, replicas: 2, visible: a.visible(),
    textAndAttributionConverged: true, duplicateUpdateHarmless: true,
    captureBytesUnchanged: true, savedConversationUnchanged: true,
    conflicts: a.conflicts(), scope: 'Disposable local fixture; no installed databases or settings accessed.',
  }, null, 2));
} finally {
  a?.close(); b?.close(); workspace?.close();
  rmSync(dir, { recursive: true, force: true });
}
