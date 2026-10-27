"""Safely decorate controlled publication HTML without consulting capture records."""
import html
from html.parser import HTMLParser
import json
import re
import sys
from codec import decode

TAGS = {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'pre', 'code', 'strong', 'em',
        'del', 'blockquote', 'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'th',
        'td', 'hr', 'br', 'span'}
CLASSES = {'publication-link', 'publication-image', 'publication-checkbox', 'raw-html'}
VOID = {'br', 'hr'}
PLACEHOLDER = re.compile(r'\x00publication-leaf:(\d+)\x00')
ENTITY = re.compile(r'&(?:#[0-9]+|#x[0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]+);')


def escape_text(text):
    # HTML parsing normalizes literal CR/CRLF. A character reference preserves
    # the exact decoded textContent and its UTF-16 clipboard coordinates.
    return html.escape(text, quote=True).replace('\r', '&#13;')


def text_html(tokens):
    # Structural whitespace in a table/list must stay a text node: wrapping it
    # in a span can make the browser move it during HTML tree construction.
    if tokens and all(t['visible'].isspace() for t in tokens):
        return escape_text(''.join(t['visible'] for t in tokens))
    groups = []
    for token in tokens:
        state = token['state'] or 'unmarked'
        if groups and groups[-1][0] == state:
            groups[-1][1] += token['visible']
        else:
            groups.append([state, token['visible']])
    return ''.join(f'<span class="tp-{state}">{escape_text(text)}</span>' for state, text in groups)


class ReaderHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.output = []
        self.canonical = []
        self.tokens = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in TAGS:
            raise ValueError('unapproved publication tag')
        cleaned = []
        for key, value in attrs:
            valid = ((key == 'class' and tag == 'span' and value in CLASSES) or
                     (key == 'start' and tag == 'ol' and value is not None and value.isdigit()) or
                     (key == 'align' and tag in {'td', 'th'} and value in {'left', 'center', 'right'}))
            if not valid:
                raise ValueError('unapproved publication attribute')
            cleaned.append(f' {key}="{html.escape(value, quote=True)}"')
        opening = '<' + tag + ''.join(cleaned) + '>'
        self.output.append(opening)
        self.canonical.append(opening)
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise ValueError('unbalanced publication markup')
        self.output.append(f'</{tag}>')
        self.canonical.append(f'</{tag}>')

    def handle_data(self, text):
        tokens = decode(text)
        self.tokens.extend(tokens)
        self.output.append(text_html(tokens))
        self.canonical.append(html.escape(''.join(t['visible'] for t in tokens), quote=True))

    def handle_comment(self, _):
        raise ValueError('unapproved publication comment')

    def finish(self):
        self.close()
        if self.stack:
            raise ValueError('unclosed publication markup')
        # Removing Markdown syntax must not join independently attributed pieces
        # into an invalid visible grapheme. Refuse instead of assigning its origin.
        if decode(''.join(t['raw'] for t in self.tokens)) != self.tokens:
            raise ValueError('rendering joins separate attribution boundaries')
        return {'html': ''.join(self.output), 'canonical': ''.join(self.canonical), 'tokens': self.tokens}


def render(plan):
    leaves = plan['leaves']
    for leaf in leaves:
        if leaf['kind'] == 'text' and ENTITY.search(leaf['text']):
            raise ValueError('HTML entities in prose require a plain-text preview to preserve exact attribution')
    raw_html = PLACEHOLDER.sub(lambda m: html.escape(leaves[int(m[1])]['text'], quote=True), plan['template'])
    parser = ReaderHTML()
    parser.feed(raw_html)
    return parser.finish()


def operate(request):
    source = request['source']
    if '\x00' in source:
        raise ValueError('publication preview does not support NUL characters')
    tokens = decode(source)
    plain = {'mode': 'plain-text', 'html': '<pre class="publication-plain">' + text_html(tokens) + '</pre>', 'tokens': tokens}
    try:
        marked = render(request['marked'])
        visible = render(request['visible'])
        if marked['canonical'] != visible['canonical']:
            raise ValueError('portable marks change Markdown structure; showing exact plain text instead')
        return {'mode': 'markdown', 'html': marked['html'], 'tokens': marked['tokens'], 'reason': None}
    except ValueError as error:
        return {**plain, 'reason': str(error)}


if __name__ == '__main__':
    try:
        print(json.dumps({'result': operate(json.load(sys.stdin))}, ensure_ascii=True))
    except (ValueError, KeyError, TypeError, IndexError) as error:
        print(json.dumps({'error': str(error)}))
        sys.exit(1)
