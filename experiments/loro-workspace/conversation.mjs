/** Explicit, local conversation import with durable identity-based replay. */
import { spawnSync } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { basename, dirname, isAbsolute, join, resolve } from 'node:path';
import { existsSync, readFileSync, openSync, writeFileSync, fsyncSync,
  closeSync, renameSync, unlinkSync, lstatSync, realpathSync } from 'node:fs';
import { LoroDoc, LoroMap, LoroText } from 'loro-crdt';
import { decode, reviseChat } from './boundary.mjs';

export function readConversation(selection) {
  const ran = spawnSync(process.env.TEXTPROV_PYTHON || 'python3',
    [fileURLToPath(new URL('./chronicle_import.py', import.meta.url))], {
      input: JSON.stringify(selection), encoding: 'utf8', maxBuffer: 128 * 1024 * 1024,
    });
  if (ran.error) throw ran.error;
  let answer;
  try { answer = JSON.parse(ran.stdout); }
  catch { throw new Error(`Chronicle import bridge failed: ${ran.stderr || ran.stdout}`); }
  if (ran.status !== 0 || answer.error) throw new Error(answer.error || ran.stderr);
  return answer.result;
}

function configuredDoc(snapshot) {
  const doc = new LoroDoc();
  doc.configTextStyle({ textprov: { expand: 'none' } });
  try {
    if (snapshot) doc.import(snapshot);
    return doc;
  } catch (error) { doc.free(); throw error; }
}

function setBody(container, portable) {
  const body = container.setContainer('body', new LoroText());
  body.applyDelta(decode(portable).map(token => ({ insert: token.visible,
    attributes: { textprov: token } })));
}

function bodyText(message) {
  if (message.get('capture').portable === null) return null;
  return message.get('body').toString();
}

// JSON object key order is immaterial to capture identity or scope equality.
function canonical(value) {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value && typeof value === 'object') return '{' + Object.keys(value).sort()
    .map(k => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}';
  return JSON.stringify(value);
}

function persist(path, bytes) {
  if (!isAbsolute(path) || !existsSync(dirname(path))) throw new Error('workspace needs an absolute path with an existing parent');
  if (existsSync(path) && (!lstatSync(path).isFile() || lstatSync(path).isSymbolicLink())) {
    throw new Error('workspace must be a regular file, not a symlink');
  }
  const temporary = path + '.' + randomUUID() + '.tmp';
  let fd;
  try {
    fd = openSync(temporary, 'wx', 0o600);
    writeFileSync(fd, bytes);
    fsyncSync(fd);
    closeSync(fd); fd = undefined;
    renameSync(temporary, path);
    fd = openSync(dirname(path), 'r');
    fsyncSync(fd);
  } finally {
    if (fd !== undefined) closeSync(fd);
    if (existsSync(temporary)) unlinkSync(temporary);
  }
}

export class ConversationWorkspace {
  constructor(path) {
    if (!isAbsolute(path)) throw new Error('workspace must be an absolute explicitly selected path');
    this.path = join(realpathSync(dirname(path)), basename(path));
    if (existsSync(this.path) && (!lstatSync(this.path).isFile() || lstatSync(this.path).isSymbolicLink())) {
      throw new Error('workspace must be a regular file, not a symlink');
    }
    this.lock = this.path + '.lock';
    this.lockFd = openSync(this.lock, 'wx', 0o600);
    try {
      const existing = existsSync(this.path);
      this.doc = configuredDoc(existing ? readFileSync(this.path) : undefined);
      const schema = this.doc.getMap('config').get('schema');
      if ((existing || schema !== undefined) && schema !== 1) throw new Error('unsupported workspace schema');
    } catch (error) {
      this.doc?.free(); closeSync(this.lockFd); unlinkSync(this.lock); throw error;
    }
  }

  importSelected(selection) {
    if (resolve(selection.database) === this.path) throw new Error('workspace must not overwrite the capture database');
    const batch = readConversation(selection);
    if (resolve(batch.scope.source_path) === this.path) throw new Error('workspace must not overwrite the capture database');
    const current = this.doc.getMap('config').get('scope');
    if (current && canonical(current) !== canonical(batch.scope)) throw new Error('selection differs from this workspace; select a separate workspace file');
    const candidate = configuredDoc(this.doc.export({ mode: 'snapshot' }));
    const counts = { added: 0, duplicates: 0, placeholders: 0, hydrated: 0,
      skippedNonchat: batch.skipped_nonchat };
    try {
      const messages = candidate.getMap('messages');
      const order = candidate.getList('order');
      for (const item of batch.items) {
        const existing = messages.get(item.identity);
        if (existing) {
          const capture = existing.get('capture');
          if (canonical(capture.metadata) !== canonical(item.metadata) || capture.role !== item.role) {
            throw new Error('capture identity reused with changed hash or metadata: ' + item.metadata.observation_id);
          }
          if (capture.portable !== null && item.portable !== null && capture.portable !== item.portable) {
            throw new Error('capture identity reused with changed portable content');
          }
          if (capture.portable === null && item.portable !== null) {
            existing.set('capture', item);
            setBody(existing, item.portable);
            counts.hydrated++;
          }
          counts.duplicates++;
          continue; // A later cache expiry never erases deliberately retained text or revisions.
        }
        const message = messages.setContainer(item.identity, new LoroMap());
        message.set('capture', item);
        if (item.portable !== null) setBody(message, item.portable);
        else counts.placeholders++;
        order.push(item.identity);
        counts.added++;
      }
      const config = candidate.getMap('config');
      config.set('schema', 1);
      config.set('scope', batch.scope);
      config.set('policy', batch.policy);
      config.set('lastImport', { newestObservation: batch.newest_observation, readAt: batch.read_at });
      candidate.commit();
      persist(this.path, candidate.export({ mode: 'snapshot' }));
    } catch (error) { candidate.free(); throw error; }
    this.doc.free(); this.doc = candidate;
    return counts;
  }

  messages() {
    const messages = this.doc.getMap('messages');
    return this.doc.getList('order').toArray().map(identity => {
      const message = messages.get(identity);
      return { identity, ...message.get('capture'), visible: bodyText(message) };
    });
  }

  revise(identity, portable, { baseRevision = null } = {}) {
    const message = this.doc.getMap('messages').get(identity);
    if (!message) throw new Error('unknown message');
    const base = baseRevision === null ? null : this.doc.getMap('revisions').get(baseRevision);
    if (baseRevision !== null && (!base || base.get('message') !== identity)) {
      throw new Error('revision base is not a revision of this message');
    }
    const marked = reviseChat(base ? base.get('portable') : (message.get('capture').portable || ''), portable);
    const candidate = configuredDoc(this.doc.export({ mode: 'snapshot' }));
    const id = randomUUID();
    try {
      const revision = candidate.getMap('revisions').setContainer(id, new LoroMap());
      revision.set('message', identity);
      revision.set('parentRevision', baseRevision);
      revision.set('portable', marked);
      setBody(revision, marked);
      candidate.commit();
      persist(this.path, candidate.export({ mode: 'snapshot' }));
    } catch (error) { candidate.free(); throw error; }
    this.doc.free(); this.doc = candidate;
    return id;
  }

  revisions() { return this.doc.getMap('revisions').toJSON(); }
  close() { this.doc.free(); closeSync(this.lockFd); unlinkSync(this.lock); }
}
