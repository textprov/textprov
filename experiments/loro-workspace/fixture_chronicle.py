"""Disposable test captures only; never searches for installed databases."""
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
from textprov import mark
from textprov.chronicle import Chronicle


def fixture(path, paged=True):
    now = time.time()
    clock = [now]
    ids = {}
    with Chronicle(path, clock=lambda: clock[0]) as c:
        def add(key, **changes):
            fields = dict(provider="claude", adapter="fixture", session_id="selected", delivery_key=key,
                          event_kind="submission", channel="user", visibility="stored", text="Same words")
            fields.update(changes)
            ids[key] = c.observe(**fields)
        add("human", text="Human " + mark("pasted AI"))
        add("same1")
        add("same2")
        add("answer", event_kind="assistant_message", channel="assistant", text="Partial answer", completeness="partial")
        add("missing", text=None, completeness="unobserved")
        add("tool", event_kind="tool_input", channel="tool", text="private tool")
        add("other-session", session_id="other")
        add("other-provider", provider="codex")
        add("other-agent", agent_id="worker")
        # Keep enough selected records to exercise the bridge's 100-row paging.
        for n in range(105 if paged else 0):
            add("page-" + str(n), text="page " + str(n))
        c.claim(observation_id=ids["human"], start=0, end=5,
                content_hash=c.inspect(ids["human"])["content_hash"],
                voice_context="fixture", voice_id="Voice1", voice_definition="Fixture human",
                basis="user_attestation", policy_version="fixture-v1", supporting_ids=[])
        # Leave expired cache material physically present in the SOURCE so the
        # test proves that lazy pruning touches only the disposable snapshot.
        clock[0] = now - 7200
        add("expired", text="Expired words")
    return ids


if __name__ == "__main__":
    print(json.dumps(fixture(sys.argv[1], paged="--small" not in sys.argv[2:])))
