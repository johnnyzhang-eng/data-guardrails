"""Known positive and negative examples for the local Semgrep rule."""
import json


def drain_unguarded(text):
    out = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            # ruleid: unguarded-json-loads-in-loop
            out.append(json.loads(line))
    return out


def drain_guarded(text):
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            # ok: unguarded-json-loads-in-loop
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def parse_one(text):
    # ok: unguarded-json-loads-in-loop
    return json.loads(text)
