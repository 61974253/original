
import threading
import time
from pynput import keyboard, mouse
from blackscreen import BlackScreen
import tkinter as tk

root = tk.Tk()
root.withdraw()

black = BlackScreen()


class IdleTimeTracker:
    def __init__(self, idle_threshold=30):
        self.idle_threshold = idle_threshold
        self.last_input = time.monotonic()
        self.idle_started = None
        self.total_idle_seconds = 0.0
        self.black = BlackScreen()

        self.running = False
        self._lock = threading.Lock()
        self._monitor_thread = None
        self._keyboard_listener = None
        self._mouse_listener = None

    def _record_input(self, *_args):
        now = time.monotonic()

        with self._lock:
            if not self.running:
                return

            if self.idle_started is not None:
                self.total_idle_seconds += (
                    now - self.idle_started
                )
                self.idle_started = None

            self.last_input = now

    def _monitor_loop(self):
        while self.running:
            now = time.monotonic()

            with self._lock:
                inactive_seconds = now - self.last_input

                if (
                    inactive_seconds >= self.idle_threshold
                    and self.idle_started is None
                ):
                    self.idle_started = (
                        self.last_input + self.idle_threshold
                    )
                    self.black.show()
                    print(
                        f"\rIdle Time: {self.get_idle_seconds() / 60:.2f} minutes",
                        end="",
                        flush=True
                    )

            time.sleep(0.25)

    def start(self):
        if self.running:
            return

        with self._lock:
            self.running = True
            self.last_input = time.monotonic()
            self.idle_started = None
            self.total_idle_seconds = 0.0

        self._keyboard_listener = keyboard.Listener(
            on_press=self._record_input,
            on_release=self._record_input,
        )

        self._mouse_listener = mouse.Listener(
            on_move=self._record_input,
            on_click=self._record_input,
            on_scroll=self._record_input,
        )

        self._keyboard_listener.start()
        self._mouse_listener.start()

        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
        )
        self._monitor_thread.start()

    def get_idle_seconds(self):
        with self._lock:
            total = self.total_idle_seconds

            if self.idle_started is not None:
                total += (
                    time.monotonic() - self.idle_started
                )

            return max(0.0, total)

    def get_idle_minutes(self):
        return int(self.get_idle_seconds() // 60)

    def stop(self):
        if not self.running:
            return

        now = time.monotonic()

        with self._lock:
            if self.idle_started is not None:
                self.total_idle_seconds += (
                    now - self.idle_started
                )
                self.idle_started = None

            self.running = False
            final_total = max(
                0.0, self.total_idle_seconds
            )

        if self._keyboard_listener is not None:
            self._keyboard_listener.stop()

        if self._mouse_listener is not None:
            self._mouse_listener.stop()

        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=1.0)

        return final_total


if __name__ == "__main__":
    tracker = IdleTimeTracker(idle_threshold=30)
    tracker.start()
    

    print("Idle tracking started. Press Ctrl+C to stop.")

    try:
        while True:
            print(
                f"\rTotal idle: "
                f"{tracker.get_idle_minutes():.1f} minutes",
                end="",
                flush=True,
            )
            time.sleep(1)
            root.mainloop()
            

    except KeyboardInterrupt:
        total = tracker.stop()
        print(f"\nTracking stopped. Total idle: {total:.1f} minutes")
