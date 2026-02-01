
"""Text cleaning utilities for TTS preparation."""

import regex as re


def clean_markdown(text: str) -> str:
    """Remove markdown syntax and special characters that degrade TTS quality."""
    if not text:
        return ""

    # 1. Remove Markdown links [text](url) -> text
    # We do this first so we don't break the brackets/parentheses with other cleans
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # 2. Remove Markdown images ![alt](url) -> ''
    text = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', text)

    # 3. Remove header markers (#, ##, ###) at start of lines
    # (?m)^ means multiline mode start of line
    text = re.sub(r'(?m)^#+\s*', '', text)

    # 4. Remove bold/italic markers (*, **, _, __)
    # We just strip the logic chars. 
    # Note: simple stripping of * and _ handles both *italic* and **bold**
    # We replace with empty string.
    text = re.sub(r'[\*_`]', '', text)

    # 5. Remove horizontal rules (---, ***, ___)
    text = re.sub(r'(?m)^[-*_]{3,}\s*$', '', text)

    # 6. Handle tables: replace | with , to make it read better (pause instead of "pipe")
    # Also ignore the separator row like | --- | --- |
    text = re.sub(r'(?m)^\|?\s*[-: ]+\|\s*[-: \|]*$', '', text) # Remove separator lines
    text = text.replace('|', ',')

    # 7. Remove other common markdown oddities or special chars
    # ~ (strikethrough)
    text = text.replace('~', '')
    
    # 8. Collapse whitespace
    # Replace multiple spaces with one
    text = re.sub(r' +', ' ', text)
    # Replace 3+ newlines with 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()
