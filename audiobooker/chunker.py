import regex as re
from typing import List

SENTENCE_RE = re.compile(r'(.+?[\.\?\!]["\']?\s+)', flags=re.S)


def split_into_sentences(text: str):
    parts = [m.group(1).strip() for m in SENTENCE_RE.finditer(text)]
    tail = SENTENCE_RE.sub('', text).strip()
    if tail:
        parts.append(tail)
    return parts if parts else [text]


def chunk_text(text: str, max_chars=4000, overlap=200) -> List[str]:
    sentences = split_into_sentences(text)
    chunks = []
    cur = ""
    for s in sentences:
        if len(cur) + len(s) + 1 <= max_chars:
            cur = (cur + " " + s).strip()
        else:
            chunks.append(cur)
            cur = " ".join(cur.split()[-overlap//5:]) + " " + s
    if cur:
        chunks.append(cur)
    return chunks
