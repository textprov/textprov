"""Focused shared-core tests using synthetic, host-independent observations."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from textprov.chronicle import Chronicle
from textprov import mark, mark_chat


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

    def test_export_chat_applies_speaker_policy_without_changing_evidence(self):
        for role, event in (("user", "submission"), ("assistant", "assistant_message")):
            original = mark("pasted", "human") + " fresh"
            key = self.chronicle.observe(**observation(role, text=original,
                                                       channel=role, event_kind=event))
            before = self.chronicle.inspect(key)
            exported = self.chronicle.export_chat(key, content_hash=before["content_hash"])
            self.assertEqual(mark_chat(original, role), exported["text"])
            self.assertEqual(role, exported["role"])
            self.assertEqual("chat-speaker-v1", exported["policy"])
            self.assertEqual(before, self.chronicle.inspect(key))
            self.assertEqual(original, self.chronicle._text(key))
            self.assertEqual([], self.chronicle.inspect(key)["claims"])

    def test_export_chat_refuses_nonchat_stale_missing_and_expired_content(self):
        key = self.chronicle.observe(**observation())
        digest = self.chronicle.inspect(key)["content_hash"]
        with self.assertRaisesRegex(ValueError, "hash"):
            self.chronicle.export_chat(key, content_hash="stale")
        with self.assertRaisesRegex(ValueError, "unknown observation"):
            self.chronicle.export_chat("missing", content_hash=digest)
        tool = self.chronicle.observe(**observation("tool", event_kind="tool_result",
                                                    channel="tool"))
        with self.assertRaisesRegex(ValueError, "not a user or assistant"):
            self.chronicle.export_chat(tool,
                                      content_hash=self.chronicle.inspect(tool)["content_hash"])
        self.now = 111
        with self.assertRaisesRegex(ValueError, "content unavailable"):
            self.chronicle.export_chat(key, content_hash=digest)

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
        self.assertEqual(0, self.chronicle.status()["observation_count"])

    def test_session_and_status_hide_storage_and_prune_cache(self):
        self.assertEqual(dict(observation_count=0, max_capture_sequence=None),
                         self.chronicle.session("synthetic", "session-1"))
        a = self.chronicle.observe(**observation(capture_sequence=0))
        self.chronicle.observe(**observation("child", agent_id="child", capture_sequence=9))
        self.chronicle.observe(**observation("missing-sequence"))
        self.chronicle.observe(**observation("foreign", provider="other", capture_sequence=99))
        self.chronicle.observe(**observation("session", session_id="other", capture_sequence=99))
        self.assertEqual(dict(observation_count=3, max_capture_sequence=9),
                         self.chronicle.session("synthetic", "session-1"))
        self.chronicle.claim(**self.claim_args(a))
        self.assertEqual(5, self.chronicle.status()["cached_observation_count"])
        self.assertEqual(25, self.chronicle.status()["cached_bytes"])
        self.now = 110
        status = self.chronicle.status()
        self.assertEqual((5, 1, 0, 0), tuple(status[k] for k in
                         ("observation_count", "claim_count", "cached_observation_count", "cached_bytes")))

    def test_inspect_expiry_is_live_cache_deadline(self):
        a = self.chronicle.observe(**observation())
        self.assertEqual(110, self.chronicle.inspect(a)["content_expires_at"])
        self.now = 105
        self.chronicle.observe(**observation())
        self.assertEqual(110, self.chronicle.inspect(a)["content_expires_at"])
        self.now = 110
        self.assertIsNone(self.chronicle.inspect(a)["content_expires_at"])
        for key, changes in (("missing", dict(text=None, completeness="unobserved")),
                             ("oversized", dict(text="x" * 101))):
            b = self.chronicle.observe(**observation(key, **changes))
            self.assertIsNone(self.chronicle.inspect(b)["content_expires_at"])

    def test_attributes_are_bounded_and_canonical(self):
        data = observation(attributes={"replace_all": False, "nested": [None, {"a": 1}]})
        a = self.chronicle.observe(**data)
        self.assertEqual(data["attributes"], self.chronicle.inspect(a)["attributes"])
        self.assertEqual(a, self.chronicle.observe(**data))
        with self.assertRaisesRegex(ValueError, "delivery key"):
            self.chronicle.observe(**dict(data, attributes={"replace_all": True}))
        for attributes in ([], {"x": float("nan")}, {"x": float("inf")},
                           {1: "bad"}, {"nested": {2: "bad"}}, {"x": (1, 2)},
                           {"x": "é" * 2048}):
            with self.assertRaises(ValueError):
                self.chronicle.observe(**observation("invalid", attributes=attributes))
        self.assertEqual(1, self.chronicle.status()["observation_count"])
        deep = {}
        for _ in range(17):
            deep = {"x": deep}
        with self.assertRaisesRegex(ValueError, "nesting"):
            self.chronicle.observe(**observation("deep", attributes=deep))
        self.chronicle.observe(**observation("limit", attributes={"x": "a" * 4088}))
        with self.assertRaisesRegex(ValueError, "4096"):
            self.chronicle.observe(**observation("over-limit", attributes={"x": "a" * 4089}))

    def test_cross_agent_access_is_explicit_and_session_bounded(self):
        a = self.chronicle.observe(**observation(host_ids={"agent": "child"}))
        b = self.chronicle.observe(**observation("write", agent_id="child",
                                                host_ids={"agent": "child"}))
        self.assertEqual([], self.chronicle.inspect(a)["event_relationships"])
        joins = self.chronicle.inspect(a, cross_agent=True)["event_relationships"]
        self.assertEqual([b], [j["observation_id"] for j in joins])
        with self.assertRaises(ValueError):
            self.chronicle.match(a, b)
        matches = self.chronicle.match(a, b, cross_agent=True)
        self.assertEqual(1, len(matches["candidates"]))
        self.assertFalse(matches["candidates"][0]["selected"])
        self.assertEqual([], self.chronicle.inspect(b)["claims"])
        args = self.claim_args(b, supporting_ids=[a])
        with self.assertRaises(ValueError):
            self.chronicle.claim(**args)
        self.chronicle.claim(**args, cross_agent=True)
        for key, change in (("provider", dict(provider="other")),
                            ("session", dict(session_id="other"))):
            foreign = self.chronicle.observe(**observation(key, host_ids={"agent": "child"}, **change))
            with self.assertRaises(ValueError):
                self.chronicle.match(a, foreign, cross_agent=True)
            with self.assertRaises(ValueError):
                self.chronicle.claim(**self.claim_args(b, supporting_ids=[foreign]), cross_agent=True)
        self.assertEqual([b], [j["observation_id"] for j in
                              self.chronicle.inspect(a, cross_agent=True)["event_relationships"]])
        for operation in (lambda: self.chronicle.inspect(a, cross_agent="false"),
                          lambda: self.chronicle.match(a, b, cross_agent=1),
                          lambda: self.chronicle.claim(**args, cross_agent=None)):
            with self.assertRaisesRegex(ValueError, "boolean"):
                operation()

    def test_shared_matching_keeps_claims_explicit_and_observations_unchanged(self):
        a = self.chronicle.observe(**observation(text="  alpha\r\n    beta"))
        b = self.chronicle.observe(**observation("write", text="\talpha\n\t  beta",
                                                agent_id="child"))
        before = self.chronicle.inspect(b)
        result = self.chronicle.match(a, b, policy="common-indent-v1", cross_agent=True)
        candidate = result["candidates"][0]
        self.assertEqual(a, candidate["source_id"])
        self.assertEqual(before["content_hash"], candidate["target_hash"])
        self.assertEqual(before, self.chronicle.inspect(b))
        for start, end in candidate["target_segments"]:
            self.chronicle.claim(**self.claim_args(
                b, start=start, end=end, supporting_ids=[a], cross_agent=True,
                basis="explicit_test_selection", policy_version="test-policy-v1"))
        self.assertEqual([[1, 7], [8, 14]], sorted(
            c["range"] for c in self.chronicle.inspect(b)["claims"]))
        with self.assertRaises(ValueError):
            self.chronicle.match(a, b, policy="common-indent-v1")
        self.now = 110
        self.assertEqual("content_unavailable", self.chronicle.match(
            a, b, policy="common-indent-v1", partial=True, cross_agent=True)["status"])

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
        for request, expected in (
            (dict(operation="session", provider="synthetic", session_id="session-1"), 1),
            (dict(operation="status"), 1)):
            result = subprocess.run(command, input=json.dumps(request), capture_output=True,
                                    text=True, env=env, timeout=15)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(expected, json.loads(result.stdout)["result"]["observation_count"])
        target = subprocess.run(command, input=json.dumps(dict(
            operation="observe", **observation("write", text="  hel\r\nworld"))),
            capture_output=True, text=True, env=env, timeout=15)
        self.assertEqual(0, target.returncode, target.stderr)
        target_id = json.loads(target.stdout)["result"]
        matched = subprocess.run(command, input=json.dumps(dict(
            operation="match", source_id=ids[0], target_id=target_id,
            policy="common-indent-v1", partial=True, min_match_chars=3)),
            capture_output=True, text=True, env=env, timeout=15)
        self.assertEqual(0, matched.returncode, matched.stderr)
        candidate = json.loads(matched.stdout)["result"]["candidates"][0]
        self.assertEqual([0, 3], candidate["source_range"])
        self.assertEqual([2, 5], candidate["target_range"])
        bad = subprocess.run(command, input='{"operation":"close"}', capture_output=True,
                             text=True, env=env, timeout=15)
        self.assertEqual(1, bad.returncode)
        self.assertIn("unknown operation", json.loads(bad.stderr)["error"])


if __name__ == "__main__":
    unittest.main()
