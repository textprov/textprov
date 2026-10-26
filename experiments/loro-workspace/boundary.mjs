/** Stage-one in-memory boundary. Positions are visible UTF-16 grapheme boundaries. */
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { LoroDoc, UndoManager } from 'loro-crdt';

const codecPath = fileURLToPath(new URL('./codec.py', import.meta.url));
const key = 'textprov';

function codec(request) {
  const ran = spawnSync(process.env.TEXTPROV_PYTHON || 'python3', [codecPath], {
    input: JSON.stringify(request), encoding: 'utf8', maxBuffer: 8 * 1024 * 1024,
  });
  if (ran.error) throw ran.error;
  let answer;
  try { answer = JSON.parse(ran.stdout); }
  catch { throw new Error(`TextProv codec failed: ${ran.stderr || ran.stdout}`); }
  if (ran.status !== 0 || answer.error) throw new Error(answer.error || ran.stderr);
  return answer.result;
}

export const decode = text => codec({ operation: 'decode', text });
export const reviseChat = (before, text) => codec({ operation: 'revise-chat', before, text })
  .map(token => token.raw).join('');

function delta(tokens) {
  return tokens.map(token => ({ insert: token.visible, attributes: { [key]: token } }));
}

function equal(a, b) {
  return a?.raw === b?.raw && a?.state === b?.state && a?.visible === b?.visible;
}

export class AttributedText {
  constructor(portable = '') {
    const tokens = decode(portable);
    this.doc = new LoroDoc();
    this.doc.configTextStyle({ [key]: { expand: 'none' } });
    this.text = this.doc.getText('body');
    this.text.applyDelta(delta(tokens));
    this.doc.commit();
    this.history = new UndoManager(this.doc, { mergeInterval: 0 });
  }

  tokens() {
    const result = [];
    for (const run of this.text.toDelta()) {
      const token = run.attributes?.[key];
      if (!token || typeof run.insert !== 'string') throw new Error('missing attribution metadata');
      if (typeof token.raw !== 'string' || typeof token.visible !== 'string' || !token.visible.length ||
          ![null, 'human', 'ai'].includes(token.state)) throw new Error('invalid attribution metadata');
      // Loro coalesces identical adjacent attributes (e.g. repeated letters).
      if (!run.insert.length || run.insert.length % token.visible.length !== 0 ||
          token.visible.repeat(run.insert.length / token.visible.length) !== run.insert) {
        throw new Error('visible text does not match attribution metadata');
      }
      for (let i = 0; i < run.insert.length; i += token.visible.length) result.push({ ...token });
    }
    // Reject a joined grapheme across run boundaries instead of splitting it.
    const roundtrip = decode(result.map(t => t.raw).join(''));
    if (roundtrip.length !== result.length || !roundtrip.every((t, i) => equal(t, result[i]))) {
      throw new Error('inconsistent grapheme attribution boundaries');
    }
    return result;
  }

  portable() { return this.tokens().map(t => t.raw).join(''); }
  visible() { return this.text.toString(); }

  range(start, end, tokens = this.tokens()) {
    const boundaries = [0];
    for (const t of tokens) boundaries.push(boundaries.at(-1) + t.visible.length);
    if (!Number.isInteger(start) || !Number.isInteger(end) || start > end ||
        !boundaries.includes(start) || !boundaries.includes(end)) {
      throw new Error('selection must use visible UTF-16 grapheme boundaries');
    }
    return [boundaries.indexOf(start), boundaries.indexOf(end)];
  }

  copy(start = 0, end = this.visible().length) {
    const tokens = this.tokens();
    const [a, b] = this.range(start, end, tokens);
    return tokens.slice(a, b).map(t => t.raw).join('');
  }

  replace(start, end, inserted, { actor = 'human', destination = 'draft' } = {}) {
    const old = this.tokens();
    const [a, b] = this.range(start, end, old);
    const raw = list => list.map(t => t.raw).join('');
    const next = codec({ operation: 'edit', before: raw(old.slice(0, a)),
      removed: raw(old.slice(a, b)), inserted, after: raw(old.slice(b)), actor, destination });
    // Preserve unchanged Loro content, including marks omitted by an AI edit.
    let prefix = 0;
    while (prefix < Math.min(old.length, next.length) && equal(old[prefix], next[prefix])) prefix++;
    let suffix = 0;
    while (suffix < Math.min(old.length, next.length) - prefix &&
           equal(old.at(-suffix - 1), next.at(-suffix - 1))) suffix++;
    const length = list => list.reduce((n, t) => n + t.visible.length, 0);
    const edits = [];
    const retain = length(old.slice(0, prefix));
    const removed = length(old.slice(prefix, old.length - suffix));
    if (retain) edits.push({ retain });
    if (removed) edits.push({ delete: removed });
    edits.push(...delta(next.slice(prefix, next.length - suffix)));
    if (!removed && !edits.some(e => 'insert' in e)) return;
    this.text.applyDelta(edits);
    this.doc.commit();
  }

  undo() { return this.history.undo(); }
  redo() { return this.history.redo(); }
  close() { this.history.free(); this.doc.free(); }
}
