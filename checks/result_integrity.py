"""L2: compare a report with a scoped aggregation of raw orders."""
import argparse
from datetime import date
import json
from pathlib import Path
import sqlite3


def recompute(connection, *, start_day: str, end_day: str, status: str) -> dict:
    """Dates are UTC, start inclusive and end exclusive; duplicates are retained.

    A matching report can still describe bad raw data: L1 is a separate gate.
    COUNT(amount) makes the incomplete monetary denominator visible.
    """
    start, end = date.fromisoformat(start_day), date.fromisoformat(end_day)
    if start >= end:
        raise ValueError("start_day must precede end_day")
    if status not in ("delivered", "cancelled"):
        raise ValueError("unsupported order status")
    rows, known, amount = connection.execute("""SELECT COUNT(*), COUNT(amount), COALESCE(SUM(amount), 0)
        FROM orders WHERE date(order_time) >= ? AND date(order_time) < ? AND status = ?""",
        (start.isoformat(), end.isoformat(), status)).fetchone()
    return {"order_rows": rows, "known_amount_rows": known, "amount_sum": amount}


def check_report(connection, report: dict) -> dict:
    if not isinstance(report, dict) or set(report) != {"scope", "metrics"}:
        raise ValueError("report must contain scope and metrics")
    scope, metrics = report["scope"], report["metrics"]
    if not isinstance(scope, dict) or set(scope) != {"start_day", "end_day", "status"}:
        raise ValueError("scope needs start_day, end_day and status")
    if not all(isinstance(value, str) for value in scope.values()):
        raise ValueError("scope values must be strings")
    if not isinstance(metrics, dict) or set(metrics) != {"order_rows", "known_amount_rows", "amount_sum"}:
        raise ValueError("report metric names do not match the contract")
    if any(type(value) is not int or value < 0 for value in metrics.values()):
        raise ValueError("metrics must be nonnegative integers")
    actual = recompute(connection, **scope)
    return {"passed": actual == metrics, "reported": metrics, "recomputed": actual}


def sample_connection():
    connection = sqlite3.connect(":memory:")
    connection.execute("CREATE TABLE orders (order_time TEXT, amount INTEGER, status TEXT)")
    connection.executemany("INSERT INTO orders VALUES (?, ?, ?)", [
        ("2025-01-01T12:00:00+00:00", 10, "delivered"),
        ("2025-01-01T12:00:00+00:00", None, "delivered"),
        ("2025-01-01T12:00:00+00:00", 0, "delivered"),
        ("2025-01-01T12:00:00+00:00", 90, "cancelled"),
        ("2025-01-02T00:00:00+00:00", 80, "delivered")])
    return connection


def known_report() -> dict:
    return {"scope": {"start_day": "2025-01-01", "end_day": "2025-01-02", "status": "delivered"},
            "metrics": {"order_rows": 3, "known_amount_rows": 2, "amount_sum": 10}}


def run_selftest() -> int:
    report = known_report()
    with sample_connection() as connection:
        good = check_report(connection, report)["passed"]
        report["metrics"]["amount_sum"] = 100
        catches_bad = not check_report(connection, report)["passed"]
    failures = 2 - int(good) - int(catches_bad)
    print(f"L2 selftest: {2 - failures}/2 known answers passed")
    return int(bool(failures))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--db", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.selftest:
        return run_selftest()
    if not (args.db and args.report):
        parser.error("provide --db and --report")
    try:
        report = json.loads(args.report.read_text())
        with sqlite3.connect(args.db.resolve().as_uri() + "?mode=ro", uri=True) as connection:
            result = check_report(connection, report)
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.exit(2, f"Invalid input: {error}\n")
    print(json.dumps(result, indent=2))
    return int(not result["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
