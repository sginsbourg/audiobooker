"""PDF extraction utilities: clean pages, detect headers/footers, and summarize tables."""

import re
from dataclasses import dataclass
from typing import List, Optional
from collections import Counter

import pdfplumber


@dataclass
class PageContent:
    page_no: int
    text: str
    tables: List[str]
    image_paths: List[str]


def is_index_like(text: str) -> bool:
    """Return True if the page text looks like an index/TOC page."""
    t = text.lower()
    if "index" in t.splitlines()[:3]:
        return True
    lines = [line.strip() for line in t.splitlines() if line.strip()]
    short_lines = sum(1 for line in lines[:30] if re.search(r"\d{1,4}$", line))
    return short_lines > 6


def detect_repeated_lines(pages_text: List[str], threshold=0.5):
    """Detect lines that repeat across pages (likely headers/footers)."""

    counts: Counter[str] = Counter()
    for t in pages_text:
        lines = [line.strip() for line in t.splitlines() if line.strip()]
        if lines:
            counts.update({lines[0], lines[-1]})
    repeated = {
        line for line, count in counts.items() if count / len(pages_text) >= threshold
    }
    return repeated


def summarize_table(table):
    """Make a short, human-readable summary from a small table.

    Only include the header and first few rows to keep summaries concise.
    """
    if not table:
        return ""
    header = table[0]
    rows = table[1:6]
    lines: list[str] = []
    for r in rows:
        pairs = [f"{h}: {c}" for h, c in zip(header, r) if c and c.strip()]
        if pairs:
            lines.append("; ".join(pairs))
    return "Table summary: " + (" | ".join(lines) if lines else "no readable rows")


def extract_pages(pdf_path: str, _image_dir: Optional[str] = None):
    """Yield PageContent entries for all non-index pages in the PDF file."""
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
        tables: list[str] = []
        for t in page.extract_tables() or []:
            tables.append(summarize_table(t))
        images: list[str] = []
        # image extraction left minimal for now
        yield PageContent(page_no=i, text=cleaned, tables=tables, image_paths=images)
