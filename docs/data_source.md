# Data Source and Version

The project uses the group's selected [BlastChar Telco Customer Churn dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn). The file was downloaded directly from Kaggle. No alternative repository's dataset, cleaning code or analysis results were substituted.

- Download endpoint: https://www.kaggle.com/api/v1/datasets/download/blastchar/telco-customer-churn
- Archive member: `WA_Fn-UseC_-Telco-Customer-Churn.csv`
- Retrieved CSV: 977,501 bytes, 7,043 data rows and 21 fields.
- Version: Kaggle metadata reports version 1, last updated on 2018-02-23. The update date is not the observation date.
- Retrieval timestamp and SHA-256: `data/raw/source_manifest.json`.
- Original metadata response: `data/raw/kaggle_metadata.json`. Its license label is `Data files © Original Authors`; this does not give this project ownership of the data or justify assigning a different license.
- Preservation: the CSV was extracted byte-for-byte, retaining CRLF line endings, whitespace, field order and values. The audit does not rewrite it.

The source page's search extract describes Churn as customers leaving within the last month. The full page body could not be extracted by the text browser; other source details are not presented as verified. The IBM dataset name identifies the teaching dataset, not operational records obtained from an actual telecom company by this group.

## Time and business limitations

Each row has a unique customer ID. There are no observation, joining or churn dates and no repeated monthly observations. Treat this as a customer-level cross-sectional sample. Tenure is duration in months, not a calendar month. The observation month and a calendar time series cannot be reconstructed from this file.

Currency, the exact SeniorCitizen age threshold, geography and sampling design have not been verified against the complete documentation for this version. Do not invent these details. Costs are unavailable, so charges are not profit or customer lifetime value.

## Retrieving another copy

The committed CSV and checksum support local reproduction. Download any new copy to a temporary location and compare hashes before considering replacement. A changed source version requires a new provenance record and audit.

IBM's public example repository was consulted for background, but its data, models and workflow were not used. The actual CSV came from the Kaggle endpoint above.
