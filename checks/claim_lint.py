"""L3: does an order-volume change support a delivery-rate-drop claim?"""
import argparse
import json
from pathlib import Path


def assess_claim(*, baseline_total, baseline_delivered, current_total, current_delivered,
                 baseline_complete, current_complete, threshold_pp=5) -> str:
    """A descriptive rate comparison, never a causal or significance test.

    Completeness must come from separate evidence; caller flags do not prove it.
    Denominators must use the same population, time window length and status
    definition. Integer cross multiplication avoids a floating-point boundary.
    """
    counts = (baseline_total, baseline_delivered, current_total, current_delivered)
    if any(type(value) is not int or value < 0 for value in counts):
        raise ValueError("counts must be nonnegative integers")
    if baseline_delivered > baseline_total or current_delivered > current_total:
        raise ValueError("delivered count exceeds total")
    if type(threshold_pp) is not int or not 1 <= threshold_pp <= 100:
        raise ValueError("threshold_pp must be an integer in [1, 100]")
    if type(baseline_complete) is not bool or type(current_complete) is not bool:
        raise ValueError("completeness flags must be booleans")
    if not baseline_complete or not current_complete:
        return "INCOMPLETE_DATA"
    if not baseline_total or not current_total:
        return "NO_COMPARISON"
    difference = 100 * (baseline_delivered * current_total - current_delivered * baseline_total)
    boundary = threshold_pp * baseline_total * current_total
    return "SUPPORTED_RATE_DROP" if difference >= boundary else "UNSUPPORTED_RATE_DROP"


# label, totals and successes, completeness flags, expected verdict
KNOWN_CASES = [
    ("volume falls, rate unchanged", (100, 90, 20, 18, True, True), "UNSUPPORTED_RATE_DROP"),
    ("rate falls ten points", (100, 90, 100, 80, True, True), "SUPPORTED_RATE_DROP"),
    ("exact five-point boundary", (100, 90, 100, 85, True, True), "SUPPORTED_RATE_DROP"),
    ("below boundary", (100, 90, 100, 86, True, True), "UNSUPPORTED_RATE_DROP"),
    ("partial input", (100, 90, 20, 10, True, False), "INCOMPLETE_DATA"),
    ("no current orders", (100, 90, 0, 0, True, True), "NO_COMPARISON"),
    ("no baseline orders", (0, 0, 100, 80, True, True), "NO_COMPARISON"),
]


def case_input(values) -> dict:
    return dict(zip(("baseline_total", "baseline_delivered", "current_total", "current_delivered",
                     "baseline_complete", "current_complete"), values))


def run_selftest() -> int:
    failures = sum(assess_claim(**case_input(values)) != expected for _, values, expected in KNOWN_CASES)
    print(f"L3 selftest: {len(KNOWN_CASES) - failures}/{len(KNOWN_CASES)} known answers passed")
    return int(bool(failures))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--claim", type=Path)
    args = parser.parse_args()
    if args.selftest:
        return run_selftest()
    if not args.claim:
        parser.error("provide --claim")
    try:
        verdict = assess_claim(**json.loads(args.claim.read_text()))
    except (OSError, ValueError, TypeError) as error:
        parser.exit(2, f"Invalid input: {error}\n")
    print(verdict)
    return int(verdict != "SUPPORTED_RATE_DROP")


if __name__ == "__main__":
    raise SystemExit(main())
