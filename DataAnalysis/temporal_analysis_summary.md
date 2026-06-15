# Gibson Temporal Analysis

## Dataset

- Source file: `DataProcessing/gibson_papers_coded_codex.json`
- Total papers: 519
- Year range: 1990-2024
- Papers with unknown year: 7

## Main Temporal Pattern

- The annual volume peaks in 2022 with 108 papers.
- Topic diversity, measured as inverse HHI/effective topics, peaks in 2017 at 6.39 effective topics.
- Within the 2020s, the most concentrated observed year is 2024 at 1.0 effective topics.
- Cross-disciplinary papers account for 319 papers (61.5%) across the full corpus.

## Overall Topic and Method Centers

- Largest topic: T1 Customer experience / behavior (173 papers).
- Largest method: M5 Survey / SEM (170 papers).

## Pre-2020 to 2020-2024 Topic Shifts

| Direction | Code | Label | Change pp |
|---|---|---|---:|
| Rising | T1 | Customer experience / behavior | 8.57 |
| Rising | T8 | Resilience / capability | 4.99 |
| Rising | T7 | Performance / measurement / bibliometric review | 0.74 |
| Declining | T3 | Logistics / fulfillment | -9.68 |
| Declining | T4 | Inventory / operations / optimization | -3.04 |
| Declining | T2 | Omni-channel / multi-channel marketing | -2.54 |

## Pre-2020 to 2020-2024 Method Shifts

| Code | Label | Change pp |
|---|---|---:|
| M5 | Survey / SEM | 9.91 |
| M2 | Literature review | 1.6 |
| M4 | Case study / interview | 0.33 |

## Interpretive Note

- These metrics follow the logic of a field-evolution report: volume, concentration, effective category counts, rising/declining shares, method adoption, and cross-disciplinary integration.
- The available data do not contain citation links or semantic embeddings, so citation-flow, UMAP, and semantic-distance analyses are intentionally not estimated here.
