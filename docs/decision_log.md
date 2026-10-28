# Data Preparation Decision Log

Date: 2026-10-29. Stage: raw data audit.

This log separates executed actions, measured evidence, proposed treatments and unresolved questions. It was prepared with Codex assistance. The student's own judgement on individual cleaning options has not yet been recorded; proposals must not be described as completed group discussions. Add actual agreement, disagreement and reasons when provided.

## D01 Preserve raw strings when checking missing values

- Evidence: 11 of 7,043 TotalCharges values contain a single space, `' '`. An empty-string-only check returns zero. The audit report lists the affected CSV lines and IDs.
- Alternatives: rely solely on parser null detection, or preserve strings and also check whether they are empty after trimming whitespace.
- Executed: the latter read-only check. No raw spaces were replaced with zero or a missing-value marker.
- Rationale: missingness is not determined solely by parser defaults. Preserving the source representation makes the finding traceable.
- Course reference: BI2 p. 10, consistency and missing values.

## D02 Treating the 11 blank accumulated charges

- Evidence: all 11 records have tenure=0 and Churn=No. They are also all of the zero-tenure records in the sample and represent approximately 0.1562% of customers.
- Possible explanation: recently joined customers may not yet have accumulated bills. Billing dates are absent, so neither the cause nor a true accumulated charge of zero is established.
- Option A: retain all 7,043 records, represent blanks explicitly as missing and retain a missingness indicator. If required by the model, fit an imputer on training data only. This retains new customers but leaves a modeling decision to be made.
- Option B: remove the 11 records, leaving 7,032 complete cases. This is simple but removes every zero-tenure customer in this sample. The churn-label share changes from 1,869/7,043 to 1,869/7,032; the denominator change must be disclosed.
- Option C: fill with zero. This retains the records but adds an unverified assumption about accumulated charges.
- Proposal: prefer A; use B as a sensitivity comparison if needed. No treatment has been applied.
- Course references: BI2 pp. 6 and 10 discuss missing data and discarding unsuitable responses, but do not prescribe an imputation rule for this dataset. Training-only fitting is a supplementary implementation safeguard.
- Student judgement: not yet recorded. This field is not a requirement to halt independent work.

## D03 No-service categories are not missing values

- Evidence: No phone service in MultipleLines agrees with PhoneService=No. No internet service in all six internet add-ons agrees with InternetService=No. All these consistency checks return zero violations.
- Alternatives: preserve these categories, merge them with No, or incorrectly treat them as missing.
- Proposal: preserve the distinction between lacking a base service and not purchasing an add-on. Any later merging for a derived metric must have an explicit definition.
- Rationale: the categories contain business information; merging loses that distinction.
- Course reference: BI2 pp. 43-53, coding meanings and nominal categories.

## D04 Checks do not automatically justify deleting records

- Evidence: zero exact duplicate rows and duplicate customer IDs. The three numeric fields contain no negative values; nonblank values parse as finite numbers. Tenure has no fractional values.
- Supplementary screening: no values are flagged by the 1.5 IQR rule in those three fields. This does not establish the absence of all business anomalies. The threshold is an implementation choice; the course discusses IQR and distributions.
- Proposal: do not delete records merely to demonstrate cleaning. Retain valid high charges and long tenures. Do not require TotalCharges to equal MonthlyCharges multiplied by tenure, because current monthly charges do not establish historical monthly prices.
- Course references: BI2 pp. 65, 74-79 and 94-99, dispersion, extreme values and distributions.

## D05 Observation period and modeling boundaries

- Evidence: no date fields; 1,869 Yes labels and 5,174 No labels.
- Proposal: use tenure as duration and describe the sample label share. Do not invent calendar cohorts or claim validated future-month prediction. Member C owns train/test splitting and evaluation.
- Handoff: customerID supports tracing, not prediction. Churn is the target and must not appear among predictors. Group thresholds and derived service counts are not yet defined.
- Course references: BI2 p. 42, cross-sectional and time-series data; BI4 pp. 36-38, classification, test data and class imbalance.

## D06 Retain traceable evidence for report writing

- Executed: preserve provenance, raw checksum, audit script, generated results and this decision log.
- Writing rule: state measurements as observations, label explanations as hypotheses and do not describe proposals as completed cleaning. Distinguish raw-data cleaning from model preprocessing.
- Next update: append the chosen treatment, affected counts, validation and limitations when implemented. Retain reasonable alternatives considered.
