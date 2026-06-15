import csv
import json
from collections import Counter, defaultdict
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
        "note": "Counts show which disciplines own each topic and where cross-field spillovers appear.",
    },
    "field_method": {
        "title": "Field x Method",
        "file": "field_method_matrix.csv",
        "row_label": "Main field",
        "note": "Counts show methodological specialization by disciplinary field.",
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


def read_rows():
    with DATA_FILE.open() as f:
        return json.load(f)


def read_matrix(filename):
    with (ANALYSIS_DIR / filename).open(newline="") as f:
        rows = list(csv.DictReader(f))
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
    counts = Counter(row.get(key) or "Unknown" for row in rows)
    return [{"name": name, "count": count} for name, count in counts.most_common()]


def decade(year):
    try:
        year_int = int(year)
    except (TypeError, ValueError):
        return "Unknown"
    return f"{year_int // 10 * 10}s"


def decade_topic_table(rows):
    decades = ["1990s", "2000s", "2010s", "2020s", "Unknown"]
    counts = defaultdict(Counter)
    for row in rows:
        counts[row["topic_category"]][decade(row.get("publication_year"))] += 1

    table = []
    for code in TOPIC_LABELS:
        values = {dec: counts[code][dec] for dec in decades}
        table.append(
            {
                "code": code,
                "label": TOPIC_LABELS[code],
                "values": values,
                "total": sum(values.values()),
            }
        )
    return {
        "columns": decades,
        "rows": sorted(table, key=lambda item: (-item["total"], item["code"])),
    }


def topic_method_zeros(matrix):
    zeros = []
    for row in matrix["rows"]:
        for method, value in row["values"].items():
            if value == 0:
                zeros.append({"topic": row["name"], "method": method})
    return zeros


def dominant_cells(matrix, n=10):
    cells = []
    for row in matrix["rows"]:
        for col, value in row["values"].items():
            cells.append({"row": row["name"], "col": col, "count": value})
    return sorted(cells, key=lambda item: item["count"], reverse=True)[:n]


def make_data():
    rows = read_rows()
    matrices = {}
    for key, config in MATRIX_FILES.items():
        matrices[key] = {**config, **read_matrix(config["file"])}

    topic_freq = top_counts(rows, "topic_category")
    method_freq = top_counts(rows, "method_category")
    field_freq = top_counts(rows, "main_field")
    confidence = top_counts(rows, "coding_confidence")
    topic_method = matrices["topic_method"]

    return {
        "source": "DataProcessing/gibson_papers_coded_codex.json",
        "totalPapers": len(rows),
        "uniquePapers": len({row["paper_id"] for row in rows}),
        "yearRange": [
            min(int(row["publication_year"]) for row in rows if str(row.get("publication_year", "")).isdigit()),
            max(int(row["publication_year"]) for row in rows if str(row.get("publication_year", "")).isdigit()),
        ],
        "topicLabels": TOPIC_LABELS,
        "methodLabels": METHOD_LABELS,
        "topicFrequency": topic_freq,
        "methodFrequency": method_freq,
        "fieldFrequency": field_freq,
        "confidence": confidence,
        "decadeTopic": decade_topic_table(rows),
        "matrices": matrices,
        "topicMethodZeros": topic_method_zeros(topic_method),
        "dominantTopicMethod": dominant_cells(topic_method),
    }


def html_escape_json(data):
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def render_html(data):
    data_json = html_escape_json(data)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>What Is Omni-channel Research?</title>
  <style>
    :root {{
      --text: #111;
      --muted: #555;
      --rule: #d7d7d7;
      --light-rule: #ececec;
      --page: #fff;
      --accent: #1f77b4;
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
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      background: #f5f5f5;
      color: var(--text);
    }}

    .page {{
      width: min(100%, 980px);
      margin: 0 auto;
      background: var(--page);
      min-height: 100vh;
      padding: 42px 58px 70px;
      box-shadow: 0 0 28px rgba(0, 0, 0, 0.08);
    }}

    header {{
      text-align: center;
      border-bottom: 1px solid var(--rule);
      padding-bottom: 22px;
      margin-bottom: 24px;
    }}

    h1 {{
      margin: 0 0 14px;
      font-size: 2.55rem;
      line-height: 1.08;
      font-weight: 500;
      letter-spacing: 0;
    }}

    .authors, .site {{
      font-size: 1.02rem;
      line-height: 1.45;
    }}

    .site {{
      color: var(--muted);
      margin-top: 4px;
    }}

    h2 {{
      margin: 28px 0 10px;
      font-size: 1rem;
      text-transform: uppercase;
      letter-spacing: 0.02em;
      font-weight: 700;
    }}

    h3 {{
      margin: 26px 0 10px;
      font-size: 1.28rem;
      font-weight: 700;
    }}

    p {{
      margin: 0 0 12px;
      font-size: 1.02rem;
      line-height: 1.58;
    }}

    .summary {{
      display: grid;
      gap: 18px;
      margin-bottom: 20px;
    }}

    .summary-block {{
      border-bottom: 1px solid var(--light-rule);
      padding-bottom: 14px;
    }}

    .keywords {{
      color: var(--muted);
      font-size: 0.94rem;
      line-height: 1.5;
    }}

    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 14px;
      margin: 18px 0 24px;
      border-top: 1px solid var(--rule);
      border-bottom: 1px solid var(--rule);
      padding: 12px 0;
    }}

    .metric {{
      text-align: center;
      min-width: 0;
    }}

    .metric-value {{
      font-family: Arial, Helvetica, sans-serif;
      font-size: 1.9rem;
      font-weight: 700;
      line-height: 1.05;
    }}

    .metric-label {{
      margin-top: 5px;
      color: var(--muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      font-family: Arial, Helvetica, sans-serif;
    }}

    .figure {{
      margin: 18px 0 26px;
      border-top: 1px solid var(--rule);
      padding-top: 12px;
    }}

    .figure-title, .table-title {{
      font-weight: 700;
      font-size: 0.96rem;
      margin-bottom: 8px;
    }}

    .note {{
      margin-top: 8px;
      color: var(--muted);
      font-size: 0.88rem;
      line-height: 1.45;
    }}

    svg {{
      display: block;
      width: 100%;
      height: auto;
      background: white;
      font-family: Arial, Helvetica, sans-serif;
    }}

    .chart-wrap {{
      overflow-x: auto;
    }}

    .chart {{
      min-width: 780px;
    }}

    .axis text, .tick-label {{
      fill: #333;
      font-size: 11px;
    }}

    .legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px 13px;
      margin-top: 8px;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 0.79rem;
    }}

    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }}

    .swatch {{
      width: 12px;
      height: 10px;
      display: inline-block;
      border: 1px solid rgba(0,0,0,0.12);
    }}

    .two-col {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      align-items: start;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 0.82rem;
      margin-top: 8px;
    }}

    th, td {{
      border-bottom: 1px solid var(--light-rule);
      padding: 7px 8px;
      text-align: right;
      vertical-align: top;
    }}

    th:first-child, td:first-child {{
      text-align: left;
    }}

    thead th {{
      border-bottom: 1px solid var(--text);
      font-weight: 700;
    }}

    tbody tr:last-child td {{
      border-bottom: 1px solid var(--text);
    }}

    .table-scroll {{
      overflow-x: auto;
    }}

    .matrix-toolbar {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: flex-end;
      margin: 8px 0 10px;
    }}

    .tabs {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      justify-content: flex-end;
      font-family: Arial, Helvetica, sans-serif;
    }}

    button {{
      border: 1px solid #888;
      background: white;
      color: #111;
      border-radius: 0;
      padding: 5px 8px;
      font: inherit;
      font-size: 0.76rem;
      cursor: pointer;
    }}

    button.active {{
      background: #111;
      color: white;
    }}

    .heatmap {{
      min-width: 820px;
    }}

    .heatmap td.cell {{
      color: #111;
      font-weight: 700;
      font-variant-numeric: tabular-nums;
    }}

    .heatmap td.zero {{
      color: #aaa;
      font-weight: 400;
      background: #fafafa !important;
    }}

    .gap-list {{
      columns: 2;
      column-gap: 28px;
      margin: 0;
      padding-left: 20px;
      font-size: 0.95rem;
      line-height: 1.5;
    }}

    .footer {{
      border-top: 1px solid var(--rule);
      margin-top: 34px;
      padding-top: 12px;
      color: var(--muted);
      font-size: 0.86rem;
      line-height: 1.45;
    }}

    @media print {{
      body {{ background: white; }}
      .page {{ box-shadow: none; padding: 28px 42px; }}
      button {{ display: none; }}
      .chart-wrap, .table-scroll {{ overflow: visible; }}
    }}

    @media (max-width: 760px) {{
      .page {{
        padding: 28px 20px 46px;
        box-shadow: none;
      }}

      h1 {{ font-size: 2rem; }}

      .metrics, .two-col {{
        grid-template-columns: 1fr;
      }}

      .matrix-toolbar {{
        display: block;
      }}

      .tabs {{
        justify-content: flex-start;
        margin-top: 10px;
      }}

      .gap-list {{
        columns: 1;
      }}
    }}
  </style>
</head>
<body>
  <article class="page">
    <header>
      <h1>What Is Omni-channel Research?</h1>
      <div class="authors">A matrix analysis of the Gibson coded paper corpus</div>
      <div class="site">BusinessAnalysis/DataVisaualizationCodex</div>
    </header>

    <section class="summary">
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
      <div class="metric"><div class="metric-value" id="metricYears"></div><div class="metric-label">Years</div></div>
      <div class="metric"><div class="metric-value" id="metricTopics"></div><div class="metric-label">Topics</div></div>
      <div class="metric"><div class="metric-value" id="metricGaps"></div><div class="metric-label">Zero cells</div></div>
    </section>

    <section>
      <h2>Introduction</h2>
      <p>This visual report follows the paper-style structure of a computational field map: first describe the sample, then show the field's major clusters, then interpret where topics, methods, and disciplinary fields reinforce or diverge from one another.</p>
      <p>The analysis is based on coded topic, method, field, cross-disciplinary, and year variables. It does not estimate semantic embeddings; instead, it uses the existing coding matrices as a transparent map of the corpus.</p>
    </section>

    <section>
      <h2>Data and Methods</h2>
      <p>The sample contains <span id="sampleN"></span> coded papers. Topics and methods are treated as categorical classifications, and the visualizations aggregate paper counts across years, decades, main fields, and topic-method cells.</p>
      <div class="figure">
        <div class="figure-title">Figure 1: Sample Composition by Topic Over Time.</div>
        <div class="chart-wrap">
          <svg id="sampleChart" class="chart" viewBox="0 0 900 360" role="img" aria-label="Stacked bar chart of topics over time"></svg>
        </div>
        <div id="topicLegend" class="legend"></div>
        <div class="note">Note: Stacked bars show topic counts by publication year. Unknown publication years are excluded from this figure but retained in aggregate tables.</div>
      </div>
    </section>

    <section>
      <h2>Findings</h2>

      <h3>Finding 1: The corpus is organized around customer, channel, and fulfillment questions.</h3>
      <p id="findingOne"></p>
      <div class="figure two-col">
        <div>
          <div class="figure-title">Figure 2a: Topic Frequency.</div>
          <svg id="topicBars" viewBox="0 0 430 300" role="img" aria-label="Topic frequency bar chart"></svg>
        </div>
        <div>
          <div class="figure-title">Figure 2b: Method Frequency.</div>
          <svg id="methodBars" viewBox="0 0 430 300" role="img" aria-label="Method frequency bar chart"></svg>
        </div>
      </div>

      <h3>Finding 2: Evidence production is split between survey/SEM and operations-modeling traditions.</h3>
      <p id="findingTwo"></p>
      <div class="figure">
        <div class="figure-title">Figure 3: Dominant Topic-Method Combinations.</div>
        <svg id="comboBars" viewBox="0 0 900 360" role="img" aria-label="Dominant topic-method combinations"></svg>
        <div class="note">Note: Bars report the largest cells from the topic-by-method matrix.</div>
      </div>

      <h3>Finding 3: Disciplinary ownership is strong but not complete.</h3>
      <p id="findingThree"></p>
      <div class="figure">
        <div class="figure-title">Figure 4: Main Field Frequency.</div>
        <svg id="fieldBars" viewBox="0 0 900 330" role="img" aria-label="Main field frequency bar chart"></svg>
      </div>

      <h3>Finding 4: Empty topic-method cells identify research opportunity zones.</h3>
      <p id="findingFour"></p>
      <ol id="gapList" class="gap-list"></ol>
    </section>

    <section>
      <h2>Matrix Appendix</h2>
      <p>The appendix makes the underlying matrices inspectable. Use the buttons to switch between topic-method, field-topic, field-method, year-topic, and year-method views.</p>
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
        <div class="table-title">Table A2: Distribution of Papers by Topic and Decade.</div>
        <div class="table-scroll">
          <table id="decadeTable"></table>
        </div>
        <div class="note">Note: Decades are based on publication year. Unknown years are reported separately.</div>
      </div>
    </section>

    <div class="footer">
      Generated from <span id="sourceFile"></span>. Visual style adapted from the structure of whatisstrategy.org/what_is_strategy.pdf: summary blocks, numbered findings, figure notes, and print-oriented academic layout.
    </div>
  </article>

  <script>
    const DATA = {data_json};
    const colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#17becf"];
    const fmt = new Intl.NumberFormat("en-US");
    const topicName = code => DATA.topicLabels[code] || code;
    const methodName = code => DATA.methodLabels[code] || code;
    const topicColor = label => colors[Object.values(DATA.topicLabels).indexOf(label) % colors.length] || "#333";

    function setText(id, value) {{
      document.getElementById(id).textContent = value;
    }}

    function sentenceList(items) {{
      return items.map(item => `${{item.name}} (${{item.count}})`).join(", ");
    }}

    function initText() {{
      const topTopics = DATA.topicFrequency.slice(0, 3);
      const topMethods = DATA.methodFrequency.slice(0, 3);
      const topFields = DATA.fieldFrequency.slice(0, 3);
      const topCell = DATA.dominantTopicMethod[0];
      const yearSpan = `${{DATA.yearRange[0]}}-${{DATA.yearRange[1]}}`;

      setText("researchSummary", `This report analyzes ${{fmt.format(DATA.totalPapers)}} coded papers from ${{yearSpan}}. Four patterns emerge. First, the corpus is concentrated in ${{topicName(topTopics[0].name)}} and ${{topicName(topTopics[1].name)}}. Second, method use is centered on ${{methodName(topMethods[0].name)}}, ${{methodName(topMethods[1].name)}}, and ${{methodName(topMethods[2].name)}}. Third, fields show clear specialization: ${{topFields[0].name}} is the largest field, while operations-oriented and supply-chain fields anchor optimization and fulfillment work. Fourth, ${{DATA.topicMethodZeros.length}} topic-method cells are empty, suggesting candidate research gaps.`);
      setText("managerialSummary", `The literature is strongest where customer behavior, channel design, fulfillment, and operational optimization are already well connected to established methods. For research planning, the most useful opportunities are not simply low-count topics; they are combinations where an important topic has rarely been studied with a method that could plausibly add new evidence.`);
      setText("keywords", `Keywords: omni-channel research, literature mapping, topic-method matrix, field evolution, research gaps`);
      setText("metricPapers", fmt.format(DATA.totalPapers));
      setText("metricYears", yearSpan);
      setText("metricTopics", DATA.topicFrequency.length);
      setText("metricGaps", DATA.topicMethodZeros.length);
      setText("sampleN", fmt.format(DATA.totalPapers));
      setText("sourceFile", DATA.source);
      setText("findingOne", `The leading topics are ${{topTopics.map(item => `${{item.name}} ${{topicName(item.name)}} (${{item.count}})`).join(", ")}}, which together define the center of gravity of the corpus.`);
      setText("findingTwo", `The largest method categories are ${{topMethods.map(item => `${{item.name}} ${{methodName(item.name)}} (${{item.count}})`).join(", ")}}, indicating two major evidence traditions: behavioral survey evidence and operations-style analytical modeling.`);
      setText("findingThree", `The largest main fields are ${{sentenceList(topFields)}}. The matrix view below shows that field-topic alignment is strong, especially for marketing/customer behavior, management science/optimization, supply chain/fulfillment, and information systems/digital technology.`);
      setText("findingFour", `There are ${{DATA.topicMethodZeros.length}} empty cells in the topic-method matrix. These cells should be read as research opportunity candidates rather than proof that no work is possible.`);
    }}

    function svgEl(name, attrs, parent) {{
      const node = document.createElementNS("http://www.w3.org/2000/svg", name);
      Object.entries(attrs || {{}}).forEach(([key, value]) => node.setAttribute(key, value));
      parent.appendChild(node);
      return node;
    }}

    function text(svg, x, y, value, attrs = {{}}) {{
      const node = svgEl("text", {{ x, y, ...attrs }}, svg);
      node.textContent = value;
      return node;
    }}

    function renderHorizontalBars(id, items, options = {{}}) {{
      const svg = document.getElementById(id);
      const width = options.width || Number(svg.viewBox.baseVal.width) || 900;
      const height = options.height || Number(svg.viewBox.baseVal.height) || 330;
      const left = options.left || 210;
      const right = 28;
      const top = 18;
      const rowH = options.rowH || 30;
      const barH = options.barH || 18;
      const max = Math.max(...items.map(item => item.count), 1);
      svg.innerHTML = "";

      items.forEach((item, index) => {{
        const y = top + index * rowH;
        const w = ((width - left - right) * item.count) / max;
        text(svg, left - 8, y + 14, item.label, {{ "text-anchor": "end", "font-size": 11, fill: "#222" }});
        svgEl("rect", {{ x: left, y, width: w, height: barH, fill: item.color || colors[index % colors.length] }}, svg);
        text(svg, left + w + 6, y + 14, fmt.format(item.count), {{ "font-size": 11, fill: "#222" }});
      }});
    }}

    function renderSampleChart() {{
      const matrix = DATA.matrices.year_topic;
      const rows = matrix.rows.filter(row => row.name !== "Unknown");
      const cols = matrix.columns;
      const svg = document.getElementById("sampleChart");
      const width = 900;
      const height = 360;
      const margin = {{ top: 18, right: 18, bottom: 45, left: 48 }};
      const innerW = width - margin.left - margin.right;
      const innerH = height - margin.top - margin.bottom;
      const maxTotal = Math.max(...rows.map(row => row.total), 1);
      const gap = 8;
      const barW = (innerW - gap * (rows.length - 1)) / rows.length;
      svg.innerHTML = "";

      const y = value => margin.top + innerH - (value / maxTotal) * innerH;
      for (let tick = 0; tick <= maxTotal; tick += 20) {{
        const yy = y(tick);
        svgEl("line", {{ x1: margin.left, y1: yy, x2: width - margin.right, y2: yy, stroke: "#e5e5e5" }}, svg);
        text(svg, margin.left - 8, yy + 4, tick, {{ "text-anchor": "end", "font-size": 11, fill: "#333" }});
      }}

      rows.forEach((row, i) => {{
        const x = margin.left + i * (barW + gap);
        let acc = 0;
        cols.forEach((col, j) => {{
          const value = row.values[col];
          if (!value) return;
          const yTop = y(acc + value);
          const yBottom = y(acc);
          const rect = svgEl("rect", {{ x, y: yTop, width: barW, height: Math.max(1, yBottom - yTop), fill: colors[j % colors.length] }}, svg);
          const title = svgEl("title", {{}}, rect);
          title.textContent = `${{row.name}} | ${{col}}: ${{value}}`;
          acc += value;
        }});
        text(svg, x + barW / 2, height - 18, row.name, {{ "text-anchor": "middle", "font-size": 11, fill: "#333", transform: `rotate(-35 ${{x + barW / 2}} ${{height - 18}})` }});
      }});
      svgEl("line", {{ x1: margin.left, y1: margin.top + innerH, x2: width - margin.right, y2: margin.top + innerH, stroke: "#111" }}, svg);
      text(svg, 10, 22, "Papers", {{ "font-size": 12, fill: "#111" }});
      text(svg, width / 2, height - 2, "Year", {{ "text-anchor": "middle", "font-size": 12, fill: "#111" }});

      document.getElementById("topicLegend").innerHTML = cols.map((col, i) =>
        `<span class="legend-item"><span class="swatch" style="background:${{colors[i % colors.length]}}"></span>${{col}}</span>`
      ).join("");
    }}

    function renderFrequencyFigures() {{
      renderHorizontalBars("topicBars", DATA.topicFrequency.map((item, i) => ({{
        label: `${{item.name}} ${{topicName(item.name)}}`,
        count: item.count,
        color: colors[i % colors.length]
      }})), {{ width: 430, height: 300, left: 210, rowH: 32 }});

      renderHorizontalBars("methodBars", DATA.methodFrequency.map((item, i) => ({{
        label: `${{item.name}} ${{methodName(item.name)}}`,
        count: item.count,
        color: colors[(i + 2) % colors.length]
      }})), {{ width: 430, height: 300, left: 220, rowH: 29 }});

      renderHorizontalBars("comboBars", DATA.dominantTopicMethod.map((item, i) => ({{
        label: `${{item.row}} x ${{item.col}}`,
        count: item.count,
        color: colors[i % colors.length]
      }})), {{ width: 900, height: 360, left: 360, rowH: 31 }});

      renderHorizontalBars("fieldBars", DATA.fieldFrequency.map((item, i) => ({{
        label: item.name,
        count: item.count,
        color: colors[i % colors.length]
      }})), {{ width: 900, height: 330, left: 280, rowH: 29 }});
    }}

    function heat(value, max) {{
      if (!value) return "#fafafa";
      const t = value / max;
      return `rgba(31, 119, 180, ${{0.12 + t * 0.76}})`;
    }}

    function renderMatrix(key) {{
      const matrix = DATA.matrices[key];
      const max = Math.max(...matrix.rows.flatMap(row => Object.values(row.values)), 1);
      const title = `Table A1: ${{matrix.title}} Matrix.`;
      setText("matrixTitle", title);
      setText("matrixNote", `Note: ${{matrix.note}} Darker cells indicate larger counts.`);

      const header = [`<th>${{matrix.row_label}}</th>`]
        .concat(matrix.columns.map(col => `<th>${{col}}</th>`))
        .concat(`<th>Total</th>`)
        .join("");
      const body = matrix.rows.map(row => {{
        const cells = matrix.columns.map(col => {{
          const value = row.values[col];
          return `<td class="cell ${{value === 0 ? "zero" : ""}}" style="background:${{heat(value, max)}}">${{value}}</td>`;
        }}).join("");
        return `<tr><td><strong>${{row.name}}</strong></td>${{cells}}<td><strong>${{row.total}}</strong></td></tr>`;
      }}).join("");
      const totals = `<tr><td><strong>Total</strong></td>${{matrix.columns.map(col => `<td><strong>${{matrix.totals[col] || 0}}</strong></td>`).join("")}}<td><strong>${{matrix.totals.Total || 0}}</strong></td></tr>`;
      document.getElementById("matrixTable").innerHTML = `<thead><tr>${{header}}</tr></thead><tbody>${{body}}${{totals}}</tbody>`;

      document.querySelectorAll("#matrixTabs button").forEach(button => {{
        button.classList.toggle("active", button.dataset.key === key);
      }});
    }}

    function renderTabs() {{
      const target = document.getElementById("matrixTabs");
      target.innerHTML = Object.entries(DATA.matrices).map(([key, matrix]) => `<button type="button" data-key="${{key}}">${{matrix.title}}</button>`).join("");
      target.addEventListener("click", event => {{
        const button = event.target.closest("button");
        if (button) renderMatrix(button.dataset.key);
      }});
    }}

    function renderDecadeTable() {{
      const table = DATA.decadeTopic;
      const header = [`<th>Research Topic</th>`].concat(table.columns.map(col => `<th>${{col}}</th>`)).concat(`<th>Total</th>`).join("");
      const body = table.rows.map(row => {{
        const cells = table.columns.map(col => `<td>${{row.values[col]}}</td>`).join("");
        return `<tr><td>${{row.code}} ${{row.label}}</td>${{cells}}<td><strong>${{row.total}}</strong></td></tr>`;
      }}).join("");
      document.getElementById("decadeTable").innerHTML = `<thead><tr>${{header}}</tr></thead><tbody>${{body}}</tbody>`;
    }}

    function renderGaps() {{
      document.getElementById("gapList").innerHTML = DATA.topicMethodZeros.map(gap => `<li>${{gap.topic}} ${{topicName(gap.topic)}} x ${{gap.method}}</li>`).join("");
    }}

    initText();
    renderSampleChart();
    renderFrequencyFigures();
    renderTabs();
    renderMatrix("topic_method");
    renderDecadeTable();
    renderGaps();
  </script>
</body>
</html>
"""


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(render_html(make_data()), encoding="utf-8")
    print(OUT_FILE.relative_to(ROOT))


if __name__ == "__main__":
    main()
