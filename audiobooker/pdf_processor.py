import re
from dataclasses import dataclass
from typing import List, Optional

import pdfplumber


@dataclass
class PageContent:
    page_no: int
    text: str
    tables: List[str]
    image_paths: List[str]


def is_index_like(text: str) -> bool:
    t = text.lower()
    if "index" in t.splitlines()[:3]:
        return True
    lines = [line.strip() for line in t.splitlines() if line.strip()]
    short_lines = sum(1 for line in lines[:30] if re.search(r"\d{1,4}$", line))
    return short_lines > 6


def detect_repeated_lines(pages_text: List[str], threshold=0.5):
    from collections import Counter

    counts = Counter()
    for t in pages_text:
        lines = [line.strip() for line in t.splitlines() if line.strip()]
        if lines:
            counts.update({lines[0], lines[-1]})
    repeated = {
        line for line, count in counts.items() if count / len(pages_text) >= threshold
    }
    return repeated


def summarize_table(table):
    if not table:
        return ""
    header = table[0]
    rows = table[1:6]
    lines = []
    for r in rows:
        pairs = [f"{h}: {c}" for h, c in zip(header, r) if c and c.strip()]
        if pairs:
            lines.append("; ".join(pairs))
    return "Table summary: " + (" | ".join(lines) if lines else "no readable rows")


def extract_pages(pdf_path: str, image_dir: Optional[str] = None):
    pages_text = []
    pages_meta = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages_text.append(text)
            pages_meta.append(page)
    repeated = detect_repeated_lines(pages_text)
    for i, (text, page) in enumerate(zip(pages_text, pages_meta), start=1):
        if is_index_like(text):
            continue
        lines = [
            line
            for line in text.splitlines()
            if line.strip() and line.strip() not in repeated
        ]
        cleaned = "\n".join(lines)
        tables = []
        for t in page.extract_tables() or []:
            tables.append(summarize_table(t))
        images = []
        # image extraction left minimal for now
        yield PageContent(page_no=i, text=cleaned, tables=tables, image_paths=images)
