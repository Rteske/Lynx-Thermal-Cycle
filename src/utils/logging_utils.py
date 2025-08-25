import logging
import datetime
import queue
import os

# Create a global queue for log messages
log_queue = queue.Queue()
gui_handler = None  # Global reference to GUI handler

def configure_logging(serial_number, base_dir: str | None = None):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    root = base_dir or os.getcwd()
    logs_dir = os.path.join(root, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_filepath = os.path.join(logs_dir, f"test_log_{serial_number}_{timestamp}.log")
    logging.basicConfig(filename=log_filepath, level=logging.INFO, format="%(asctime)s - %(message)s")
    # Also log to console for CLI visibility
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logging.getLogger().addHandler(console)

    if gui_handler is not None:
        logging.getLogger().addHandler(gui_handler)  # Ensure GUI logging updates with new logs

def log_message(message):
    """Log message globally and send to the queue for GUI updates."""
    print(message)
    logging.info(message)
    log_queue.put(message)  # Add message to the queue for GUI processing
