#!/usr/bin/env python
"""CLI script to generate audiobooks from PDF files."""
import argparse
from pathlib import Path

from pydub import AudioSegment

from audiobooker.chunker import chunk_text
from audiobooker.pdf_processor import extract_pages
from audiobooker.tts_providers import EdgeTTSProvider


def assemble_audio(parts, out_file):
    combined = None
    for p in parts:
        seg = AudioSegment.from_file(p)
        combined = seg if combined is None else (combined + seg)
    if combined is None:
        raise ValueError("No audio parts to assemble")
    combined.export(out_file, format=Path(out_file).suffix.replace(".", ""))
    return out_file


# pylint: disable=too-many-locals
def main():
    """Main CLI entry point for audiobook generation.

    This function is intentionally compact; pylint's `too-many-locals` rule is disabled
    for readability and to avoid premature refactors during development.
    """
    p = argparse.ArgumentParser()
    p.add_argument("pdf", help="input PDF file (English only)")
    p.add_argument("--out", default="out", help="output directory")
    p.add_argument("--voice", default="en-GB-RyanNeural", help="voice id (edge-tts)")
    p.add_argument("--chunk-size", type=int, default=4000)
    p.add_argument("--split-seconds", type=int, default=60 * 60)
    args = p.parse_args()

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    tts = EdgeTTSProvider(voice=args.voice)

    chunk_files = []
    page_cnt = 0
    for page in extract_pages(args.pdf, str(outdir / "images")):
        page_cnt += 1
        text = page.text
        for t in page.tables:
            text += "\n\n" + t
        chunks = chunk_text(text, max_chars=args.chunk_size)
        for i, c in enumerate(chunks):
            fname = outdir / f"p{page_cnt:04d}_c{i:03d}.mp3"
            tts.synthesize(c, str(fname), voice=args.voice)
            chunk_files.append(str(fname))

    parts = []
    running_secs = 0
    group = []
    for f in chunk_files:
        dur = AudioSegment.from_file(f).duration_seconds
        if running_secs + dur > args.split_seconds and group:
            idx = len(parts) + 1
            outpath = outdir / f"audiobook_part_{idx:03d}.mp3"
            assemble_audio(group, outpath)
            parts.append(str(outpath))
            group = []
            running_secs = 0
        group.append(f)
        running_secs += dur
    if group:
        idx = len(parts) + 1
        outpath = outdir / f"audiobook_part_{idx:03d}.mp3"
        assemble_audio(group, outpath)
        parts.append(str(outpath))

    print("Created parts:", parts)


if __name__ == "__main__":
    main()
