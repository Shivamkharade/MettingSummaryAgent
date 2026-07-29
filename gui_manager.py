import queue

gui_queue = queue.Queue()


def log(message):
    gui_queue.put(("log", message))


def set_status(status):
    gui_queue.put(("status", status))


def set_meeting(meeting):
    gui_queue.put(("meeting", meeting))


def set_step(step):
    gui_queue.put(("step", step))