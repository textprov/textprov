/** Local UI controller. No capture reads or persistence; caller supplies a workspace. */
import { DraftReplica } from './draft.mjs';
import { decode } from './boundary.mjs';

export class UISession {
  constructor(workspace) { this.workspace = workspace; this.replicas = [];
    this.messages = workspace.messages().map(m => ({ ...m, tokens: m.portable === null ? [] : decode(m.portable) })); }
  state() {
    return { messages: this.messages, replicas: this.replicas.map(r => r.inspect()),
      sources: this.replicas[0]?.sources() || [] };
  }
  execute(command) {
    if (command.operation === 'restore') {
      if (this.replicas.length) throw new Error('restart before restoring another draft');
      if (command.saved?.format !== 'textprov-local-draft-1') throw new Error('unsupported checkpoint');
      const a = DraftReplica.restore({ snapshot: new Uint8Array(Buffer.from(command.saved.snapshot, 'base64')),
        pending: command.saved.pending ? new Uint8Array(Buffer.from(command.saved.pending, 'base64')) : undefined });
      this.replicas = [a, a.fork()];
      return this.state();
    }
    if (command.operation === 'select') {
      if (this.replicas.length) throw new Error('a draft already exists; restart to select a new draft');
      const a = DraftReplica.fromConversation(this.workspace, command.selections);
      this.replicas = [a, a.fork()];
      return this.state();
    }
    if (command.operation === 'decode') return decode(command.text);
    if (command.operation === 'sync') {
      if (this.replicas.length !== 2) throw new Error('select passages first');
      const [a, b] = this.replicas;
      const au = a.update(b.version()), bu = b.update(a.version());
      a.receive(bu); b.receive(au);
      return this.state();
    }
    const r = this.replicas[command.replica];
    if (!r) throw new Error('select a valid draft replica');
    if (command.expectedHash !== r.inspect().reviewHash) throw new Error('draft changed; refresh before editing or copying');
    switch (command.operation) {
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
    return this.state();
  }
  close() { this.replicas.forEach(r => r.close()); }
}
