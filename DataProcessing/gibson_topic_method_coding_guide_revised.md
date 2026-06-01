# Topic and Method Coding Guide for Gibson Papers

## 0. Source Basis

The JSON contains these main fields:

- Marketing
- Management Science & Operations Research
- Supply Chain Management
- Information Systems & Management
- Business School (Unclassified)
- Quantitative Methods
- Consumer Psychology
- Operations Management
- Strategy & Organization

The most frequent sub-fields include:

- Consumer Behavior
- Omni-Channel & Multi-Channel Marketing
- Logistics & Fulfillment
- Omni-Channel Retailing (General)
- Optimization Models
- Customer Experience & Loyalty
- E-Commerce & Information Systems
- Inventory Management
- Mixed Methods Research
- Consumer Decision-Making Process
- Digital Transformation
- Logistics & Distribution Networks
- Pricing & Promotion Strategy
- Bibliometric Analysis

Therefore, the categories below are not a generic business taxonomy. They are a simplified coding taxonomy designed for this Gibson papers corpus.

---

# 1. Topic Category

Use one primary topic category for each paper.

## Topic Category Codebook

| Code | Topic category |判斷標準 |
|---|---|---|
| T1 | Customer experience / behavior | 消費者旅程、滿意度、忠誠、購買意圖、channel choice、consumer behavior、consumer decision-making |
| T2 | Omni-channel / multi-channel marketing | omni-channel marketing、multi-channel marketing、promotion、pricing、retail marketing、channel integration、customer touchpoints |
| T3 | Logistics / fulfillment | 配送、last-mile、BOPS、click-and-collect、returns、delivery options、fulfillment、distribution networks、reverse logistics |
| T4 | Inventory / operations / optimization | 庫存、補貨、order allocation、retail operations、pricing model、assortment planning、mathematical decision model |
| T5 | Digital technology / information systems | 平台、資訊系統、e-commerce、mobile、AI、machine learning、IoT、data analytics、digital transformation |
| T6 | Strategy / business model / organization | 商業模式、business model innovation、omnichannel transformation、strategic integration、implementation strategy、channel integration strategy |
| T7 | Performance / measurement / bibliometric review | KPI、performance framework、evaluation model、assessment system、bibliometric analysis、literature mapping、research trend analysis |
| T8 | Resilience / capability | supply chain resilience、dynamic capabilities、organizational capability、collaboration、flexibility、redundancy、disruption response、recovery、crisis response |

---

## Topic Classification Rule

Each paper should receive only one primary topic category.

Use this order:

1. Read the title.
2. Read the abstract’s research purpose.
3. Identify the paper’s main outcome, dependent variable, or research object.
4. If still unclear, read the conclusion and identify the stated contribution.
5. Select the topic that best represents the paper’s main research problem.

If a paper discusses multiple topics, choose the topic it mainly tries to explain, model, or evaluate. Do not classify based on background terms only.

---

## Topic Examples

| Paper content | Topic category |
|---|---|
| customer satisfaction, purchase intention, loyalty, consumer behavior | T1 Customer experience / behavior |
| omni-channel promotion, channel integration, multi-channel retail marketing | T2 Omni-channel / multi-channel marketing |
| BOPS, delivery, last-mile, returns, fulfillment networks | T3 Logistics / fulfillment |
| inventory strategy, pricing model, order allocation, Stackelberg game, optimization | T4 Inventory / operations / optimization |
| information systems, e-commerce platform, AI, IoT, mobile technology, data analytics | T5 Digital technology / information systems |
| retailer transformation, business model innovation, strategic integration, channel integration strategy | T6 Strategy / business model / organization |
| KPI, performance metric, assessment framework, bibliometric mapping, research trends | T7 Performance / measurement / bibliometric review |
| supply chain resilience, dynamic capabilities, organizational capability, collaboration, flexibility, redundancy, disruption response, recovery | T8 Resilience / capability |

---

## Topic Boundary Notes

### T6 vs. T8

Use **T6** when the paper focuses on strategy, business model, transformation, implementation, or channel integration strategy.

Use **T8** when the paper focuses on resilience, organizational capability, dynamic capability, disruption response, crisis response, recovery, flexibility, redundancy, or collaboration capability.

Do not assign T6 only because a paper proposes a framework. Assign T6 only when the framework concerns strategy, business model, transformation, or implementation.

### T3 vs. T4

Use **T3** when the research object is logistics or fulfillment: last-mile delivery, BOPS, BORIS/BORS, returns, reverse logistics, fulfillment network, delivery options, distribution network, routing, or shipping.

Use **T4** when the research object is inventory, order quantity, replenishment, pricing decision, assortment planning, channel competition, game-theoretic decisions, or operational optimization.

If a fulfillment/logistics paper uses optimization, classify it by the research object, not only by the method. For example, a last-mile routing optimization paper should usually be T3, while an inventory-pricing game model should usually be T4.

---

# 2. Method Category

Use one primary method category for each paper.

## Method Category Codebook

| Code | Method category | 判斷標準 |
|---|---|---|
| M1 | Conceptual framework | 主要提出概念架構、分類架構、propositions，沒有實證或數學模型 |
| M2 | Literature review | 主要整理既有文獻，包括 narrative review、systematic review、synthesized review |
| M3 | Bibliometric analysis | 使用 citation、keyword、co-occurrence、co-citation、VOSviewer、SciMAT、network visualization |
| M4 | Case study / interview | 使用案例、訪談、質性資料、multiple case study |
| M5 | Survey / SEM | 問卷、PLS-SEM、SEM、consumer survey、structural model |
| M6 | Experiment | scenario experiment、online experiment、lab experiment、field experiment |
| M7 | Optimization / simulation / game model | 數學模型、optimization、simulation、game theory、Stackelberg、inventory model、routing model |
| M8 | Statistical / econometric modeling | regression、panel data、transaction data、econometric model、choice model、logit model、propensity score matching、Markov chain、probabilistic model、panel model、stochastic frontier analysis |
| M9 | Mixed methods | 明確結合質性與量化方法，例如 case + survey、interview + SEM、sequential mixed methods |

---

## Method Classification Rule

If a paper uses multiple methods, choose the dominant method used to produce the main findings.

Use this order:

1. If the paper explicitly says mixed methods and uses both qualitative and quantitative stages, choose M9 Mixed methods.
2. If it uses optimization, game theory, simulation, routing, or inventory models, choose M7 Optimization / simulation / game model.
3. If it uses SEM, PLS-SEM, or survey-based structural modeling, choose M5 Survey / SEM.
4. If it uses regression, panel data, transaction data, logit / choice models, propensity score matching, Markov chain, probabilistic models, panel models, or stochastic frontier analysis, choose M8 Statistical / econometric modeling.
5. If it uses scenario, lab, online, or field experiments, choose M6 Experiment.
6. If it uses citation, keyword, co-occurrence, VOSviewer, SciMAT, or bibliometric mapping, choose M3 Bibliometric analysis.
7. If it mainly uses cases, interviews, or qualitative evidence, choose M4 Case study / interview.
8. If it mainly reviews literature without bibliometric tools, choose M2 Literature review.
9. If it mainly proposes a conceptual framework without empirical testing, choose M1 Conceptual framework.

---

# 3. Suggested Coding Fields

For each paper, create one row with these fields:

| Field | Description |
|---|---|
| paper_id | Unique paper ID |
| title | Paper title |
| publication_year | Publication year |
| main_field | Main field from JSON |
| sub_field | Sub-field from JSON |
| cross_disciplinary_fields | Cross-disciplinary fields from JSON |
| cross_count | Number of cross-disciplinary fields |
| topic_category | Coded primary topic category |
| method_category | Coded primary method category |
| coding_confidence | 1 = uncertain, 2 = mostly certain, 3 = certain |

---

# 4. Coding Confidence

Use `coding_confidence` to mark uncertainty.

| Score | Meaning |
|---:|---|
| 1 | Uncertain; needs review |
| 2 | Mostly certain |
| 3 | Clear classification |

Only papers with `coding_confidence = 1` need detailed checking later.

---

# 5. Coding Quality Check

After coding each batch of papers, check these items:

1. Confirm that all resilience, capability, disruption-response, and recovery papers are coded as **T8**, not T6.
2. Confirm that logistics-object papers are coded as **T3**, even when they use optimization methods.
3. Confirm that inventory, pricing, assortment, channel competition, and operational decision-model papers are coded as **T4**.
4. Confirm that M8 is labeled **Statistical / econometric modeling**, not Regression / econometric analysis.
5. Recheck all papers with `coding_confidence = 1` or `coding_confidence = 2`.

---

# 6. Short Method Statement

Each paper is assigned one primary topic category and one primary method category. The topic category is based on the paper’s central research problem, while the method category is based on the dominant research design used to produce the main findings. When multiple topics or methods appear, the category most central to the paper’s research objective is selected. Resilience, capability, disruption-response, and recovery papers are separated into T8 rather than merged into general strategy papers. The categories are adjusted from the observed fields and sub-fields in the Gibson papers metadata rather than from a general business taxonomy.
