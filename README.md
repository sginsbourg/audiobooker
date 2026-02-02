# Audiobooker

![CI](https://github.com/sginsbourg/audiobooker/actions/workflows/ci.yml/badge.svg)

A minimal, practical toolkit to convert English-language PDFs into narrated audiobooks with smart processing.

---

## User manual ✅

### Overview

`audiobooker` is an intelligent PDF-to-audiobook converter. It leverages **OpenClaw (AI Assistant)** for high-quality text cleaning, chapter identification, and coherent audio part management. It extracts text from PDF pages, removes noise, summarizes tables, and converts the results into natural-sounding TTS audio.

### OpenClaw Integration 🦞

Audiobooker is integrated with [OpenClaw](https://github.com/openclaw/openclaw), a personal AI assistant. When the `--openclaw` flag is used, OpenClaw performs the following tasks:

1. **AI-Powered Cleaning**: OpenClaw identifies and removes repetitive headers, footers, page numbers, and institutional boilerplate that standard filters might miss.
2. **Smart Chaptering**: OpenClaw analyzes document flow to split long texts into logical chapters.
3. **Intelligent Audio Management**: OpenClaw organizes the final audio files according to these rules:
    * **No chapter is split** across two adjacent audio files.
    * One audio file may contain **multiple small chapters**.
    * Chapters are kept intact to ensure a natural listening experience.

### Workflow and File Organization 📂

Audiobooker follows a strict organization and cleanup procedure for every generation:

1. **Project Isolation**: For every PDF processed, a new subfolder is created within your output directory (default: `out/`), named after the original PDF file.
2. **Audio Creation**: All generated audio files (parts) are saved directly into this project folder.
3. **Automatic Cleanup**: All temporary audio chunks (`.mp3`) used during the synthesis process are automatically removed once the final parts are assembled.
4. **Source Archiving**: At the end of a successful generation, the original PDF file is **moved** into the project folder alongside the audio files for archival.

### Prerequisites

* Windows (tested) or other OS with Python 3.11+
* Tesseract (for OCR on scanned PDFs)
* FFmpeg (audio assembly and conversions)
* **OpenClaw**: Cloned in the `openclaw` directory at the root of this repo.
* **Node.js 22+** and **pnpm**: Required to run OpenClaw.
* **LM Studio**: Running locally (or a similar provider) to power OpenClaw's reasoning.
* **SMTP Configuration (Optional)**: For email notifications, set the following environment variables in a `.env` file at the root:
  * `SMTP_SERVER` (e.g., `smtp.gmail.com`)
  * `SMTP_PORT` (e.g., `587`)
  * `SMTP_USER` (your email)
  * `SMTP_PASSWORD` (your app-specific password)
  * `SENDER_EMAIL` (the "from" address)

### Quick start

1. **Activate Environment**:

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

1. **Install Dependencies**:

```powershell
python -m pip install -r requirements.txt
```

1. **Setup OpenClaw**:

```powershell
cd openclaw
pnpm install
pnpm build
# See openclaw/README.md for configuring your AI model/LM Studio connection
```

1. **Run with AI features** (enabled by default):

```powershell
$env:PYTHONPATH='.'; python scripts/generate_audiobook.py <input.pdf> --out ./book_out
```

### Command-line options

* `pdf` (positional): PDF file path or empty for paste.
* `--no-openclaw`: **Disable AI-powered cleaning, chaptering, and audio management.**
* `--out`: Output directory (default: `out`).
* `--voice`: Edge TTS voice ID (default: `en-GB-RyanNeural`).
* `--chunk-size`: Max characters per TTS chunk (default: 4000).
* `--split-seconds`: Target duration (seconds) per audio part (default: 3600).
* `--keep-chunks`: Keep intermediate audio files.

### Testing

* Run the smoke tests: `pytest -q`
* The smoke test uses an offline `MockTTSProvider` and asserts the generator creates non-empty MP3 files.

### Advanced usage

* **Custom TTS**: Implement the `TTSProvider` interface in `audiobooker/tts_providers.py`.
* **OpenClaw Skills**: You can extend OpenClaw's capabilities by adding new skills to its internal registry.

### Troubleshooting

* **OpenClaw not found**: Ensure `openclaw` is cloned in the root and `pnpm` is installed.
* **Tesseract/FFmpeg**: Confirm these are on your system PATH.
* **AI errors**: Ensure your local LLM (LM Studio) is running and reachable by OpenClaw.

### Contributing

* Create issues and pull requests on the `audiobooker` GitHub repo.

---

## Recent changes (2026-01-30)

* **Default voice changed** to `en-GB-RyanNeural` (a deeper English male voice) and set as the app default.
* **Sanity test completed**: created `pdfs/new.pdf` and generated audio parts into `out_test/` and `out_test_ryan/` to validate end-to-end processing.
* **Environment prepared**: installed Tesseract and FFmpeg, created Python `venv`, and installed core Python packages required by the toolchain.
* **Added tests & CI**: `pytest` smoke test (`tests/test_smoke.py`) and GitHub Actions CI (`.github/workflows/ci.yml`) — CI runs tests but does **not** upload audio artifacts.
* **Repository created** at: <https://github.com/sginsbourg/audiobooker>

If you want, I can add a GitHub Action to run a smoke test on every push, or implement advanced features such as BLIP-based image captions or an Azure/ElevenLabs TTS provider.
