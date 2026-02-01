
import os
import shutil
from pathlib import Path
from pydub import AudioSegment
from audiobooker.chunker import chunk_text
from audiobooker.pdf_processor import extract_pages, PageContent
from audiobooker.tts_providers import EdgeTTSProvider
from audiobooker.text_cleaner import clean_markdown

class AudiobookGenerator:
    def __init__(self, output_dir="out", voice="en-GB-RyanNeural", chunk_size=4000, split_seconds=3600, keep_chunks=False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir = self.output_dir / "images"
        self.voice = voice
        self.chunk_size = chunk_size
        self.split_seconds = split_seconds
        self.keep_chunks = keep_chunks
        self.tts = EdgeTTSProvider(voice=self.voice)

    def assemble_audio(self, parts, out_file):
        combined = None
        for p in parts:
            seg = AudioSegment.from_file(p)
            combined = seg if combined is None else (combined + seg)
        if combined is None:
            raise ValueError("No audio parts to assemble")
        combined.export(out_file, format=Path(out_file).suffix.replace(".", ""))
        return out_file

    def process(self, input_source, is_text=False):
        # input_source is either a text string (if is_text=True) or a pdf path (str)
        
        if is_text:
             pages_iter = [
                PageContent(page_no=1, text=input_source, tables=[], image_paths=[])
            ]
        else:
            pages_iter = extract_pages(input_source, str(self.images_dir))

        chunk_files = []
        page_cnt = 0
        
        for page in pages_iter:
            page_cnt += 1
            text = page.text
            for t in page.tables:
                text += "\n\n" + t
            
            cleaned_text = clean_markdown(text)
            chunks = chunk_text(cleaned_text, max_chars=self.chunk_size)
            
            for i, c in enumerate(chunks):
                fname = self.output_dir / f"p{page_cnt:04d}_c{i:03d}.mp3"
                # If we were in an async context we would await this, but the underlying mock/edge-tts might be sync or handled via run_until_complete inside the provider
                # The current EdgeTTSProvider.synthesize code uses subprocess or sync calls? 
                # Let's check tts_providers.py content first to be sure. 
                # Since we are making a class, we assume synthesize is blocking for now as per original script.
                self.tts.synthesize(c, str(fname), voice=self.voice)
                chunk_files.append(str(fname))
        
        # Assembly
        parts = []
        running_secs = 0
        group = []
        for f in chunk_files:
            dur = AudioSegment.from_file(f).duration_seconds
            if running_secs + dur > self.split_seconds and group:
                idx = len(parts) + 1
                outpath = self.output_dir / f"audiobook_part_{idx:03d}.mp3"
                self.assemble_audio(group, outpath)
                parts.append(str(outpath))
                group = []
                running_secs = 0
            group.append(f)
            running_secs += dur
        
        if group:
            idx = len(parts) + 1
            outpath = self.output_dir / f"audiobook_part_{idx:03d}.mp3"
            self.assemble_audio(group, outpath)
            parts.append(str(outpath))

        # Cleanup
        if not self.keep_chunks:
            for f in chunk_files:
                try:
                    Path(f).unlink()
                except OSError:
                    pass
        
        return parts

