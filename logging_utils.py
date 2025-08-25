import logging
import datetime
import queue

# Create a global queue for log messages
log_queue = queue.Queue()
gui_handler = None  # Global reference to GUI handler

def configure_logging(serial_number):
    global gui_handler
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"test_log_{serial_number}_{timestamp}.log"
    logging.basicConfig(filename=log_filename, level=logging.INFO, format="%(asctime)s - %(message)s")

    if gui_handler:
        logging.getLogger().addHandler(gui_handler)  # Ensure GUI logging updates with new logs

def log_message(message):
    """Log message globally and send to the queue for GUI updates."""
    print(message)
    logging.info(message)
    log_queue.put(message)  # Add message to the queue for GUI processing
