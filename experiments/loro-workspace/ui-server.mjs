/** Loopback-only UI, explicit saved-conversation input, no installed configuration. */
import { createServer } from 'node:http';
import { randomBytes } from 'node:crypto';
import { mkdtempSync, readFileSync, copyFileSync, rmSync } from 'node:fs';
import { tmpdir, homedir } from 'node:os';
import { join, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';
import { ConversationWorkspace } from './conversation.mjs';
import { UISession } from './ui-session.mjs';
import { LocalDraftStore } from './local-drafts.mjs';

export function createUI(workspace, { label = 'Disposable sample conversation', store } = {}) {
  const session = new UISession(workspace, { store, label });
  const token = randomBytes(24).toString('hex');
  const assets = new Map([['/', ['ui.html', 'text/html']], ['/ui.mjs', ['ui.mjs', 'text/javascript']],
    ['/ui.css', ['ui.css', 'text/css']], ['/editor.mjs', ['editor.mjs', 'text/javascript']]]);
  const server = createServer(async (req, res) => {
    const origin = `http://127.0.0.1:${server.address().port}`;
    res.setHeader('Cache-Control', 'no-store');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('Referrer-Policy', 'no-referrer');
    res.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' blob:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'");
    const send = (status, value) => { res.writeHead(status, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(value)); };
    if (req.headers.host !== new URL(origin).host) return send(403, { error: 'loopback Host required' });
    if (req.headers.origin && req.headers.origin !== origin) return send(403, { error: 'same origin required' });
    if (req.headers['sec-fetch-site'] === 'cross-site') return send(403, { error: 'cross-site access refused' });
    try {
      if (req.method === 'GET' && assets.has(req.url)) {
        const [file, type] = assets.get(req.url);
        let body = readFileSync(new URL(file, import.meta.url), 'utf8');
        if (file === 'ui.html') body = body.replace('TOKEN_PLACEHOLDER', token);
        res.writeHead(200, { 'Content-Type': type + '; charset=utf-8' }); return res.end(body);
      }
      if (req.headers['x-textprov-token'] !== token) return send(403, { error: 'local session token required' });
      if (req.method === 'GET' && req.url === '/api/responses') return send(200, { responses: session.responseState(), persistence: session.state().persistence });
      if (req.method === 'GET' && req.url === '/api/state') return send(200, session.state());
      if (req.method !== 'POST' || req.url !== '/api/action') return send(404, { error: 'not found' });
      if (req.headers['content-type'] !== 'application/json') return send(415, { error: 'JSON required' });
      let size = 0; const chunks = [];
      for await (const chunk of req) {
        chunks.push(chunk); size += chunk.length;
        if (size > 2 * 1024 * 1024) return send(413, { error: 'request too large' });
      }
      return send(200, session.execute(JSON.parse(Buffer.concat(chunks).toString('utf8'))));
    } catch (error) { send(400, { error: error.message }); }
  });
  server.on('close', () => session.close());
  return { server, session };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  const options = {};
  for (let i = 0; i < args.length; i += 2) {
    if (!['--conversation', '--data'].includes(args[i]) || !args[i + 1] || !isAbsolute(args[i + 1]) || options[args[i]]) {
      throw new Error('usage: node ui-server.mjs [--conversation /absolute/conversation.loro] [--data /absolute/private-directory]');
    }
    options[args[i]] = args[i + 1];
  }
  const conversation = options['--conversation'];
  const directory = options['--data'] || join(process.env.XDG_DATA_HOME || join(homedir(), '.local', 'share'), 'textprov-workspace');
  const store = new LocalDraftStore(directory);
  const dir = mkdtempSync(join(tmpdir(), 'textprov-ui-'));
  let workspace;
  try {
    const path = join(dir, 'conversation.loro');
    if (conversation) copyFileSync(conversation, path);
    workspace = new ConversationWorkspace(path);
    if (!conversation) {
      const database = join(dir, 'fixture.sqlite');
      const created = spawnSync(process.env.TEXTPROV_PYTHON || 'python3',
        [fileURLToPath(new URL('fixture_chronicle.py', import.meta.url)), database, '--small'], { encoding: 'utf8' });
      if (created.status !== 0) throw new Error(created.stderr);
      workspace.importSelected({ database, provider: 'claude', session: 'selected', agent: null });
    }
    const { server, session } = createUI(workspace, { label: conversation ? 'Private copy of selected saved conversation' : undefined, store });
    const cleanup = () => { workspace.close(); store.close(); rmSync(dir, { recursive: true, force: true }); };
    server.on('close', cleanup);
    server.on('error', error => { session.close(); cleanup(); console.error(error.message); process.exitCode = 1; });
    for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, () => server.close());
    server.listen(0, '127.0.0.1', () => console.log(`TextProv local workspace: http://127.0.0.1:${server.address().port}\nApplied edits save locally in ${store.directory}. Reopen saved drafts in the UI. No capture records or settings changed.`));
  } catch (error) { workspace?.close(); store.close(); rmSync(dir, { recursive: true, force: true }); throw error; }
}
