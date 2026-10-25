"""Native patch rewriting tests; project files are never modified by hooks."""
import importlib.util
from pathlib import Path
import tempfile
import shutil
import subprocess
import unittest

import textprov

spec = importlib.util.spec_from_file_location(
    'document_tools', Path(__file__).resolve().parents[1] / 'document_tools.py')
document_tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(document_tools)


class DocumentToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode('utf-8'))
        return path

    def rewrite(self, body):
        value = {'command': '*** Begin Patch\n' + body + '*** End Patch\n', 'other': 'kept'}
        result = document_tools.rewrite_tool_input(
            {'tool_name': 'apply_patch', 'tool_input': value, 'cwd': str(self.root)})
        self.assertEqual(value['other'], 'kept')
        if result is not None:
            self.assertEqual(result['other'], 'kept')
        return result

    def test_add_marks_prose_but_protects_whole_markdown_fence(self):
        result = self.rewrite('*** Add File: new.md\n+Hello world.\n+```python\n+print("hello")\n+```\n')
        command = result['command']
        self.assertIn('+' + textprov.mark_document('Hello world.').rstrip('\n'), command)
        self.assertIn('+```python\n+print("hello")\n+```', command)
        self.assertFalse((self.root / 'new.md').exists())

    def test_update_uses_fence_context_outside_chunk(self):
        original = 'Title\n\n```python\nold()\n```\n'
        path = self.write('doc.md', original)
        self.assertIsNone(self.rewrite('*** Update File: doc.md\n@@\n-old()\n+new()\n'))
        self.assertEqual(path.read_bytes(), original.encode())

    def test_retyping_marked_human_text_preserves_marks(self):
        human = textprov.mark('Human text.', state='human')
        original = human + '\n'
        path = self.write('doc.md', original)
        result = self.rewrite('*** Update File: doc.md\n@@\n-' + human + '\n+Human text.\n+New prose.\n')
        command = result['command']
        self.assertIn('-' + human + '\n+' + human + '\n', command)
        self.assertIn('+' + textprov.mark_document('New prose.').rstrip('\n'), command)
        self.assertEqual(path.read_bytes(), original.encode())

    def test_unchanged_marked_context_and_delete_records_are_exact(self):
        human = textprov.mark('Human context', state='human')
        self.write('doc.md', human + '\nold prose\n')
        body = '*** Update File: doc.md\n@@\n ' + human + '\n-old prose\n+New prose\n'
        result = self.rewrite(body)
        self.assertIn(' ' + human + '\n-old prose\n', result['command'])

    def test_crlf_content_and_missing_final_newline(self):
        path = self.write('doc.md', 'Original\r\nlast')
        result = self.rewrite('*** Update File: doc.md\n@@\n-Original\r\n+Replacement\r\n last\n')
        self.assertIn('\r\n last\n*** End Patch\n', result['command'])
        self.assertEqual(path.read_bytes(), b'Original\r\nlast')
        self.assertEqual(textprov.strip_marks(result['command']),
                         '*** Begin Patch\n*** Update File: doc.md\n@@\n-Original\r\n+Replacement\r\n last\n*** End Patch\n')

    def test_move_to_markdown_marks_additions(self):
        self.write('source.txt', 'Old\n')
        result = self.rewrite('*** Update File: source.txt\n*** Move to: moved.md\n@@\n-Old\n+New\n')
        self.assertIn('*** Move to: moved.md\n', result['command'])
        self.assertNotIn('+New\n', result['command'])

    def test_move_cannot_overwrite_existing_marks(self):
        self.write('source.md', 'Old\n')
        self.write('destination.md', textprov.mark('Human', state='human'))
        with self.assertRaises(ValueError):
            self.rewrite('*** Update File: source.md\n*** Move to: destination.md\n@@\n-Old\n+New\n')

    def test_existing_marks_in_added_text_survive(self):
        human = textprov.mark('Pasted human words', state='human')
        result = self.rewrite('*** Add File: doc.md\n+' + human + '\n')
        # Already marked content needs no tool-input replacement.
        self.assertIsNone(result)

    def test_delete_and_non_documents_are_not_rewritten(self):
        self.write('doc.md', 'old\n')
        self.assertIsNone(self.rewrite('*** Delete File: doc.md\n'))
        self.assertIsNone(self.rewrite('*** Add File: script.py\n+print(1)\n'))
        self.assertTrue((self.root / 'doc.md').exists())

    def test_multifile_patch_marks_each_document(self):
        result = self.rewrite('*** Add File: a.md\n+Alpha\n*** Add File: b.markdown\n+Beta\n')
        self.assertIn('+' + textprov.mark_document('Alpha'), result['command'])
        self.assertIn('+' + textprov.mark_document('Beta'), result['command'])

    def test_ambiguous_or_absent_context_denied(self):
        self.write('doc.md', 'same\nsame\n')
        for body in ('@@\n-same\n+New\n', '@@\n-missing\n+New\n', '@@\n+New\n'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                self.rewrite('*** Update File: doc.md\n' + body)

    def test_eof_anchor_disambiguates(self):
        self.write('doc.md', 'same\nsame\n')
        self.assertIsNotNone(self.rewrite('*** Update File: doc.md\n@@\n-same\n+New\n*** End of File\n'))

    def test_paths_are_relative_without_traversal_or_symlinks(self):
        outside = self.root.parent / 'outside.md'
        (self.root / 'link').symlink_to(self.root, target_is_directory=True)
        for name in ('../outside.md', str(outside), 'link/doc.md'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.rewrite('*** Add File: ' + name + '\n+New\n')

    def test_absolute_in_project_path_is_supported(self):
        name = str(self.root.resolve() / 'absolute.md')
        result = self.rewrite('*** Add File: ' + name + '\n+New prose\n')
        self.assertIn('*** Add File: ' + name, result['command'])

    def apply_native(self, result):
        executable = shutil.which('apply_patch')
        if not executable:
            self.skipTest('native Codex apply_patch executable is unavailable')
        process = subprocess.run([executable, result['command']], cwd=str(self.root),
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr)

    def test_native_copy_paste_and_document_edit_preserve_existing_marks(self):
        human = textprov.mark_chat('Human words', 'user')
        ai = textprov.mark_chat('AI words', 'assistant')
        self.write('doc.md', human + '\n' + ai + '\nold prose\n')
        result = self.rewrite('*** Update File: doc.md\n@@\n ' + human + '\n ' + ai +
                              '\n-old prose\n+Fresh sentence\n')
        self.apply_native(result)
        actual = (self.root / 'doc.md').read_bytes().decode('utf-8')
        self.assertEqual(actual, human + '\n' + ai + '\n' +
                         textprov.mark_document('Fresh sentence') + '\n')
        # Simulate a plain UTF-8 clipboard/editor round trip, then an ordinary
        # editor appending unmarked text. Existing selectors survive bytewise.
        self.write('pasted.md', actual)
        self.assertEqual((self.root / 'pasted.md').read_bytes(), actual.encode('utf-8'))
        with (self.root / 'pasted.md').open('a', encoding='utf-8') as editor:
            editor.write('Editor addition\n')
        self.assertEqual((self.root / 'pasted.md').read_bytes(),
                         (actual + 'Editor addition\n').encode('utf-8'))

    def test_native_crlf_and_final_newline_semantics(self):
        self.write('doc.md', 'Original\r\nlast')
        result = self.rewrite('*** Update File: doc.md\n@@\n-Original\n+Replacement\n last\n')
        self.apply_native(result)
        self.assertEqual((self.root / 'doc.md').read_bytes(),
                         (textprov.mark_document('Replacement') + '\r\nlast\r\n').encode('utf-8'))

    def test_native_add_and_move(self):
        result = self.rewrite('*** Add File: new.md\n+New prose\n')
        self.apply_native(result)
        old = (self.root / 'new.md').read_bytes().decode('utf-8')
        result = self.rewrite('*** Update File: new.md\n*** Move to: moved.md\n@@\n ' +
                              old.rstrip('\n') + '\n+More prose\n')
        self.apply_native(result)
        self.assertFalse((self.root / 'new.md').exists())
        self.assertEqual((self.root / 'moved.md').read_bytes(),
                         (old + textprov.mark_document('More prose') + '\n').encode('utf-8'))

    def test_unrelated_tools_are_ignored(self):
        self.assertIsNone(document_tools.rewrite_tool_input({'tool_name': 'Bash'}))


if __name__ == '__main__':
    unittest.main()
