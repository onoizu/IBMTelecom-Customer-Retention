# 数据来源与版本

本项目使用小组讨论指定的 [BlastChar Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)。实际文件直接从 Kaggle 下载，没有用其他仓库的文件替换，也没有使用他人的清洗代码或分析结果。

- 下载接口：https://www.kaggle.com/api/v1/datasets/download/blastchar/telco-customer-churn
- 下载包内文件：`WA_Fn-UseC_-Telco-Customer-Churn.csv`
- 本次获取的 CSV：977,501 字节，7,043 行数据、21 个字段。
- 版本：Kaggle 元数据报告为 1；最后更新时间为 2018-02-23。该更新时间不是数据观察日期。
- 取得时间及 SHA-256：见 `data/raw/source_manifest.json`。
- 原始元数据：见 `data/raw/kaggle_metadata.json`，其中许可标签为 `Data files © Original Authors`。不要把该标签改写成我们拥有数据版权或随意指定开源许可证。
- 保留方式：从 ZIP 按字节提取 CSV，保留 CRLF、空格、原始字段顺序与值；审查不重写 CSV。

数据源页面检索结果将 Churn 描述为最近一个月内离开的客户；完整页面正文未能通过文本浏览器提取，因此其他细节不假装已核实。课件与笔记中的 IBM 数据集名称用于识别该教学数据集，不将它描述成我们取得的真实电信企业运营记录。

## 时间与业务边界

每行是一个唯一客户 ID。文件没有观察日期、入网日期、具体流失日期或按月重复观测；当前按客户横截面样本理解。`tenure` 是客户已入网月数，不是月份日期。无法从此文件确定具体观察月份或重建日历时间序列。

费用货币单位、SeniorCitizen 的准确年龄阈值、具体地域和抽样方案尚未从本版本的完整数据说明核实；报告不擅自补充。没有成本数据，费用字段不能直接等同利润或客户终身价值。

## 来源复取

已提交的原始 CSV 和校验值足以本地重建审查结果。若重新下载，应先放到临时目录并比较 SHA-256，不能直接覆盖 `data/raw/`。若来源版本变化，应建立新版本记录，再重新审查。

本次查阅了 IBM 的公开示例仓库作为来源背景，但没有使用其数据、模型或分析流程。最终数据文件来自上述 Kaggle 地址。
