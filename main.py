import speech_recognition as sr
import pyttsx3
from openai import OpenAI
from dotenv import load_dotenv
import os
import datetime
import threading
from queue import Queue
from time import sleep

# Import custom modules
from face_rec import FaceTrainingSystem
from pomodoro import start_pomodoro
from scheduler import GoogleCalendarScheduler
from time_utils import TimerUtils

# Initialize OpenAI
load_dotenv()
API_KEY = os.getenv("OPENAI_KEY")
if not API_KEY:
    raise ValueError("API Key not found. Please set it in your .env file.")

client = OpenAI(api_key=API_KEY)

class RobotAssistant:
    def __init__(self):
        # Initialize Text-to-Speech
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 120)
        self.engine.setProperty("voice", "alex")
        
        # Initialize Speech Recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize subsystems
        self.face_system = FaceTrainingSystem()
        self.calendar = GoogleCalendarScheduler()
        self.timer = TimerUtils()
        
        # Initialize ChatGPT context
        self.messages = [
            {"role": "system", "content": "You are a helpful robot assistant named Tom. Keep responses brief and clear."}
        ]
        
        # Control flags
        self.is_running = True
        self.current_mode = None
        
        # Start face recognition in a separate thread
        self.face_thread = threading.Thread(target=self.run_face_recognition)
        self.face_thread.daemon = True
        self.face_thread.start()

    def speak(self, text):
        """Text-to-speech output"""
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Listen for voice commands"""
        with self.microphone as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5.0)
                text = self.recognizer.recognize_google(audio)
                return text.lower()
            except sr.UnknownValueError:
                return ""
            except sr.RequestError:
                self.speak("Sorry, there was an error with the speech recognition service.")
                return ""

    def get_gpt_response(self, user_input):
        """Get response from ChatGPT"""
        self.messages.append({"role": "user", "content": user_input})
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
                max_tokens=150
            )
            reply = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return "I'm sorry, I encountered an error processing your request."

    def run_face_recognition(self):
        """Run face recognition in background"""
        while self.is_running:
            if self.current_mode == "face_recognition":
                self.face_system.run()
            sleep(0.1)

    def handle_command(self, command):
        """Process voice commands"""
        if "tom" not in command:
            return

        if "schedule" in command or "appointment" in command:
            self.speak("What would you like to schedule?")
            event_details = self.listen()
            try:
                # Simple date parsing - enhance as needed
                title = event_details.split("on")[0].strip()
                date_str = event_details.split("on")[1].strip()
                date_time = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                
                if self.calendar.add_appointment(title, date_time):
                    self.speak("Event scheduled successfully")
                else:
                    self.speak("Sorry, I couldn't schedule the event")
            except Exception as e:
                self.speak("I couldn't understand the date format. Please use YYYY-MM-DD HH:MM format")

        elif "pomodoro" in command:
            self.speak("Starting a Pomodoro session with 25 minutes work and 5 minutes break")
            start_pomodoro(25, 5)

        elif "face recognition" in command:
            self.speak("Starting face recognition system")
            self.current_mode = "face_recognition"

        elif "timer" in command:
            if "countdown" in command:
                try:
                    minutes = int(''.join(filter(str.isdigit, command)))
                    self.speak(f"Starting {minutes} minute countdown")
                    self.timer.countdown(minutes * 60)
                except ValueError:
                    self.speak("Please specify the number of minutes")
            elif "set" in command:
                self.speak("What time should I set the timer for? Use HH:MM:SS format")
                time_str = self.listen()
                self.timer.precise_timer(time_str)

        elif "world time" in command:
            if "london" in command:
                time = self.timer.get_world_time("Europe/London")
                self.speak(f"The time in London is {time}")
            # Add more cities as needed

        else:
            # Default to ChatGPT response
            response = self.get_gpt_response(command)
            self.speak(response)

    def run(self):
        """Main run loop"""
        self.speak("Hello, I'm Tom, your robot assistant. How can I help you?")
        
        while self.is_running:
            command = self.listen()
            if command:
                self.handle_command(command)
                
            if "goodbye" in command or "bye" in command:
                self.speak("Goodbye! Have a great day!")
                self.is_running = False

if __name__ == "__main__":
    assistant = RobotAssistant()
    assistant.run()