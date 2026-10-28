# IBM Telco Customer Retention

COMP3134 BI-enabled CRM group project. Part B covers data preparation and exploratory analysis.

## Current stage

Stage 1 is complete: the original Kaggle CSV is preserved and audited. No records have been cleaned, removed, imputed or encoded. Modeling, report prose and slides are later stages.

## Reproduce the audit

Requires Python 3.10 or later, with no third-party packages:

```sh
python3 scripts/audit_data.py
```

The script resolves paths relative to the repository, verifies the raw SHA-256, and regenerates the audit outputs without rewriting the raw CSV.

- [Audit results and screenshot sections](reports/audit/audit.md)
- [Decision log with evidence and alternatives](docs/decision_log.md)
- [Initial field dictionary](docs/data_dictionary.md)
- [Source and observation-period limitations](docs/data_source.md)
- [Handoff for member C](docs/handoff_to_C.md)
- [Screenshot guide](docs/screenshots.md)

Raw source: [BlastChar Telco Customer Churn on Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn), version 1 as reported at retrieval. The exact downloaded CSV and source metadata are in `data/raw/`.

Audit summaries are generated, not hand-edited. Update the script and rerun if checks change. Analysis decisions belong in the decision log. Course slides and personal meeting notes are not copied into this repository.
