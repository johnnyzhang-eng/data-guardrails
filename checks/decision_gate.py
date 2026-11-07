"""L5: validate a decision record's required evidence fields, not its truth."""
import argparse
import copy
import json
from pathlib import Path

TEXT_FIELDS = ("claim", "scope", "action", "owner", "alternative_explanation", "stop_condition")
GATES = ("measurement_verified", "mechanism_compared", "contrary_evidence_sought")


def evaluate(record) -> dict:
    if not isinstance(record, dict):
        raise ValueError("decision record must be an object")
    missing = [field for field in TEXT_FIELDS
               if not isinstance(record.get(field), str) or not record[field].strip()]
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence or any(
            not isinstance(item, str) or not item.strip() for item in evidence):
        missing.append("evidence")
    missing.extend(field for field in GATES if record.get(field) is not True)
    return {"verdict": "HOLD" if missing else "REVIEW_READY", "missing": missing}


def known_record() -> dict:
    return {"claim": "The small order count may be incomplete input.",
            "scope": "Synthetic orders, complete UTC days only.",
            "action": "Recompute the daily row counts before interpreting demand.",
            "owner": "demo learner", "alternative_explanation": "Demand may also have changed.",
            "stop_condition": "Keep the conclusion on hold until input completeness is checked.",
            "evidence": ["L1 row-count output for the synthetic dataset"],
            "measurement_verified": True, "mechanism_compared": True, "contrary_evidence_sought": True}


def known_cases() -> list:
    good = known_record()
    cases = [("complete record", good, "REVIEW_READY")]
    for field in (*TEXT_FIELDS, "evidence", *GATES):
        changed = copy.deepcopy(good)
        del changed[field]
        cases.append((f"missing {field}", changed, "HOLD"))
    return cases


def run_selftest() -> int:
    cases = known_cases()
    failures = sum(evaluate(record)["verdict"] != expected for _, record, expected in cases)
    print(f"L5 selftest: {len(cases) - failures}/{len(cases)} known answers passed")
    return int(bool(failures))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--record", type=Path)
    args = parser.parse_args()
    if args.selftest:
        return run_selftest()
    if not args.record:
        parser.error("provide --record")
    try:
        result = evaluate(json.loads(args.record.read_text()))
    except (OSError, ValueError) as error:
        parser.exit(2, f"Invalid input: {error}\n")
    print(json.dumps(result, indent=2))
    return int(result["verdict"] == "HOLD")


if __name__ == "__main__":
    raise SystemExit(main())
