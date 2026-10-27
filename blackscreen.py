
import tkinter as tk
from tkinter import messagebox


class BlackScreen:
    def __init__(self, on_submit=None):
        self.on_submit = on_submit
        self.window = None
        self.reason_var = None
        self.submit_button = None

    def show(self):
        # Already open-ah irundha duplicate window create panna vendaam
        if self.window is not None:
            try:
                if self.window.winfo_exists():
                    self.window.lift()
                    return
            except tk.TclError:
                pass

        self.window = tk.Toplevel()
        self.window.title("Idle Reason")
        self.window.configure(bg="black")
        self.window.attributes("-fullscreen", True)
        self.window.attributes("-topmost", True)
        self.window.protocol("WM_DELETE_WINDOW", self.prevent_close)

        self.reason_var = tk.StringVar(value="")

        title = tk.Label(
            self.window,
            text="YOU ARE IDLE",
            font=("Arial", 28, "bold"),
            fg="white",
            bg="black",
        )
        title.pack(pady=(100, 20))

        instruction = tk.Label(
            self.window,
            text="Please select your idle reason",
            font=("Arial", 16),
            fg="white",
            bg="black",
        )
        instruction.pack(pady=10)

        reasons = ["Break", "Lunch", "Meeting", "Others"]

        for reason in reasons:
            radio = tk.Radiobutton(
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
            )
            radio.pack(anchor="center", pady=8)

        self.submit_button = tk.Button(
            self.window,
            text="Submit",
            font=("Arial", 14, "bold"),
            width=15,
            command=self.submit_reason,
        )
        self.submit_button.pack(pady=30)

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

        # Parent application-kku selected reason-ai anuppum
        if self.on_submit is not None:
            try:
                result = self.on_submit(reason)

                # Callback False return pannina close panna vendaam
                if result is False:
                    messagebox.showerror(
                        "Error",
                        "Reason could not be saved. Please try again.",
                        parent=self.window,
                    )
                    return

            except Exception as error:
                messagebox.showerror(
                    "Error",
                    f"Could not save idle reason:\n{error}",
                    parent=self.window,
                )
                return

        # Submit successful aana piragu mattum close aagum
        self.close()

    def prevent_close(self):
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
        # Compatibility method: existing code hide() call pannina
        self.close()


# Standalone test
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    def test_save_reason(reason):
        print("Selected idle reason:", reason)
        # Ithu test mattum; database-la save pannaadhu.
        return True

    black = BlackScreen(on_submit=test_save_reason)
    black.show()

    root.mainloop()
