import traceback

from gui_manager import (
    log,
    set_status,
    set_step,
    set_meeting,
)

from utils1 import update_meeting_status

def handle_processing_error(
    exception: Exception,
    meeting_hash: str | None,
    video_path: str,
):
    error_trace = traceback.format_exc()

    print(error_trace)

    if meeting_hash:
        try:
            update_meeting_status(
                meeting_hash,
                "failed",
            )
        except Exception:
            pass

    set_status("Monitoring")
    set_step("Error")
    set_meeting("None")

    log(f"Meeting processing failed: {exception}")

