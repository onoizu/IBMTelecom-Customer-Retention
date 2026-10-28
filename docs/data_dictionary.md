# Initial Field Dictionary

Working definitions for the 21 raw fields. Exact age thresholds, currency and observation month remain unverified. No encoding has been applied. Observed domains come from the file; numeric codes are not automatically continuous measurements.

| Field | Working meaning | Semantic type | Observed domain |
| --- | --- | --- | --- |
| customerID | Customer identifier for tracing, not prediction | Identifier | 7,043 unique IDs |
| gender | Gender category recorded by the source | Categorical | Female / Male |
| SeniorCitizen | Source-defined senior-customer flag; age threshold unverified | Categorical | 0 / 1 |
| Partner | Whether the customer has a partner | Categorical | No / Yes |
| Dependents | Whether the customer has dependents | Categorical | No / Yes |
| tenure | Customer tenure in months | Integer duration | 0 to 72 |
| PhoneService | Whether the customer has phone service | Categorical | No / Yes |
| MultipleLines | Whether the customer has multiple phone lines | Categorical | No / No phone service / Yes |
| InternetService | Internet service type | Categorical | DSL / Fiber optic / No |
| OnlineSecurity | Online security subscription | Categorical | No / No internet service / Yes |
| OnlineBackup | Online backup subscription | Categorical | No / No internet service / Yes |
| DeviceProtection | Device protection subscription | Categorical | No / No internet service / Yes |
| TechSupport | Technical support subscription | Categorical | No / No internet service / Yes |
| StreamingTV | Streaming TV subscription | Categorical | No / No internet service / Yes |
| StreamingMovies | Streaming movies subscription | Categorical | No / No internet service / Yes |
| Contract | Contract duration category | Categorical | Month-to-month / One year / Two year |
| PaperlessBilling | Paperless billing indicator | Categorical | No / Yes |
| PaymentMethod | Payment method | Categorical | Bank transfer (automatic) / Credit card (automatic) / Electronic check / Mailed check |
| MonthlyCharges | Monthly charge amount; currency unverified | Numeric amount | 18.25 to 118.75 |
| TotalCharges | Accumulated charges; currency and blank-value meaning unverified | Numeric amount | 18.8 to 8684.8; 11 single-space values ' ' |
| Churn | Churn target; source extract says left within the last month, calendar month unknown | Categorical | No / Yes |

## Cleaned output schema

The original 21 fields remain in their original order. TotalCharges now uses an empty CSV field for its 11 missing values. Its other values, and all values in the other original fields, are unchanged. CSV still stores text representations; `data/processed/schema.json` specifies the intended types.

| Added field | Definition | Type | Counts | Role |
| --- | --- | --- | --- | --- |
| TotalChargesMissing | 1 if the raw TotalCharges is blank after stripping whitespace, otherwise 0 | Binary integer | 1: 11; 0: 7,032 | Data-quality flag; predictor inclusion is not yet decided |

The indicator is the only added field. There are no tenure bands, service counts or encoded model features.

## Future model encoding and business metrics

- Proposed binary mapping: Yes=1, No=0; not yet implemented.
- SeniorCitizen 0/1 values are category flags, not ages.
- Define model encoding later; BI2 pp. 51-53 discuss one-hot encoding for nominal categories.
- Contract categories have a duration order, but codes 0/1/2 would not be actual month counts. Record the encoding rationale.
- No phone service and No internet service are meaningful states, not blanks.
- No business-derived metrics have been created. Specify consistent groups and service-count definitions before handoff.
