#!/usr/bin/env python3
"""Codex hook translation and CLI; attribution and persistence belong to core."""

import argparse
from collections import Counter
from contextlib import contextmanager
import fcntl
import hashlib
from importlib import metadata
import inspect
import json
import os
from pathlib import Path
import sys
import time

from document_tools import rewrite_tool_input

VERSION = "0.1.3"
ADAPTER = "codex-hooks-v1"
PROVIDER = "codex"
MAX_INPUT_BYTES = 4 * 1024 * 1024
EVENTS = {"UserPromptSubmit", "PreToolUse", "PostToolUse", "Stop", "SubagentStop"}
LIMITATIONS = [
    "Hook fixtures are verified; installed-host behavior still needs a separate trial.",
    "Hosted tools, reasoning, intermediate assistant messages and specialized paths bypassing hooks are unobserved.",
    "Transcript files are not read: their format is not a stable hook interface.",
    "Continued Stop/SubagentStop events lack a documented per-message ID and are skipped.",
    "A conflicting payload under the same native event identity is reported, never text-deduplicated.",
    "Tool inputs are structured observations; tool results are partial because host output can be truncated.",
    "Hook order is not causal order; capture_sequence is omitted.",
    "Codex hooks cannot rewrite displayed chat; copy-chat exports retained messages with human/AI marks.",
    "Native apply_patch Markdown prose is marked before execution; shell writes and bypassed tool paths require the marking helper.",
    "Marking is the configured human/AI policy, not authorship verification; existing marks take precedence.",
]


def json_text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def required_string(value, label):
    if not isinstance(value, str) or not value:
        raise ValueError(label + " must be a nonempty string")
    return value


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class State:
    """Adapter diagnostics are separate from the shared Chronicle database."""

    def __init__(self, data, project=None, session=None):
        if not data:
            raise ValueError("PLUGIN_DATA is required (or pass --data for explicit CLI use)")
        self.root = Path(data).expanduser().resolve()
        self.project = None
        self.session = session
        if project is not None:
            required_string(project, "cwd/project")
            if not Path(project).is_absolute():
                raise ValueError("cwd/project must be an absolute path")
            self.project = str(Path(project).resolve())
        self.directory = self.root if self.project is None else self.root / "projects" / digest(self.project)
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.diagnostics = self.directory / "diagnostics.jsonl"
        if session is not None:
            required_string(session, "session_id")
            session_dir = self.directory / "sessions" / digest(session)
            session_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            self.diagnostics = session_dir / "diagnostics.jsonl"

    @property
    def db_path(self):
        if self.project is None:
            raise ValueError("a project is required for Chronicle access")
        return self.directory / "chronicle.sqlite"

    @contextmanager
    def lock(self):
        # Coordinate processes, including first database initialization. No
        # read/max/write sequence numbers are manufactured by the adapter.
        with (self.directory / "adapter.lock").open("a") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def diagnostic(self, code, *, event=None, field=None):
        record = dict(time=time.time(), code=code)
        if event in EVENTS:
            record["event"] = event
        if field is not None:
            record["field"] = field
        # Deliberately omit payloads and exception messages: diagnostics outlive
        # the core's raw-content retention policy.
        with self.diagnostics.open("a") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            handle.write(json_text(record) + "\n")
            handle.flush()

    def diagnostic_summary(self):
        counts = Counter()
        recent = []
        paths = [self.diagnostics]
        if self.session is None and self.project is not None:
            paths.extend(sorted((self.directory / "sessions").glob("*/diagnostics.jsonl")))
        for path in paths:
            if not path.exists():
                continue
            with path.open() as handle:
                fcntl.flock(handle, fcntl.LOCK_SH)
                for line in handle:
                    try:
                        item = json.loads(line)
                    except ValueError:
                        counts["diagnostic_log_invalid"] += 1
                        continue
                    counts[item["code"]] += 1
                    recent.append(item)
        return dict(counts=dict(counts), recent=sorted(recent, key=lambda x: x["time"])[-20:])

    def record_session(self):
        """Keep discovery metadata outside core; no conversation content."""
        path = self.diagnostics.parent / "session.json"
        if not path.exists():
            temporary = path.with_suffix(".tmp")
            temporary.write_text(json_text({"session_id": self.session}) + "\n")
            temporary.replace(path)

    def sessions(self):
        return [json.loads(path.read_text())["session_id"]
                for path in sorted((self.directory / "sessions").glob("*/session.json"))]


def core_class():
    try:
        from textprov.chronicle import Chronicle
    except ImportError as error:
        raise ValueError("TextProv core with Chronicle APIs is required; install the local Python package into TEXTPROV_PYTHON") from error
    if not all(hasattr(Chronicle, name) for name in ("observe", "session", "status", "inspect", "match", "claim",
                                                   "list_observations", "transfer", "resolve", "export", "export_chat")):
        raise ValueError("TextProv core lacks required Chronicle APIs")
    if not {"scope", "plain"}.issubset(inspect.signature(Chronicle.export_chat).parameters):
        raise ValueError("TextProv core 0.1.7 or newer with chat marking scopes is required")
    return Chronicle


def core_version():
    try:
        import textprov
        return textprov.__version__
    except (ImportError, AttributeError):
        try:
            return metadata.version("textprov")
        except metadata.PackageNotFoundError:
            return "unavailable"


def event_records(payload, state):
    """Translate documented fields, keeping identities separate from content."""
    event = required_string(payload.get("hook_event_name"), "hook_event_name")
    if event not in EVENTS:
        state.diagnostic("unsupported_event")
        return []
    turn = payload.get("turn_id")
    if not isinstance(turn, str) or not turn:
        state.diagnostic("missing_native_identity", event=event, field="turn_id")
        return []
    host_ids = {"turn": turn}
    agent = payload.get("agent_id")
    if agent is not None:
        required_string(agent, "agent_id")
        host_ids["agent"] = agent
    attributes = {"hook_event": event}
    for name in ("model", "permission_mode", "agent_type"):
        if isinstance(payload.get(name), str):
            attributes[name] = payload[name]
    common = dict(provider=PROVIDER, adapter=ADAPTER, session_id=state.session,
                  agent_id=agent, host_ids=host_ids)
    records = []

    def add(identity, field, kind, channel, visibility, *, value=None, present=True,
            completeness="complete", representation="text", extra=None):
        facts = dict(attributes, payload_field=field, representation=representation)
        if extra:
            facts.update(extra)
        if not present:
            text = None
            completeness = "unobserved"
            state.diagnostic("missing_content", event=event, field=field)
        elif isinstance(value, str) and representation == "text":
            text = value
        else:
            text = json_text(value)
            facts["representation"] = "json"
        records.append(dict(common, delivery_key=json_text([event, turn, identity, field]),
                            event_kind=kind, channel=channel, visibility=visibility,
                            text=text, completeness=completeness, attributes=facts))

    if event == "UserPromptSubmit":
        if "prompt" in payload and not isinstance(payload["prompt"], str):
            raise ValueError("prompt must be a string")
        add("submission", "prompt", "submission", "user", "structured",
            value=payload.get("prompt"), present="prompt" in payload)
    elif event in {"PreToolUse", "PostToolUse"}:
        call = payload.get("tool_use_id")
        if not isinstance(call, str) or not call:
            state.diagnostic("missing_native_identity", event=event, field="tool_use_id")
            return []
        tool = required_string(payload.get("tool_name"), "tool_name")
        host_ids["tool_call"] = call
        attributes["tool_name"] = tool
        value = payload.get("tool_input")
        add(call, "tool_input", "tool_input" if event == "PreToolUse" else "tool_executed_input",
            "assistant_tool", "structured", value=value, present="tool_input" in payload,
            representation="text" if isinstance(value, str) else "json")
        # A string-valued local tool_input can itself be JSON arguments.
        # Preserve it verbatim above; use a decoded *additional* command
        # observation only for tools whose field is documented by the host.
        decoded = value
        if isinstance(value, str):
            try:
                decoded = json.loads(value)
            except ValueError:
                decoded = None
        if tool in {"Bash", "apply_patch"} and isinstance(decoded, dict):
            command = decoded.get("command")
            if isinstance(command, str):
                add(call, "tool_input.command", "tool_command" if event == "PreToolUse" else "tool_executed_command",
                    "assistant_tool", "structured", value=command)
        if event == "PostToolUse":
            value = payload.get("tool_response")
            add(call, "tool_response", "tool_result", "tool", "structured" if tool.startswith("mcp__") else "model",
                value=value, present="tool_response" in payload,
                completeness="partial", representation="text" if isinstance(value, str) else "json")
    else:
        if event == "SubagentStop" and agent is None:
            state.diagnostic("missing_native_identity", event=event, field="agent_id")
            return []
        active = payload.get("stop_hook_active")
        if type(active) is not bool:
            raise ValueError("stop_hook_active must be a boolean")
        if active:
            state.diagnostic("continued_stop_without_message_identity", event=event)
            return []
        value = payload.get("last_assistant_message")
        if value is not None and not isinstance(value, str):
            raise ValueError("last_assistant_message must be a string or null")
        add(agent or "main", "last_assistant_message", "assistant_message", "assistant", "structured",
            value=value, present=value is not None,
            completeness="partial", extra={"stop_hook_active": active})
    return records


def read_payload():
    raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("hook payload exceeds 4 MiB input limit")
    payload = json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError("non-finite JSON")))
    if not isinstance(payload, dict):
        raise ValueError("hook payload must be an object")
    return payload


def capture(args):
    # An unscoped journal keeps malformed-input failures visible without
    # guessing a project or session from the process's current directory.
    state = State(args.data)
    try:
        payload = read_payload()
        project = required_string(payload.get("cwd"), "cwd")
        session = required_string(payload.get("session_id"), "session_id")
        state = State(args.data, project, session)
        with state.lock():
            state.record_session()
            records = event_records(payload, state)
            if records:
                with core_class()(state.db_path) as chronicle:
                    for record in records:
                        chronicle.observe(**record)
    except Exception as error:
        code = "capture_failed"
        if isinstance(error, json.JSONDecodeError):
            code = "malformed_payload"
        elif isinstance(error, ValueError) and str(error) == "delivery key reused with different observation":
            code = "conflicting_native_identity"
        state.diagnostic(code)
        # Raw errors can include observed content. Never persist or print them.
        print(json_text({"error": "TextProv capture failed", "type": type(error).__name__,
                         "diagnostics": str(state.diagnostics)}), file=sys.stderr)
        print("{}")
        return 1
    response = {}
    if payload.get("hook_event_name") == "PreToolUse":
        try:
            rewrite_payload = payload
            if payload.get("tool_name") == "apply_patch" and isinstance(payload.get("tool_input"), str):
                rewrite_payload = dict(payload, tool_input=json.loads(payload["tool_input"]))
            updated = rewrite_tool_input(rewrite_payload)
            if updated is not None:
                response = {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                            "permissionDecision": "allow", "updatedInput": updated}}
        except (ValueError, OSError, UnicodeError):
            state.diagnostic("document_marking_failed", event="PreToolUse")
            response = {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "TextProv could not safely preserve document marks. Read the exact file and use a supported Markdown patch or the marking helper."}}
    print(json_text(response))
    return 0


def operate(args):
    state = State(args.data, args.project, args.session)
    with state.lock():
        with core_class()(state.db_path) as chronicle:
            if args.command == "status":
                result = dict(plugin_version=VERSION, core_version=core_version(), provider=PROVIDER,
                              project=state.project, database=str(state.db_path),
                              chronicle=chronicle.status(), diagnostics=state.diagnostic_summary(),
                              observed_sessions=state.sessions(),
                              unscoped_diagnostics=State(args.data).diagnostic_summary(), limitations=LIMITATIONS)
                result["marking"] = dict(policy="chat-speaker-v2", default_scope="prose",
                                         scopes=["prose", "all", "off"], existing_marks="preserved",
                                         chat_display=False, chat_copy_command="copy-chat",
                                         plain_copy_option="--plain",
                                         documents="native apply_patch Markdown prose")
                if args.session:
                    result["session"] = chronicle.session(PROVIDER, args.session)
            elif args.command == "list":
                if not hasattr(chronicle, "list_observations"):
                    raise ValueError("this operation requires core list_observations API")
                result = chronicle.list_observations(PROVIDER, args.session, agent_id=args.agent,
                                                     cross_agent=args.cross_agent, limit=args.limit,
                                                     before_id=args.before)
            elif args.command == "query":
                request = read_payload()
                operation = request.pop("operation", None)
                if operation not in {"transfer", "resolve", "export"}:
                    raise ValueError("query operation must be transfer, resolve or export")
                cross_agent = request.pop("cross_agent", False)
                if type(cross_agent) is not bool:
                    raise ValueError("cross_agent must be a boolean")
                cross_agent = args.cross_agent or cross_agent
                if operation == "transfer":
                    identifiers = [request["source_id"], request["target_id"]]
                    request["cross_agent"] = cross_agent
                else:
                    identifiers = [request["observation_id"]]
                check_scope(chronicle, identifiers, args.session, args.agent, cross_agent)
                result = getattr(chronicle, operation)(**request)
            else:
                # UUID lookup doesn't imply permission to switch sessions. CLI
                # scopes every selected observation before calling shared APIs.
                identifiers = [args.observation] if args.command in {"inspect", "claim", "copy-chat"} else [args.source, args.target]
                if args.command == "claim":
                    identifiers.extend(args.support)
                check_scope(chronicle, identifiers, args.session, args.agent, args.cross_agent)
                if args.command == "inspect":
                    result = chronicle.inspect(args.observation, cross_agent=args.cross_agent)
                elif args.command == "copy-chat":
                    info = chronicle.inspect(args.observation)
                    result = chronicle.export_chat(args.observation, content_hash=info["content_hash"],
                                                   scope=args.marks, plain=args.plain)
                elif args.command == "match":
                    result = chronicle.match(args.source, args.target, cross_agent=args.cross_agent,
                                             policy=args.policy, partial=args.partial, min_match_chars=args.min_chars)
                else:
                    result = chronicle.claim(observation_id=args.observation, start=args.start, end=args.end,
                                             content_hash=args.content_hash, voice_context=args.voice_context,
                                             voice_id=args.voice_id, voice_definition=args.voice_definition,
                                             basis=args.basis, policy_version=args.policy_version,
                                             supporting_ids=args.support, cross_agent=args.cross_agent)
    if args.command == "copy-chat":
        # No extra newline: stdout is the exact selected copy representation.
        sys.stdout.write(result["text"])
    else:
        print(json_text({"result": result}))
    return 0


def check_scope(chronicle, identifiers, session, agent, cross_agent):
    for identifier in identifiers:
        info = chronicle.inspect(identifier)
        if info["provider"] != PROVIDER or info["session_id"] != session:
            raise ValueError("observation is outside the selected provider/session")
        if not cross_agent and info["agent_id"] != agent:
            raise ValueError("observation is outside the selected agent; use --agent or --cross-agent")


def main(argv=None):
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default=os.environ.get("PLUGIN_DATA"), help="plugin data directory (default: PLUGIN_DATA)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("hook", help="read one Codex hook JSON object from stdin")
    commands.add_parser("mark", help="read a shared chat/document marking or strip-marks JSON request on stdin")
    for name in ("status", "list", "inspect", "match", "claim", "query", "copy-chat"):
        cmd = commands.add_parser(name)
        cmd.add_argument("--project", required=True, help="absolute session cwd; namespaces the project database")
        cmd.add_argument("--session", required=name != "status")
        if name not in {"status"}:
            cmd.add_argument("--agent", default=None)
            cmd.add_argument("--cross-agent", action="store_true")
        if name == "list":
            cmd.add_argument("--limit", type=int, default=100)
            cmd.add_argument("--before", help="exclusive observation ID cursor from next_before_id")
        if name in {"inspect", "claim", "copy-chat"}:
            cmd.add_argument("observation")
        if name == "copy-chat":
            output = cmd.add_mutually_exclusive_group()
            output.add_argument("--marks", choices=("prose", "all", "off"), default="prose",
                                help="where to add marks (default: prose); existing marks survive")
            output.add_argument("--plain", action="store_true",
                                help="explicitly remove TextProv marks from the copied text")
        if name == "match":
            cmd.add_argument("source")
            cmd.add_argument("target")
            cmd.add_argument("--policy", default="exact-v1")
            cmd.add_argument("--partial", action="store_true")
            cmd.add_argument("--min-chars", type=int, default=16)
        if name == "claim":
            cmd.add_argument("--start", type=int, required=True)
            cmd.add_argument("--end", type=int, required=True)
            for field in ("content-hash", "voice-context", "voice-id", "voice-definition", "basis", "policy-version"):
                cmd.add_argument("--" + field, required=True)
            cmd.add_argument("--support", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        if args.command == "mark":
            from textprov.marking import main as marking_main
            return marking_main([])
        return capture(args) if args.command == "hook" else operate(args)
    except Exception as error:
        print(json_text({"error": str(error), "type": type(error).__name__}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
