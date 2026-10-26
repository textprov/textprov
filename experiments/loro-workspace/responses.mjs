/** Local response attempts; no provider calls, clocks, timers, capture writes or settings. */
import { createHash, randomUUID } from 'node:crypto';
import { AttributedText, decode } from './boundary.mjs';

const hash = value => createHash('sha256').update(value, 'utf8').digest('hex');
const copy = value => structuredClone(value);
const statuses = ['streaming', 'completed', 'cancelled', 'failed', 'interrupted'];
const limit = 1024 * 1024;

function chat(text, actor) {
  if (typeof text !== 'string' || text.length > limit) throw new Error('response text must be a bounded string');
  const body = new AttributedText();
  try {
    body.replace(0, 0, text, { actor, destination: 'chat' });
    return { portable: body.portable(), tokens: body.tokens(), text: body.visible() };
  } finally { body.close(); }
}

function captureContext(replica) {
  const portable = replica.portable(); // Conflict review remains a precondition.
  const saved = replica.checkpoint();
  return {
    draftId: replica.header.id, portable, reviewHash: hash(portable),
    version: Buffer.from(replica.version()).toString('base64'),
    snapshot: Buffer.from(saved.snapshot).toString('base64'),
    pending: Buffer.from(saved.pending || []).toString('base64'), sources: replica.sources(),
  };
}

function validateContext(context) {
  if (!context || typeof context.draftId !== 'string' || typeof context.portable !== 'string' ||
      typeof context.version !== 'string' || !context.version || typeof context.snapshot !== 'string' ||
      !context.snapshot || typeof context.pending !== 'string' || !Array.isArray(context.sources) ||
      context.reviewHash !== hash(context.portable)) throw new Error('invalid response context');
  decode(context.portable);
}

function render(raw, final) {
  let candidate = raw;
  // Provider chunks may cut a surrogate pair; never feed an unpaired high half to the codec.
  const last = candidate.charCodeAt(candidate.length - 1);
  if (last >= 0xD800 && last <= 0xDBFF) candidate = candidate.slice(0, -1);
  const tokens = decode(candidate);
  // The final grapheme can still acquire combining marks, a selector, or a ZWJ continuation.
  if (!final) tokens.pop();
  const prefix = tokens.map(t => t.raw).join('');
  return { ...chat(prefix, 'assistant'), publishedLength: prefix.length };
}

export class ResponseAttempts {
  constructor(saved) {
    this.attempts = new Map();
    if (saved === undefined) return;
    if (saved?.format !== 'textprov-response-attempts-1' || !Array.isArray(saved.attempts)) {
      throw new Error('unsupported response attempts snapshot');
    }
    for (const value of saved.attempts) {
      const attempt = copy(value);
      if (!attempt || typeof attempt.id !== 'string' || this.attempts.has(attempt.id) ||
          typeof attempt.rootId !== 'string' || !(attempt.parentId === null || typeof attempt.parentId === 'string') ||
          !statuses.includes(attempt.status) || typeof attempt.prompt !== 'string' ||
          !Number.isInteger(attempt.nextSequence) || attempt.nextSequence < 0 ||
          typeof attempt.raw !== 'string' || attempt.raw.length > limit ||
          !Number.isInteger(attempt.publishedLength) || attempt.publishedLength < 0 || attempt.publishedLength > attempt.raw.length ||
          typeof attempt.createdAt !== 'string' || !(attempt.finishedAt === null || typeof attempt.finishedAt === 'string') ||
          !(attempt.error === null || typeof attempt.error === 'string')) throw new Error('invalid response attempt snapshot');
      validateContext(attempt.context);
      if (attempt.contextHash !== hash(JSON.stringify(attempt.context))) throw new Error('response context changed');
      const prompt = decode(attempt.prompt);
      if (prompt.map(t => t.visible).join('') !== attempt.promptVisible || chat(attempt.prompt, 'human').portable !== attempt.prompt) throw new Error('invalid response prompt');
      const rendered = chat(attempt.raw.slice(0, attempt.publishedLength), 'assistant');
      if (rendered.portable !== attempt.portable || rendered.text !== attempt.text ||
          JSON.stringify(rendered.tokens) !== JSON.stringify(attempt.tokens) ||
          (attempt.status === 'completed' && attempt.publishedLength !== attempt.raw.length)) {
        throw new Error('response snapshot attribution changed');
      }
      if (attempt.status === 'streaming') {
        // Keep exactly what was published and retain its buffered suffix for inspection.
        attempt.status = 'interrupted'; attempt.finishedAt = new Date().toISOString();
        attempt.error = 'local process stopped before the response finished';
      }
      this.attempts.set(attempt.id, attempt);
    }
    for (const attempt of this.attempts.values()) {
      if (attempt.parentId !== null) {
        const parent = this.attempts.get(attempt.parentId);
        if (!parent || parent.rootId !== attempt.rootId) throw new Error('response alternative has no matching parent');
        const seen = new Set([attempt.id]);
        let ancestor = parent;
        while (ancestor) {
          if (seen.has(ancestor.id)) throw new Error('response alternative lineage contains a cycle');
          seen.add(ancestor.id);
          ancestor = ancestor.parentId === null ? null : this.attempts.get(ancestor.parentId);
        }
      } else if (attempt.rootId !== attempt.id) throw new Error('response root identity changed');
    }
  }

  #get(id) {
    const attempt = this.attempts.get(id);
    if (!attempt) throw new Error('unknown response attempt');
    return attempt;
  }

  #streaming(id) {
    const attempt = this.#get(id);
    if (attempt.status !== 'streaming') throw new Error('response attempt is no longer streaming');
    return attempt;
  }

  #start(context, prompt, parent) {
    validateContext(context);
    const markedPrompt = chat(prompt, 'human');
    const id = randomUUID();
    const attempt = {
      id, rootId: parent?.rootId || id, parentId: parent?.id || null, status: 'streaming',
      prompt: markedPrompt.portable, promptVisible: markedPrompt.text,
      context: copy(context), contextHash: hash(JSON.stringify(context)),
      nextSequence: 0, raw: '', publishedLength: 0, portable: '', text: '', tokens: [],
      error: null, createdAt: new Date().toISOString(), finishedAt: null,
    };
    this.attempts.set(id, attempt);
    return this.inspect(id);
  }

  start(replica, { prompt = '' } = {}) { return this.#start(captureContext(replica), prompt, null); }

  regenerate(id, { replica, useCurrentContext = false, prompt } = {}) {
    const parent = this.#get(id);
    if (useCurrentContext && !replica) throw new Error('current-context regeneration needs a draft replica');
    return this.#start(useCurrentContext ? captureContext(replica) : parent.context,
      prompt === undefined ? parent.prompt : prompt, parent);
  }

  appendChunk(id, sequence, text) {
    const attempt = this.#streaming(id);
    if (!Number.isInteger(sequence) || sequence !== attempt.nextSequence) throw new Error('response chunk is duplicated or out of order');
    if (typeof text !== 'string' || attempt.raw.length + text.length > limit) throw new Error('response chunk exceeds the local text limit');
    const raw = attempt.raw + text;
    const rendered = render(raw, false); // Validate before advancing sequence or changing published text.
    Object.assign(attempt, rendered, { raw, nextSequence: sequence + 1 });
    return this.inspect(id);
  }

  finish(id) {
    const attempt = this.#streaming(id);
    const rendered = render(attempt.raw, true);
    if (rendered.publishedLength !== attempt.raw.length) throw new Error('response ends with an incomplete Unicode character');
    Object.assign(attempt, rendered, { status: 'completed', finishedAt: new Date().toISOString() });
    return this.inspect(id);
  }

  cancel(id) { return this.#stop(id, 'cancelled', null); }
  fail(id, error = 'local response failed') {
    if (typeof error !== 'string') throw new Error('response failure needs a text description');
    return this.#stop(id, 'failed', error);
  }

  #stop(id, status, error) {
    const attempt = this.#streaming(id);
    Object.assign(attempt, render(attempt.raw, true), { status, error, finishedAt: new Date().toISOString() });
    return this.inspect(id);
  }

  inspect(id) {
    const attempt = this.#get(id);
    return copy({ ...attempt, pendingText: attempt.raw.slice(attempt.publishedLength) });
  }
  list() { return [...this.attempts.keys()].map(id => this.inspect(id)); }
  clone() {
    // A transaction candidate remains in the same process; only reopening from disk interrupts work.
    const next = new ResponseAttempts();
    for (const [id, attempt] of this.attempts) next.attempts.set(id, copy(attempt));
    return next;
  }
  snapshot() { return { format: 'textprov-response-attempts-1', attempts: [...this.attempts.values()].map(copy) }; }
  contextChanged(id, replica) {
    const context = this.#get(id).context;
    return context.draftId !== replica.header.id || context.reviewHash !== replica.inspect().reviewHash ||
      context.version !== Buffer.from(replica.version()).toString('base64');
  }
}
