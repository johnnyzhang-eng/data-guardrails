import pytest

from checks.claim_lint import KNOWN_CASES, assess_claim, case_input, run_selftest


@pytest.mark.parametrize("label,values,expected", KNOWN_CASES, ids=[case[0] for case in KNOWN_CASES])
def test_known_answers(label, values, expected):
    assert assess_claim(**case_input(values)) == expected


@pytest.mark.parametrize("field,value", [
    ("baseline_total", -1), ("current_total", True), ("current_delivered", 101),
    ("threshold_pp", 0), ("baseline_complete", "yes"),
])
def test_inconsistent_inputs_do_not_get_a_verdict(field, value):
    data = case_input((100, 90, 100, 80, True, True))
    data[field] = value
    with pytest.raises(ValueError):
        assess_claim(**data)


def test_changing_the_threshold_changes_the_same_claim():
    data = case_input((100, 90, 100, 85, True, True))
    assert assess_claim(**data, threshold_pp=6) == "UNSUPPORTED_RATE_DROP"


def test_selftest():
    assert run_selftest() == 0
