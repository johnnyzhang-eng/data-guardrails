"""L1: inspect raw SQLite orders; a failing check exits with status 1."""
import argparse
from datetime import date, datetime, timedelta
import json
from pathlib import Path
import sqlite3


def check_quality(connection, *, as_of: str, day: str) -> dict:
    """Demo policies: <=48h age, 50%-150% of prior 3 days, no bad keys/NULLs.

    The row-count baseline includes calendar days with zero rows. These are
    teaching thresholds, not universal service objectives.
    """
    now = datetime.fromisoformat(as_of)
    if now.tzinfo is None:
        raise ValueError("as_of must include a timezone")
    target = date.fromisoformat(day)
    if target >= now.date():
        raise ValueError("row-count checks need a completed day")
    total, latest = connection.execute("SELECT COUNT(*), MAX(order_time) FROM orders").fetchone()
    try:
        stamp = datetime.fromisoformat(latest) if latest else None
        age = (now - stamp).total_seconds() / 3600 if stamp else None
    except (ValueError, TypeError):
        age = None
    daily = dict(connection.execute("SELECT date(order_time), COUNT(*) FROM orders GROUP BY date(order_time)"))
    baseline = sum(daily.get(str(target - timedelta(days=i)), 0) for i in (1, 2, 3)) / 3
    current = daily.get(target.isoformat(), 0)
    ratio = current / baseline if baseline else None
    distinct_ids, known_ids, known_amounts = connection.execute(
        "SELECT COUNT(DISTINCT order_id), COUNT(order_id), COUNT(amount) FROM orders").fetchone()
    null_rate = (total - known_amounts) / total if total else None
    missing_merchants = connection.execute("""SELECT COUNT(*) FROM orders o
        LEFT JOIN merchants m ON o.merchant_id = m.merchant_id WHERE m.merchant_id IS NULL""").fetchone()[0]
    missing_users = connection.execute("""SELECT COUNT(*) FROM orders o
        LEFT JOIN users u ON o.user_id = u.user_id WHERE u.user_id IS NULL""").fetchone()[0]
    return {
        "freshness": {"passed": total > 0 and age is not None and 0 <= age <= 48, "age_hours": age},
        "row_count": {"passed": ratio is not None and 0.5 <= ratio <= 1.5,
                      "rows": current, "baseline_rows": baseline, "ratio": ratio},
        "unique_order_id": {"passed": total > 0 and distinct_ids == total,
                            "duplicate_excess": known_ids - distinct_ids, "missing_ids": total - known_ids},
        "amount_null_rate": {"passed": total > 0 and null_rate == 0, "rate": null_rate},
        "foreign_keys": {"passed": total > 0 and missing_merchants + missing_users == 0,
                         "missing_merchants": missing_merchants, "missing_users": missing_users},
    }


def run_selftest() -> int:
    from examples.generate_data import AS_OF, CHECK_DAY, populate
    with sqlite3.connect(":memory:") as connection:
        populate(connection)
        result = check_quality(connection, as_of=AS_OF, day=CHECK_DAY)
    expected = {"freshness": ("age_hours", 84), "row_count": ("rows", 4),
                "unique_order_id": ("duplicate_excess", 1),
                "amount_null_rate": ("rate", 1 / 145), "foreign_keys": ("missing_merchants", 1)}
    failures = [key for key, (metric, value) in expected.items()
                if result[key]["passed"] or result[key][metric] != value]
    print(f"L1 selftest: {len(expected) - len(failures)}/{len(expected)} known answers passed")
    return int(bool(failures))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--db", type=Path)
    parser.add_argument("--as-of")
    parser.add_argument("--day")
    args = parser.parse_args()
    if args.selftest:
        return run_selftest()
    if not all((args.db, args.as_of, args.day)):
        parser.error("provide --db, --as-of and --day")
    try:
        with sqlite3.connect(args.db.resolve().as_uri() + "?mode=ro", uri=True) as connection:
            result = check_quality(connection, as_of=args.as_of, day=args.day)
    except (ValueError, sqlite3.Error) as error:
        parser.exit(2, f"Invalid input: {error}\n")
    print(json.dumps(result, indent=2))
    return int(any(not row["passed"] for row in result.values()))


if __name__ == "__main__":
    raise SystemExit(main())
