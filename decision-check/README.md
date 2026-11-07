# L5: a small decision-review protocol

Use these gates before declaring a result unusable, treating a symptom as a
repeat of an earlier problem, or taking a consequential action on a conclusion.
This is a general review protocol, not an installed agent skill.

1. **P1 — verify the measurement.** Write down the population, time window,
   denominator, missing inputs and an independent recalculation. A low order
   count can mean incomplete input; it does not by itself establish low demand.
2. **P2 — compare mechanisms.** List evidence for the proposed cause and an
   alternative. Similar-looking charts can result from different causes. A
   duplicate order and a one-to-many join can both inflate totals but need
   different corrections.
3. **P3 — seek contrary evidence.** Record what would overturn the preferred
   explanation, who will review it, and the condition for stopping or revising
   the action. Agreement is not independent evidence.

Keep a record with `claim`, `scope`, `action`, `owner`,
`alternative_explanation`, `stop_condition`, a nonempty `evidence` list, and
three booleans: `measurement_verified`, `mechanism_compared`,
`contrary_evidence_sought`. Evidence should identify a reproducible query,
input and output; the short synthetic example only illustrates that structure.
For an unfamiliar problem, the mechanism comparison can explicitly say that
no previous mechanism has been established.

```bash
python3 -m checks.decision_gate --record examples/decision.json
python3 -m checks.decision_gate --selftest
```

The executable checks **record completeness**, not the truth of the evidence.
`REVIEW_READY` means a person has a filled-in record to review. It neither
authorizes an action nor proves the conclusion. Missing fields or gates return
`HOLD` with exit status 1. The known-answer tests check the complete record and
each missing field; they cannot test a person's judgment.

In the demo, an order count of 4 against a baseline of 20 is an L1 alert. The
decision is to hold a demand conclusion pending completeness evidence. A
different example has 90/100 versus 18/20 delivered orders: volume fell, but
the delivery rate stayed at 90%. L3 rejects a five-point rate-drop claim.
