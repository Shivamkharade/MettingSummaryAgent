from typing import TypedDict,Optional,Literal
from langgraph.graph import StateGraph,START,END
from utils1 import (
    load_processed_meetings,
    save_processed_meetings,
    get_output_directory,
    meeting_registry_lock,
    update_meeting_status
)
from gui_manager import (
    log,
    set_step,
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
        
        case _:
            raise ValueError(
                f"Unknown meeting status: {state['status']}"
            )

def check_processed_node(state: ValidationState):
    set_step("Validating Meeting")

    log("Checking meeting history...")
    
    try:

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
            log("New meeting detected.")
            return {
                "status": "new",
                "video_path": state["video_path"],
                "meeting_hash": state["meeting_hash"],
            }

        # Meeting already exists
        log(f"Meeting already exists with status: {matching_meeting['status']}")
        return {
            "status": matching_meeting["status"],
            "video_path": matching_meeting["file_path"],
            "meeting_hash": state["meeting_hash"],
        }
    
    except Exception as e:
        raise RuntimeError(
            f"Failed to validate meeting history: {e} "
        ) from e
    
def save_new_meeting_node(state: ValidationState):
    log("Saving new meeting to registry...")
    
    try:

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
        
        log("Meeting registered successfully.")
        return {
            "status": "processing",
            "meeting_hash": state["meeting_hash"],
        }
    
    except Exception as e:
        raise RuntimeError (
            f"Failed to register new meeting: {e}"
        ) from e 

def retry_meeting_node(state: ValidationState):
    log("Retrying previously incomplete meeting...")
    
    try:
        update_meeting_status(
            state["meeting_hash"],
            "processing",
            "validation"
        )
        
        log("Meeting marked for reprocessing.")
        return {
            "status": "processing",
            "meeting_hash": state["meeting_hash"],
        }
    except Exception as e:
        raise RuntimeError(
            f"Failed to prepare meeting for retry: {e}"
        ) from e
    
def already_processed_notification_node(state: ValidationState):
    set_step("Already Processed")

    log("Meeting has already been processed.")
    
    try:

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
    except Exception as e:
        raise RuntimeError(
            f"Failed to display already processed notification: {e}"
        ) from e 
        
    set_step("Waiting...")

    log("Skipped already processed meeting.")

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