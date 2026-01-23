from vosk import Model, KaldiRecognizer
import wave
import json
import os

MODEL_PATH = "models/vosk-model-en-us-0.22"

if not os.path.exists(MODEL_PATH):
    raise RuntimeError(f"VOSK model not found at {MODEL_PATH}")

model = Model(MODEL_PATH)

def transcribe_audio(wav_path: str) -> str:
    wf = wave.open(wav_path, "rb")
    
    if wf.getnchannels() != 1:
        raise ValueError("Audio must be mono WAV")
    
    rec = KaldiRecognizer(model, wf.getframerate())
    text = ""
    
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        
        # ✅ FIXED: Capture BOTH partial and final results
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text += result.get("text", "") + " "
        else:
            # Partial results for better real-time feedback
            partial = json.loads(rec.PartialResult())
            print(f"Partial: {partial.get('partial', '')}")
    
    # Final result
    final = json.loads(rec.FinalResult())
    text += final.get("text", "")
    
    wf.close()
    return text.strip()
