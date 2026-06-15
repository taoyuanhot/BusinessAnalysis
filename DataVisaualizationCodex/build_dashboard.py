import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "DataAnalysis"
DATA_FILE = ROOT / "DataProcessing" / "gibson_papers_coded_codex.json"
OUT_DIR = ROOT / "DataVisaualizationCodex"
OUT_FILE = OUT_DIR / "index.html"


TOPIC_LABELS = {
    "T1": "Customer experience / behavior",
    "T2": "Omni-channel / multi-channel marketing",
    "T3": "Logistics / fulfillment",
    "T4": "Inventory / operations / optimization",
    "T5": "Digital technology / information systems",
    "T6": "Strategy / business model / organization",
    "T7": "Performance / measurement / bibliometric review",
    "T8": "Resilience / capability",
}


METHOD_LABELS = {
    "M1": "Conceptual framework",
    "M2": "Literature review",
    "M3": "Bibliometric analysis",
    "M4": "Case study / interview",
    "M5": "Survey / SEM",
    "M6": "Experiment",
    "M7": "Optimization / simulation / game model",
    "M8": "Statistical / econometric modeling",
    "M9": "Mixed methods",
}


MATRIX_FILES = {
    "topic_method": {
        "title": "Topic x Method",
        "file": "topic_method_matrix.csv",
        "row_label": "Topic",
        "note": "Counts show how each substantive topic is methodologically organized.",
    },
    "field_topic": {
        "title": "Field x Topic",
        "file": "field_topic_matrix.csv",
        "row_label": "Main field",
        "note": "Counts show which fields own each topic and where cross-field spillovers appear.",
    },
    "field_method": {
        "title": "Field x Method",
        "file": "field_method_matrix.csv",
        "row_label": "Main field",
        "note": "Counts show methodological specialization by field.",
    },
    "year_topic": {
        "title": "Year x Topic",
        "file": "year_topic_matrix.csv",
        "row_label": "Year",
        "note": "Counts show the changing topical composition of the corpus.",
    },
    "year_method": {
        "title": "Year x Method",
        "file": "year_method_matrix.csv",
        "row_label": "Year",
        "note": "Counts show the changing methodological composition of the corpus.",
    },
}


def read_json(path):
    with path.open() as f:
        return json.load(f)


def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def convert(value):
    if value == "":
        return None
    try:
        if "." in value:
            return float(value)
        return int(value)
    except (TypeError, ValueError):
        return value


def converted_csv(path):
    return [{key: convert(value) for key, value in row.items()} for row in read_csv(path)]


def read_matrix(path):
    rows = read_csv(path)
    first_col = list(rows[0])[0]
    columns = [col for col in rows[0] if col not in (first_col, "Total")]
    body = []
    totals = {}
    for row in rows:
        name = row[first_col]
        values = {col: int(row[col] or 0) for col in columns}
        total = int(row["Total"] or 0)
        if name == "Total":
            totals = {**values, "Total": total}
        else:
            body.append({"name": name, "values": values, "total": total})
    return {"columns": columns, "rows": body, "totals": totals}


def top_counts(rows, key):
    counts = {}
    for row in rows:
        value = row.get(key) or "Unknown"
        counts[value] = counts.get(value, 0) + 1
    return [{"name": name, "count": count} for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]


def dominant_cells(matrix, n=10):
    cells = []
    for row in matrix["rows"]:
        for col, value in row["values"].items():
            cells.append({"row": row["name"], "col": col, "count": value})
    return sorted(cells, key=lambda item: item["count"], reverse=True)[:n]


def matrix_zeros(matrix):
    zeros = []
    for row in matrix["rows"]:
        for col, value in row["values"].items():
            if value == 0:
                zeros.append({"row": row["name"], "col": col})
    return zeros


def make_data():
    rows = read_json(DATA_FILE)
    matrices = {}
    for key, config in MATRIX_FILES.items():
        matrices[key] = {**config, **read_matrix(ANALYSIS_DIR / config["file"])}

    years = [int(row["publication_year"]) for row in rows if str(row.get("publication_year", "")).isdigit()]
    annual = converted_csv(ANALYSIS_DIR / "temporal_year_summary.csv")
    topic_shift = converted_csv(ANALYSIS_DIR / "temporal_topic_shift_pre2020_vs_2020s.csv")
    method_shift = converted_csv(ANALYSIS_DIR / "temporal_method_shift_pre2020_vs_2020s.csv")
    topic_period = converted_csv(ANALYSIS_DIR / "temporal_period_topic_shares.csv")
    method_period = converted_csv(ANALYSIS_DIR / "temporal_period_method_shares.csv")
    topic_decade = converted_csv(ANALYSIS_DIR / "temporal_decade_topic_shares.csv")
    method_decade = converted_csv(ANALYSIS_DIR / "temporal_decade_method_shares.csv")

    return {
        "source": "DataProcessing/gibson_papers_coded_codex.json",
        "totalPapers": len(rows),
        "uniquePapers": len({row["paper_id"] for row in rows}),
        "yearRange": [min(years), max(years)],
        "unknownYears": sum(1 for row in rows if not str(row.get("publication_year", "")).isdigit()),
        "topicLabels": TOPIC_LABELS,
        "methodLabels": METHOD_LABELS,
        "topicFrequency": top_counts(rows, "topic_category"),
        "methodFrequency": top_counts(rows, "method_category"),
        "fieldFrequency": top_counts(rows, "main_field"),
        "annual": annual,
        "topicShift": topic_shift,
        "methodShift": method_shift,
        "topicPeriod": topic_period,
        "methodPeriod": method_period,
        "topicDecade": topic_decade,
        "methodDecade": method_decade,
        "matrices": matrices,
        "dominantTopicMethod": dominant_cells(matrices["topic_method"]),
        "topicMethodZeros": matrix_zeros(matrices["topic_method"]),
    }


def render_html(data):
    data_json = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>What Is Omni-channel Research?</title>
  <style>
    :root {
      --text: #111;
      --muted: #555;
      --rule: #d4d4d4;
      --light-rule: #ececec;
      --page: #fff;
      --blue: #1f77b4;
      --orange: #ff7f0e;
      --green: #2ca02c;
      --red: #d62728;
      --purple: #9467bd;
      --brown: #8c564b;
      --pink: #e377c2;
      --gray: #7f7f7f;
      --cyan: #17becf;
      font-family: Georgia, "Times New Roman", Times, serif;
      color-scheme: light;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: #f5f5f5;
      color: var(--text);
    }

    .page {
      width: min(100%, 1020px);
      min-height: 100vh;
      margin: 0 auto;
      padding: 44px 62px 72px;
      background: var(--page);
      box-shadow: 0 0 28px rgba(0, 0, 0, 0.08);
    }

    header {
      text-align: center;
      border-bottom: 1px solid var(--rule);
      margin-bottom: 24px;
      padding-bottom: 22px;
    }

    h1 {
      margin: 0 0 14px;
      font-size: 2.6rem;
      line-height: 1.08;
      font-weight: 500;
      letter-spacing: 0;
    }

    .authors, .site {
      font-size: 1.02rem;
      line-height: 1.45;
    }

    .site {
      color: var(--muted);
      margin-top: 4px;
    }

    h2 {
      margin: 28px 0 10px;
      font-size: 1rem;
      text-transform: uppercase;
      letter-spacing: 0.02em;
      font-weight: 700;
    }

    h3 {
      margin: 26px 0 10px;
      font-size: 1.25rem;
      line-height: 1.25;
      font-weight: 700;
    }

    p {
      margin: 0 0 12px;
      font-size: 1.02rem;
      line-height: 1.58;
    }

    .summary-block {
      border-bottom: 1px solid var(--light-rule);
      margin-bottom: 17px;
      padding-bottom: 14px;
    }

    .keywords, .note, .footer {
      color: var(--muted);
      font-size: 0.88rem;
      line-height: 1.45;
    }

    .metrics {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin: 18px 0 24px;
      border-top: 1px solid var(--rule);
      border-bottom: 1px solid var(--rule);
      padding: 12px 0;
    }

    .metric { text-align: center; min-width: 0; }

    .metric-value {
      font-family: Arial, Helvetica, sans-serif;
      font-weight: 700;
      font-size: 1.8rem;
      line-height: 1.1;
    }

    .metric-label {
      margin-top: 5px;
      color: var(--muted);
      font-family: Arial, Helvetica, sans-serif;
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .figure {
      margin: 18px 0 28px;
      border-top: 1px solid var(--rule);
      padding-top: 12px;
    }

    .figure-title, .table-title {
      margin-bottom: 8px;
      font-weight: 700;
      font-size: 0.96rem;
    }

    .chart-wrap, .table-scroll { overflow-x: auto; }

    svg {
      display: block;
      width: 100%;
      height: auto;
      background: white;
      font-family: Arial, Helvetica, sans-serif;
    }

    .chart { min-width: 820px; }

    .two-col {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      align-items: start;
    }

    .legend {
      display: flex;
      flex-wrap: wrap;
      gap: 6px 13px;
      margin-top: 8px;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 0.78rem;
    }

    .legend-item {
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }

    .swatch {
      width: 12px;
      height: 10px;
      border: 1px solid rgba(0,0,0,0.12);
      display: inline-block;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 0.82rem;
    }

    th, td {
      border-bottom: 1px solid var(--light-rule);
      padding: 7px 8px;
      text-align: right;
      vertical-align: top;
    }

    th:first-child, td:first-child { text-align: left; }
    thead th { border-bottom: 1px solid var(--text); font-weight: 700; }
    tbody tr:last-child td { border-bottom: 1px solid var(--text); }

    .matrix-toolbar {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-end;
      margin: 8px 0 10px;
    }

    .tabs {
      display: flex;
      flex-wrap: wrap;
      justify-content: flex-end;
      gap: 6px;
      font-family: Arial, Helvetica, sans-serif;
    }

    button {
      border: 1px solid #888;
      border-radius: 0;
      background: white;
      color: #111;
      padding: 5px 8px;
      font: inherit;
      font-size: 0.76rem;
      cursor: pointer;
    }

    button.active { background: #111; color: white; }

    .heatmap { min-width: 820px; }
    .heatmap td.cell { color: #111; font-weight: 700; font-variant-numeric: tabular-nums; }
    .heatmap td.zero { color: #aaa; font-weight: 400; background: #fafafa !important; }

    .shift-table td:nth-child(4), .shift-table td:nth-child(7) {
      font-weight: 700;
    }

    .gap-list {
      columns: 2;
      column-gap: 28px;
      margin: 0;
      padding-left: 20px;
      font-size: 0.94rem;
      line-height: 1.5;
    }

    .change-list {
      margin: 8px 0 0;
      padding-left: 20px;
      font-size: 1rem;
      line-height: 1.55;
    }

    .change-list li {
      margin-bottom: 7px;
    }

    .footer {
      border-top: 1px solid var(--rule);
      margin-top: 34px;
      padding-top: 12px;
    }

    @media print {
      body { background: white; }
      .page { box-shadow: none; padding: 28px 42px; }
      button { display: none; }
      .chart-wrap, .table-scroll { overflow: visible; }
    }

    @media (max-width: 780px) {
      .page { padding: 28px 20px 46px; box-shadow: none; }
      h1 { font-size: 2rem; }
      .metrics, .two-col { grid-template-columns: 1fr; }
      .matrix-toolbar { display: block; }
      .tabs { justify-content: flex-start; margin-top: 10px; }
      .gap-list { columns: 1; }
    }
  </style>
</head>
<body>
  <article class="page">
    <header>
      <h1>What Is Omni-channel Research?</h1>
      <div class="authors">A temporal and matrix analysis of the Gibson coded paper corpus</div>
      <div class="site">BusinessAnalysis/DataVisaualizationCodex</div>
    </header>

    <section>
      <div class="summary-block">
        <h2>Research Summary</h2>
        <p id="researchSummary"></p>
      </div>
      <div class="summary-block">
        <h2>Managerial Summary</h2>
        <p id="managerialSummary"></p>
      </div>
      <div class="keywords" id="keywords"></div>
    </section>

    <section class="metrics" aria-label="Dataset metrics">
      <div class="metric"><div class="metric-value" id="metricPapers"></div><div class="metric-label">Papers</div></div>
      <div class="metric"><div class="metric-value" id="metricPeak"></div><div class="metric-label">Peak year</div></div>
      <div class="metric"><div class="metric-value" id="metricDiversity"></div><div class="metric-label">Max effective topics</div></div>
      <div class="metric"><div class="metric-value" id="metricCross"></div><div class="metric-label">Cross-field share</div></div>
    </section>

    <section>
      <h2>Introduction</h2>
      <p>This report reframes the coded corpus as a field-evolution problem. The central question is no longer only which topics and methods dominate, but how the field changes over time: where volume accelerates, where topical concentration rises or falls, which methods gain share, and whether the corpus becomes more cross-disciplinary.</p>
      <p>The analysis follows the logic of a computational field map while staying within the available data. The current corpus supports time-series counts, concentration metrics, period shifts, method evolution, and field integration. It does not contain citation links or paper embeddings, so citation-flow and semantic-space claims are intentionally left out.</p>
    </section>

    <section>
      <h2>Data and Methods</h2>
      <p id="dataMethods"></p>
      <div class="figure">
        <div class="figure-title">Figure 1: Sample Composition by Topic Over Time.</div>
        <div class="chart-wrap">
          <svg id="sampleChart" class="chart" viewBox="0 0 920 370" role="img" aria-label="Stacked bar chart of topics over time"></svg>
        </div>
        <div id="topicLegend" class="legend"></div>
        <div class="note">Note: Stacked bars show topic counts by publication year. Unknown publication years are excluded from this figure but retained in aggregate counts.</div>
      </div>
    </section>

    <section>
      <h2>Findings</h2>

      <h3>Finding 1: The field grows sharply after 2018 and peaks in 2022.</h3>
      <p id="findingOne"></p>
      <div class="figure">
        <div class="figure-title">Figure 2: Annual Paper Volume.</div>
        <svg id="volumeChart" viewBox="0 0 900 280" role="img" aria-label="Annual paper volume"></svg>
        <div class="note">Note: The line reports annual paper counts. Sparse early years should be read cautiously because several years have only one to four papers.</div>
      </div>

      <div class="figure">
        <div class="figure-title">Figure 2b: Percentage Power Distribution by Topic.</div>
        <div class="chart-wrap">
          <svg id="shareChart" class="chart" viewBox="0 0 920 340" role="img" aria-label="Percentage stacked bar chart of topic shares over time"></svg>
        </div>
        <div class="note">Note: Each annual bar sums to 100 percent. This view separates field composition from annual publication volume.</div>
      </div>

      <h3>Finding 2: The corpus disperses during formation, then reconsolidates around fewer effective topics in the 2020s.</h3>
      <p id="findingTwo"></p>
      <div class="figure">
        <div class="figure-title">Figure 3: Field Structure Over Time.</div>
        <svg id="structureChart" viewBox="0 0 900 320" role="img" aria-label="Effective topics and effective methods over time"></svg>
        <div id="structureLegend" class="legend"></div>
        <div class="note">Note: Effective topics and methods are inverse-HHI measures. Higher values indicate a more even distribution across categories; lower values indicate concentration.</div>
      </div>

      <h3>Finding 3: The substantive center shifts from logistics/operations toward customer experience and resilience.</h3>
      <p id="findingThree"></p>
      <div class="figure">
        <div class="figure-title">Figure 4: Pre-2020 vs 2020-2024 Topic Share Change.</div>
        <svg id="topicShiftChart" viewBox="0 0 900 360" role="img" aria-label="Topic share shift before and after 2020"></svg>
        <div class="note">Note: Values are percentage-point changes in topic share from pre-2020 papers to papers published in 2020-2024.</div>
      </div>

      <h3>Finding 4: Methodological change is visible: survey/SEM rises while conceptual framing declines.</h3>
      <p id="findingFour"></p>
      <div class="figure">
        <div class="figure-title">Figure 5: Pre-2020 vs 2020-2024 Method Share Change.</div>
        <svg id="methodShiftChart" viewBox="0 0 900 380" role="img" aria-label="Method share shift before and after 2020"></svg>
        <div class="note">Note: This is a method-evolution analogue to the causal-method tables in the reference report, but uses the method categories available in this corpus.</div>
      </div>

      <h3>Finding 5: Cross-disciplinary work remains substantial and becomes especially visible in recent years.</h3>
      <p id="findingFive"></p>
      <div class="figure">
        <div class="figure-title">Figure 6: Cross-Disciplinary Share Over Time.</div>
        <svg id="crossChart" viewBox="0 0 900 280" role="img" aria-label="Cross-disciplinary share over time"></svg>
        <div class="note">Note: A paper is counted as cross-disciplinary when its coded cross_count is greater than zero.</div>
      </div>

      <h3>Notable temporal changes.</h3>
      <p>The most unusual changes are not all in the largest categories. The list below highlights shifts that are large, abrupt, or strategically meaningful for interpreting the field.</p>
      <ul id="notableChanges" class="change-list"></ul>
    </section>

    <section>
      <h2>Tables</h2>
      <div class="figure">
        <div class="table-title">Table 1: Rising and Declining Topics, Pre-2020 vs 2020-2024.</div>
        <div class="table-scroll"><table id="topicShiftTable" class="shift-table"></table></div>
      </div>
      <div class="figure">
        <div class="table-title">Table 2: Methodology Evolution, Pre-2020 vs 2020-2024.</div>
        <div class="table-scroll"><table id="methodShiftTable" class="shift-table"></table></div>
      </div>
      <div class="figure">
        <div class="table-title">Table 3: Topic Distribution by Period.</div>
        <div class="table-scroll"><table id="topicPeriodTable"></table></div>
      </div>
    </section>

    <section>
      <h2>Matrix Appendix</h2>
      <p>The original matrix analysis is retained as an appendix. These tables show the structural cross-sections behind the temporal patterns above.</p>
      <div class="figure">
        <div class="matrix-toolbar">
          <div>
            <div class="figure-title" id="matrixTitle">Table A1: Topic x Method Matrix.</div>
            <div class="note" id="matrixNote"></div>
          </div>
          <div id="matrixTabs" class="tabs" aria-label="Matrix selector"></div>
        </div>
        <div class="table-scroll">
          <table id="matrixTable" class="heatmap"></table>
        </div>
      </div>

      <div class="figure">
        <div class="table-title">Table A2: Topic-Method Zero Cells.</div>
        <ol id="gapList" class="gap-list"></ol>
        <div class="note">Note: Zero cells are candidates for research opportunities, not proof that the combination is theoretically impossible.</div>
      </div>
    </section>

    <div class="footer">
      Generated from <span id="sourceFile"></span> and the temporal analysis files in DataAnalysis. The report structure follows the style of whatisstrategy.org/what_is_strategy.pdf: summary blocks, numbered findings, temporal figures, figure notes, and appendix tables.
    </div>
  </article>

  <script>
    const DATA = __DATA__;
    const colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#17becf"];
    const fmt = new Intl.NumberFormat("en-US");
    const pct = value => `${(value * 100).toFixed(1)}%`;
    const pp = value => `${value > 0 ? "+" : ""}${value.toFixed(2)}pp`;
    const topicName = code => DATA.topicLabels[code] || code;
    const methodName = code => DATA.methodLabels[code] || code;
    const setText = (id, value) => { document.getElementById(id).textContent = value; };

    function initText() {
      const annual = DATA.annual;
      const peak = annual.reduce((best, row) => row.Total > best.Total ? row : best, annual[0]);
      const maxEff = annual.reduce((best, row) => row["Effective topics"] > best["Effective topics"] ? row : best, annual[0]);
      const latest = annual[annual.length - 1];
      const topTopic = DATA.topicFrequency[0];
      const topMethod = DATA.methodFrequency[0];
      const risingTopic = DATA.topicShift[0];
      const fallingTopic = DATA.topicShift[DATA.topicShift.length - 1];
      const risingMethod = DATA.methodShift[0];
      const fallingMethod = DATA.methodShift[DATA.methodShift.length - 1];
      const totalCross = annual.reduce((sum, row) => sum + row["Cross-disciplinary papers"], 0);
      const crossShare = totalCross / DATA.totalPapers;

      setText("researchSummary", `This report analyzes ${fmt.format(DATA.totalPapers)} coded papers from ${DATA.yearRange[0]}-${DATA.yearRange[1]}. Five temporal patterns emerge. Annual volume peaks in ${peak.Year}; topic diversity peaks earlier, in ${maxEff.Year}, then reconsolidates in the 2020s; the substantive center shifts toward ${topicName(risingTopic.Code)} and away from ${topicName(fallingTopic.Code)}; method share shifts toward ${methodName(risingMethod.Code)} and away from ${methodName(fallingMethod.Code)}; and cross-disciplinary papers account for ${pct(crossShare)} of the corpus.`);
      setText("managerialSummary", `The field is not just growing; it is changing shape. Recent work is more customer-experience centered, more resilience-aware, and more survey/SEM-heavy than the pre-2020 literature. For research planning, the strongest opportunities are temporal gaps: topics that are rising but methodologically narrow, and declining areas that may need renewal through new empirical designs.`);
      setText("keywords", "Keywords: omni-channel research, field evolution, temporal analysis, method evolution, topic concentration, research gaps");
      setText("metricPapers", fmt.format(DATA.totalPapers));
      setText("metricPeak", `${peak.Year} (${peak.Total})`);
      setText("metricDiversity", `${maxEff.Year}: ${maxEff["Effective topics"]}`);
      setText("metricCross", pct(crossShare));
      setText("dataMethods", `The source contains ${fmt.format(DATA.totalPapers)} coded papers, ${DATA.unknownYears} papers with unknown publication year, ${DATA.topicFrequency.length} topic categories, and ${DATA.methodFrequency.length} method categories. Time analysis uses annual counts, inverse-HHI effective category counts, pre-2020 versus 2020-2024 share changes, and cross-disciplinary indicators.`);
      setText("findingOne", `Publication volume is sparse before 2015, accelerates in 2018-2019, and reaches its maximum in ${peak.Year} with ${peak.Total} coded papers. This makes the 2020-2023 period the main empirical mass of the corpus.`);
      setText("findingTwo", `The field is most dispersed in ${maxEff.Year}, with ${maxEff["Effective topics"]} effective topics. In the 2020s, annual effective-topic counts settle around four to five in the large years, indicating partial reconsolidation around a smaller set of dominant themes.`);
      setText("findingThree", `${risingTopic.Code} ${topicName(risingTopic.Code)} rises by ${pp(risingTopic["Change pp"])}, while ${fallingTopic.Code} ${topicName(fallingTopic.Code)} falls by ${pp(fallingTopic["Change pp"])}. The shift is from logistics/fulfillment emphasis toward customer experience and resilience.`);
      setText("findingFour", `${risingMethod.Code} ${methodName(risingMethod.Code)} gains ${pp(risingMethod["Change pp"])}, while ${fallingMethod.Code} ${methodName(fallingMethod.Code)} changes by ${pp(fallingMethod["Change pp"])}. This suggests a stronger behavioral empirical center in the recent literature.`);
      setText("findingFive", `Across the full corpus, ${fmt.format(totalCross)} papers are coded as cross-disciplinary. Recent years remain strongly cross-field, especially 2023, when the cross-disciplinary share reaches ${pct(annual.find(row => row.Year === 2023)["Cross-disciplinary share"])}.`);
      setText("sourceFile", DATA.source);
      renderNotableChanges(peak, maxEff, risingTopic, fallingTopic, risingMethod, fallingMethod, annual);
    }

    function svgEl(name, attrs, parent) {
      const node = document.createElementNS("http://www.w3.org/2000/svg", name);
      Object.entries(attrs || {}).forEach(([key, value]) => node.setAttribute(key, value));
      parent.appendChild(node);
      return node;
    }

    function label(svg, x, y, value, attrs = {}) {
      const node = svgEl("text", { x, y, ...attrs }, svg);
      node.textContent = value;
      return node;
    }

    function renderStackedTopics() {
      const matrix = DATA.matrices.year_topic;
      const rows = matrix.rows.filter(row => row.name !== "Unknown");
      const cols = matrix.columns;
      const svg = document.getElementById("sampleChart");
      const width = 920, height = 370;
      const margin = { top: 18, right: 18, bottom: 46, left: 48 };
      const innerW = width - margin.left - margin.right;
      const innerH = height - margin.top - margin.bottom;
      const maxTotal = Math.max(...rows.map(row => row.total), 1);
      const gap = 8;
      const barW = (innerW - gap * (rows.length - 1)) / rows.length;
      const y = value => margin.top + innerH - (value / maxTotal) * innerH;
      svg.innerHTML = "";

      for (let tick = 0; tick <= maxTotal; tick += 20) {
        const yy = y(tick);
        svgEl("line", { x1: margin.left, y1: yy, x2: width - margin.right, y2: yy, stroke: "#e5e5e5" }, svg);
        label(svg, margin.left - 8, yy + 4, tick, { "text-anchor": "end", "font-size": 11, fill: "#333" });
      }

      rows.forEach((row, i) => {
        const x = margin.left + i * (barW + gap);
        let acc = 0;
        cols.forEach((col, j) => {
          const value = row.values[col];
          if (!value) return;
          const yTop = y(acc + value);
          const yBottom = y(acc);
          const rect = svgEl("rect", { x, y: yTop, width: barW, height: Math.max(1, yBottom - yTop), fill: colors[j % colors.length] }, svg);
          svgEl("title", {}, rect).textContent = `${row.name} | ${col}: ${value}`;
          acc += value;
        });
        label(svg, x + barW / 2, height - 18, row.name, { "text-anchor": "middle", "font-size": 11, fill: "#333", transform: `rotate(-35 ${x + barW / 2} ${height - 18})` });
      });
      svgEl("line", { x1: margin.left, y1: margin.top + innerH, x2: width - margin.right, y2: margin.top + innerH, stroke: "#111" }, svg);
      label(svg, 10, 22, "Papers", { "font-size": 12, fill: "#111" });

      document.getElementById("topicLegend").innerHTML = cols.map((col, i) =>
        `<span class="legend-item"><span class="swatch" style="background:${colors[i % colors.length]}"></span>${col}</span>`
      ).join("");
    }

    function renderTopicShareChart() {
      const matrix = DATA.matrices.year_topic;
      const rows = matrix.rows.filter(row => row.name !== "Unknown" && row.total > 0);
      const cols = matrix.columns;
      const svg = document.getElementById("shareChart");
      const width = 920, height = 340;
      const margin = { top: 18, right: 18, bottom: 46, left: 52 };
      const innerW = width - margin.left - margin.right;
      const innerH = height - margin.top - margin.bottom;
      const gap = 8;
      const barW = (innerW - gap * (rows.length - 1)) / rows.length;
      const y = value => margin.top + innerH - value * innerH;
      svg.innerHTML = "";

      for (let tick = 0; tick <= 1; tick += 0.25) {
        const yy = y(tick);
        svgEl("line", { x1: margin.left, y1: yy, x2: width - margin.right, y2: yy, stroke: "#e5e5e5" }, svg);
        label(svg, margin.left - 8, yy + 4, `${Math.round(tick * 100)}%`, { "text-anchor": "end", "font-size": 11, fill: "#333" });
      }

      rows.forEach((row, i) => {
        const x = margin.left + i * (barW + gap);
        let acc = 0;
        cols.forEach((col, j) => {
          const value = row.values[col] / row.total;
          if (!value) return;
          const yTop = y(acc + value);
          const yBottom = y(acc);
          const rect = svgEl("rect", { x, y: yTop, width: barW, height: Math.max(1, yBottom - yTop), fill: colors[j % colors.length] }, svg);
          svgEl("title", {}, rect).textContent = `${row.name} | ${col}: ${(value * 100).toFixed(1)}%`;
          acc += value;
        });
        label(svg, x + barW / 2, height - 18, row.name, { "text-anchor": "middle", "font-size": 11, fill: "#333", transform: `rotate(-35 ${x + barW / 2} ${height - 18})` });
      });
      svgEl("line", { x1: margin.left, y1: margin.top + innerH, x2: width - margin.right, y2: margin.top + innerH, stroke: "#111" }, svg);
      label(svg, 8, 22, "Share", { "font-size": 12, fill: "#111" });
    }

    function renderLineChart(id, series, options) {
      const svg = document.getElementById(id);
      const width = 900, height = options.height || 300;
      const margin = { top: 20, right: options.right ?? 110, bottom: 38, left: 52 };
      const innerW = width - margin.left - margin.right;
      const innerH = height - margin.top - margin.bottom;
      const years = DATA.annual.map(row => row.Year);
      const xMin = Math.min(...years), xMax = Math.max(...years);
      const yMax = options.yMax || Math.max(...series.flatMap(s => s.values.map(d => d.value))) * 1.12;
      const x = year => margin.left + ((year - xMin) / (xMax - xMin)) * innerW;
      const y = value => margin.top + innerH - (value / yMax) * innerH;
      svg.innerHTML = "";

      for (let i = 0; i <= 5; i++) {
        const value = yMax * i / 5;
        const yy = y(value);
        svgEl("line", { x1: margin.left, y1: yy, x2: width - margin.right, y2: yy, stroke: "#e5e5e5" }, svg);
        label(svg, margin.left - 8, yy + 4, options.percent ? `${Math.round(value * 100)}%` : value.toFixed(options.decimals ?? 0), { "text-anchor": "end", "font-size": 11, fill: "#333" });
      }

      series.forEach((s, i) => {
        const points = s.values.map(d => `${x(d.year)},${y(d.value)}`).join(" ");
        svgEl("polyline", { points, fill: "none", stroke: s.color || colors[i], "stroke-width": 2.4 }, svg);
        s.values.forEach(d => {
          svgEl("circle", { cx: x(d.year), cy: y(d.value), r: 3, fill: s.color || colors[i] }, svg);
        });
        if (options.endLabels !== false) {
          const last = s.values[s.values.length - 1];
          label(svg, width - 10, y(last.value) + 4, s.name, { "text-anchor": "end", "font-size": 12, fill: s.color || colors[i] });
        }
      });

      years.forEach(year => {
        if (year % 2 === 0 || years.length < 12) {
          label(svg, x(year), height - 15, year, { "text-anchor": "middle", "font-size": 11, fill: "#333" });
        }
      });
      svgEl("line", { x1: margin.left, y1: margin.top + innerH, x2: width - margin.right, y2: margin.top + innerH, stroke: "#111" }, svg);
      label(svg, width / 2, height - 1, "Year", { "text-anchor": "middle", "font-size": 12, fill: "#111" });
    }

    function renderHorizontalChange(id, rows, labelFn) {
      const svg = document.getElementById(id);
      const width = 900, height = Number(svg.viewBox.baseVal.height);
      const margin = { top: 16, right: 130, bottom: 26, left: 292 };
      const innerW = width - margin.left - margin.right;
      const values = rows.map(row => row["Change pp"]);
      const maxAbs = Math.max(...values.map(Math.abs), 1);
      const zero = margin.left + innerW / 2;
      const scale = value => zero + (value / maxAbs) * (innerW / 2);
      svg.innerHTML = "";
      svgEl("line", { x1: zero, y1: margin.top, x2: zero, y2: height - margin.bottom, stroke: "#111" }, svg);
      label(svg, zero, height - 6, "0pp", { "text-anchor": "middle", "font-size": 11, fill: "#333" });

      rows.forEach((row, i) => {
        const y = margin.top + i * 36 + 16;
        const value = row["Change pp"];
        const x = scale(value);
        label(svg, margin.left - 18, y + 4, labelFn(row), { "text-anchor": "end", "font-size": 12, fill: "#222" });
        svgEl("line", { x1: zero, y1: y, x2: x, y2: y, stroke: value >= 0 ? "#1f77b4" : "#d62728", "stroke-width": 10, "stroke-linecap": "butt" }, svg);
        label(svg, value >= 0 ? x + 8 : x + 8, y + 4, pp(value), { "text-anchor": "start", "font-size": 12, fill: "#222", "font-weight": 700 });
      });
    }

    function renderStructureLegend() {
      const items = [
        ["Effective topics", "#1f77b4"],
        ["Effective methods", "#ff7f0e"],
        ["Effective fields", "#2ca02c"]
      ];
      document.getElementById("structureLegend").innerHTML = items.map(([name, color]) =>
        `<span class="legend-item"><span class="swatch" style="background:${color}"></span>${name}</span>`
      ).join("");
    }

    function renderNotableChanges(peak, maxEff, risingTopic, fallingTopic, risingMethod, fallingMethod, annual) {
      const cross2023 = annual.find(row => row.Year === 2023);
      const expansion = DATA.topicPeriod.find(row => row.Code === "T3");
      const surgeT1 = DATA.topicPeriod.find(row => row.Code === "T1");
      const items = [
        `Volume turns into a true surge after 2018 and peaks in ${peak.Year} with ${peak.Total} papers, so the corpus is heavily shaped by the 2020-2023 publication wave.`,
        `The broadest topical spread appears in ${maxEff.Year} (${maxEff["Effective topics"]} effective topics), before the field reconsolidates around customer experience, channel questions, fulfillment, and operations.`,
        `${fallingTopic.Code} ${topicName(fallingTopic.Code)} has the largest negative share shift (${pp(fallingTopic["Change pp"])}), even though it remains important in absolute count. This looks like relative displacement rather than disappearance.`,
        `${risingTopic.Code} ${topicName(risingTopic.Code)} gains the most share (${pp(risingTopic["Change pp"])}), while T8 resilience/capability also rises from a very small base, suggesting a post-2020 capability and disruption lens.`,
        `${risingMethod.Code} ${methodName(risingMethod.Code)} gains ${pp(risingMethod["Change pp"])}, while ${fallingMethod.Code} ${methodName(fallingMethod.Code)} declines by ${pp(fallingMethod["Change pp"])}. The field is moving from framing papers toward more behavioral empirical evidence.`,
        `Cross-disciplinary share reaches ${pct(cross2023["Cross-disciplinary share"])} in 2023, making that year stand out as especially integrative across coded fields.`,
        `During the 2018-2019 expansion period, T3 takes ${(expansion["Expansion (2018-2019) share"] * 100).toFixed(1)}% of the topic mix; during the 2020-2023 surge, T1 rises to ${(surgeT1["Surge (2020-2023) share"] * 100).toFixed(1)}%. That is the clearest field-center rotation.`
      ];
      document.getElementById("notableChanges").innerHTML = items.map(item => `<li>${item}</li>`).join("");
    }

    function renderCharts() {
      renderStackedTopics();
      renderTopicShareChart();
      renderLineChart("volumeChart", [{
        name: "Papers",
        color: "#111",
        values: DATA.annual.map(row => ({ year: row.Year, value: row.Total }))
      }], { height: 280, yMax: 120 });

      renderLineChart("structureChart", [
        { name: "Effective topics", color: "#1f77b4", values: DATA.annual.map(row => ({ year: row.Year, value: row["Effective topics"] })) },
        { name: "Effective methods", color: "#ff7f0e", values: DATA.annual.map(row => ({ year: row.Year, value: row["Effective methods"] })) },
        { name: "Effective fields", color: "#2ca02c", values: DATA.annual.map(row => ({ year: row.Year, value: row["Effective fields"] })) }
      ], { height: 320, yMax: 7, decimals: 1, endLabels: false });
      renderStructureLegend();

      renderHorizontalChange("topicShiftChart", DATA.topicShift, row => `${row.Code} ${topicName(row.Code)}`);
      renderHorizontalChange("methodShiftChart", DATA.methodShift, row => `${row.Code} ${methodName(row.Code)}`);

      renderLineChart("crossChart", [{
        name: "Cross-disciplinary share",
        color: "#9467bd",
        values: DATA.annual.map(row => ({ year: row.Year, value: row["Cross-disciplinary share"] }))
      }], { height: 280, yMax: 1, percent: true, decimals: 1 });
    }

    function renderShiftTable(id, rows, labelFn) {
      const headers = ["Code", "Label", "Pre-2020 count", "Pre-2020 share", "2020-2024 count", "2020-2024 share", "Change pp"];
      const body = rows.map(row => `<tr>
        <td>${row.Code}</td>
        <td>${labelFn(row)}</td>
        <td>${row["Pre-2020 count"]}</td>
        <td>${pct(row["Pre-2020 share"])}</td>
        <td>${row["2020-2024 count"]}</td>
        <td>${pct(row["2020-2024 share"])}</td>
        <td>${pp(row["Change pp"])}</td>
      </tr>`).join("");
      document.getElementById(id).innerHTML = `<thead><tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr></thead><tbody>${body}</tbody>`;
    }

    function renderPeriodTable() {
      const periods = ["Formation (1990-2017)", "Expansion (2018-2019)", "Surge (2020-2023)", "Recent/partial (2024+)", "Unknown"];
      const header = ["Topic"].concat(periods.map(p => `${p} share`)).concat("Total");
      const body = DATA.topicPeriod.map(row => `<tr>
        <td>${row.Code} ${row.Label}</td>
        ${periods.map(p => `<td>${pct(row[`${p} share`])}</td>`).join("")}
        <td><strong>${row.Total}</strong></td>
      </tr>`).join("");
      document.getElementById("topicPeriodTable").innerHTML = `<thead><tr>${header.map(h => `<th>${h}</th>`).join("")}</tr></thead><tbody>${body}</tbody>`;
    }

    function heat(value, max) {
      if (!value) return "#fafafa";
      return `rgba(31, 119, 180, ${0.12 + (value / max) * 0.76})`;
    }

    function renderMatrix(key) {
      const matrix = DATA.matrices[key];
      const max = Math.max(...matrix.rows.flatMap(row => Object.values(row.values)), 1);
      setText("matrixTitle", `Table A1: ${matrix.title} Matrix.`);
      setText("matrixNote", `Note: ${matrix.note} Darker cells indicate larger counts.`);
      const header = [`<th>${matrix.row_label}</th>`].concat(matrix.columns.map(col => `<th>${col}</th>`)).concat("<th>Total</th>").join("");
      const body = matrix.rows.map(row => {
        const cells = matrix.columns.map(col => {
          const value = row.values[col];
          return `<td class="cell ${value === 0 ? "zero" : ""}" style="background:${heat(value, max)}">${value}</td>`;
        }).join("");
        return `<tr><td><strong>${row.name}</strong></td>${cells}<td><strong>${row.total}</strong></td></tr>`;
      }).join("");
      const totals = `<tr><td><strong>Total</strong></td>${matrix.columns.map(col => `<td><strong>${matrix.totals[col] || 0}</strong></td>`).join("")}<td><strong>${matrix.totals.Total || 0}</strong></td></tr>`;
      document.getElementById("matrixTable").innerHTML = `<thead><tr>${header}</tr></thead><tbody>${body}${totals}</tbody>`;
      document.querySelectorAll("#matrixTabs button").forEach(button => button.classList.toggle("active", button.dataset.key === key));
    }

    function renderMatrixTabs() {
      const target = document.getElementById("matrixTabs");
      target.innerHTML = Object.entries(DATA.matrices).map(([key, matrix]) => `<button type="button" data-key="${key}">${matrix.title}</button>`).join("");
      target.addEventListener("click", event => {
        const button = event.target.closest("button");
        if (button) renderMatrix(button.dataset.key);
      });
    }

    function renderGaps() {
      document.getElementById("gapList").innerHTML = DATA.topicMethodZeros.map(gap => `<li>${gap.row} ${topicName(gap.row)} x ${gap.col}</li>`).join("");
    }

    initText();
    renderCharts();
    renderShiftTable("topicShiftTable", DATA.topicShift, row => topicName(row.Code));
    renderShiftTable("methodShiftTable", DATA.methodShift, row => methodName(row.Code));
    renderPeriodTable();
    renderMatrixTabs();
    renderMatrix("topic_method");
    renderGaps();
  </script>
</body>
</html>
"""
    return html.replace("__DATA__", data_json)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(render_html(make_data()), encoding="utf-8")
    print(OUT_FILE.relative_to(ROOT))


if __name__ == "__main__":
    main()
