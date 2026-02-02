
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import shutil
import os
from pathlib import Path
import uuid
from typing import Optional

# Adjust path to import from parent directory
import sys
sys.path.append(str(Path(__file__).parent.parent))

from audiobooker.generator import AudiobookGenerator

app = FastAPI()

# Mount static files for the frontend
# We will serve index.html from static or directly
app.mount("/static", StaticFiles(directory="ui/static"), name="static")

UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path("ui_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

class TextRequest(BaseModel):
    text: str
    voice: str = "en-GB-RyanNeural"

@app.get("/")
async def read_index():
    return FileResponse("ui/static/index.html")

@app.post("/api/generate/text")
def generate_from_text(request: TextRequest):
    try:
        job_id = str(uuid.uuid4())
        job_out = OUTPUT_DIR / job_id
        
        gen = AudiobookGenerator(
            output_dir=job_out,
            voice=request.voice,
            keep_chunks=False
        )
        
        parts = gen.process(request.text, is_text=True)
        
        if not parts:
            raise HTTPException(status_code=500, detail="No audio generated")
            
        # Return the first part for playback
        # In a real app we might zip them or return a playlist
        final_file = parts[0]
        relative_path = f"/api/download/{job_id}/{Path(final_file).name}"
        
        return {"status": "success", "audio_url": relative_path}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/pdf")
def generate_from_pdf(file: UploadFile = File(...), voice: str = Form("en-GB-RyanNeural")):
    try:
        job_id = str(uuid.uuid4())
        job_out = OUTPUT_DIR / job_id
        
        temp_pdf = UPLOAD_DIR / f"{job_id}_{file.filename}"
        with open(temp_pdf, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        gen = AudiobookGenerator(
            output_dir=job_out,
            voice=voice,
            keep_chunks=False
        )
        
        parts = gen.process(str(temp_pdf), is_text=False)
        
        # Cleanup upload
        os.remove(temp_pdf)
        
        if not parts:
            raise HTTPException(status_code=500, detail="No audio generated")
            
        final_file = parts[0]
        relative_path = f"/api/download/{job_id}/{Path(final_file).name}"
        
        return {"status": "success", "audio_url": relative_path}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download/{job_id}/{filename}")
async def download_file(job_id: str, filename: str):
    file_path = OUTPUT_DIR / job_id / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="audio/mpeg", filename=filename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
