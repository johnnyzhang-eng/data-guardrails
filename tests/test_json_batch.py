"""L4 known answers, observable batch behavior, and optional static-rule tests."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

from checks.json_batch import SELFTEST_CASES, parse_lines, run_selftest


@pytest.mark.parametrize("label,text,expected", SELFTEST_CASES,
                         ids=[case[0] for case in SELFTEST_CASES])
def test_known_answers(label, text, expected):
    assert parse_lines(text) == expected


def test_selftest():
    assert run_selftest() == 0


def test_unsafe_fixture_loses_later_orders_and_safe_fixture_keeps_them():
    root = Path(__file__).resolve().parents[1]
    path = root / "semgrep/tests/unguarded-json-loads-in-loop.py"
    spec = importlib.util.spec_from_file_location("batch_fixtures", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    text = '{"order_id": 1}\nbroken\n{"order_id": 2}'
    with pytest.raises(json.JSONDecodeError):
        module.drain_unguarded(text)
    assert module.drain_guarded(text) == [{"order_id": 1}, {"order_id": 2}]
    assert parse_lines(text) == ([{"order_id": 1}, {"order_id": 2}], [2])


def test_cli_rejects_bad_line_without_losing_good_rows(tmp_path):
    import sys

    path = tmp_path / "orders.jsonl"
    path.write_text('{"order_id": 1}\nbroken\n{"order_id": 2}\n', encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "-m", "checks.json_batch", "--file", str(path)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        check=False,
    )
    assert result.returncode == 1
    assert json.loads(result.stdout) == {
        "values": [{"order_id": 1}, {"order_id": 2}], "rejected_lines": [2],
    }


@pytest.mark.skipif(shutil.which("semgrep") is None, reason="Semgrep is not installed")
def test_semgrep_known_answers():
    env = dict(os.environ, SEMGREP_SEND_METRICS="off", SEMGREP_ENABLE_VERSION_CHECK="0")
    result = subprocess.run(
        ["semgrep", "--test", "--config", "semgrep/rules", "semgrep/tests"],
        cwd=Path(__file__).resolve().parents[1], env=env,
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
