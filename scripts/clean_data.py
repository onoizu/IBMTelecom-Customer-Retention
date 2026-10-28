"""Preserve customers and expose missing charges. Standard library only."""
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
import csv
import hashlib
import io
import json

from audit_data import DOMAINS, ADDONS, table

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / 'data/processed'
REPORTS = ROOT / 'reports/cleaning'


def normalize_total_charges(raw_value):
    """Represent unknown charges explicitly without imputing a numeric value."""
    is_missing = raw_value.strip() == ''
    return ('' if is_missing else raw_value), ('1' if is_missing else '0')


def clean_rows(rows, fields):
    """Reject unexpected problems rather than silently dropping or fixing rows.

    CSV numbers retain their original lexical precision. Only TotalCharges
    blanks change to an empty field; a new binary indicator exposes missingness.
    """
    if len(fields) != len(set(fields)) or set(fields) != {'customerID', 'tenure', 'MonthlyCharges', 'TotalCharges', *DOMAINS}:
        raise ValueError('Unexpected raw schema')
    if not rows:
        raise ValueError('Empty input')
    seen, cleaned, changes = set(), [], []
    for line, row in enumerate(rows, 2):
        if set(row) != set(fields) or any(v is None for v in row.values()):
            raise ValueError(f'Malformed CSV at line {line}')
        customer = row['customerID']
        if not customer.strip() or customer != customer.strip() or customer in seen:
            raise ValueError(f'Missing, padded or duplicate ID at line {line}')
        seen.add(customer)
        for field, allowed in DOMAINS.items():
            if row[field] not in allowed:
                raise ValueError(f'Unexpected {field} at line {line}')
        missing = not row['TotalCharges'].strip()
        for field in ['tenure', 'MonthlyCharges', 'TotalCharges']:
            if field == 'TotalCharges' and missing:
                continue
            try:
                value = Decimal(row[field])
            except InvalidOperation as exc:
                raise ValueError(f'Invalid {field} at line {line}') from exc
            if not value.is_finite() or value < 0:
                raise ValueError(f'Nonfinite or negative {field} at line {line}')
            if field == 'tenure' and value != value.to_integral_value():
                raise ValueError(f'Fractional tenure at line {line}')
        if (row['PhoneService'] == 'No') != (row['MultipleLines'] == 'No phone service'):
            raise ValueError(f'Phone-service conflict at line {line}')
        for field in ADDONS:
            if (row['InternetService'] == 'No') != (row[field] == 'No internet service'):
                raise ValueError(f'Internet-service conflict at line {line}')
        result = dict(row)
        result['TotalCharges'], result['TotalChargesMissing'] = normalize_total_charges(row['TotalCharges'])
        if result['TotalCharges'] != row['TotalCharges']:
            changes.append({'csv_line': line, 'customerID': customer, 'field': 'TotalCharges',
                            'old_value_repr': repr(row['TotalCharges']), 'new_value_repr': repr(''),
                            'operation': 'whitespace_to_missing', 'reason': 'Unknown is not assumed to be zero'})
        cleaned.append(result)
    return cleaned, changes


def csv_bytes(rows, fields):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode('utf-8')


def main():
    manifest = json.loads((ROOT / 'data/raw/source_manifest.json').read_text())
    raw_path = ROOT / 'data/raw' / manifest['file']
    original = raw_path.read_bytes()
    raw_hash = hashlib.sha256(original).hexdigest()
    if raw_hash != manifest['sha256']:
        raise ValueError('Raw checksum mismatch; review the source before cleaning')
    reader = csv.DictReader(io.StringIO(original.decode('utf-8-sig')))
    rows, fields = list(reader), reader.fieldnames
    cleaned, changes = clean_rows(rows, fields)
    new_fields = fields + ['TotalChargesMissing']
    data = csv_bytes(cleaned, new_fields)
    reloaded = list(csv.DictReader(io.StringIO(data.decode())))
    if reloaded != cleaned or raw_path.read_bytes() != original:
        raise ValueError('CSV round-trip or raw preservation failed')
    for before, after in zip(rows, reloaded):
        for field in fields:
            expected = '' if field == 'TotalCharges' and not before[field].strip() else before[field]
            if after[field] != expected:
                raise ValueError(f'Unexpected change to {field}')
        if after['TotalChargesMissing'] != str(int(after['TotalCharges'] == '')):
            raise ValueError('Missingness indicator mismatch')
    missing = sum(r['TotalChargesMissing'] == '1' for r in cleaned)
    source_churn = Counter(r['Churn'] for r in rows)
    clean_churn = Counter(r['Churn'] for r in cleaned)
    if source_churn != clean_churn or len(rows) != len(cleaned):
        raise ValueError('Row or target counts changed')
    summary = {'input_rows': len(rows), 'output_rows': len(cleaned),
               'input_columns': len(fields), 'output_columns': len(new_fields),
               'deleted_rows': 0, 'imputed_values': 0, 'recoded_category_values': 0,
               'changed_original_cells': len(changes), 'missing_total_charges': missing,
               'added_indicator_cells': len(cleaned), 'indicator_ones': missing,
               'indicator_zeros': len(cleaned)-missing, 'churn_before': dict(source_churn),
               'churn_after': dict(clean_churn), 'raw_sha256': raw_hash,
               'clean_sha256': hashlib.sha256(data).hexdigest(),
               'checks': {'raw_unchanged': True, 'all_customers_retained_in_order': True,
                          'all_other_original_cells_unchanged': True, 'csv_round_trip': True,
                          'missingness_indicator_matches': True, 'target_counts_unchanged': True}}
    types = {c: 'categorical string' for c in fields}
    types.update(customerID='identifier string', tenure='nonnegative integer months',
                 MonthlyCharges='nonnegative decimal amount', TotalCharges='nullable nonnegative decimal amount',
                 TotalChargesMissing='binary integer flag')
    schema = {'file': 'telco_clean.csv', 'encoding': 'utf-8', 'delimiter': ',',
              'missing_representation': 'Empty CSV field, allowed only in TotalCharges',
              'columns': [{'name': c, 'semantic_type': types[c], 'nullable': c == 'TotalCharges'} for c in new_fields],
              'indicator_definition': '1 iff the source TotalCharges is empty after stripping whitespace; otherwise 0',
              'target': 'Churn', 'identifier': 'customerID',
              'note': 'CSV has no stored types. Parse numeric columns when loading; empty charges must not become zero.'}
    for directory in [PROCESSED, REPORTS]:
        directory.mkdir(parents=True, exist_ok=True)
    (PROCESSED / 'telco_clean.csv').write_bytes(data)
    (PROCESSED / 'schema.json').write_text(json.dumps(schema, indent=2) + '\n')
    (REPORTS / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (REPORTS / 'cell_changes.csv').write_bytes(csv_bytes(changes, ['csv_line', 'customerID', 'field', 'old_value_repr', 'new_value_repr', 'operation', 'reason']))
    operations = [['Raw records retained', len(cleaned)], ['Records deleted', 0],
                  ['Original TotalCharges cells normalized to missing', len(changes)], ['Values imputed', 0],
                  ['Original category values recoded', 0], ['New indicator values created', len(cleaned)],
                  ['Indicator = 1', missing], ['Indicator = 0', len(cleaned)-missing]]
    report = f'''# Stage 2 Cleaning Summary

The cleaned dataset retains all {len(cleaned):,} customers. Whitespace-only accumulated charges are represented as missing rather than assumed to be zero. No model preprocessing or train/test split is performed.

{table(['Operation', 'Count'], operations)}

## Decision and limitation

Retaining the records avoids removing every zero-tenure customer in this sample. A missing value communicates uncertainty; it does not resolve the billing amount. The 11 affected records have tenure=0 and Churn=No, but these attributes do not determine the cleaning rule. The rule depends only on the raw TotalCharges text.

The new TotalChargesMissing field equals 1 for missing charges and 0 otherwise. It is a data-quality indicator; its use as a model feature remains a decision for C, not an automatic recommendation. No tenure bands or service-count metrics are added.

## Loading contract

`data/processed/telco_clean.csv` contains {len(new_fields)} fields: the original {len(fields)} plus the indicator. An empty field in TotalCharges means missing, not zero. Numeric values were validated, but CSV does not store data types. Read `data/processed/schema.json` and explicitly parse numeric columns. With pandas, default NA parsing recognizes the empty field; with csv.DictReader it remains an empty string.

## Validation

All IDs and row order are retained. Every original cell except the listed whitespace-to-missing changes is unchanged. Service labels and Churn counts are preserved. CSV serialization round-trips successfully and indicator values agree with missingness. Details are in `summary.json` and `cell_changes.csv`.

Raw SHA-256: `{raw_hash}`

Clean SHA-256: `{summary['clean_sha256']}`

Rebuild with `python3 scripts/clean_data.py`. Course basis: BI2 p. 10 for missingness and consistency, pp. 43-53 for explicit coding definitions. Keeping unknown charges missing is the project's chosen treatment, not a mandated course rule.
'''
    (REPORTS / 'cleaning.md').write_text(report)
    print(f'CLEANING COMPLETE | {len(rows):,} -> {len(cleaned):,} rows | {len(fields)} -> {len(new_fields)} fields')
    print(f'Original cells changed: {len(changes)} | Deleted: 0 | Imputed: 0')
    print(f'TotalChargesMissing: 1={missing}, 0={len(cleaned)-missing}')
    print('Verified: raw preserved, all other cells unchanged, CSV round-trip, target counts unchanged.')


if __name__ == '__main__':
    main()
