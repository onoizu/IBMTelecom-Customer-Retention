# Data Preparation Decision Log

Date: 2026-10-29. Stages: raw data audit, cleaning and descriptive EDA. Earlier alternatives are retained below; implementation updates distinguish the selected treatment from those alternatives.

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
- Initial proposal at Stage 1: prefer A; use B as a sensitivity comparison if needed. See the implementation update below for the treatment subsequently applied.
- Course references: BI2 pp. 6 and 10 discuss missing data and discarding unsuitable responses, but do not prescribe an imputation rule for this dataset. Training-only fitting is a supplementary implementation safeguard.
- Student judgement: not yet recorded. This field is not a requirement to halt independent work.

### Implementation update for D02

After authorization to continue, Option A was implemented for the cleaned data. All 7,043 records are retained. Eleven whitespace-only TotalCharges cells become empty CSV fields, explicitly defined as missing by the schema. No amount is imputed. TotalChargesMissing is added for all records: 11 ones and 7,032 zeros. The normalization rule reads only TotalCharges, not tenure or Churn. The indicator is retained for traceability; using it as a predictor is left to C.

The affected IDs, source line numbers and before/after representations are in `reports/cleaning/cell_changes.csv`. All other original cells and row order remain unchanged. True zero values are preserved, invalid nonblank amounts raise an error, and rerunning reproduces identical outputs. Unknown charges still require a model-side decision; retaining missingness does not resolve their true value. No personal explanation from the student has been invented.

## D03 No-service categories are not missing values

- Evidence: No phone service in MultipleLines agrees with PhoneService=No. No internet service in all six internet add-ons agrees with InternetService=No. All these consistency checks return zero violations.
- Alternatives: preserve these categories, merge them with No, or incorrectly treat them as missing.
- Proposal: preserve the distinction between lacking a base service and not purchasing an add-on. Any later merging for a derived metric must have an explicit definition.
- Rationale: the categories contain business information; merging loses that distinction.
- Course reference: BI2 pp. 43-53, coding meanings and nominal categories.

Implementation update: all original category strings were preserved exactly, including no-service states. Service-dependency rules are validated before export; conflicts stop processing rather than trigger an undocumented repair.

## D04 Checks do not automatically justify deleting records

- Evidence: zero exact duplicate rows and duplicate customer IDs. The three numeric fields contain no negative values; nonblank values parse as finite numbers. Tenure has no fractional values.
- Supplementary screening: no values are flagged by the 1.5 IQR rule in those three fields. This does not establish the absence of all business anomalies. The threshold is an implementation choice; the course discusses IQR and distributions.
- Proposal: do not delete records merely to demonstrate cleaning. Retain valid high charges and long tenures. Do not require TotalCharges to equal MonthlyCharges multiplied by tenure, because current monthly charges do not establish historical monthly prices.
- Course references: BI2 pp. 65, 74-79 and 94-99, dispersion, extreme values and distributions.

Implementation update: zero records deleted and zero outliers capped. The cleaning script rejects invalid amounts, duplicate IDs, invalid categories and inconsistent base/add-on service states rather than silently changing the data.

## D05 Observation period and modeling boundaries

- Evidence: no date fields; 1,869 Yes labels and 5,174 No labels.
- Proposal: use tenure as duration and describe the sample label share. Do not invent calendar cohorts or claim validated future-month prediction. Member C owns train/test splitting and evaluation.
- Handoff: customerID supports tracing, not prediction. Churn is the target and must not appear among predictors. Group thresholds and derived service counts are not yet defined.
- Course references: BI2 p. 42, cross-sectional and time-series data; BI4 pp. 36-38, classification, test data and class imbalance.

## D06 Retain traceable evidence for report writing

- Executed: preserve provenance, raw checksum, audit script, generated results and this decision log.
- Writing rule: state measurements as observations, label explanations as hypotheses and do not describe proposals as completed cleaning. Distinguish raw-data cleaning from model preprocessing.
- Next update: append the chosen treatment, affected counts, validation and limitations when implemented. Retain reasonable alternatives considered.

## D07 Scope of exploratory analysis and model ownership

The updated team arrangement uses a decision tree for C, replacing the old K-means description. B owns descriptive EDA; C owns feature preprocessing, splitting, tuning and evaluation; D owns model-informed profiles and final business insights. No clustering, K selection, customer segment labels or tree training is included here.

Full-sample plots describe the dataset and are not independent model-validation evidence. C must select and tune features using training/validation data and keep test evaluation separate. No threshold is optimized against the full-sample target.

## D08 Denominators and unknown charges in EDA

- Choice: group churn share = number of Yes labels in that group / all customers in that group. Display both counts alongside rates.
- Alternative rejected: dividing by all churners answers a different question and can misrepresent group risk.
- Unknown TotalCharges are excluded only from calculations requiring that variable. Other analyses keep 7,043 records. Every numeric summary and correlation includes its actual sample size.
- No-service categories remain separate. The same no-internet customers appear in multiple service panels, so those panels must not be added together.
- Course basis: BI2 frequency and relative-frequency discussion, especially pp. 80-91. Missing-value handling is the project implementation choice.

## D09 Numeric distributions and correlation

- Display means, medians, quartiles and standard deviations. Use 12 equal-width histogram bins as a reproducible visual setting, not a new feature or a teacher-specified rule.
- Compare numeric distributions by observed Churn label using boxplots. The full-sample IQR audit and within-label boxplot outliers use different reference distributions; subgroup outliers can appear even when the full-sample screen flags none. No observations are removed from either.
- Calculate Pearson correlation for tenure, MonthlyCharges and TotalCharges using pairwise complete records. Exclude IDs and arbitrary category codes; keep Churn comparisons in separate descriptive tables and plots.
- Pearson measures linear association. It is not a causal claim or significance test. No p-values, confidence intervals or generalization to a verified population are reported.
- Tenure and accumulated charges have r approximately 0.826 (n=7,032). Accumulation provides a plausible interpretation; this is not an automatic feature-removal rule for C's decision tree.
- Course basis: BI2 descriptive statistics and distributions; the screenshot assignment requires relationship checks. Boxplot styling and Pearson implementation are project choices, not claimed to be mandated in every detail by the teacher.
