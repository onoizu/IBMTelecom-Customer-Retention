# 初版字段字典

本表覆盖原始 21 个字段。描述为项目使用的工作释义；精确年龄阈值、货币及日历观察期尚未核实。CSV 原文未编码。类别值来自实际文件；不把数字编码自动当作连续数量。

| 字段 | 工作含义 | 语义类型 | 实测值域 |
| --- | --- | --- | --- |
| customerID | 客户标识，用于追溯，不作为预测输入 | 标识 | 7,043 个唯一 ID |
| gender | 来源记录的性别类别 | 类别 | Female / Male |
| SeniorCitizen | 是否属于来源定义的年长客户；年龄阈值尚未核实 | 类别 | 0 / 1 |
| Partner | 是否有伴侣 | 类别 | No / Yes |
| Dependents | 是否有受抚养人 | 类别 | No / Yes |
| tenure | 客户入网时长，单位为月 | 数值（月数为整数，费用为金额） | 0 至 72 |
| PhoneService | 是否有电话服务 | 类别 | No / Yes |
| MultipleLines | 是否有多条电话线路 | 类别 | No / No phone service / Yes |
| InternetService | 互联网服务类型 | 类别 | DSL / Fiber optic / No |
| OnlineSecurity | 是否订购在线安全服务 | 类别 | No / No internet service / Yes |
| OnlineBackup | 是否订购在线备份服务 | 类别 | No / No internet service / Yes |
| DeviceProtection | 是否订购设备保护服务 | 类别 | No / No internet service / Yes |
| TechSupport | 是否订购技术支持服务 | 类别 | No / No internet service / Yes |
| StreamingTV | 是否订购电视流媒体服务 | 类别 | No / No internet service / Yes |
| StreamingMovies | 是否订购电影流媒体服务 | 类别 | No / No internet service / Yes |
| Contract | 合约期限类别 | 类别 | Month-to-month / One year / Two year |
| PaperlessBilling | 是否使用无纸账单 | 类别 | No / Yes |
| PaymentMethod | 付款方式 | 类别 | Bank transfer (automatic) / Credit card (automatic) / Electronic check / Mailed check |
| MonthlyCharges | 月度收费金额；货币单位未核实 | 数值（月数为整数，费用为金额） | 18.25 至 118.75 |
| TotalCharges | 累计收费金额；空白含义待处理，货币单位未核实 | 数值（月数为整数，费用为金额） | 18.8 至 8684.8；另有 11 个单空格 ' ' |
| Churn | 流失目标标签；来源页面摘要描述为最近一个月离开，具体月份未知 | 类别 | No / Yes |

## 后续编码与派生指标

- 二元 Yes/No 编码需明确映射；建议统一为 Yes=1、No=0，但当前尚未实施。
- SeniorCitizen 的 0/1 是类别标记，不是实际年龄。
- 无序多类别采用何种模型编码由清洗与建模阶段共同明确；参照 BI2 第 51–53 页的 one-hot 说明。
- Contract 即使具有期限顺序，也不能随意用 0/1/2 代表实际月数；模型编码应记录选择理由。
- No phone service / No internet service 是有含义的状态，不属于空白缺失。
- 暂无派生指标，避免在与 C 的交接口径未明确前生成不一致的分组或服务数量。
