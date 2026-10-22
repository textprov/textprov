"""Focused shared-core tests using synthetic, host-independent observations."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from textprov.chronicle import Chronicle


def observation(key="prompt", **changes):
    fields = dict(provider="synthetic", adapter="fixture", session_id="session-1",
                  delivery_key=key, event_kind="submission", channel="user",
                  visibility="stored", text="hello", host_ids={"turn": "1"})
    fields.update(changes)
    return fields


class TestChronicle(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name) / "chronicle.sqlite"
        self.now = 100
        self.chronicle = Chronicle(self.path, max_bytes=100, ttl_seconds=10,
                             clock=lambda: self.now)
        self.addCleanup(self.chronicle.close)

    def test_idempotent_delivery_is_not_content_deduplication(self):
        first = self.chronicle.observe(**observation())
        self.assertEqual(first, self.chronicle.observe(**observation()))
        second = self.chronicle.observe(**observation("another"))
        self.assertNotEqual(first, second)
        with self.assertRaisesRegex(ValueError, "delivery key"):
            self.chronicle.observe(**observation(text="changed"))
        self.assertEqual([], self.chronicle.inspect(first)["claims"])

    def test_typed_scoped_ids_correlate_parallel_calls(self):
        first = self.chronicle.observe(**observation("call-a", host_ids={"call": "a"}))
        self.chronicle.observe(**observation("call-b", host_ids={"call": "b"}))
        result = self.chronicle.observe(**observation("result-a", host_ids={"call": "a"},
                                                  visibility="model", channel="tool"))
        for changes in ({"session_id": "other"}, {"agent_id": "child"},
                        {"provider": "other"}, {"host_ids": {"display": "a"}}):
            data = observation("unrelated", host_ids={"call": "a"})
            data.update(changes)
            self.chronicle.observe(**data)
        joins = self.chronicle.inspect(first)["event_relationships"]
        self.assertEqual([result], [j["observation_id"] for j in joins])
        self.assertEqual("call", joins[0]["kind"])

    def test_repeated_exact_passages_are_candidates_not_claims(self):
        source = self.chronicle.observe(**observation(text="😀é"))
        target = self.chronicle.observe(**observation("write", text="😀é and 😀é"))
        matches = self.chronicle.match(source, target)
        self.assertEqual("ambiguous", matches["status"])
        self.assertEqual([[0, 2], [7, 9]], [c["target_range"] for c in matches["candidates"]])
        self.assertEqual([], self.chronicle.inspect(target)["claims"])
        self.assertTrue(all(not c["selected"] for c in matches["candidates"]))

    def test_matching_never_splits_clusters_or_normalizes(self):
        source = self.chronicle.observe(**observation(text="e"))
        target = self.chronicle.observe(**observation("write", text="e\u0301"))
        self.assertEqual([], self.chronicle.match(source, target)["candidates"])
        composed = self.chronicle.observe(**observation("composed", text="é"))
        self.assertEqual([], self.chronicle.match(composed, target)["candidates"])

    def test_scope_and_missing_evidence_are_explicit(self):
        source = self.chronicle.observe(**observation())
        other = self.chronicle.observe(**observation("other", session_id="other"))
        with self.assertRaisesRegex(ValueError, "same scope"):
            self.chronicle.match(source, other)
        missing = self.chronicle.observe(**observation("missing", text=None, completeness="unobserved"))
        self.assertEqual("content_unavailable", self.chronicle.match(source, missing)["status"])
        partial = self.chronicle.observe(**observation("partial", completeness="partial"))
        self.assertEqual("incomplete_source", self.chronicle.match(partial, source)["status"])

    def claim_args(self, target, **changes):
        args = dict(observation_id=target, start=0, end=5,
                    content_hash=self.chronicle.inspect(target)["content_hash"],
                    voice_context="example", voice_id="author-a", voice_definition="Supplied author A",
                    basis="user_attestation", policy_version="manual-v1")
        args.update(changes)
        return args

    def test_claims_survive_expiry_but_text_and_new_claims_do_not(self):
        target = self.chronicle.observe(**observation())
        args = self.claim_args(target)
        claim_id = self.chronicle.claim(**args)
        self.now += 11
        info = self.chronicle.inspect(target)
        self.assertFalse(info["content_available"])
        self.assertEqual(claim_id, info["claims"][0]["claim_id"])
        self.assertEqual(claim_id, self.chronicle.claim(**args))
        with self.assertRaisesRegex(ValueError, "unavailable"):
            self.chronicle.claim(**dict(args, basis="another_attestation"))
        self.assertEqual(target, self.chronicle.observe(**observation()))
        self.assertFalse(self.chronicle.inspect(target)["content_available"])

    def test_claim_rejects_stale_hash_split_cluster_and_foreign_support(self):
        target = self.chronicle.observe(**observation(text="e\u0301😀"))
        with self.assertRaisesRegex(ValueError, "grapheme"):
            self.chronicle.claim(**self.claim_args(target, end=1))
        with self.assertRaisesRegex(ValueError, "hash"):
            self.chronicle.claim(**self.claim_args(target, end=2, content_hash="stale"))
        foreign = self.chronicle.observe(**observation("foreign", agent_id="child"))
        with self.assertRaisesRegex(ValueError, "outside scope"):
            self.chronicle.claim(**self.claim_args(target, end=2, supporting_ids=[foreign]))
        self.chronicle.claim(**self.claim_args(target, end=2))

    def test_cache_byte_bound_and_policy_survive_reopen(self):
        first = self.chronicle.observe(**observation(text="é" * 30))  # 60 UTF-8 bytes
        second = self.chronicle.observe(**observation("second", text="😀" * 15))
        oversized = self.chronicle.observe(**observation("oversized", text="x" * 101))
        with Chronicle(self.path) as reopened:
            self.assertEqual(100, reopened.max_bytes)
            # Use the same clock as the original connection for inspection.
            reopened.clock = lambda: self.now
            self.assertFalse(reopened.inspect(first)["content_available"])
            self.assertTrue(reopened.inspect(second)["content_available"])
            self.assertFalse(reopened.inspect(oversized)["content_available"])
        self.assertEqual("content_unavailable", self.chronicle.match(first, second)["status"])

    def test_invalid_observation_leaves_no_row(self):
        for changes in ({"text": None}, {"visibility": "guess"}, {"host_ids": []},
                        {"capture_sequence": True}, {"text": "\ud800"}):
            with self.assertRaises(ValueError):
                self.chronicle.observe(**observation(**changes))
        self.assertEqual(0, self.chronicle.db.execute("SELECT count(*) FROM observations").fetchone()[0])

    def test_separate_process_bridge_retries_and_inspection(self):
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]))
        command = [sys.executable, "-m", "textprov.chronicle", "--db",
                   str(self.path.with_name("bridge.sqlite"))]
        payload = json.dumps(dict(operation="observe", **observation()))
        workers = [subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True, env=env) for _ in range(2)]
        for worker in workers:
            worker.stdin.write(payload)
            worker.stdin.close()
            worker.stdin = None
        results = [worker.communicate(timeout=15) for worker in workers]
        self.assertEqual([0, 0], [worker.returncode for worker in workers], results)
        ids = [json.loads(out)["result"] for out, err in results]
        self.assertEqual(ids[0], ids[1])
        inspected = subprocess.run(command, input=json.dumps(dict(operation="inspect", observation_id=ids[0])),
                                   capture_output=True, text=True, env=env, timeout=15)
        self.assertEqual(0, inspected.returncode, inspected.stderr)
        self.assertEqual("submission", json.loads(inspected.stdout)["result"]["event_kind"])
        bad = subprocess.run(command, input='{"operation":"close"}', capture_output=True,
                             text=True, env=env, timeout=15)
        self.assertEqual(1, bad.returncode)
        self.assertIn("unknown operation", json.loads(bad.stderr)["error"])


if __name__ == "__main__":
    unittest.main()
