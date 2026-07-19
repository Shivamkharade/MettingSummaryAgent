from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import time

# Import your compiled LangGraph
from Metting_agent import graph

WATCH_FOLDER = r"C:\Users\SKharade\Projects and Learning\C_TEST_RECORDING\New folder"

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


observer = Observer()
observer.schedule(MyHandler(), WATCH_FOLDER, recursive=False)
observer.start()

print(f"Watching folder:\n{WATCH_FOLDER}")

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    observer.stop()

observer.join()