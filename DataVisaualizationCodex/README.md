# Gibson Data Visualization Codex

This folder contains a self-contained HTML visual report generated from the matrix and temporal-analysis outputs in `../DataAnalysis`.

The format is adapted from the report structure of `whatisstrategy.org/what_is_strategy.pdf`: research summary, managerial summary, numbered findings, figure notes, and print-oriented academic layout.

## Files

- `build_dashboard.py` rebuilds the visual report from the latest analysis outputs.
- `index.html` is the generated report and can be opened directly in a browser.

## Rebuild

From the repository workspace:

```bash
python3 BusinessAnalysis/DataVisaualizationCodex/build_dashboard.py
```

The dashboard uses:

- `topic_method_matrix.csv`
- `field_topic_matrix.csv`
- `field_method_matrix.csv`
- `year_topic_matrix.csv`
- `year_method_matrix.csv`
- `gibson_papers_coded_codex.json`

## Visualization Choices

The report now focuses on field evolution over time:

- annual volume growth and the 2022 publication peak
- topic concentration, dispersion, and reconsolidation using inverse-HHI effective categories
- pre-2020 versus 2020-2024 topic shifts
- pre-2020 versus 2020-2024 method shifts
- cross-disciplinary share over time

The appendix keeps the original matrix analysis inspectable through switchable heatmap tables.

## Required Analysis Files

In addition to the original matrix outputs, the report uses:

- `temporal_year_summary.csv`
- `temporal_period_topic_shares.csv`
- `temporal_period_method_shares.csv`
- `temporal_decade_topic_shares.csv`
- `temporal_decade_method_shares.csv`
- `temporal_topic_shift_pre2020_vs_2020s.csv`
- `temporal_method_shift_pre2020_vs_2020s.csv`
- `temporal_analysis_summary.md`
