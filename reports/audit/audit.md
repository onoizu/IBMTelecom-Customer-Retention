# Stage 1 Raw Data Audit

This stage only inspects the data. No records have been deleted, imputed, encoded or exported as cleaned data.

## Data overview

Source: https://www.kaggle.com/datasets/blastchar/telco-customer-churn

File: `WA_Fn-UseC_-Telco-Customer-Churn.csv`. Each row corresponds to a customer ID. The download date is not the observation date.

| Item | Result |
| --- | --- |
| Customer records | 7043 |
| Fields | 21 |
| Unique customer IDs | 7043 |
| Exact duplicate rows beyond the first | 0 |
| Duplicate customer IDs beyond the first | 0 |
| Churn = Yes | 1869 |
| Churn = No | 5174 |
| Sample share with Churn = Yes | 26.5370% |
| Blank TotalCharges | 11 |
| Raw file unchanged | True |

## Missing value evidence

Blank includes empty strings and whitespace-only strings. The original CSV is preserved; repr exposes spaces below.

| CSV line including header | customerID | tenure | MonthlyCharges | TotalCharges raw representation | Churn |
| --- | --- | --- | --- | --- | --- |
| 490 | 4472-LVYGI | 0 | 52.55 | ' ' | No |
| 755 | 3115-CZMZD | 0 | 20.25 | ' ' | No |
| 938 | 5709-LVOEQ | 0 | 80.85 | ' ' | No |
| 1084 | 4367-NUYAO | 0 | 25.75 | ' ' | No |
| 1342 | 1371-DWPAZ | 0 | 56.05 | ' ' | No |
| 3333 | 7644-OMVMY | 0 | 19.85 | ' ' | No |
| 3828 | 3213-VVOLG | 0 | 25.35 | ' ' | No |
| 4382 | 2520-SGTTA | 0 | 20 | ' ' | No |
| 5220 | 2923-ARZLG | 0 | 19.7 | ' ' | No |
| 6672 | 4075-WKNIU | 0 | 73.35 | ' ' | No |
| 6756 | 2775-SEFEE | 0 | 61.9 | ' ' | No |

Blank charges are concentrated among customers with tenure zero. This pattern alone does not establish that their accumulated charges equal zero.

## Field quality checks

CSV has no native data types. The audit preserves original strings and parses numerical values only in memory.

| Field | Distinct raw values | Blank values | Empty strings | Leading or trailing whitespace |
| --- | --- | --- | --- | --- |
| customerID | 7043 | 0 | 0 | 0 |
| gender | 2 | 0 | 0 | 0 |
| SeniorCitizen | 2 | 0 | 0 | 0 |
| Partner | 2 | 0 | 0 | 0 |
| Dependents | 2 | 0 | 0 | 0 |
| tenure | 73 | 0 | 0 | 0 |
| PhoneService | 2 | 0 | 0 | 0 |
| MultipleLines | 3 | 0 | 0 | 0 |
| InternetService | 3 | 0 | 0 | 0 |
| OnlineSecurity | 3 | 0 | 0 | 0 |
| OnlineBackup | 3 | 0 | 0 | 0 |
| DeviceProtection | 3 | 0 | 0 | 0 |
| TechSupport | 3 | 0 | 0 | 0 |
| StreamingTV | 3 | 0 | 0 | 0 |
| StreamingMovies | 3 | 0 | 0 | 0 |
| Contract | 3 | 0 | 0 | 0 |
| PaperlessBilling | 2 | 0 | 0 | 0 |
| PaymentMethod | 4 | 0 | 0 | 0 |
| MonthlyCharges | 1585 | 0 | 0 | 0 |
| TotalCharges | 6531 | 11 | 0 | 11 |
| Churn | 2 | 0 | 0 | 0 |

## Numeric range checks

| Field | Valid numeric values | Minimum | Maximum | Median | Negative values | 1.5 IQR flags |
| --- | --- | --- | --- | --- | --- | --- |
| tenure | 7043 | 0.0 | 72.0 | 29.0 | 0 | 0 |
| MonthlyCharges | 7043 | 18.25 | 118.75 | 70.35 | 0 | 0 |
| TotalCharges | 7032 | 18.8 | 8684.8 | 1397.475 | 0 | 0 |

IQR flags are screening indicators, not proof of error or a reason for automatic deletion. The 1.5 IQR threshold is a supplementary implementation choice, not a stated course requirement. No unsupported upper charge limit is imposed.

## Categories and cross-field consistency

| Check | Violating records |
| --- | --- |
| gender: outside expected categories | 0 |
| SeniorCitizen: outside expected categories | 0 |
| Partner: outside expected categories | 0 |
| Dependents: outside expected categories | 0 |
| PhoneService: outside expected categories | 0 |
| PaperlessBilling: outside expected categories | 0 |
| Churn: outside expected categories | 0 |
| MultipleLines: outside expected categories | 0 |
| InternetService: outside expected categories | 0 |
| OnlineSecurity: outside expected categories | 0 |
| OnlineBackup: outside expected categories | 0 |
| DeviceProtection: outside expected categories | 0 |
| TechSupport: outside expected categories | 0 |
| StreamingTV: outside expected categories | 0 |
| StreamingMovies: outside expected categories | 0 |
| Contract: outside expected categories | 0 |
| PaymentMethod: outside expected categories | 0 |
| phone_service_vs_multiple_lines | 0 |
| internet_service_vs_OnlineSecurity | 0 |
| internet_service_vs_OnlineBackup | 0 |
| internet_service_vs_DeviceProtection | 0 |
| internet_service_vs_TechSupport | 0 |
| internet_service_vs_StreamingTV | 0 |
| internet_service_vs_StreamingMovies | 0 |
| tenure_noninteger | 0 |

CSV lines containing nonblank values that cannot be parsed as finite numbers: `{'tenure': [], 'MonthlyCharges': [], 'TotalCharges': []}`.

## Time scope and analysis limitations

The file has no observation, joining or churn date columns. The source page describes Churn as leaving within the last month; the calendar month has not been verified. Tenure is duration in months, not a calendar time series. The reported share describes this sample and cannot be directly generalized to a real business or the current market. Feature relationships with Churn have not yet been analysed.

## Reproducibility

Run `python3 scripts/audit_data.py` to rebuild the audit outputs. The script first verifies the raw SHA-256:

`88be4b93fbe0cc83421af1c503794c97c342eca914c1576db7c276e61d61358a`

Course references: BI2 p. 10 (consistency and missing values), pp. 43-53 (coding and dictionaries), pp. 64-99 (descriptive statistics); BI4 p. 38 (class imbalance and test data). See `docs/decision_log.md` for rules and proposed treatments. For screenshots of executable work, use `notebooks/01_raw_data_audit.ipynb` and `docs/screenshots.md`.
