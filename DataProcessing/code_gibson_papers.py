import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
METADATA = ROOT / "FirstTry(UnderstandingAllPapers)" / "Gibson_papers_2026-V1_metadata.json"
OUTPUT = ROOT / "gibson_papers_coded_codex.json"


def norm(text):
    return re.sub(r"\s+", " ", (text or "")).strip()


def words(text):
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def has_any(text, patterns):
    return any(re.search(pattern, text, flags=re.I) for pattern in patterns)


def clean_title_from_file(file_name):
    stem = Path(file_name).stem
    stem = re.sub(r"^\d+\s*-\s*", "", stem)
    stem = stem.replace("_", "'")
    stem = re.sub(r"\s+", " ", stem).strip(" -")
    if stem.upper() == stem:
        small = {"a", "an", "and", "as", "at", "for", "from", "in", "of", "on", "or", "the", "to", "under", "with"}
        parts = []
        for i, w in enumerate(stem.lower().split()):
            parts.append(w if i and w in small else w.capitalize())
        stem = " ".join(parts)
    return stem


def title_for(entry):
    file_title = clean_title_from_file(entry["file"])
    extracted = norm(entry.get("title"))
    if not extracted or "~" not in file_title:
        return file_title
    if "~" in file_title and extracted:
        return extracted
    if not extracted:
        return file_title
    file_words = set(words(file_title))
    extracted_words = set(words(extracted))
    overlap = len(file_words & extracted_words)
    # PDF extraction often captured journal headers instead of titles. Prefer the
    # filename title when the extracted title is very short or weakly overlapping.
    if len(extracted) < 25 or (file_words and overlap / max(1, min(len(file_words), len(extracted_words))) < 0.35):
        return file_title
    return extracted


METHOD_PATTERNS = {
    "M9": [r"mixed methods", r"sequential mixed", r"qualitative.*quantitative", r"interview.*survey", r"case.*survey"],
    "M7": [
        r"optimization", r"optimisation", r"optimal", r"game[- ]theor", r"stackelberg", r"simulation",
        r"mixed integer", r"integer program", r"mathematical model", r"routing model", r"inventory model",
        r"decision model", r"heuristic", r"metaheuristic", r"markov decision process", r"\bmdp\b",
    ],
    "M5": [r"\bsem\b", r"pls[- ]sem", r"structural equation", r"survey", r"questionnaire", r"partial least squares"],
    "M8": [
        r"regression", r"econometric", r"panel data", r"transaction data", r"logit", r"choice model",
        r"propensity score", r"markov chain", r"probabilistic", r"field data", r"empirical analysis",
        r"stochastic frontier", r"data analytics", r"random forest", r"machine learning",
        r"statistical\s*model", r"quantitative\s*analysis",
    ],
    "M6": [r"experiment", r"experimental", r"scenario[- ]based", r"field experiment", r"lab experiment", r"randomized"],
    "M3": [r"bibliometric", r"vosviewer", r"scimat", r"co[- ]citation", r"co[- ]occurrence", r"network visualization"],
    "M4": [r"case study", r"case studies", r"interview", r"qualitative", r"exploratory study", r"focus group"],
    "M2": [r"literature review", r"systematic review", r"narrative review", r"synthesi[sz]ed review", r"review paper"],
}


def classify_method(text, main_field, sub_field):
    blob = text.lower()
    title_blob = blob[:250]
    if has_any(title_blob, [r"special issue introduction", r"some reflections", r"\bconceptual\b"]):
        return "M1", 3
    if has_any(title_blob, [r"literature review", r"systematic review", r"research agenda", r"future research directions"]):
        return "M2", 3
    if has_any(blob, METHOD_PATTERNS["M9"]):
        return "M9", 3
    # Keep guide priority: formal models before surveys/regressions/experiments.
    for code in ["M7", "M5", "M8", "M6", "M3", "M4", "M2"]:
        if has_any(blob, METHOD_PATTERNS[code]):
            conf = 3 if code in {"M7", "M5", "M3", "M9"} else 2
            return code, conf
    sf = (sub_field or "").lower()
    mf = (main_field or "").lower()
    if "bibliometric" in sf:
        return "M3", 3
    if "mixed methods" in sf:
        return "M9", 3
    if "optimization" in sf or "inventory" in sf or "operations research" in mf:
        return "M7", 2
    if "consumer" in mf or "marketing" in mf:
        return "M5", 1
    return "M1", 1


TOPIC_PATTERNS = {
    "T8": [
        r"resilien", r"dynamic capabilit", r"capabilit(?:y|ies)", r"disruption", r"recovery",
        r"crisis", r"preparedness", r"responsiveness", r"redundanc", r"flexibility", r"collaboration",
        r"black swan", r"post[- ]covid", r"covid-19.*response",
    ],
    "T7": [
        r"performance", r"kpi", r"metric", r"measurement", r"assess", r"evaluation", r"framework for assessing",
        r"bibliometric", r"research trend", r"literature mapping", r"network visualization",
    ],
    "T3": [
        r"logistics", r"fulfil", r"fulfill", r"last[- ]mile", r"delivery", r"distribution network",
        r"routing", r"shipping", r"parcel", r"return", r"reverse logistics", r"ship[- ]from[- ]store",
        r"ship[- ]to[- ]store", r"click[- ]and[- ]collect", r"\bbops\b", r"\bbopis\b", r"pickup",
        r"pick[- ]up", r"pick up", r"warehouse", r"dark store", r"freight",
    ],
    "T4": [
        r"inventory", r"replenishment", r"order allocation", r"order quantity", r"pricing", r"price ",
        r"assortment", r"optimization", r"optimisation", r"game", r"stackelberg", r"channel competition",
        r"operational", r"operations", r"store selection", r"facility location", r"ordering decision",
        r"coupon", r"product availability", r"capacity",
    ],
    "T5": [
        r"information system", r"\bis\b", r"e-commerce", r"platform", r"mobile", r"app\b", r"ai\b",
        r"artificial intelligence", r"machine learning", r"\biot\b", r"data analytics", r"digital technolog",
        r"smart retail", r"rfid", r"chatbot", r"augmented reality", r"electronic shelf", r"digitalization",
    ],
    "T6": [
        r"strategy", r"business model", r"transformation", r"implementation", r"organization",
        r"organis", r"retail format", r"innovation", r"entry and expansion", r"transitioning",
        r"concept to implementation",
    ],
    "T2": [
        r"marketing", r"promotion", r"advertising", r"channel integration", r"touchpoint", r"coupon",
        r"cross[- ]channel", r"multi[- ]channel", r"omni[- ]channel retailing", r"retail marketing",
        r"brand", r"loyalty card", r"targeting",
    ],
    "T1": [
        r"consumer", r"customer", r"shopper", r"satisfaction", r"loyalty", r"purchase intention",
        r"continuance intention", r"behavior", r"behaviour", r"decision[- ]making", r"channel choice",
        r"journey", r"experience", r"patronage", r"willingness to pay", r"webrooming", r"showrooming",
    ],
}


def classify_topic(text, main_field, sub_field):
    blob = text.lower()
    title_blob = blob[: max(250, len(blob.split("abstract")[0]) if "abstract" in blob else 250)]
    sf = (sub_field or "").lower()
    mf = (main_field or "").lower()

    # Revised guide boundary rules.
    if has_any(blob, [r"resilien", r"disruption", r"recovery", r"dynamic capabilit", r"supply chain capabilit", r"covid-19.*response"]):
        return "T8", 3
    if "bibliometric" in sf or has_any(title_blob, [r"bibliometric", r"performance management", r"measur(?:e|ing|ement).*performance", r"\bmetrics?\b", r"research trends?", r"literature mapping"]):
        return "T7", 3
    if has_any(title_blob, [r"special issue introduction", r"some reflections"]):
        return "T2", 3

    subfield_map = {
        "consumer behavior": "T1",
        "customer experience & loyalty": "T1",
        "consumer decision-making process": "T1",
        "cross-generational & cross-cultural studies": "T1",
        "service management": "T1",
        "omni-channel & multi-channel marketing": "T2",
        "pricing & promotion strategy": "T2",
        "retail strategy": "T2",
        "digital marketing & social media": "T2",
        "logistics & fulfillment": "T3",
        "logistics & distribution networks": "T3",
        "optimization models": "T4",
        "inventory management": "T4",
        "inventory & procurement": "T4",
        "omni-channel supply chain coordination": "T4",
        "retail operations": "T4",
        "e-commerce & information systems": "T5",
        "digital transformation": "T5",
        "iot & smart technologies": "T5",
        "artificial intelligence & machine learning": "T5",
        "risk perception & privacy": "T5",
        "business model innovation": "T6",
        "organizational behavior & management": "T6",
        "competitive strategy & capabilities": "T6",
    }
    mapped = subfield_map.get(sf)

    scores = {}
    for code, patterns in TOPIC_PATTERNS.items():
        scores[code] = sum(2 if has_any(title_blob, [p]) else 0 for p in patterns)
        scores[code] += sum(1 for p in patterns if re.search(p, blob, flags=re.I))

    if mapped:
        scores[mapped] += 7
    elif "omni-channel retailing (general)" in sf:
        scores["T2"] += 2
        scores["T6"] += 1
    elif "mixed methods" in sf or "empirical research methods" in sf:
        # Method-oriented subfields should not dominate topic coding.
        pass

    if "operations research" in mf:
        scores["T4"] += 2
    if "information systems" in mf:
        scores["T5"] += 2
    if "consumer psychology" in mf:
        scores["T1"] += 2
    if "strategy" in mf or "organization" in mf:
        scores["T6"] += 2
    if has_any(title_blob, [r"special issue introduction", r"some reflections"]):
        scores["T2"] += 6

    # T3 vs T4: logistics/fulfillment object wins even when optimized, unless the
    # title is mainly pricing/inventory/assortment/channel competition.
    logistics_object = has_any(title_blob, TOPIC_PATTERNS["T3"])
    operations_object = has_any(title_blob, [r"inventory", r"pricing", r"assortment", r"channel competition", r"order quantity", r"replenishment"])
    if logistics_object and not operations_object:
        scores["T3"] += 5
    if operations_object:
        scores["T4"] += 4

    # Consumer outcome wins over generic marketing background.
    if has_any(title_blob, TOPIC_PATTERNS["T1"]) and has_any(blob, [r"satisfaction", r"loyalty", r"purchase", r"intention", r"behavior", r"behaviour", r"experience"]):
        scores["T1"] += 4

    # Narrow T7: generic "assessment/evaluation" in consumer papers is not enough.
    if scores["T7"] and not has_any(blob, [r"bibliometric", r"performance management", r"\bmetrics?\b", r"kpi", r"measur(?:e|ing|ement).*performance", r"literature mapping", r"research trend"]):
        scores["T7"] = min(scores["T7"], 2)

    best, score = max(scores.items(), key=lambda item: (item[1], ["T8", "T7", "T3", "T4", "T5", "T6", "T2", "T1"].index(item[0]) * -0.01))
    confidence = 3 if score >= 8 else 2 if score >= 4 else 1
    return best, confidence


METHOD_LABELS = {
    "M1": "Conceptual framework",
    "M2": "literature review",
    "M3": "bibliometric analysis",
    "M4": "case/interview qualitative evidence",
    "M5": "survey/SEM evidence",
    "M6": "experimental design",
    "M7": "optimization, simulation, or game-modeling",
    "M8": "statistical/econometric modeling",
    "M9": "mixed-methods design",
}

TOPIC_LABELS = {
    "T1": "customer experience/behavior",
    "T2": "omni-channel or multi-channel marketing",
    "T3": "logistics/fulfillment",
    "T4": "inventory, operations, or optimization",
    "T5": "digital technology/information systems",
    "T6": "strategy, business model, or organization",
    "T7": "performance, measurement, or bibliometric mapping",
    "T8": "resilience or organizational capability",
}


def coding_note(topic, method, title, text):
    topic_phrase = TOPIC_LABELS[topic]
    method_phrase = METHOD_LABELS[method]
    cues = []
    low = text.lower()
    for cue in [
        "structural equation", "PLS-SEM", "survey", "optimization", "game", "simulation",
        "bibliometric", "case study", "interview", "experiment", "regression", "mixed methods",
        "last-mile", "BOPS", "inventory", "pricing", "resilience", "dynamic capabilities",
        "customer experience", "loyalty", "digital transformation",
    ]:
        if cue.lower() in low:
            cues.append(cue)
    cue_text = "; cues include " + ", ".join(cues[:4]) if cues else ""
    return f"Classified as {topic_phrase} based on the paper's central research object; method coded as {method_phrase}{cue_text}."


def paper_id_counts(entries):
    base_ids = []
    for entry in entries:
        match = re.match(r"^(\d+)", entry["file"])
        base_ids.append(match.group(1) if match else Path(entry["file"]).stem)
    return Counter(base_ids)


def main():
    entries = json.loads(METADATA.read_text())
    counts = paper_id_counts(entries)
    seen = defaultdict(int)
    coded = []

    for entry in sorted(entries, key=lambda e: (int(re.match(r"^(\d+)", e["file"]).group(1)), e["file"].lower())):
        base = re.match(r"^(\d+)", entry["file"]).group(1)
        seen[base] += 1
        paper_id = base if counts[base] == 1 else f"{base}_{seen[base]}"
        title = title_for(entry)
        abstract = norm(entry.get("abstract"))
        text = " ".join([title, abstract, entry.get("main_field", ""), entry.get("sub_field", "")])
        topic, topic_conf = classify_topic(text, entry.get("main_field"), entry.get("sub_field"))
        method, method_conf = classify_method(text, entry.get("main_field"), entry.get("sub_field"))
        confidence = min(topic_conf, method_conf)
        if entry.get("main_field") == "(Unable to Read)" or len(abstract) < 80:
            confidence = 1
        elif confidence == 1:
            confidence = 2

        cross = entry.get("cross_disciplinary") or []
        coded.append(
            {
                "paper_id": paper_id,
                "title": title,
                "publication_year": (re.search(r"\d{4}", entry.get("publication_date", "")) or [""])[0],
                "main_field": entry.get("main_field", ""),
                "sub_field": entry.get("sub_field", ""),
                "cross_disciplinary_fields": cross,
                "cross_count": len(cross),
                "topic_category": topic,
                "method_category": method,
                "coding_confidence": confidence,
                "coding_notes": coding_note(topic, method, title, text),
            }
        )

    OUTPUT.write_text(json.dumps(coded, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {len(coded)} records to {OUTPUT.name}")
    print("Topic counts:", dict(Counter(item["topic_category"] for item in coded).most_common()))
    print("Method counts:", dict(Counter(item["method_category"] for item in coded).most_common()))
    print("Confidence counts:", dict(Counter(item["coding_confidence"] for item in coded).most_common()))


if __name__ == "__main__":
    main()
