from zipfile import Path
import whisper
import os

def transcribe(path):
    path = os.path.join(os.path.dirname(__file__), path)
    model = whisper.load_model("base")
    result = model.transcribe(path)
    return result