import pytest

from checks.decision_gate import evaluate, known_cases, known_record, run_selftest


@pytest.mark.parametrize("label,record,expected", known_cases(), ids=[case[0] for case in known_cases()])
def test_known_answers(label, record, expected):
    assert evaluate(record)["verdict"] == expected


@pytest.mark.parametrize("value", [False, "true", 1, None])
def test_checked_fields_require_boolean_true(value):
    record = known_record()
    record["measurement_verified"] = value
    assert evaluate(record) == {"verdict": "HOLD", "missing": ["measurement_verified"]}


def test_whitespace_is_not_evidence():
    record = known_record()
    record["evidence"] = [" "]
    assert evaluate(record)["verdict"] == "HOLD"


def test_non_object_is_invalid():
    with pytest.raises(ValueError):
        evaluate([])


def test_selftest():
    assert run_selftest() == 0
