import time
from datetime import datetime, timedelta
import pytz
from plyer import notification


class TimerUtils:
    """
    Module tien ich cho cac chuc nang timer
    """
    @staticmethod
    def precise_timer(target_time: str, callback=None):
        """
        Doi den khoang thoi gian cu the va co tuy chon dung ham callback().
        :params target_time (str) - Thoi gian chi dinh theo format HH:MM:SS.
        :params callback (callable, optional) - Ham tuy chon duoc goi den sau khi hoan thanh.
        """
        now = datetime.now()
        try:
            target_hour, target_min, target_sec = map(
                int, target_time.split(":"))
            target_datetime = now.replace(
                hour=target_hour, minute=target_min, second=target_sec, microsecond=0)
            if target_datetime < now:
                # Set for the next day if the time has passed
                target_datetime += timedelta(days=1)
            wait_seconds = (target_datetime - now).total_seconds()
            time.sleep(wait_seconds)
            if callback:
                callback()
            TimerUtils._send_notification(
                "Precise Timer", "Target time reached!")
        except ValueError:
            print("Invalid time format. Use HH:MM:SS")

    @staticmethod
    def countdown(seconds: int, callback=None):
        """
        Dem nguoc trong mot khoang thoi gian nhat dinh, co tuy chon kich hoat callback.
        :params seconds (int) - Thoi gian dem nguoc (giay).
        :parans callback (callable, optional) - Ham tuy chon duoc goi den sau khi hoan thanh.
        """
        while seconds > 0:
            mins, secs = divmod(seconds, 60)
            print(f"Countdown: {mins:02}:{secs:02}", end="\r")
            time.sleep(1)
            seconds -= 1
        if callback:
            callback()
        TimerUtils._send_notification("Countdown Timer", "Time's up!")

    @staticmethod
    def get_world_time(timezone: str) -> str:
        """
        Lay thoi gian hien tai cho mot mui gio cu the.
        (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List)
        :params timezone (str) - Mui gio khu vuc (e.g., "Asia/Ho_Chi_Minh", "Europe/London").
        :returns str - Thoi gian hien tai o mui gio khu vuc do.
        """
        try:
            tz = pytz.timezone(timezone)
            world_time = datetime.now(tz)
            return world_time.strftime("%d/%m/%Y %H:%M:%S")
        except pytz.UnknownTimeZoneError:
            return "Invalid timezone. Please check the timezone format."

    @staticmethod
    def _send_notification(title: str, message: str):
        """
        Gui thong bao len man hinh.
        :params title (str) - Tieu de thong bao.
        :params message (str) - Noi dung thong bao.
        """
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )
