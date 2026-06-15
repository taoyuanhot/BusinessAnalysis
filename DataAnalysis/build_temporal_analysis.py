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


def numeric_year(row):
    value = row.get("publication_year")
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def decade_for_year(year):
    if year is None:
        return "Unknown"
    return f"{year // 10 * 10}s"


def period_for_year(year):
    if year is None:
        return "Unknown"
    if year <= 2017:
        return "Formation (1990-2017)"
    if year <= 2019:
        return "Expansion (2018-2019)"
    if year <= 2023:
        return "Surge (2020-2023)"
    return "Recent/partial (2024+)"


def hhi(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return sum((value / total) ** 2 for value in counts.values())


def effective_count(counts):
    value = hhi(counts)
    return 0.0 if value == 0 else 1 / value


def share(count, total):
    return 0.0 if total == 0 else count / total


def write_csv(path, headers, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    return path


def annual_summary(rows):
    by_year = defaultdict(list)
    for row in rows:
        year = numeric_year(row)
        if year is not None:
            by_year[year].append(row)

    output = []
    for year in sorted(by_year):
        year_rows = by_year[year]
        total = len(year_rows)
        topic_counts = Counter(row["topic_category"] for row in year_rows)
        method_counts = Counter(row["method_category"] for row in year_rows)
        field_counts = Counter(row["main_field"] for row in year_rows)
        top_topic, top_topic_count = topic_counts.most_common(1)[0]
        top_method, top_method_count = method_counts.most_common(1)[0]
        cross_count = sum(1 for row in year_rows if int(row.get("cross_count", 0)) > 0)
        output.append(
            {
                "Year": year,
                "Total": total,
                "Topic HHI": round(hhi(topic_counts), 4),
                "Effective topics": round(effective_count(topic_counts), 2),
                "Top topic": top_topic,
                "Top topic label": TOPIC_LABELS[top_topic],
                "Top topic share": round(share(top_topic_count, total), 4),
                "Method HHI": round(hhi(method_counts), 4),
                "Effective methods": round(effective_count(method_counts), 2),
                "Top method": top_method,
                "Top method label": METHOD_LABELS[top_method],
                "Top method share": round(share(top_method_count, total), 4),
                "Field HHI": round(hhi(field_counts), 4),
                "Effective fields": round(effective_count(field_counts), 2),
                "Cross-disciplinary papers": cross_count,
                "Cross-disciplinary share": round(share(cross_count, total), 4),
                "Average cross count": round(sum(int(row.get("cross_count", 0)) for row in year_rows) / total, 3),
            }
        )
    return output


def period_matrix(rows, row_key, order, labels):
    periods = ["Formation (1990-2017)", "Expansion (2018-2019)", "Surge (2020-2023)", "Recent/partial (2024+)", "Unknown"]
    counts = defaultdict(Counter)
    totals = Counter()
    for row in rows:
        period = period_for_year(numeric_year(row))
        value = row[row_key]
        counts[value][period] += 1
        totals[period] += 1

    output = []
    for code in order:
        record = {"Code": code, "Label": labels[code]}
        row_total = 0
        for period in periods:
            count = counts[code][period]
            row_total += count
            record[f"{period} count"] = count
            record[f"{period} share"] = round(share(count, totals[period]), 4)
        record["Total"] = row_total
        output.append(record)
    return periods, output


def early_late_shift(rows, row_key, order, labels):
    early = [row for row in rows if (numeric_year(row) is not None and numeric_year(row) <= 2019)]
    late = [row for row in rows if (numeric_year(row) is not None and 2020 <= numeric_year(row) <= 2024)]
    early_counts = Counter(row[row_key] for row in early)
    late_counts = Counter(row[row_key] for row in late)
    output = []
    for code in order:
        early_share = share(early_counts[code], len(early))
        late_share = share(late_counts[code], len(late))
        output.append(
            {
                "Code": code,
                "Label": labels[code],
                "Pre-2020 count": early_counts[code],
                "Pre-2020 share": round(early_share, 4),
                "2020-2024 count": late_counts[code],
                "2020-2024 share": round(late_share, 4),
                "Change pp": round((late_share - early_share) * 100, 2),
                "Relative change": "" if early_share == 0 else round((late_share / early_share) - 1, 4),
            }
        )
    return sorted(output, key=lambda row: row["Change pp"], reverse=True)


def decade_shares(rows, row_key, order, labels):
    decades = ["1990s", "2000s", "2010s", "2020s", "Unknown"]
    counts = defaultdict(Counter)
    totals = Counter()
    for row in rows:
        dec = decade_for_year(numeric_year(row))
        value = row[row_key]
        counts[value][dec] += 1
        totals[dec] += 1

    output = []
    for code in order:
        record = {"Code": code, "Label": labels[code]}
        record_total = 0
        for dec in decades:
            count = counts[code][dec]
            record_total += count
            record[f"{dec} count"] = count
            record[f"{dec} share"] = round(share(count, totals[dec]), 4)
        record["Total"] = record_total
        output.append(record)
    return decades, output


def write_summary(rows, annual, topic_shift, method_shift):
    valid_years = [numeric_year(row) for row in rows if numeric_year(row) is not None]
    topic_counts = Counter(row["topic_category"] for row in rows)
    method_counts = Counter(row["method_category"] for row in rows)
    cross_total = sum(1 for row in rows if int(row.get("cross_count", 0)) > 0)
    annual_by_year = {row["Year"]: row for row in annual}
    peak_year = max(annual, key=lambda row: row["Total"])
    max_effective = max(annual, key=lambda row: row["Effective topics"])
    min_recent = min([row for row in annual if row["Year"] >= 2020], key=lambda row: row["Effective topics"])
    rising_topics = topic_shift[:3]
    declining_topics = topic_shift[-3:]
    rising_methods = method_shift[:3]

    lines = [
        "# Gibson Temporal Analysis",
        "",
        "## Dataset",
        "",
        f"- Source file: `DataProcessing/gibson_papers_coded_codex.json`",
        f"- Total papers: {len(rows)}",
        f"- Year range: {min(valid_years)}-{max(valid_years)}",
        f"- Papers with unknown year: {sum(1 for row in rows if numeric_year(row) is None)}",
        "",
        "## Main Temporal Pattern",
        "",
        f"- The annual volume peaks in {peak_year['Year']} with {peak_year['Total']} papers.",
        f"- Topic diversity, measured as inverse HHI/effective topics, peaks in {max_effective['Year']} at {max_effective['Effective topics']} effective topics.",
        f"- Within the 2020s, the most concentrated observed year is {min_recent['Year']} at {min_recent['Effective topics']} effective topics.",
        f"- Cross-disciplinary papers account for {cross_total} papers ({cross_total / len(rows):.1%}) across the full corpus.",
        "",
        "## Overall Topic and Method Centers",
        "",
        f"- Largest topic: {topic_counts.most_common(1)[0][0]} {TOPIC_LABELS[topic_counts.most_common(1)[0][0]]} ({topic_counts.most_common(1)[0][1]} papers).",
        f"- Largest method: {method_counts.most_common(1)[0][0]} {METHOD_LABELS[method_counts.most_common(1)[0][0]]} ({method_counts.most_common(1)[0][1]} papers).",
        "",
        "## Pre-2020 to 2020-2024 Topic Shifts",
        "",
        "| Direction | Code | Label | Change pp |",
        "|---|---|---|---:|",
    ]
    for row in rising_topics:
        lines.append(f"| Rising | {row['Code']} | {row['Label']} | {row['Change pp']} |")
    for row in reversed(declining_topics):
        lines.append(f"| Declining | {row['Code']} | {row['Label']} | {row['Change pp']} |")

    lines += [
        "",
        "## Pre-2020 to 2020-2024 Method Shifts",
        "",
        "| Code | Label | Change pp |",
        "|---|---|---:|",
    ]
    for row in rising_methods:
        lines.append(f"| {row['Code']} | {row['Label']} | {row['Change pp']} |")

    lines += [
        "",
        "## Interpretive Note",
        "",
        "- These metrics follow the logic of a field-evolution report: volume, concentration, effective category counts, rising/declining shares, method adoption, and cross-disciplinary integration.",
        "- The available data do not contain citation links or semantic embeddings, so citation-flow, UMAP, and semantic-distance analyses are intentionally not estimated here.",
    ]

    out = OUT_DIR / "temporal_analysis_summary.md"
    out.write_text("\n".join(lines) + "\n")
    return out


def main():
    rows = read_rows()
    annual = annual_summary(rows)
    topic_periods, topic_period = period_matrix(rows, "topic_category", TOPIC_ORDER, TOPIC_LABELS)
    method_periods, method_period = period_matrix(rows, "method_category", METHOD_ORDER, METHOD_LABELS)
    topic_decades, topic_decade = decade_shares(rows, "topic_category", TOPIC_ORDER, TOPIC_LABELS)
    method_decades, method_decade = decade_shares(rows, "method_category", METHOD_ORDER, METHOD_LABELS)
    topic_shift = early_late_shift(rows, "topic_category", TOPIC_ORDER, TOPIC_LABELS)
    method_shift = early_late_shift(rows, "method_category", METHOD_ORDER, METHOD_LABELS)

    outputs = [
        write_csv(
            OUT_DIR / "temporal_year_summary.csv",
            list(annual[0]),
            annual,
        ),
        write_csv(
            OUT_DIR / "temporal_period_topic_shares.csv",
            ["Code", "Label"]
            + [field for period in topic_periods for field in (f"{period} count", f"{period} share")]
            + ["Total"],
            topic_period,
        ),
        write_csv(
            OUT_DIR / "temporal_period_method_shares.csv",
            ["Code", "Label"]
            + [field for period in method_periods for field in (f"{period} count", f"{period} share")]
            + ["Total"],
            method_period,
        ),
        write_csv(
            OUT_DIR / "temporal_decade_topic_shares.csv",
            ["Code", "Label"]
            + [field for dec in topic_decades for field in (f"{dec} count", f"{dec} share")]
            + ["Total"],
            topic_decade,
        ),
        write_csv(
            OUT_DIR / "temporal_decade_method_shares.csv",
            ["Code", "Label"]
            + [field for dec in method_decades for field in (f"{dec} count", f"{dec} share")]
            + ["Total"],
            method_decade,
        ),
        write_csv(
            OUT_DIR / "temporal_topic_shift_pre2020_vs_2020s.csv",
            list(topic_shift[0]),
            topic_shift,
        ),
        write_csv(
            OUT_DIR / "temporal_method_shift_pre2020_vs_2020s.csv",
            list(method_shift[0]),
            method_shift,
        ),
        write_summary(rows, annual, topic_shift, method_shift),
    ]

    for out in outputs:
        print(out.relative_to(ROOT))


if __name__ == "__main__":
    main()
