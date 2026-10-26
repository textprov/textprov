/** Local workspace controller; capture input and the private draft store stay separate. */
import { createPublication, exportMarkedText } from './publication.mjs';
import { DraftReplica } from './draft.mjs';
import { ResponseAttempts } from './responses.mjs';
import { randomUUID } from 'node:crypto';
import { decode } from './boundary.mjs';

export class UISession {
  constructor(workspace, { store, simulationDelay = 500, label = 'Disposable sample conversation' } = {}) { this.workspace = workspace; this.replicas = [];
    this.sourceLabel = label; this.initialLabel = label; this.publication = null;
    this.responses = new ResponseAttempts(); this.timers = new Map(); this.simulationDelay = simulationDelay;
    this.store = store; this.savedId = null; this.generation = 0; this.title = 'Untitled draft'; this.savedAt = null; this.saveError = null;
    this.messages = workspace.messages().map(m => ({ ...m, tokens: m.portable === null ? [] : decode(m.portable) })); }
  state() {
    return { draftId: this.replicas[0]?.header.id || null, versions: this.replicas.map(r => Buffer.from(r.version()).toString('base64')), label: this.sourceLabel, messages: this.messages, replicas: this.replicas.map(r => r.inspect()),
      sources: this.replicas[0]?.sources() || [], persistence: { enabled: !!this.store, id: this.savedId, title: this.title, savedAt: this.savedAt, error: this.saveError, directory: this.store?.directory }, savedDrafts: this.store?.list() || [], responses: this.responseState() };
  }
  checkpoint(replica) {
    const saved = replica.checkpoint();
    return { snapshot: Buffer.from(saved.snapshot).toString('base64'), pending: Buffer.from(saved.pending || []).toString('base64') };
  }
  restoreReplica(saved) {
    return DraftReplica.restore({ snapshot: new Uint8Array(Buffer.from(saved.snapshot, 'base64')),
      pending: saved.pending ? new Uint8Array(Buffer.from(saved.pending, 'base64')) : undefined });
  }
  save() {
    if (!this.store || !this.replicas.length) return;
    this.savedId ||= randomUUID();
    try {
      const record = this.store.save(this.savedId, this.title, { replicas: this.replicas.map(r => this.checkpoint(r)),
        label: this.sourceLabel, messages: this.messages.map(({ tokens, ...m }) => m), responses: this.responses.snapshot() }, this.generation);
      this.generation = record.generation; this.savedAt = record.savedAt; this.saveError = null;
    } catch (error) { if (error.generation) this.generation = error.generation; this.saveError = error.message; }
  }
  changed() { this.save(); return this.state(); }
  execute(command) {
    if (command.operation === 'publication-export') {
      const snapshot = this.publication;
      if (!snapshot || command.id !== snapshot.id || command.hash !== snapshot.hash) throw new Error('publication preview changed; create or refresh the preview');
      return { format: 'textprov-marked-text-1', filename: 'textprov-publication.txt', mediaType: 'text/plain;charset=utf-8',
        hash: snapshot.hash, portable: exportMarkedText(snapshot) };
    }
    if (command.operation === 'save') {
      if (typeof command.title === 'string' && command.title.trim()) this.title = command.title.trim().slice(0, 200);
      return this.changed();
    }
    if (command.operation === 'open' || command.operation === 'new') {
      this.save();
      if (this.saveError) throw new Error('current draft could not be saved: ' + this.saveError);
      if (command.operation === 'new') {
        this.publication = null; this.stopTimers(); this.responses = new ResponseAttempts();
        this.replicas.forEach(r => r.close()); this.replicas = [];
        this.messages = this.workspace.messages().map(m => ({ ...m, tokens: m.portable === null ? [] : decode(m.portable) }));
        this.sourceLabel = this.initialLabel;
        this.savedId = null; this.generation = 0; this.savedAt = null; this.title = 'Untitled draft';
        return this.state();
      }
      if (!this.store) throw new Error('local saving is not enabled');
      const record = this.store.read(command.id);
      if (record.payload.replicas?.length !== 2 || !Array.isArray(record.payload.messages)) throw new Error('invalid saved workspace');
      const next = [];
      let messages, responses;
      try {
        for (const saved of record.payload.replicas) next.push(this.restoreReplica(saved));
        if (next[0].header.id !== next[1].header.id) throw new Error('saved replicas belong to different drafts');
        responses = new ResponseAttempts(record.payload.responses);
        messages = record.payload.messages.map(m => ({ ...m, tokens: m.portable === null ? [] : decode(m.portable) }));
      } catch (error) { next.forEach(r => r.close()); throw error; }
      this.publication = null; this.stopTimers(); this.responses = responses;
      this.replicas.forEach(r => r.close()); this.replicas = next; this.messages = messages;
      this.sourceLabel = record.payload.label || 'Retained source conversation';
      this.savedId = record.id; this.generation = record.generation; this.title = record.title; this.savedAt = record.savedAt;
      return this.changed();
    }
    if (command.operation === 'restore') {
      if (this.replicas.length) throw new Error('restart before restoring another draft');
      if (command.saved?.format !== 'textprov-local-draft-1') throw new Error('unsupported checkpoint');
      const a = DraftReplica.restore({ snapshot: new Uint8Array(Buffer.from(command.saved.snapshot, 'base64')),
        pending: command.saved.pending ? new Uint8Array(Buffer.from(command.saved.pending, 'base64')) : undefined });
      this.replicas = [a, a.fork()];
      return this.changed();
    }
    if (command.operation === 'select') {
      if (this.replicas.length) throw new Error('a draft already exists; restart to select a new draft');
      const a = DraftReplica.fromConversation(this.workspace, command.selections);
      this.replicas = [a, a.fork()];
      return this.changed();
    }
    if (command.operation === 'decode') return decode(command.text);
    if (command.operation === 'sync') {
      if (this.replicas.length !== 2) throw new Error('select passages first');
      const [a, b] = this.replicas;
      const au = a.update(b.version()), bu = b.update(a.version());
      a.receive(bu); b.receive(au);
      return this.changed();
    }
    if (command.operation === 'response-cancel') {
      this.responses.cancel(command.id); this.stopTimer(command.id); return this.changed();
    }
    const r = this.replicas[command.replica];
    if (!r) throw new Error('select a valid draft replica');
    if (command.expectedHash !== r.inspect().reviewHash) throw new Error('draft changed; refresh before editing or copying');
    switch (command.operation) {
      case 'publication-preview': {
        const snapshot = createPublication(r, { title: command.title || this.title });
        this.publication = structuredClone(snapshot);
        return snapshot;
      }
      case 'response-start':
      case 'response-regenerate': {
        if (typeof command.simulatedText !== 'string' || !command.simulatedText.length || command.simulatedText.length > 32000) throw new Error('provide 1–32000 simulated response characters');
        decode(command.simulatedText);
        if (this.responses.list().length >= 32) throw new Error('this prototype supports 32 attempts per draft');
        if (this.responses.list().some(a => a.status === 'streaming')) throw new Error('cancel or finish the current response first');
        const attempt = command.operation === 'response-start'
          ? this.responses.start(r, { prompt: command.prompt })
          : this.responses.regenerate(command.id, { replica: r, useCurrentContext: command.useCurrentContext === true });
        this.save();
        // Do not start producing tokens while the context/attempt could not be saved.
        if (this.saveError) { this.responses.fail(attempt.id, 'response paused because local saving failed'); return this.changed(); }
        this.schedule(attempt.id, command.simulatedText);
        return this.state();
      }
      case 'response-insert': {
        const attempt = this.responses.inspect(command.id);
        if (attempt.status !== 'completed') throw new Error('only completed responses can be inserted automatically');
        if (this.responses.contextChanged(command.id, r)) throw new Error('draft context changed; inspect the original context or copy a chosen marked passage explicitly');
        r.replace(r.visible().length, r.visible().length, '\n\n' + attempt.portable);
        break;
      }
      case 'edit':
        r.replace(command.start, command.end, command.text, { actor: command.actor || 'human' }); break;
      case 'undo': r.undo(); break;
      case 'redo': r.redo(); break;
      case 'resolve': r.resolve(command.text, { expectedHash: command.expectedHash }); break;
      case 'copy': return { portable: r.copy(command.start, command.end) };
      case 'checkpoint': {
        const saved = r.checkpoint();
        return { format: 'textprov-local-draft-1', snapshot: Buffer.from(saved.snapshot).toString('base64'),
          pending: Buffer.from(saved.pending || []).toString('base64') };
      }
      default: throw new Error('unknown UI operation');
    }
    return this.changed();
  }
  responseState() {
    return this.responses.list().map(({ raw, context, ...attempt }) => ({ ...attempt,
      context: { draftId: context.draftId, portable: context.portable, reviewHash: context.reviewHash,
        version: context.version, sources: context.sources },
      contextChanged: this.replicas[0] ? this.responses.contextChanged(attempt.id, this.replicas[0]) : false }));
  }
  stopTimer(id) { const timer = this.timers.get(id); if (timer) clearTimeout(timer); this.timers.delete(id); }
  stopTimers() { for (const id of this.timers.keys()) this.stopTimer(id); }
  schedule(id, text) {
    const chunks = [...text].reduce((all, char) => {
      if (!all.length || [...all.at(-1)].length >= 12) all.push(char); else all[all.length - 1] += char;
      return all;
    }, []);
    let at = 0;
    const tick = () => {
      this.timers.delete(id);
      if (this.responses.inspect(id).status !== 'streaming') return;
      try {
        this.responses.appendChunk(id, at, chunks[at]); at++;
        if (at === chunks.length) this.responses.finish(id);
        this.save();
        if (this.saveError && this.responses.inspect(id).status === 'streaming') {
          this.responses.fail(id, 'stream stopped because local saving failed'); this.save();
        }
      } catch (error) {
        if (this.responses.inspect(id).status === 'streaming') this.responses.fail(id, error.message);
        this.save();
      }
      if (this.responses.inspect(id).status === 'streaming') this.timers.set(id, setTimeout(tick, this.simulationDelay));
    };
    this.timers.set(id, setTimeout(tick, this.simulationDelay));
  }
  close() { this.stopTimers(); this.replicas.forEach(r => r.close()); }

}
