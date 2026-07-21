from pathlib import Path
from typing import Any

def get_output_directory(video_path: str) -> Path:
    """
    Creates the following structure:

    Meeting_Agent/
    ├── Meetings/
    │     meeting.mp4
    │
    └── Meetings_Summary/
          meeting/
    """

    video = Path(video_path)

    # Meeting_Agent/Meetings
    meetings_folder = video.parent

    # Meeting_Agent
    project_root = meetings_folder.parent

    # Meeting_Agent/Summary
    summary_root = project_root / "Meetings_Summary"

    # Meeting_Agent/Summary/<meeting_name>
    meeting_folder = summary_root / video.stem

    meeting_folder.mkdir(parents=True, exist_ok=True)

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

def save_text_file(video_path: str, filename: str, content: Any) -> Path:
    """
    Saves text content into the meeting's output folder.
    """

    output_folder = get_output_directory(video_path)
    file_path = output_folder / filename

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

    file_path.write_text(text, encoding="utf-8")

    return file_path
