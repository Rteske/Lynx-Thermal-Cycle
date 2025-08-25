class Sequencer:
    def __init__(self):
        self.operations_complete = 0
        self.operations = []

class Operation:
    def __init__(self, name, target_temp, time_period, on_off_params):
        self.name = name
        self.target_recording_temp = target_temp
        self.time_recording_period = time_period
        self.on_off_params = on_off_params
        self.complete = False
        self.running = False
        