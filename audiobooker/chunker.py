

"""Text chunking utilities for natural sentence-aware splitting."""

"""Text chunking utilities for natural sentence-aware splitting."""

import regex as re

SENTENCE_RE = re.compile(r'(.+?[\.\?\!]["\']?\s+)', flags=re.S)


def split_into_sentences(text: str) -> list[str]:
    """Return a list of sentences found in `text` using a lightweight regex."""
    parts = [m.group(1).strip() for m in SENTENCE_RE.finditer(text)]
    tail = SENTENCE_RE.sub("", text).strip()
    if tail:
        parts.append(tail)
    return parts if parts else [text]


def chunk_text(text: str, max_chars: int = 4000, overlap: int = 200) -> list[str]:
    """Split `text` into chunks not exceeding `max_chars`, with `overlap` approx characters of overlap.

    This preserves sentence boundaries to avoid mid-sentence truncation.
    """
    sentences = split_into_sentences(text)
    chunks: list[str] = []
    cur = ""
    for s in sentences:
        if len(cur) + len(s) + 1 <= max_chars:
            cur = (cur + " " + s).strip()
        else:
            chunks.append(cur)
            cur = " ".join(cur.split()[-overlap // 5 :]) + " " + s
    if cur:
        chunks.append(cur)
    return chunks
