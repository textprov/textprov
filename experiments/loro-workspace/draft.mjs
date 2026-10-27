/** Local shared draft: selected passage copies, independent replicas, explicit conflicts. */
import { createHash, randomUUID } from 'node:crypto';
import { LoroDoc, VersionVector } from 'loro-crdt';
import { AttributedText, decode } from './boundary.mjs';

const hash = text => createHash('sha256').update(text, 'utf8').digest('hex');
function validateEdits(doc) {
  for (const edit of Object.values(doc.getMap('edits').toJSON())) {
    if (!edit || !Array.isArray(edit.seen) || !edit.seen.every(id => typeof id === 'string') ||
        !Array.isArray(edit.footprint) || !edit.footprint.every(id => typeof id === 'string') ||
        !(edit.anchor === null || typeof edit.anchor === 'string') ||
        typeof edit.insertion !== 'boolean' || !['human', 'assistant'].includes(edit.actor) ||
        !Number.isInteger(edit.start) || !Number.isInteger(edit.end) || edit.start < 0 || edit.end < edit.start ||
        typeof edit.baseHash !== 'string' || !/^[a-f0-9]{64}$/.test(edit.baseHash)) {
      throw new Error('invalid shared draft edit metadata');
    }
  }
  for (const resolution of Object.values(doc.getMap('resolutions').toJSON())) {
    if (!resolution || !Array.isArray(resolution.pairs) ||
        !resolution.pairs.every(pair => Array.isArray(pair) && pair.length === 2 && pair.every(id => typeof id === 'string')) ||
        typeof resolution.reviewedHash !== 'string' || !/^[a-f0-9]{64}$/.test(resolution.reviewedHash) ||
        typeof resolution.resultHash !== 'string' || !/^[a-f0-9]{64}$/.test(resolution.resultHash)) {
      throw new Error('invalid shared draft resolution metadata');
    }
  }
}
function signature(value) {
  if (Array.isArray(value)) return '[' + value.map(signature).join(',') + ']';
  if (value && typeof value === 'object') return '{' + Object.keys(value).sort()
    .map(k => JSON.stringify(k) + ':' + signature(value[k])).join(',') + '}';
  return JSON.stringify(value);
}

function docFrom(checkpoint) {
  const doc = new LoroDoc();
  doc.configTextStyle({ textprov: { expand: 'none' } });
  try {
    if (checkpoint) {
      doc.import(checkpoint.snapshot);
      if (checkpoint.pending) doc.import(checkpoint.pending);
    }
    return doc;
  } catch (error) { doc.free(); throw error; }
}

function checkpoint(doc) {
  return { snapshot: doc.export({ mode: 'snapshot' }), pending: doc.exportPendingUpdates() };
}

function selectedPassage(workspace, selection) {
  const message = workspace.messages().find(m => m.identity === selection.message);
  if (!message) throw new Error('selected message is outside this conversation');
  let portable = message.portable;
  const revisionId = selection.revision || null;
  if (revisionId !== null) {
    const revision = workspace.revisions()[revisionId];
    if (!revision || revision.message !== selection.message) throw new Error('selected revision is not part of this message');
    portable = revision.portable;
  }
  if (portable === null) throw new Error('selected passage content is unavailable');
  const sourceHash = hash(portable);
  if (selection.expectedHash !== undefined && selection.expectedHash !== sourceHash) throw new Error('selected source hash is stale');
  const body = new AttributedText(portable);
  let passage;
  try { passage = body.copy(selection.start, selection.end); }
  finally { body.close(); }
  if (!passage.length) throw new Error('select a nonempty passage');
  return {
    id: randomUUID(), message: selection.message, observationId: message.metadata.observation_id,
    originalContentHash: message.metadata.content_hash, revision: revisionId,
    sourceHash, passageHash: hash(passage), coordinateSystem: 'visible-utf16-grapheme-boundaries',
    start: selection.start, end: selection.end, completeness: message.metadata.completeness,
    portable: passage,
  };
}

export class DraftReplica {
  static fromConversation(workspace, selections, { title = 'Shared draft' } = {}) {
    if (!Array.isArray(selections) || !selections.length) throw new Error('select at least one passage');
    if (typeof title !== 'string') throw new Error('draft title must be text');
    // Validate every selection before constructing a draft or changing any source.
    const sources = selections.map(s => selectedPassage(workspace, s));
    const doc = docFrom();
    try {
      doc.getMap('draft').set('header', { schema: 1, id: randomUUID(), title,
        sourceNamespace: workspace.doc.getMap('config').get('scope').namespace, sources });
      doc.getText('body').applyDelta(decode(sources.map(s => s.portable).join('\n\n'))
        .map(token => ({ insert: token.visible, attributes: { textprov: token } })));
      doc.commit();
      return new DraftReplica(doc);
    } catch (error) { doc.free(); throw error; }
  }

  static restore(saved) {
    const doc = docFrom(saved);
    try { return new DraftReplica(doc); } catch (error) { doc.free(); throw error; }
  }

  constructor(doc) {
    this.doc = doc;
    this.header = doc.getMap('draft').get('header');
    if (!this.header || this.header.schema !== 1) throw new Error('not a supported shared draft');
    validateEdits(doc);
    this.body = AttributedText.bind(doc, doc.getText('body'));
  }

  fork() { return DraftReplica.restore(this.checkpoint()); }
  checkpoint() { return checkpoint(this.doc); }
  sources() { return structuredClone(this.header.sources); }
  visible() { return this.body.visible(); }
  inspect() { return { text: this.visible(), tokens: this.body.tokens(), conflicts: this.conflicts(),
    reviewHash: hash(this.body.portable()) }; }

  portable() {
    if (this.conflicts().length) throw new Error('concurrent overlapping edits need review before copying or exporting');
    return this.body.portable();
  }

  copy(start = 0, end = this.visible().length) {
    this.portable();
    return this.body.copy(start, end);
  }

  version() {
    const version = this.doc.version();
    try { return version.encode(); } finally { version.free(); }
  }

  update(from) {
    const version = from ? VersionVector.decode(from) : undefined;
    try { return { draftId: this.header.id,
      bytes: this.doc.export({ mode: 'update', ...(version ? { from: version } : {}) }) }; }
    finally { version?.free(); }
  }

  receive(envelope) {
    if (envelope.draftId !== this.header.id || !(envelope.bytes instanceof Uint8Array)) {
      throw new Error('update belongs to another draft or is not binary');
    }
    // Preflight pending and newly applied operations without damaging live state
    // or recreating the live UndoManager. No operations interleave here.
    const candidate = docFrom(this.checkpoint());
    try {
      const result = candidate.import(envelope.bytes);
      if (signature(candidate.getMap('draft').get('header')) !== signature(this.header)) {
        throw new Error('draft source references or identity were changed');
      }
      validateEdits(candidate);
      const value = AttributedText.bind(candidate, candidate.getText('body'));
      value.close();
      this.doc.import(envelope.bytes);
      return { pending: (result.pending?.size || 0) > 0, conflicts: this.conflicts() };
    } finally { candidate.free(); }
  }

  replace(start, end, portable, { actor = 'human' } = {}) {
    if (this.conflicts().length) throw new Error('concurrent overlapping edits need review before further edits');
    this.#edit(start, end, portable, actor, true);
  }

  #edit(start, end, portable, actor, manageGroup) {
    const old = this.body.tokens();
    this.body.range(start, end, old);
    const seen = Object.keys(this.doc.getMap('edits').toJSON());
    // Stable Loro character IDs identify removed graphemes across index shifts.
    const footprint = [];
    let offset = 0;
    let anchor = null;
    for (const token of old) {
      if ((offset >= start && offset < end) || offset === start) {
        const cursor = this.body.text.getCursor(offset, 0);
        try {
          const id = cursor?.pos();
          if (id) {
            const key = `${id.peer}:${id.counter}`;
            if (offset >= start && offset < end) footprint.push(key);
            if (offset === start) anchor = key;
          }
        } finally { cursor?.free(); }
      }
      offset += token.visible.length;
    }
    const before = this.body.portable();
    if (manageGroup) this.body.history.groupStart();
    try {
      this.body.replace(start, end, portable, { actor, destination: 'draft' });
      if (this.body.portable() === before) return;
      this.doc.getMap('edits').set(randomUUID(), { seen, footprint, anchor,
        insertion: start === end, actor, start, end, baseHash: hash(before) });
      this.doc.commit();
    } finally { if (manageGroup) this.body.history.groupEnd(); }
  }

  resolve(portable, { expectedHash, actor = 'human' } = {}) {
    const conflicts = this.conflicts();
    if (!conflicts.length) throw new Error('no overlapping edits need resolution');
    const reviewedHash = hash(this.body.portable());
    if (expectedHash !== reviewedHash) throw new Error('resolution base changed; review the current draft');
    decode(portable);
    this.body.history.groupStart();
    try {
      this.#edit(0, this.visible().length, portable, actor, false);
      this.doc.getMap('resolutions').set(randomUUID(), { pairs: conflicts.map(c => c.edits),
        reviewedHash, resultHash: hash(this.body.portable()) });
      this.doc.commit();
    } finally { this.body.history.groupEnd(); }
  }

  prepareEdit(start, end, portable, { actor = 'assistant' } = {}) {
    this.body.range(start, end);
    decode(portable);
    return { draftId: this.header.id, baseHash: hash(this.body.portable()), start, end, portable, actor };
  }

  applyPrepared(proposal) {
    if (proposal.draftId !== this.header.id) throw new Error('proposal belongs to another draft');
    if (proposal.baseHash !== hash(this.body.portable())) return { applied: false, reason: 'stale-base', proposal };
    this.replace(proposal.start, proposal.end, proposal.portable, { actor: proposal.actor });
    return { applied: true };
  }

  conflicts() {
    const edits = Object.entries(this.doc.getMap('edits').toJSON()).sort(([a], [b]) => a.localeCompare(b));
    const resolved = new Set(Object.values(this.doc.getMap('resolutions').toJSON())
      .flatMap(r => r.pairs.map(pair => [...pair].sort().join(':'))));
    const conflicts = [];
    for (let i = 0; i < edits.length; i++) for (let j = i + 1; j < edits.length; j++) {
      const [aId, a] = edits[i], [bId, b] = edits[j];
      if (resolved.has([aId, bId].sort().join(':'))) continue;
      if (a.seen.includes(bId) || b.seen.includes(aId)) continue;
      const overlap = a.footprint.some(id => b.footprint.includes(id)) ||
        (a.insertion && a.anchor !== null && b.footprint.includes(a.anchor)) ||
        (b.insertion && b.anchor !== null && a.footprint.includes(b.anchor));
      if (overlap) conflicts.push({ edits: [aId, bId], reason: 'concurrent-overlap' });
    }
    return conflicts;
  }

  undo() {
    if (this.conflicts().length) throw new Error('review overlapping edits instead of undoing concurrent deletions');
    return this.body.undo();
  }
  redo() {
    if (this.conflicts().length) throw new Error('review overlapping edits before redo');
    return this.body.redo();
  }
  close() { this.body.close(); this.doc.free(); }
}
