#!/usr/bin/env python3
"""
Extract metadata from PDF papers in Gibson_papers_2026-V1 folder.
Fields: title, authors, publication_date, abstract, main_field, sub_field, cross_disciplinary
"""

import os
import re
import json
import pdfplumber

PAPERS_DIR = "/Users/jonahchou/development/BusinessResearch/Gibson_papers_2026-V1"
OUTPUT_FILE = "/Users/jonahchou/development/BusinessResearch/Gibson_papers_2026-V1_metadata.json"

# ─────────────────────────────────────────────
# Field classification rules
# ─────────────────────────────────────────────

FIELD_RULES = [
    # (main_field, sub_field, keywords)
    ("管理科學與作業研究", "最佳化模型", ["optim", "mathematical model", "linear program", "integer program", "stochastic model", "heuristic", "metaheuristic", "markov decision", "dynamic programming", "simulation model", "multi-period"]),
    ("管理科學與作業研究", "存貨管理", ["inventory", "replenishment", "order quantity", "safety stock", "lead time", "stock-out", "newsvendor", "eoq"]),
    ("管理科學與作業研究", "物流與配送網路", ["routing", "vehicle routing", "vrp", "last-mile", "distribution network", "last mile", "delivery network", "multi-tier", "shared capacity", "routing problem"]),
    ("供應鏈管理", "全通路供應鏈協調", ["supply chain coordination", "supply chain resilience", "channel coordination", "supply chain integration", "supply chain performance"]),
    ("供應鏈管理", "物流與履約", ["logistics", "fulfilment", "fulfillment", "parcel delivery", "shipping", "warehouse", "click-and-collect", "bops", "ship-from-store", "store fulfil"]),
    ("供應鏈管理", "庫存與採購", ["inventory strategy", "procurement", "sourcing", "fresh product", "perishable"]),
    ("行銷學", "消費者行為", ["consumer behav", "shopper behav", "purchase intention", "buying behav", "customer behav", "shopping behav", "customer journey", "shopper journey", "customer decision", "showroom"]),
    ("行銷學", "全通路與多通路行銷", ["omni-channel market", "omnichannel market", "multichannel market", "channel integration", "cross-channel", "channel strategy", "channel switching", "channel choice"]),
    ("行銷學", "價格與促銷策略", ["pricing decision", "price competition", "price strategy", "discount", "promotion", "coupon", "price optim", "revenue management"]),
    ("行銷學", "顧客體驗與忠誠度", ["customer experience", "customer loyalty", "customer satisfaction", "brand loyalty", "customer engagement", "service quality", "touchpoint"]),
    ("行銷學", "數位行銷與社群媒體", ["social media", "digital market", "online review", "e-wom", "influencer", "social commerce", "word-of-mouth", "online advertising"]),
    ("行銷學", "零售策略", ["retail strateg", "retail format", "store format", "assortment", "category management", "private label"]),
    ("資訊管理學", "數位轉型", ["digital transform", "digitali", "industry 4.0", "smart retail", "digital business", "digital technolog"]),
    ("資訊管理學", "電子商務與資訊系統", ["e-commerce", "ecommerce", "online platform", "information system", "erp", "big data", "analytics", "data-driven"]),
    ("資訊管理學", "人工智慧與機器學習", ["machine learning", "artificial intelligence", "deep learning", "neural network", "ai ", "prediction model", "forecasting model"]),
    ("資訊管理學", "物聯網與智慧技術", ["iot", "internet of things", "rfid", "blockchain", "automation", "robot"]),
    ("作業管理", "零售作業", ["retail operation", "store operation", "buy online", "bopus", "in-store fulfil", "store-based fulfil", "omni-channel operation"]),
    ("作業管理", "服務管理", ["service level", "service operation", "capacity planning", "service design", "service innovation"]),
    ("策略與組織管理", "商業模式創新", ["business model innov", "business model transform", "platform business", "ecosystem"]),
    ("策略與組織管理", "競爭策略與能力", ["competitive advantage", "dynamic capabilit", "resource-based", "strategic capabilit", "competitive strateg", "firm capabilit"]),
    ("策略與組織管理", "組織行為與管理", ["bricolage", "organizational behav", "firm performance", "sme", "small medium", "organizational capabilit"]),
    ("消費者心理學", "消費者決策歷程", ["decision making", "decision-making", "cognitive", "attitude", "perception", "motivation", "information processing", "mental model"]),
    ("消費者心理學", "跨世代與跨文化研究", ["generation y", "generation z", "millennial", "gen y", "gen z", "cross-cultural", "cultural differ"]),
    ("消費者心理學", "風險感知與隱私", ["risk percep", "privacy concern", "trust", "security concern", "uncertainty"]),
    ("計量方法", "文獻計量分析", ["bibliometric", "systematic review", "literature review", "meta-analysis", "review of literature"]),
    ("計量方法", "實證研究方法", ["structural equation", "sem ", "regression", "questionnaire", "survey data", "empirical study", "empirical research", "experiment"]),
    ("計量方法", "混合研究方法", ["mixed method", "qualitative", "case study", "interview", "ethnograph", "grounded theory"]),
]


def classify_field(text_lower: str):
    scores = {}
    sub_map = {}
    for main_field, sub_field, keywords in FIELD_RULES:
        for kw in keywords:
            if kw.lower() in text_lower:
                scores[main_field] = scores.get(main_field, 0) + 1
                if main_field not in sub_map:
                    sub_map[main_field] = {}
                sub_map[main_field][sub_field] = sub_map[main_field].get(sub_field, 0) + 1

    if not scores:
        return "商學院（待分類）", "全通路零售相關", []

    sorted_fields = sorted(scores.items(), key=lambda x: -x[1])
    main_field = sorted_fields[0][0]
    sub_scores = sub_map.get(main_field, {})
    sub_field = max(sub_scores, key=sub_scores.get) if sub_scores else "一般"

    cross = []
    if len(sorted_fields) >= 2:
        first_score = sorted_fields[0][1]
        for other_field, other_score in sorted_fields[1:3]:
            if other_score >= first_score * 0.4:
                cross.append(other_field)

    return main_field, sub_field, cross


# ─────────────────────────────────────────────
# Text extraction
# ─────────────────────────────────────────────

def extract_text_pages(pdf_path: str, max_pages: int = 3):
    """Return list of page texts, skipping ResearchGate cover pages."""
    pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            start = 0
            # Skip ResearchGate / Academia.edu cover pages
            if len(pdf.pages) > 1:
                p0 = pdf.pages[0].extract_text() or ""
                if "researchgate.net/publication" in p0.lower() or \
                   "academia.edu" in p0.lower() or \
                   "see discussions, stats" in p0.lower():
                    start = 1
            for page in pdf.pages[start: start + max_pages]:
                t = page.extract_text() or ""
                pages.append(t)
    except Exception:
        pass
    return pages


def full_text(pages):
    return "\n".join(pages)


# ─────────────────────────────────────────────
# Parser: Title
# ─────────────────────────────────────────────

SKIP_TITLE_PATTERNS = [
    r"^journal of", r"^international journal", r"^european journal",
    r"^volume\s+\d+", r"^vol\.", r"^issn", r"^\d{4}[,\s]",
    r"^https?://", r"^doi:", r"^to cite", r"^to link", r"^published",
    r"^submit", r"^article views", r"^view ", r"^full terms",
    r"^copyright", r"^received", r"^accepted", r"^available online",
    r"^contents list", r"^journal homepage", r"^\d+\s*$",
    r"^production,", r"^research article", r"^original article",
    r"^california management", r"^review of", r"^\d+ ", r"^page \d+",
    r"^\w+\s+\d{4},\s+vol\.", r"^the current issue",
]


def parse_title(pages, filename_title: str) -> str:
    text = full_text(pages)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Try "To cite this article: ... Title, Journal" pattern from page 0
    # e.g. "Chang et al. (2024) Title of Paper, Journal Name..."
    # Better: look for title before author line on page 1 for Elsevier/Tandfonline
    # Strategy: find first meaningful multi-word line that is NOT a journal/meta line
    title_parts = []
    for line in lines[:20]:
        ll = line.lower()
        if any(re.match(pat, ll) for pat in SKIP_TITLE_PATTERNS):
            continue
        # Stop at author/affiliation lines
        if re.search(r'\buniversity\b|\binstitute\b|\bdepartment\b|\bschool of\b|\bcollege\b', ll):
            break
        # Stop at abstract/keywords/intro
        if re.search(r'^(abstract|keywords|introduction|summary|highlights)\b', ll):
            break
        # stop at article-info marker (Elsevier two-column)
        if re.search(r'a r t i c l e|article history|article info', ll):
            break
        # must look like a title (enough words, starts with uppercase)
        if len(line.split()) >= 3 and re.match(r'[A-Z\d]', line):
            title_parts.append(line)
            # stop if we collected enough characters
            if sum(len(p) for p in title_parts) > 40:
                break

    title = " ".join(title_parts).strip()
    title = re.sub(r'\s+', ' ', title)

    # Reject if too short or looks like a journal header
    if len(title) < 12:
        return filename_title
    return title


# ─────────────────────────────────────────────
# Parser: Authors
# ─────────────────────────────────────────────

def parse_authors(pages) -> list:
    text = full_text(pages)

    # --- Strategy 1: "To cite this article: Author A, Author B (Year) Title, Journal" ---
    cite_match = re.search(
        r"To cite this article:\s*(.+?)\s*\(\d{4}\)",
        text, re.I | re.S
    )
    if cite_match:
        raw = re.sub(r'\s+', ' ', cite_match.group(1)).strip()
        parts = re.split(r'\s*(?:,\s*(?=[A-Z])|\band\b|&)\s*', raw)
        parts = [p.strip() for p in parts if p.strip() and 4 < len(p.strip()) < 60]
        if parts:
            return parts

    # --- Strategy 2: Elsevier / generic authors ---
    # Case A: "Firstname Lastname, University Affiliation" on same line → extract name only
    # Case B: "Firstname Lastname, Firstname Lastname" without affiliation on same line
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    author_lines = []
    for line in lines[:50]:
        ll = line.lower()
        if any(re.match(pat, ll) for pat in SKIP_TITLE_PATTERNS):
            continue
        if re.search(r'^(abstract|a\s*b\s*s\s*t\s*r\s*a\s*c\s*t|keywords|summary|introduction|purpose)\b', ll):
            break
        if re.search(r'article history|article info|a r t i c l e', ll):
            break

        # Case A: line starts with "Firstname Lastname* ," followed by affiliation keyword
        affil_match = re.match(
            r'^([A-Z][a-zéèêëàâîïôùûüç\-]+(?:[\s\-][A-Z\-][a-zéèêëàâîïôùûüç\-]+){1,3})[\*\d\s]*,\s*(?:[A-Z])',
            line
        )
        if affil_match and re.search(r'university|institute|department|school|college|tech|politecnico|univer', ll):
            name = re.sub(r'[\*\d]', '', affil_match.group(1)).strip()
            if 4 < len(name) < 50:
                author_lines.append(name)
            continue  # don't break, more authors may follow

        # Stop at lines that ARE affiliations (no name pattern at start)
        if re.search(r'\buniversity\b|\binstitute\b|\bdepartment\b|\bschool of\b|\bcollege\b', ll):
            if not re.match(r'^[A-Z][a-z]+\s+[A-Z]', line):
                break

        # Case B: pure name list line (no affiliation on same line)
        # Must look like capitalized name(s), reasonably short
        if re.search(r'\b[A-Z][a-zéèêëàâîïôùûüç\-]+[\s\-][A-Z][a-zéèêëàâîïôùûüç\-]+\b', line) or \
           re.search(r'\b[A-Z]\.\s+[A-Z][a-z]+\b', line):
            if not re.search(r'\buniversity\b|\bdepartment\b|\bschool\b|\binstitute\b|\btech\b', ll):
                clean = re.sub(r'[\*]|(?<=[a-zA-Z])\d+', '', line).strip()
                if 4 < len(clean) < 150:
                    author_lines.append(clean)

    if author_lines:
        combined = " ".join(author_lines)
        parts = re.split(r'\s*(?:,\s*(?=[A-Z])|\band\b\s*(?=[A-Z])|&\s*(?=[A-Z])|;\s*(?=[A-Z]))\s*', combined)
        parts = [p.strip() for p in parts if p.strip() and 3 < len(p.strip()) < 60
                 and re.search(r'^[A-Z]', p)
                 and not re.search(r'\buniversity\b|\bdepartment\b|\bschool\b|\binstitute\b', p, re.I)
                 and len(p.split()) >= 2]  # must be at least two words (first + last name)
        if parts:
            return parts

    # --- Strategy 3: Emerald compact format (no spaces) — name before affiliation ---
    # e.g. "JasonIanPallant,SeanJamesSands,...SwinburneUniversity"
    emerald = re.findall(r'([A-Z][a-z]+(?:[\s\-][A-Z][a-z]+)+)\s*,?\s*[A-Z][a-z].*?[Uu]niversity', text)
    if emerald:
        return list(dict.fromkeys(emerald))[:6]

    # --- Strategy 4: ResearchGate "N authors, including: Name" ---
    rg = re.search(r'\d+\s+authors?,\s+including:\s*\n([^\n]+)', text, re.I)
    if rg:
        return [rg.group(1).strip()]

    # --- Strategy 5: JSTOR "Author(s): Name A and Name B" ---
    jstor = re.search(r'Author\(s\):\s*(.+?)(?:\n|Source:)', text, re.I)
    if jstor:
        raw = jstor.group(1).strip()
        parts = re.split(r'\s+and\s+|,\s*', raw)
        parts = [p.strip() for p in parts if p.strip() and len(p.strip()) < 60]
        if parts:
            return parts

    return ["(未擷取到作者)"]


# ─────────────────────────────────────────────
# Parser: Date
# ─────────────────────────────────────────────

def parse_date(text: str) -> str:
    patterns = [
        r"Published online[:\s]+\d{1,2}\s+\w+\s+(\d{4})",
        r"Available online[:\s]+\d{1,2}\s+\w+\s+(\d{4})",
        r"Published[:\s]+\d{1,2}\s+\w+\s+(\d{4})",
        r"To cite this article:.+?\((\d{4})\)",
        r"\b(20\d{2}),\s*VOL",
        r"Volume\s+\d+.*?,?\s*(\d{4})",
        r"Accepted\s+\d+\s+\w+\s+(\d{4})",
        r"Accepted\s+\w+\s+\d+,\s+(\d{4})",
        r"Received.+?Accepted.+?(\d{4})",
        r"\b(20\d{2}),\s*\d+\(\d+\)",  # 2024, 75(4)
        r"\b(20\d{2})\b",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I | re.S)
        if m:
            return m.group(1).strip()
    return "(未擷取到日期)"


# ─────────────────────────────────────────────
# Parser: Abstract
# ─────────────────────────────────────────────

ABSTRACT_STOP = re.compile(
    r'\n\s*(?:KEYWORDS?|KEYwORdS|Key words|HIGHLIGHTS?|JEL|1\.\s+INTRO|Introduction|INTRODUCTION|©\s*20)',
    re.I
)


def parse_abstract(text: str) -> str:
    # --- Pattern 1: explicit ABSTRACT / Abstract section header (newline after) ---
    m = re.search(
        r'(?:^|\n)\s*(?:a\s*b\s*s\s*t\s*r\s*a\s*c\s*t|ABSTRACT|Abstract)\s*\n([\s\S]{50,2500})',
        text, re.I
    )
    if m:
        snippet = m.group(1)
        stop = ABSTRACT_STOP.search(snippet)
        if stop:
            snippet = snippet[:stop.start()]
        snippet = re.sub(r'\s+', ' ', snippet).strip()
        if len(snippet) > 60:
            return snippet[:2000]

    # --- Pattern 2: Elsevier two-column spaced "a b s t r a c t" marker ---
    m2 = re.search(r'a\s*b\s*s\s*t\s*r\s*a\s*c\s*t\s*\n([\s\S]{50,2500})', text, re.I)
    if m2:
        snippet = m2.group(1)
        # Strip leading "Article history:" date noise (Elsevier two-column layout)
        snippet = re.sub(r'^Article\s*history[:\s]+', '', snippet, flags=re.I)
        snippet = re.sub(r'(?:Received|Accepted|Available|Revised)\s+\d{1,2}\s+\w+\s+\d{4}\.?\s*', '', snippet)
        stop = ABSTRACT_STOP.search(snippet)
        if stop:
            snippet = snippet[:stop.start()]
        snippet = re.sub(r'\s+', ' ', snippet).strip()
        if len(snippet) > 60:
            return snippet[:2000]

    # --- Pattern 3: Elsevier compact (no spaces) "a r t i c l e i n f o ... ArticleHistory: <abstract text>" ---
    # In compact Elsevier, abstract follows "ArticleHistory:" or "Articlehistory:"
    m3 = re.search(r'[Aa]rticle\s*[Hh]istory[:\s]+(.{100,2500}?)(?:[Kk]eywords?|©|\Z)', text, re.S)
    if m3:
        snippet = re.sub(r'\s+', ' ', m3.group(1)).strip()
        # Remove date artifacts (Received/Accepted)
        snippet = re.sub(r'(?:Received|Accepted|Available|Revised)\s+\d{1,2}\s+\w+\s+\d{4}\.?\s*', '', snippet)
        if len(snippet) > 60:
            return snippet[:2000]

    # --- Pattern 4: SUMMARY header (e.g., CMR / SAGE) ---
    m4 = re.search(r'(?:^|\n)\s*SUMMARY\s*\n([\s\S]{50,2000})', text, re.I)
    if m4:
        snippet = m4.group(1)
        stop = re.search(r'\n[A-Z]{4,}|\nKeyword|\n\d+\.', snippet)
        if stop:
            snippet = snippet[:stop.start()]
        snippet = re.sub(r'\s+', ' ', snippet).strip()
        if len(snippet) > 60:
            return snippet[:2000]

    # --- Pattern 5: Emerald "Purpose – ..." inline abstract ---
    m5 = re.search(r'(?:Purpose\s*[–—-]+\s*)(.{60,2000}?)(?:Design/methodology|Findings|Keywords?|©)', text, re.S | re.I)
    if m5:
        snippet = re.sub(r'\s+', ' ', m5.group(0)).strip()
        if len(snippet) > 60:
            return snippet[:2000]

    # --- Pattern 6: JSTOR / MIS Quarterly — first substantial paragraph after author block ---
    # Look for paragraph after author affiliation lines
    m6 = re.search(r'(?:U\.S\.A\.|U\.K\.|USA|UK)\s*\{[^}]+\}\s*\n+([\s\S]{100,2000})', text)
    if m6:
        snippet = re.sub(r'\s+', ' ', m6.group(1)).strip()
        stop = re.search(r'\n[A-Z]{3,}|\nKeyword|\n\d+\s+Introduction', snippet)
        if stop:
            snippet = snippet[:stop.start()]
        if len(snippet) > 60:
            return snippet[:2000]

    # --- Fallback: keyword "abstract" inline (e.g., Emerald compact) ---
    idx = text.lower().find("abstract")
    if idx != -1:
        snippet = text[idx + 8: idx + 2500].strip()
        snippet = re.sub(r'\s+', ' ', snippet)
        if len(snippet) > 60:
            return snippet[:2000]

    return "(未擷取到摘要)"


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def filename_to_title(filename: str) -> str:
    name = os.path.splitext(filename)[0]
    name = re.sub(r'^\d+\s*-\s*', '', name)
    return name.title()


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def process_all():
    files = sorted([f for f in os.listdir(PAPERS_DIR) if f.lower().endswith(".pdf")])
    results = []
    total = len(files)

    for i, fname in enumerate(files):
        pdf_path = os.path.join(PAPERS_DIR, fname)
        fn_title = filename_to_title(fname)

        print(f"[{i+1}/{total}] {fname[:70]}")

        pages = extract_text_pages(pdf_path, max_pages=3)
        text = full_text(pages)

        if not text.strip():
            results.append({
                "file": fname,
                "title": fn_title,
                "authors": ["(無法讀取)"],
                "publication_date": "(無法讀取)",
                "abstract": "(無法讀取)",
                "main_field": "(無法讀取)",
                "sub_field": "(無法讀取)",
                "cross_disciplinary": []
            })
            continue

        title = parse_title(pages, fn_title)
        authors = parse_authors(pages)
        date = parse_date(text)
        abstract = parse_abstract(text)

        classify_text = (title + " " + abstract).lower()
        main_field, sub_field, cross = classify_field(classify_text)

        results.append({
            "file": fname,
            "title": title,
            "authors": authors,
            "publication_date": date,
            "abstract": abstract,
            "main_field": main_field,
            "sub_field": sub_field,
            "cross_disciplinary": cross
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone. {total} papers -> {OUTPUT_FILE}")
    return results


if __name__ == "__main__":
    results = process_all()

    # Quality stats
    missing_auth = sum(1 for d in results if "未擷取" in str(d["authors"]))
    missing_abs  = sum(1 for d in results if "未擷取" in d["abstract"])
    missing_date = sum(1 for d in results if "未擷取" in d["publication_date"])
    print(f"\nQuality stats ({len(results)} papers):")
    print(f"  Missing authors : {missing_auth}")
    print(f"  Missing abstract: {missing_abs}")
    print(f"  Missing date    : {missing_date}")