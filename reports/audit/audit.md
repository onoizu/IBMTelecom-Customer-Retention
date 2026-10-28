# 第一阶段 原始数据审查

本阶段只检查数据，未删除、填补、编码或生成清洗后数据。

## 截图 A 数据概览

来源：https://www.kaggle.com/datasets/blastchar/telco-customer-churn

文件：`WA_Fn-UseC_-Telco-Customer-Churn.csv`。每行对应一个客户 ID。下载日期是获取日期，不是客户观察日期。

| 项目 | 结果 |
| --- | --- |
| 客户记录 | 7043 |
| 字段数 | 21 |
| 唯一客户 ID | 7043 |
| 完全重复行（不含首次） | 0 |
| 重复客户 ID（不含首次） | 0 |
| Churn = Yes | 1869 |
| Churn = No | 5174 |
| 样本中 Churn = Yes 比例 | 26.5370% |
| 空白 TotalCharges | 11 |
| 原始文件保持不变 | True |

## 截图 B 缺失值证据

“空白”包括空字符串及仅含空格的字符串。原始字符保留在 CSV；以下使用 repr 显示空格。

| CSV 行号（含表头） | customerID | tenure | MonthlyCharges | TotalCharges 原文 | Churn |
| --- | --- | --- | --- | --- | --- |
| 490 | 4472-LVYGI | 0 | 52.55 | ' ' | No |
| 755 | 3115-CZMZD | 0 | 20.25 | ' ' | No |
| 938 | 5709-LVOEQ | 0 | 80.85 | ' ' | No |
| 1084 | 4367-NUYAO | 0 | 25.75 | ' ' | No |
| 1342 | 1371-DWPAZ | 0 | 56.05 | ' ' | No |
| 3333 | 7644-OMVMY | 0 | 19.85 | ' ' | No |
| 3828 | 3213-VVOLG | 0 | 25.35 | ' ' | No |
| 4382 | 2520-SGTTA | 0 | 20 | ' ' | No |
| 5220 | 2923-ARZLG | 0 | 19.7 | ' ' | No |
| 6672 | 4075-WKNIU | 0 | 73.35 | ' ' | No |
| 6756 | 2775-SEFEE | 0 | 61.9 | ' ' | No |

空白值集中于 tenure 为 0 的客户，是值得进一步解释的模式；它本身不能证明累计费用必然为 0。

## 字段质量检查

CSV 没有原生数据类型。审查保留字符原文，数值检查只在内存中解析。

| 字段 | 原始唯一值数 | 空白数 | 空字符串数 | 首尾空白数 |
| --- | --- | --- | --- | --- |
| customerID | 7043 | 0 | 0 | 0 |
| gender | 2 | 0 | 0 | 0 |
| SeniorCitizen | 2 | 0 | 0 | 0 |
| Partner | 2 | 0 | 0 | 0 |
| Dependents | 2 | 0 | 0 | 0 |
| tenure | 73 | 0 | 0 | 0 |
| PhoneService | 2 | 0 | 0 | 0 |
| MultipleLines | 3 | 0 | 0 | 0 |
| InternetService | 3 | 0 | 0 | 0 |
| OnlineSecurity | 3 | 0 | 0 | 0 |
| OnlineBackup | 3 | 0 | 0 | 0 |
| DeviceProtection | 3 | 0 | 0 | 0 |
| TechSupport | 3 | 0 | 0 | 0 |
| StreamingTV | 3 | 0 | 0 | 0 |
| StreamingMovies | 3 | 0 | 0 | 0 |
| Contract | 3 | 0 | 0 | 0 |
| PaperlessBilling | 2 | 0 | 0 | 0 |
| PaymentMethod | 4 | 0 | 0 | 0 |
| MonthlyCharges | 1585 | 0 | 0 | 0 |
| TotalCharges | 6531 | 11 | 0 | 11 |
| Churn | 2 | 0 | 0 | 0 |

## 数值范围检查

| 字段 | 有效数值数 | 最小值 | 最大值 | 中位数 | 负值数 | 1.5 IQR 标记数 |
| --- | --- | --- | --- | --- | --- | --- |
| tenure | 7043 | 0.0 | 72.0 | 29.0 | 0 | 0 |
| MonthlyCharges | 7043 | 18.25 | 118.75 | 70.35 | 0 | 0 |
| TotalCharges | 7032 | 18.8 | 8684.8 | 1397.475 | 0 | 0 |

IQR 标记只用于初筛，不代表错误或删除依据。1.5 IQR 是补充检查规则，不声称课件要求使用此阈值。未设置来源未证实的费用上限。

## 类别与跨字段一致性

| 检查 | 违反规则的记录数 |
| --- | --- |
| gender 类别不在预期集合 | 0 |
| SeniorCitizen 类别不在预期集合 | 0 |
| Partner 类别不在预期集合 | 0 |
| Dependents 类别不在预期集合 | 0 |
| PhoneService 类别不在预期集合 | 0 |
| PaperlessBilling 类别不在预期集合 | 0 |
| Churn 类别不在预期集合 | 0 |
| MultipleLines 类别不在预期集合 | 0 |
| InternetService 类别不在预期集合 | 0 |
| OnlineSecurity 类别不在预期集合 | 0 |
| OnlineBackup 类别不在预期集合 | 0 |
| DeviceProtection 类别不在预期集合 | 0 |
| TechSupport 类别不在预期集合 | 0 |
| StreamingTV 类别不在预期集合 | 0 |
| StreamingMovies 类别不在预期集合 | 0 |
| Contract 类别不在预期集合 | 0 |
| PaymentMethod 类别不在预期集合 | 0 |
| phone_service_vs_multiple_lines | 0 |
| internet_service_vs_OnlineSecurity | 0 |
| internet_service_vs_OnlineBackup | 0 |
| internet_service_vs_DeviceProtection | 0 |
| internet_service_vs_TechSupport | 0 |
| internet_service_vs_StreamingTV | 0 |
| internet_service_vs_StreamingMovies | 0 |
| tenure_noninteger | 0 |

非空但无法转成有限数值的 CSV 行号：`{'tenure': [], 'MonthlyCharges': [], 'TotalCharges': []}`。

## 时间与分析边界

文件没有观察日期、入网日期或流失日期列。来源页面将 Churn 描述为最近一个月内离开，具体日历月份未核实。tenure 表示入网月数，不能当成日历时间序列。当前比例是该样本的标签比例，不能直接外推到真实企业或当前市场。尚未进行特征与 Churn 的关系分析。

## 可复现性

运行 `python3 scripts/audit_data.py` 重建审查输出。脚本首先核对原始文件 SHA-256：

`88be4b93fbe0cc83421af1c503794c97c342eca914c1576db7c276e61d61358a`

课堂依据：BI2 第 10 页（一致性与缺失检查）、第 43–53 页（编码与字典）、第 64–99 页（描述统计）；BI4 第 38 页（类别不平衡与测试数据）。具体规则及处理建议见 `docs/decision_log.md`。
