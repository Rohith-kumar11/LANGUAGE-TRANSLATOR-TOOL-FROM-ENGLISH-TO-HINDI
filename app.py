# translator-model/app.py

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from nmt_model import NMTTranslator
import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
import os

app = Flask(__name__)
CORS(app)

translator = NMTTranslator()

# ------------------- TEXT TRANSLATION -------------------
@app.route("/translate", methods=["POST"])
def translate_text():
    data = request.get_json()
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    translated = translator.translate(text)
    return jsonify({"translated_text": translated})


# ------------------- AUDIO TRANSLATION -------------------
@app.route("/audio-translate", methods=["POST"])
def audio_translate():
    if "audio" not in request.files:
        return "No audio file provided", 400

    webm_audio = request.files["audio"]
    webm_path = "temp_audio.webm"
    wav_path = "temp_audio.wav"
    webm_audio.save(webm_path)

    # Convert webm to wav
    try:
        audio = AudioSegment.from_file(webm_path, format="webm")
        audio.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)
        print(f"Recognized: {text}")

        translated_text = translator.translate(text)
        print(f"Translated: {translated_text}")

        tts = gTTS(translated_text, lang="hi")
        output_audio = "translated.mp3"
        tts.save(output_audio)

        return send_file(output_audio, mimetype="audio/mpeg")

    except Exception as e:
        print(f"Error: {e}")
        return f"Error processing audio: {str(e)}", 500
    finally:
        for path in [webm_path, wav_path]:
            if os.path.exists(path):
                os.remove(path)

if __name__ == "__main__":
    app.run(debug=True)
