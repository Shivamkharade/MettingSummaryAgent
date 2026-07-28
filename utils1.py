from pathlib import Path
from typing import Any
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import json
import threading
import hashlib

PROCESSED_MEETINGS_FILE = Path("processed_meetings.json")
CONFIG_FILE = Path("config.json")
Global_model = 'gemini-3.6-flash'
meeting_registry_lock = threading.Lock()

def get_output_directory(video_path: str) -> Path:

    config = load_config()

    output_folder = config.get("output_folder", "")

    if not output_folder:
        raise ValueError("Output folder is not configured.")

    output_root = Path(output_folder)

    video = Path(video_path)

    meeting_folder = output_root / video.stem

    meeting_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    return meeting_folder

def extract_text(response):

    content = response.content

    if isinstance(content, str):
        return content

    elif isinstance(content, dict):
        return content.get("text", "")

    elif isinstance(content, list):
        parts = []

        for item in content:

            if isinstance(item, dict):
                parts.append(item.get("text", ""))

            elif hasattr(item, "text"):
                parts.append(item.text)

            else:
                parts.append(str(item))

        return "\n".join(parts)

    return str(content)

def load_config():

    if not CONFIG_FILE.exists():
        return {
            "api_key": "",
            "meeting_folder": "",
            "output_folder": ""
        }

    with open(CONFIG_FILE, "r") as file:
        return json.load(file)

def save_config(settings):

    with open(CONFIG_FILE, "w") as file:
        json.dump(settings, file, indent=4)

def get_api_key() -> str:

    api_key = load_config().get("api_key", "").strip()

    print(f"Loaded API Key: {api_key}")

    return api_key

def get_gemini_client():
    return genai.Client(api_key=get_api_key())

def get_llm():
    return ChatGoogleGenerativeAI(
        model=Global_model,
        google_api_key=get_api_key()
    )

def save_text_file(video_path: str, filename: str, content: Any) -> Path:
    """
    Saves content into a PDF file inside the meeting's output folder.

    Example:
        save_pdf_file(video_path, "summary.pdf", summary)
    """

    output_folder = get_output_directory(video_path)

    # Ensure the filename ends with .pdf
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    file_path = output_folder / filename

    # Convert different content types to text
    if isinstance(content, str):
        text = content

    elif isinstance(content, dict):
        text = content.get("text", str(content))

    elif isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(item.get("text", ""))
            elif hasattr(item, "text"):
                parts.append(item.text)
            else:
                parts.append(str(item))
        text = "\n".join(parts)

    else:
        text = str(content)

    # Create PDF
    doc = SimpleDocTemplate(str(file_path))
    styles = getSampleStyleSheet()
    style = styles["BodyText"]

    story = []

    # Preserve line breaks
    for line in text.splitlines():
        line = line.strip()
        if line:
            story.append(Paragraph(line.replace("\n", "<br/>"), style))
        else:
            story.append(Paragraph("&nbsp;", style))

    doc.build(story)

    return file_path

def load_processed_meetings() -> dict:
    """
    Load the processed meetings JSON.

    Returns:
        {
            "meetings": []
        }
        if the file doesn't exist.
    """

    if not PROCESSED_MEETINGS_FILE.exists():
        return {
            "meetings": []
        }

    with open(PROCESSED_MEETINGS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def save_processed_meetings(data: dict) -> None:
    """
    Save the processed meetings JSON.
    """

    with open(PROCESSED_MEETINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def update_meeting_status(
    meeting_hash: str,
    status: str,
    last_completed_step: str | None = None,
) -> None:
    """
    Updates the status and/or last completed step for a meeting.

    Parameters
    ----------
    meeting_hash : str
        SHA-256 hash of the meeting.

    status : str
        processing / completed / failed

    last_completed_step : str | None
        Name of the most recently completed node.
    """

    with meeting_registry_lock:

        meetings = load_processed_meetings()

        for meeting in meetings["meetings"]:

            if meeting["hash"] == meeting_hash:

                meeting["status"] = status

                if last_completed_step is not None:
                    meeting["last_completed_step"] = last_completed_step

                save_processed_meetings(meetings)

                return

        raise ValueError(
            f"Meeting with hash '{meeting_hash}' was not found."
        )

def generate_meeting_hash(path: str) -> str:

    sha256 = hashlib.sha256()

    with open(path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()