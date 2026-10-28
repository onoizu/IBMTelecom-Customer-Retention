"""Reproducible descriptive EDA; no fitting, feature selection or causal claims."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import statistics as st
import sys
from audit_data import DOMAINS, table

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/eda'
NUMERIC = ['tenure', 'MonthlyCharges', 'TotalCharges']
LABELS = ['Tenure (months)', 'Monthly charges (source units)', 'Total charges (source units)']


def load_data():
    path = ROOT / 'data/processed/telco_clean.csv'
    content = path.read_bytes()
    expected = json.loads((ROOT / 'reports/cleaning/summary.json').read_text())['clean_sha256']
    if hashlib.sha256(content).hexdigest() != expected:
        raise ValueError('Cleaned data differs from the validated cleaning output')
    with path.open(newline='') as f:
        rows = list(csv.DictReader(f))
    return rows, content


def group_summary(rows, field):
    """Rate denominator is every customer in the category, not all churners."""
    results = []
    for category in DOMAINS[field]:
        group = [r for r in rows if r[field] == category]
        yes = sum(r['Churn'] == 'Yes' for r in group)
        results.append(dict(field=field, category=category, n=len(group), churn_yes=yes,
                            churn_no=len(group)-yes, churn_rate=yes/len(group) if group else None))
    return results


def write_csv(name, records):
    with (OUT / name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(records)


def calculate(rows):
    categories = [item for field in DOMAINS if field != 'Churn' for item in group_summary(rows, field)]
    numeric = []
    for field in NUMERIC:
        for label in ['All', 'No', 'Yes']:
            subset = [r for r in rows if label == 'All' or r['Churn'] == label]
            values = [float(r[field]) for r in subset if r[field] != '']
            q1, _, q3 = st.quantiles(values, n=4, method='inclusive')
            numeric.append(dict(field=field, churn_group=label, group_n=len(subset), valid_n=len(values),
                                missing_n=len(subset)-len(values), minimum=min(values), q1=q1,
                                median=st.median(values), mean=st.mean(values), q3=q3,
                                maximum=max(values), sample_std=st.stdev(values)))
    correlations = []
    for i, left in enumerate(NUMERIC):
        for right in NUMERIC[i+1:]:
            pairs = [(float(r[left]), float(r[right])) for r in rows if r[left] != '' and r[right] != '']
            correlations.append(dict(left=left, right=right, pair_n=len(pairs),
                                     excluded_n=len(rows)-len(pairs),
                                     pearson_r=st.correlation([a for a,b in pairs], [b for a,b in pairs])))
    return categories, numeric, correlations


def plot(rows, categories, correlations):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                         'axes.spines.right':False,'figure.facecolor':'white','savefig.facecolor':'white','svg.hashsalt':'telco-eda-v1'})
    colors = ['#287C8E', '#D16C4A']
    figures = OUT / 'figures'
    figures.mkdir(exist_ok=True)
    def save(fig, name):
        fig.savefig(figures / (name+'.png'), dpi=200)
        fig.savefig(figures / (name+'.svg'), metadata={'Date':None})
        plt.close(fig)
    counts = Counter(r['Churn'] for r in rows)
    fig, ax = plt.subplots(figsize=(7,4.5), layout='constrained')
    bars=ax.bar(['No','Yes'],[counts['No'],counts['Yes']],color=colors,width=.6)
    ax.set(title='Churn label distribution',ylabel='Customers',ylim=(0,6000))
    for bar,label in zip(bars,['No','Yes']):
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+100,
                f"n = {counts[label]:,}\n{counts[label]/len(rows):.2%}",ha='center')
    fig.supxlabel('Full customer sample, n = 7,043; descriptive labels, not a forecast',fontsize=9)
    save(fig,'01_churn_distribution')
    fig, axes = plt.subplots(1,3,figsize=(14,4.6),layout='constrained')
    for ax,field,label in zip(axes,NUMERIC,LABELS):
        values=[float(r[field]) for r in rows if r[field]!='']
        ax.hist(values,bins=12,color=colors[0],edgecolor='white')
        ax.set(xlabel=label,ylabel='Customers',title=f'n = {len(values):,}; missing = {len(rows)-len(values)}')
    fig.suptitle('Numeric distributions before modeling')
    fig.supxlabel('12 equal-width bins per variable; no imputation or outlier deletion',fontsize=9)
    save(fig,'02_numeric_distributions')
    fig,axes=plt.subplots(1,3,figsize=(14,4.6),layout='constrained')
    for ax,field,label in zip(axes,NUMERIC,LABELS):
        groups=[[float(r[field]) for r in rows if r['Churn']==g and r[field]!=''] for g in ['No','Yes']]
        boxes=ax.boxplot(groups,tick_labels=[f'No\nn={len(groups[0]):,}',f'Yes\nn={len(groups[1]):,}'],patch_artist=True)
        for box,color in zip(boxes['boxes'],colors):box.set_facecolor(color);box.set_alpha(.7)
        ax.set(ylabel=label,xlabel='Churn label')
    fig.suptitle('Numeric values by observed churn label')
    fig.supxlabel('Box: Q1–Q3; line: median; whiskers: 1.5 IQR; points beyond whiskers retained',fontsize=9)
    save(fig,'03_numeric_by_churn')
    overall=counts['Yes']/len(rows)
    def rate_panel(ax,field):
        data=[r for r in categories if r['field']==field]
        y=list(range(len(data)))
        ax.barh(y,[r['churn_rate'] for r in data],color=colors[0],height=.55)
        ax.set_yticks(y,[r['category'] for r in data]);ax.invert_yaxis()
        ax.set_xlim(0,.82);ax.xaxis.set_major_formatter(PercentFormatter(1))
        ax.axvline(overall,color=colors[1],ls='--',lw=1)
        ax.set_title(field,loc='left',fontweight='bold')
        ax.set_xlabel('Within-category Churn = Yes share')
        for pos,r in enumerate(data):
            ax.text(r['churn_rate']+.015,pos,f"{r['churn_rate']:.1%} ({r['churn_yes']:,}/{r['n']:,})",va='center',fontsize=9, bbox=dict(facecolor='white',edgecolor='none',pad=1))
    fig,axes=plt.subplots(1,2,figsize=(13,4.5),layout='constrained')
    for ax,field in zip(axes,['Contract','InternetService']):rate_panel(ax,field)
    fig.suptitle('Observed churn shares by contract and internet service')
    fig.supxlabel('Labels: Yes / all customers in category. Dashed line: overall 26.54%. Associations are not causal.',fontsize=9)
    save(fig,'04_contract_internet_churn')
    fields=['OnlineSecurity','OnlineBackup','DeviceProtection','TechSupport','StreamingTV','StreamingMovies']
    fig,axes=plt.subplots(3,2,figsize=(14,11),layout='constrained')
    for ax,field in zip(axes.flat,fields):rate_panel(ax,field)
    fig.suptitle('Observed churn shares by internet add-on status')
    fig.supxlabel('Labels: Yes / category total. No internet service is retained; repeated groups overlap across panels.\nDashed line: overall 26.54%. Differences may reflect customer mix, not service effects.',fontsize=10)
    save(fig,'05_service_churn')
    matrix=[[1.0 if i==j else 0 for j in range(3)] for i in range(3)]
    for r in correlations:
        i,j=NUMERIC.index(r['left']),NUMERIC.index(r['right']);matrix[i][j]=matrix[j][i]=r['pearson_r']
    fig,ax=plt.subplots(figsize=(7,5.5),layout='constrained')
    im=ax.imshow(matrix,vmin=-1,vmax=1,cmap='RdBu_r')
    ax.set_xticks(range(3),NUMERIC,rotation=20);ax.set_yticks(range(3),NUMERIC)
    for i in range(3):
        for j in range(3):
            count=sum(r[NUMERIC[i]] != '' and r[NUMERIC[j]] != '' for r in rows)
            ax.text(j,i,f'{matrix[i][j]:.3f}\nn={count:,}',ha='center',va='center',color='white' if abs(matrix[i][j])>.7 else 'black')
    fig.colorbar(im,ax=ax,label='Pearson r',shrink=.8)
    ax.set_title('Numeric correlations with pairwise sample sizes')
    fig.supxlabel('Pairwise complete observations; no imputation. IDs, category codes and Churn are excluded.',fontsize=9)
    save(fig,'06_numeric_correlations')


def main():
    rows, original = load_data()
    OUT.mkdir(parents=True,exist_ok=True)
    categories,numeric,correlations=calculate(rows)
    write_csv('category_churn.csv',categories)
    write_csv('numeric_summary.csv',numeric)
    write_csv('numeric_correlations.csv',correlations)
    count=Counter(r['Churn'] for r in rows)
    overview={'customers':len(rows),'churn_counts':dict(count),'churn_share':count['Yes']/len(rows),
              'clean_sha256':hashlib.sha256(original).hexdigest(), 'scope':'Full-sample descriptive EDA; not held-out model evaluation'}
    (OUT/'overview.json').write_text(json.dumps(overview,indent=2)+'\n')
    selected=[r for r in categories if r['field'] in ['Contract','InternetService','TechSupport']]
    report=f'''# Exploratory Data Analysis

This is Part B's full-sample descriptive exploration. Member C owns decision-tree training and evaluation; D owns model-informed customer profiles and final business insights. No features are selected, thresholds optimized or models fitted here.

## Population and denominators

The cleaned sample contains {len(rows):,} customers, including {count['Yes']:,} with Churn=Yes ({count['Yes']/len(rows):.2%}). Each categorical rate equals the Yes count divided by every customer in that category, not by all churners. Counts are provided to show group size.

TotalCharges uses 7,032 known values; its 11 unknown values are excluded only from calculations requiring that field. Those customers remain in all other applicable analyses. Numeric summaries report valid and missing counts by label.

## Selected descriptive comparisons

{table(['Field','Category','Yes','Group total','Within-group share'],[[r['field'],r['category'],r['churn_yes'],r['n'],f"{r['churn_rate']:.2%}"] for r in selected])}

These comparisons describe this sample. Contract and service differences may reflect tenure, customer mix or other factors. They do not establish that changing a contract or buying a service prevents churn. Refer to the complete category table for all original categorical fields.

## Numeric summaries by label

{table(['Field','Label','Valid n','Missing n','Median','Mean'],[[r['field'],r['churn_group'],r['valid_n'],r['missing_n'],f"{r['median']:.2f}",f"{r['mean']:.2f}"] for r in numeric])}

## Numeric relationships

{table(['Left','Right','Pair n','Excluded n','Pearson r'],[[r['left'],r['right'],r['pair_n'],r['excluded_n'],f"{r['pearson_r']:.3f}"] for r in correlations])}

Pearson coefficients describe linear association only. No significance tests or population inference are made. Nominal categories are not assigned arbitrary numbers for correlation. TotalCharges can accumulate with tenure, so their relationship is not automatically an independent churn driver or a reason to remove a feature from a decision tree.

## Method choices and limits

- BI2 pp. 64-99 supports descriptive statistics, frequencies and distributions. Twelve equal-width histogram bins are a display choice, not model features or a teacher-mandated threshold.
- Boxplots and Pearson correlation are project implementation choices for the assigned distribution and relationship checks; not every detail is mandated by the lectures.
- Raw category values and no-service states remain distinct. No tenure bands, fee bands or service counts are introduced without agreeing their definitions with C.
- No confidence intervals, p-values, causal conclusions or future-period performance are claimed. Calendar observation dates and sampling design are unavailable; fee units are not labeled as a verified currency.
- Full-sample relationships are descriptive. C should choose preprocessing and tune the decision tree using training/validation data and reserve test data for evaluation. These plots are not held-out evidence of predictive performance.

## Artifacts

CSV tables contain the underlying statistics. Six PNG/SVG figure pairs are in `figures/`. The executed notebook shows loading, grouped-rate calculations and denominator checks for process screenshots. See `docs/decision_log.md` for rationale and `docs/handoff_to_C.md` for modeling boundaries.
'''
    (OUT/'eda.md').write_text(report)
    if '--tables-only' not in sys.argv:plot(rows,categories,correlations)
    if (ROOT/'data/processed/telco_clean.csv').read_bytes()!=original:raise ValueError('EDA changed the input')
    print(f'EDA COMPLETE | {len(rows):,} customers | {len(categories)} category rows | {len(numeric)} numeric summaries')
    for r in group_summary(rows,'Contract'):
        print(f"{r['category']}: {r['churn_yes']}/{r['n']} = {r['churn_rate']:.2%}")
    print('Numeric correlations:',[(r['left'],r['right'],round(r['pearson_r'],3),r['pair_n']) for r in correlations])


if __name__=='__main__':main()
