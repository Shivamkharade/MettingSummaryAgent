from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
import traceback
import threading
from Metting_agent import graph
from error_handler import handle_processing_error
from utils1 import (
    generate_meeting_hash,
    load_processed_meetings,
    meeting_registry_lock
)
from gui_manager import (
    log,
    set_status,
    set_meeting,
    set_step,
)

observer = None

class MyHandler(FileSystemEventHandler):
    
    last_seen = {}

    def handle_file(self, path: str):

        file_path = Path(path)

        if file_path.is_dir():
            return

        if file_path.suffix.lower() not in {
            ".mp4",
            ".wav",
            ".mp3",
            ".mkv",
            ".mov",
        }:
            return
        
        now = time.time()
        
        previous = self.last_seen.get(file_path,0)
        
        if now - previous < 10:
            return
        
        self.last_seen[file_path] = now

        print("=" * 60)
        print("Meeting detected")
        print(file_path)
        print("=" * 60)

        set_status("Processing")
        set_meeting(file_path.name)
        set_step("Preparing Meeting")

        log(f"Meeting detected: {file_path.name}")

        thread = threading.Thread(
            target=process_file,
            args=(str(file_path),),
            daemon=True,
        )
        thread.start()
    
    def on_created(self, event):

        if event.is_directory:
            return

        self.handle_file(event.src_path)
    
    def on_moved(self, event):

        if event.is_directory:
            return

        self.handle_file(event.dest_path)
    
    def on_modified(self, event):

        if event.is_directory:
            return

        self.handle_file(event.src_path)

def process_file(path: str):

    print("=" * 60)
    print(f"Worker Thread Started:\n{path}")
    print("=" * 60)

    print("Waiting 10 seconds for the file to finish copying...")
    log("Waiting for file copy to complete...")
    time.sleep(10)
    log("File copy complete.")

    print(f"Running Meeting Agent for:\n{path}")
    set_step("Running Meeting Agent")

    log("Starting Meeting Agent...")    
    
    meeting_hash = generate_meeting_hash(path)
    
    try:

        graph.invoke(
            {
                "video_path": path,
                "meeting_hash":meeting_hash
            }
        )

        print(f"\nMeeting completed:\n{path}")
        set_status("Monitoring")

        set_step("Waiting...")

        set_meeting("None")

    except Exception as e:
        try:
            handle_processing_error(
                meeting_hash=meeting_hash,
                video_path=path,
                exception=e
            )
        except Exception:
            traceback.print_exc()

def start_watchdog(folder_path):

    global observer

    observer = Observer()
    set_status("Monitoring")

    set_step("Waiting...")

    log(f"Watching folder: {folder_path}")

    observer.schedule(
        MyHandler(),
        folder_path,
        recursive=False
    )

    observer.start()

    print(f"Watching folder:\n{folder_path}")

    try:
        while observer.is_alive():
            time.sleep(1)

    finally:
        observer.stop()
        observer.join()
        print("Monitoring Stopped")
        set_status("Stopped")

        set_step("Stopped")

        set_meeting("None")

        log("Monitoring stopped.")

def stop_watchdog():

    global observer

    if observer is not None:
        observer.stop()
