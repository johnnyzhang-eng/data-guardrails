# Prior art and scope

Official documentation checked on **2026-11-08**. This is a capability comparison,
not a benchmark. The tools below were not installed or integrated for this
review. Layer mappings are this project's interpretation of the documented
capabilities; custom assertions still need a correct metric definition and tests.

| Tool | Relevant layers | Core capability | Relationship to this repository | Official references |
| --- | --- | --- | --- | --- |
| Soda Core | L1; L2 with custom checks | Core v3 turns basic SodaCL checks into data-source queries, including counts, missing values and duplicates. Current Core is described as a Data Contract engine. | A practical alternative when a supported connector and managed check definitions are useful. The included YAML illustrates **v3 SodaCL**, is not a v4 contract, and is not run in CI. Do not infer that every feature in the wider Soda platform is available in Core. | [Core v3 overview](https://docs.soda.io/soda-documentation/soda-v3/overview-main), [SodaCL metrics](https://docs.soda.io/soda-documentation/soda-v3/sodacl-reference/metrics-and-checks), [current official project](https://github.com/sodadata/soda-core) |
| Great Expectations (GX Core) | L1; L2 with custom Expectations | Python Expectations grouped into Suites; Batch and Validation Definitions identify data and rules; Checkpoints run validations and actions; Data Docs present definitions and results. | A fuller validation workflow. This repository keeps a small SQLite implementation so the author can explain each calculation; it does not reproduce GX's configuration and reporting system. | [GX Core overview](https://docs.greatexpectations.io/docs/core/introduction/gx_overview/), [test an Expectation](https://docs.greatexpectations.io/docs/core/define_expectations/test_an_expectation/) |
| dbt data tests | L1 and L2 | SQL assertions return failing rows. Built-in generic tests cover `unique`, `not_null`, `accepted_values` and `relationships`; singular tests express custom SQL. | If the data already lives in dbt models, use dbt to enforce these assertions near the transformations. The report-versus-recalculation comparison here follows the same assertion pattern without a dbt project. Data tests differ from dbt unit tests of transformation logic. | [Data tests](https://docs.getdbt.com/docs/build/data-tests) |
| Deequ / PyDeequ | L1; L2 with custom constraints or comparisons | Deequ computes metrics and verifies constraints using Apache Spark; it also offers profiling, constraint suggestions, stored metrics and anomaly checks. PyDeequ exposes Deequ to Python. | Suitable when Spark is already required by the workload. This small example needs neither a JVM nor Spark. Suggested constraints still require review; learning a threshold does not make it a business rule. | [Deequ official documentation](https://github.com/awslabs/deequ), [PyDeequ official documentation](https://github.com/awslabs/python-deequ) |
| Pandera | L1; L2 with custom checks | DataFrame schemas and models validate types, nullability, uniqueness and custom checks; lazy validation can collect multiple failures. Supported features vary by backend. | A useful option for checks at DataFrame function boundaries. This repository instead checks SQLite tables directly. Comparing two independently calculated outputs would still require an explicit custom check. | [Pandera documentation](https://pandera.readthedocs.io/en/stable/), [DataFrame schemas](https://pandera.readthedocs.io/en/stable/dataframe_schemas.html) |
| Elementary | L1 and visibility into L1/L2 test results | The dbt package stores run metadata and test results and supplies anomaly and schema tests. The OSS CLI builds observability reports and supports alerts for a dbt project. | Adds history and operational visibility around dbt tests. A report of passing tests cannot establish that the report metric or business claim was specified correctly. This repository supplies small known-answer checks instead of an observability service. | [Elementary OSS](https://docs.elementary-data.com/oss/oss-introduction), [dbt package](https://docs.elementary-data.com/data-tests/dbt/dbt-package) |
| Semgrep | L4 | Code patterns expressed as rules can identify recurring code shapes. Annotated positive and negative examples are exercised with `semgrep --test`. | The local rule targets one narrow Python parsing pattern. It does not prove that all exception handling is correct or replace runtime tests; import aliases and other loop forms need separate coverage. | [Rule syntax](https://docs.semgrep.dev/writing-rules/rule-syntax), [Rule tests](https://docs.semgrep.dev/writing-rules/testing-rules) |

The comparison does not claim exclusive coverage. L3 checks the arithmetic and
scope behind one defined analytical claim; general causal validity remains a
human responsibility. L5 is a decision-review protocol with a small evidence
completeness check. These roles can be supported by other tools, but a green
validation result alone does not establish them.

**Pending verification (待核):** connector compatibility with this exact SQLite
schema, runtime/API compatibility of any optional integration, and equivalence
between the illustrative SodaCL YAML and an executable Soda Core scan. The
current Soda documentation separates v3 and v4; direct retrieval of some v4
reference pages failed during this review. No v4 syntax compatibility is claimed.

Also distinguish a fixed row-count threshold from historical anomaly detection.
The v3 SodaCL reference states that change-over-time thresholds require Soda
Cloud; the native example in this repository calculates its own explicit baseline
without using that service. See [SodaCL metrics and
checks](https://docs.soda.io/soda-documentation/soda-v3/sodacl-reference/metrics-and-checks).
