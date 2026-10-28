
import os
import subprocess
import sys
import tkinter as tk
from getpass import getpass
from dotenv import load_dotenv
from supabase import create_client
from datetime import datetime
from zoneinfo import ZoneInfo
from idle_monitor import IdleTimeTracker


# Load Supabase credentials from the .env file
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError(
        "SUPABASE_URL or SUPABASE_KEY is missing in the .env file."
    )

supabase = create_client(url, key)

def save_idle_reason(user_id, reason):
    # Save the logged-in user's selected reason
    supabase.table("useractivity").insert({
        "userid": str(user_id),
        "idle_reason": reason,
    }).execute()
    print("db save successful for user:", user_id, "with reason:", reason)

    return True



def login(root):
    # Get login details from the user
    name = input("Enter your user ID: ").strip()
    password = getpass("Enter your password: ")

    try:
        # Find the user in the Supabase users table
        result = (
            supabase.table("users")
            .select("user_id, password")
            .eq("user_id", name)
            .limit(1)
            .execute()
        )

        # Check whether the user exists
        if not result.data:
            print("Login Failed: User not found!")
            return False

        user = result.data[0]

        # Compare the entered password with the stored password
        if user["password"] != password:
            print("Login Failed: Incorrect password!")
            return False

        print("Login Successful!")


        # Start application_tracker.py after successful login
        tracker_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "app_tracker.py"
        )
        subprocess.Popen([sys.executable, tracker_path])

        # Save the login time in Indian Standard Time
        login_time = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).strftime("%H:%M:%S")

        # Insert the successful login activity into Supabase
        supabase.table("useractivity").insert({
            "userid": user["user_id"],
            "login_time": login_time
        }).execute()

        print("Login time saved:", login_time)

        # Create and start the idle monitor using the main Tkinter root
        monitor = IdleTimeTracker(
            root=root,
            idle_threshold=30,
            on_idle_reason=lambda reason:
            save_idle_reason(
                user["user_id"], reason
            ),
        )

        monitor.start()

        # Stop the monitor when the application window closes
        def close_application():
            monitor.stop()
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", close_application)

        print("Idle monitoring started. Stay inactive for 30 seconds to test.")
        return True

    except Exception as error:
        print("Login Error:", error)
        return False


if __name__ == "__main__":
    # Create Tkinter on the main thread
    root = tk.Tk()
    root.withdraw()

    # Ask for login credentials and start monitoring after success
    login_successful = login(root)

    if login_successful:
        # Run Tkinter's event loop on the main thread
        try:
            root.mainloop()
        finally:
            try:
                root.destroy()
            except tk.TclError:
                pass
    else:
        root.destroy()
