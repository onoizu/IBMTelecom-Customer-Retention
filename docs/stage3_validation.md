# Stage 3 EDA Validation

The EDA tables and notebook were executed on 2026-10-29.

- Every categorical field reconciles to 7,043 customers and 1,869 Yes labels, with rates independently checked against grouped counts.
- Numeric valid/missing counts, means and medians were independently reconciled to the cleaned CSV.
- Pearson coefficients were independently recomputed with the centered-product formula and agree within 1e-12.
- All five table/report files reproduce byte-for-byte when rerun outside the repository root. The cleaned input hash is unchanged.
- Six PNG/SVG figure pairs were generated. Each PNG was visually inspected for readable labels, counts and missing-value notes. Rate labels have white backgrounds to avoid intersection with the reference line.
- Full-sample descriptive results are not held-out decision-tree evaluation or causal evidence.

Run `python3 scripts/verify_eda.py` for table verification. Install `requirements-eda.txt` to regenerate figures. Numerical tables and the text-output notebook require only the Python standard library.
