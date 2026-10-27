/** Private local draft library. Separate from Chronicle and plugin configuration. */
import { randomUUID, createHash } from 'node:crypto';
import { mkdirSync, lstatSync, realpathSync, openSync, closeSync, writeFileSync, readFileSync,
  fsyncSync, renameSync, unlinkSync, existsSync, readdirSync } from 'node:fs';
import { join, isAbsolute } from 'node:path';
const validId = id => typeof id === 'string' && /^[a-f0-9-]{36}$/.test(id);
const digest = value => createHash('sha256').update(JSON.stringify(value)).digest('hex');

export class LocalDraftStore {
  constructor(directory, { beforeCommit = () => {}, afterRename = () => {} } = {}) {
    if (!isAbsolute(directory)) throw new Error('draft library needs an absolute directory');
    mkdirSync(directory, { recursive: true, mode: 0o700 });
    if (!lstatSync(directory).isDirectory() || lstatSync(directory).isSymbolicLink()) throw new Error('draft library must be a real directory');
    if ((lstatSync(directory).mode & 0o077) !== 0) throw new Error('draft library must be private (directory mode 0700)');
    this.directory = realpathSync(directory); this.beforeCommit = beforeCommit; this.afterRename = afterRename;
    this.lock = join(this.directory, '.writer.lock'); this.owner = randomUUID();
    if (existsSync(this.lock)) {
      if (lstatSync(this.lock).isSymbolicLink()) throw new Error('invalid draft library lock');
      let owner;
      try { owner = JSON.parse(readFileSync(this.lock, 'utf8')); } catch { throw new Error('unreadable draft library lock; inspect it before recovery'); }
      if (!Number.isInteger(owner.pid) || owner.pid <= 0) throw new Error('invalid draft library lock');
      try { process.kill(owner.pid, 0); throw new Error('draft library is already open in another process'); }
      catch (error) { if (error.code !== 'ESRCH') throw error; }
      throw new Error('draft library has a stale writer lock; stop all workspace servers, then remove ' + this.lock + ' before reopening');
    }
    const fd = openSync(this.lock, 'wx', 0o600);
    try { writeFileSync(fd, JSON.stringify({ pid: process.pid, owner: this.owner })); fsyncSync(fd); }
    finally { closeSync(fd); }
  }
  path(id) { if (!validId(id)) throw new Error('invalid saved draft ID'); return join(this.directory, id + '.json'); }
  read(id) {
    const path = this.path(id);
    if (!lstatSync(path).isFile() || lstatSync(path).isSymbolicLink()) throw new Error('saved draft must be a regular file');
    const record = JSON.parse(readFileSync(path, 'utf8'));
    if (record.format !== 'textprov-local-workspace-1' || record.id !== id ||
        !Number.isInteger(record.generation) || record.generation < 1 ||
        typeof record.title !== 'string' || typeof record.savedAt !== 'string' || record.hash !== digest(record.payload)) {
      throw new Error('saved draft integrity check failed');
    }
    return record;
  }
  list() {
    return readdirSync(this.directory).filter(name => /^[a-f0-9-]{36}\.json$/.test(name)).map(name => {
      const id = name.slice(0, -5);
      try { const { title, savedAt, generation } = this.read(id); return { id, title, savedAt, generation }; }
      catch (error) { return { id, error: error.message }; }
    }).sort((a, b) => (b.savedAt || '').localeCompare(a.savedAt || ''));
  }
  save(id, title, payload, expectedGeneration = 0) {
    const path = this.path(id);
    const generation = existsSync(path) ? this.read(id).generation : 0;
    if (generation !== expectedGeneration) throw new Error('saved draft changed; reopen before overwriting');
    const record = { format: 'textprov-local-workspace-1', id, title, savedAt: new Date().toISOString(),
      generation: generation + 1, hash: digest(payload), payload };
    const temporary = join(this.directory, '.' + randomUUID() + '.tmp');
    let fd, renamed = false;
    try {
      fd = openSync(temporary, 'wx', 0o600); writeFileSync(fd, JSON.stringify(record)); fsyncSync(fd); closeSync(fd); fd = undefined;
      this.beforeCommit(record);
      renameSync(temporary, path); renamed = true; this.afterRename(record);
      fd = openSync(this.directory, 'r'); fsyncSync(fd);
      return record;
    } catch (error) {
      if (renamed) { error.generation = record.generation; error.message = 'save replaced the file but durability is uncertain: ' + error.message; }
      throw error;
    } finally {
      if (fd !== undefined) closeSync(fd);
      if (existsSync(temporary)) unlinkSync(temporary);
    }
  }
  close() {
    if (this.closed) return;
    this.closed = true;
    if (existsSync(this.lock) && JSON.parse(readFileSync(this.lock, 'utf8')).owner === this.owner) unlinkSync(this.lock);
  }
}
