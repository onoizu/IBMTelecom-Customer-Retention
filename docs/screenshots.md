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

## Later stages

- Cleaning: show the implemented transformation, affected counts and checks in the same view.
- EDA: show the grouping or calculation code and resulting chart/table; state denominators.
- Export high-resolution figures for report/slides separately from process screenshots.
- Capture later stages only after the corresponding operations have actually run.
