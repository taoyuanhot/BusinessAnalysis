# Gibson Data Visualization Codex

This folder contains a self-contained HTML visual report generated from the CSV matrices in `../DataAnalysis`.

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

The report focuses on four research-useful claims:

- the corpus is organized around customer, channel, and fulfillment questions
- evidence production is split between survey/SEM and operations-modeling traditions
- disciplinary ownership is strong but not complete
- empty topic-method cells identify research opportunity zones

The appendix keeps the underlying matrices inspectable through switchable heatmap tables.
