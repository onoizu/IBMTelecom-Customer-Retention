"""Decision-tree modelling, three priority leaves and training-subsample stability."""
from pathlib import Path
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.cache' / 'matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME', str(ROOT / '.cache'))
os.environ.setdefault('OMP_NUM_THREADS', '1')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from joblib import dump
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
    confusion_matrix, f1_score, precision_recall_curve, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from threadpoolctl import threadpool_limits

threadpool_limits(limits=1)
SEED = 42
CHECK_SEEDS = list(range(100, 120))  # Fixed in advance; do not select the best seed.
OUT = ROOT / 'reports' / 'model'
OUT.mkdir(parents=True, exist_ok=True)

# 1. Read the validated cleaned data; unknown accumulated charges remain missing.
DATA = ROOT / 'data' / 'processed' / 'telco_clean.csv'
cleaning = json.loads((ROOT / 'reports/cleaning/summary.json').read_text())
manifest = json.loads((ROOT / 'data/raw/source_manifest.json').read_text())
source = {'repository': 'https://github.com/onoizu/IBMTelecom-Customer-Retention',
    'path': 'data/processed/telco_clean.csv', 'sha256': cleaning['clean_sha256'],
    'rows': cleaning['output_rows'], 'columns': cleaning['output_columns'],
    'dataset_page': manifest['dataset_page'], 'raw_sha256': manifest['sha256'],
    'cleaning_summary': 'reports/cleaning/summary.json'}
assert hashlib.sha256(DATA.read_bytes()).hexdigest() == source['sha256'], 'Review the changed data snapshot first.'
df = pd.read_csv(DATA)
for col in ['tenure', 'MonthlyCharges', 'TotalCharges']:
    df[col] = pd.to_numeric(df[col], errors='raise')
assert df['customerID'].is_unique and df['Churn'].isin(['Yes', 'No']).all()
assert df['TotalChargesMissing'].eq(df['TotalCharges'].isna().astype(int)).all()
num_cols = ['tenure', 'MonthlyCharges']
cat_cols = ['gender', 'SeniorCitizen', 'Partner', 'Dependents', 'PhoneService',
    'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
    'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies',
    'Contract', 'PaperlessBilling', 'PaymentMethod']
X = df[num_cols + cat_cols].copy()  # Exclude ID, target, accumulated charges and the audit indicator.
X[cat_cols] = X[cat_cols].astype(str)
y = df['Churn'].map({'No': 0, 'Yes': 1})

# 2. Keep the reference split; stability checks use training and validation customers only.
train_val, test = train_test_split(df.index, test_size=.2, stratify=y, random_state=SEED)
train, val = train_test_split(train_val, test_size=.25, stratify=y.loc[train_val], random_state=SEED)
X_train, X_val, X_test = X.loc[train], X.loc[val], X.loc[test]
y_train, y_val, y_test = y.loc[train], y.loc[val], y.loc[test]
splits = df[['customerID']].copy()
for name, idx in [('train', train), ('validation', val), ('test', test)]:
    splits.loc[idx, 'split'] = name
splits.to_csv(OUT / 'data_split.csv', index=False)
print(f'Train={len(train)}, validation={len(val)}, test={len(test)}', flush=True)

# 3. Select tree parameters within training folds; select the F1 threshold on validation data.
prep = ColumnTransformer([
    ('num', SimpleImputer(strategy='median'), num_cols),
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols)
], verbose_feature_names_out=False)
pipeline = Pipeline([('prep', prep), ('model', DecisionTreeClassifier(random_state=SEED))])
search = GridSearchCV(pipeline,
    {'model__max_depth': [2, 3, 4], 'model__min_samples_leaf': [50, 100, 200]},
    scoring='average_precision', cv=StratifiedKFold(5, shuffle=True, random_state=SEED), n_jobs=1)
search.fit(X_train, y_train)
model = search.best_estimator_
pd.DataFrame(search.cv_results_).to_csv(OUT / 'DT_cv.csv', index=False)
p_val = model.predict_proba(X_val)[:, 1]
precision, recall, candidate_thresholds = precision_recall_curve(y_val, p_val)
scores = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-12)
threshold = float(candidate_thresholds[np.flatnonzero(np.isclose(scores, scores.max()))[-1]])
print(f'DT: {search.best_params_}, CV AP={search.best_score_:.3f}', flush=True)

# Two helpers: consistent metrics and exact leaf-path rules.
def evaluate(actual, risk, threshold):
    predicted = risk >= threshold
    tn, fp, fn, tp = confusion_matrix(actual, predicted, labels=[0, 1]).ravel()
    budget = int(np.ceil(len(actual) * .2))
    cutoff = np.sort(risk)[-budget]
    above, tied = risk > cutoff, risk == cutoff
    captured = actual.to_numpy()[above].sum() + (budget - above.sum()) * actual.to_numpy()[tied].mean()
    return {'threshold': threshold, 'accuracy': accuracy_score(actual, predicted),
        'precision': precision_score(actual, predicted, zero_division=0),
        'recall': recall_score(actual, predicted), 'f1': f1_score(actual, predicted),
        'roc_auc': roc_auc_score(actual, risk), 'AP': average_precision_score(actual, risk),
        'brier': brier_score_loss(actual, risk), 'recall_at_20pct': captured / actual.sum(),
        'tn': int(tn), 'fp': int(fp), 'fn': int(fn), 'tp': int(tp)}


def get_rules(fitted):
    tree = fitted['model'].tree_
    names = fitted['prep'].get_feature_names_out()
    stack, rows = [(0, [])], []
    while stack:
        node, path = stack.pop()
        left, right = tree.children_left[node], tree.children_right[node]
        if left != right:
            feature, cut = names[tree.feature[node]], float(tree.threshold[node])
            stack += [(left, path + [(feature, '<=', cut)]), (right, path + [(feature, '>', cut)])]
        else:
            distribution = tree.value[node][0]
            rows.append({'leaf': node,
                'rule': ' AND '.join(f'{name} {op} {cut:.12g}' for name, op, cut in path),
                'conditions_json': json.dumps(path), 'train_n': int(tree.n_node_samples[node]),
                'train_churn_rate': float(distribution[1] / distribution.sum())})
    return pd.DataFrame(rows)


# 4. Select three priority leaves by training churn proportions, never test outcomes.
rules = get_rules(model)
priority = rules.sort_values(['train_churn_rate', 'train_n'], ascending=False).head(3).copy()
priority['segment_id'] = ['S1', 'S2', 'S3']
id_map = priority.set_index('leaf').segment_id.to_dict()
rules.to_csv(OUT / 'DT_rules.csv', index=False)

# 5. Refit fixed parameters on 80% training subsamples; compare on fixed validation customers.
# Match customer membership; node IDs are not comparable across refitted trees.
reference_leaves = model['model'].apply(model['prep'].transform(X_val))
reference_used = set()
for feature in model['model'].tree_.feature:
    if feature >= 0:
        encoded = model['prep'].get_feature_names_out()[feature]
        reference_used.add(next((c for c in cat_cols if encoded.startswith(c + '_')), encoded))
stability_runs, segment_matches, fitted_usage = [], [], []
for check_seed in CHECK_SEEDS:
    subset, _ = train_test_split(train, train_size=.8, stratify=y_train, random_state=check_seed)
    assert not set(subset).intersection(test)
    fitted = clone(model).set_params(model__random_state=check_seed).fit(X.loc[subset], y.loc[subset])
    names = fitted['prep'].get_feature_names_out()
    used = {next((c for c in cat_cols if names[f].startswith(c + '_')), names[f])
            for f in fitted['model'].tree_.feature if f >= 0}
    root = names[fitted['model'].tree_.feature[0]]
    root = next((c for c in cat_cols if root.startswith(c + '_')), root)
    p_check = fitted.predict_proba(X_val)[:, 1]
    leaves_check = fitted['model'].apply(fitted['prep'].transform(X_val))
    repeat_rules = get_rules(fitted).set_index('leaf')
    stability_runs.append({'seed': check_seed, 'training_n': len(subset), 'root_feature': root,
        'used_features': '|'.join(sorted(used)), 'validation_AP': average_precision_score(y_val, p_check),
        'validation_ROC_AUC': roc_auc_score(y_val, p_check),
        'agreement_with_reference': float(np.mean((p_check >= threshold) == (p_val >= threshold)))})
    fitted_usage.append((root, used))
    for group in priority.itertuples():
        reference = reference_leaves == group.leaf
        candidates = []
        for candidate in np.unique(leaves_check):
            match = leaves_check == candidate
            union = np.logical_or(reference, match).sum()
            overlap = np.logical_and(reference, match).sum() / union if union else np.nan
            candidates.append((overlap, int(candidate)))
        overlap, best_leaf = max(candidates)
        matched = repeat_rules.loc[best_leaf]
        segment_matches.append({'seed': check_seed, 'segment_id': group.segment_id,
            'reference_validation_n': int(reference.sum()),
            'matched_leaf': best_leaf, 'matched_validation_n': int((leaves_check == best_leaf).sum()),
            'membership_jaccard': overlap, 'matched_rule': matched.rule,
            'matched_conditions_json': matched.conditions_json,
            'matched_train_churn_rate': matched.train_churn_rate})
runs = pd.DataFrame(stability_runs)
matches = pd.DataFrame(segment_matches)
segment_stability = matches.groupby('segment_id', as_index=False).agg(
    repetitions=('seed', 'size'), mean_jaccard=('membership_jaccard', 'mean'),
    median_jaccard=('membership_jaccard', 'median'), min_jaccard=('membership_jaccard', 'min'),
    max_jaccard=('membership_jaccard', 'max'))
feature_stability = pd.DataFrame([{'feature': feature,
    'reference_tree_uses_feature': feature in reference_used,
    'used_runs': sum(feature in used for _, used in fitted_usage),
    'used_fraction': np.mean([feature in used for _, used in fitted_usage]),
    'root_runs': sum(root == feature for root, _ in fitted_usage)} for feature in X.columns])
runs.to_csv(OUT / 'stability_runs.csv', index=False)
matches.to_csv(OUT / 'stability_segment_matches.csv', index=False)
segment_stability.to_csv(OUT / 'segment_stability.csv', index=False)
feature_stability.to_csv(OUT / 'feature_stability.csv', index=False)
print(f'Stability check complete: {len(CHECK_SEEDS)} training-only refits; fixed validation and test customers.', flush=True)

# 6. Evaluate the reference model on test customers; test data do not select or match segments.
risk = model.predict_proba(X_test)[:, 1]
metrics = pd.DataFrame([evaluate(y_test, risk, threshold)], index=['DT'])
metrics.to_csv(OUT / 'metrics.csv', index_label='model')
pd.DataFrame([evaluate(y_test, risk, .5)], index=['DT']).to_csv(OUT / 'metrics_threshold_05.csv', index_label='model')
test_leaves = model['model'].apply(model['prep'].transform(X_test))
predictions = df.loc[test, ['customerID']].copy()
predictions['actual_churn'], predictions['DT_risk'] = y_test, risk
predictions['DT_prediction'], predictions['leaf'] = (risk >= threshold).astype(int), test_leaves
predictions['segment_id'] = pd.Series(test_leaves, index=X_test.index).map(id_map).fillna('Other')
predictions.to_csv(OUT / 'test_predictions.csv', index=False)
profile_data = X_test.copy().assign(leaf=test_leaves, churn=y_test)
profiles = profile_data.groupby('leaf').agg(n=('churn', 'size'), churn_count=('churn', 'sum'),
    churn_rate=('churn', 'mean'), tenure_median=('tenure', 'median'), monthly_charge_median=('MonthlyCharges', 'median'))
shares = pd.get_dummies(profile_data[cat_cols], prefix_sep='=').groupby(profile_data['leaf']).mean()
profiles = profiles.join(shares).reset_index().merge(rules, on='leaf')
profiles['segment_id'] = profiles.leaf.map(id_map).fillna('Other')
profiles.to_csv(OUT / 'DT_profiles.csv', index=False)

# Separate training/test counts; customers outside the three priority leaves remain Other.
segments = priority.merge(
    profiles[['leaf', 'n', 'churn_count', 'churn_rate', 'tenure_median', 'monthly_charge_median']], on='leaf')
segments = segments.rename(columns={'n': 'test_n', 'churn_count': 'test_churn_count', 'churn_rate': 'test_churn_rate',
    'tenure_median': 'test_tenure_median', 'monthly_charge_median': 'test_monthly_charge_median'})
segments = segments.merge(segment_stability[['segment_id', 'mean_jaccard', 'min_jaccard']], on='segment_id')
# Wilson intervals describe sample uncertainty, not intervention effects.
z = 1.959963984540054
n, p = segments.test_n, segments.test_churn_rate
center = (p + z*z/(2*n)) / (1 + z*z/n)
half = z * np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)
segments['test_rate_ci_low'], segments['test_rate_ci_high'] = center-half, center+half
segments['validation_n'] = [int((reference_leaves == leaf).sum()) for leaf in segments.leaf]
segments.to_csv(OUT / 'priority_segments.csv', index=False)

# 7. Raw-field permutation importance and English plots.
result = permutation_importance(model, X_test, y_test, scoring='average_precision',
                                n_repeats=5, random_state=SEED, n_jobs=1)
importance = pd.DataFrame({'feature': X.columns, 'AP_drop': result.importances_mean,
    'std': result.importances_std}).sort_values('AP_drop', ascending=False)
importance.to_csv(OUT / 'DT_importance.csv', index=False)
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
fig, ax = plt.subplots(figsize=(7, 5), layout='constrained')
precision, recall, _ = precision_recall_curve(y_test, risk)
ax.step(recall, precision, where='post', label=f'DT: AP={metrics.loc["DT", "AP"]:.3f}')
ax.axhline(y_test.mean(), ls='--', color='gray', label='Test churn proportion')
ax.set(xlabel='Recall (fraction)', ylabel='Precision (fraction)', title='Decision tree: test-set precision-recall')
ax.legend(); fig.savefig(OUT / 'performance.png', dpi=180); plt.close(fig)
feature_names = model['prep'].get_feature_names_out()
(OUT / 'decision_tree.txt').write_text(export_text(model['model'], feature_names=list(feature_names)), encoding='utf-8')
fig, ax = plt.subplots(figsize=(24, 10), layout='constrained')
plot_tree(model['model'], feature_names=feature_names, filled=True, node_ids=True, fontsize=8, precision=2, ax=ax)
ax.set_title('Training decision tree | value = [stayed, churned] | node IDs match DT_profiles.csv')
fig.savefig(OUT / 'decision_tree.png', dpi=180); plt.close(fig)
fig, ax = plt.subplots(figsize=(8, 5), layout='constrained')
top = importance.head(8).sort_values('AP_drop')
ax.barh(top.feature, top.AP_drop, xerr=top['std'], color='steelblue')
ax.set(title='DT: predictive feature importance', xlabel='Test AP decrease (mean +/- SD, 5 permutations)')
fig.savefig(OUT / 'feature_importance.png', dpi=180); plt.close(fig)
# 8. Save reproducibility metadata and the fitted pipeline; no report generation here.
summary = {'repetitions': len(CHECK_SEEDS), 'seeds': CHECK_SEEDS, 'training_fraction': .8,
    'fixed_validation_n': len(val), 'test_used_for_stability': False, 'hyperparameters_refitted': False,
    'validation_AP_mean': runs.validation_AP.mean(), 'validation_AP_std': runs.validation_AP.std(ddof=1),
    'membership_match': 'Best Jaccard overlap with one refitted leaf on fixed validation customers',
    'scope': 'Training-subsample sensitivity of a fixed specification; not independent folds or causal evidence'}
(OUT / 'run_info.json').write_text(json.dumps({'seed': SEED, 'parameters': search.best_params_,
    'threshold': threshold, 'cv_AP': search.best_score_, 'data_source': source, 'features': list(X.columns),
    'priority_selection': 'Top three leaves by training churn proportion; not test outcomes',
    'priority_leaf_ids': [int(x) for x in priority.leaf], 'stability': summary,
    'split_sizes': {'train': len(train), 'validation': len(val), 'test': len(test)},
    'versions': {'sklearn': sklearn.__version__, 'pandas': pd.__version__, 'numpy': np.__version__}},
    ensure_ascii=False, indent=2), encoding='utf-8')
dump({'pipeline': model, 'threshold': threshold, 'features': list(X.columns), 'source': source,
      'priority_segments': segments[['segment_id', 'leaf', 'rule']].to_dict('records')},
    OUT / 'decision_tree_model.joblib')
print(metrics[['accuracy', 'precision', 'recall', 'f1', 'roc_auc', 'AP']].round(4).to_string())
print(segment_stability[['segment_id', 'mean_jaccard', 'min_jaccard', 'max_jaccard']].round(3).to_string(index=False))
print(f'Model outputs saved to: {OUT}')
print('See README.md for model design, priority-group definitions and interpretation limits.')
