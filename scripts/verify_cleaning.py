"""Independently verify exported cleaning results and fail-closed input checks."""
from pathlib import Path
import csv
import hashlib
import json
import subprocess
import sys
from clean_data import clean_rows

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT / 'data/raw/source_manifest.json').read_text())
    source = ROOT / 'data/raw' / manifest['file']
    raw = list(csv.DictReader(source.open(newline='')))
    result_path = ROOT / 'data/processed/telco_clean.csv'
    result = list(csv.DictReader(result_path.open(newline='')))
    assert len(raw) == len(result) == 7043
    assert [r['customerID'] for r in raw] == [r['customerID'] for r in result]
    changes = []
    for before, after in zip(raw, result):
        for field in before:
            if before[field] != after[field]:
                changes.append((before['customerID'], field, before[field], after[field]))
        assert after['TotalChargesMissing'] == ('1' if after['TotalCharges'] == '' else '0')
    assert len(changes) == 11
    assert all(field == 'TotalCharges' and old == ' ' and new == '' for _, field, old, new in changes)
    assert sum(r['Churn'] == 'Yes' for r in result) == 1869
    assert sum(r['tenure'] == '0' for r in result) == 11
    assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest['sha256']

    # A real zero must remain zero. Missing detection must not use the target.
    zero = dict(raw[0], TotalCharges='0')
    unknown = dict(raw[0], TotalCharges=' ', Churn='Yes', tenure='12')
    for item, expected_value, expected_flag in [(zero, '0', '0'), (unknown, '', '1')]:
        cleaned, _ = clean_rows([item], list(item))
        assert cleaned[0]['TotalCharges'] == expected_value
        assert cleaned[0]['TotalChargesMissing'] == expected_flag

    # Unexpected numeric values, duplicates and inconsistent services must fail.
    bad_cases = [[dict(raw[0], TotalCharges=value)] for value in ['invalid', 'NaN', '-1', 'Infinity']]
    bad_cases += [[dict(raw[0], tenure='1.5')], [raw[0], raw[0]],
                  [dict(raw[0], PhoneService='Yes', MultipleLines='No phone service')]]
    for case in bad_cases:
        try:
            clean_rows(case, list(raw[0]))
        except ValueError:
            pass
        else:
            raise AssertionError('Unexpected input was silently accepted')
    paths = [*sorted((ROOT / 'data/processed').glob('*')), *sorted((ROOT / 'reports/cleaning').glob('*'))]
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    subprocess.run([sys.executable, str(ROOT / 'scripts/clean_data.py')], cwd=ROOT / 'docs', check=True)
    assert before == {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    print('VERIFIED: exactly 11 original cells changed; all 7,043 customers retained.')
    print('VERIFIED: zero is preserved, missingness is target-independent, invalid inputs fail.')
    print(f'VERIFIED: {len(paths)} generated files reproduce byte-for-byte from outside the repository root.')


if __name__ == '__main__':
    main()
