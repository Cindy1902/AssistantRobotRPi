import time
from plyer import notification


def start_pomodoro(work_time: int, break_time: int):
    """
    Bat dau bo dem Pomodoro.
    :params work_time (int): thoi gian lam viec (phut).
    :params break_time (int): thoi gian nghi (phut).
    :return
    """
    count = 0
    print(
        f"The pomodoro timer has started with {work_time} minutes and {break_time} minutes break, start working!!")

    try:
        while True:
            time.sleep(work_time * 60)
            count += 1
            notify(
                "Good Work!", f"Take a {break_time}-minute break. You have completed {count} pomodoros so far.")

            time.sleep(break_time * 60)
            notify("Back To Work!", "Try doing another pomodoro...")

    except KeyboardInterrupt:
        print("\nPomodoro timer stopped. Good job!")


def notify(title: str, message: str):
    """
    Gui thong bao he thong bang Plyer.
    :params title (str): tieu de cua thong bao.
    :params message (str): noi dung thong bao.
    """
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )
