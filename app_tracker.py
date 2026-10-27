
import time
import psutil
import win32gui
import win32process


def get_active_application():
    try:
        hwnd = win32gui.GetForegroundWindow()

        if not hwnd:
            return None

        _, process_id = win32process.GetWindowThreadProcessId(hwnd)

        process = psutil.Process(process_id)

        return process.name()

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


if __name__ == "__main__":
    print("Application tracking started...")

    last_app = None

    try:
        while True:
            app_name = get_active_application()

            if app_name and app_name != last_app:
                print("Active Application:", app_name)
                last_app = app_name

            time.sleep(1)

    except KeyboardInterrupt:
        print("Application tracking stopped.")
