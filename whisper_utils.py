import whisper
import torch
from transformers import pipeline

# Load the base model once
model = whisper.load_model('base')

def whisper_transcribe(audio_path, language=None):
    # language: 'en', 'hi', 'ta', or None for auto
    result = model.transcribe(audio_path, language=language)
    return result['text'].strip()

def wav2vec2_transcribe(audio_path, model_name='facebook/wav2vec2-base-960h'):
    asr = pipeline('automatic-speech-recognition', model=model_name)
    result = asr(audio_path)
    return result['text'].strip() 