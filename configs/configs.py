import time

from configs.calibration import Calibration
import os
import datetime

class Config:
    def __init__(self, name):
        self.name = name
    
    def to_dict(self):
        print("Converting to dict")
        return self.__dict__
    
class LynxOQPSKConfig(Config):
    def __init__(self):
        super().__init__("OQPSK_CALIBRATION")
        print("Initializing OQPSK")
        self.frequencies = {
            "L": [1.95E+9, 3E+9, 4E+9],
            "M": [10E+9, 12.5E+9, 15E+9],
            "H": [25E+9, 28E+9, 31E+9]
        }

        self.gain_settings = [41]
        self.static_bandwidths = [10E+6, 200E+6]
        self.harmonic_measurement_bandwidths = {
            "L": [1E+9, 8E+9],
            "M": [5E+9, 20E+9],
            "H": [18E+9, 40E+9]
        }

        self.waveforms = ["CW", "OQPSK"]
        self.sa_save_register = "1"

        # CHANGE BACK TO 4 FOR THOSE PATHS THAT HAVE 2 @ INDX 0, 4
        self.paths = {
            "Band1_SN1": [2,1,1,2,1,1],
            "Band2_SN1": [2,2,2,2,1,1],
            "Band3_SN1": [2,3,3,2,1,1],
            "Band1_SN2": [2,4,4,2,1,1],
            "Band2_SN2": [2,5,5,2,1,1],
            "Band3_SN3": [2,6,6,2,1,1]
        }

        self.input_losses = {
            "Band1_SN1": {1.95E+9: 8.76, 3E+9: 7.76, 4E+9: 7.78},
            "Band2_SN1": {10E+9: 6.83, 12.5E+9: 5.69, 15E+9: 5.65},
            "Band3_SN1": {25E+9: 4.05, 28E+9: 4.15, 31E+9: 3.45},
            "Band1_SN2": {1.95E+9: 8.76, 3E+9: 7.76, 4E+9: 7.78},
            "Band2_SN2": {10E+9: 6.83, 12.5E+9: 5.69, 15E+9: 5.65},
            "Band3_SN3": {25E+9: 4.05, 28E+9: 4.15, 31E+9: 3.45}
        }

        self.output_losses = {
            "Band1_SN1": {1.95E+9: 21.75, 3E+9: 22.21, 4E+9: 22.52},
            "Band2_SN1": {10E+9: 23.8, 12.5E+9: 24.33, 15E+9: 24.93},
            "Band3_SN1": {25E+9: 26.52, 28E+9: 26.92, 31E+9: 27.18},
            "Band1_SN2": {1.95E+9: 21.75, 3E+9: 22.21, 4E+9: 22.52},
            "Band2_SN2": {10E+9: 23.8, 12.5E+9: 24.33, 15E+9: 24.93},
            "Band3_SN3": {25E+9: 26.52, 28E+9: 26.92, 31E+9: 27.18}
        }

    def get_input_loss_by_switchpath_and_freq(self, switchpath, freq):
        input_loss = 0
        for path, losses in self.input_losses.items():
            if switchpath == path:
                print(losses)
                input_loss = losses[freq]
                break

        return input_loss
    
    def get_output_loss_by_switchpath_and_freq(self, switchpath, freq):
        output_loss = 0
        for path, losses in self.output_losses.items():
            if switchpath == path:
                output_loss = losses[freq]
                break

        return output_loss
    
    def get_bandpath_by_frequency(self,frequency):
        for bandpath, freqs in self.frequencies.items():
            if frequency in freqs:
                return bandpath

class LynxPaConfig(Config):
    def __init__(self, project):
        super().__init__("LYNX_PA")

        self.base_dir = "D:\\Lynx\\ATE\\"

        self.test_dir = os.getcwd()
        self.data_dir_base = os.path.join(self.test_dir, f"{project}_data")
        self.data_dir_results = self.data_dir_base

        self.init_paths()

        self.output_losses = {
            "Band1_SN1": {1.95E+9: 21.06, 3E+9: 21.55, 4E+9: 21.85},
            "Band2_SN1": {10E+9: 23.51, 12.5E+9: 24.18, 15E+9: 24.69},
            "Band3_SN1": {25E+9: 21.32, 28E+9: 22.02, 31E+9: 22.72},
            "Band1_SN2": {1.95E+9: 21.12, 3E+9: 21.61, 4E+9: 21.93},
            "Band2_SN2": {10E+9: 23.48, 12.5E+9: 24.16, 15E+9: 24.67},
            "Band3_SN2": {25E+9: 21.29, 28E+9: 22.03, 31E+9: 22.75}
        }

        self.input_losses = {
            "Band1_SN1": {1.95E+9: 8.5, 3E+9: 7.6, 4E+9: 7.6},
            "Band2_SN1": {10E+9: 6.7, 12.5E+9: 5.65, 15E+9: 5.63},
            "Band3_SN1": {25E+9: 3.88, 28E+9: 3.94, 31E+9: 3.3},
            "Band1_SN2": {1.95E+9: 8.5, 3E+9: 7.65, 4E+9: 7.6},
            "Band2_SN2": {10E+9: 6.7, 12.5E+9: 5.67, 15E+9: 5.65},
            "Band3_SN2": {25E+9: 4.03, 28E+9: 4, 31E+9: 3.38}
        }


    def create_session_dir(self):
        start_timestamp = datetime.datetime.now()
        session = start_timestamp.strftime("%Y%m%d%H%M%S")
        self.data_dir_results = os.path.join(self.data_dir_results, session)

        if not os.path.exists(self.data_dir_results):
            os.mkdir(self.data_dir_results)

    def change_sno_dir(self, sno):
        self.data_dir_results = os.path.join(self.data_dir_results, sno)
        if not os.path.exists(self.data_dir_results):
            os.mkdir(self.data_dir_results)

    def change_results_dir(self, results_dir_name):
        self.data_dir_results = os.path.join(self.data_dir_results, results_dir_name)
        if not os.path.exists(self.data_dir_results):
            os.mkdir(self.data_dir_results)

    def new_sno(self, sno, results_dir_name):
        self.data_dir_results = self.data_dir_base
        self.change_sno_dir(sno)
        self.change_results_dir(results_dir_name)
        self.create_session_dir()
        self.init_paths()

    def init_paths(self):
        self.paths = {
            "Band1_SN1": {
                "S21":{
                    "switchpath": [1,1,1,1,1,1],
                    "state_filepath": os.path.join(self.base_dir, "band1_1_gain_phase.csa"),
                    "gain_results_filepath": os.path.join(self.data_dir_results, "band1_1_gain.csv"),
                    "phase_results_filepath": os.path.join(self.data_dir_results, "band1_1_phase.csv")
                },
                "S11":{
                    "switchpath": [1,1,1,1,1,1],
                    "state_filepath": os.path.join(self.base_dir, "band1_1_S11.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "band1_1_S11.csv")
                },
                "S22":{
                    "switchpath": [1,1,1,1,4,4],
                    "state_filepath": os.path.join(self.base_dir, "band1_1_S22.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "band1_1_S22.csv")

                },
                "Signal Analyzer Bandwidth": {
                    "switchpath": [2,1,1,2,1,1],
                    "register": "1",
                    "standard_results_filepath": os.path.join(self.data_dir_results, "band1_1_bandwidth.csv"),
                    "harmonic_results_filepath":  os.path.join(self.data_dir_results, "band1_1_harmonic_bandwidth.csv"),
                    "power_meter_filepath": os.path.join(self.data_dir_results, "band1_1_power_meter.csv"),
                    "wideband_results_filepath": os.path.join(self.data_dir_results, "band1_1_wideband.csv"),
                    "freqs": [1.95E+9, 3E+9, 4E+9],
                    "attenuation_settings": [0,31],
                    "bandwidths": [10E+6, 200E+6],
                    "harmonic_start_stop": [1e+9, 17e+9],
                    "wideband_start_stop": [1e+9, 8e+9],
                    "waveforms": ["CW", "OQPSK"]
                }
            },
            "Band2_SN1": {
                "S21":{
                    "switchpath": [1,2,2,1,1,1],
                    "state_filepath": os.path.join(self.base_dir, "band2_1_gain_phase.csa"),
                    "gain_results_filepath": os.path.join(self.data_dir_results, "band2_1_gain.csv"),
                    "phase_results_filepath": os.path.join(self.data_dir_results, "band2_1_phase.csv")
                },
                "S11":{
                    "switchpath": [1,2,2,1,4,4],
                    "state_filepath": os.path.join(self.base_dir, "band2_1_S11.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "band2_1_S11.csv")
                },
                "S22":{
                    "switchpath": [1,2,2,1,4,4],
                    "state_filepath": os.path.join(self.base_dir, "band2_1_S22.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "band2_1_S22.csv")
                },
                "Signal Analyzer Bandwidth": {
                    "switchpath": [2,2,2,2,1,1],
                    "register": "1",
                    "standard_results_filepath": os.path.join(self.data_dir_results, "band2_1_bandwidth.csv"),
                    "harmonic_results_filepath":  os.path.join(self.data_dir_results, "band2_1_harmonic_bandwidth.csv"),
                    "power_meter_filepath": os.path.join(self.data_dir_results, "band2_1_power_meter.csv"),
                    "wideband_results_filepath": os.path.join(self.data_dir_results, "band2_1_wideband.csv"),
                    "freqs": [10E+9, 12.5E+9, 15E+9],
                    "attenuation_settings": [0,31],
                    "bandwidths": [10E+6, 200E+6],
                    "harmonic_start_stop": [9e+9, 40e+9],
                    "wideband_start_stop": [5e+9, 20e+9],
                    "waveforms": ["CW", "OQPSK"]
                }
            },
            "Band3_SN1": {
                "S21":{
                    "switchpath": [1,3,3,1,1,1],
                    "state_filepath": os.path.join(self.base_dir, "band3_1_gain_phase.csa"),
                    "gain_results_filepath": os.path.join(self.data_dir_results, "band3_1_gain.csv"),
                    "phase_results_filepath": os.path.join(self.data_dir_results, "band3_1_phase.csv")
                },
                "S11":{
                    "switchpath": [1,3,3,1,4,4],
                    "state_filepath": os.path.join(self.base_dir, "band3_1_S11.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "band3_1_S11.csv")
                },
                "S22":{
                    "switchpath": [1,3,3,1,4,4],
                    "state_filepath": os.path.join(self.base_dir, "band3_1_S22.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "band3_1_S22.csv")
                },
                "Signal Analyzer Bandwidth": {
                    "switchpath": [2,3,3,2,1,1],
                    "register": "1",
                    "standard_results_filepath": os.path.join(self.data_dir_results, "band3_1_bandwidth.csv"),
                    "harmonic_results_filepath":  os.path.join(self.data_dir_results, "band3_1_harmonic_bandwidth.csv"),
                    "power_meter_filepath": os.path.join(self.data_dir_results, "band3_1_power_meter.csv"),
                    "wideband_results_filepath": os.path.join(self.data_dir_results, "band3_1_wideband.csv"),
                    "freqs": [25E+9, 28E+9, 31E+9],
                    "attenuation_settings": [0,31],
                    "bandwidths": [10E+6, 200E+6],
                    "harmonic_start_stop": [18e+9, 40e+9],
                    "wideband_start_stop": [18e+9, 40e+9],
                    "waveforms": ["CW", "OQPSK"]
                }
            },
            "Band1_SN2": {
                "S21":{
                    "switchpath": [1,4,4,1,1,1],
                    "state_filepath": os.path.join(self.base_dir, "band1_2_gain_phase.csa"),
                    "gain_results_filepath": os.path.join(self.data_dir_results, "band1_2_gain.csv"),
                    "phase_results_filepath": os.path.join(self.data_dir_results, "band1_2_phase.csv")
                },
                "S11":{
                    "switchpath": [1,4,4,1,4,4],
                    "state_filepath": os.path.join(self.base_dir, "band1_2_S11.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "band1_2_S11.csv")
                },
                "S22":{
                    "switchpath": [1,4,4,1,4,4],
                    "state_filepath": os.path.join(self.base_dir, "band1_2_S22.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "band1_2_S22.csv")
                },
                "Signal Analyzer Bandwidth": {
                    "switchpath": [2,4,4,2,1,1],
                    "register": "1",
                    "standard_results_filepath": os.path.join(self.data_dir_results, "band1_2_bandwidth.csv"),
                    "harmonic_results_filepath":  os.path.join(self.data_dir_results, "band1_2_harmonic_bandwidth.csv"),
                    "power_meter_filepath": os.path.join(self.data_dir_results, "band1_2_power_meter.csv"),
                    "wideband_results_filepath": os.path.join(self.data_dir_results, "band1_2_wideband.csv"),
                    "freqs": [1.95E+9, 3E+9, 4E+9],
                    "attenuation_settings": [0,31],
                    "bandwidths": [10E+6, 200E+6],
                    "harmonic_start_stop": [1e+9, 17e+9],
                    "wideband_start_stop": [1e+9, 8e+9],
                    "waveforms": ["CW", "OQPSK"]
                }
            },
            "Band2_SN2": {
                "S21":{
                    "switchpath": [1,5,5,1,1,1],
                    "state_filepath": os.path.join(self.base_dir, "band2_2_gain_phase.csa"),
                    "gain_results_filepath": os.path.join(self.data_dir_results, "band2_2_gain.csv"),
                    "phase_results_filepath": os.path.join(self.data_dir_results, "band2_2_phase.csv")
                },
                "S11":{
                    "switchpath": [1,5,5,1,4,4],
                    "state_filepath": os.path.join(self.base_dir, "band2_2_S11.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "band2_2_S11.csv")
                },
                "S22":{
                    "switchpath": [1,5,5,1,4,4],
                    "state_filepath": os.path.join(self.base_dir, "band2_2_S22.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "band2_2_S22.csv")
                },
                "Signal Analyzer Bandwidth": {
                    "switchpath": [2,5,5,2,1,1],
                    "register": "1",
                    "standard_results_filepath": os.path.join(self.data_dir_results, "band2_2_bandwidth.csv"),
                    "harmonic_results_filepath":  os.path.join(self.data_dir_results, "band2_2_harmonic_bandwidth.csv"),
                    "power_meter_filepath": os.path.join(self.data_dir_results, "band2_2_power_meter.csv"),
                    "wideband_results_filepath": os.path.join(self.data_dir_results, "band2_2_wideband.csv"),
                    "freqs": [10E+9, 12.5E+9, 15E+9],
                    "attenuation_settings": [0,31],
                    "bandwidths": [10E+6, 200E+6],
                    "harmonic_start_stop": [9e+9, 40e+9],
                    "wideband_start_stop": [5e+9, 20e+9],
                    "waveforms": ["CW", "OQPSK"]
                }
            },
            "Band3_SN2": {
                "S21":{
                    "switchpath": [1,6,6,1,1,1],
                    "state_filepath": os.path.join(self.base_dir, "band3_2_gain_phase.csa"),
                    "gain_results_filepath": os.path.join(self.data_dir_results, "band3_2_gain.csv"),
                    "phase_results_filepath": os.path.join(self.data_dir_results, "band3_2_phase.csv")
                },
                "S11":{
                    "switchpath": [1,6,6,1,4,4],
                    "state_filepath": os.path.join(self.base_dir, "band3_2_S11.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "band3_2_S11.csv")
                },
                "S22":{
                    "switchpath": [1,6,6,1,4,4],
                    "state_filepath": os.path.join(self.base_dir, "band3_2_S22.csa"),
                    "results_filepath": os.path.join(self.data_dir_results, "band3_2_S22.csv")
                },
                "Signal Analyzer Bandwidth": {
                    "switchpath": [2,6,6,2,1,1],
                    "register": "1",
                    "standard_results_filepath": os.path.join(self.data_dir_results, "band3_2_bandwidth.csv"),
                    "harmonic_results_filepath":  os.path.join(self.data_dir_results, "band3_2_harmonic_bandwidth.csv"),
                    "power_meter_filepath": os.path.join(self.data_dir_results, "band3_2_power_meter.csv"),
                    "wideband_results_filepath": os.path.join(self.data_dir_results, "band3_2_wideband.csv"),
                    "freqs": [25E+9, 28E+9, 31E+9],
                    "attenuation_settings": [0,31],
                    "bandwidths": [10E+6, 200E+6],
                    "harmonic_start_stop": [18e+9, 20e+9],
                    "wideband_start_stop": [18e+9, 40e+9],
                    "waveforms": ["CW", "OQPSK"]
                }
            }
        }

    def get_output_loss_by_path_and_freq(self, path, freq):
        output_loss = 0
        for bandpath, losses in self.output_losses.items():
            if path == bandpath:
                output_loss = losses[freq]
                break

        return output_loss

    def get_input_loss_by_path_and_freq(self, path, freq):
        input_loss = 0
        for bandpath, losses in self.input_losses.items():
            if path == bandpath:
                input_loss = losses[freq]
                break

        return input_loss

    def get_bandpath_by_path(self, path):
        if "Band1" in path:
            return "L"
        elif "Band2" in path:
            return "M"
        elif "Band3" in path:
            return "H"

class Results:
    def __init__(self, name):
        self.name = None
        self.frequencies = []

    def to_dict(self):
        return self.__dict__
    
class PNAXResults(Results):
    def __init__(self):
        super().__init__("PNAX_Result")
        self.paths = {}

class OQPSKResults(Results):
    def __init__(self):
        super().__init__("OQPSK_Result")
        self.paths = {}