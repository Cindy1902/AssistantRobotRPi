import speech_recognition as sr
import pyttsx3
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("OPENAI_KEY")

if not API_KEY:
    raise ValueError("API Key not found. Please set it in your .env file.")

client = OpenAI(api_key=API_KEY)

#Initializing pyttsx3
listening = True
engine = pyttsx3.init("dummy")

#Set your openai api key and customizing the chatgpt role
messages = [{"role": "system", "content": "Your name is Tom and you can talk to me like a friend, help me find answers when I need and give answer in 2 lines"}]

#Customizing The output voice
voices = engine.getProperty("voices")
rate = engine.getProperty("rate")
volume = engine.getProperty("volume")
engine.setProperty("rate", 120)
engine.setProperty("volume", volume)
engine.setProperty("voice", "alex")


def get_response(user_input):
    messages.append({"role": "user", "content": user_input})
    try:
        response = client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = messages,
            max_tokens = 150
        )
        ChatGPT_reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": ChatGPT_reply})
        return ChatGPT_reply
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "I'm sorry, I can't process your request right now."


while listening:
    with sr.Microphone() as source:
        recognizer = sr.Recognizer()
        recognizer.adjust_for_ambient_noise(source)
        recognizer.dynamic_energy_threshold = 3000

        try:
            print("Listening...")
            audio = recognizer.listen(source, timeout=5.0)
            response = recognizer.recognize_google(audio)
            print(response)

            if "tom" in response.lower():
                response_from_openai = get_response(response)
                engine.say(response_from_openai)
                engine.runAndWait()
            else:
                print("Didn't recognize 'Tom'.")
        except sr.UnknownValueError:
            print("Didn't recognize anything.")
        except Exception as e:
            print(f"Unexpected error: {e}")