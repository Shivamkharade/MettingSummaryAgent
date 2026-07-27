from typing import TypedDict,Optional
from langgraph.graph import StateGraph,START,END
from utils1 import (
    load_processed_meetings,
    save_processed_meetings,
    get_output_directory,
    meeting_registry_lock
)
from win11toast import toast
import hashlib
from pathlib import Path


class ValidationState(TypedDict):
    video_path: str
    meeting_hash: Optional[str]
    already_processed: Optional[bool]
    continue_processing: Optional[bool]

def route_meeting(state):
    if state["already_processed"]:
        return "already_processed"

    return "new_meeting"

def generate_hash_node(state: ValidationState):
    sha256 = hashlib.sha256()

    with open(state["video_path"], "rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)
    
    meetings = load_processed_meetings()
    
    save_processed_meetings(meetings)

    return {
        "meeting_hash": sha256.hexdigest()
    }

def check_processed_node(state: ValidationState):

    with meeting_registry_lock:

        meetings = load_processed_meetings()

        matching_meeting = next(
            (
                meeting
                for meeting in meetings["meetings"]
                if meeting["hash"] == state["meeting_hash"]
            ),
            None
        )

    if matching_meeting:
        return {
            "already_processed": True,
            "video_path": matching_meeting["file_path"],
        }

    return {
        "already_processed": False,
        "video_path": state["video_path"],
    }
    
def save_new_meeting_node(state: ValidationState):

    with meeting_registry_lock:

        meetings = load_processed_meetings()

        meetings["meetings"].append({
            "name": Path(state["video_path"]).name,
            "file_path": state["video_path"],
            "hash": state["meeting_hash"],
        })

        save_processed_meetings(meetings)

    return {
        "continue_processing": True
    }
    
def already_processed_notification_node(state: ValidationState):

    output_folder = get_output_directory(state["video_path"])

    toast(
        "⚠️ Meeting Already Processed",
        f"{Path(state['video_path']).stem}\n\n"
        "This meeting has already been processed.",
        buttons=[
            {
                "activationType": "protocol",
                "arguments": output_folder.as_uri(),
                "content": "📂 Open Folder"
            },
            {
                "activationType": "system",
                "arguments": "dismiss",
                "content": "Dismiss"
            }
        ]
    )

    return {
        'continue_processing' : False
    }

builder = StateGraph(ValidationState)

builder.add_node("generate_hash", generate_hash_node)
builder.add_node("check_processed", check_processed_node)
builder.add_node("already_processed_notification", already_processed_notification_node)
builder.add_node('save_new_meeting',save_new_meeting_node)

builder.add_edge(START, "generate_hash")

builder.add_edge(
    "generate_hash",
    "check_processed"
)

builder.add_conditional_edges(
    "check_processed",
    route_meeting,
    {
        "already_processed": "already_processed_notification",
        "new_meeting": 'save_new_meeting',
    }
)

builder.add_edge(
    'save_new_meeting',
    END
)

builder.add_edge(
    "already_processed_notification",
    END
)

validation_graph = builder.compile()