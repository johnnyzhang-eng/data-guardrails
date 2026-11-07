"""L4: keep valid JSON lines and record rejected physical line numbers.

This is a parsing guard, not order-schema validation. The static rule in
semgrep/ catches one common way of accidentally removing this guard.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_lines(text: str) -> tuple[list[object], list[int]]:
    """Skip blank lines; retain valid JSON values and 1-based bad line numbers."""
    values: list[object] = []
    rejected: list[int] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            values.append(json.loads(line))
        except json.JSONDecodeError:
            rejected.append(number)
    return values, rejected


# Literal expected answers are deliberately independent of the parser.
SELFTEST_CASES = [
    ("two orders", '{"order_id": 1}\n{"order_id": 2}',
     ([{"order_id": 1}, {"order_id": 2}], [])),
    ("bad middle line", '{"order_id": 1}\nbroken\n{"order_id": 2}',
     ([{"order_id": 1}, {"order_id": 2}], [2])),
    ("blank lines keep numbering", '\n{"order_id": 1}\n\nbroken\n',
     ([{"order_id": 1}], [4])),
    ("all bad", '{\n}', ([], [1, 2])),
    ("empty input", '', ([], [])),
]


def run_selftest() -> int:
    failed = 0
    for label, text, expected in SELFTEST_CASES:
        actual = parse_lines(text)
        if actual != expected:
            failed += 1
            print(f"FAIL {label}: expected {expected!r}, got {actual!r}")
    if failed:
        print(f"L4 JSON batch selftest: {failed} failed")
        return 1
    print(f"L4 JSON batch selftest: {len(SELFTEST_CASES)} passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--selftest", action="store_true")
    group.add_argument("--file", type=Path, help="Read a local UTF-8 JSON-lines file")
    args = parser.parse_args()
    if args.selftest:
        return run_selftest()
    values, rejected = parse_lines(args.file.read_text(encoding="utf-8"))
    print(json.dumps({"values": values, "rejected_lines": rejected}, indent=2))
    return int(bool(rejected))


if __name__ == "__main__":
    raise SystemExit(main())
