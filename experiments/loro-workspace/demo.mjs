import assert from 'node:assert/strict';
import { AttributedText } from './boundary.mjs';

const human = new AttributedText();
const assistant = new AttributedText();
let draft;
try {
  human.replace(0, 0, 'My words.', { actor: 'human', destination: 'chat' });
  assistant.replace(0, 0, 'An AI answer.', { actor: 'assistant', destination: 'chat' });
  const source = human.copy() + '\n' + assistant.copy();
  draft = new AttributedText(source);
  draft.replace(draft.visible().length, draft.visible().length, '\nMy editor addition.');
  const before = draft.portable();
  const start = draft.visible().indexOf('answer');
  draft.replace(start, start + 'answer'.length, 'explanation', { actor: 'assistant' });
  const edited = draft.portable();
  draft.undo();
  assert.equal(draft.portable(), before);
  draft.redo();
  assert.equal(draft.portable(), edited);
  if (process.argv.includes('--portable')) {
    process.stdout.write(draft.copy());
  } else {
    const totals = { human: 0, ai: 0, unmarked: 0 };
    for (const token of draft.tokens()) totals[token.state || 'unmarked']++;
    const roundtrip = new AttributedText(draft.copy());
    const exactRoundTrip = roundtrip.portable() === edited;
    roundtrip.close();
    console.log(JSON.stringify({
      visible: draft.visible(),
      graphemesByRecordedState: totals,
      exactRoundTrip,
      undoAndRedo: 'exact text and attribution restored',
      scope: 'in-memory Loro only; no Chronicle or plugin configuration access',
    }, null, 2));
  }
} finally {
  human.close(); assistant.close(); draft?.close();
}
