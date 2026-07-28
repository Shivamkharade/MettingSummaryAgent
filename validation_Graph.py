from typing import TypedDict,Optional,Literal
from langgraph.graph import StateGraph,START,END
from utils1 import (
    load_processed_meetings,
    save_processed_meetings,
    get_output_directory,
    meeting_registry_lock,
    update_meeting_status
)
from win11toast import toast
from pathlib import Path

class ValidationState(TypedDict):
    video_path: str
    meeting_hash: Optional[str]
    status : Optional[Literal["new","processing","completed","failed"]]

def route_meeting(state: ValidationState):

    match state["status"]:

        case "new":
            return "new_meeting"

        case "completed":
            return "completed"

        case "failed":
            return "retry_meeting"

        case "processing":
            return "retry_meeting"

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

    # Meeting has never been seen before
    if matching_meeting is None:
        return {
            "status": "new",
            "video_path": state["video_path"],
            "meeting_hash": state["meeting_hash"],
        }

    # Meeting already exists
    return {
        "status": matching_meeting["status"],
        "video_path": matching_meeting["file_path"],
        "meeting_hash": state["meeting_hash"],
    }
    
def save_new_meeting_node(state: ValidationState):

    with meeting_registry_lock:

        meetings = load_processed_meetings()

        meetings["meetings"].append({
            "name": Path(state["video_path"]).name,
            "file_path": state["video_path"],
            "hash": state["meeting_hash"],
            "status": "new",
            "last_completed_step": None,
        })

        save_processed_meetings(meetings)
    
    update_meeting_status(
            state["meeting_hash"],
            "processing",
            "validation"
        )

    return {
        "status": "processing",
        "meeting_hash": state["meeting_hash"],
    }

def retry_meeting_node(state: ValidationState):

    update_meeting_status(
        state["meeting_hash"],
        "processing",
        "validation"
    )

    return {
        "status": "processing",
        "meeting_hash": state["meeting_hash"],
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

builder = StateGraph(ValidationState)

builder.add_node("check_processed", check_processed_node)
builder.add_node("already_processed_notification", already_processed_notification_node)
builder.add_node('save_new_meeting',save_new_meeting_node)
builder.add_node("retry_meeting", retry_meeting_node)

builder.add_edge(START, "check_processed")

builder.add_conditional_edges(
    "check_processed",
    route_meeting,
    {
        "completed": "already_processed_notification",
        "new_meeting": "save_new_meeting",
        "retry_meeting": "retry_meeting",
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

builder.add_edge(
    "retry_meeting",
    END
)

validation_graph = builder.compile()