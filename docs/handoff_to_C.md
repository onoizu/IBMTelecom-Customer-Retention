# Stage 2 Handoff to Member C

The cleaned dataset is available at `data/processed/telco_clean.csv`. Read `data/processed/schema.json` for the loading contract. Model training, splitting, imputation and feature encoding are still outstanding.

- Size: 7,043 unique customers, 22 fields: 21 original fields plus TotalChargesMissing.
- Target: Churn, unchanged at 1,869 Yes and 5,174 No. A future Yes=1/No=0 mapping has not been applied.
- Identifier: customerID is retained for tracing; exclude it from predictors.
- TotalCharges: 11 whitespace-only source values are now empty CSV fields meaning missing, not zero. All 11 customers remain. Their tenure is zero and their Churn label is No, but neither field was used to decide missingness.
- TotalChargesMissing: 1 for those 11 records, 0 for the other 7,032. This is an audit flag; decide separately whether it belongs in the model. It is not evidence of a causal relationship with churn.
- All other original cell values, service categories, customer IDs and row order are unchanged. No records were dropped, amounts imputed or values capped.
- CSV stores no types. Parse tenure as an integer and charges as numeric values, allowing missing TotalCharges. pandas default NA parsing recognizes empty fields; csv.DictReader returns empty strings.
- C owns the train/test split, random seed and evaluation. Fit any learned imputation and encoding on training data only. A model that cannot accept missing values needs preprocessing before fitting.
- No tenure bands or service counts have been created. Define boundaries, inclusion of base services and handling of no-service states before deriving these metrics.
- There are no calendar dates; do not describe this as a validated future-period forecast.

Rebuild with `python3 scripts/clean_data.py` and verify with `python3 scripts/verify_cleaning.py`. The cell-level log is in `reports/cleaning/cell_changes.csv`, the counts in `reports/cleaning/summary.json`, and the reasoning in decision D02. The executed notebook `notebooks/02_data_cleaning.ipynb` shows the transformation and checks. Stage 3 EDA is now available below.

## Stage 3 descriptive EDA update

The updated modeling scope is a decision tree, not the older K-means plan. B has completed descriptive EDA in `reports/eda/` and `notebooks/03_exploratory_analysis.ipynb`. The cleaned CSV is unchanged.

- Contract shares: month-to-month 1,655/3,875 (42.71%); one year 166/1,473 (11.27%); two year 48/1,695 (2.83%).
- Median tenure: 10 months for Yes and 38 for No. Median monthly charges: 79.65 for Yes and 64.43 for No, in source units.
- Tenure versus TotalCharges: Pearson r=0.826 using 7,032 complete pairs; this is a relationship to consider, not a directive to remove a predictor.
- These are full-sample, unadjusted observations. They do not prove intervention effects or measure held-out model performance. Do not select or tune the final model on the test set based on these results.
- No tree, split, model encoding, tenure bands, optimized thresholds or customer segments were created. Use the raw category definitions and make model-side decisions within training/validation.
- D can reuse the figures and exact counts, but final profiles and business insights should be developed with the model results.

## Part C implementation update

The handoff above records the preparation-stage status. Decision-tree preprocessing, splitting, training, validation and test evaluation are now implemented in `scripts/model_decision_tree.py`; running it creates local outputs in `reports/model/`, which are ignored by Git. See the root README for feature decisions, run commands, priority-group definitions and limitations. The cleaned input and all Part B audit, cleaning and EDA outputs are unchanged.
