import { parseArgs } from 'node:util';
import { ConversationWorkspace } from './conversation.mjs';

try {
  const { values } = parseArgs({ options: {
    database: { type: 'string' }, workspace: { type: 'string' }, provider: { type: 'string' },
    session: { type: 'string' }, agent: { type: 'string' },
    'main-agent': { type: 'boolean' }, 'all-agents': { type: 'boolean' },
  } });
  if (!values.database || !values.workspace || !values.provider || !values.session ||
      [Boolean(values.agent), Boolean(values['main-agent']), Boolean(values['all-agents'])].filter(Boolean).length !== 1) {
    throw new Error('usage: node import.mjs --database /absolute/chronicle.sqlite --workspace /absolute/conversation.loro --provider PROVIDER --session ID (--main-agent | --agent ID | --all-agents)');
  }
  const workspace = new ConversationWorkspace(values.workspace);
  try {
    const result = workspace.importSelected({ database: values.database, provider: values.provider,
      session: values.session, agent: values.agent || null, cross_agent: Boolean(values['all-agents']) });
    const messages = workspace.messages();
    console.log(JSON.stringify({ ...result, retainedMessages: messages.length,
      unavailableMessages: messages.filter(m => m.portable === null).length,
      partialMessages: messages.filter(m => ['partial', 'truncated'].includes(m.metadata.completeness)).length,
      workspace: workspace.path, retention: 'Selected content is retained in this private local workspace independently of Chronicle cache expiry.' }, null, 2));
  } finally { workspace.close(); }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
