# 🎥 AI Meeting Assistant

> **An AI-powered desktop automation application that continuously monitors a folder for new meeting recordings, intelligently processes them using Google Gemini, and automatically generates transcripts, summaries, action items, and organised meeting documentation.**

Built using **Python**, **LangGraph**, **LangChain**, **Google Gemini**, **CustomTkinter**, and **Watchdog**, this project demonstrates workflow orchestration, graph-based AI pipelines, desktop automation, parallel processing, and production-oriented application design.

---

# Table of Contents

- Overview
- Problem Statement
- Solution
- Key Features
- System Architecture
- Workflow Overview
- Validation Workflow
- Transcript Workflow
- Project Structure
- Technology Stack
- Engineering Decisions
- Installation
- Running the Application
- Output Structure
- Configuration
- Error Handling & Reliability
- Skills Demonstrated
- Future Enhancements
- Author

---

# Overview

The AI Meeting Assistant is a desktop application that automatically watches a user-selected folder for new meeting recordings.

Whenever a new recording appears, the application:

- Detects the recording automatically
- Verifies whether it has already been processed
- Generates a complete verbatim transcript
- Produces a professional meeting summary
- Extracts action items
- Organises all outputs into a dedicated meeting folder
- Notifies the user when processing is complete

The user simply drops a meeting recording into the monitored folder—the entire workflow is executed automatically.

---

# Problem Statement

Modern teams record hundreds of online meetings every month.

Finding information inside these recordings is difficult because users typically need to:

- Watch the entire recording
- Take manual notes
- Identify action items
- Organise documents manually

This becomes increasingly time-consuming as the number of meetings grows.

---

# Solution

This project automates the complete meeting documentation workflow using LangGraph-based AI pipelines.

It continuously monitors a meeting folder and automatically performs duplicate validation, transcript generation, summarisation, action-item extraction, PDF generation, and desktop notification.

---

# Key Features

- 📁 Automatic folder monitoring
- 🎥 Supports MP4, MKV, MOV, MP3 and WAV
- 🔐 SHA-256 duplicate meeting detection
- ✍️ Verbatim transcript generation
- 📝 AI meeting summaries
- ✅ Action item extraction
- ⚡ Automatic retry with exponential backoff
- 🔀 Long-video chunking
- 🚀 Parallel transcription using LangGraph Fan-Out / Fan-In
- 📄 PDF generation
- 📂 Meeting-specific output folders
- 🔔 Windows desktop notifications
- ⚙️ Persistent configuration

---

# System Architecture

```text
                    CustomTkinter GUI
                           │
                           ▼
                    Configuration
                           │
                           ▼
                 Watchdog Folder Monitor
                           │
                New Recording Detected
                           │
                           ▼
                  LangGraph Main Graph
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
     Validation Graph            Transcript Graph
             │                           │
     Duplicate?                  Short / Long
             │                           │
      ┌──────┴──────┐            ┌────────┴────────┐
      ▼             ▼            ▼                 ▼
     Stop      Continue      Direct AI      Chunk + Parallel
                                              │
                                              ▼
                                      Merge Transcript
                                              │
                         ┌────────────────────┴────────────────────┐
                         ▼                                         ▼
                   Summary Node                           Action Items Node
                         └────────────────────┬────────────────────┘
                                              ▼
                                      Notification Node
                                              ▼
                                             END
```

---

# Workflow Overview

```text
START
  │
Validation
  │
  ├── Duplicate ─────────► END
  │
  ▼
Transcript Graph
  │
  ├────────────┐
  ▼            ▼
Summary   Action Items
  └───────┬────┘
          ▼
   Notification
          ▼
         END
```

---

# Validation Workflow

1. Compute SHA-256 hash
2. Compare with processed meetings
3. Skip duplicates
4. Continue only for new meetings

---

# Transcript Workflow

Short meetings are processed directly.

Long meetings are:

- Split into 45-minute chunks
- Processed in parallel
- Merged back into a single transcript

---

# Project Structure

```text
AI-Meeting-Assistant/
│
├── settings_gui.py
├── watcher.py
├── Meeting_agent.py
├── validation_graph.py
├── video_transcript_generate.py
├── utils.py
├── config.json
├── processed_meetings.json
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Technology Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| Workflow | LangGraph |
| Prompting | LangChain |
| AI Model | Google Gemini |
| GUI | CustomTkinter |
| Monitoring | Watchdog |
| Video | FFmpeg / FFprobe |
| PDF | ReportLab |
| Notifications | Win11Toast |

---

# Engineering Decisions

## Why LangGraph?

The application is divided into independent graphs and nodes, making the workflow modular, maintainable and easy to extend.

## Why SHA-256?

Duplicate meetings are identified by content instead of filename, preventing unnecessary API usage.

## Why Watchdog?

The application behaves like a background desktop agent that automatically reacts to new recordings.

## Why Parallel Processing?

Long meetings are split into chunks and processed concurrently, reducing overall processing time.

---

# Installation

```bash
git clone https://github.com/yourusername/AI-Meeting-Assistant.git

cd AI-Meeting-Assistant

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```

Install FFmpeg and ensure both `ffmpeg` and `ffprobe` are available in your system PATH.

Create a Google Gemini API key from:

https://aistudio.google.com/app/apikey

---

# Running the Application

```bash
python settings_gui.py
```

Configure:

- Gemini API Key
- Meeting Folder
- Output Folder

Click **Save Settings**, then **Start Monitoring**.

---

# Output Structure

```text
Meeting_Output/
│
├── Sprint Planning/
│   ├── transcript.pdf
│   ├── summary.pdf
│   └── action_items.pdf
│
└── Client Meeting/
    ├── transcript.pdf
    ├── summary.pdf
    ├── action_items.pdf
    └── chunks/
```

---

# Error Handling & Reliability

- SHA-256 duplicate validation
- Retry with exponential backoff
- Parallel chunk processing
- Ordered transcript merging
- Desktop notifications
- Automatic configuration loading

---

# Skills Demonstrated

- Python
- LangGraph
- LangChain
- Google Gemini
- AI Workflow Design
- Parallel Processing
- Desktop Automation
- Prompt Engineering
- Desktop GUI Development
- File System Monitoring

---

# Future Enhancements

- Speaker diarisation
- Meeting sentiment analysis
- Vector database search
- RAG chatbot
- Microsoft Teams integration
- Zoom integration
- Calendar integration
- Docker deployment

---

# Author

**Shivam Kharade**

Built to demonstrate workflow orchestration, AI automation, desktop application development, and production-oriented software design.
