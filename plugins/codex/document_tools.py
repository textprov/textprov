"""Conservative, in-memory marking of native apply_patch document edits.

Only Markdown additions are rewritten. Context and deletion records retain their
original spelling; uncertain matches fail closed instead of authorizing an edit
whose AI additions would not be marked. This module never writes project files.
"""
from pathlib import Path


def _path(root, value):
    path = Path(value)
    if '..' in path.parts or not path.parts:
        raise ValueError('document patch forbids parent traversal')
    target = path if path.is_absolute() else root / path
    try:
        relative = target.relative_to(root)
    except ValueError as error:
        raise ValueError('document patch escapes the project') from error
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('document patch cannot follow symlinks')
    if not target.resolve().is_relative_to(root):
        raise ValueError('document patch escapes the project')
    return target


def _markdown(path):
    return path.suffix.lower() in {'.md', '.markdown'}


def _read(path):
    try:
        # Preserve CRLF and source marks exactly.
        with path.open(encoding='utf-8', newline='') as source:
            return source.read()
    except (OSError, UnicodeError) as error:
        raise ValueError('cannot read document patch source: ' + str(error)) from error


def _lines(text):
    # Native apply_patch matches logical lines and restores source CRLF on write.
    text = text.replace('\r\n', '\n')
    return text.split('\n')[:-1] if text.endswith('\n') else text.split('\n') if text else []


def rewrite_tool_input(payload):
    """Return rewritten native tool_input, or None for unrelated/unchanged input.

    Native patches append a final newline and preserve a source CRLF convention.
    Attribution compares logical lines so newline serialization is not AI prose.
    Unsupported or ambiguous Markdown patches raise ValueError for host denial.
    """
    if payload.get('tool_name') != 'apply_patch':
        return None
    value = payload.get('tool_input')
    if not isinstance(value, dict) or not isinstance(value.get('command'), str):
        raise ValueError('apply_patch requires a string tool_input.command')
    command = value['command']
    records = command.split('\n')
    end = len(records) - 1 if records[-1] == '' else len(records)
    if not records or records[0] != '*** Begin Patch' or end < 2 or records[end - 1] != '*** End Patch':
        raise ValueError('unsupported apply_patch envelope')
    root = Path(payload.get('cwd', '')).resolve()
    if not payload.get('cwd') or not root.is_dir():
        raise ValueError('document patch requires an existing project cwd')
    from textprov import mark_document_edit
    changed = False
    seen = set()
    i = 1
    while i < end - 1:
        header = records[i]
        operation = next((name for name in ('Add', 'Update', 'Delete')
                          if header.startswith('*** ' + name + ' File: ')), None)
        if operation is None:
            raise ValueError('unsupported apply_patch file header')
        name = header.split(' File: ', 1)[1]
        target = _path(root, name)
        if target in seen:
            raise ValueError('repeated document patch path')
        seen.add(target)
        j = i + 1
        while j < end - 1 and not any(records[j].startswith('*** ' + op + ' File: ')
                                       for op in ('Add', 'Update', 'Delete')):
            j += 1
        move = None
        start = i + 1
        if start < j and records[start].startswith('*** Move to: '):
            move = _path(root, records[start][13:])
            if operation != 'Update' or move in seen or move.exists():
                raise ValueError('invalid document move')
            seen.add(move)
            start += 1
        eligible = _markdown(target) or (move is not None and _markdown(move))
        if not eligible:
            i = j
            continue
        if operation == 'Delete':
            if start != j:
                raise ValueError('delete document patch has unexpected content')
            i = j
            continue
        additions = []
        if operation == 'Add':
            if target.exists():
                raise ValueError('add document patch would overwrite an existing file')
            new = []
            for k in range(start, j):
                if not records[k].startswith('+'):
                    raise ValueError('unsupported add document patch record')
                new.append(records[k][1:].removesuffix('\r'))
                additions.append((len(new) - 1, k))
            old_text = ''
        else:
            old_text = _read(target)
            old = _lines(old_text)
            new = []
            cursor = 0
            k = start
            while k < j:
                if records[k] == '@@' or records[k].startswith('@@ '):
                    k += 1
                elif k != start:
                    raise ValueError('unsupported document patch chunk')
                chunk = []
                eof = False
                while k < j and not (records[k] == '@@' or records[k].startswith('@@ ')):
                    record = records[k]
                    if record == '*** End of File':
                        eof = True
                        k += 1
                        if k != j:
                            raise ValueError('unexpected content after End of File')
                        break
                    if not record or record[0] not in ' +-':
                        raise ValueError('unsupported document patch record')
                    chunk.append((record[0], record[1:].removesuffix('\r'), k))
                    k += 1
                before = [line for prefix, line, _ in chunk if prefix != '+']
                if not chunk:
                    raise ValueError('empty document patch chunk')
                if before:
                    matches = [p for p in range(cursor, len(old) - len(before) + 1)
                               if old[p:p + len(before)] == before
                               and (not eof or p + len(before) == len(old))]
                else:
                    # A context-free insertion is only unambiguous in an empty
                    # file, or when explicitly anchored at end of file.
                    matches = [len(old)] if eof or not old else []
                if len(matches) != 1:
                    raise ValueError('document patch context is missing or ambiguous')
                position = matches[0]
                new.extend(old[cursor:position])
                for prefix, line, record_index in chunk:
                    if prefix != '-':
                        if prefix == '+':
                            additions.append((len(new), record_index))
                        new.append(line)
                cursor = position + len(before)
            new.extend(old[cursor:])
        # Match source newline semantics during attribution. The native patch
        # writer decides final-newline serialization; it is not an AI prose edit.
        final_lf = operation == 'Add' or old_text.endswith('\n')
        new_text = '\n'.join(new) + ('\n' if new and final_lf else '')
        marked = _lines(mark_document_edit(old_text.replace('\r\n', '\n'), new_text))
        if len(marked) != len(new):
            raise ValueError('document marking changed patch line structure')
        addition_rows = {row for row, _ in additions}
        if any(marked[row] != line for row, line in enumerate(new) if row not in addition_rows):
            raise ValueError('document marking would alter untouched patch context')
        for row, record_index in additions:
            replacement = '+' + marked[row] + ('\r' if records[record_index].endswith('\r') else '')
            changed = changed or records[record_index] != replacement
            records[record_index] = replacement
        i = j
    if not changed:
        return None
    return dict(value, command='\n'.join(records))
