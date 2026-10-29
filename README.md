# IBM Telco Customer Retention

**Customer Churn Analysis and Interpretable Machine Learning**  
COMP3134 — BI-enabled CRM Group Project

## Project Overview

This project explores how customer data and interpretable machine learning can support retention planning for a telecommunications business. Using the IBM Telco Customer Churn dataset distributed through Kaggle, the project combines data auditing, cleaning, exploratory analysis and decision-tree modelling to identify patterns associated with churn and customer groups worth investigating for retention initiatives.

The analysis covers **7,043 customer records**. The focus is on producing transparent, reproducible findings that connect model outputs with practical CRM questions.

## Objectives

- Examine how customer characteristics, service subscriptions and account information relate to churn.
- Build an interpretable classification model to identify customers associated with higher churn risk.
- Translate decision-tree rules into understandable customer groups for retention planning.
- Assess model performance and the stability of the selected groups.

## Approach

### 1. Data Auditing and Cleaning

Preserved the original CSV and verified its integrity using SHA-256 checks. Audited missing values and service-category relationships, then produced a separate cleaned dataset retaining every customer record.

Eleven whitespace-only `TotalCharges` values were represented as missing and tracked through a `TotalChargesMissing` indicator. No customer records were removed, and no charge values were imputed during cleaning.

### 2. Exploratory Data Analysis

Produced six figure sets and supporting tables to examine customer profiles, churn patterns and relationships among numerical variables. Kept full-sample descriptive findings separate from model evaluation outputs.

### 3. Decision-Tree Modelling

Built a reproducible classification workflow using 18 predictors covering customer information, service subscriptions and account characteristics. Split the data into training, validation and test sets in a **60% / 20% / 20%** ratio, with stratification and a fixed random seed.

Fitted missing-value handling and one-hot encoding on training data within the modelling pipeline. Compared tree configurations through five-fold training cross-validation using average precision. The selected tree used a maximum depth of four and a minimum of 100 training customers per leaf. A separate classification threshold was selected using validation F1.

### 4. Customer Group Analysis

Selected three priority leaves based on training churn proportions, without using test labels to choose the groups:

- **New fibre customers on monthly contracts:** tenure of 0–1 months.
- **Early-tenure fibre customers on monthly contracts:** tenure of 2–15 months.
- **New DSL customers without the technical-support add-on:** monthly contracts and tenure of 0–3 months.

These groups identify areas for further investigation, such as onboarding support and early customer experience. They do not establish which retention action will work best.

## Results

At the validation-selected threshold, the model achieved the following results on the test split:

- **ROC-AUC:** 0.826
- **Average precision:** 0.600
- **Precision:** 53.8%
- **Recall:** 69.3%
- **Accuracy:** 76.1%

The model identified **259 of 374 observed churners**, while flagging 222 non-churners. Accuracy was interpreted alongside other metrics because predicting no churn for every customer would already achieve 73.5% accuracy.

The three priority groups contained **19.2% of test customers** and **47.9% of observed test churners**, concentrating a substantial share of churn cases into a smaller subset of customers.

## Stability and Interpretation

Conducted 20 refits on training subsamples to examine feature recurrence and group-membership stability. Contract, tenure, internet service and monthly charges appeared in every refit, while exact group boundaries varied. This supports recurring broad patterns rather than an identical tree structure across runs.

The dataset contains no dates or longitudinal customer histories. Earlier exploration had already inspected the test split, so the reported results should not be treated as a fresh, untouched final evaluation. Findings describe associations rather than causes, and the selected groups are neither calibrated individual future-risk estimates nor evidence of retention effectiveness.

## Deliverables

- Reproducible Python scripts for auditing, cleaning, EDA and decision-tree modelling.
- Executed audit, cleaning and exploratory-analysis notebooks.
- Data-quality reports, a cell-level change log and analysis decision documentation.
- Generated model outputs, including a tree diagram, segment profiles, evaluation metrics and stability results.

Audit, cleaning, EDA and modelling are complete. Generated model outputs remain local and can be reproduced by running the scripts. Final report prose, PDF-generation code and presentation slides are outside the scope of this contribution.

## Future Development

- Evaluate the model on new, time-stamped customer data.
- Compare alternative models while considering interpretability.
- Select operating thresholds using retention capacity and business costs.
- Test proposed retention actions through controlled pilots that measure outcomes, costs and customer complaints.

## Dataset

[IBM Telco Customer Churn — Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)

This is an academic group project using a public dataset; it does not imply a partnership with IBM or a deployment in a telecommunications business.
