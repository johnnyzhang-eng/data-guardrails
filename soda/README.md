# Illustrative Soda Core checks

**Example only, not run in CI. 示例，未在 CI 里运行。**

`checks.yml` illustrates **Soda Core v3 SodaCL**; it is not a v4 Data Contract.
It is not a second executable implementation of the native L1 checks.

The native demo uses SQLite text timestamps. Soda's built-in freshness check
expects a date or timestamp type; a supported connector and type adaptation
would need to be selected and tested first. Soda freshness normally uses scan
time; the native demo uses a fixed `--as-of` to make known answers repeatable.
Its absolute `row_count > 0` is not the native three-day row-count comparison.
The missing-value threshold is zero, equivalent to a zero null-rate policy for
a nonempty table. A zero duplicate count checks uniqueness; a nonzero value
does not necessarily have the same counting definition as `duplicate_excess`.

No connection configuration or external service is included. Run the native
Python checks for the working example. For the official syntax and feature
boundaries, see [numeric metrics](https://docs.soda.io/soda-documentation/soda-v3/sodacl-reference/numeric-metrics),
[missing values](https://docs.soda.io/soda-documentation/soda-v3/sodacl-reference/missing-metrics),
[freshness](https://docs.soda.io/soda-documentation/soda-v3/sodacl-reference/freshness)
and [reference checks](https://docs.soda.io/soda-documentation/soda-v3/sodacl-reference/reference).
