from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware  # ← CORS ADDED
from fastapi import HTTPException
import shutil
import os
import traceback
from services.audio_utils import convert_to_wav
from services.video_utils import extract_audio_from_video
from services.transcriber import transcribe_audio
from services.summarizer import summarize_text
from services.pdf_generator import create_pdf

app = FastAPI(title="Noteify AI - Perfect Lecture Notes")

# ✅ CORS - Allows frontend:3000 to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

AUDIO_FORMATS = {'.mp3', '.wav', '.m4a', '.aac'}
VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}

@app.get("/")
async def root():
    return {
        "message": "✅ Noteify AI - Perfect Lecture Notes Generator",
        "features": [
            "📄 Full Transcription (100% content preserved)",
            "📝 Smart Summary (key points only)", 
            "📄 Professional PDF (perfect alignment)"
        ],
        "supported_formats": sorted(list(AUDIO_FORMATS | VIDEO_FORMATS))
    }

@app.post("/process")
async def process_lecture(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No file provided")
    
    filename = file.filename.lower()
    file_ext = os.path.splitext(filename)[1]
    
    input_path = f"{UPLOAD_DIR}/{filename}"
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    audio_path = None
    wav_path = None
    pdf_path = None
    
    try:
        print(f"📁 Processing: {filename}")
        
        if file_ext in VIDEO_FORMATS:
            print("🎥 Extracting audio...")
            audio_path = extract_audio_from_video(input_path)
        elif file_ext in AUDIO_FORMATS:
            print("🎵 Using audio file...")
            audio_path = input_path
        else:
            raise HTTPException(400, f"Unsupported format: {file_ext}")
        
        print("🔄 Converting to WAV...")
        wav_path = convert_to_wav(audio_path)
        
        print("🎙️ Transcribing...")
        transcription = transcribe_audio(wav_path)
        print(f"📝 Full transcription: {len(transcription)} chars")
        
        if not transcription.strip():
            raise HTTPException(400, "❌ No speech detected")
        
        print("📚 Creating smart summary...")
        notes_data = summarize_text(transcription)
        
        print("📄 Generating perfect PDF...")
        pdf_filename = f"notes_{os.path.splitext(filename)[0]}.pdf"
        pdf_path = f"{UPLOAD_DIR}/{pdf_filename}"
        create_pdf(notes_data, pdf_path)
        
        # ✅ PERFECT JSON RESPONSE for Frontend
        response = {
            "success": True,
            "filename": filename,
            "type": "video" if file_ext in VIDEO_FORMATS else "audio",
            "content": {
                "full_transcription": notes_data["full_transcription"],
                "summary": notes_data["summary"]
            },
            "pdf_url": f"/download/{pdf_filename}"
        }
        print(f"✅ Response sent: {response['content']['full_transcription'][:100]}...")
        return response
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(500, f"Processing failed: {str(e)}")
    
    finally:
        # Clean up temp files (KEEP PDF)
        cleanup_files = [input_path, audio_path, wav_path]
        for path in cleanup_files:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    print(f"🗑️ Cleaned: {os.path.basename(path)}")
                except:
                    pass

@app.get("/download/{filename}")
async def download_pdf(filename: str):
    file_path = f"{UPLOAD_DIR}/{filename}"
    if os.path.exists(file_path):
        print(f"📥 Serving PDF: {filename}")
        return FileResponse(
            file_path, 
            filename="perfect-lecture-notes.pdf",
            media_type="application/pdf"
        )
    print(f"❌ PDF not found: {file_path}")
    raise HTTPException(404, "PDF not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
