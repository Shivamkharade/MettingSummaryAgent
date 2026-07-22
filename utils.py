from pathlib import Path
from typing import Any
from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
import json


CONFIG_FILE = Path("config.json")

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
        model="gemini-2.5-flash",
        google_api_key=get_api_key()
    )