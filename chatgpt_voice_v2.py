import speech_recognition as sr
import pyttsx3
import openai

#Initializing pyttsx3
listening = True
engine = pyttsx3.init("dummy")

#Set your openai api key and customizing the chatgpt role
openai.api_key = "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"
messages = [{"role": "system", "content": "Your name is Coco and give answers in 2 lines"}]

#Customizing The output voice
voices = engine.getProperty("voices")
rate = engine.getProperty("rate")
volume = engine.getProperty("volume")


def get_response(user_input):
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model = "gpt-4",
        messages = messages
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply


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

            if "coco" in response.lower():

                response_from_openai = get_response(response)
                engine.setProperty("rate", 120)
                engine.setProperty("volume", volume)
                engine.setProperty("voice", "alex")
                engine.say(response_from_openai)
                engine.runAndWait()
            else:
                print("Didn't recognize 'Coco'.")
        except sr.UnknownValueError:
            print("Didn't recognize anything.")