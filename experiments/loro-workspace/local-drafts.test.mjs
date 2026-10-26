import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, readFileSync, rmSync, writeFileSync, statSync, symlinkSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { LocalDraftStore } from './local-drafts.mjs';
function library(t, options) {
  const path = mkdtempSync(join(tmpdir(), 'textprov-local-store-'));
  const store = new LocalDraftStore(path, options);
  t.after(() => { store.close(); rmSync(path, { recursive: true, force: true }); });
  return { path, store };
}
test('private atomic library reopens exact payload and refuses stale generations and path traversal', t => {
  const { store, path } = library(t), id = randomUUID();
  const payload = { text: 'A\u{E0101}', replicas: ['first', 'second'] };
  const saved = store.save(id, 'A draft', payload);
  assert.deepEqual(store.read(id).payload, payload);
  assert.equal(statSync(store.path(id)).mode & 0o777, 0o600);
  assert.throws(() => store.save(id, 'lost update', {}, 0), /changed/);
  assert.throws(() => store.read('../capture'), /invalid/);
  assert.throws(() => new LocalDraftStore(path), /already open/);
  store.close();
  const reopened = new LocalDraftStore(path);
  try { assert.equal(reopened.list()[0].title, 'A draft'); assert.equal(reopened.read(id).generation, saved.generation); }
  finally { reopened.close(); }
});
test('failed commit leaves last saved bytes intact and retry advances once', t => {
  let fail = false;
  const { store } = library(t, { beforeCommit: () => { if (fail) throw new Error('simulated disk failure'); } });
  const id = randomUUID(); store.save(id, 'original', { text: 'kept' });
  const before = readFileSync(store.path(id)); fail = true;
  assert.throws(() => store.save(id, 'new', { text: 'not lost in memory' }, 1), /disk failure/);
  assert.deepEqual(readFileSync(store.path(id)), before);
  fail = false; assert.equal(store.save(id, 'retry', { text: 'recovered' }, 1).generation, 2);
});
test('corrupt records are reported and symlink targets are never overwritten', t => {
  const { store, path } = library(t), id = randomUUID(), linked = randomUUID();
  store.save(id, 'valid', { text: 'original' });
  const record = JSON.parse(readFileSync(store.path(id))); record.payload.text = 'damaged';
  writeFileSync(store.path(id), JSON.stringify(record));
  assert.match(store.list().find(r => r.id === id).error, /integrity/);
  const target = join(path, 'untouched'); writeFileSync(target, 'capture bytes'); symlinkSync(target, store.path(linked));
  assert.throws(() => store.save(linked, 'unsafe', {}), /regular file/);
  assert.equal(readFileSync(target, 'utf8'), 'capture bytes');
});
test('a dead process lock is reported without racing another recovering writer', t => {
  const { path, store } = library(t); store.close();
  writeFileSync(join(path, '.writer.lock'), JSON.stringify({ pid: 2147483647, owner: 'dead' }));
  const before = readFileSync(join(path, '.writer.lock'));
  assert.throws(() => new LocalDraftStore(path), /stale writer lock/);
  assert.deepEqual(readFileSync(join(path, '.writer.lock')), before);
});

test('post-replacement durability uncertainty reports committed generation for safe retry', t => {
  let fail = true;
  const { store } = library(t, { afterRename: () => { if (fail) throw new Error('directory flush unavailable'); } });
  const id = randomUUID();
  assert.throws(() => store.save(id, 'draft', { text: 'retained' }), error => {
    assert.match(error.message, /durability is uncertain/); assert.equal(error.generation, 1); return true;
  });
  assert.equal(store.read(id).payload.text, 'retained');
  fail = false; assert.equal(store.save(id, 'retry', { text: 'retained' }, 1).generation, 2);
});
