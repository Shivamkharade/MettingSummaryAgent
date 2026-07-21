# 🎥 AI Meeting Assistant

An AI-powered meeting assistant built using **LangGraph**, **Google Gemini**, and **Python** that automatically watches a folder for new meeting recordings, generates a verbatim transcript, summarizes the discussion, extracts action items, and saves the results in a structured format.

---

# Features

- 📁 Automatically monitors a folder for new meeting recordings.
- 🎥 Supports:
  - MP4
  - MKV
  - MOV
  - MP3
  - WAV
- ✍️ Generates a complete verbatim transcript.
- 📝 Creates a concise meeting summary.
- ✅ Extracts action items with assignee and deadlines.
- 🔔 Sends a Windows notification when processing completes.
- 📂 Organizes outputs into meeting-specific folders.
- ⚡ Parallel transcription for long meetings using LangGraph Fan-Out/Fan-In architecture.
- 🔁 Automatic retry for temporary Gemini API failures.

---

# Project Architecture

```
                   Watchdog
                      │
                      ▼
              New Meeting File
                      │
                      ▼
               Meeting Graph
                      │
      ┌───────────────┴───────────────┐
      ▼                               ▼
 Transcript Graph                Summary Node
      │                               │
      │                         Action Items Node
      │                               │
      └───────────────┬───────────────┘
                      ▼
              Notification Node
```

---

# Transcript Graph

The transcript generation is implemented as a dedicated **LangGraph subgraph**.

```
START
   │
route_video
   │
   ├──────────────► transcript_node
   │
   └──────────────► split_video_node
                           │
                           ▼
                     Fan-Out (Send)
                           │
          ┌────────┬────────┬────────┐
          ▼        ▼        ▼        ▼
     transcribe_chunk_node
          ▼        ▼        ▼        ▼
          └────────┴────────┴────────┘
                    Fan-In
                      │
                      ▼
             merge_transcripts_node
                      │
                     END
```

---

# Long Video Processing

Videos are classified into two categories.

## Short Videos

- Duration ≤ 50 minutes
- Uploaded directly to Google Gemini
- Transcript generated in a single request

## Long Videos

- Duration > 50 minutes
- Split into 45-minute chunks using FFmpeg
- Chunks processed in parallel using LangGraph Fan-Out
- Individual transcripts merged back together in the correct order

---

# Output Structure

```
Meetings/
│
├── TeamMeeting.mp4
├── SprintReview.mp4

Meetings_Summary/
│
├── TeamMeeting/
│      transcript.txt
│      summary.txt
│      action_items.txt
│
└── SprintReview/
       transcript.txt
       summary.txt
       action_items.txt
```

---

# Technologies Used

- Python
- LangGraph
- LangChain
- Google Gemini 2.5 Flash
- Google GenAI SDK
- FFmpeg
- FFprobe
- Watchdog
- Windows Toast Notifications

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

### Short Video

```
START
   │
   ▼
Transcript
   │
   ▼
END
```

### Long Video

```
START
   │
   ▼
Split Video
   │
   ▼
Fan-Out
   │
   ▼
Chunk Workers
   │
   ▼
Fan-In
   │
   ▼
Merge Transcript
   │
   ▼
END
```

---

# Folder Monitoring

The project continuously monitors a folder using **Watchdog**.

Whenever a new meeting recording is detected:

1. Waits briefly for the file copy to finish.
2. Starts the Meeting Agent.
3. Generates:
   - Transcript
   - Summary
   - Action Items
4. Saves the generated files.
5. Sends a Windows desktop notification.

---

# Generated Files

For every meeting recording the following files are generated:

- `transcript.txt`
- `summary.txt`
- `action_items.txt`

---

# Error Handling

The project includes:

- Automatic retry for temporary Gemini API (503) errors.
- Parallel chunk processing.
- Transcript merging after all workers complete.
- Video duration validation using FFprobe.
- Separate execution paths for short and long videos.

---

# Prerequisites

Before running the project, ensure the following software is installed.

## 1. Install Python

Download Python 3.11 or later from:

https://www.python.org/downloads/

Verify the installation:

```bash
python --version
```

---

## 2. Install FFmpeg

Download FFmpeg from:

https://www.gyan.dev/ffmpeg/builds/

Download the **Essentials Build** ZIP file.

Extract it to a location such as:

```
C:\ffmpeg
```

The folder structure should look like:

```
C:\ffmpeg
│
└── bin
     │
     ├── ffmpeg.exe
     ├── ffprobe.exe
     └── ffplay.exe
```

---

### Add FFmpeg to Windows PATH

1. Press **Windows Key**
2. Search for **Environment Variables**
3. Open **Edit the system environment variables**
4. Click **Environment Variables**
5. Under **System Variables**, select **Path**
6. Click **Edit**
7. Click **New**
8. Add:

```
C:\ffmpeg\bin
```

9. Click **OK** on all windows.

Restart your terminal.

Verify the installation:

```bash
ffmpeg -version
```

and

```bash
ffprobe -version
```

Both commands should print the installed version.

---

## 3. Create a Google Gemini API Key

Create a free API key from:

https://aistudio.google.com/app/apikey

---

## 4. Clone the Repository

```bash
git clone https://github.com/yourusername/AI-Meeting-Assistant.git

cd AI-Meeting-Assistant
```

---

## 5. Create a Virtual Environment

Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

## 6. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 7. Configure Environment Variables

Create a file named:

```
.env
```

Add your Gemini API key:

```env
GOOGLE_API_KEY=YOUR_API_KEY
```

---

## 8. Configure the Watch Folder

Open:

```
watcher.py
```

Modify:

```python
WATCH_FOLDER = r"YOUR_MEETING_FOLDER"
```

Example:

```python
WATCH_FOLDER = r"C:\Meetings"
```

---

# Run the Project

Start the watcher:

```bash
python watcher.py
```

Now copy or move a meeting recording into the configured watch folder.

The Meeting Assistant will automatically:

- Detect the new recording
- Generate a transcript
- Generate a summary
- Extract action items
- Save the generated files
- Display a Windows notification

---

# Future Improvements

- Speaker diarization
- Meeting minutes generation
- PDF report generation
- Email delivery
- Calendar integration
- Cloud storage support
- Vector database for meeting search
- RAG over previous meetings
- Multi-language transcript export
- Streamlit web dashboard

---

# Author

**Shivam Kharade**

Built using **LangGraph**, **Google Gemini**, **LangChain**, and **Python**.