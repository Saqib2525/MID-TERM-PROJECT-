import os
from flask import Flask, request, render_template, jsonify, send_file
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS

app = Flask(__name__)

# Define a list of supported languages and their labels
supported_languages = [
    {"code": "en", "label": "English"},
    {"code": "es", "label": "Spanish"},
    {"code": "fr", "label": "French"},
    {"code": "de", "label": "German"},
]

# Define a dictionary to map language codes to their respective labels
language_labels = {lang["code"]: lang["label"] for lang in supported_languages}

def convert_audio_to_text(audio_path):
    r = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_text = r.listen(source)
        try:
            text = r.recognize_google(audio_text, language='en')  # Recognize in English
            return text
        except sr.UnknownValueError:
            return "Could not understand the audio."
        except sr.RequestError:
            return "Could not request results; check your network connection."

def translate_text(text, target_language):
    try:
        translated_text = GoogleTranslator(source='auto', target=target_language).translate(text)
        return translated_text
    except Exception as e:
        return str(e)

def generate_and_save_audio(translated_text, target_language):
    try:
        tts = gTTS(translated_text, lang=target_language)
        tts.save("output.mp3")
    except Exception as e:
        return str(e)
        
# ...
# ...

@app.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    text = request.form.get('text-input')
    target_language = request.form.get('target-language', 'en')  # Get selected language or default to English
    
    # Generate and save the converted text as "output.mp3"
    try:
        tts = gTTS(text=text, lang=target_language, slow=False)
        tts.save("output.mp3")
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

    return jsonify({'success': True})

# ...


# ...

    
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if audio_file:
            audio_path = "uploaded_audio.wav"
            audio_file.save(audio_path)

            text = convert_audio_to_text(audio_path)
            os.remove(audio_path)  # Remove the temporary audio file

            target_language = request.form.get('target-language', 'en')

            # Check if the selected target language is supported
            if target_language not in [lang["code"] for lang in supported_languages]:
                return jsonify({'error': 'Selected language is not supported'}), 400

            # Translate the recognized text to the selected target language
            translated_text = translate_text(text, target_language)

            # Generate and save the translated text as "output.mp3"
            generate_and_save_audio(translated_text, target_language)

            return render_template('index.html', text=text, translated_text=translated_text, supported_languages=supported_languages, selected_language=target_language, language_labels=language_labels)

    return render_template('index.html', text=None, supported_languages=supported_languages, selected_language='en', language_labels=language_labels, audio_url=None)

@app.route('/play_audio')
def play_audio():
    return send_file('output.mp3')

if __name__ == '__main__':
    app.run(debug=True)
