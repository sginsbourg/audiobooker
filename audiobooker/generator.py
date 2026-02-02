import os
import shutil
from pathlib import Path
from pydub import AudioSegment
from audiobooker.chunker import chunk_text
from audiobooker.pdf_processor import extract_pages, PageContent
from audiobooker.tts_providers import EdgeTTSProvider
from audiobooker.text_cleaner import clean_markdown
from audiobooker.openclaw_processor import OpenClawProcessor

class AudiobookGenerator:
    def __init__(self, output_dir="out", voice="en-GB-RyanNeural", chunk_size=4000, split_seconds=3600, keep_chunks=False, use_openclaw=False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir = self.output_dir / "images"
        self.voice = voice
        self.chunk_size = chunk_size
        self.split_seconds = split_seconds
        self.keep_chunks = keep_chunks
        self.tts = EdgeTTSProvider(voice=self.voice)
        self.use_openclaw = use_openclaw
        self.openclaw = OpenClawProcessor() if use_openclaw else None

    def assemble_audio(self, parts, out_file):
        combined = None
        for p in parts:
            if not os.path.exists(p):
                print(f"Warning: Audio part {p} not found, skipping.")
                continue
            seg = AudioSegment.from_file(p)
            combined = seg if combined is None else (combined + seg)
        if combined is None:
            raise ValueError("No audio parts to assemble")
        combined.export(out_file, format=Path(out_file).suffix.replace(".", ""))
        return out_file

    def process(self, input_source, is_text=False):
        # input_source is either a text string (if is_text=True) or a pdf path (str)
        
        full_text = ""
        if is_text:
            full_text = input_source
        else:
            pages_iter = extract_pages(input_source, str(self.images_dir))
            for page in pages_iter:
                full_text += page.text + "\n"
                for t in page.tables:
                    full_text += "\n\n" + t + "\n"

        # 1. Clean Text
        if self.use_openclaw:
            print("Cleaning text with OpenClaw...")
            cleaned_text = self.openclaw.clean_text(full_text)
        else:
            cleaned_text = clean_markdown(full_text)

        # 2. Split into Chapters
        if self.use_openclaw:
            print("Splitting into chapters with OpenClaw...")
            chapters = self.openclaw.split_into_chapters(cleaned_text)
        else:
            # Basic fallback: treat whole text as one chapter
            chapters = [{"title": "Main Content", "content": cleaned_text}]

        # 3. Plan Audio Files
        if self.use_openclaw:
            print("Planning audio files with OpenClaw...")
            audio_plan = self.openclaw.plan_audio_files(chapters, target_duration_sec=self.split_seconds)
        else:
            # Fallback simple grouping
            audio_plan = [[ch] for ch in chapters]

        # 4. Generate Audio for each chapter and assemble按照 plan
        final_parts = []
        for i, group in enumerate(audio_plan):
            group_files = []
            for j, chapter in enumerate(group):
                print(f"Generating audio for Chapter: {chapter['title']}")
                # Chunk chapter if it's too long for TTS
                ch_chunks = chunk_text(chapter['content'], max_chars=self.chunk_size)
                ch_files = []
                for k, c in enumerate(ch_chunks):
                    fname = self.output_dir / f"group{i:03d}_ch{j:03d}_c{k:03d}.mp3"
                    self.tts.synthesize(c, str(fname), voice=self.voice)
                    ch_files.append(str(fname))
                
                # Merge chunks into a single chapter file (optional but cleaner for assembly)
                chapter_file = self.output_dir / f"group{i:03d}_ch{j:02d}_full.mp3"
                self.assemble_audio(ch_files, str(chapter_file))
                group_files.append(str(chapter_file))
                
                # Cleanup chapter chunks
                if not self.keep_chunks:
                    for f in ch_files:
                        try: Path(f).unlink()
                        except: pass
            
            # Merge all chapters in the group into one final audio part
            idx = len(final_parts) + 1
            outpath = self.output_dir / f"audiobook_part_{idx:03d}.mp3"
            self.assemble_audio(group_files, outpath)
            final_parts.append(str(outpath))
            
            # Cleanup chapter files
            if not self.keep_chunks:
                for f in group_files:
                    try: Path(f).unlink()
                    except: pass
        
        return final_parts

