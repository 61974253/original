
import threading
import time
import tkinter as tk
from pynput import keyboard, mouse
from blackscreen import BlackScreen


class IdleTimeTracker:
    def __init__(self, root, on_idle_reason=None, idle_threshold=30):
        # Use the Tkinter root created by the main thread
        self.root = root
        self.idle_threshold = idle_threshold
        self.on_idle_reason = on_idle_reason  # Callback for idle reason submission
        self.black = BlackScreen(root, on_submit=on_idle_reason)

        self.last_input = time.monotonic()
        self.idle_started = None
        self.total_idle_seconds = 0.0

        self.running = False
        self._lock = threading.Lock()
        self._keyboard_listener = None
        self._mouse_listener = None
        self._check_job = None

    def _record_input(self, *_args):
        # Record keyboard or mouse activity
        now = time.monotonic()

        with self._lock:
            if not self.running:
                return

            if self.idle_started is not None:
                # Finish the idle period when activity resumes
                self.total_idle_seconds += (
                    now - self.idle_started
                )
                self.idle_started = None

                # Ask Tkinter main thread to close the black screen

            self.last_input = now

    def _check_idle(self):
        # This method runs on the Tkinter main thread
        if not self.running:
            return

        show_black_screen = False

        with self._lock:
            now = time.monotonic()
            inactive_seconds = now - self.last_input

            if (
                inactive_seconds >= self.idle_threshold
                and self.idle_started is None
            ):
                self.idle_started = (
                    self.last_input + self.idle_threshold
                )
                show_black_screen = True

            total = self.total_idle_seconds

            if self.idle_started is not None:
                total += now - self.idle_started

        # Open the window on the main thread, not a worker thread
        if show_black_screen:
            self.black.show()

        print(
            f"\rTotal idle: {total / 60:.2f} minutes",
            end="",
            flush=True,
        )

        # Schedule the next check on the main thread
        if self.running:
            self._check_job = self.root.after(
                250, self._check_idle
            )

    def start(self):
        if self.running:
            return

        with self._lock:
            self.running = True
            self.last_input = time.monotonic()
            self.idle_started = None
            self.total_idle_seconds = 0.0

        # Listen for keyboard activity
        self._keyboard_listener = keyboard.Listener(
            on_press=self._record_input,
            on_release=self._record_input,
        )

        # Listen for mouse activity
        self._mouse_listener = mouse.Listener(
            on_move=self._record_input,
            on_click=self._record_input,
            on_scroll=self._record_input,
        )

        self._keyboard_listener.start()
        self._mouse_listener.start()

        # Start periodic checks on the Tkinter main thread
        self._check_job = self.root.after(
            250, self._check_idle
        )

    def get_idle_seconds(self):
        with self._lock:
            total = self.total_idle_seconds

            if self.idle_started is not None:
                total += time.monotonic() - self.idle_started

            return max(0.0, total)

    def get_idle_minutes(self):
        return self.get_idle_seconds() / 60

    def stop(self):
        with self._lock:
            if not self.running:
                return self.total_idle_seconds

            if self.idle_started is not None:
                self.total_idle_seconds += (
                    time.monotonic() - self.idle_started
                )
                self.idle_started = None

            self.running = False
            final_total = self.total_idle_seconds

        # Cancel the scheduled Tkinter check
        if self._check_job is not None:
            try:
                self.root.after_cancel(self._check_job)
            except tk.TclError:
                pass
            self._check_job = None

        if self._keyboard_listener is not None:
            self._keyboard_listener.stop()

        if self._mouse_listener is not None:
            self._mouse_listener.stop()

        # Close the idle window on the main thread
        self.black.hide()

        return final_total


if __name__ == "__main__":
    # Create Tkinter on the main thread
    root = tk.Tk()
    root.withdraw()

    tracker = IdleTimeTracker(
        root=root,
        idle_threshold=30,
    )

    tracker.start()

    print("Idle tracking started.")
    print("The idle reason window opens after 30 seconds.")
    print("Close the application window or stop the program to exit.")

    try:
        root.mainloop()
    finally:
        total = tracker.stop()

        try:
            root.destroy()
        except tk.TclError:
            pass

        print(
            f"\nTracking stopped. "
            f"Total idle: {total / 60:.2f} minutes"
        )
