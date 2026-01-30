import fitz
from pathlib import Path

from audiobooker.chunker import chunk_text
from audiobooker.pdf_processor import extract_pages


def make_sample_pdf(path: Path) -> None:
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
    doc.save(str(path))


class MockTTSProvider:
    """A simple mock TTS provider that writes a small non-empty file."""

    def synthesize(self, text: str, out_path: str, voice: str | None = None) -> None:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        # write a tiny non-empty file (not a real mp3, but sufficient for smoke tests)
        p.write_bytes(b"FAKE_MP3_CONTENT" + str(len(text)).encode())


def test_smoke_creates_nonempty_mp3(tmp_path: Path) -> None:
    """End-to-end smoke test (offline): ensures mp3 parts are produced and non-empty."""
    pdf = tmp_path / "new.pdf"
    make_sample_pdf(pdf)

    outdir = tmp_path / "out"
    tts = MockTTSProvider()

    created = []
    page_cnt = 0
    for page in extract_pages(str(pdf), None):
        page_cnt += 1
        text = page.text
        for t in page.tables:
            text += "\n\n" + t
        chunks = chunk_text(text, max_chars=4000)
        for i, c in enumerate(chunks):
            fname = outdir / f"p{page_cnt:04d}_c{i:03d}.mp3"
            tts.synthesize(c, str(fname), voice="test")
            created.append(fname)

    assert created, "No audio parts were generated"
    for f in created:
        assert f.exists(), f"Missing file: {f}"
        assert f.stat().st_size > 0, f"Empty file: {f}"
