from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

WATCH_FOLDER = r"C:\\Users\\SKharade\\Projects and Learning\\C_TEST_RECORDING"

class MyHandler(FileSystemEventHandler):

    def on_created(self, event):

        if event.is_directory:
            return

        print("New file:", event.src_path)

        # Trigger your LangGraph
        process_file(event.src_path)


def process_file(path):
    print("Running LangGraph for:", path)

    # graph.invoke(...)
    # pass file path to your graph


observer = Observer()
observer.schedule(MyHandler(), WATCH_FOLDER, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    observer.stop()

observer.join()