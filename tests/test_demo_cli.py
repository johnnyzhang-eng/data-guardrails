import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def run(*arguments):
    return subprocess.run([sys.executable, *arguments], cwd=ROOT,
                          capture_output=True, text=True, check=False)


def test_seeded_demo_and_read_only_checks(tmp_path):
    database = tmp_path / "delivery.sqlite3"
    assert run("examples/generate_data.py", "--db", str(database)).returncode == 0
    quality = run("-m", "checks.data_quality", "--db", str(database),
                  "--as-of", "2025-01-12T00:00:00+00:00", "--day", "2025-01-07")
    assert quality.returncode == 1, quality.stderr
    assert all(not row["passed"] for row in json.loads(quality.stdout).values())
    report = run("-m", "checks.result_integrity", "--db", str(database), "--report", "examples/report.json")
    assert report.returncode == 0, report.stderr
    assert json.loads(report.stdout)["recomputed"] == {
        "order_rows": 16, "known_amount_rows": 16, "amount_sum": 697}
    absent = tmp_path / "absent.sqlite3"
    bad = run("-m", "checks.result_integrity", "--db", str(absent), "--report", "examples/report.json")
    assert bad.returncode == 2
    assert not absent.exists()


@pytest.mark.parametrize("module,flag,path,code,token", [
    ("checks.claim_lint", "--claim", "examples/rate_claim.json", 1, "UNSUPPORTED_RATE_DROP"),
    ("checks.json_batch", "--file", "examples/orders.jsonl", 1, "rejected_lines"),
    ("checks.decision_gate", "--record", "examples/decision.json", 0, "REVIEW_READY"),
])
def test_public_examples(module, flag, path, code, token):
    result = run("-m", module, flag, path)
    assert result.returncode == code, result.stderr
    assert token in result.stdout
