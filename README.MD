# 🎥 AI Meeting Assistant

An AI-powered desktop application that automatically monitors a folder for new meeting recordings, generates a verbatim transcript using Google Gemini, summarizes the meeting, extracts action items, and organizes all outputs into meeting-specific folders.

The project is built using **Python**, **LangGraph**, **LangChain**, **Google Gemini**, and **CustomTkinter**, demonstrating graph-based AI workflows, parallel processing, desktop GUI development, and automation.

---

# Features

- 📁 Automatically monitors a folder for new meeting recordings.
- 🎥 Supports multiple media formats:
  - MP4
  - MKV
  - MOV
  - MP3
  - WAV
- ✍️ Generates a complete verbatim transcript.
- 📝 Produces a professional meeting summary.
- ✅ Extracts action items with assignee and deadline (if mentioned).
- 🔀 Automatically splits long meetings into smaller chunks.
- ⚡ Parallel transcription using LangGraph Fan-Out / Fan-In.
- 📂 Organizes outputs into meeting-specific folders.
- 💾 Saves configuration using `config.json`.
- 🖥️ Simple desktop GUI built with CustomTkinter.
- 🔔 Windows desktop notification after processing.
- 🔁 Automatic retry for temporary Gemini API failures.

---

# Project Architecture

```
                          CustomTkinter GUI
                                  │
                                  ▼
                            config.json
                                  │
                                  ▼
                             Watchdog
                                  │
                    Detect New Meeting Recording
                                  │
                                  ▼
                        LangGraph Main Workflow
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
 Transcript Subgraph         Summary Node          Action Items Node
        │                         │                         │
        └───────────────┬─────────┴───────────────┬─────────┘
                        ▼                         ▼
                  Notification Node
                        │
                        ▼
                       END
```

---

# LangGraph Workflow

## Main Graph

```
START
   │
   ▼
Transcript Subgraph
   │
   ├────────► Summary
   │
   └────────► Action Items
                    │
                    ▼
            Notification
                    │
                    ▼
                   END
```

---

## Transcript Subgraph

Before generating a transcript, the application checks the meeting duration.

### Short Meeting

```
START
   │
Route Video
   │
   ▼
Transcript Node
   │
   ▼
END
```

---

### Long Meeting

```
START
   │
Route Video
   │
   ▼
Split Video
   │
   ▼
Fan-Out
   │
   ├────────────┐
   ▼            ▼
Chunk 1     Chunk 2     Chunk 3 ...
   │            │
   ▼            ▼
Transcribe  Transcribe  Transcribe
   │            │
   └──────┬─────┘
          ▼
     Merge Transcript
          │
          ▼
         END
```

Long meetings are automatically divided into **45-minute chunks**, processed in parallel, and merged back together in the correct order.

---

# Project Structure

```
AI-Meeting-Assistant/
│
├── settings_gui.py
├── watcher.py
├── Metting_agent.py
├── video_tanscript_generate.py
├── utils.py
├── config.json
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Technologies Used

- Python
- LangGraph
- LangChain
- Google Gemini 2.5 Flash
- Google GenAI SDK
- CustomTkinter
- Watchdog
- FFmpeg
- FFprobe
- Win11Toast
- Threading
- JSON Configuration

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/AI-Meeting-Assistant.git

cd AI-Meeting-Assistant
```

---

## 2. Create a Virtual Environment

Windows

```bash
python -m venv venv
```

Activate it

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Install FFmpeg

Download FFmpeg from

https://www.gyan.dev/ffmpeg/builds/

Download the **Essentials Build**.

Extract it, for example:

```
C:\ffmpeg
```

Your directory should look like

```
C:\ffmpeg
│
└── bin
    ├── ffmpeg.exe
    ├── ffprobe.exe
    └── ffplay.exe
```

---

## Add FFmpeg to PATH

Add

```
C:\ffmpeg\bin
```

to your Windows PATH.

Verify the installation.

```bash
ffmpeg -version
```

```bash
ffprobe -version
```

Both commands should display version information.

---

# Create a Gemini API Key

Create a free API key from

https://aistudio.google.com/app/apikey

---

# Running the Application

Launch the GUI.

```bash
python settings_gui.py
```

---

# GUI

The application provides a simple desktop interface.

Fill in:

- Google Gemini API Key
- Meeting Folder
- Output Folder

Click

```
Save Settings
```

The application stores these values inside

```
config.json
```

so they are automatically loaded the next time the application starts.

---

After saving the settings, click

```
Start Monitoring
```

The application will continuously monitor the selected meeting folder.

Whenever a new meeting recording is added, processing begins automatically.

---

To stop monitoring, click

```
Stop Monitoring
```

---

# Supported File Formats

- MP4
- MOV
- MKV
- MP3
- WAV

---

# Processing Pipeline

Whenever a new recording is detected:

1. Watchdog detects the file.
2. Waits briefly until copying is complete.
3. LangGraph workflow starts.
4. Meeting duration is checked.
5. Short meetings are uploaded directly.
6. Long meetings are split into chunks.
7. Gemini generates a verbatim transcript.
8. LangChain generates:
   - Meeting Summary
   - Action Items
9. Files are saved.
10. Windows notification is displayed.

---

# Output Structure

The selected output folder will contain one folder for every meeting.

```
Output Folder
│
├── Sprint Planning/
│   ├── transcript.txt
│   ├── summary.txt
│   ├── action_items.txt
│
├── Client Meeting/
│   ├── transcript.txt
│   ├── summary.txt
│   ├── action_items.txt
│
└── Quarterly Review/
    ├── transcript.txt
    ├── summary.txt
    ├── action_items.txt
    └── chunks/
        ├── chunk_000.mp4
        ├── chunk_001.mp4
        └── chunk_002.mp4
```

The `chunks` directory is created only for long meetings.

---

# Configuration

All application settings are stored in

```
config.json
```

Example

```json
{
    "api_key": "YOUR_GEMINI_API_KEY",
    "meeting_folder": "C:/Meetings",
    "output_folder": "C:/Meeting_Output"
}
```

The application automatically reads this configuration every time it starts.

---

# Error Handling

The application includes several reliability features.

- Automatic retry for temporary Gemini API failures.
- Validation of meeting duration.
- Parallel chunk processing.
- Ordered transcript merging.
- Meeting-specific output folders.
- File monitoring with Watchdog.
- Windows notification after successful completion.

---

# Learning Highlights

This project demonstrates practical experience with

- LangGraph StateGraph
- Subgraphs
- Fan-Out / Fan-In architecture
- Parallel AI workflows
- LangChain Prompt Templates
- Google Gemini API
- Desktop GUI development
- Folder monitoring automation
- File processing
- Configuration management
- AI-powered workflow automation

---

# Author

**Shivam Kharade**

Built with Python, LangGraph, LangChain, Google Gemini, and CustomTkinter.