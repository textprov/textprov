"""Supplied attribution policy tests; these do not establish host coverage."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from textprov.chronicle import Chronicle


class TestPolicy(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "policy.sqlite"
        self.now = 100
        self.chronicle = Chronicle(self.path, ttl_seconds=10, clock=lambda: self.now)
        self.addCleanup(self.chronicle.close)

    def observe(self, key, text, **changes):
        fields = dict(provider="fixture", adapter="policy-test-v1", session_id="session",
                      delivery_key=key, event_kind="capture", channel="user",
                      visibility="stored", text=text)
        fields.update(changes)
        return self.chronicle.observe(**fields)

    def claim(self, observation_id, start, end, voice="a", **changes):
        fields = dict(observation_id=observation_id, start=start, end=end,
                      content_hash=self.chronicle.inspect(observation_id)["content_hash"],
                      voice_context="document", voice_id=voice,
                      voice_definition="Supplied " + voice, basis="attestation",
                      policy_version="manual-v1")
        fields.update(changes)
        return self.chronicle.claim(**fields)

    def arguments(self, source, target, claim_ids, **changes):
        fields = dict(source_id=source, target_id=target, candidate_index=0,
                      source_claim_ids=claim_ids,
                      source_hash=self.chronicle.inspect(source)["content_hash"],
                      target_hash=self.chronicle.inspect(target)["content_hash"])
        fields.update(changes)
        return fields

    def ranges(self, observation_id):
        return [(item["range"], item["voice_id"])
                for item in self.chronicle.resolve(observation_id)["ranges"]]

    def test_multiple_supplied_voices_leave_unknown_ranges_unknown(self):
        source = self.observe("source", "alpha ? beta")
        target = self.observe("target", "x alpha ? beta y", channel="assistant")
        a = self.claim(source, 0, 5)
        b = self.claim(source, 8, 12, "b")
        evidence = self.chronicle.transfer(**self.arguments(source, target, [b, a]))
        self.assertEqual([([0, 2], None), ([2, 7], "a"), ([7, 10], None),
                          ([10, 14], "b"), ([14, 16], None)], self.ranges(target))
        inspected = self.chronicle.inspect(target)
        self.assertEqual(2, len(inspected["claims"]))
        self.assertEqual([evidence], inspected["passage_relationships"])
        self.assertTrue(evidence["candidate"]["selected"])
        self.assertTrue(all(item["basis"] == "supplied_claim_transfer" for item in inspected["claims"]))
        self.assertEqual({a, b}, {item["supporting_claim_ids"][0] for item in inspected["claims"]})

    def test_normalization_maps_claims_without_claiming_removed_indentation(self):
        source = self.observe("source", "  alpha\r\n    beta")
        target = self.observe("target", "\talpha\n\t  beta")
        supplied = self.claim(source, 0, 17)
        evidence = self.chronicle.transfer(**self.arguments(
            source, target, [supplied], comparison_policy="common-indent-v1"))
        self.assertEqual([([0, 1], None), ([1, 7], "a"), ([7, 8], None), ([8, 14], "a")],
                         self.ranges(target))
        self.assertEqual([[1, 7], [8, 14]], evidence["candidate"]["target_segments"])

    def test_repeated_candidates_require_explicit_selection(self):
        source = self.observe("source", "echo")
        target = self.observe("target", "echo echo")
        supplied = self.claim(source, 0, 4)
        arguments = self.arguments(source, target, [supplied], candidate_index=1)
        self.chronicle.transfer(**arguments)
        self.assertEqual([([0, 5], None), ([5, 9], "a")], self.ranges(target))
        for value in (None, True, -1, 2):
            with self.assertRaises(ValueError):
                self.chronicle.transfer(**dict(arguments, candidate_index=value))
        arguments.pop("candidate_index")
        with self.assertRaises(TypeError):
            self.chronicle.transfer(**arguments)

    def test_partial_transfers_never_fill_changed_middle(self):
        source = self.observe("source", "abcXYZdef")
        target = self.observe("target", "abc123def")
        supplied = self.claim(source, 0, 9)
        arguments = self.arguments(source, target, [supplied], partial=True, min_match_chars=3)
        self.chronicle.transfer(**arguments)
        self.chronicle.transfer(**dict(arguments, candidate_index=1))
        self.assertEqual([([0, 3], "a"), ([3, 6], None), ([6, 9], "a")], self.ranges(target))
        self.assertEqual(2, len(self.chronicle.inspect(target)["passage_relationships"]))

    def test_unicode_graphemes_and_crlf_are_preserved(self):
        source = self.observe("source", "e\u0301\r\n👩‍💻")
        target = self.observe("target", "(e\u0301\n👩‍💻)")
        first = self.claim(source, 0, 4)
        second = self.claim(source, 4, 7, "b")
        self.chronicle.transfer(**self.arguments(source, target, [first, second],
                                                comparison_policy="line-endings-v1"))
        self.assertEqual([([0, 1], None), ([1, 4], "a"), ([4, 7], "b"), ([7, 8], None)],
                         self.ranges(target))

    def test_source_conflicts_cannot_be_hidden_by_selecting_only_one_claim(self):
        source = self.observe("source", "abcde")
        target = self.observe("target", "abcde")
        supplied = self.claim(source, 0, 5)
        self.claim(source, 2, 5, "b")
        with self.assertRaisesRegex(ValueError, "conflicting overlapping"):
            self.chronicle.transfer(**self.arguments(source, target, [supplied]))
        with self.assertRaisesRegex(ValueError, "conflicting overlapping"):
            self.chronicle.resolve(source)
        self.assertEqual([], self.chronicle.inspect(target)["claims"])

    def test_overlapping_selected_source_claims_are_rejected(self):
        source = self.observe("source", "abcde")
        target = self.observe("target", "abcde")
        a = self.claim(source, 0, 4)
        b = self.claim(source, 2, 5)
        self.assertEqual([([0, 5], "a")], self.ranges(source))
        with self.assertRaisesRegex(ValueError, "source claims overlap"):
            self.chronicle.transfer(**self.arguments(source, target, [a, b]))

    def test_target_conflict_rolls_back_entire_transfer(self):
        source = self.observe("source", "alpha beta")
        target = self.observe("target", "alpha beta")
        a = self.claim(source, 0, 5)
        b = self.claim(source, 6, 10, "b")
        existing = self.claim(target, 7, 10, "c")
        before = self.chronicle.status()
        with self.assertRaisesRegex(ValueError, "conflicting overlapping"):
            self.chronicle.transfer(**self.arguments(source, target, [a, b]))
        self.assertEqual(before, self.chronicle.status())
        inspected = self.chronicle.inspect(target)
        self.assertEqual([existing], [item["claim_id"] for item in inspected["claims"]])
        self.assertEqual([], inspected["passage_relationships"])

    def test_same_voice_overlap_resolves_and_definition_conflict_refuses(self):
        source = self.observe("source", "abcdef")
        target = self.observe("target", "abcdef")
        supplied = self.claim(source, 0, 6)
        existing = self.claim(target, 0, 2)
        self.chronicle.transfer(**self.arguments(source, target, [supplied]))
        resolution = self.chronicle.resolve(target)
        self.assertEqual([([0, 6], "a")], self.ranges(target))
        self.assertIn(existing, resolution["ranges"][0]["claim_ids"])
        self.claim(target, 5, 6, voice_definition="Different definition")
        with self.assertRaisesRegex(ValueError, "conflicting definitions"):
            self.chronicle.resolve(target)

    def test_retry_and_resolution_keep_evidence_after_cache_expiry(self):
        source = self.observe("source", "alpha")
        target = self.observe("target", "alpha")
        supplied = self.claim(source, 0, 5)
        arguments = self.arguments(source, target, [supplied])
        evidence = self.chronicle.transfer(**arguments)
        self.assertEqual(evidence, self.chronicle.transfer(**arguments))
        self.now += 11
        self.assertFalse(self.chronicle.inspect(target)["content_available"])
        self.assertEqual(evidence, self.chronicle.transfer(**arguments))
        self.assertEqual([evidence], self.chronicle.inspect(source)["passage_relationships"])
        self.assertEqual([([0, 5], "a")], self.ranges(target))
        self.assertEqual(2, self.chronicle.status()["claim_count"])
        with self.assertRaisesRegex(ValueError, "unavailable"):
            self.chronicle.transfer(**dict(arguments, partial=True))

    def test_hashes_claim_membership_policy_and_completeness_are_checked(self):
        source = self.observe("source", "alpha")
        target = self.observe("target", "alpha")
        unrelated = self.observe("unrelated", "alpha")
        supplied = self.claim(source, 0, 5)
        unrelated_claim = self.claim(unrelated, 0, 5)
        arguments = self.arguments(source, target, [supplied])
        for changes in (dict(source_hash="stale"), dict(target_hash="stale"),
                        dict(policy="guess"), dict(source_claim_ids=[]),
                        dict(source_claim_ids=[unrelated_claim])):
            with self.assertRaises(ValueError):
                self.chronicle.transfer(**dict(arguments, **changes))
        partial_source = self.observe("partial", "alpha", completeness="partial")
        partial_claim = self.claim(partial_source, 0, 5)
        with self.assertRaisesRegex(ValueError, "source must be complete"):
            self.chronicle.transfer(**self.arguments(partial_source, target, [partial_claim]))
        with self.assertRaisesRegex(ValueError, "hash"):
            self.chronicle.resolve(target, content_hash="stale")
        missing = self.observe("missing", None, completeness="unobserved")
        with self.assertRaisesRegex(ValueError, "no captured content"):
            self.chronicle.resolve(missing)

    def test_cross_agent_opt_in_remains_session_bounded(self):
        source = self.observe("source", "alpha")
        target = self.observe("target", "alpha", agent_id="child")
        supplied = self.claim(source, 0, 5)
        arguments = self.arguments(source, target, [supplied])
        with self.assertRaisesRegex(ValueError, "same scope"):
            self.chronicle.transfer(**arguments)
        evidence = self.chronicle.transfer(**dict(arguments, cross_agent=True))
        self.assertEqual([], self.chronicle.inspect(target)["passage_relationships"])
        self.assertEqual([evidence], self.chronicle.inspect(target, cross_agent=True)["passage_relationships"])
        foreign = self.observe("foreign", "alpha", session_id="other")
        with self.assertRaisesRegex(ValueError, "same scope"):
            self.chronicle.transfer(**self.arguments(source, foreign, [supplied], cross_agent=True))

    def test_listing_is_metadata_only_scoped_bounded_and_pageable(self):
        a = self.observe("a", "secret raw text")
        b = self.observe("b", "other raw text")
        child = self.observe("child", "child raw text", agent_id="child")
        self.observe("other", "unrelated", session_id="other")
        page = self.chronicle.list_observations("fixture", "session", limit=1)
        self.assertEqual([b], [item["observation_id"] for item in page["observations"]])
        self.assertEqual(b, page["next_before_id"])
        next_page = self.chronicle.list_observations("fixture", "session", limit=1,
                                                   before_id=page["next_before_id"])
        self.assertEqual([a], [item["observation_id"] for item in next_page["observations"]])
        self.assertIsNone(next_page["next_before_id"])
        all_agents = self.chronicle.list_observations("fixture", "session", cross_agent=True)
        self.assertEqual([child, b, a], [item["observation_id"] for item in all_agents["observations"]])
        self.assertNotIn("raw text", json.dumps(all_agents))
        for limit in (0, 1001, True):
            with self.assertRaises(ValueError):
                self.chronicle.list_observations("fixture", "session", limit=limit)
        with self.assertRaisesRegex(ValueError, "outside scope"):
            self.chronicle.list_observations("fixture", "session", before_id=child)
        self.now += 11
        self.assertFalse(self.chronicle.list_observations("fixture", "session")["observations"][0]["content_available"])

    def test_json_bridge_exposes_resolution_listing_and_durable_transfer(self):
        source = self.observe("source", "alpha")
        target = self.observe("target", "alpha")
        supplied = self.claim(source, 0, 5)
        evidence = self.chronicle.transfer(**self.arguments(source, target, [supplied]))
        command = [sys.executable, "-m", "textprov.chronicle", "--db", str(self.path)]
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]))
        for request in (dict(operation="resolve", observation_id=target),
                        dict(operation="list_observations", provider="fixture", session_id="session"),
                        dict(operation="transfer", **self.arguments(source, target, [supplied]))):
            completed = subprocess.run(command, input=json.dumps(request), capture_output=True,
                                       text=True, env=env, timeout=15)
            self.assertEqual(0, completed.returncode, completed.stderr)
            result = json.loads(completed.stdout)["result"]
            if request["operation"] == "transfer":
                self.assertEqual(evidence, result)

    def test_chronicle_export_requires_explicit_multivoice_mapping_and_preserves_ivs(self):
        from textprov.export import restore

        text = "辻\U000e0100 Alpha ? Beta\r\n"
        observation = self.observe("export", text)
        self.claim(observation, 0, 8)
        self.claim(observation, 11, 15, "b")
        mappings = [dict(voice_context="document", voice_id="a", state="human"),
                    dict(voice_context="document", voice_id="b", state="ai")]
        arguments = dict(observation_id=observation,
                         content_hash=self.chronicle.inspect(observation)["content_hash"],
                         voice_states=mappings, allow_lossy=True)
        report = self.chronicle.export(**arguments)
        self.assertEqual(text.encode("utf-8"), restore(report).encode("utf-8"))
        self.assertIn("辻\U000e0100 ", report["text"])
        self.assertIn(" ? ", report["text"])
        self.assertIn("A\U000e0100", report["text"])
        self.assertIn("B\U000e0101", report["text"])
        with self.assertRaisesRegex(ValueError, "missing explicit"):
            self.chronicle.export(**dict(arguments, voice_states=mappings[:1]))
        with self.assertRaisesRegex(ValueError, "allow_lossy"):
            self.chronicle.export(**dict(arguments, allow_lossy=False))
        with self.assertRaisesRegex(ValueError, "hash"):
            self.chronicle.export(**dict(arguments, content_hash="stale"))
        self.now += 11
        with self.assertRaisesRegex(ValueError, "unavailable"):
            self.chronicle.export(**arguments)

    def test_chronicle_export_refuses_conflicting_claims_and_detects_corrupt_cache(self):
        observation = self.observe("export", "hello")
        self.claim(observation, 0, 5)
        arguments = dict(observation_id=observation,
                         content_hash=self.chronicle.inspect(observation)["content_hash"],
                         voice_states=[dict(voice_context="document", voice_id="a", state="ai")],
                         allow_lossy=True)
        self.chronicle.db.execute("UPDATE cache SET text = 'other' WHERE observation_id = ?",
                                  (observation,))
        with self.assertRaisesRegex(ValueError, "integrity"):
            self.chronicle.export(**arguments)
        self.chronicle.db.execute("UPDATE cache SET text = 'hello' WHERE observation_id = ?",
                                  (observation,))
        self.claim(observation, 1, 4, "b")
        with self.assertRaisesRegex(ValueError, "conflicting overlapping"):
            self.chronicle.export(**arguments)


if __name__ == "__main__":
    unittest.main()
