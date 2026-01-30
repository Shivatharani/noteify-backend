from pydub import AudioSegment
import os


def convert_to_wav(input_path: str) -> str:
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    output_path = input_path.rsplit(".", 1)[0] + ".wav"
    audio.export(output_path, format="wav")
    return output_path