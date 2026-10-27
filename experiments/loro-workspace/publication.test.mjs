import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { AttributedText, decode } from './boundary.mjs';
import { createPublication, exportMarkedText, renderPublication } from './publication.mjs';

function mark(text, state = 'ai', mode = 'vs') {
  const ran = spawnSync(process.env.TEXTPROV_PYTHON || 'python3', ['-c',
    'import json,sys; from textprov import mark; print(json.dumps(mark(*json.load(sys.stdin))))'], {
    input: JSON.stringify([text, state, mode]), encoding: 'utf8',
    env: { ...process.env, PYTHONPATH: fileURLToPath(new URL('../../python', import.meta.url)) },
  });
  assert.equal(ran.status, 0, ran.stderr); return JSON.parse(ran.stdout);
}
function replica(t, portable) {
  const body = new AttributedText(portable); t.after(() => body.close());
  return { body, header: { id: 'local-draft-id', privateSource: 'do not publish' },
    portable: () => body.portable(), version: () => {
      const version = body.doc.version(); try { return version.encode(); } finally { version.free(); }
    }, sources: () => { throw new Error('publication must not read source references'); },
    checkpoint: () => { throw new Error('publication must not read private checkpoints'); } };
}
function renderedText(html) {
  const ran = spawnSync(process.env.TEXTPROV_PYTHON || 'python3', ['-c',
    "import sys,json; from html.parser import HTMLParser\nclass P(HTMLParser):\n def handle_data(self,d): self.parts.append(d)\np=P(convert_charrefs=True); p.parts=[]; p.feed(sys.stdin.read()); print(json.dumps(''.join(p.parts)))"],
    { input: html, encoding: 'utf8' });
  assert.equal(ran.status, 0, ran.stderr); return JSON.parse(ran.stdout);
}

test('publication pins exact mixed source and exports UTF-8 without private history or live mutations', t => {
  const source = '# Publication\r\n\r\n' + mark('Human e\u0301 👩🏽‍💻', 'human') + ' ' + mark('AI text') +
    ' ' + mark('PUA', 'ai', 'pua') + '\n\n`code` stays literal.\n';
  const r = replica(t, source), version = r.version();
  const publication = createPublication(r, { title: 'Reader edition' });
  assert.equal(publication.portable, source); assert.deepEqual(r.version(), version);
  assert.equal(r.body.portable(), source);
  assert.deepEqual(publication.tokens, decode(source));
  assert.equal(publication.counts.ai + publication.counts.human + publication.counts.unmarked, publication.counts.total);
  assert.equal(publication.counts.total, publication.tokens.length);
  assert.ok(publication.counts.unmarked > 0); assert.ok(publication.counts.ai > 0); assert.ok(publication.counts.human > 0);
  assert.equal(publication.preview.mode, 'markdown');
  assert.equal(publication.preview.tokens.map(t => t.visible).join(''), renderedText(publication.preview.html));
  assert.doesNotMatch(JSON.stringify(publication), /privateSource|do not publish|sourceNamespace|originalContentHash|snapshot|checkpoint|prompt|sources/);
  r.body.replace(0, 0, 'A later edit.\n');
  assert.equal(exportMarkedText(publication), source); assert.notEqual(r.body.portable(), source);
  const directory = mkdtempSync(join(tmpdir(), 'textprov-publication-'));
  try {
    const path = join(directory, 'publication.txt'); writeFileSync(path, exportMarkedText(publication), 'utf8');
    assert.deepEqual(readFileSync(path), Buffer.from(source, 'utf8'));
  } finally { rmSync(directory, { recursive: true, force: true }); }
});

test('Markdown reader text retains exact per-character attribution and safe block structure', () => {
  const human = mark('Human', 'human'), ai = mark('AI'), pua = mark('PUA', 'ai', 'pua');
  const preview = renderPublication(`# ${human}\n\n**${ai}** and ${pua}.\n\n> A quote\n\n- One\n- Two\n\n\`\`\`js\nx < y\n\`\`\`\n`);
  assert.equal(preview.mode, 'markdown'); assert.match(preview.html, /<h1>/); assert.match(preview.html, /<strong>/);
  assert.match(preview.html, /<blockquote>/); assert.match(preview.html, /<ul>/); assert.match(preview.html, /<pre><code>/);
  assert.equal(preview.tokens.map(t => t.visible).join(''), renderedText(preview.html));
  assert.equal(preview.tokens.slice(0, 5).map(t => t.raw).join(''), human);
  const puaStart = preview.tokens.map(t => t.visible).join('').indexOf('PUA');
  assert.equal(preview.tokens.slice(puaStart, puaStart + 3).map(t => t.raw).join(''), pua);
  assert.ok(preview.tokens.some(t => t.state === null));
});

test('raw HTML, links, images, and task controls remain inert in a publication preview', () => {
  const source = '<script>alert(1)</script>\n\n<img src="https://example.test/track" onerror="alert(1)">\n\n' +
    '[click](javascript:alert(1)) ![remote alt](https://example.test/track)\n\n- [x] Done\n\n' +
    'Inline <iframe src="file:///private/data"></iframe> and `raw <img>`.';
  const preview = renderPublication(source);
  assert.equal(preview.mode, 'markdown');
  assert.doesNotMatch(preview.html, /<(?:script|img|iframe|a|input|style|object|svg)\b/i);
  assert.doesNotMatch(preview.html, /<[^>]*\b(?:src|href|onerror|style)\s*=/i);
  assert.match(preview.html, /&lt;script&gt;/); assert.match(preview.html, /publication-link/);
  assert.match(renderedText(preview.html), /\[Image: remote alt\]/);
  assert.match(renderedText(preview.html), /\[x\] Done/);
  assert.equal(preview.tokens.map(t => t.visible).join(''), renderedText(preview.html));
});

test('ambiguous entities and marked Markdown syntax use an explicit lossless plain-text fallback', () => {
  for (const source of ['A &amp; B', 'A &amp; B\r\nNext\rLast', '#\u{E0101} Heading', 'a`\u0301`']) {
    const preview = renderPublication(source);
    assert.equal(preview.mode, 'plain-text', source); assert.ok(preview.reason);
    assert.deepEqual(preview.tokens, decode(source));
    assert.equal(renderedText(preview.html), decode(source).map(t => t.visible).join(''));
    assert.equal(preview.tokens.map(t => t.raw).join(''), source);
  }
  assert.equal(renderPublication('Escaped \\* stays text and `&amp;` stays code.').mode, 'markdown');
});

test('table whitespace remains valid structural text and reader-copy tokens match its textContent', () => {
  const preview = renderPublication('| A | B |\n| :--- | ---: |\n| one | two |\n');
  assert.equal(preview.mode, 'markdown');
  assert.match(preview.html, /<table>\n<thead>\n<tr>/);
  assert.doesNotMatch(preview.html, /<(?:table|thead|tbody|tr)>\s*<span/);
  assert.equal(preview.tokens.map(t => t.visible).join(''), renderedText(preview.html));
});

test('conflicts, unsupported encoding, NUL, and changed export source are refused', t => {
  assert.throws(() => createPublication({ portable() { throw new Error('overlapping edits need review'); } }), /need review/);
  assert.throws(() => renderPublication('\u{E0101}'), /selector/);
  assert.throws(() => renderPublication('a\0b'), /NUL/);
  const publication = createPublication(replica(t, 'Original'));
  publication.portable += 'tampered';
  assert.throws(() => exportMarkedText(publication), /integrity/);
  assert.throws(() => createPublication(replica(t, 'a'), { title: 42 }), /title/);
});
