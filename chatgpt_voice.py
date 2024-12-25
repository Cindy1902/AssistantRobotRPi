import os
import openai
import time
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3
import numpy as np
from gtts import gTTS

mytext = "Hello"
language = "en"
openai.api_key = ""
load_dotenv()
model = "gpt-4"

# Khoi tao phuong thuc "nhan dien giong noi" va "chuyen van ban thanh giong noi"
r = sr.Recognizer()
engine = pyttsx3.init("dummy")
voice = engine.getProperty("voices")[1]
engine.setProperty("voice", voice.id)
name = "Cindy"
greetings = [f"whats up {name}",
             "yeah?",
             "well, hello there, how's it going today?"]


def listen_for_wake_word(source):
    print("Listening for 'Hey'...")

    while True:
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            if "hey" in text.lower():
                print("Wake word detected.")
                engine.say(np.random.choice(greetings))
                engine.runAndWait()
                listen_and_respond(source)
                break
        except sr.UnknownValueError:
            pass

# Lang nghe cau lenh va phan hoi bang OpenAI


def listen_and_respond(source):
    print("Listening...")
    while True:
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print(f"You said: {text}")
            if not text:
                continue
            # Gui cau lenh den OpenAI thong qua API
            response = openai.ChatCompletion.create(
                model="gpt-4", messages=[{"role": "user", "content": f"{text}"}])
            response_text = response.choices[0].message.content
            print(response_text)
            print("generating audio")
            myobj = gTTS(text=response_text, lang=language, slow=False)
            myobj.save("response.mp3")
            print("speaking")
            os.system("vlc response.mp3")
            # Speak the response
            print("speaking")
            engine.say(response_text)
            engine.runAndWait()
            if not audio:
                listen_for_wake_word(source)
        except sr.UnknownValueError:
            time.sleep(2)
            print("Silence found, shutting up, listening...")
            listen_for_wake_word(source)
            break
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            engine.say(f"Could not request results; {e}")
            engine.runAndWait()
            listen_for_wake_word(source)
            break


# Su dung microphone mac dinh lam dau vao am thanh
with sr.Microphone() as source:
    listen_for_wake_word(source)
