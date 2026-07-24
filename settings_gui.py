import customtkinter as ctk
from tkinter import filedialog
from watcher import start_watchdog, stop_watchdog
from utils1 import load_config,save_config
import threading


ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


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


def save_settings():

    settings = {
        "api_key": api_entry.get(),
        "meeting_folder": meeting_folder_entry.get(),
        "output_folder": output_folder_entry.get()
    }

    save_config(settings)

    status_label.configure(
        text="Status : Settings Saved"
    )


def load_settings():

    settings = load_config()

    api_entry.insert(
        0,
        settings.get("api_key", "")
    )

    meeting_folder_entry.insert(
        0,
        settings.get("meeting_folder", "")
    )

    output_folder_entry.insert(
        0,
        settings.get("output_folder", "")
    )


def start_monitoring():

    settings = load_config()

    meeting_folder = settings.get("meeting_folder", "")

    if meeting_folder == "":

        status_label.configure(
            text="Status : Please select a Meeting Folder"
        )

        return

    status_label.configure(
        text="Status : Monitoring..."
    )

    thread = threading.Thread(
        target=start_watchdog,
        args=(meeting_folder,),
        daemon=True
    )

    thread.start()

    start_button.configure(
        state="disabled"
    )

    print("Monitoring Started")

def stop_monitoring():

    stop_watchdog()

    status_label.configure(
        text="Status : Stopped"
    )

    start_button.configure(
        state="normal"
    )

# ------------------------------------
# GUI
# ------------------------------------
app = ctk.CTk()

app.title("Meeting Agent")
app.geometry("700x500")


# ------------------------------------
# Header Frame
# ------------------------------------
header_frame = ctk.CTkFrame(app)

header_frame.pack(
    fill="x",
    padx=20,
    pady=20
)

title = ctk.CTkLabel(
    header_frame,
    text="Meeting Agent",
    font=("Arial", 28, "bold")
)

title.pack(
    pady=15
)


# ------------------------------------
# Settings Frame
# ------------------------------------
settings_frame = ctk.CTkFrame(app)

settings_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=(0, 20)
)

settings_frame.grid_columnconfigure(
    1,
    weight=1
)


# ------------------------------------
# API KEY
# ------------------------------------
api_label = ctk.CTkLabel(
    settings_frame,
    text="Google API Key"
)

api_label.grid(
    row=0,
    column=0,
    padx=20,
    pady=20,
    sticky="w"
)

api_entry = ctk.CTkEntry(
    settings_frame
)

api_entry.grid(
    row=0,
    column=1,
    padx=(0, 20),
    pady=20,
    sticky="ew"
)


# ------------------------------------
# Meeting Folder
# ------------------------------------
meeting_folder_label = ctk.CTkLabel(
    settings_frame,
    text="Meeting Folder"
)

meeting_folder_label.grid(
    row=1,
    column=0,
    padx=20,
    pady=20,
    sticky="w"
)

meeting_folder_entry = ctk.CTkEntry(
    settings_frame
)

meeting_folder_entry.grid(
    row=1,
    column=1,
    padx=(0, 20),
    pady=20,
    sticky="ew"
)

meeting_folder_button = ctk.CTkButton(
    settings_frame,
    text="Browse",
    command=browse_meeting_folder
)

meeting_folder_button.grid(
    row=1,
    column=2,
    padx=(0, 20),
    pady=20
)


# ------------------------------------
# Output Folder
# ------------------------------------
output_folder_label = ctk.CTkLabel(
    settings_frame,
    text="Output Folder"
)

output_folder_label.grid(
    row=2,
    column=0,
    padx=20,
    pady=20,
    sticky="w"
)

output_folder_entry = ctk.CTkEntry(
    settings_frame
)

output_folder_entry.grid(
    row=2,
    column=1,
    padx=(0, 20),
    pady=20,
    sticky="ew"
)

output_folder_button = ctk.CTkButton(
    settings_frame,
    text="Browse",
    command=browse_output_folder
)

output_folder_button.grid(
    row=2,
    column=2,
    padx=(0, 20),
    pady=20
)


# ------------------------------------
# Buttons
# ------------------------------------
save_button = ctk.CTkButton(
    app,
    text="Save Settings",
    command=save_settings
)

save_button.pack(
    pady=20
)

# ------------------------------------
# Status
# ------------------------------------
status_label = ctk.CTkLabel(
    app,
    text="Status : Stopped",
    font=("Arial", 16)
)

status_label.pack(
    pady=(0, 20)
)

# ------------------------------------
# Buttons
# ------------------------------------

button_frame = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

button_frame.pack(
    pady=10
)

start_button = ctk.CTkButton(
    button_frame,
    text="Start Monitoring",
    command=start_monitoring
)

start_button.pack(
    side="left",
    padx=10
)

stop_button = ctk.CTkButton(
    button_frame,
    text="Stop Monitoring",
    command=stop_monitoring
)

stop_button.pack(
    side="left",
    padx=10
)

# ------------------------------------
# Load saved settings
# ------------------------------------
load_settings()

app.mainloop()