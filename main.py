from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

AUDIO_FORMATS = {".mp3", ".wav", ".m4a", ".aac"}
VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

# ─────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "status": "running",
        "service": "Noteify AI Backend",
        "message": "Upload audio/video to generate professional lecture notes"
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

    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    audio_path = None
    wav_path = None

    try:
        print(f"📁 Received file: {filename}")

        # Step 1: Handle input type
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

        # Step 2: Convert to WAV
        print("🔄 Converting to WAV...")
        wav_path = convert_to_wav(audio_path)

        # Step 3: Transcription
        print("🎙️ Transcribing audio...")
        transcription_text = transcribe_audio(wav_path)

        if not transcription_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No speech detected in the audio"
            )

        print("📚 Generating structured summary...")
        notes_data = summarize_text(transcription_text)

        # Step 4: Generate PDF
        pdf_filename = os.path.splitext(filename)[0] + ".pdf"
        pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)

        print("📄 Creating professional PDF...")
        create_pdf(notes_data, pdf_path, filename)

        # ✅ FULL TRANSCRIPTION + CLEAN SUMMARY
        full_transcription = " ".join(notes_data["full_transcription"])
        summary = notes_data["summary"]["paragraph"].strip()
        
        # Clean up summary (remove extra dots, ensure proper ending)
        summary = summary.rstrip('.').rstrip('…').rstrip('...').strip()
        if not summary.endswith(('.', '!', '?')):
            summary += '.'

        response = {
            "success": True,
            "filename": filename,
            "output": {
                # FULL CONTENT - No truncation!
                "full_transcription": full_transcription,
                "summary_paragraph": summary
            },
            "pdf_url": f"/api/download/{pdf_filename}"
        }

        print("✅ Processing completed successfully")
        print(f"📝 Full transcription length: {len(full_transcription)} chars")
        return response

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
        # Cleanup temp files (keep PDF)
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
