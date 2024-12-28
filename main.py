import speech_recognition as sr
import pyttsx3
from openai import OpenAI
from dotenv import load_dotenv
import os
from time import sleep
from datetime import datetime

# Import các module tùy chỉnh
from time_utils import TimerUtils
from face_rec import FaceTrainingSystem
from scheduler import GoogleCalendarScheduler

class VoiceControlBot:
    def __init__(self):
        # Khởi tạo speech recognition
        self.recognizer = sr.Recognizer()
        
        # Khởi tạo text-to-speech
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 120)
        self.engine.setProperty("voice", "alex")
        
        # Khởi tạo các module
        self.timer = TimerUtils()
        self.face_system = FaceTrainingSystem()
        self.scheduler = AppointmentScheduler()
        
        # Khởi tạo OpenAI (cho chatbot)
        load_dotenv()
        self.api_key = os.getenv("OPENAI_KEY")
        if self.api_key:
            self.openai_client = OpenAI(api_key=self.api_key)
            self.messages = [{"role": "system", "content": "Your name is Tom and you can talk to me like a friend"}]
        
        # Định nghĩa các từ khóa và chức năng tương ứng
        self.commands = {
            "timer": self.handle_timer,
            "countdown": self.handle_countdown,
            "time": self.handle_world_time,
            "face": self.handle_face_recognition,
            "schedule": self.handle_scheduler,
            "chat": self.handle_chat
        }

    def speak(self, text):
        """Chuyển văn bản thành giọng nói"""
        print(f"Bot: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        """Lắng nghe và nhận dạng giọng nói"""
        with sr.Microphone() as source:
            print("Đang lắng nghe...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5.0)
                text = self.recognizer.recognize_google(audio, language='vi-VN')
                print(f"Bạn: {text}")
                return text.lower()
            except sr.UnknownValueError:
                print("Không nhận dạng được giọng nói")
                return None
            except sr.RequestError:
                print("Lỗi kết nối")
                return None

    def handle_timer(self, command):
        """Xử lý lệnh hẹn giờ"""
        self.speak("Bạn muốn đặt hẹn giờ cho mấy giờ? (Format: HH:MM:SS)")
        time_str = self.listen()
        if time_str:
            self.timer.precise_timer(time_str)
            self.speak(f"Đã đặt hẹn giờ cho {time_str}")

    def handle_countdown(self, command):
        """Xử lý lệnh đếm ngược"""
        self.speak("Bạn muốn đếm ngược bao nhiêu giây?")
        try:
            seconds = int(self.listen())
            self.timer.countdown(seconds)
            self.speak("Bắt đầu đếm ngược")
        except:
            self.speak("Không hiểu được thời gian đếm ngược")

    def handle_world_time(self, command):
        """Xử lý lệnh xem giờ quốc tế"""
        self.speak("Bạn muốn xem giờ của khu vực nào?")
        timezone = self.listen()
        if timezone:
            time = self.timer.get_world_time(timezone)
            self.speak(f"Thời gian ở {timezone} là {time}")

    def handle_face_recognition(self, command):
        """Xử lý nhận diện khuôn mặt"""
        self.speak("Khởi động hệ thống nhận diện khuôn mặt")
        self.face_system.run()

    def handle_scheduler(self, command):
        """Xử lý lịch hẹn"""
        self.speak("Bạn muốn thêm lịch hẹn mới không?")
        if "có" in self.listen():
            self.speak("Tên lịch hẹn là gì?")
            title = self.listen()
            self.speak("Thời gian hẹn là khi nào? (Format: DD/MM/YYYY HH:MM)")
            date_str = self.listen()
            try:
                date_time = datetime.strptime(date_str, "%d/%m/%Y %H:%M")
                self.scheduler.add_appointment(title, date_time)
                self.speak("Đã thêm lịch hẹn thành công")
            except:
                self.speak("Không hiểu được định dạng thời gian")

    def handle_chat(self, command):
        """Xử lý trò chuyện với ChatGPT"""
        if not self.api_key:
            self.speak("Chưa cấu hình API key cho ChatGPT")
            return
            
        response = self.get_chat_response(command)
        self.speak(response)

    def get_chat_response(self, user_input):
        """Lấy phản hồi từ ChatGPT"""
        self.messages.append({"role": "user", "content": user_input})
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=self.messages,
                max_tokens=150
            )
            reply = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            print(f"Lỗi API OpenAI: {e}")
            return "Xin lỗi, tôi không thể xử lý yêu cầu lúc này"

    def run(self):
        """Chạy bot"""
        self.speak("Xin chào! Tôi là trợ lý ảo của bạn")
        
        while True:
            command = self.listen()
            if command:
                # Kiểm tra từ khóa trong câu lệnh
                for keyword, handler in self.commands.items():
                    if keyword in command:
                        handler(command)
                        break
                else:
                    self.speak("Tôi không hiểu lệnh này")

if __name__ == "__main__":
    bot = VoiceControlBot()
    bot.run()