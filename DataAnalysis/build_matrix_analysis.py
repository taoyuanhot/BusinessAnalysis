import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "DataProcessing" / "gibson_papers_coded_codex.json"
OUT_DIR = ROOT / "DataAnalysis"

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

TOPIC_ORDER = list(TOPIC_LABELS)
METHOD_ORDER = list(METHOD_LABELS)


def read_rows():
    with INPUT.open() as f:
        return json.load(f)


def write_matrix(filename, row_key, col_key, row_order=None, col_order=None, row_label=None, col_labels=None):
    rows = read_rows()
    row_values = row_order or sorted({str(r[row_key]) for r in rows if r.get(row_key) not in ("", None)})
    col_values = col_order or sorted({str(r[col_key]) for r in rows if r.get(col_key) not in ("", None)})
    counts = Counter((str(r.get(row_key) or "Unknown"), str(r.get(col_key) or "Unknown")) for r in rows)

    out = OUT_DIR / filename
    with out.open("w", newline="") as f:
        writer = csv.writer(f)
        headers = [row_label or row_key] + [col_labels.get(c, c) if col_labels else c for c in col_values] + ["Total"]
        writer.writerow(headers)
        for rv in row_values:
            values = [counts[(rv, cv)] for cv in col_values]
            writer.writerow([rv] + values + [sum(values)])
        totals = [sum(counts[(rv, cv)] for rv in row_values) for cv in col_values]
        writer.writerow(["Total"] + totals + [sum(totals)])
    return out


def write_topic_cross_count():
    rows = read_rows()
    col_values = sorted({int(r.get("cross_count", 0)) for r in rows})
    counts = Counter((r["topic_category"], int(r.get("cross_count", 0))) for r in rows)
    out = OUT_DIR / "topic_cross_count_matrix.csv"
    with out.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Topic"] + [f"cross_count_{c}" for c in col_values] + ["Total"])
        for topic in TOPIC_ORDER:
            vals = [counts[(topic, c)] for c in col_values]
            writer.writerow([topic] + vals + [sum(vals)])
        totals = [sum(counts[(topic, c)] for topic in TOPIC_ORDER) for c in col_values]
        writer.writerow(["Total"] + totals + [sum(totals)])
    return out


def top_pairs(rows, a, b, n=10):
    counts = Counter((r[a], r[b]) for r in rows)
    return counts.most_common(n)


def sparse_pairs(rows, a_values, b_values, a, b):
    counts = Counter((r[a], r[b]) for r in rows)
    return [(av, bv) for av in a_values for bv in b_values if counts[(av, bv)] == 0]


def write_summary():
    rows = read_rows()
    topic_counts = Counter(r["topic_category"] for r in rows)
    method_counts = Counter(r["method_category"] for r in rows)
    field_counts = Counter(r["main_field"] for r in rows)
    confidence_counts = Counter(r["coding_confidence"] for r in rows)
    topic_method_top = top_pairs(rows, "topic_category", "method_category")
    field_topic_top = top_pairs(rows, "main_field", "topic_category")
    field_method_top = top_pairs(rows, "main_field", "method_category")

    topic_method_zeros = sparse_pairs(rows, TOPIC_ORDER, METHOD_ORDER, "topic_category", "method_category")

    by_year_topic = defaultdict(Counter)
    for r in rows:
        by_year_topic[r["publication_year"]][r["topic_category"]] += 1
    yearly_peaks = []
    for year in sorted(y for y in by_year_topic if y):
        topic, count = by_year_topic[year].most_common(1)[0]
        yearly_peaks.append((year, topic, count))

    lines = [
        "# Gibson Matrix Analysis",
        "",
        "## Dataset",
        "",
        f"- Source file: `DataProcessing/gibson_papers_coded_codex.json`",
        f"- Total papers: {len(rows)}",
        f"- Unique paper IDs: {len({r['paper_id'] for r in rows})}",
        f"- Coding confidence counts: {dict(sorted(confidence_counts.items()))}",
        "",
        "## Topic Frequencies",
        "",
        "| Topic | Label | Count |",
        "|---|---|---:|",
    ]
    for code, count in topic_counts.most_common():
        lines.append(f"| {code} | {TOPIC_LABELS.get(code, code)} | {count} |")

    lines += [
        "",
        "## Method Frequencies",
        "",
        "| Method | Label | Count |",
        "|---|---|---:|",
    ]
    for code, count in method_counts.most_common():
        lines.append(f"| {code} | {METHOD_LABELS.get(code, code)} | {count} |")

    lines += [
        "",
        "## Main Field Frequencies",
        "",
        "| Main field | Count |",
        "|---|---:|",
    ]
    for field, count in field_counts.most_common():
        lines.append(f"| {field} | {count} |")

    lines += [
        "",
        "## Dominant Topic-Method Combinations",
        "",
        "| Topic | Method | Count |",
        "|---|---|---:|",
    ]
    for (topic, method), count in topic_method_top:
        lines.append(f"| {topic} {TOPIC_LABELS.get(topic, '')} | {method} {METHOD_LABELS.get(method, '')} | {count} |")

    lines += [
        "",
        "## Dominant Field-Topic Combinations",
        "",
        "| Main field | Topic | Count |",
        "|---|---|---:|",
    ]
    for (field, topic), count in field_topic_top:
        lines.append(f"| {field} | {topic} {TOPIC_LABELS.get(topic, '')} | {count} |")

    lines += [
        "",
        "## Dominant Field-Method Combinations",
        "",
        "| Main field | Method | Count |",
        "|---|---|---:|",
    ]
    for (field, method), count in field_method_top:
        lines.append(f"| {field} | {method} {METHOD_LABELS.get(method, '')} | {count} |")

    lines += [
        "",
        "## Structural Interpretation",
        "",
        f"- The corpus is concentrated in {topic_counts.most_common(1)[0][0]} ({TOPIC_LABELS[topic_counts.most_common(1)[0][0]]}) and {topic_counts.most_common(2)[1][0]} ({TOPIC_LABELS[topic_counts.most_common(2)[1][0]]}).",
        f"- The most common method is {method_counts.most_common(1)[0][0]} ({METHOD_LABELS[method_counts.most_common(1)[0][0]]}), showing that survey/SEM-style evidence is a major methodological center of the corpus.",
        "- Topic-method gaps are visible where matrix cells are zero; these combinations may indicate underdeveloped research opportunities rather than methodological impossibility.",
        "- Field-topic concentration can be used to identify disciplinary ownership, while off-diagonal cells suggest cross-field opportunities.",
        "",
        "## Zero Topic-Method Cells",
        "",
        "| Topic | Method |",
        "|---|---|",
    ]
    for topic, method in topic_method_zeros[:80]:
        lines.append(f"| {topic} {TOPIC_LABELS[topic]} | {method} {METHOD_LABELS[method]} |")

    lines += [
        "",
        "## Yearly Dominant Topics",
        "",
        "| Year | Dominant topic | Count |",
        "|---|---|---:|",
    ]
    for year, topic, count in yearly_peaks:
        lines.append(f"| {year} | {topic} {TOPIC_LABELS.get(topic, '')} | {count} |")

    out = OUT_DIR / "gibson_matrix_analysis_summary.md"
    out.write_text("\n".join(lines) + "\n")
    return out


def main():
    rows = read_rows()
    field_order = [field for field, _ in Counter(r["main_field"] for r in rows).most_common()]
    year_order = sorted({r["publication_year"] for r in rows if r["publication_year"]})
    if any(not r["publication_year"] for r in rows):
        year_order.append("Unknown")

    outputs = [
        write_matrix("topic_method_matrix.csv", "topic_category", "method_category", TOPIC_ORDER, METHOD_ORDER, "Topic", METHOD_LABELS),
        write_matrix("field_topic_matrix.csv", "main_field", "topic_category", field_order, TOPIC_ORDER, "Main field", TOPIC_LABELS),
        write_matrix("year_topic_matrix.csv", "publication_year", "topic_category", year_order, TOPIC_ORDER, "Year", TOPIC_LABELS),
        write_matrix("year_method_matrix.csv", "publication_year", "method_category", year_order, METHOD_ORDER, "Year", METHOD_LABELS),
        write_matrix("field_method_matrix.csv", "main_field", "method_category", field_order, METHOD_ORDER, "Main field", METHOD_LABELS),
        write_topic_cross_count(),
        write_summary(),
    ]
    for out in outputs:
        print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
