# Audiobooker

A minimal, practical toolkit to convert English-language PDFs into narrated audiobooks with smart processing.

---

## User manual ✅

### Overview
`audiobooker` extracts text from PDF pages, removes repeated headers/footers and index pages, summarizes tables, optionally captions images, and converts the cleaned text into natural-sounding TTS audio using a pluggable provider. The output is a set of audio parts and optionally an assembled audiobook file.

### Prerequisites
- Windows (tested) or other OS with Python 3.11+
- Tesseract (for OCR on scanned PDFs)
- FFmpeg (audio assembly and conversions)
- Python virtual environment (recommended)

System install examples (Windows):
```powershell
# using winget
winget install --id tesseract-ocr.tesseract -e --accept-package-agreements --accept-source-agreements
winget install --id Gyan.FFmpeg.Essentials -e --accept-package-agreements --accept-source-agreements
```

### Quick start
1. Create and activate a virtual environment:
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```
2. Install Python dependencies:
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
3. Run the generator:
```powershell
python scripts/generate_audiobook.py <input.pdf> --out ./book_out --voice en-GB-RyanNeural
```

### Command-line options
- `pdf` (positional): PDF file path (English-only)
- `--out`: Output directory (default: `out`)
- `--voice`: Edge TTS voice ID (default: `en-US-GuyNeural`)
- `--chunk-size`: Max characters per TTS chunk (default: 4000)
- `--split-seconds`: Split audiobook parts every N seconds (default: 3600)

### How it handles tricky cases
- Large PDFs: processed page-by-page and chunked to stay within TTS limits.
- Scanned pages: Tesseract OCR is used via `pytesseract`.
- Repeating headers/footers: detected and removed across pages to avoid reading repeated content.
- Index / TOC pages: heuristics detect index-like pages and skip them.
- Tables: summarized into short human-readable rows (first several rows are converted into text summaries).
- Images: left as TODO—image captioning using BLIP/transformers can be enabled later.

### Advanced usage and customization
- Swap TTS providers by implementing the `TTSProvider` interface in `audiobooker/tts_providers.py`.
- To use Azure or ElevenLabs TTS, add a provider class that implements `synthesize(text, out_path, voice)`.
- For better NLP (table summarization, smart chaptering, image captioning), install `transformers` and `torch` and enable the optional modules in the code.

### Troubleshooting
- "tesseract not found": add its install folder (e.g., `C:\Program Files\Tesseract-OCR`) to PATH or reinstall via winget.
- "ffmpeg not found": confirm FFmpeg bin folder is on PATH.
- TTS errors: confirm internet access and provider credentials if using paid/closed-source TTS.

### Contributing
- Create issues and pull requests on the `audiobooker` GitHub repo. Keep changes small and add tests where possible.

---

If you want, I can now initialize the repo (create `.gitignore`, commit files) and create a **public** GitHub repository named `audiobooker` and push it. Let me know if you want a specific license (MIT, Apache-2.0, etc.).
