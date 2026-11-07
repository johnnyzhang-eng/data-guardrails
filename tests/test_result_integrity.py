import copy

import pytest

from checks.result_integrity import check_report, known_report, recompute, run_selftest, sample_connection


def test_known_answer_distinguishes_null_zero_and_status():
    with sample_connection() as connection:
        result = check_report(connection, known_report())
    assert result["passed"] is True
    assert result["recomputed"] == {"order_rows": 3, "known_amount_rows": 2, "amount_sum": 10}


def test_bad_total_is_rejected():
    report = known_report()
    report["metrics"]["amount_sum"] = 100
    with sample_connection() as connection:
        assert check_report(connection, report)["passed"] is False


def test_equivalent_iso_date_forms_cannot_produce_a_false_zero_match():
    report = known_report()
    report["scope"].update(start_day="20250101", end_day="20250102")
    with sample_connection() as connection:
        assert check_report(connection, report)["passed"] is True
        report["metrics"] = {"order_rows": 0, "known_amount_rows": 0, "amount_sum": 0}
        assert check_report(connection, report)["passed"] is False


def test_empty_scope_and_exclusive_end():
    with sample_connection() as connection:
        assert recompute(connection, start_day="2025-01-02", end_day="2025-01-03", status="delivered") == {
            "order_rows": 1, "known_amount_rows": 1, "amount_sum": 80}
        assert recompute(connection, start_day="2025-01-03", end_day="2025-01-04", status="delivered") == {
            "order_rows": 0, "known_amount_rows": 0, "amount_sum": 0}


@pytest.mark.parametrize("change", ["missing_metric", "boolean", "unknown_status", "bad_window", "missing_scope"])
def test_invalid_contracts_fail_instead_of_matching(change):
    report = copy.deepcopy(known_report())
    if change == "missing_metric":
        del report["metrics"]["known_amount_rows"]
    elif change == "boolean":
        report["metrics"]["order_rows"] = True
    elif change == "unknown_status":
        report["scope"]["status"] = "anything"
    elif change == "bad_window":
        report["scope"]["end_day"] = report["scope"]["start_day"]
    else:
        del report["scope"]
    with sample_connection() as connection, pytest.raises(ValueError):
        check_report(connection, report)


def test_selftest():
    assert run_selftest() == 0
