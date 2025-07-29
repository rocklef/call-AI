from TTS.api import TTS
import os

tts_models = {
    'en': 'tts_models/en/vctk/vits',
    'hi': 'tts_models/multilingual/multi-dataset/your_tts',
    'ta': 'tts_models/multilingual/multi-dataset/your_tts',
    'your_tts': 'tts_models/multilingual/multi-dataset/your_tts',
    'xtts': 'tts_models/multilingual/xtts_v2',
}

def coqui_tts(text, language='en', out_path='output.wav', model_key=None):
    model_name = tts_models.get(model_key or language, tts_models['en'])
    tts = TTS(model_name)
    tts.tts_to_file(text=text, file_path=out_path, speaker_wav=None, language=language)
    return out_path 