# Stage 2 Cleaning Summary

The cleaned dataset retains all 7,043 customers. Whitespace-only accumulated charges are represented as missing rather than assumed to be zero. No model preprocessing or train/test split is performed.

| Operation | Count |
| --- | --- |
| Raw records retained | 7043 |
| Records deleted | 0 |
| Original TotalCharges cells normalized to missing | 11 |
| Values imputed | 0 |
| Original category values recoded | 0 |
| New indicator values created | 7043 |
| Indicator = 1 | 11 |
| Indicator = 0 | 7032 |

## Decision and limitation

Retaining the records avoids removing every zero-tenure customer in this sample. A missing value communicates uncertainty; it does not resolve the billing amount. The 11 affected records have tenure=0 and Churn=No, but these attributes do not determine the cleaning rule. The rule depends only on the raw TotalCharges text.

The new TotalChargesMissing field equals 1 for missing charges and 0 otherwise. It is a data-quality indicator; its use as a model feature remains a decision for C, not an automatic recommendation. No tenure bands or service-count metrics are added.

## Loading contract

`data/processed/telco_clean.csv` contains 22 fields: the original 21 plus the indicator. An empty field in TotalCharges means missing, not zero. Numeric values were validated, but CSV does not store data types. Read `data/processed/schema.json` and explicitly parse numeric columns. With pandas, default NA parsing recognizes the empty field; with csv.DictReader it remains an empty string.

## Validation

All IDs and row order are retained. Every original cell except the listed whitespace-to-missing changes is unchanged. Service labels and Churn counts are preserved. CSV serialization round-trips successfully and indicator values agree with missingness. Details are in `summary.json` and `cell_changes.csv`.

Raw SHA-256: `88be4b93fbe0cc83421af1c503794c97c342eca914c1576db7c276e61d61358a`

Clean SHA-256: `dd268a5970f95d3382f0f985bd8ac917e78203e2d055939ae7dfdc96d661823f`

Rebuild with `python3 scripts/clean_data.py`. Course basis: BI2 p. 10 for missingness and consistency, pp. 43-53 for explicit coding definitions. Keeping unknown charges missing is the project's chosen treatment, not a mandated course rule.
