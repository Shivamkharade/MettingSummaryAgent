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
- 🛡️ Centralized exception handling
- 📄 Automatic error.log generation for failed meetings
- 🔍 Chained exception tracing for easier debugging

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
                  Main Meeting Graph
                           │
                           ▼
                  Validation Graph
                           │
                           ▼
           New / Retry / Completed Meeting
                           │
                           ▼
                  Restore Previous State
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
   Transcript Graph     Summary        Action Items
         │                                   │
         └─────────────────┬─────────────────┘
                           ▼
                 Windows Notification
                           │
                           ▼
              Centralized Error Handler
                           │
                           ▼
                          END
```

---

# 🔄 Main Workflow

```text
START
   │
   ▼
Validation Graph
   │
   ▼
Restore Previous State
   │
   ├──────────────► Transcript
   │
   ├──────────────► Summary
   │
   ├──────────────► Action Items
   │
   └──────────────► Notification
           │
           ▼
          END
```
The application resumes processing from the last successfully completed workflow step instead of restarting the entire pipeline.

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
New Meeting
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

If processing is interrupted:

```text
processing
      │
      ▼
failed
      │
      ▼
Restore Previous State
      │
      ▼
Resume Processing
```
---

# ♻️ Workflow Restoration

The application supports automatic workflow restoration after interruptions.

Instead of regenerating every AI artifact, previously generated outputs are restored from disk using the `last_completed_step` stored in the meeting registry.

This allows the workflow to resume from exactly where it stopped.

Example:

```text
Validation
      │
      ▼
Transcript Generated
      │
      ▼
Summary Generated
      │
      ▼
Application Closed
      │
      ▼
Restart
      │
      ▼
Restore Transcript
Restore Summary
      │
      ▼
Generate Action Items
      │
      ▼
Notification
```

Previously completed AI tasks are never regenerated unnecessarily, reducing API usage and processing time.

---
# 🧩 LangGraph Architecture

The application is composed of three independent LangGraph workflows.

```text
                 Main Meeting Graph
                        │
                        ▼
                Validation Graph
                        │
                        ▼
                Restore State Node
                        │
                        ▼
               Transcript Graph
                        │
                        ▼
                  Summary Node
                        │
                        ▼
               Action Items Node
                        │
                        ▼
               Notification Node
```

Separating the application into multiple graphs keeps responsibilities isolated, improves maintainability, and simplifies future extensions.

---

# 🛡️ Error Handling

The application uses a centralized exception handling system designed to make debugging and recovery easier.

Every workflow node raises meaningful exceptions, which are propagated through the LangGraph workflow using Python's exception chaining (`raise ... from e`).

When a failure occurs, the application automatically:

- Captures the complete traceback
- Preserves the entire exception chain
- Marks the meeting as **failed**
- Resets the application state
- Generates an `error.log` file inside the meeting output folder
- Allows failed meetings to be retried automatically

Example exception flow:

```text
Gemini Server Error
        │
        ▼
Transcript Node
        │
        ▼
Transcript Graph
        │
        ▼
Meeting Graph
        │
        ▼
Centralized Error Handler
```

---

# 🎥 Transcript Graph

Transcript generation is handled by a dedicated LangGraph workflow.

## Short Meetings

```text
Video
   │
   ▼
Upload to Gemini
   │
   ▼
Generate Transcript
```

---

## Long Meetings

```text
Video
   │
   ▼
Split into 45-minute Chunks
   │
   ▼
          Fan-Out
   ┌────────┼────────┐
   ▼        ▼        ▼
Chunk 1  Chunk 2  Chunk 3
   │        │        │
Gemini   Gemini   Gemini
   ▼        ▼        ▼
   └────────┼────────┘
            ▼
     Merge Transcript
            ▼
     Final Transcript
```

Large meetings are processed significantly faster by transcribing multiple chunks in parallel before merging them into a single transcript.

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

├── Meeting_agent.py
├── validation_graph.py
├── video_transcript_generate.py
├── watcher.py
├── error_handler.py
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

Sprint Planning/

├── transcript.pdf
├── summary.pdf
├── action_items.pdf
│
├── restore/
│   ├── transcript.txt
│   ├── summary.txt
│   ├── action_items.txt
│   └── error.log
│
└── chunks/
```

The `restore` directory stores intermediate workflow outputs, allowing interrupted meetings to resume without regenerating completed AI tasks.

---

# 🛡️ Error Handling & Reliability

The application includes:

- SHA-256 duplicate detection
- Meeting lifecycle tracking
- Automatic workflow restoration
- Restore previous workflow state
- Automatic retry of failed meetings
- Thread-safe registry updates
- Multi-threaded meeting processing
- Automatic retry for temporary Gemini server errors
- Exponential backoff
- Parallel chunk transcription
- Ordered transcript merging
- Centralized exception handling
- Exception chaining using `raise ... from e`
- Automatic error log generation
- Graceful recovery after processing failures

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