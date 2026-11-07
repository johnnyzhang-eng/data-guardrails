import sqlite3

import pytest

from checks.data_quality import check_quality, run_selftest
from examples.generate_data import AS_OF, CHECK_DAY, populate


@pytest.fixture
def database():
    connection = sqlite3.connect(":memory:")
    populate(connection)
    yield connection
    connection.close()


def inspect(connection, as_of=AS_OF, day=CHECK_DAY):
    return check_quality(connection, as_of=as_of, day=day)


def test_seeded_known_answers(database):
    result = inspect(database)
    assert {key: row["passed"] for key, row in result.items()} == {
        "freshness": False, "row_count": False, "unique_order_id": False,
        "amount_null_rate": False, "foreign_keys": False}
    assert result["freshness"]["age_hours"] == 84
    assert result["row_count"] == {"passed": False, "rows": 4, "baseline_rows": 20, "ratio": 0.2}
    assert result["unique_order_id"]["duplicate_excess"] == 1
    assert result["amount_null_rate"]["rate"] == 1 / 145
    assert result["foreign_keys"]["missing_merchants"] == 1


def test_regeneration_replaces_instead_of_appending(database):
    before = database.execute("SELECT * FROM orders ORDER BY rowid").fetchall()
    populate(database)
    assert database.execute("SELECT * FROM orders ORDER BY rowid").fetchall() == before


def test_repaired_input_can_pass(database):
    database.execute("DELETE FROM orders WHERE rowid = (SELECT MAX(rowid) FROM orders)")
    database.execute("UPDATE orders SET amount = 0 WHERE amount IS NULL")
    database.execute("UPDATE orders SET merchant_id = 1 WHERE merchant_id = 9999")
    result = inspect(database, as_of="2025-01-09T00:00:00+00:00", day="2025-01-06")
    assert all(row["passed"] for row in result.values())


def test_empty_orders_fail_all_checks(database):
    database.execute("DELETE FROM orders")
    assert all(not row["passed"] for row in inspect(database).values())


@pytest.mark.parametrize("stamp,expected", [
    ("2025-01-10T12:00:00+00:00", True),
    ("2025-01-10T12:00:01+00:00", False),
    ("2025-01-08T11:59:59+00:00", False),
])
def test_freshness_boundary_and_future_dates(database, stamp, expected):
    assert inspect(database, as_of=stamp)["freshness"]["passed"] is expected


def test_absent_calendar_days_are_in_the_baseline(database):
    database.execute("DELETE FROM orders WHERE date(order_time) IN ('2025-01-04', '2025-01-05')")
    assert inspect(database)["row_count"]["baseline_rows"] == 20 / 3


def test_equivalent_iso_date_forms_use_the_same_day(database):
    assert inspect(database, day="20250106") == inspect(database, day="2025-01-06")


def test_zero_baseline_has_no_ratio(database):
    database.execute("DELETE FROM orders WHERE date(order_time) < '2025-01-07'")
    assert inspect(database)["row_count"]["ratio"] is None
    assert inspect(database)["row_count"]["passed"] is False


def test_null_primary_and_reference_keys_are_bad(database):
    database.execute("UPDATE orders SET order_id = NULL, user_id = NULL WHERE rowid = 1")
    result = inspect(database)
    assert result["unique_order_id"]["missing_ids"] == 1
    assert result["foreign_keys"]["missing_users"] == 1


def test_selftest():
    assert run_selftest() == 0
