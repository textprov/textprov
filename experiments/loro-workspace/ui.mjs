import { portableRange, visibleEdit } from './editor.mjs';
const $ = selector => document.querySelector(selector);
const token = $('meta[name="textprov-token"]').content;
let state, busy = false;
const selections = [];
const buffers = new Map();
const status = text => { $('#status').textContent = text; };
async function api(command) {
  const response = await fetch(command ? '/api/action' : '/api/state', {
    method: command ? 'POST' : 'GET', headers: { 'x-textprov-token': token, 'Content-Type': 'application/json' },
    ...(command ? { body: JSON.stringify(command) } : {}),
  });
  const value = await response.json();
  if (!response.ok) throw new Error(value.error);
  return value;
}
function element(tag, text, className) {
  const el = document.createElement(tag); if (text !== undefined) el.textContent = text;
  if (className) el.className = className; return el;
}
function button(text, action, secondary = false) {
  const el = element('button', text, secondary ? 'secondary' : '');
  el.onclick = () => Promise.resolve().then(action).catch(error => status(error.message)); return el;
}
function selectedRange(parent) {
  const selection = window.getSelection();
  if (!selection.rangeCount || selection.isCollapsed) return null;
  const range = selection.getRangeAt(0);
  if (!parent.contains(range.startContainer) || !parent.contains(range.endContainer)) return null;
  const prefix = range.cloneRange(); prefix.selectNodeContents(parent); prefix.setEnd(range.startContainer, range.startOffset);
  const start = prefix.toString().length;
  return { start, end: start + range.toString().length };
}
function preview(parent, tokens, canCopy = () => true) {
  const runs = [];
  for (const t of tokens) {
    if (runs.length && runs.at(-1).state === t.state) runs.at(-1).text += t.visible;
    else runs.push({ state: t.state, text: t.visible });
  }
  parent.replaceChildren(...runs.map(run => element('span', run.text, run.state || 'unmarked')));
  parent.oncopy = event => {
    event.preventDefault();
    try {
      if (!canCopy()) throw new Error('Apply edits or review conflicts before copying.');
      const range = selectedRange(parent);
      if (!range) throw new Error('Select text within this preview.');
      event.clipboardData.setData('text/plain', portableRange(tokens, range.start, range.end));
      status('Copied preview selection with TextProv marks.');
    } catch (error) { status(error.message); }
  };
}
// A browser may dispatch copy to the focused body instead of the selected span.
// Resolve the selection explicitly so highlighted previews always encode marks.
document.addEventListener('copy', event => {
  if (event.defaultPrevented) return;
  const selection = window.getSelection();
  if (!selection.rangeCount) return;
  const node = selection.getRangeAt(0).commonAncestorContainer;
  const el = node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement;
  el?.closest('.preview')?.oncopy?.(event);
});
function report(tokens) {
  const counts = { ai: 0, human: 0, unmarked: 0 };
  for (const t of tokens) counts[t.state || 'unmarked']++;
  return `${counts.ai} AI · ${counts.human} recorded human · ${counts.unmarked} unmarked graphemes`;
}
function download(name, data, type) {
  const url = URL.createObjectURL(new Blob([data], { type }));
  const a = element('a'); a.href = url; a.download = name; a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
async function action(command, message, focus) {
  if (busy) throw new Error('Wait for the current edit to finish.');
  if (['undo', 'redo'].includes(command.operation) && buffers.has(command.replica)) throw new Error('Apply typed edits before using draft history.');
  if (command.operation === 'sync' && buffers.size) throw new Error('Apply typed edits in both replicas before syncing.');
  busy = true;
  document.querySelectorAll('#replicas textarea').forEach(el => { el.disabled = true; });
  try {
    const next = await api(command);
    if (command.operation === 'edit') buffers.delete(command.replica);
    state = { ...state, ...next }; renderDrafts();
    if (focus) {
      const area = $(`#draft-${focus.replica}`);
      if (area && !area.disabled) { area.focus(); area.setSelectionRange(focus.at, focus.at); }
    }
    status(message);
  } catch (error) { renderDrafts(); throw error; }
  finally { busy = false; }
}
function renderMessages() {
  $('#source-label').textContent = state.label;
  $('#messages').replaceChildren(...state.messages.map((m, i) => {
    const card = element('article');
    card.addEventListener('mousedown', event => {
      if (event.target.tagName === 'BUTTON') event.preventDefault();
    });
    card.append(element('header', `${m.role} · ${m.metadata.completeness || 'capture'} · ${m.metadata.observation_id.slice(0, 8)}`));
    if (m.portable === null) { card.append(element('p', 'Capture text unavailable.')); return card; }
    const area = element('textarea', undefined, 'message'); area.value = m.visible; area.readOnly = true;
    area.setAttribute('aria-label', `Message ${i + 1}: ${m.role}`);
    const visual = element('div', undefined, 'preview'); preview(visual, m.tokens);
    area.addEventListener('copy', event => {
      event.preventDefault();
      try { event.clipboardData.setData('text/plain', portableRange(m.tokens, area.selectionStart, area.selectionEnd));
        status('Copied message selection with recorded attribution.'); }
      catch (error) { status(error.message); }
    });
    card.append(visual, area, button('Add selected passage', () => {
      if (state.replicas.length) throw new Error('Draft already created. Restart the server to begin a new selection.');
      const { start, end } = selectedRange(visual) || { start: area.selectionStart, end: area.selectionEnd };
      if (start === end) throw new Error('Select some message text first.');
      portableRange(m.tokens, start, end);
      selections.push({ message: m.identity, start, end });
      $('#selections').append(element('li', m.visible.slice(start, end)));
      $('#create').disabled = false; status(`${selections.length} passage(s) selected.`);
    }));
    return card;
  }));
}
function renderDrafts() {
  $('#sync').disabled = state.replicas.length !== 2;
  if (!state.replicas.length) return;
  $('#create').disabled = true;
  $('#source-passages').open = false;
  $('#replicas').replaceChildren(...state.replicas.map((r, replica) => {
    const card = element('div', undefined, 'replica');
    card.append(element('h3', `Replica ${replica ? 'B' : 'A'}`));
    const label = element('label', 'Insertion source');
    const actor = element('select'); actor.setAttribute('aria-label', `Insertion source ${replica ? 'B' : 'A'}`);
    for (const [value, text] of [['human', 'Human editing'], ['assistant', 'Simulate AI editing']]) {
      const option = element('option', text); option.value = value; actor.append(option);
    }
    // Keep the chosen source across rerenders; this is simulation, never a model call.
    actor.value = sessionStorage.getItem(`actor-${replica}`) || 'human';
    actor.onchange = () => sessionStorage.setItem(`actor-${replica}`, actor.value);
    label.append(actor); card.append(label);
    const area = element('textarea'); area.id = `draft-${replica}`; area.value = buffers.get(replica)?.text ?? r.text;
    area.setAttribute('aria-label', `Draft ${replica ? 'B' : 'A'}`); area.disabled = !!r.conflicts.length;
    const base = () => ({ replica, expectedHash: r.reviewHash });
    const replace = (start, end, text, at) => action({ ...base(), operation: 'edit', start, end, text, actor: actor.value },
      'Edit applied locally. Sync to exchange changes.', { replica, at });
    const apply = () => {
      const at = area.selectionStart, edit = visibleEdit(r.text, area.value);
      return replace(edit.start, edit.end, edit.text, at);
    };
    area.addEventListener('input', () => {
      if (area.value === r.text) buffers.delete(replica);
      else buffers.set(replica, { text: area.value });
      status('Typed changes are pending. Apply edits to update attribution before copying or syncing.');
    });
    area.addEventListener('paste', event => {
      event.preventDefault();
      if (buffers.has(replica)) { status('Apply typed edits before pasting marked text.'); return; }
      const start = area.selectionStart, end = area.selectionEnd;
      replace(start, end, event.clipboardData.getData('text/plain'), start).catch(e => status(e.message));
    });
    for (const name of ['copy', 'cut']) area.addEventListener(name, event => {
      event.preventDefault();
      try {
        if (buffers.has(replica)) throw new Error('Apply typed edits before copying.');
        if (busy || r.conflicts.length) throw new Error('Finish editing or reviewing conflicts before copying.');
        const start = area.selectionStart, end = area.selectionEnd;
        const raw = portableRange(r.tokens, start, end);
        event.clipboardData.setData('text/plain', raw);
        status('Copied plain text with embedded TextProv marks.');
        if (name === 'cut' && start !== end) replace(start, end, '', start).catch(e => status(e.message));
      } catch (error) { status(error.message); }
    });
    area.addEventListener('keydown', event => {
      if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
        event.preventDefault(); apply().catch(e => status(e.message)); return;
      }
      if (!buffers.has(replica) && (event.metaKey || event.ctrlKey) && ['z', 'y'].includes(event.key.toLowerCase())) {
        event.preventDefault();
        action({ ...base(), operation: event.shiftKey || event.key.toLowerCase() === 'y' ? 'redo' : 'undo' }, 'Draft history updated.').catch(e => status(e.message));
      }
    });
    card.append(area);
    const applyButton = button('Apply edits', apply); applyButton.disabled = !!r.conflicts.length; card.append(applyButton);
    if (r.conflicts.length) {
      card.append(element('p', 'Concurrent overlapping edits need review. Copy and ordinary edits are paused.', 'conflict'));
      card.append(button('Accept displayed merge after review', () => action({ ...base(), operation: 'resolve',
        text: r.tokens.map(t => t.raw).join('') }, 'Reviewed merge accepted. Sync to share the decision.')));
    }
    const visual = element('div', undefined, 'preview'); preview(visual, r.tokens, () => !busy && !buffers.has(replica) && !r.conflicts.length);
    card.append(element('p', report(r.tokens), 'stats'), visual);
    for (const operation of ['undo', 'redo']) {
      const b = button(operation === 'undo' ? 'Undo' : 'Redo', () => action({ ...base(), operation }, 'Draft history updated.'), true);
      b.disabled = !!r.conflicts.length || buffers.has(replica); card.append(b);
    }
    const save = button('Download marked text', async () => {
      if (buffers.has(replica)) throw new Error('Apply typed edits before exporting.');
      const value = await api({ ...base(), operation: 'copy', start: 0, end: r.text.length });
      download(`textprov-draft-${replica ? 'B' : 'A'}.txt`, value.portable, 'text/plain;charset=utf-8');
      status('Downloaded portable marked text. Publication is up to you.');
    }, true); save.disabled = !!r.conflicts.length; card.append(save);
    card.append(button('Download private checkpoint', async () => {
      if (buffers.has(replica)) throw new Error('Apply typed edits before saving a checkpoint.');
      const saved = await api({ ...base(), operation: 'checkpoint' });
      download(`textprov-private-draft-${replica}.json`, JSON.stringify(saved), 'application/json');
      status('Private checkpoint includes draft history and selected source passages.');
    }, true));
    return card;
  }));
}
$('#highlights').onchange = () => document.body.classList.toggle('highlight', $('#highlights').checked);
document.body.classList.add('highlight');
$('#restore').onchange = async event => {
  const file = event.target.files[0];
  if (!file) return;
  try {
    if (file.size > 1400000) throw new Error('Checkpoint exceeds this UI request limit.');
    await action({ operation: 'restore', saved: JSON.parse(await file.text()) }, 'Private checkpoint restored into two replicas with its original source references.');
  } catch (error) { status(error.message); }
};
$('#create').onclick = () => action({ operation: 'select', selections }, 'Two replicas created from the selected passages.').catch(e => status(e.message));
$('#sync').onclick = () => action({ operation: 'sync' }, 'Replica changes exchanged. Review any overlapping edits.').catch(e => status(e.message));
let probeVersion = 0;
$('#probe').addEventListener('input', async () => {
  const version = ++probeVersion;
  try {
    const tokens = await api({ operation: 'decode', text: $('#probe').value });
    if (version !== probeVersion) return;
    $('#probe-report').textContent = report(tokens); preview($('#probe-preview'), tokens);
  } catch (error) {
    if (version !== probeVersion) return;
    $('#probe-report').textContent = error.message; $('#probe-preview').replaceChildren();
  }
});
window.addEventListener('beforeunload', event => { if (state?.replicas.length) { event.preventDefault(); event.returnValue = ''; } });
try { state = await api(); renderMessages(); renderDrafts(); status('Select a message passage to begin.'); }
catch (error) { status(error.message); }
