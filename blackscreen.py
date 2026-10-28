
import tkinter as tk
from tkinter import messagebox


class BlackScreen:
    def __init__(self, root, on_submit=None):
        self.root = root
        self.on_submit = on_submit
        self.window = None
        self.reason_var = None

    def show(self):
        # Avoid opening duplicate black screens
        if self.window is not None:
            try:
                if self.window.winfo_exists():
                    self.window.lift()
                    return
            except tk.TclError:
                pass

        self.window = tk.Toplevel(self.root)
        self.window.title("Idle Reason")
        self.window.configure(bg="black")
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-topmost", True)

        # Prevent closing without submitting a reason
        self.window.protocol(
            "WM_DELETE_WINDOW", self.prevent_close
        )

        self.reason_var = tk.StringVar(value="")

        tk.Label(
            self.window,
            text="YOU ARE IDLE",
            font=("Arial", 28, "bold"),
            fg="white",
            bg="black",
        ).pack(pady=(100, 20))

        tk.Label(
            self.window,
            text="Please select your idle reason",
            font=("Arial", 16),
            fg="white",
            bg="black",
        ).pack(pady=10)

        for reason in ["Break", "Lunch", "Meeting", "Others"]:
            tk.Radiobutton(
                self.window,
                text=reason,
                variable=self.reason_var,
                value=reason,
                font=("Arial", 15),
                fg="white",
                bg="black",
                selectcolor="black",
                activebackground="black",
                activeforeground="white",
            ).pack(anchor="center", pady=8)

        tk.Button(
            self.window,
            text="Submit",
            font=("Arial", 14, "bold"),
            width=15,
            command=self.submit_reason,
        ).pack(pady=30)

        self.window.focus_force()
        self.window.grab_set()

    def submit_reason(self):
        reason = self.reason_var.get()

        if not reason:
            messagebox.showwarning(
                "Reason Required",
                "Please select an idle reason.",
                parent=self.window,
            )
            return

        if self.on_submit is None:
            messagebox.showerror(
                "Error",
                "Database save function is not connected.",
                parent=self.window,
            )
            return

        try:
            result = self.on_submit(reason)

            if result is False:
                return

            self.close()

        except Exception as error:
            messagebox.showerror(
                "Database Error",
                str(error),
                parent=self.window,
            )

    def prevent_close(self):
        # Keep the screen open until Submit is clicked
        messagebox.showinfo(
            "Idle Reason Required",
            "Please select a reason and click Submit.",
            parent=self.window,
        )

    def close(self):
        if self.window is not None:
            try:
                self.window.grab_release()
            except tk.TclError:
                pass

            try:
                self.window.destroy()
            except tk.TclError:
                pass

            self.window = None

    def hide(self):
        # Keep compatibility with idle_monitor.py
        self.close()
