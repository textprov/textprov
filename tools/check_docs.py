"""Check proposal Markdown links and validate the deliberately VS-marked proposal prose."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote

root = Path(__file__).resolve().parents[1]
files = [root / 'README.md', *sorted((root / 'docs').rglob('*.md')),
         *(root / name / 'README.md' for name in ('python', 'ruby', 'js', 'site', 'ucd')),
         *sorted((root / 'experiments').rglob('*.md'))]
errors = []
for path in files:
    source = path.read_text()
    marked_proposal = path == root / 'README.md' or root / 'docs' in path.parents
    for cp in map(ord, source):
        if marked_proposal and cp in (0xE0100, 0xE0101):
            continue
        if 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF:
            errors.append(f'{path.relative_to(root)}: literal variation selector U+{cp:04X}; use code-point notation in proposal prose')
    source = source.replace('\U000E0100', '').replace('\U000E0101', '')
    for target in re.findall(r'\]\(([^\s)]+)(?:\s+"[^"]*")?\)', source):
        target = unquote(target.strip('<>'))
        if re.match(r'[a-z][a-z0-9+.-]*:', target, re.I) or target.startswith('#'):
            continue
        filename = target.split('#', 1)[0]
        if not filename:
            continue
        if not (path.parent / filename).exists():
            errors.append(f'{path.relative_to(root)}: missing link {target}')
if errors:
    print('\n'.join(errors), file=sys.stderr)
    sys.exit(1)
print(f'Proposal links and hidden-marker check: {len(files)} Markdown files passed')
