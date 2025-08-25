import time
from logging_utils import log_message, configure_logging
import logging

logger = logging.getLogger()

class MockedTest:
    def __init__(self, mocked_value):
        self.mocked_value = mocked_value

    def get_mocked_value(self):
        return self.mocked_value
    
    def run_tests(self):
        time.sleep(5)
        log_message("MOCKED TEST: Running tests...")
        time.sleep(5)