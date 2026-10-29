# IBM Telco Customer Retention

COMP3134 BI-enabled CRM group project. This repository combines data preparation and descriptive EDA (Part B) with decision-tree modelling and priority-customer identification (Part C).

## Current stage

Stages 1, 2 and 3 are complete: the original Kaggle CSV is preserved and audited, and a separate cleaned CSV retains all 7,043 customers. Eleven whitespace-only TotalCharges values are represented as missing, with a new TotalChargesMissing indicator. No records are removed, no charges are imputed, and service categories are unchanged. Descriptive EDA is complete with six figure sets and underlying tables. Decision-tree modelling is now included: the cleaned data feed a reproducible training/validation/test workflow, three priority leaves and 20 training-subsample stability checks. Final report prose, PDF-generation code and slides are not included.

## Reproduce decision-tree modelling

Use Python 3.12 and a dedicated virtual environment. The EDA and model requirement files record different tested plotting versions; install them in separate environments.

```sh
python3.12 -m venv .venv-model
source .venv-model/bin/activate
python -m pip install -r requirements-model.txt
python scripts/model_decision_tree.py
```

The script reads `data/processed/telco_clean.csv` directly and checks its SHA-256 against `reports/cleaning/summary.json`. It resolves paths relative to this repository, so it also runs from another working directory. Cleaning and raw data are not rewritten. Each run overwrites the local model outputs in `reports/model/`. These generated files are ignored by Git and are not uploaded; paths listed below are available after running the script.

### Inputs and modelling decisions

- Target: `Churn`, mapped as No=0 and Yes=1. There are 18 raw predictors.
- Customer information: `gender`, `SeniorCitizen`, `Partner`, `Dependents`.
- Service subscriptions: `PhoneService`, `MultipleLines`, `InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`.
- Account information: `tenure`, `MonthlyCharges`, `Contract`, `PaperlessBilling`, `PaymentMethod`.
- Excluded: `customerID` (identifier), `Churn` (target), `TotalCharges` (simplification given its overlap with tenure/monthly charges), and `TotalChargesMissing` (audit indicator). Excluding overlapping fields is a project choice, not a requirement of decision trees.
- Stratified split with seed 42: 4,225 training, 1,409 validation and 1,409 test customers (60%/20%/20%). Missing-value filling and full one-hot encoding are fitted within the pipeline on training data only. No-service categories stay distinct.
- Training-only five-fold cross-validation compares maximum depths 2/3/4 and minimum leaf sizes 50/100/200 using average precision (AP). The selected tree has maximum depth 4 and at least 100 training customers per leaf.
- Validation F1 selects a classification threshold of 0.334545. This threshold is separate from the tree's feature cutoffs and its default 0.5 classification threshold. AP is not accuracy.
- Three priority leaves are selected by training churn proportion, with training size breaking ties. Test labels do not select the groups. Other customers remain `Other`; the three groups are not a complete segmentation of the customer base.

### Saved results and figures

At the selected threshold, test accuracy is 76.1%, precision 53.8%, recall 69.3%, ROC-AUC 0.826 and AP 0.600. Predicting No for everyone would give 73.5% accuracy, so accuracy alone is not a useful justification. The model identifies 259 of 374 observed churners and flags 222 non-churners.

The priority groups are defined by the fitted tree. These test results describe held-out customer records rather than future intervention effects:

- **S1 - New fiber customers on monthly contracts:** tenure 0-1 months; leaf 24; training 129/152 (84.9%), test 40/44 (90.9%).
- **S2 - Early-tenure fiber customers on monthly contracts:** tenure 2-15 months; leaf 25; training 310/481 (64.4%), test 102/166 (61.4%).
- **S3 - New DSL customers without the technical-support add-on:** monthly contract, tenure 0-3 months, TechSupport=No; leaf 18; training 101/182 (55.5%), test 37/60 (61.7%). The encoded rule is non-fiber plus TechSupport=No; the validated service dependencies make this DSL. Not buying the add-on does not imply that general customer service is unavailable.

Together, these leaves cover 270/1,409 test customers (19.2%) and 179/374 test churners (47.9%). The proportions have sampling uncertainty; the exported Wilson intervals do not establish future risk or treatment effects.

- Decision-tree diagram (`reports/model/decision_tree.png`), plain-text tree (`reports/model/decision_tree.txt`), exact leaf rules (`reports/model/DT_rules.csv`) and test leaf profiles (`reports/model/DT_profiles.csv`).
- Test precision-recall curve (`reports/model/performance.png`), test metrics (`reports/model/metrics.csv`), metrics at threshold 0.5 (`reports/model/metrics_threshold_05.csv`), test predictions (`reports/model/test_predictions.csv`) and permutation importance (`reports/model/DT_importance.csv`).
- Priority groups with training/test counts and intervals (`reports/model/priority_segments.csv`).
- Stability runs (`reports/model/stability_runs.csv`), feature recurrence (`reports/model/feature_stability.csv`), group membership summary (`reports/model/segment_stability.csv`) and all matched memberships (`reports/model/stability_segment_matches.csv`).
- Cross-validation candidates (`reports/model/DT_cv.csv`), saved split (`reports/model/data_split.csv`), run metadata (`reports/model/run_info.json`) and fitted pipeline (`reports/model/decision_tree_model.joblib`).

### Stability and interpretation limits

Twenty fixed seeds (100-119) each sample 80% of the original training customers. Tree settings stay fixed; the same validation customers are used for comparisons, and test customers are excluded from stability refitting and matching. Match groups by customer-membership Jaccard overlap, not node ID. These overlapping subsamples are a sensitivity check, not 20 independent final evaluations.

Contract, tenure, internet service and monthly charges appear in all 20 refits; Contract is always the root. Mean membership overlap is 0.642/0.692/0.704 for S1/S2/S3, with minima 0.145/0.235/0.358. Broad features recur, but exact segment boundaries can change. Feature recurrence does not establish that the tree structure is unchanged.

The sample has no dates or customer histories. Earlier exploration has already inspected this test split, so it is not a fresh final validation. Tree rules, feature importance and group differences describe associations, not causes. Leaf proportions are not separately calibrated individual future probabilities. High risk does not prove that a customer is easier to retain. Strategies should be evaluated in future controlled retention pilots, including costs and complaints. Monthly charges are not profit or customer lifetime value.

Generated model outputs contain English labels and remain local, including customer-level predictions, split assignments, figures and the fitted pipeline. Report/PDF-generation scripts, report-specific dependencies, bilingual report outputs, local environments and caches are also excluded from this modelling contribution.

## Reproduce EDA

For tables and checks, Python 3.10+ and its standard library are sufficient:

```sh
python3 scripts/eda.py --tables-only
python3 scripts/verify_eda.py
python3 scripts/run_audit_notebook.py --stage eda
```

For figures, use a Python 3.12+ virtual environment and install the tested plotting versions:

```sh
python3 -m pip install -r requirements-eda.txt
python3 scripts/eda.py
```

- [EDA findings and limitations](reports/eda/eda.md)
- [Executed EDA notebook](notebooks/03_exploratory_analysis.ipynb)
- [Figure files in PNG and SVG](reports/eda/figures)
- [Category counts and rates](reports/eda/category_churn.csv)
- [Numeric summaries](reports/eda/numeric_summary.csv)
- [Numeric correlations and sample sizes](reports/eda/numeric_correlations.csv)

These are full-sample descriptive results, not causal estimates or held-out decision-tree performance. The EDA stage does not fit models or create segments; those outputs are kept separately in `reports/model/`.

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

- [Audit results](reports/audit/audit.md)
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
