from pathlib import Path

import fitz

p = Path(__file__).resolve().parents[1] / "pdfs"
p.mkdir(exist_ok=True)
doc = fitz.open()
# pages with headers/footers and table
for i in range(1, 4):
    page = doc.new_page()
    header = f"My Book Title - Chapter {i}"
    footer = f"Page {i} - Confidential"
    page.insert_text((72, 40), header, fontsize=10)
    page.insert_text((72, 750), footer, fontsize=10)
    body = (
        "This is sample content for testing the audiobook generator. "
        "It should be read aloud by the TTS engine in a natural-sounding voice.\n\n"
        "Here is a small table:\nName | Value\nAlpha | 123\nBeta | 456\nGamma | 789\n\n"
        "End of sample page."
    )
    page.insert_textbox(fitz.Rect(72, 72, 540, 720), body, fontsize=11)
# index-like page
page = doc.new_page()
page.insert_text((72, 40), "Index")
idx_text = "alpha................................1\nbeta................................2\ngamma................................3\n"
page.insert_textbox(fitz.Rect(72, 72, 540, 720), idx_text, fontsize=11)
out = p / "new.pdf"
doc.save(str(out))
print("WROTE", out)
