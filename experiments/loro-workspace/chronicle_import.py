"""Read a selected Chronicle through a disposable snapshot, never the live core."""
import hashlib
import json
from contextlib import closing
from pathlib import Path
import sqlite3
import sys
import tempfile
import time

from codec import decode
from textprov.chronicle import Chronicle


def selected_conversation(selection):
    path = Path(selection["database"])
    if not path.is_absolute() or not path.is_file():
        raise ValueError("database must select an existing absolute Chronicle file")
    path = path.resolve(strict=True)
    for key in ("provider", "session"):
        if not isinstance(selection[key], str) or not selection[key]:
            raise ValueError(key + " must be explicitly selected")
    agent = selection["agent"]  # omission is not implicit cross-agent consent
    if agent is not None and (not isinstance(agent, str) or not agent):
        raise ValueError("agent must be null (main agent) or a nonempty ID")
    cross = selection.get("cross_agent", False)
    if type(cross) is not bool:
        raise ValueError("cross_agent must be a boolean")
    limit = selection.get("max_observations", 10000)
    if type(limit) is not int or not 1 <= limit <= 10000:
        raise ValueError("max_observations must be between 1 and 10000")
    namespace = hashlib.sha256(str(path).encode("utf-8")).hexdigest()
    scope = dict(namespace=namespace, source_path=str(path), provider=selection["provider"],
                 session=selection["session"], agent=agent, cross_agent=cross)
    with tempfile.TemporaryDirectory(prefix="textprov-import-") as temp:
        snapshot = Path(temp) / "capture.sqlite"
        with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as source:
            source.execute("PRAGMA query_only=ON")
            with closing(sqlite3.connect(str(snapshot))) as target:
                source.backup(target)
                tables = {row[0] for row in target.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                if not {"settings", "observations", "cache", "claims", "host_ids", "passage_relationships"} <= tables:
                    raise ValueError("selected database is not a Chronicle")
        read_at = time.time()
        rows = []
        with Chronicle(snapshot, clock=lambda: read_at) as chronicle:
            before = None
            while True:
                page = chronicle.list_observations(scope["provider"], scope["session"],
                    agent_id=agent, cross_agent=cross, limit=100, before_id=before)
                rows.extend(page["observations"])
                if len(rows) > limit:
                    raise ValueError("selected conversation exceeds observation limit; no partial import")
                before = page["next_before_id"]
                if before is None:
                    break
            newest = rows[0]["observation_id"] if rows else None
            items, skipped, total_bytes = [], 0, 0
            for row in reversed(rows):
                role = {("submission", "user"): "user", ("assistant_message", "assistant"): "assistant"}.get(
                    (row["event_kind"], row["channel"]))
                if role is None:
                    skipped += 1
                    continue
                metadata = {k: v for k, v in row.items() if k not in
                            ("content_available", "content_expires_at")}
                portable = None
                if row["content_available"]:
                    portable = chronicle.export_chat(row["observation_id"],
                        content_hash=row["content_hash"])["text"]
                    decode(portable)  # refuse unsupported encoding before importing any message
                    total_bytes += len(portable.encode("utf-8"))
                    if total_bytes > 16 * 1024 * 1024:
                        raise ValueError("conversation export exceeds 16 MiB; no partial import")
                items.append(dict(identity=namespace + ":" + row["observation_id"],
                                  metadata=metadata, role=role, portable=portable,
                                  availability="available" if portable is not None else "unavailable"))
    return dict(scope=scope, items=items, newest_observation=newest, skipped_nonchat=skipped,
                read_at=read_at, policy="chat-speaker-v1")


if __name__ == "__main__":
    try:
        print(json.dumps({"result": selected_conversation(json.load(sys.stdin))}, ensure_ascii=True))
    except (ValueError, KeyError, TypeError, OSError, sqlite3.Error) as error:
        print(json.dumps({"error": str(error)}))
        sys.exit(1)
