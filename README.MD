# 🎥 AI Meeting Assistant

> **An AI-powered desktop application that automatically watches a folder for new meeting recordings, generates transcripts using Google Gemini, creates meeting summaries and action items, and organizes everything into structured meeting folders.**

Built using **Python**, **LangGraph**, **LangChain**, **Google Gemini**, **CustomTkinter**, **Watchdog**, and **FFmpeg**, this project demonstrates workflow orchestration, AI automation, desktop application development, parallel processing, and production-oriented software design.

---

# 🚀 Features

- 🎥 Automatic meeting recording detection
- 📂 Folder monitoring using Watchdog
- 🖥️ Desktop GUI using CustomTkinter
- 🔐 SHA-256 duplicate meeting detection
- 📄 Verbatim transcript generation
- 📝 AI-generated meeting summaries
- ✅ Automatic action item extraction
- 📑 PDF generation for all outputs
- 🚀 Parallel processing of long meetings
- ⚡ Fan-Out / Fan-In workflow using LangGraph
- 🔄 Meeting lifecycle tracking
- 🔔 Windows desktop notifications
- 📁 Automatic meeting-specific output folders
- ⚙️ Persistent configuration
- 🧵 Multi-threaded processing

---

# 🏗️ System Architecture

```text
                    CustomTkinter GUI
                           │
                           ▼
                 Save Configuration
                           │
                           ▼
                 Watchdog Folder Monitor
                           │
                New Recording Detected
                           │
                           ▼
                 Generate SHA-256 Hash
                           │
                           ▼
                 Main LangGraph Workflow
                           │
          ┌────────────────┴────────────────┐
          ▼                                 ▼
 Validation Graph                  Transcript Graph
          │                                 │
          ▼                                 ▼
Duplicate Check                 Short / Long Meeting
          │                                 │
          ▼                                 ▼
Already Processed?                 Split if Required
          │                                 │
          ▼                                 ▼
     Stop Processing          Parallel Chunk Transcription
                                            │
                                            ▼
                                   Merge Transcript
                                            │
                  ┌─────────────────────────┴────────────────────┐
                  ▼                                              ▼
          Summary Generator                           Action Item Generator
                  └─────────────────────────┬────────────────────┘
                                            ▼
                                   Desktop Notification
                                            ▼
                                           END
```

---

# 🔄 Workflow

```text
START
   │
Validation
   │
   ├──────── Already Processed ───────► END
   │
   ▼
Transcript Generation
   │
   ├─────────────┐
   ▼             ▼
Summary     Action Items
      \       /
       \     /
     Notification
          │
          ▼
         END
```

---

# ✅ Validation Workflow

Every meeting is uniquely identified using a **SHA-256 hash**.

The application maintains a persistent registry (`processed_meetings.json`) containing:

- Meeting Name
- File Path
- Meeting Hash
- Processing Status
- Last Completed Workflow Step

## Meeting Lifecycle

```text
new
 │
 ▼
processing (validation)
 │
 ▼
processing (transcript)
 │
 ▼
processing (summary)
 │
 ▼
processing (action_items)
 │
 ▼
completed
```

If the application crashes during processing:

```text
processing
      │
      ▼
failed
      │
      ▼
Automatic Retry
```

This ensures partially processed meetings are resumed instead of being treated as duplicates.

---

# 🎥 Transcript Workflow

The application automatically determines whether a meeting is **short** or **long**.

## Short Meetings

```text
Video
   │
   ▼
Gemini
   │
   ▼
Transcript
```

## Long Meetings

```text
Video
   │
   ▼
Split into 45-minute chunks
   │
   ▼
Fan-Out
   │
   ▼
Parallel Gemini Transcription
   │
   ▼
Merge
   │
   ▼
Final Transcript
```

Long recordings are processed significantly faster by transcribing multiple chunks simultaneously.

---

# 🛠️ Technology Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| Workflow | LangGraph |
| AI Framework | LangChain |
| LLM | Google Gemini |
| GUI | CustomTkinter |
| File Monitoring | Watchdog |
| Video Processing | FFmpeg / FFprobe |
| PDF Generation | ReportLab |
| Notifications | Win11Toast |

---

# 📂 Project Structure

```text
AI-Meeting-Assistant/
│
├── Meeting_agent.py
├── validation_graph.py
├── video_transcript_generate.py
├── watcher.py
├── settings_gui.py
├── utils1.py
│
├── config.json
├── processed_meetings.json
├── requirements.txt
├── README.md
│
├── output/
│
└── recordings/
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/<your-github-username>/AI-Meeting-Assistant.git

cd AI-Meeting-Assistant
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🎬 Install FFmpeg

The application requires **FFmpeg** and **FFprobe**.

Download:

https://ffmpeg.org/download.html

After installation:

- Add the **FFmpeg `bin`** folder to your system **PATH**.

Verify the installation:

```bash
ffmpeg -version

ffprobe -version
```

---

# 🔑 Create a Google Gemini API Key

Generate an API key from:

https://aistudio.google.com/app/apikey

---

# ▶️ How to Use

## Step 1

Run the application:

```bash
python settings_gui.py
```

---

## Step 2

Enter:

- Google Gemini API Key
- Meeting Folder
- Output Folder

---

## Step 3

Click:

```
Save Settings
```

---

## Step 4

Click:

```
Start Monitoring
```

The application will now monitor the selected meeting folder continuously.

---

## Step 5

Copy or move a meeting recording into the monitored folder.

Supported formats:

- MP4
- MOV
- MKV
- MP3
- WAV

---

## Step 6

The application automatically:

- Detects the meeting recording
- Computes the SHA-256 hash
- Checks for duplicates
- Generates a transcript
- Creates a meeting summary
- Extracts action items
- Saves all outputs as PDF files
- Displays a Windows notification when processing is complete

No manual intervention is required.

---

# 📁 Output Structure

```text
Output/

├── Sprint Planning/
│   ├── transcript.pdf
│   ├── summary.pdf
│   ├── action_items.pdf
│
├── Client Meeting/
│   ├── transcript.pdf
│   ├── summary.pdf
│   ├── action_items.pdf
│   └── chunks/
│
└── Team Sync/
    ├── transcript.pdf
    ├── summary.pdf
    └── action_items.pdf
```

---

# 🛡️ Error Handling & Reliability

The application includes:

- SHA-256 duplicate detection
- Meeting lifecycle tracking
- Automatic retry of failed meetings
- Thread-safe registry updates
- Multi-threaded meeting processing
- Automatic retry for temporary Gemini server errors
- Exponential backoff
- Parallel chunk transcription
- Ordered transcript merging

---

# 💡 Skills Demonstrated

- Python
- LangGraph
- LangChain
- Google Gemini API
- Workflow Orchestration
- AI Automation
- Prompt Engineering
- Desktop Application Development
- Parallel Processing
- Multi-threading
- File System Monitoring
- PDF Generation
- Software Architecture
- Error Recovery
- Production-Oriented Design

---

# 👨‍💻 Author

**Shivam Kharade**

This project was built to demonstrate modern AI workflow orchestration, desktop automation, LangGraph-based pipeline design, and production-oriented software engineering.

If you found this project interesting, feel free to ⭐ the repository.