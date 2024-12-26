from PIL import Image
import os
import time

class FaceUI:
    def __init__(self, lcd_display):
        self.lcd = lcd_display
        self.current_expression = None

    def display_image(self, image_path):
        if os.path.exists(image_path):
            image = Image.open(image_path).convert('RGB')
            self.lcd.image(image)
            self.lcd.display()
        else:
            print(f"Error: Image at '{image_path}' not found.")

    def display_video(self, video_path):
        if not os.path.exists(video_path):
            print(f"Error: Video at '{video_path}' not found.")
            return

        try:
            import cv2
            cap = cv2.VideoCapture(video_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                self.lcd.image(image)
                self.lcd.display()
                time.sleep(1 / 30)  # Adjust frame rate if necessary

            cap.release()
        except ImportError:
            print("Error: OpenCV is required for video playback. Please install it using 'pip install opencv-python'.")

    def change_expression(self, expression, media_path):
        if expression != self.current_expression:
            self.current_expression = expression
            if media_path.endswith('.jpg') or media_path.endswith('.png'):
                self.display_image(media_path)
            elif media_path.endswith('.mp4') or media_path.endswith('.avi'):
                self.display_video(media_path)
            else:
                print("Error: Unsupported media format.")

# Usage example (to be placed in the main script):
# from scheduler import AppointmentScheduler
# from face_ui import FaceUI
# 
# # Example for scheduler
# scheduler = AppointmentScheduler()
# scheduler.add_appointment("Doctor's Appointment", datetime(2024, 12, 28, 15, 0))
# scheduler.start_scheduler()
# 
# # Example for Face UI (assuming `lcd_display` is an initialized object for LCD display)
# face_ui = FaceUI(lcd_display)
# face_ui.change_expression("happy", "path/to/happy_image.jpg")
# face_ui.change_expression("sad", "path/to/sad_video.mp4")
