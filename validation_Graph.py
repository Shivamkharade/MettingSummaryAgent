from typing import TypedDict,Optional
from langgraph.graph import StateGraph,START,END
from utils import (
    load_processed_meetings,
    save_processed_meetings,
    get_output_directory
)
from win11toast import toast
import hashlib
from pathlib import Path


class ValidationState(TypedDict):
    video_path: str
    
    meeting_hash: Optional[str]
    already_processed: Optional[bool]

def route_meeting(state):
    if state["already_processed"]:
        return "skip"

    return "process"

def generate_hash_node(file_path: str, chunk_size: int = 1024 * 1024) -> str:

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(chunk_size):
            sha256.update(chunk)
    
    hash = sha256.hexdigest()
    
    return {
        'meeting_hash' : hash
    }

def check_processed_node(state: ValidationState):
    meetings = load_processed_meetings()

    already_processed = any(
        meeting["hash"] == state["meeting_hash"]
        for meeting in meetings["meetings"]
    )

    return {
        "already_processed": already_processed
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

    return {}
    
def route_meeting(state):
    if state["already_processed"]:
        return "already_processed"

    return "new_meeting"

builder = StateGraph(ValidationState)

builder.add_node("generate_hash", generate_hash_node)
builder.add_node("check_processed", check_processed_node)
builder.add_node("already_processed_notification", already_processed_notification_node)

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
        "new_meeting": END,
    }
)

builder.add_edge(
    "already_processed_notification",
    END
)

validation_graph = builder.compile()