"""Provider-neutral marking operations for a Git workspace.

A caller supplies a root and operation IDs; no provider events, environment
variables, or process-wide state are required. Prompt logs contain the supplied
prompt text, so callers should account for its local persistence.
"""

import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

from . import mark
from .editing import (
    HUMAN_MIN_WORDS,
    human_shingles,
    plain_map,
    remark,
    rewrite_edit,
)

SUFFIXES = (".md", ".markdown")
# Hand-built samples whose marks are the content; never touch them.
EXCLUDED = ("docs/examples/", "site/public/", "site/dist/", "node_modules/")
PROMPT_LOG_TAIL = 300
SNAPSHOT_MAX_AGE = 24 * 3600

# Only the git subcommand position counts; options can have quoted values.
_SHELL_WORD = r"""(?:"[^"]*"|'[^']*'|[^\s"'])+"""
GIT_MOVES_TREE = re.compile(
    r"\bgit(?:\s+(?:-[Cc]|--(?:git-dir|work-tree|namespace|config-env))\s+"
    + _SHELL_WORD
    + r"|\s+-"
    + _SHELL_WORD
    + r")*\s+(checkout|switch|merge|pull|rebase|stash|reset|restore"
    r"|cherry-pick|revert|apply|am|worktree|bisect)\b"
)


def read_text(path):
    try:
        with open(path, encoding="utf-8", newline="") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError):
        return None


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


class Workspace:
    """Apply the prose-marking policy within an explicitly selected Git root.

    Relative file paths resolve under root, independently of the caller's cwd.
    State defaults to root/.textprov; separate instances do not share globals.
    """

    def __init__(
        self, root, *, state_dir=None, human_min_words=HUMAN_MIN_WORDS
    ):
        if human_min_words < 1:
            raise ValueError("human_min_words must be positive")
        self.root = Path(root).resolve()
        state_path = (
            Path(state_dir) if state_dir is not None else Path(".textprov")
        )
        self.state_dir = self.resolve(state_path)
        self.prompt_log = self.state_dir / "prompts.jsonl"
        self.snapshots = self.state_dir / "snapshots"
        self.human_min_words = human_min_words

    def resolve(self, path):
        path = Path(path)
        return (path if path.is_absolute() else self.root / path).resolve()

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.root), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def relative(self, path):
        try:
            return self.resolve(path).relative_to(self.root).as_posix()
        except ValueError:
            return None

    def suffix_in_scope(self, rel):
        return (
            rel is not None
            and rel.lower().endswith(SUFFIXES)
            and not rel.startswith(".git/")
            and not any(part in rel for part in EXCLUDED)
        )

    def in_scope(self, path):
        rel = self.relative(path)
        if not self.suffix_in_scope(rel):
            return False
        return self.git("check-ignore", "-q", "--", rel).returncode != 0

    def scoped_files(self):
        listing = self.git("ls-files", "-co", "--exclude-standard", "-z").stdout
        return [
            rel
            for rel in listing.split("\0")
            if self.suffix_in_scope(rel)
            and self.suffix_in_scope(self.relative(rel))
        ]

    def head(self, suffix=""):
        return self.git(
            "rev-parse", "--verify", "-q", "HEAD" + suffix
        ).stdout.strip()

    def committed_on(self, base):
        """Distinguish a single new commit from a checkout of its revision."""
        return self.head("^") == base and self.git(
            "reflog", "-1", "--format=%gs"
        ).stdout.startswith("commit: ")

    def load_shingles(self):
        try:
            with open(self.prompt_log, encoding="utf-8") as handle:
                entries = handle.readlines()[-PROMPT_LOG_TAIL:]
        except OSError:
            return set()
        texts = []
        for entry in entries:
            try:
                text = json.loads(entry)["text"]
            except (ValueError, KeyError, TypeError):
                continue
            if isinstance(text, str):
                texts.append(text)
        return human_shingles(texts, self.human_min_words)

    def record_prompt(self, prompt, session=None):
        """Append human-marked prompt text to the local JSONL log."""
        if not isinstance(prompt, str) or not prompt.strip():
            return
        self.state_dir.mkdir(parents=True, exist_ok=True)
        entry = {
            "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "session": session,
            "text": mark(prompt, state="human"),
        }
        with open(self.prompt_log, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def prepare_write(self, path, content):
        """Return marked content, or None when the file is outside scope."""
        if not self.in_scope(path):
            return None
        return remark(
            read_text(self.resolve(path)) or "",
            content,
            shingles=self.load_shingles(),
            min_words=self.human_min_words,
        )

    def prepare_edit(self, path, old_string, new_string, replace_all=False):
        """Return a mark-aware replacement pair; ambiguous edits raise Ambiguous."""
        snapshot = self._prepare_edit_snapshot(
            path, old_string, new_string, replace_all
        )
        return snapshot[2] if snapshot is not None else None

    def _prepare_edit_snapshot(self, path, old_string, new_string, replace_all):
        if not self.in_scope(path):
            return None
        target = self.resolve(path)
        raw = read_text(target)
        if raw is None:
            return None
        result = rewrite_edit(
            raw,
            old_string,
            new_string,
            replace_all,
            shingles=self.load_shingles(),
            min_words=self.human_min_words,
        )
        return (target, raw, result) if result is not None else None

    def has_marks(self, path):
        """Report whether an in-scope file carries provenance marks."""
        if not self.in_scope(path):
            return False
        raw = read_text(self.resolve(path))
        return raw is not None and plain_map(raw)[0] != raw

    def apply_edit(self, path, old_string, new_string, replace_all=False):
        """Apply a mark-aware replacement and return how many places changed.

        For callers that cannot have their own edit rewritten by prepare_edit.
        Returns 0 when the file is out of scope or old_string is absent;
        ambiguous edits raise Ambiguous and leave the file alone. Preparation
        and replacement share one raw snapshot; this is not a locked write.
        """
        snapshot = self._prepare_edit_snapshot(
            path, old_string, new_string, replace_all
        )
        if snapshot is None:
            return 0
        target, raw, (old, new) = snapshot
        count = raw.count(old)
        if not replace_all:
            count = min(count, 1)
        if old != new:
            write_text(target, raw.replace(old, new, count))
        return count

    def snapshot_path(self, operation_id):
        # Provider IDs may contain separators, or differ only by case on macOS.
        name = hashlib.sha256(
            (operation_id or "none").encode("utf-8")
        ).hexdigest()
        return self.snapshots / f"{name}.json"

    def before_command(self, command, operation_id):
        """Snapshot eligible files before a command; skip known Git tree moves."""
        if GIT_MOVES_TREE.search(command):
            return
        self.snapshots.mkdir(parents=True, exist_ok=True)
        now = time.time()
        for stale in self.snapshots.glob("*.json"):
            if now - stale.stat().st_mtime > SNAPSHOT_MAX_AGE:
                stale.unlink()
        files = {}
        for rel in self.scoped_files():
            text = read_text(self.root / rel)
            if text is not None:
                files[rel] = text
        self.snapshot_path(operation_id).write_text(
            json.dumps({"head": self.head(), "files": files}), encoding="utf-8"
        )

    def after_command(self, operation_id):
        """Mark changed files against the matching snapshot, then consume it.

        A revision change is ignored unless it was exactly one new commit.
        New paths containing an unchanged copy of old text are not new writing.
        """
        path = self.snapshot_path(operation_id)
        if not path.exists():
            return
        snapshot = json.loads(path.read_text(encoding="utf-8"))
        path.unlink()
        if snapshot["head"] != self.head() and not self.committed_on(
            snapshot["head"]
        ):
            return
        before = snapshot["files"]
        known = None
        shingles = None
        for rel in self.scoped_files():
            text = read_text(self.root / rel)
            if text is None or text == before.get(rel):
                continue
            if rel not in before:
                if known is None:
                    known = {plain_map(old)[0] for old in before.values()}
                if plain_map(text)[0] in known:
                    continue
            if shingles is None:
                shingles = self.load_shingles()
            marked = remark(
                before.get(rel, ""),
                text,
                carry=False,
                shingles=shingles,
                min_words=self.human_min_words,
            )
            if marked != text and self.in_scope(rel):
                write_text(self.root / rel, marked)
