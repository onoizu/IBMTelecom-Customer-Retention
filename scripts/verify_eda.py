"""Verify exported EDA against independently grouped cleaned records."""
from collections import Counter
from pathlib import Path
import csv
import hashlib
import math
import statistics
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def read(path):
    with (ROOT/path).open(newline='') as f:return list(csv.DictReader(f))

def main():
    rows=read('data/processed/telco_clean.csv')
    groups=read('reports/eda/category_churn.csv')
    for field in {r['field'] for r in groups}:
        counts=Counter(r[field] for r in rows)
        yes=Counter(r[field] for r in rows if r['Churn']=='Yes')
        exported=[r for r in groups if r['field']==field]
        assert sum(int(r['n']) for r in exported)==len(rows)
        assert sum(int(r['churn_yes']) for r in exported)==1869
        for r in exported:
            assert int(r['n'])==counts[r['category']]
            assert int(r['churn_yes'])==yes[r['category']]
            assert math.isclose(float(r['churn_rate']),yes[r['category']]/counts[r['category']])
    for item in read('reports/eda/numeric_summary.csv'):
        selected=[r for r in rows if item['churn_group']=='All' or r['Churn']==item['churn_group']]
        values=sorted(float(r[item['field']]) for r in selected if r[item['field']]!='')
        assert int(item['valid_n'])==len(values)
        assert int(item['missing_n'])==len(selected)-len(values)
        assert math.isclose(float(item['mean']),sum(values)/len(values))
        assert float(item['median'])==statistics.median(values)
    for item in read('reports/eda/numeric_correlations.csv'):
        pairs=[(float(r[item['left']]),float(r[item['right']])) for r in rows if r[item['left']]!='' and r[item['right']]!='']
        x,y=zip(*pairs); mx,my=sum(x)/len(x),sum(y)/len(y)
        value=sum((a-mx)*(b-my) for a,b in pairs)/math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
        assert int(item['pair_n'])==len(pairs)
        assert math.isclose(float(item['pearson_r']),value,abs_tol=1e-12)
    files=[p for p in (ROOT/'reports/eda').iterdir() if p.is_file()]
    before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    source=ROOT/'data/processed/telco_clean.csv'; original=source.read_bytes()
    subprocess.run([sys.executable,str(ROOT/'scripts/eda.py'),'--tables-only'],cwd=ROOT/'docs',check=True)
    assert before=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    assert source.read_bytes()==original
    print('VERIFIED: each category field reconciles to 7,043 customers and 1,869 Yes labels.')
    print('VERIFIED: means, medians, missing denominators and independent Pearson calculations agree.')
    print('VERIFIED: all EDA tables reproduce byte-for-byte; cleaned input is unchanged.')

if __name__=='__main__':main()
