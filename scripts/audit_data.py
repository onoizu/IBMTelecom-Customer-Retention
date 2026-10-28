"""Read-only raw-data audit. Python 3.10+, standard library only.

Run from any directory. Outputs are deterministic; raw CSV is never rewritten.
"""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import io
import json
import math
import statistics

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
OUT = ROOT / 'reports/audit'
NUMERIC = ['tenure', 'MonthlyCharges', 'TotalCharges']
ADDONS = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies']
DOMAINS = {
    'gender': ['Female', 'Male'], 'SeniorCitizen': ['0', '1'],
    **{c: ['Yes', 'No'] for c in ['Partner', 'Dependents', 'PhoneService', 'PaperlessBilling', 'Churn']},
    'MultipleLines': ['Yes', 'No', 'No phone service'],
    'InternetService': ['DSL', 'Fiber optic', 'No'],
    **{c: ['Yes', 'No', 'No internet service'] for c in ADDONS},
    'Contract': ['Month-to-month', 'One year', 'Two year'],
    'PaymentMethod': ['Electronic check', 'Mailed check', 'Bank transfer (automatic)', 'Credit card (automatic)'],
}


def table(headers, records):
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(map(cell, row)) + ' |' for row in records])


def main():
    manifest = json.loads((RAW / 'source_manifest.json').read_text())
    source = RAW / manifest['file']
    original = source.read_bytes()
    sha = hashlib.sha256(original).hexdigest()
    if sha != manifest['sha256']:
        raise ValueError('Raw file hash differs from the saved source manifest')
    reader = csv.DictReader(io.StringIO(original.decode('utf-8-sig')))
    rows = list(reader)
    fields = reader.fieldnames
    expected = {'customerID', *NUMERIC, *DOMAINS}
    if set(fields) != expected or len(fields) != len(expected):
        raise ValueError('Unexpected schema; review the dataset version before auditing')
    if not rows or any(None in r or None in r.values() for r in rows):
        raise ValueError('Empty data or malformed CSV row')
    n = len(rows)
    blank = {c: sum(not r[c].strip() for r in rows) for c in fields}
    profile = []
    for c in fields:
        profile.append([c, len({r[c] for r in rows}), blank[c],
                        sum(r[c] == '' for r in rows), sum(r[c] != r[c].strip() for r in rows)])
    categories = {c: dict(sorted(Counter(r[c] for r in rows).items())) for c in DOMAINS}
    invalid = {c: sum(r[c] not in allowed for r in rows) for c, allowed in DOMAINS.items()}
    numeric, invalid_numeric = {}, {}
    for c in NUMERIC:
        values, bad = [], []
        for i, r in enumerate(rows, 2):
            if not r[c].strip():
                continue
            try:
                v = float(r[c])
                if not math.isfinite(v):
                    raise ValueError()
                values.append(v)
            except ValueError:
                bad.append(i)
        if not values:
            raise ValueError(f'No numeric observations for {c}')
        q1, _, q3 = statistics.quantiles(values, n=4, method='inclusive')
        iqr = q3 - q1
        numeric[c] = {'nonmissing': len(values), 'min': min(values), 'max': max(values),
                      'mean': statistics.mean(values), 'median': statistics.median(values),
                      'q1': q1, 'q3': q3, 'negative': sum(v < 0 for v in values),
                      'iqr_flags': sum(v < q1 - 1.5 * iqr or v > q3 + 1.5 * iqr for v in values)}
        invalid_numeric[c] = bad
    consistency = {
        'phone_service_vs_multiple_lines': sum((r['PhoneService'] == 'No') != (r['MultipleLines'] == 'No phone service') for r in rows),
        **{f'internet_service_vs_{c}': sum((r['InternetService'] == 'No') != (r[c] == 'No internet service') for r in rows) for c in ADDONS},
        'tenure_noninteger': sum(float(r['tenure']) % 1 != 0 for r in rows if r['tenure'].strip()),
    }
    duplicates = n - len({tuple(r[c] for c in fields) for r in rows})
    duplicate_ids = n - len({r['customerID'] for r in rows})
    missing_total = [dict(csv_line=i, **r) for i, r in enumerate(rows, 2) if not r['TotalCharges'].strip()]
    churn = Counter(r['Churn'] for r in rows)
    summary = {'rows': n, 'columns': len(fields), 'sha256': sha, 'blank_cells': blank,
               'exact_duplicate_rows_excluding_first': duplicates,
               'duplicate_customer_ids_excluding_first': duplicate_ids,
               'invalid_categories': invalid, 'invalid_numeric_csv_lines': invalid_numeric,
               'numeric_summary': numeric, 'consistency_violations': consistency,
               'churn_counts': dict(churn), 'churn_share': churn['Yes'] / n,
               'missing_total_charges_tenure_counts': dict(Counter(r['tenure'] for r in missing_total)),
               'missing_total_charges_churn_counts': dict(Counter(r['Churn'] for r in missing_total)),
               'zero_tenure_rows': sum(r['tenure'] == '0' for r in rows),
               'raw_unchanged': source.read_bytes() == original}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
    (OUT / 'category_counts.json').write_text(json.dumps(categories, indent=2) + '\n')
    with (OUT / 'missing_total_charges.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['csv_line'] + fields)
        writer.writeheader()
        writer.writerows(missing_total)
    report = f'''# Stage 1 Raw Data Audit

This stage only inspects the data. No records have been deleted, imputed, encoded or exported as cleaned data.

## Data overview

Source: {manifest['dataset_page']}

File: `{source.name}`. Each row corresponds to a customer ID. The download date is not the observation date.

{table(['Item', 'Result'], [['Customer records', n], ['Fields', len(fields)], ['Unique customer IDs', n - duplicate_ids], ['Exact duplicate rows beyond the first', duplicates], ['Duplicate customer IDs beyond the first', duplicate_ids], ['Churn = Yes', churn['Yes']], ['Churn = No', churn['No']], ['Sample share with Churn = Yes', f"{churn['Yes']/n:.4%}"], ['Blank TotalCharges', len(missing_total)], ['Raw file unchanged', summary['raw_unchanged']]])}

## Missing value evidence

Blank includes empty strings and whitespace-only strings. The original CSV is preserved; repr exposes spaces below.

{table(['CSV line including header', 'customerID', 'tenure', 'MonthlyCharges', 'TotalCharges raw representation', 'Churn'], [[r['csv_line'], r['customerID'], r['tenure'], r['MonthlyCharges'], repr(r['TotalCharges']), r['Churn']] for r in missing_total])}

Blank charges are concentrated among customers with tenure zero. This pattern alone does not establish that their accumulated charges equal zero.

## Field quality checks

CSV has no native data types. The audit preserves original strings and parses numerical values only in memory.

{table(['Field', 'Distinct raw values', 'Blank values', 'Empty strings', 'Leading or trailing whitespace'], profile)}

## Numeric range checks

{table(['Field', 'Valid numeric values', 'Minimum', 'Maximum', 'Median', 'Negative values', '1.5 IQR flags'], [[c, v['nonmissing'], v['min'], v['max'], v['median'], v['negative'], v['iqr_flags']] for c, v in numeric.items()])}

IQR flags are screening indicators, not proof of error or a reason for automatic deletion. The 1.5 IQR threshold is a supplementary implementation choice, not a stated course requirement. No unsupported upper charge limit is imposed.

## Categories and cross-field consistency

{table(['Check', 'Violating records'], [[f'{c}: outside expected categories', v] for c, v in invalid.items()] + list(consistency.items()))}

CSV lines containing nonblank values that cannot be parsed as finite numbers: `{invalid_numeric}`.

## Time scope and analysis limitations

The file has no observation, joining or churn date columns. The source page describes Churn as leaving within the last month; the calendar month has not been verified. Tenure is duration in months, not a calendar time series. The reported share describes this sample and cannot be directly generalized to a real business or the current market. Feature relationships with Churn have not yet been analysed.

## Reproducibility

Run `python3 scripts/audit_data.py` to rebuild the audit outputs. The script first verifies the raw SHA-256:

`{sha}`

Course references: BI2 p. 10 (consistency and missing values), pp. 43-53 (coding and dictionaries), pp. 64-99 (descriptive statistics); BI4 p. 38 (class imbalance and test data). See `docs/decision_log.md` for rules and proposed treatments. For screenshots of executable work, use `notebooks/01_raw_data_audit.ipynb` and `docs/screenshots.md`.
'''
    (OUT / 'audit.md').write_text(report)
    print(f'AUDIT COMPLETE | {n:,} rows | {len(fields)} columns')
    print(f'Duplicates: {duplicates} rows / {duplicate_ids} IDs | Blank TotalCharges: {len(missing_total)}')
    print(f'Churn Yes: {churn["Yes"]:,} ({churn["Yes"]/n:.4%}) | Raw unchanged: {summary["raw_unchanged"]}')
    print('Report: reports/audit/audit.md')


if __name__ == '__main__':
    main()
