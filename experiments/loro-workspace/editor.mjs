/** Pure browser helpers. All coordinates are visible UTF-16 grapheme boundaries. */
export function portableRange(tokens, start, end) {
  let at = 0, result = '', sawStart = start === 0, sawEnd = end === 0;
  for (const t of tokens) {
    const next = at + t.visible.length;
    if (at === start) sawStart = true;
    if (next === end) sawEnd = true;
    if (at >= start && next <= end) result += t.raw;
    at = next;
  }
  if (start === at) sawStart = true;
  if (end === at) sawEnd = true;
  if (start < 0 || start > end || !sawStart || !sawEnd) throw new Error('Select whole characters, including combining marks.');
  return result;
}
export function visibleEdit(before, after) {
  const segment = text => [...new Intl.Segmenter(undefined, { granularity: 'grapheme' }).segment(text)].map(s => s.segment);
  const a = segment(before), b = segment(after);
  let p = 0, s = 0;
  while (p < Math.min(a.length, b.length) && a[p] === b[p]) p++;
  while (s < Math.min(a.length, b.length) - p && a.at(-1 - s) === b.at(-1 - s)) s++;
  return { start: a.slice(0, p).join('').length, end: a.slice(0, a.length - s).join('').length,
    text: b.slice(p, b.length - s).join('') };
}
