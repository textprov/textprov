/** Immutable local publication boundary. Exports source marks, never private history. */
import { createHash, randomUUID } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { marked } from 'marked';
import { decode } from './boundary.mjs';

const hash = value => createHash('sha256').update(value, 'utf8').digest('hex');
const codecPath = fileURLToPath(new URL('./publication-codec.py', import.meta.url));

function plan(source) {
  const leaves = [];
  const collect = (text, kind = 'text') => {
    if (typeof text !== 'string') throw new Error('invalid Markdown publication text');
    const id = leaves.push({ text, kind }) - 1;
    return `\0publication-leaf:${id}\0`;
  };
  const renderer = new marked.Renderer();
  renderer.text = function (token) {
    return token.tokens ? this.parser.parseInline(token.tokens) : collect(token.text);
  };
  renderer.code = ({ text }) => `<pre><code>${collect(text, 'code')}</code></pre>\n`;
  renderer.codespan = ({ text }) => `<code>${collect(text, 'code')}</code>`;
  renderer.html = ({ text, block }) => block
    ? `<pre>${collect(text, 'html')}</pre>\n`
    : `<span class="raw-html">${collect(text, 'html')}</span>`;
  renderer.link = function ({ tokens }) {
    return `<span class="publication-link">${this.parser.parseInline(tokens)}</span>`;
  };
  renderer.image = function ({ tokens, text }) {
    return `<span class="publication-image">[Image: ${tokens ? this.parser.parseInline(tokens) : collect(text)}]</span>`;
  };
  renderer.checkbox = ({ checked }) => `<span class="publication-checkbox">[${checked ? 'x' : ' '}]</span> `;
  return { template: marked.parse(source, { renderer, async: false, gfm: true }), leaves };
}

export function renderPublication(portable) {
  const tokens = decode(portable);
  const text = tokens.map(t => t.visible).join('');
  const ran = spawnSync(process.env.TEXTPROV_PYTHON || 'python3', [codecPath], {
    input: JSON.stringify({ source: portable, marked: plan(portable), visible: plan(text) }),
    encoding: 'utf8', maxBuffer: 64 * 1024 * 1024,
  });
  if (ran.error) throw ran.error;
  let answer;
  try { answer = JSON.parse(ran.stdout); }
  catch { throw new Error(`Publication codec failed: ${ran.stderr || ran.stdout}`); }
  if (ran.status !== 0 || answer.error) throw new Error(answer.error || ran.stderr);
  return answer.result;
}

export function createPublication(replica, { title = 'Untitled publication' } = {}) {
  if (typeof title !== 'string' || title.length > 200) throw new Error('publication title must be text up to 200 characters');
  const portable = replica.portable(); // Existing conflict gate applies before any preview/export.
  const tokens = decode(portable);
  const counts = { ai: 0, human: 0, unmarked: 0, total: tokens.length };
  for (const t of tokens) counts[t.state || 'unmarked']++;
  const publication = {
    format: 'textprov-publication-1', id: randomUUID(), draftId: replica.header.id,
    title, version: Buffer.from(replica.version()).toString('base64'), hash: hash(portable),
    portable, text: tokens.map(t => t.visible).join(''), tokens, counts,
    preview: renderPublication(portable),
  };
  // Return owned values; no Loro containers, source refs, or editing state escape.
  return structuredClone(publication);
}

export function exportMarkedText(publication) {
  if (publication?.format !== 'textprov-publication-1' || typeof publication.portable !== 'string' ||
      publication.hash !== hash(publication.portable)) throw new Error('publication source integrity check failed');
  decode(publication.portable);
  return publication.portable;
}
