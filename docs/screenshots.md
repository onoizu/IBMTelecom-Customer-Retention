# Screenshots of Executed Work

Capture the code and its actual output together. A screenshot of a written conclusion or decision log is not evidence of execution. GitHub already retains commit history; no commit screenshot is required.

## Stage 1 notebook

Open `notebooks/01_raw_data_audit.ipynb` in a notebook editor such as VS Code or Jupyter. Saved outputs were produced by actually executing the cells with `python3 scripts/run_audit_notebook.py`, a sequential Python runner rather than a Jupyter kernel. GitHub displays saved code and output but does not execute them. To demonstrate your own run, select a Python kernel and run the cells in order, or run that command in your terminal. The notebook code uses the Python standard library only.

1. **Load and inspect**: capture the code cell under `1. Load the original CSV` and its output. Include the file read, row/column count, first three records and raw checksum verification. This shows what was loaded and how its integrity was checked.
2. **Investigate blanks**: capture the code cell under `2. Investigate TotalCharges blanks` and its output. Include the comparison between empty-string detection and whitespace-aware detection, the affected records and their tenure/churn counts. The output distinguishes a space from zero using repr.
3. **Verify reproducibility**: capture the code cell under `3. Rerun the audit and verify preservation` with its output. Include the actual script invocation and the assertions comparing raw and output hashes.

On macOS, press Shift+Command+4 and select the code plus output area. Keep the cell execution number and section title visible. If a cell and its output do not fit legibly, use two overlapping screenshots rather than hiding code or shrinking text excessively.

Suggested filenames: `01_load_and_inspect.png`, `02_investigate_blanks.png`, `03_verify_reproducibility.png`. Saved notebook outputs document a run performed with Codex assistance; do not describe them as a personal execution unless you rerun the notebook yourself.

The audit Markdown remains useful as a result summary, and the decision log preserves rationale. Neither is the primary process screenshot.

## Stage 2 cleaning checkpoints

Open `notebooks/02_data_cleaning.ipynb`. Its saved outputs come from actual execution using `python3 scripts/run_audit_notebook.py --stage cleaning`.

1. **Transformation and execution**: capture section 1 code and output, including the printed normalization function and actual cleaning counts. This shows the implemented rule rather than a prose conclusion.
2. **Before and after**: capture section 2 code and its table of 11 affected customers. Keep the raw `' '`, cleaned `''`, indicator and tenure visible. The empty string is the documented missing representation, not zero.
3. **Verification**: capture section 3 assertions and output, showing that only the intended cells changed, real zero is preserved and the original file checksum still matches. Use two screenshots if needed for legibility.

Suggested filenames: `04_cleaning_rule_and_run.png`, `05_cleaning_before_after.png`, `06_cleaning_verification.png`. Capturing the first two is sufficient for a compact process record; keep the notebook for full validation evidence. No Git history screenshot is needed.

## Later stage checkpoints

- Cleaning: show the implemented transformation, affected counts and checks in the same view.
- EDA: show the grouping or calculation code and resulting chart/table; state denominators.
- Export high-resolution figures for report/slides separately from process screenshots.
- Capture later stages only after the corresponding operations have actually run.

## Stage 3 EDA checkpoints

Open `notebooks/03_exploratory_analysis.ipynb`. The outputs were actually generated with `python3 scripts/run_audit_notebook.py --stage eda`.

1. Capture section 1 code and output: filtering each contract category, counting Yes labels, dividing by group size, and the resulting three rates. This demonstrates the calculation and denominator choice.
2. Capture section 2 code and output: missing-aware numeric summaries and the complete-pair correlation calculation. Keep valid/missing counts visible.
3. Section 3 verifies category totals, independent correlations and reproducibility. Capture it if validation evidence is needed.

Use `07_eda_group_rates.png` and `08_eda_missing_denominators.png`. For report/slides, use the exported figure files directly rather than screenshotting chart previews. A figure alone does not replace the code-and-output process record.
