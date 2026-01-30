from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
import traceback

from services.audio_utils import convert_to_wav
from services.video_utils import extract_audio_from_video
from services.speech_to_text import transcribe_audio
from services.summarizer import summarize_text
from services.pdf_generator import create_pdf

# ─────────────────────────────────────────────
# App Initialization
# ─────────────────────────────────────────────
app = FastAPI(
    title="Noteify AI – Professional Lecture Notes Generator",
    version="1.0"
)

# CORS (safe to keep; no issues on Render)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(UPLOAD_DIR, exist_ok=True)

AUDIO_FORMATS = {".mp3", ".wav", ".m4a", ".aac"}
VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

# ─────────────────────────────────────────────
# Serve Frontend (React build)
# ─────────────────────────────────────────────
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    # React Router support (important!)
    @app.get("/{path:path}")
    def serve_react_routes(path: str):
        file_path = os.path.join(STATIC_DIR, path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

else:
    # Fallback if frontend is not built
    @app.get("/")
    def root():
        return {
            "status": "running",
            "service": "Noteify AI Backend",
            "message": "Frontend not built yet"
        }

# ─────────────────────────────────────────────
# Main Processing Endpoint - FULL TRANSCRIPTION
# ─────────────────────────────────────────────
@app.post("/api/process")
async def process_lecture(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    filename = file.filename.lower()
    file_ext = os.path.splitext(filename)[1]
    input_path = os.path.join(UPLOAD_DIR, filename)

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    audio_path = None
    wav_path = None

    try:
        print(f"📁 Received file: {filename}")

        if file_ext in VIDEO_FORMATS:
            print("🎥 Extracting audio from video...")
            audio_path = extract_audio_from_video(input_path)
        elif file_ext in AUDIO_FORMATS:
            print("🎵 Processing audio file...")
            audio_path = input_path
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format: {file_ext}"
            )

        print("🔄 Converting to WAV...")
        wav_path = convert_to_wav(audio_path)

        print("🎙️ Transcribing audio...")
        transcription_text = transcribe_audio(wav_path)

        if not transcription_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No speech detected in the audio"
            )

        print("📚 Generating structured summary...")
        notes_data = summarize_text(transcription_text)

        pdf_filename = os.path.splitext(filename)[0] + ".pdf"
        pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)

        print("📄 Creating professional PDF...")
        create_pdf(notes_data, pdf_path, filename)

        full_transcription = " ".join(notes_data["full_transcription"])
        summary = notes_data["summary"]["paragraph"].strip()

        summary = summary.rstrip('.').rstrip('…').rstrip('...').strip()
        if not summary.endswith(('.', '!', '?')):
            summary += '.'

        return {
            "success": True,
            "filename": filename,
            "output": {
                "full_transcription": full_transcription,
                "summary_paragraph": summary
            },
            "pdf_url": f"/api/download/{pdf_filename}"
        }

    except HTTPException:
        raise
    except Exception as e:
        print("❌ Error occurred")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )
    finally:
        for path in [input_path, audio_path, wav_path]:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

# ─────────────────────────────────────────────
# PDF Download Endpoint
# ─────────────────────────────────────────────
@app.get("/api/download/{filename}")
def download_pdf(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename
    )
