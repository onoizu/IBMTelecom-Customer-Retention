# Exploratory Data Analysis

This is Part B's full-sample descriptive exploration. Member C owns decision-tree training and evaluation; D owns model-informed customer profiles and final business insights. No features are selected, thresholds optimized or models fitted here.

## Population and denominators

The cleaned sample contains 7,043 customers, including 1,869 with Churn=Yes (26.54%). Each categorical rate equals the Yes count divided by every customer in that category, not by all churners. Counts are provided to show group size.

TotalCharges uses 7,032 known values; its 11 unknown values are excluded only from calculations requiring that field. Those customers remain in all other applicable analyses. Numeric summaries report valid and missing counts by label.

## Selected descriptive comparisons

| Field | Category | Yes | Group total | Within-group share |
| --- | --- | --- | --- | --- |
| InternetService | DSL | 459 | 2421 | 18.96% |
| InternetService | Fiber optic | 1297 | 3096 | 41.89% |
| InternetService | No | 113 | 1526 | 7.40% |
| TechSupport | Yes | 310 | 2044 | 15.17% |
| TechSupport | No | 1446 | 3473 | 41.64% |
| TechSupport | No internet service | 113 | 1526 | 7.40% |
| Contract | Month-to-month | 1655 | 3875 | 42.71% |
| Contract | One year | 166 | 1473 | 11.27% |
| Contract | Two year | 48 | 1695 | 2.83% |

These comparisons describe this sample. Contract and service differences may reflect tenure, customer mix or other factors. They do not establish that changing a contract or buying a service prevents churn. Refer to the complete category table for all original categorical fields.

## Numeric summaries by label

| Field | Label | Valid n | Missing n | Median | Mean |
| --- | --- | --- | --- | --- | --- |
| tenure | All | 7043 | 0 | 29.00 | 32.37 |
| tenure | No | 5174 | 0 | 38.00 | 37.57 |
| tenure | Yes | 1869 | 0 | 10.00 | 17.98 |
| MonthlyCharges | All | 7043 | 0 | 70.35 | 64.76 |
| MonthlyCharges | No | 5174 | 0 | 64.43 | 61.27 |
| MonthlyCharges | Yes | 1869 | 0 | 79.65 | 74.44 |
| TotalCharges | All | 7032 | 11 | 1397.47 | 2283.30 |
| TotalCharges | No | 5163 | 11 | 1683.60 | 2555.34 |
| TotalCharges | Yes | 1869 | 0 | 703.55 | 1531.80 |

## Numeric relationships

| Left | Right | Pair n | Excluded n | Pearson r |
| --- | --- | --- | --- | --- |
| tenure | MonthlyCharges | 7043 | 0 | 0.248 |
| tenure | TotalCharges | 7032 | 11 | 0.826 |
| MonthlyCharges | TotalCharges | 7032 | 11 | 0.651 |

Pearson coefficients describe linear association only. No significance tests or population inference are made. Nominal categories are not assigned arbitrary numbers for correlation. TotalCharges can accumulate with tenure, so their relationship is not automatically an independent churn driver or a reason to remove a feature from a decision tree.

## Method choices and limits

- BI2 pp. 64-99 supports descriptive statistics, frequencies and distributions. Twelve equal-width histogram bins are a display choice, not model features or a teacher-mandated threshold.
- Boxplots and Pearson correlation are project implementation choices for the assigned distribution and relationship checks; not every detail is mandated by the lectures.
- Raw category values and no-service states remain distinct. No tenure bands, fee bands or service counts are introduced without agreeing their definitions with C.
- No confidence intervals, p-values, causal conclusions or future-period performance are claimed. Calendar observation dates and sampling design are unavailable; fee units are not labeled as a verified currency.
- Full-sample relationships are descriptive. C should choose preprocessing and tune the decision tree using training/validation data and reserve test data for evaluation. These plots are not held-out evidence of predictive performance.

## Artifacts

CSV tables contain the underlying statistics. Six PNG/SVG figure pairs are in `figures/`. The executed notebook shows loading, grouped-rate calculations and denominator checks for process screenshots. See `docs/decision_log.md` for rationale and `docs/handoff_to_C.md` for modeling boundaries.
