"""Experimental shared plugin core. No host integration or in-band encoding.

Run ``python -m textprov.chronicle --db PATH`` with one JSON request on stdin.
The database belongs to one project; provider/session scope bounds optional cross-agent joins.
"""

import argparse
import hashlib
import json
import sqlite3
import sys
import time
import uuid

from ._grapheme import segments


def _json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _string(value, name):
    if not isinstance(value, str) or not value:
        raise ValueError(name + " must be a nonempty string")
    value.encode("utf-8")  # Reject lone surrogates: offsets are Unicode scalars.
    return value


def _attributes(value):
    """Accept bounded, strict JSON metadata, never Python-only coercions."""
    value = {} if value is None else value

    def validate(item, depth=0):
        if depth > 16:
            raise ValueError("attributes nesting exceeds 16 levels")
        if isinstance(item, dict):
            for key, child in item.items():
                if not isinstance(key, str):
                    raise ValueError("attributes keys must be strings")
                validate(child, depth + 1)
        elif isinstance(item, list):
            for child in item:
                validate(child, depth + 1)
        elif item is not None and type(item) not in (str, int, float, bool):
            raise ValueError("attributes must contain JSON values")

    if not isinstance(value, dict):
        raise ValueError("attributes must be an object")
    validate(value)
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False,
                         separators=(",", ":"), allow_nan=False)
    if len(encoded.encode("utf-8")) > 4096:
        raise ValueError("attributes exceed 4096 UTF-8 bytes")
    return json.loads(encoded)


def _validate_cross_agent(cross_agent):
    if type(cross_agent) is not bool:
        raise ValueError("cross_agent must be a boolean")


def _scope_matches(a, b, cross_agent):
    return a == b or (cross_agent and json.loads(a)[:2] == json.loads(b)[:2])


def _boundaries(text):
    result, offset = {0}, 0
    for cluster in segments(text):
        offset += len(cluster)
        result.add(offset)
    return result


class Chronicle:
    """Transactional metadata with an expiring, globally byte-bounded text cache.

    Cache policy is persisted on creation and shared by all processes. Expiration
    is lazy on operations, not a background deletion service. Metadata persists.
    Callers supply stable delivery keys; text equality never deduplicates events.
    """

    def __init__(self, path, *, max_bytes=1024 * 1024, ttl_seconds=3600, clock=time.time):
        if type(max_bytes) is not int or max_bytes < 0:
            raise ValueError("max_bytes must be a nonnegative integer")
        if type(ttl_seconds) is not int or ttl_seconds < 0:
            raise ValueError("ttl_seconds must be a nonnegative integer")
        self.clock = clock
        self.db = sqlite3.connect(str(path), timeout=10, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS settings (
                singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
                version INTEGER NOT NULL, max_bytes INTEGER NOT NULL, ttl INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS observations (
                id TEXT PRIMARY KEY, scope TEXT NOT NULL, adapter TEXT NOT NULL,
                delivery_key TEXT NOT NULL, record TEXT NOT NULL, captured_at REAL NOT NULL,
                UNIQUE(scope, adapter, delivery_key)
            );
            CREATE TABLE IF NOT EXISTS host_ids (
                observation_id TEXT NOT NULL REFERENCES observations(id),
                scope TEXT NOT NULL, kind TEXT NOT NULL, value TEXT NOT NULL,
                PRIMARY KEY(observation_id, kind)
            );
            CREATE INDEX IF NOT EXISTS host_join ON host_ids(scope, kind, value);
            CREATE TABLE IF NOT EXISTS cache (
                observation_id TEXT PRIMARY KEY REFERENCES observations(id),
                text TEXT NOT NULL, bytes INTEGER NOT NULL, expires REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS claims (
                id TEXT PRIMARY KEY, observation_id TEXT NOT NULL REFERENCES observations(id),
                record TEXT NOT NULL
            );
        """)
        self.db.execute("INSERT OR IGNORE INTO settings VALUES (1, 1, ?, ?)",
                        (max_bytes, ttl_seconds))
        settings = self.db.execute("SELECT * FROM settings").fetchone()
        if settings["version"] != 1:
            self.close()
            raise ValueError("unsupported chronicle schema")
        self.max_bytes, self.ttl = settings["max_bytes"], settings["ttl"]

    def close(self):
        self.db.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _transaction(self, action):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            self._prune()
            result = action()
            self.db.execute("COMMIT")
            return result
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def _prune(self):
        self.db.execute("DELETE FROM cache WHERE expires <= ?", (self.clock(),))
        rows = self.db.execute("""SELECT c.observation_id, c.bytes FROM cache c
            JOIN observations o ON o.id = c.observation_id
            ORDER BY o.captured_at, o.rowid""").fetchall()
        total = sum(row["bytes"] for row in rows)
        for row in rows:
            if total <= self.max_bytes:
                break
            self.db.execute("DELETE FROM cache WHERE observation_id = ?", (row[0],))
            total -= row["bytes"]

    def _observation(self, observation_id):
        row = self.db.execute("SELECT * FROM observations WHERE id = ?",
                              (observation_id,)).fetchone()
        if row is None:
            raise ValueError("unknown observation: " + str(observation_id))
        return row

    def _text(self, observation_id):
        row = self.db.execute("SELECT text FROM cache WHERE observation_id = ?",
                              (observation_id,)).fetchone()
        if row is None:
            raise ValueError("content unavailable: " + observation_id)
        return row[0]

    def observe(self, *, provider, adapter, session_id, delivery_key, event_kind,
                channel, visibility, text=None, completeness="complete",
                agent_id=None, host_version=None, host_ids=None, capture_sequence=None,
                attributes=None):
        """Record one content block. Retry with the same key and identical fields.

        A changed payload under an existing delivery key is rejected. Missing text
        must explicitly use completeness='unobserved'. No claims are inferred.
        """
        fields = dict(provider=provider, adapter=adapter, session_id=session_id,
                      delivery_key=delivery_key, event_kind=event_kind, channel=channel)
        for name, value in fields.items():
            _string(value, name)
        if agent_id is not None:
            _string(agent_id, "agent_id")
        if host_version is not None:
            _string(host_version, "host_version")
        if visibility not in {"structured", "model", "stored", "display"}:
            raise ValueError("invalid visibility")
        if completeness not in {"complete", "partial", "truncated", "unobserved"}:
            raise ValueError("invalid completeness")
        if (text is None) != (completeness == "unobserved"):
            raise ValueError("missing text requires unobserved completeness and vice versa")
        if text is not None and not isinstance(text, str):
            raise ValueError("text must be a string")
        if capture_sequence is not None and (type(capture_sequence) is not int or capture_sequence < 0):
            raise ValueError("capture_sequence must be a nonnegative integer")
        ids = {} if host_ids is None else host_ids
        if not isinstance(ids, dict):
            raise ValueError("host_ids must be an object")
        for kind, value in ids.items():
            _string(kind, "ID kind")
            _string(value, "ID value")
        attributes = _attributes(attributes)
        raw = None if text is None else text.encode("utf-8")
        record = dict(fields, schema_version=1, agent_id=agent_id, host_version=host_version,
                      host_ids=ids, visibility=visibility, completeness=completeness,
                      capture_sequence=capture_sequence,
                      content_hash=None if raw is None else hashlib.sha256(raw).hexdigest(),
                      scalar_length=None if text is None else len(text))
        record["attributes"] = attributes
        canonical = _json(record)
        scope = _json([provider, session_id, agent_id])

        def action():
            previous = self.db.execute("""SELECT id, record FROM observations
                WHERE scope = ? AND adapter = ? AND delivery_key = ?""",
                (scope, adapter, delivery_key)).fetchone()
            if previous:
                prior = json.loads(previous["record"])
                prior.setdefault("attributes", {})  # Records written before attributes.
                if _json(prior) != canonical:
                    raise ValueError("delivery key reused with different observation")
                return previous["id"]
            observation_id = str(uuid.uuid4())
            now = self.clock()
            self.db.execute("INSERT INTO observations VALUES (?, ?, ?, ?, ?, ?)",
                            (observation_id, scope, adapter, delivery_key, canonical, now))
            self.db.executemany("INSERT INTO host_ids VALUES (?, ?, ?, ?)",
                                [(observation_id, scope, k, v) for k, v in ids.items()])
            if raw is not None and len(raw) <= self.max_bytes and self.ttl > 0:
                self.db.execute("INSERT INTO cache VALUES (?, ?, ?, ?)",
                                (observation_id, text, len(raw), now + self.ttl))
            self._prune()
            return observation_id
        return self._transaction(action)

    def session(self, provider, session_id):
        """Summarize observations across all agents in one provider/session.

        The maximum sequence is a snapshot, not an atomic sequence allocator.
        """
        _string(provider, "provider")
        _string(session_id, "session_id")

        def action():
            row = self.db.execute("""
                SELECT count(*) AS observation_count,
                       max(json_extract(record, '$.capture_sequence')) AS max_capture_sequence
                FROM observations
                WHERE json_extract(scope, '$[0]') = ?
                  AND json_extract(scope, '$[1]') = ?
            """, (provider, session_id)).fetchone()
            return dict(row)
        return self._transaction(action)

    def status(self):
        """Return project totals and live cache usage after lazy expiration."""
        def action():
            return dict(
                observation_count=self.db.execute("SELECT count(*) FROM observations").fetchone()[0],
                claim_count=self.db.execute("SELECT count(*) FROM claims").fetchone()[0],
                cached_observation_count=self.db.execute("SELECT count(*) FROM cache").fetchone()[0],
                cached_bytes=self.db.execute("SELECT coalesce(sum(bytes), 0) FROM cache").fetchone()[0],
                max_bytes=self.max_bytes, ttl_seconds=self.ttl)
        return self._transaction(action)

    def inspect(self, observation_id, *, cross_agent=False):
        """Inspect metadata, typed ID joins and claims without returning raw text."""
        _validate_cross_agent(cross_agent)

        def action():
            row = self._observation(observation_id)
            joins = self.db.execute("""SELECT b.observation_id, a.kind, a.value, b.scope
                FROM host_ids a JOIN host_ids b
                  ON a.kind = b.kind AND a.value = b.value
                WHERE a.observation_id = ? AND b.observation_id != ?
                ORDER BY b.observation_id, a.kind""", (observation_id, observation_id))
            retained = self.db.execute("SELECT expires FROM cache WHERE observation_id = ?",
                                       (observation_id,)).fetchone()
            claims = self.db.execute("SELECT record FROM claims WHERE observation_id = ? ORDER BY id",
                                     (observation_id,))
            metadata = json.loads(row["record"])
            metadata.setdefault("attributes", {})
            return dict(metadata, observation_id=observation_id,
                        captured_at=row["captured_at"], content_available=retained is not None,
                        content_expires_at=None if retained is None else retained["expires"],
                        event_relationships=[
                            dict(observation_id=j["observation_id"], kind=j["kind"],
                                 value=j["value"], basis="host_id")
                            for j in joins if _scope_matches(row["scope"], j["scope"], cross_agent)],
                        claims=[json.loads(c[0]) for c in claims])
        return self._transaction(action)

    def match(self, source_id, target_id, *, cross_agent=False):
        """Find every exact occurrence of the full source block in a target block.

        This deliberately small matcher does not infer chronology or attribution,
        normalize text or match partial source blocks. Cross-agent access is opt-in
        and always stays within a provider/session.
        """
        _validate_cross_agent(cross_agent)

        def action():
            source, target = self._observation(source_id), self._observation(target_id)
            if source_id == target_id or not _scope_matches(source["scope"], target["scope"], cross_agent):
                raise ValueError("matching requires distinct observations in the same scope")
            a, b = json.loads(source["record"]), json.loads(target["record"])
            if a["completeness"] != "complete":
                return {"status": "incomplete_source", "candidates": []}
            try:
                needle, haystack = self._text(source_id), self._text(target_id)
            except ValueError:
                return {"status": "content_unavailable", "candidates": []}
            if not needle:
                return {"status": "empty_source", "candidates": []}
            boundaries = _boundaries(haystack)
            candidates, start = [], 0
            while True:
                start = haystack.find(needle, start)
                if start < 0:
                    break
                end = start + len(needle)
                if start in boundaries and end in boundaries:
                    candidates.append(dict(source_id=source_id, target_id=target_id,
                        source_range=[0, len(needle)], target_range=[start, end],
                        source_hash=a["content_hash"], target_hash=b["content_hash"],
                        method="exact", basis="text_equality", selected=False,
                        target_completeness=b["completeness"]))
                start += 1
            return {"status": "ambiguous" if len(candidates) > 1 else "searched",
                    "candidates": candidates}
        return self._transaction(action)

    def claim(self, *, observation_id, start, end, content_hash, voice_context,
              voice_id, voice_definition, basis, policy_version, supporting_ids=None,
              cross_agent=False):
        """Persist an explicit claim; identical requests are idempotent.

        Claims can conflict and remain separately inspectable. No automatic winner
        or voice projection is applied. The caller supplies the voice definition.
        """
        for name, value in dict(voice_context=voice_context, voice_id=voice_id,
                                voice_definition=voice_definition, basis=basis,
                                policy_version=policy_version).items():
            _string(value, name)
        _validate_cross_agent(cross_agent)
        support = [] if supporting_ids is None else supporting_ids
        if not isinstance(support, list) or any(not isinstance(s, str) for s in support):
            raise ValueError("supporting_ids must be a list of observation IDs")

        def action():
            row = self._observation(observation_id)
            metadata = json.loads(row["record"])
            if metadata["content_hash"] != content_hash or content_hash is None:
                raise ValueError("claim content hash does not match observation")
            if type(start) is not int or type(end) is not int or not 0 <= start < end <= metadata["scalar_length"]:
                raise ValueError("invalid scalar range")
            for supporting_id in support:
                if not _scope_matches(self._observation(supporting_id)["scope"],
                                      row["scope"], cross_agent):
                    raise ValueError("supporting observation is outside scope")
            record = dict(observation_id=observation_id, range=[start, end],
                          content_hash=content_hash, voice_context=voice_context,
                          voice_id=voice_id, voice_definition=voice_definition, basis=basis,
                          policy_version=policy_version, supporting_ids=sorted(set(support)))
            canonical = _json(record)
            claim_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            if self.db.execute("SELECT 1 FROM claims WHERE id = ?", (claim_id,)).fetchone():
                return claim_id
            boundaries = _boundaries(self._text(observation_id))
            if start not in boundaries or end not in boundaries:
                raise ValueError("claim splits a grapheme cluster")
            self.db.execute("INSERT INTO claims VALUES (?, ?, ?)",
                            (claim_id, observation_id, _json(dict(record, claim_id=claim_id))))
            return claim_id
        return self._transaction(action)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True, help="project-specific SQLite file")
    args = parser.parse_args(argv)
    try:
        request = json.load(sys.stdin)
        if not isinstance(request, dict):
            raise ValueError("request must be an object")
        operation = request.pop("operation", None)
        if operation not in {"observe", "inspect", "match", "claim", "session", "status"}:
            raise ValueError("unknown operation")
        with Chronicle(args.db) as chronicle:
            result = getattr(chronicle, operation)(**request)
        print(_json({"result": result}))
        return 0
    except (ValueError, TypeError, OSError, sqlite3.Error) as error:
        print(_json({"error": str(error)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
