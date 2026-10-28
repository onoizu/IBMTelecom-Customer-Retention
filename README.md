# IBM Telco Customer Retention

COMP3134 BI-enabled CRM group project. Part B covers data preparation and exploratory analysis.

## Current stage

Stages 1 and 2 are complete: the original Kaggle CSV is preserved and audited, and a separate cleaned CSV retains all 7,043 customers. Eleven whitespace-only TotalCharges values are represented as missing, with a new TotalChargesMissing indicator. No records are removed, no charges are imputed, and service categories are unchanged. EDA, modeling, report prose and slides are later stages.

## Reproduce cleaning

```sh
python3 scripts/clean_data.py
python3 scripts/verify_cleaning.py
python3 scripts/run_audit_notebook.py --stage cleaning
```

- [Cleaned data](data/processed/telco_clean.csv) and [loading schema](data/processed/schema.json)
- [Cleaning counts and limitations](reports/cleaning/cleaning.md)
- [Cell-level change log](reports/cleaning/cell_changes.csv)
- [Executed cleaning notebook](notebooks/02_data_cleaning.ipynb)

The cleaned CSV contains 22 fields. Empty TotalCharges fields mean unknown, not zero. The indicator is a data-quality flag, not an automatically selected model feature. CSV has no native types: numeric parsing and model-side imputation must be explicit.

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
- [Executable audit walkthrough with actual outputs](notebooks/01_raw_data_audit.ipynb)

To regenerate the notebook outputs with standard Python, run `python3 scripts/run_audit_notebook.py`. This sequential runner executes the saved cells; it is not a Jupyter kernel. The notebook can also be run in a Python notebook editor. Capture code and actual output together for process screenshots.

All project Markdown, code comments, notebook explanations and commit messages are written in English.

Raw source: [BlastChar Telco Customer Churn on Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn), version 1 as reported at retrieval. The exact downloaded CSV and source metadata are in `data/raw/`.

Audit summaries are generated, not hand-edited. Update the script and rerun if checks change. Analysis decisions belong in the decision log. Course slides and personal meeting notes are not copied into this repository.
