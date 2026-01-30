import subprocess
import os
import sys


def extract_audio_from_video(video_path: str) -> str:
    """Extract audio from video using system FFmpeg - NO PYTHON PACKAGE NEEDED"""
    audio_path = video_path.rsplit(".", 1)[0] + ".mp3"
    
    # ✅ Use system FFmpeg directly (most reliable)
    cmd = [
        'ffmpeg', 
        '-i', video_path,
        '-vn',           # No video
        '-acodec', 'mp3',
        '-ac', '1',      # Mono
        '-ar', '16000',  # 16kHz for Vosk
        '-y',            # Overwrite
        audio_path
    ]
    
    try:
        print(f"🎥 Running FFmpeg: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")
        
        if not os.path.exists(audio_path):
            raise RuntimeError("FFmpeg created no output file")
        
        print(f"✅ Audio extracted: {audio_path}")
        return audio_path
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg timeout - video too long")
    except FileNotFoundError:
        raise RuntimeError("❌ FFmpeg not found! Install from https://ffmpeg.org/download.html")
    except Exception as e:
        raise RuntimeError(f"Video extraction failed: {e}")