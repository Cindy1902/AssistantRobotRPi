import os
import openai
import time
from dotenv import load_dotenv
import speech_recognition as sr
import subprocess
import numpy as np
from gtts import gTTS

# Load API Key và cấu hình
load_dotenv()
openai.api_key = "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"
model = "gpt-4"

# Khởi tạo nhận diện giọng nói và chuyển văn bản thành giọng nói
r = sr.Recognizer()

# Cấu hình trợ lý ảo
name = "Cindy"
greetings = [f"What's up {name}", "Yeah?", "Hello there, how's it going today?"]
wake_word = "hey"
language = "en"

# Hàm phát âm thanh
def play_audio(file_path):
    try:
        # Sử dụng omxplayer để phát âm thanh
        subprocess.run(["omxplayer", file_path], check=True)
    except Exception as e:
        print(f"Error playing audio: {e}")

# Hàm lắng nghe từ wake word
def listen_for_wake_word():
    print(f"Listening for wake word '{wake_word}'...")
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)  # Loại bỏ tiếng ồn môi trường
        while True:
            try:
                audio = r.listen(source)
                text = r.recognize_google(audio).lower()
                if wake_word in text:
                    print("Wake word detected.")
                    play_greeting()
                    listen_and_respond()
            except sr.UnknownValueError:
                pass  # Không phát hiện từ khóa, tiếp tục lắng nghe
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)

# Phát lời chào ngẫu nhiên
def play_greeting():
    greeting = np.random.choice(greetings)
    print(f"Assistant: {greeting}")
    tts = gTTS(text=greeting, lang=language)
    tts.save("greeting.mp3")
    play_audio("greeting.mp3")

# Lắng nghe và phản hồi
def listen_and_respond():
    print("Listening for command...")
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=10)  # Giới hạn thời gian lắng nghe
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            if text:
                # Gửi yêu cầu tới OpenAI
                response = openai.ChatCompletion.create(
                    model=model, messages=[{"role": "user", "content": text}]
                )
                response_text = response.choices[0].message.content.strip()
                print(f"Assistant: {response_text}")

                # Phát âm thanh bằng gTTS
                tts = gTTS(text=response_text, lang=language)
                tts.save("response.mp3")
                play_audio("response.mp3")
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    try:
        listen_for_wake_word()
    except KeyboardInterrupt:
        print("\nExiting programs.")