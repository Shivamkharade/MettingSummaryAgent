import traceback
from pathlib import Path
from datetime import datetime
from utils1 import (
    update_meeting_status,
    get_output_directory
)
from gui_manager import (
    log,
    set_status,
    set_step,
    set_meeting,
)

def save_error_log(
    video_path: str,
    error_trace: str,
):
    """
    Saves the complete traceback to error.log
    inside the meeting's output folder.
    """

    output_folder = get_output_directory(video_path)

    restore_folder = output_folder / "restore"

    restore_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    error_log = restore_folder / "error.log"

    with open(error_log, "a", encoding="utf-8") as file:
        file.write("=" * 80 + "\n")
        file.write(f"Time: {datetime.now()}\n")
        file.write(f"Meeting: {Path(video_path).name}\n\n")
        file.write(error_trace)
        file.write("\n\n")

def handle_processing_error(
    exception: Exception,
    meeting_hash: str | None,
    video_path: str,
):
    """
    Handles any exception that occurs while
    processing a meeting.
    """

    error_trace = traceback.format_exc()

    print(error_trace)

    # Save full traceback
    try:
        save_error_log(
            video_path,
            error_trace,
        )
    except Exception:
        print("Failed to save error.log")

    # Update registry
    if meeting_hash:
        try:
            update_meeting_status(
                meeting_hash,
                "failed",
            )
        except Exception:
            pass

    # Reset GUI
    set_status("Monitoring")
    set_step("Error")
    set_meeting("None")

    # GUI log
    log(f"Meeting processing failed: {exception}")