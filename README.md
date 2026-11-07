# data-guardrails

这是一个学生个人项目，用五层检查练习“数据、报表、结论、代码和决策分别怎样出错”。
所有例子都是从零生成的外卖合成数据；没有接入生产，也不宣称经过生产验证。
已知答案自测用于检验检查器本身，不能代替真实数据上的验证。

A small learning project for checking data work at five different layers.
Each layer has an executable check, fixed known-answer selftests and pytest
coverage. The core runs offline with Python 3.12+ and SQLite from the standard
library. Optional tool examples are clearly separated from working checks.

| Layer | Question | Implementation |
| --- | --- | --- |
| L1 — data quality | Are the raw tables fit to inspect? | Freshness, daily row-count change, unique/non-null order IDs, amount null rate and references to merchants/users. |
| L2 — result integrity | Does the report equal a recalculation of raw data? | Compare scoped row counts, known-amount counts and an amount sum with the report JSON. |
| L3 — analytical claim | Do the supplied counts support the stated conclusion? | Check a delivery-rate-drop claim, its denominators, completeness flags and percentage-point threshold. |
| L4 — code recurrence | Can one bad input line interrupt a batch again? | A safe JSON-lines parser, regression tests and a narrow Semgrep rule with annotated fixtures. |
| L5 — decision review | Is there enough recorded evidence to review an action? | A three-gate protocol and a required-field checker; a filled record does not establish truth. |

## Run

From this repository's root, with Python already available:

```bash
bash run_selftests.sh
python3 -m pytest -q
```

The first command uses only the standard library for its five runtime checks.
It also runs `semgrep --test` if Semgrep is already installed; otherwise it
prints an explicit skip. The second command needs an existing pytest installation.
`requirements-dev.txt` records the test-tool versions used by the CI definition.
No local installation is needed to run the native selftests.
Set `PYTHON` to an existing interpreter path if necessary. Run pytest with the
same interpreter. Selftest failure is a nonzero exit; an absent Semgrep is a
nonzero exit when `REQUIRE_SEMGREP=1`.

```bash
python3 examples/generate_data.py --db artifacts/delivery.sqlite3
python3 -m checks.data_quality --db artifacts/delivery.sqlite3 \
  --as-of 2025-01-12T00:00:00+00:00 --day 2025-01-07
python3 -m checks.result_integrity --db artifacts/delivery.sqlite3 \
  --report examples/report.json
python3 -m checks.claim_lint --claim examples/rate_claim.json
python3 -m checks.json_batch --file examples/orders.jsonl
python3 -m checks.decision_gate --record examples/decision.json
```

Run the example commands individually: some intentionally return status 1.
L1 flags all five seeded problems; L2's supplied report matches and returns 0.
L3 returns `UNSUPPORTED_RATE_DROP` and status 1: 90/100 and 18/20 are both 90%,
although order volume fell. L4 keeps both valid orders, records bad line 2 and
returns 1. L5 returns `REVIEW_READY` and status 0 for the illustrative record.
For L1, L2, L3 and L5, malformed inputs return 2. A selftest returning 0 means
the checker recognized its known answers, including bad-data cases.

## Synthetic dataset and policies

The schema is deliberately small:

```text
orders(order_id, user_id, merchant_id, order_time, amount, status)
merchants(merchant_id, city, category)
users(user_id, city, register_date)
```

The fixed seed is 16. There are 144 distinct orders across eight UTC days and
one repeated row, for 145 raw rows. One amount is NULL, one is zero, and one
order references an absent merchant. The seventh day has 4 orders instead of
20. The feed ends after the eighth day. At the fixed check time, its newest
event is 84 hours old. All records and problem cases are synthetic; they are
not anonymized business records.

The generator replaces the three demo tables on rerun. Use a disposable demo
database: those table names are rebuilt, while unrelated tables are left alone.
Raw orders deliberately lack database key/reference constraints so the checks
can observe invalid rows. The dimension tables have primary keys.

L1 uses a maximum age of 48 hours, a daily count between 50% and 150% of the
mean of the previous three calendar days, and zero tolerance for bad keys,
missing amounts or references. Empty input fails all five checks. Missing
calendar days count as zero, and a zero baseline cannot pass. The age uses
event time, so it does not establish when data arrived. Thresholds are demo
policies, not universal production defaults.

L2 uses an inclusive start date, exclusive end date and explicit order status.
Amounts are integer demo currency units. NULL amounts are excluded from the
sum and exposed through `known_amount_rows`; zero amounts are counted. Raw
duplicates remain in the recalculation. Agreement proves report consistency
under that scope, not clean source data. L1 must still be considered.

L3 checks one descriptive rate comparison, not causation or statistical
significance. The caller must independently establish comparable populations,
windows, status definitions and completeness. L5 checks recorded fields and
boolean gates; it cannot verify evidence or authorize an action.

## Scope and status

This is a personal learning project with no production integration. Native
checks are intentionally small enough to read and explain in an interview.
Passing tests demonstrate these specific examples, not general correctness.

The GitHub Actions workflow targets Ubuntu and Python 3.12, provisions the
declared test tools, and runs selftests, Semgrep fixtures and pytest. A workflow
file is not evidence of a successful hosted CI run.

- [Official-tool comparison](docs/PRIOR-ART.md): Soda Core, GX Core, dbt,
  Deequ/PyDeequ, Pandera, Elementary and Semgrep.
- [Soda example](soda/README.md): v3 SodaCL illustration, **not run in CI**.
- [Semgrep rule and limits](semgrep/README.md): one code pattern, not a proof
  of correct exception handling.
- [Decision protocol](decision-check/README.md): measurement, mechanism and
  contrary-evidence gates.

There are no external-data connectors or automatic corrective actions.
