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
    report = f'''# 第一阶段 原始数据审查

本阶段只检查数据，未删除、填补、编码或生成清洗后数据。

## 截图 A 数据概览

来源：{manifest['dataset_page']}

文件：`{source.name}`。每行对应一个客户 ID。下载日期是获取日期，不是客户观察日期。

{table(['项目', '结果'], [['客户记录', n], ['字段数', len(fields)], ['唯一客户 ID', n - duplicate_ids], ['完全重复行（不含首次）', duplicates], ['重复客户 ID（不含首次）', duplicate_ids], ['Churn = Yes', churn['Yes']], ['Churn = No', churn['No']], ['样本中 Churn = Yes 比例', f"{churn['Yes']/n:.4%}"], ['空白 TotalCharges', len(missing_total)], ['原始文件保持不变', summary['raw_unchanged']]])}

## 截图 B 缺失值证据

“空白”包括空字符串及仅含空格的字符串。原始字符保留在 CSV；以下使用 repr 显示空格。

{table(['CSV 行号（含表头）', 'customerID', 'tenure', 'MonthlyCharges', 'TotalCharges 原文', 'Churn'], [[r['csv_line'], r['customerID'], r['tenure'], r['MonthlyCharges'], repr(r['TotalCharges']), r['Churn']] for r in missing_total])}

空白值集中于 tenure 为 0 的客户，是值得进一步解释的模式；它本身不能证明累计费用必然为 0。

## 字段质量检查

CSV 没有原生数据类型。审查保留字符原文，数值检查只在内存中解析。

{table(['字段', '原始唯一值数', '空白数', '空字符串数', '首尾空白数'], profile)}

## 数值范围检查

{table(['字段', '有效数值数', '最小值', '最大值', '中位数', '负值数', '1.5 IQR 标记数'], [[c, v['nonmissing'], v['min'], v['max'], v['median'], v['negative'], v['iqr_flags']] for c, v in numeric.items()])}

IQR 标记只用于初筛，不代表错误或删除依据。1.5 IQR 是补充检查规则，不声称课件要求使用此阈值。未设置来源未证实的费用上限。

## 类别与跨字段一致性

{table(['检查', '违反规则的记录数'], [[f'{c} 类别不在预期集合', v] for c, v in invalid.items()] + list(consistency.items()))}

非空但无法转成有限数值的 CSV 行号：`{invalid_numeric}`。

## 时间与分析边界

文件没有观察日期、入网日期或流失日期列。来源页面将 Churn 描述为最近一个月内离开，具体日历月份未核实。tenure 表示入网月数，不能当成日历时间序列。当前比例是该样本的标签比例，不能直接外推到真实企业或当前市场。尚未进行特征与 Churn 的关系分析。

## 可复现性

运行 `python3 scripts/audit_data.py` 重建审查输出。脚本首先核对原始文件 SHA-256：

`{sha}`

课堂依据：BI2 第 10 页（一致性与缺失检查）、第 43–53 页（编码与字典）、第 64–99 页（描述统计）；BI4 第 38 页（类别不平衡与测试数据）。具体规则及处理建议见 `docs/decision_log.md`。
'''
    (OUT / 'audit.md').write_text(report)
    print(f'AUDIT COMPLETE | {n:,} rows | {len(fields)} columns')
    print(f'Duplicates: {duplicates} rows / {duplicate_ids} IDs | Blank TotalCharges: {len(missing_total)}')
    print(f'Churn Yes: {churn["Yes"]:,} ({churn["Yes"]/n:.4%}) | Raw unchanged: {summary["raw_unchanged"]}')
    print('Report: reports/audit/audit.md')


if __name__ == '__main__':
    main()
