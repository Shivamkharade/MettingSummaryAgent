from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time

# Import your compiled LangGraph
from Metting_agent import graph

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
        
        print("Waiting 10 seconds for the file to finish copying...")
        time.sleep(10)

        process_file(str(file_path))


def process_file(path: str):

    print(f"Running Meeting Agent for:\n{path}")

    try:

        result = graph.invoke(
            {
                "video_path": path
            }
        )

        print("\nMeeting processing completed successfully.")

    except Exception as e:
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