# Stage 1 Validation Record

Checks performed on 2026-10-29:

1. Run the audit from outside the repository, using `/tmp`, to verify path independence.
2. Compare SHA-256 hashes of every audit output before and after a rerun: identical.
3. Verify the original CSV against its source manifest: raw bytes unchanged.
4. Independently count records, Yes labels and blank TotalCharges using CSV column positions: counts reconcile with the audit.
5. Verify that Yes and No labels sum to 7,043 records.
6. Run `git diff --check`: no whitespace errors in tracked changes.

Confirmed: 7,043 rows, 21 fields, 1,869 Yes labels, 5,174 No labels, 11 blank TotalCharges, zero duplicate IDs and zero exact duplicate rows. No violations were found in the specified category and service-dependency checks.

These checks establish reproducibility of the audit, not the absence of every potential business issue. Cleaning, modeling and final report/slides have not been completed.
