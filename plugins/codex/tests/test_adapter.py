"""Sanitized hook fixtures and process tests; these do not run a Codex trial."""

import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
REPO = PLUGIN.parents[1]
spec = importlib.util.spec_from_file_location("codex_adapter", PLUGIN / "textprov_codex.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)
from textprov.chronicle import Chronicle

FIXTURES = json.loads((Path(__file__).parent / "fixtures" / "hooks.json").read_text())


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.data = Path(self.temp.name) / "plugin data"
        self.project = str(Path(self.temp.name) / "project α")
        self.session = "fixture-session"
        self.env = dict(os.environ, PLUGIN_DATA=str(self.data), TEXTPROV_PYTHON=sys.executable,
                        PYTHONPATH=str(REPO / "python"))

    def payload(self, name, **changes):
        result = copy.deepcopy(FIXTURES[name])
        result.update(cwd=self.project)
        result.update(changes)
        return result

    def run_hook(self, payload, expected=0):
        raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
        result = subprocess.run([str(PLUGIN / "bin" / "textprov"), "hook"], input=raw,
                                text=True, capture_output=True, env=self.env)
        self.assertEqual(result.returncode, expected, result.stderr)
        self.assertEqual(result.stdout, "{}\n")
        return result

    def cli(self, command, *arguments, session=True, expected=0, project=None, request=None):
        argv = [str(PLUGIN / "bin" / "textprov"), command, "--project", project or self.project]
        if session:
            argv.extend(["--session", self.session])
        result = subprocess.run(argv + list(arguments), input=None if request is None else json.dumps(request),
                                text=True, capture_output=True, env=self.env)
        self.assertEqual(result.returncode, expected, result.stderr)
        return json.loads(result.stdout)["result"] if expected == 0 else result

    def observations(self, **options):
        state = adapter.State(self.data, self.project, self.session)
        with Chronicle(state.db_path) as chronicle:
            return chronicle.list_observations("codex", self.session, **options)["observations"]

    def test_packaged_hooks_use_documented_entries_and_wrapper(self):
        manifest = json.loads((PLUGIN / "plugin.json").read_text())
        self.assertEqual(manifest["extensions"]["com.openai"]["hooks"], "./hooks/hooks.json")
        hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())["hooks"]
        self.assertEqual(set(hooks), adapter.EVENTS)
        for groups in hooks.values():
            for group in groups:
                command = group["hooks"][0]["command"]
                self.assertEqual(command, '"${PLUGIN_ROOT}/bin/textprov" hook')
        self.assertTrue(os.access(PLUGIN / "bin" / "textprov", os.X_OK))

    def test_capture_preserves_identity_unicode_and_visibility_without_claims(self):
        for name in ("prompt", "pre", "post", "stop", "subagent"):
            self.run_hook(self.payload(name))
        rows = self.observations(cross_agent=True)
        self.assertEqual(len(rows), 8)
        prompt = next(row for row in rows if row["event_kind"] == "submission")
        raw = FIXTURES["prompt"]["prompt"]
        self.assertEqual(prompt["content_hash"], hashlib.sha256(raw.encode()).hexdigest())
        self.assertEqual(prompt["scalar_length"], len(raw))
        self.assertEqual(prompt["host_ids"], {"turn": "turn-1"})
        self.assertIsNone(prompt["capture_sequence"])
        self.assertEqual(prompt["visibility"], "structured")
        tool = next(row for row in rows if row["event_kind"] == "tool_result")
        self.assertEqual(tool["visibility"], "model")
        self.assertEqual(tool["completeness"], "partial")
        info = self.cli("inspect", tool["observation_id"])
        self.assertTrue(any(j["kind"] == "tool_call" for j in info["event_relationships"]))
        self.assertEqual(info["claims"], [])
        status = self.cli("status", session=False)
        self.assertEqual(status["chronicle"]["claim_count"], 0)
        self.assertEqual(status["chronicle"]["observation_count"], 8)
        self.assertEqual(status["observed_sessions"], [self.session])
        self.assertTrue(status["limitations"])

    def test_duplicate_delivery_is_idempotent_and_equal_text_different_calls_stays_separate(self):
        first = self.payload("pre")
        self.run_hook(first)
        ids = {row["observation_id"] for row in self.observations()}
        self.run_hook(first)
        self.assertEqual(ids, {row["observation_id"] for row in self.observations()})
        self.run_hook(self.payload("pre", tool_use_id="call-2"))
        self.assertEqual(len(self.observations()), 4)
        result = self.cli("status")
        self.assertIsNone(result["session"]["max_capture_sequence"])

    def test_changed_native_identity_reports_conflict_without_payload_leak(self):
        self.run_hook(self.payload("prompt"))
        secret = "PRIVATE PAYLOAD MUST NOT APPEAR IN DIAGNOSTICS"
        result = self.run_hook(self.payload("prompt", prompt=secret), expected=1)
        self.assertNotIn(secret, result.stderr)
        status = self.cli("status")
        self.assertEqual(status["diagnostics"]["counts"]["conflicting_native_identity"], 1)
        self.assertNotIn(secret, json.dumps(status))
        self.assertEqual(len(self.observations()), 1)

    def test_missing_ids_are_gaps_never_text_deduplication(self):
        for name, field in (("prompt", "turn_id"), ("pre", "tool_use_id"), ("subagent", "agent_id")):
            value = self.payload(name)
            del value[field]
            self.run_hook(value)
        status = self.cli("status")
        self.assertEqual(status["chronicle"]["observation_count"], 0)
        self.assertEqual(status["diagnostics"]["counts"]["missing_native_identity"], 3)

    def test_missing_output_is_unobserved_but_empty_and_json_null_are_observed(self):
        missing = self.payload("post")
        del missing["tool_response"]
        self.run_hook(missing)
        self.run_hook(self.payload("post", tool_use_id="empty", tool_response=""))
        self.run_hook(self.payload("post", tool_use_id="null", tool_response=None))
        self.run_hook(self.payload("stop", last_assistant_message=None))
        rows = self.observations()
        by_call = {row["host_ids"].get("tool_call"): row for row in rows
                   if row["event_kind"] in {"tool_result", "assistant_message"}}
        self.assertEqual(by_call["call-1"]["completeness"], "unobserved")
        self.assertIsNone(by_call["call-1"]["content_hash"])
        self.assertEqual(by_call["empty"]["scalar_length"], 0)
        self.assertEqual(by_call["null"]["content_hash"], hashlib.sha256(b"null").hexdigest())
        self.assertEqual(by_call[None]["completeness"], "unobserved")
        self.assertEqual(self.cli("status")["diagnostics"]["counts"]["missing_content"], 2)

    def test_json_string_tool_input_keeps_original_and_extracts_documented_command(self):
        command = "cat <<'EOF'\ncafé\n辻󠄀\nEOF"
        raw = '  { "command" : ' + json.dumps(command, ensure_ascii=False) + ' } '
        self.run_hook(self.payload("pre", tool_input=raw, tool_name="apply_patch"))
        rows = self.observations()
        self.assertEqual(len(rows), 2)
        hashes = {row["attributes"]["payload_field"]: row["content_hash"] for row in rows}
        self.assertEqual(hashes["tool_input"], hashlib.sha256(raw.encode()).hexdigest())
        self.assertEqual(hashes["tool_input.command"], hashlib.sha256(command.encode()).hexdigest())

    def test_structured_mcp_response_is_not_flattened_to_model_text(self):
        response = {"content": [{"type": "text", "text": "one"}, {"type": "image", "data": "AA=="}], "isError": False}
        self.run_hook(self.payload("post", tool_name="mcp__fixture__read", tool_response=response))
        row = self.observations()[0]
        self.assertEqual(row["visibility"], "structured")
        self.assertEqual(row["attributes"]["representation"], "json")
        self.assertEqual(row["content_hash"], hashlib.sha256(adapter.json_text(response).encode()).hexdigest())

    def test_post_input_preserves_executed_input_after_other_hook_rewrite(self):
        self.run_hook(self.payload("pre", tool_input={"command": "original command"}))
        self.run_hook(self.payload("post", tool_input={"command": "rewritten command"}))
        rows = self.observations()
        commands = {row["event_kind"]: row for row in rows if row["event_kind"].endswith("command")}
        self.assertEqual(commands["tool_command"]["content_hash"], hashlib.sha256(b"original command").hexdigest())
        self.assertEqual(commands["tool_executed_command"]["content_hash"], hashlib.sha256(b"rewritten command").hexdigest())

    def test_continued_stop_reports_unsupported_gap(self):
        for name in ("stop", "subagent"):
            self.run_hook(self.payload(name, stop_hook_active=True))
        status = self.cli("status")
        self.assertEqual(status["chronicle"]["observation_count"], 0)
        self.assertEqual(status["diagnostics"]["counts"]["continued_stop_without_message_identity"], 2)

    def test_malformed_payload_is_persisted_without_guessing_scope(self):
        self.run_hook('{"private":"do not retain",', expected=1)
        status = self.cli("status", session=False)
        self.assertEqual(status["unscoped_diagnostics"]["counts"]["malformed_payload"], 1)
        self.assertNotIn("do not retain", json.dumps(status))
        self.run_hook([], expected=1)
        self.run_hook(self.payload("prompt", prompt=123), expected=1)
        self.assertEqual(self.cli("status")["diagnostics"]["counts"]["capture_failed"], 1)

    def test_project_session_and_agent_scope_and_explicit_cross_agent(self):
        self.run_hook(self.payload("prompt"))
        self.run_hook(self.payload("prompt", agent_id="child", prompt="child passage"))
        self.run_hook(self.payload("prompt", session_id="other-session", prompt="other session"))
        self.run_hook(self.payload("prompt", cwd=self.project + "-other", prompt="other project"))
        rows = self.cli("list")["observations"]
        self.assertEqual(len(rows), 1)
        all_rows = self.cli("list", "--cross-agent")["observations"]
        self.assertEqual(len(all_rows), 2)
        child = next(row for row in all_rows if row["agent_id"] == "child")
        self.cli("inspect", child["observation_id"], expected=1)
        self.assertEqual(self.cli("inspect", child["observation_id"], "--agent", "child")["agent_id"], "child")
        self.assertEqual(self.cli("inspect", child["observation_id"], "--cross-agent")["agent_id"], "child")
        state = adapter.State(self.data, self.project)
        with Chronicle(state.db_path) as chronicle:
            other = chronicle.list_observations("codex", "other-session")["observations"][0]
        self.cli("inspect", other["observation_id"], "--cross-agent", expected=1)
        self.assertEqual(self.cli("status", session=False)["chronicle"]["observation_count"], 3)

    def test_cli_passes_matching_options_and_explicit_claims_to_core(self):
        self.run_hook(self.payload("prompt", prompt="quoted\r\npassage"))
        self.run_hook(self.payload("prompt", turn_id="turn-2", prompt="prefix quoted\npassage suffix"))
        rows = self.cli("list")["observations"]
        source = next(row for row in rows if row["host_ids"]["turn"] == "turn-1")
        target = next(row for row in rows if row["host_ids"]["turn"] == "turn-2")
        result = self.cli("match", source["observation_id"], target["observation_id"], "--policy", "line-endings-v1", "--min-chars", "3")
        self.assertEqual(len(result["candidates"]), 1)
        result_partial = self.cli("match", source["observation_id"], target["observation_id"], "--policy", "line-endings-v1", "--partial", "--min-chars", "3")
        self.assertTrue(result_partial["candidates"])
        claim = self.cli("claim", target["observation_id"], "--start", "7", "--end", "21",
                         "--content-hash", target["content_hash"], "--voice-context", "fixture", "--voice-id", "author",
                         "--voice-definition", "Supplied author", "--basis", "user_attestation", "--policy-version", "manual-v1",
                         "--support", source["observation_id"])
        self.assertEqual(self.cli("inspect", target["observation_id"])["claims"][0]["claim_id"], claim)

    def test_public_listing_pagination(self):
        for number in range(3):
            self.run_hook(self.payload("prompt", turn_id="turn-" + str(number)))
        first = self.cli("list", "--limit", "2")
        second = self.cli("list", "--limit", "2", "--before", first["next_before_id"])
        self.assertEqual(len(first["observations"]), 2)
        self.assertEqual(len(second["observations"]), 1)
        self.assertIsNone(second["next_before_id"])

    def test_query_forwards_transfer_resolve_export_with_scope(self):
        self.run_hook(self.payload("prompt", prompt="supplied text"))
        self.run_hook(self.payload("prompt", turn_id="turn-2", prompt="prefix supplied text suffix"))
        rows = self.cli("list")["observations"]
        source = next(row for row in rows if row["host_ids"]["turn"] == "turn-1")
        target = next(row for row in rows if row["host_ids"]["turn"] == "turn-2")
        claim = self.cli("claim", source["observation_id"], "--start", "0", "--end", "13",
                         "--content-hash", source["content_hash"], "--voice-context", "fixture", "--voice-id", "author",
                         "--voice-definition", "Supplied author", "--basis", "user_attestation", "--policy-version", "manual-v1")
        request = dict(operation="transfer", source_id=source["observation_id"], target_id=target["observation_id"],
                       candidate_index=0, source_claim_ids=[claim], source_hash=source["content_hash"], target_hash=target["content_hash"])
        evidence = self.cli("query", request=request)
        self.assertTrue(evidence["claim_ids"])
        resolution = self.cli("query", request=dict(operation="resolve", observation_id=target["observation_id"], content_hash=target["content_hash"]))
        self.assertEqual(resolution["ranges"][1]["voice_id"], "author")
        exported = self.cli("query", request=dict(operation="export", observation_id=target["observation_id"],
                            content_hash=target["content_hash"], allow_lossy=True,
                            voice_states=[dict(voice_context="fixture", voice_id="author", state="human")]))
        self.assertIn("text", exported)
        self.assertNotEqual(exported["text"], "prefix supplied text suffix")
        request["operation"] = "observe"
        self.cli("query", request=request, expected=1)
        self.run_hook(self.payload("prompt", session_id="other-session"))
        state = adapter.State(self.data, self.project)
        with Chronicle(state.db_path) as chronicle:
            other = chronicle.list_observations("codex", "other-session")["observations"][0]
        self.cli("query", "--cross-agent", request=dict(operation="resolve", observation_id=other["observation_id"]), expected=1)
        self.run_hook(self.payload("prompt", turn_id="child-turn", agent_id="child"))
        child = next(row for row in self.observations(cross_agent=True) if row["agent_id"] == "child")
        self.cli("query", request=dict(operation="resolve", observation_id=child["observation_id"]), expected=1)
        self.assertEqual(self.cli("query", request=dict(operation="resolve", observation_id=child["observation_id"], cross_agent=True))["observation_id"], child["observation_id"])

    def test_concurrent_first_open_and_retries_keep_unique_observations(self):
        payloads = [self.payload("pre", tool_use_id="parallel-" + str(number)) for number in range(8)]
        with ThreadPoolExecutor(max_workers=8) as executor:
            list(executor.map(self.run_hook, payloads + payloads))
        rows = self.observations()
        self.assertEqual(len(rows), 16)
        self.assertEqual(len({row["observation_id"] for row in rows}), 16)
        self.assertTrue(all(row["capture_sequence"] is None for row in rows))
        self.assertEqual(self.cli("status")["diagnostics"]["counts"], {})


if __name__ == "__main__":
    unittest.main()
