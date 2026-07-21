# 🎥 AI Meeting Assistant

An AI-powered meeting assistant built using **LangGraph**, **Google Gemini**, and **Python** that automatically watches a folder for new meeting recordings, generates a transcript, summarizes the discussion, extracts action items, and saves the results in a structured format.

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

The transcript generation itself is implemented as a **subgraph**.

```
START
   │
route_video
   │
   ├───────────────► transcript_node
   │
   │
   └───────────────► split_video_node
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

- ≤ 50 minutes
- Uploaded directly to Gemini
- Single transcript generated

## Long Videos

- > 50 minutes
- Split into 45-minute chunks using FFmpeg
- Chunks processed in parallel
- Individual transcripts merged in chronological order

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

↓

Transcript Subgraph

↓

Summary

↓

Action Items

↓

Notification

↓

END
```

---

## Transcript Subgraph

### Short Video

```
START

↓

Transcript

↓

END
```

### Long Video

```
START

↓

Split Video

↓

Fan-Out

↓

Chunk Workers

↓

Fan-In

↓

Merge Transcript

↓

END
```

---

# Folder Monitoring

The project continuously watches a folder using **Watchdog**.

Whenever a new meeting recording is detected:

1. Waits briefly for the file copy to finish.
2. Starts the Meeting Agent.
3. Generates all outputs.
4. Sends a desktop notification.

---

# Generated Files

For every meeting the project generates:

- transcript.txt
- summary.txt
- action_items.txt

---

# Error Handling

The project includes:

- Retry mechanism for temporary Gemini 503 errors.
- Parallel worker isolation.
- Automatic transcript merging.
- Video duration validation using FFprobe.
- Separate processing paths for short and long recordings.

---

# Requirements

- Python 3.11+
- FFmpeg installed and added to PATH
- Google Gemini API Key

Create a `.env` file:

```env
GOOGLE_API_KEY=YOUR_API_KEY
```

---

# Install

```bash
git clone https://github.com/yourusername/AI-Meeting-Assistant.git

cd AI-Meeting-Assistant

pip install -r requirements.txt
```

---

# Run

Start the folder watcher:

```bash
python test.py
```

Drop a meeting recording into the watched folder.

The assistant automatically processes the recording.

---

# Future Improvements

- Speaker diarization
- Meeting minutes generation
- PDF report generation
- Email delivery of meeting summary
- Calendar integration
- Cloud storage support
- Vector database for meeting search
- RAG over previous meetings
- Multi-language transcript export
- Web dashboard using Streamlit

---

# Author

Shivam Kharade

Built using LangGraph, Google Gemini and Python.