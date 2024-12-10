import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import pyttsx3
import datetime
import wikipedia
import webbrowser
import os
import time
import subprocess
import picamera2
import wolframalpha
import json
import requests  # type: ignore


# Thiet lap giong noi
def speak(text):
    # using gTTS(slow performance, best quality)
    try:
        tts = gTTS(text=text, lang="en")

        filename = "data.wav"
        tts.save(filename)

        print(text)
        playsound(filename)

        os.remove(filename)
    except Exception as e:
        print(f"Error: {e}")
    # using pyttsx3 module (best performance, low quality)
    # try:
    #     engine = pyttsx3.init()
    #     engine.setProperty("rate", 145)
    #     engine.setProperty("voice", "english+f1")
    #     engine.say(text)
    #     engine.runAndWait()
    # except Exception as e:
    #     print(f"Error: {e}")


# Greeting user
def greeting():
    hour = datetime.datetime.now().hour
    if hour >= 0 and hour <= 12:
        speak("Hello, Good morning")
    elif hour >= 12 and hour < 18:
        speak("Hello, Good afternoon")
    else:
        speak("Hello, Good evening")


# Record command from user
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

        try:
            print("Recognizing...")
            statement = r.recognize_google(audio, language="en-us")
            print(f"User said: {statement}\n")
        except Exception:
            speak("Pardon me, please say that again")
            return "None"
        return statement


if __name__ == "__main__":
    speak("Loading your AI personal assistant CoCo")
    greeting()
    while True:
        speak("Tell me how can I help you now?")
        statement = takeCommand().lower()
        if statement == 0:
            continue

        # Turn off robot assistant
        if "good bye" in statement or "ok bye" in statement or "stop" in statement:
            speak("Your personal assistant CoCo is shutting dow. Good bye")
            break

        # Information extraction using Wikipedia
        if "wikipedia" in statement:
            speak("Searching Wikipedia...")
            statement = statement.replace("wikipedia", "")
            results = wikipedia.summary(statement, sentences=3)
            speak("According to Wikipedia")
            speak(results)

        # Open browser, gmail and youtube
        if "open youtube" in statement:
            webbrowser.open_new_tab("https://www.youtube.com")
            speak("YouTube is open now")
            time.sleep(5)
        elif "open gmail" in statement:
            webbrowser.open_new_tab("https://mail.google.com")
            speak("Gmail is open now")
            time.sleep(5)
        elif "open google" in statement:
            webbrowser.open_new_tab("https://google.com")
            speak("Google Search is open now")
            time.sleep(5)
