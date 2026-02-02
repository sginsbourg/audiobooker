#!/usr/bin/env python
"""CLI script to generate audiobooks from PDF files."""
import argparse
from audiobooker.generator import AudiobookGenerator

def main():
    """Main CLI entry point for audiobook generation."""
    p = argparse.ArgumentParser()
    p.add_argument("pdf", nargs="?", help="input PDF file (English only) or empty for paste")
    p.add_argument("--out", default="out", help="output directory")
    p.add_argument("--voice", default="en-GB-RyanNeural", help="voice id (edge-tts)")
    p.add_argument("--chunk-size", type=int, default=4000)
    p.add_argument("--split-seconds", type=int, default=60 * 60)
    p.add_argument(
        "--paste",
        action="store_true",
        help="paste text directly from terminal (supports up to ~10k chars)",
    )
    p.add_argument(
        "--keep-chunks",
        action="store_true",
        help="do not delete intermediate audio chunks after assembly",
    )
    p.add_argument(
        "--openclaw",
        action="store_true",
        help="use OpenClaw AI for cleaning and chapter splitting",
    )
    args = p.parse_args()

    if not args.pdf and not args.paste:
        p.error("You must specify either a PDF file or --paste")
    if args.pdf and args.paste:
        p.error("Cannot specify both a PDF file and --paste")

    source = args.pdf
    is_text = False

    if args.paste:
        print(
            "Paste your text below (finish with Ctrl+Z + Enter on Windows, Ctrl+D on Unix):"
        )
        import sys
        text = sys.stdin.read()
        if not text.strip():
            print("No text provided. Exiting.")
            return
        print(f"\nProcessing {len(text)} characters of input text...")
        source = text
        is_text = True
    
    gen = AudiobookGenerator(
        output_dir=args.out,
        voice=args.voice,
        chunk_size=args.chunk_size,
        split_seconds=args.split_seconds,
        keep_chunks=args.keep_chunks,
        use_openclaw=args.openclaw
    )
    
    parts = gen.process(source, is_text=is_text)
    print("Created parts:", parts)

if __name__ == "__main__":
    main()
