import os
import openai
import json
import pyaudio
import time
from vosk import Model, KaldiRecognizer
from gtts import gTTS
import subprocess
import numpy as np

# Cấu hình API Key
openai.api_key = "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"
model = "gpt-4"

# Đường dẫn đến mô hình Vosk
vosk_model_path = "/home/levi/Downloads/vosk-model-small-en-us-0.15"
if not os.path.exists(vosk_model_path):
    raise FileNotFoundError(f"Vosk model not found at {vosk_model_path}")

# Khởi tạo mô hình Vosk
vosk_model = Model(vosk_model_path)
recognizer = KaldiRecognizer(vosk_model, 16000)

# Cấu hình trợ lý
name = "Cindy"
greetings = [f"What's up {name}", "Yeah?", "Hello there, how's it going today?"]
wake_word = "hey"

# Hàm phát âm thanh
def play_audio(file_path):
    """Phát âm thanh từ file."""
    try:
        subprocess.run(["cvlc", "--play-and-exit", file_path], check=True)
    except Exception as e:
        print(f"Error playing audio: {e}")

def speak(text):
    """Chuyển văn bản thành giọng nói và phát âm."""
    tts = gTTS(text=text, lang="en")
    file_path = "response.mp3"
    tts.save(file_path)
    play_audio(file_path)

# Hàm nhận diện giọng nói từ microphone
def recognize_from_microphone():
    """Lắng nghe và nhận diện giọng nói."""
    p = pyaudio.PyAudio()
    stream = None
    try:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=8192)
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
    except Exception as e:
        print(f"Audio input error: {e}")
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
        p.terminate()


# Hàm phát hiện từ wake word
def listen_for_wake_word():
    """Lắng nghe từ wake word."""
    while True:
        recognized_text = recognize_from_microphone()
        if recognized_text and wake_word in recognized_text.lower():
            print("Wake word detected!")
            play_greeting()
            listen_and_respond()

# Phát lời chào
def play_greeting():
    """Phát lời chào."""
    greeting = np.random.choice(greetings)
    print(f"Assistant: {greeting}")
    speak(greeting)

# Lắng nghe và phản hồi
def listen_and_respond():
    """Xử lý yêu cầu từ người dùng và phản hồi."""
    print("Listening for command...")
    command = recognize_from_microphone()
    if command:
        print(f"You said: {command}")
        try:
            # Gửi yêu cầu tới OpenAI
            response = openai.ChatCompletion.create(
                model=model, messages=[{"role": "user", "content": command}], max_tokens=150
            )
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
