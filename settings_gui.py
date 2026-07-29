import customtkinter as ctk
from tkinter import filedialog
import threading

from watcher import start_watchdog, stop_watchdog
from utils1 import (
    load_config,
    save_config,
)
from gui_manager import gui_queue
# ----------------------------------------------------
# Appearance
# ----------------------------------------------------

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ----------------------------------------------------
# Main Window
# ----------------------------------------------------

app = ctk.CTk()

app.title("🎥 AI Meeting Assistant")

app.geometry("850x600")

app.minsize(850, 600)

# ----------------------------------------------------
# Helper Functions
# ----------------------------------------------------

def on_closing():

    try:
        stop_watchdog()
    except Exception:
        pass

    app.destroy()


app.protocol("WM_DELETE_WINDOW", on_closing)

def browse_meeting_folder():

    folder = filedialog.askdirectory()

    if folder:

        meeting_folder_entry.delete(0, "end")
        meeting_folder_entry.insert(0, folder)

def browse_output_folder():

    folder = filedialog.askdirectory()

    if folder:

        output_folder_entry.delete(0, "end")
        output_folder_entry.insert(0, folder)

def update_status(text):

    status_value.configure(text=text)


def update_meeting(text):

    meeting_value.configure(text=text)


def update_step(text):

    step_value.configure(text=text)

def process_gui_queue():

    while not gui_queue.empty():

        action, value = gui_queue.get()

        if action == "log":
            append_log(value)

        elif action == "status":
            update_status(value)

        elif action == "meeting":
            update_meeting(value)

        elif action == "step":
            update_step(value)

    app.after(100, process_gui_queue)

# ----------------------------------------------------
# Logging
# ----------------------------------------------------

def append_log(message):

    log_box.configure(state="normal")

    log_box.insert("end", message + "\n")

    log_box.see("end")

    log_box.configure(state="disabled")

# ----------------------------------------------------
# Save Settings
# ----------------------------------------------------

def save_settings():

    settings = {
        "api_key": api_entry.get(),
        "meeting_folder": meeting_folder_entry.get(),
        "output_folder": output_folder_entry.get()
    }

    save_config(settings)

    update_status("Settings Saved")

    append_log("Settings saved successfully.")

# ----------------------------------------------------
# Load Settings
# ----------------------------------------------------

def load_settings():

    settings = load_config()

    api_entry.delete(0, "end")
    api_entry.insert(
        0,
        settings.get("api_key", "")
    )

    meeting_folder_entry.delete(0, "end")
    meeting_folder_entry.insert(
        0,
        settings.get("meeting_folder", "")
    )

    output_folder_entry.delete(0, "end")
    output_folder_entry.insert(
        0,
        settings.get("output_folder", "")
    )

# ----------------------------------------------------
# Start Monitoring
# ----------------------------------------------------

def start_monitoring():

    meeting_folder = meeting_folder_entry.get().strip() 

    if meeting_folder == "":

        update_status("Select Meeting Folder")

        append_log("Please select a meeting folder.")

        return

    update_status("Monitoring")

    append_log("Monitoring started...")

    thread = threading.Thread(
        target=start_watchdog,
        args=(meeting_folder,),
        daemon=True
    )

    thread.start()

    start_button.configure(
    state="disabled"
    )

    stop_button.configure(
        state="normal"
    )

    meeting_folder_entry.configure(state="disabled")
    output_folder_entry.configure(state="disabled")
    api_entry.configure(state="disabled")

    meeting_folder_button.configure(state="disabled")
    output_folder_button.configure(state="disabled")

# ----------------------------------------------------
# Stop Monitoring
# ----------------------------------------------------

def stop_monitoring():

    stop_watchdog()

    update_status("Stopped")

    append_log("Monitoring stopped.")

    start_button.configure(
        state="normal"
    )

    stop_button.configure(
        state="disabled"
    )

    meeting_folder_entry.configure(state="normal")
    output_folder_entry.configure(state="normal")
    api_entry.configure(state="normal")

    meeting_folder_button.configure(state="normal")
    output_folder_button.configure(state="normal")

# ====================================================
# Header
# ====================================================

title = ctk.CTkLabel(
    app,
    text="🎥 AI Meeting Assistant",
    font=("Segoe UI", 24, "bold")
)

title.pack(
    pady=(15, 10)
)

# ====================================================
# Settings Frame
# ====================================================

settings_frame = ctk.CTkFrame(app)

settings_frame.pack(
    fill="x",
    padx=15,
    pady=(0, 10)
)

settings_frame.grid_columnconfigure(
    1,
    weight=1
)

# ====================================================
# API Key
# ====================================================

api_label = ctk.CTkLabel(
    settings_frame,
    text="Google API Key"
)

api_label.grid(
    row=0,
    column=0,
    padx=(15,10),
    pady=10,
    sticky="w"
)

api_entry = ctk.CTkEntry(
    settings_frame,
    placeholder_text="Enter your Gemini API Key",
    show="*"
)

api_entry.grid(
    row=0,
    column=1,
    padx=(0,15),
    pady=10,
    sticky="ew"
)

# ====================================================
# Meeting Folder
# ====================================================

meeting_folder_label = ctk.CTkLabel(
    settings_frame,
    text="Meeting Folder"
)

meeting_folder_label.grid(
    row=1,
    column=0,
    padx=(15,10),
    pady=8,
    sticky="w"
)

meeting_folder_entry = ctk.CTkEntry(
    settings_frame,
    placeholder_text="Select folder to monitor"
)

meeting_folder_entry.grid(
    row=1,
    column=1,
    padx=(0,10),
    pady=8,
    sticky="ew"
)

meeting_folder_button = ctk.CTkButton(
    settings_frame,
    text="Browse",
    width=110,
    command=browse_meeting_folder
)

meeting_folder_button.grid(
    row=1,
    column=2,
    padx=(0,15),
    pady=8
)

# ====================================================
# Output Folder
# ====================================================

output_folder_label = ctk.CTkLabel(
    settings_frame,
    text="Output Folder"
)

output_folder_label.grid(
    row=2,
    column=0,
    padx=(15,10),
    pady=(8,15),
    sticky="w"
)

output_folder_entry = ctk.CTkEntry(
    settings_frame,
    placeholder_text="Select output folder"
)

output_folder_entry.grid(
    row=2,
    column=1,
    padx=(0,10),
    pady=(8,15),
    sticky="ew"
)

output_folder_button = ctk.CTkButton(
    settings_frame,
    text="Browse",
    width=110,
    command=browse_output_folder
)

output_folder_button.grid(
    row=2,
    column=2,
    padx=(0,15),
    pady=(8,15)
)

# ====================================================
# Control Buttons
# ====================================================

button_frame = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

button_frame.pack(
    fill="x",
    padx=15,
    pady=(0,10)
)

save_button = ctk.CTkButton(
    button_frame,
    text="💾 Save Settings",
    width=140,
    command=save_settings
)

save_button.pack(
    side="left",
    padx=(0,10)
)

start_button = ctk.CTkButton(
    button_frame,
    text="▶ Start Monitoring",
    width=160,
    command=start_monitoring
)

start_button.pack(
    side="left",
    padx=(0,10)
)

stop_button = ctk.CTkButton(
    button_frame,
    text="■ Stop",
    width=110,
    command=stop_monitoring,
    state="disabled"
)

stop_button.pack(
    side="left"
)

# ====================================================
# Dashboard
# ====================================================

dashboard_frame = ctk.CTkFrame(app)

dashboard_frame.pack(
    fill="x",
    padx=15,
    pady=(0,10)
)

dashboard_frame.grid_columnconfigure(1, weight=1)

# ----------------------------------------------------
# Status
# ----------------------------------------------------

status_title = ctk.CTkLabel(
    dashboard_frame,
    text="Status",
    font=("Segoe UI", 12, "bold")
)

status_title.grid(
    row=0,
    column=0,
    padx=(15,10),
    pady=(15,5),
    sticky="w"
)

status_value = ctk.CTkLabel(
    dashboard_frame,
    text="Stopped"
)

status_value.grid(
    row=0,
    column=1,
    sticky="w",
    pady=(15,5)
)

# ----------------------------------------------------
# Current Meeting
# ----------------------------------------------------

meeting_title = ctk.CTkLabel(
    dashboard_frame,
    text="Current Meeting",
    font=("Segoe UI",12,"bold")
)

meeting_title.grid(
    row=1,
    column=0,
    padx=(15,10),
    pady=5,
    sticky="nw"
)

meeting_value = ctk.CTkLabel(
    dashboard_frame,
    text="None",
    justify="left",
    anchor="w",
    wraplength=600
)

meeting_value.grid(
    row=1,
    column=1,
    sticky="w",
    pady=5
)

# ----------------------------------------------------
# Current Step
# ----------------------------------------------------

step_title = ctk.CTkLabel(
    dashboard_frame,
    text="Current Step",
    font=("Segoe UI",12,"bold")
)

step_title.grid(
    row=2,
    column=0,
    padx=(15,10),
    pady=(5,15),
    sticky="nw"
)

step_value = ctk.CTkLabel(
    dashboard_frame,
    text="Waiting..."
)

step_value.grid(
    row=2,
    column=1,
    sticky="w",
    pady=(5,15)
)

# ====================================================
# Processing Log
# ====================================================

log_frame = ctk.CTkFrame(app)

log_frame.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=(0,10)
)

log_title = ctk.CTkLabel(
    log_frame,
    text="Processing Log",
    font=("Segoe UI", 14, "bold")
)

log_title.pack(
    anchor="w",
    padx=15,
    pady=(12,5)
)

log_box = ctk.CTkTextbox(
    log_frame,
    corner_radius=8,
    font=("Consolas", 11)
)

log_box.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=(0,15)
)

log_box.insert(
    "end",
    "=============================================\n"
)

log_box.insert(
    "end",
    " AI Meeting Assistant Started\n"
)

log_box.insert(
    "end",
    " Waiting for monitoring to begin...\n"
)

log_box.insert(
    "end",
    "=============================================\n\n"
)

log_box.configure(
    state="disabled"
)

# ====================================================
# Initial Values
# ====================================================

update_status("Stopped")

update_meeting("None")

update_step("Waiting...")

load_settings()

append_log("AI Meeting Assistant started.")

process_gui_queue()

app.mainloop()