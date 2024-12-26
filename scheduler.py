import schedule
import time
from datetime import datetime, timedelta
import threading

class AppointmentScheduler:
    def __init__(self):
        self.appointments = []
        self.notification_callbacks = []

    def add_appointment(self, title, date_time):
        appointment = {"title": title, "date_time": date_time}
        self.appointments.append(appointment)
        self.schedule_notifications(appointment)

    def schedule_notifications(self, appointment):
        one_day_before = appointment["date_time"] - timedelta(days=1)
        one_hour_before = appointment["date_time"] - timedelta(hours=1)

        schedule.every().day.at(one_day_before.strftime("%H:%M")).do(self.notify, appointment, "1 day")
        schedule.every().day.at(one_hour_before.strftime("%H:%M")).do(self.notify, appointment, "1 hour")

    def notify(self, appointment, when):
        message = f"Reminder: '{appointment['title']}' is scheduled in {when}."
        print(message)
        for callback in self.notification_callbacks:
            callback(message)

    def add_notification_callback(self, callback):
        self.notification_callbacks.append(callback)

    def start_scheduler(self):
        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(1)

        thread = threading.Thread(target=run_schedule, daemon=True)
        thread.start()
