import json
import time
import logging

class TempProfileRunner:
    def __init__(self, temp_controller, profile_path):
        self.temp_controller = temp_controller
        self.profile_path = profile_path
        self.logger = logging.getLogger(__name__)
        self.profile = self._load_profile()

    def _load_profile(self):
        with open(self.profile_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def run(self):
        self.logger.info("Starting temperature profile from %s", self.profile_path)
        for step in self.profile.get('steps', []):
            temp = step.get('temperature')
            duration = step.get('duration')
            self.logger.info("Setting temperature to %s°C for %s seconds", temp, duration)
            self.temp_controller.set_temperature(temp)
            time.sleep(duration)
        self.logger.info("Temperature profile complete.")
