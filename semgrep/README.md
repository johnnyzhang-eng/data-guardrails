# L4: prevent a parsing mistake from returning

One malformed JSON line must not discard the valid orders after it.
The rule flags `json.loads()` inside a `for` loop unless it is inside a
`try`/`except` block. The positive fixture must match; negative fixtures must
remain clear. Its matching patterns retain the small, generic rule; the
description and examples are written solely for this project.

With Semgrep already available, run from the repository root:

```bash
semgrep --test --config semgrep/rules semgrep/tests
```

The standard-library parsing guard also has executable regression checks:

```bash
python3 -m checks.json_batch --selftest
python3 -m checks.json_batch --file orders.jsonl
```

The file command prints valid values and rejected physical line numbers. It
exits 1 when any line is rejected, so keeping good rows does not hide an error.
Blank lines are skipped. This validates JSON syntax, not an order schema.

The static rule has a deliberately narrow scope: it does not follow function
aliases, inspect comprehensions, or prove exception handling is correct. Any
enclosing `try`/`except` is excluded, including a handler for the wrong exception
or one that merely raises again. Runtime tests are still necessary. The safe
fixture illustrates continuation; `checks/json_batch.py` additionally records
rejected line numbers. No external service is used.
