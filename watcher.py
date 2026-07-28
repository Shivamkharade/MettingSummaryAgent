from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time
import threading

# Import your compiled LangGraph
from Metting_agent import graph
from utils1 import update_meeting_status
import hashlib

observer = None
# WATCH_FOLDER = r"C:\Users\SKharade\Projects and Learning\C_TEST_RECORDING\New folder"

class MyHandler(FileSystemEventHandler):

    def on_created(self, event):

        # Ignore folders
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Process only meeting recordings
        if file_path.suffix.lower() not in [
            ".mp4",
            ".wav",
            ".mp3",
            ".mkv",
            ".mov"
        ]:
            return

        print("=" * 60)
        print("New meeting detected")
        print(file_path)
        print("=" * 60)
        
        thread = threading.Thread(
            target=process_file,
            args=(str(file_path),),
            daemon=True
        )

        thread.start()


def generate_meeting_hash(path: str) -> str:

    sha256 = hashlib.sha256()

    with open(path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()

def process_file(path: str):

    print("=" * 60)
    print(f"Worker Thread Started:\n{path}")
    print("=" * 60)

    print("Waiting 10 seconds for the file to finish copying...")
    time.sleep(10)

    print(f"Running Meeting Agent for:\n{path}")
    
    meeting_hash = generate_meeting_hash(path)
    
    try:

        graph.invoke(
            {
                "video_path": path
            }
        )

        print(f"\nMeeting completed:\n{path}")

    except Exception as e:
        try:
            update_meeting_status(
                meeting_hash,
                "failed"
            )
        except Exception:
            pass

        print(f"\nError while processing meeting:\n{e}")


def start_watchdog(folder_path):

    global observer

    observer = Observer()

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

def stop_watchdog():

    global observer

    if observer is not None:
        observer.stop()