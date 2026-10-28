# Stage 2 Validation Record

The cleaning pipeline and its verification script were executed on 2026-10-29.

- All 7,043 customer IDs and their order are preserved.
- Exactly 11 original cells change from a single space to an empty missing field, all in TotalCharges. Every other original cell remains unchanged.
- The new indicator has 11 ones and 7,032 zeros, matching missing charges exactly.
- The raw CSV SHA-256 still matches the source manifest.
- CSV serialization round-trips to the same records.
- Churn counts remain 1,869 Yes and 5,174 No; all 11 zero-tenure customers remain.
- Boundary checks preserve true zero, detect whitespace and demonstrate that the rule does not depend on Churn or tenure. Synthetic test records are used only in memory and never exported as project data.
- Malformed nonblank amounts, NaN, infinity, negative amounts, fractional tenure, duplicate IDs and inconsistent phone service are rejected.
- Five generated output files reproduce byte-for-byte when cleaning is rerun from outside the repository root.
- All three cells in the cleaning notebook executed successfully with saved actual outputs.

Run `python3 scripts/verify_cleaning.py` to repeat the preservation, boundary and reproducibility checks. The 11 unknown charges remain unknown; successful cleaning validation does not establish their true values or make the dataset immediately compatible with every model.
