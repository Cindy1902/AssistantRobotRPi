import os
from dotenv import load_dotenv
from openai import OpenAI

KEY = os.getenv("OPENAI_KEY")
client = OpenAI(api_key=KEY)
import time
import speech_recognition as sr
import pyttsx3
from vosk import Model, KaldiRecognizer
import subprocess
import numpy as np
from gtts import gTTS

# Load API Key và cấu hình
model = "gpt-4"

# Đường dẫn đến mô hình Vosk
vosk_model_path = "/home/levi/Downloads/vosk-model-small-en-us-0.15"
if not os.path.exists(vosk_model_path):
    raise FileNotFoundError(f"Vosk model not found at {vosk_model_path}")

# Khởi tạo mô hình Vosk
vosk_model = Model(vosk_model_path)
recognizer = KaldiRecognizer(vosk_model, 16000)

# Khởi tạo TTS (Text-to-Speech)
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 180) # Tốc độ nói

# Cấu hình trợ lý ảo
name = "Cindy"
greetings = [f"What's up {name}", "Yeah?", "Hello there, how's it going today?"]
wake_word = "hey"
language = "en"

# Hàm phát âm thanh
def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

# Hàm lắng nghe âm thanh qua Vosk
def recognize_from_microphone():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    print("Listening...")
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                print(f"Recognized: {text}")
                return text

# Hàm lắng nghe từ wake word
def listen_for_wake_word():
    while True:
        recognized_text = recognize_from_microphone()
        if wake_word in recognized_text.lower():
            print("Wake word detected!")
            play_greeting()
            listen_and_respond()

# Phát lời chào
def play_greeting():
    greeting = np.random.choice(greetings)
    print(f"Assistant: {greeting}")
    speak(greeting)

# Lắng nghe và phản hồi
def listen_and_respond():
    print("Listening for command...")
    command = recognize_from_microphone()
    if command:
        print(f"You said: {command}")
        # Gửi yêu cầu tới OpenAI
        try:
            response = client.chat.completions.create(model=model, messages=[{"role": "user", "content": command}], max_tokens=150)
            response_text = response.choices[0].message.content.strip()
            print(f"Assistant: {response_text}")
            speak(response_text)
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            speak("Sorry, I couldn't process your request.")

# Chương trình chính
if __name__ == "__main__":
    try:
        listen_for_wake_word()
    except KeyboardInterrupt:
        print("\nExiting program.")