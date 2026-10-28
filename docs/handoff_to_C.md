# Stage 1 Handoff to Member C

The current output is a raw-data audit, not final modeling input. No model training, train/test split, imputation, encoding or feature creation has taken place.

- Raw data: 7,043 unique customers and 21 fields.
- Target: Churn, with 1,869 Yes and 5,174 No labels. Proposed future mapping: Yes=1 and No=0; not yet applied.
- Identifier: retain customerID for tracing, but exclude it from predictors.
- TotalCharges: 11 space-only values, all with tenure=0. Proposed cleaning approach: retain customers and mark missing charges explicitly. The model-side treatment remains open. See decision D02.
- Service categories: preserve the distinction between No, No phone service and No internet service. Refer to BI2 for nominal one-hot encoding.
- Splitting: C owns the random seed, split and evaluation. Fit any learned imputation or encoding on training data only.
- Derived metrics: tenure groups and service counts have not been created. Define boundaries, inclusion of base services and treatment of no-service states before use.
- Time scope: no calendar dates; this is not an already validated future-period prediction exercise.
- See README for checks and reproduction. A later stage will provide cleaned data and operation counts.
