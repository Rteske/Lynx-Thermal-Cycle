import pyvisa
from lynx_pa_module_level_test import BandwithPowerModuleTest, NetworkAnalyzerModuleTest
from instruments.network_analyzer import PNAXNetworkAnalyzer
from instruments.power_meter import E4418BPowerMeter
from instruments.power_supply import PowerSupply
from instruments.signal_generator import E4438CSignalGenerator
from instruments.temp_probe import Agilent34401A
from instruments.signal_analyzer import MXASignalAnalyzer
from instruments.ztm import ZtmModular  
from instruments.AIOUSB.aiousb import Aiousb
from configs.scribe import Scribe
from mocked_test_class import MockedTest
from logging_utils import log_message, configure_logging, log_queue
# from logging_utils import log_message, configure_logging
import logging
import time

logger = logging.getLogger()

class PaModuleTestManager:
    def __init__(self, sim) -> None:
        self.instruments_connection = {"rfpm1_input": True, "rfpm2_output": True, "rfsg": True, "rfsa": True, "na": True, "temp_probe": True, "daq": True}
        if not sim:
            self.rm = pyvisa.ResourceManager()
            self.instruments = self.rm.list_resources()
            log_message(self.instruments)
            self.running_state = False
            self.state = False


            
            try:
                self.rfpm1 = E4418BPowerMeter("GPIB0::14::INSTR", name="rfpm1")
                log_message("POWER METER 1 OUtSPUT CONNECTED")
            except:
                self.instruments_connection["rfpm1"] = False

            try:
                self.rfpm2 = E4418BPowerMeter("GPIB0::16::INSTR", name="rfpm2")
                log_message("POWER METER 2 input CONNECTED")
            except: 
                self.instruments_connection["rfpm2"] = False


            try:
                self.rfsg = E4438CSignalGenerator("GPIB0::30::INSTR")
                log_message("RFSg CONNECTED")
            except Exception as e:
                log_message(e)
                log_message("RFSg NOT CONNECTED")
                self.instruments_connection["rfsg"] = False

            try:
                self.rfsa = MXASignalAnalyzer("TCPIP0::K-N90X0A-000005.local::hislip0::INSTR")
                log_message("RFSa CONNECTED")
            except Exception as e:
                log_message(e)
                self.instruments_connection["rfsa"] = False
                log_message("RFSa NOt CONNECTED")

            try:
                self.na = PNAXNetworkAnalyzer("TCPIP0::K-Instr0000.local::hislip0::INSTR")
                log_message("NA CONNECTED")
            except:
                self.instruments_connection["na"] = False
                log_message("NA NOT connected")

            try:

                self.temp_probe = Agilent34401A("GPIB0::29::INSTR")
                log_message("TEMP PROBE 1 CONNECTED")
            except:
                log_message("Failed to connect to temp probe")
                self.instruments_connection["temp_probe"] = False

            try:
                self.temp_probe2 = Agilent34401A("GPIB0::22::INSTR")
            except:
                log_message("Failed to connect to temp probe 2")
                log_message("TEMP PROBE 2 CONNECTED")
                self.instruments_connection["temp_probe2"] = False

            try:
                self.power_supply = PowerSupply(visa_address="GPIB0::6::INSTR")
            except:
                self.instruments_connection["power_supply"] = False

            try:
                self.daq = Aiousb()
            except:
                log_message("FAILED TO CONNECT TO AIOUSB")
                self.instruments_connection["daq"] = False

            try:
                self.switch_bank = ZtmModular()
                self.switch_bank.init_resource("02402230028")
                self.switch_bank.reset_all_switches()
            except Exception as e:
                log_message(e)
                log_message("Failed to connect to switch bank")
                self.instruments_connection["switch_bank"] = False

            from configs.configs import LynxPaConfig

            self.lynx_config = LynxPaConfig("LYNX_PA")

            self.sig_a_test = BandwithPowerModuleTest(rfpm1=self.rfpm1, rfpm2=self.rfpm2, rfsa=self.rfsa, rfsg=self.rfsg, temp_probe=self.temp_probe, temp_probe2=self.temp_probe2, daq=self.daq, psu=self.power_supply, config=self.lynx_config, switch_bank=self.switch_bank)

            self.freqs_and_switchpaths_siga_tests = {}

            self.na_test = NetworkAnalyzerModuleTest(na=self.na, temp_probe=self.temp_probe, temp_probe2=self.temp_probe2, daq=self.daq, psu=self.power_supply, config=self.lynx_config, switch_bank=self.switch_bank)

            self.freqs_and_switchpaths_na_tests = {}

            self.paths = [
            "HIGH_BAND_PATH1 (Vertical)",
            "HIGH_BAND_PATH2 (Vertical)",
            "HIGH_BAND_PATH3 (Vertical)",
            "LOW_BAND_PATH1 (Vertical)",
            "LOW_BAND_PATH2 (Vertical)",
            "LOW_BAND_PATH3 (Vertical)",
            "HIGH_BAND_PATH1 (Horizontal)",
            "HIGH_BAND_PATH2 (Horizontal)",
            "HIGH_BAND_PATH3 (Horizontal)",
            "LOW_BAND_PATH1 (Horizontal)",
            "LOW_BAND_PATH2 (Horizontal)",
            "LOW_BAND_PATH3 (Horizontal)"
            ]

            self.scribe = Scribe("LYNX_PA")

    def process_and_write_module_na_data(self, gain_bucket, phase_bucket, switchpath, ratioed_power):
        freqs = gain_bucket[0]["freqs"]

        headers = [
            "attenuation_setting",
            "datetime_string",
            "temp_probe",
            "temp_probe2",
            "voltage",
            "current"
            ] + freqs

        self.scribe.write_na_module_data(switchpath, ratioed_power, "MLOG", headers)
        self.scribe.write_na_module_data(switchpath, ratioed_power, "PHASE", headers)

        for gain_data in gain_bucket:
            freqs = gain_data["freqs"]
            gain = gain_data["gain"]
            gain_setting = gain_data["gain_setting"]
            datetime_string = gain_data["datetime_string"]
            temp_probe = gain_data["temp_probe1_value"]
            temp_probe2 = gain_data["temp_probe2_value"]
            voltage = gain_data["voltage"]
            current = gain_data["current"]
            
            frame = [
                gain_setting,
                datetime_string,
                temp_probe,
                temp_probe2,
                voltage,
                current
                ] + gain

            self.scribe.write_na_module_data(switchpath, ratioed_power, "MLOG", frame)

        for phase_data in phase_bucket:
            freqs = phase_data["freqs"]
            phase = phase_data["phase"]
            gain_setting = phase_data["gain_setting"]
            datetime_string = phase_data["datetime_string"]
            temp_probe = phase_data["temp_probe1_value"]
            temp_probe2 = phase_data["temp_probe2_value"]
            voltage = phase_data["voltage"]
            current = phase_data["current"]

            frame = [
                gain_setting,
                datetime_string,
                temp_probe,
                temp_probe2,
                voltage,
                current
            ] + phase

            self.scribe.write_na_module_data(switchpath, ratioed_power, "PHASE", frame)
    
    def process_and_write_module_power_meter_tests(self, power_meter_bucket, results_filepath):
        freq = power_meter_bucket["frequency_center"]
        calibrated_power = power_meter_bucket["rfpm1_output_power_calibrated"]
        uncalibrated_power = power_meter_bucket["rfpm1_output_power_uncalibrated"]
        output_loss = power_meter_bucket["rfpm1_output_loss_@_freq"]
        waveform = power_meter_bucket["waveform"]
        datetime_string = power_meter_bucket["datetime_string"]
        temp_probe = power_meter_bucket["temp_probe1_value"]
        temp_probe2 = power_meter_bucket["temp_probe2_value"]
        voltage = power_meter_bucket["voltage"]
        current = power_meter_bucket["current"]
        gain_setting = power_meter_bucket["gain_setting"]

        headers = [
            "freq",
            "attenuation_setting",
            "waveform",
            "calibrated_power",
            "uncalibrated_power",
            "output_loss",
            "datetime",
            "temp_probe",
            "temp_probe2",
            "voltage",
            "current"
        ]

        self.scribe.write_data_from_filepath(results_filepath, headers)

        frame = [
            freq,
            gain_setting,
            waveform,
            calibrated_power,
            uncalibrated_power,
            output_loss,
            datetime_string,
            temp_probe,
            temp_probe2,
            voltage,
            current
        ]
        self.scribe.write_data_from_filepath(results_filepath, frame)


    def process_and_write_module_standard_bandwidth_tests(self, standard_bucket, results_filepath):
        freq = standard_bucket["frequency_center"]
        freqs = standard_bucket["freqs"]
        powers = standard_bucket["powers"]
        bandwidth = standard_bucket["bandwidth"]
        gain_setting = standard_bucket["gain_setting"]
        waveform = standard_bucket["waveform"]
        datetime_string = standard_bucket["datetime_string"]
        temp_probe = standard_bucket["temp_probe1_value"]
        temp_probe2 = standard_bucket["temp_probe2_value"]
        voltage = standard_bucket["voltage"]
        current = standard_bucket["current"]

        headers_frame = [
        "freq",
        "attenuation_setting",
        "waveform",
        "bandwidth",
        "datetime_string",
        "temp_probe",
        "temp_probe2",
        "voltage",
        "current", 
        ] + freqs

        frame = [
            freq,
            gain_setting,
            waveform,
            bandwidth,
            datetime_string,
            temp_probe,
            temp_probe2,
            voltage,
            current
            ] + powers
        
        self.scribe.write_data_from_filepath(results_filepath, headers_frame)
        self.scribe.write_data_from_filepath(results_filepath, frame)

    def process_and_write_module_harmonic_tests(self, harmonic_bucket, results_filepath):
        freq = harmonic_bucket["frequency_center"]
        freqs = harmonic_bucket["freqs"]
        gain_setting = harmonic_bucket["gain_setting"]
        powers = harmonic_bucket["powers"]
        bandwidth = harmonic_bucket["bandwidth"]
        waveform = harmonic_bucket["waveform"]
        datetime_string = harmonic_bucket["datetime_string"]
        temp_probe = harmonic_bucket["temp_probe1_value"]
        temp_probe2 = harmonic_bucket["temp_probe2_value"]
        voltage = harmonic_bucket["voltage"]
        current = harmonic_bucket["current"]

        headers_frame = [
        "freq",
        "attenuation_setting",
        "waveform",
        "bandwidth",
        "datetime_string",
        "temp_probe",
        "temp_probe2",
        "voltage",
        "current", 
        ] + freqs
        frame = [
                freq,
                gain_setting,
                waveform,
                bandwidth,
                datetime_string,
                temp_probe,
                temp_probe2,
                voltage,
                current
                ] + powers
        
        self.scribe.write_data_from_filepath(results_filepath, headers_frame)
        self.scribe.write_data_from_filepath(results_filepath, frame)

    def process_and_write_module_S_param(self, bucket, filepath, headers=False):
        freqs = bucket["freqs"]
        try:
            trace_data = bucket["gain"]
        except:
            trace_data = bucket["phase"]

        gain_setting = bucket["gain_setting"]
        datetime_string = bucket["datetime_string"]
        temp_probe = bucket["temp_probe1_value"]
        temp_probe2 = bucket["temp_probe2_value"]
        voltage = bucket["voltage"]
        current = bucket["current"]

        if headers:
            headers = [
                "attenuation_setting",
                "datetime_string",
                "temp_probe1_value",
                "temp_probe2_value",
                "voltage",
                "current"
            ] + freqs

            self.scribe.write_data_from_filepath(filepath=filepath, data=headers)

        frame = [
        gain_setting,
        datetime_string,
        temp_probe,
        temp_probe2,
        voltage,
        current
        ] + trace_data

        self.scribe.write_data_from_filepath(filepath=filepath, data=frame)
        

    def clean_up(self):
        self.daq.disable_rf()
        self.rfsg.stop()
        # self.power_supply.get_output_state(False)
        self.switch_bank.reset_all_switches()

    def run_state_process(self, path, gain_setting, measurement_type, options={}):
        switchpath = self.lynx_config.paths[path][measurement_type]["switchpath"]
        if measurement_type == "Signal Analyzer Bandwidth":
            bandwidth = options["bandwidth"]
            if bandwidth == "harmonic":
                bandwidth = self.lynx_config.paths[path][measurement_type]["harmonic_start_stop"]
            elif bandwidth == "wideband":
                bandwidth = self.lynx_config.paths[path][measurement_type]["wideband_start_stop"]
            else:
                bandwidth = float(bandwidth) * 1e+6

            frequency = options["frequency"]
            waveform = options["waveform"]
            input_loss = self.lynx_config.get_input_loss_by_path_and_freq(path=path, freq=frequency)
            self.sig_a_test.recover_test_state(switchpath=switchpath, bandwidth=bandwidth, frequency=frequency, gain_setting=gain_setting,waveform=waveform, input_loss=input_loss)
        else:
            statefile_path = self.lynx_config.paths[path][measurement_type]["state_filepath"]
            self.na_test.recover_test_state(switchpath, gain_setting, statefile_path=statefile_path)

    def run_and_process_tests(self, path, sno, sig_a_tests=False, na_tests=True):
        if sig_a_tests:
            # Run SIG A tests
            switchpath = self.lynx_config.paths[path]["Signal Analyzer Bandwidth"]["switchpath"]
            freqs = self.lynx_config.paths[path]["Signal Analyzer Bandwidth"]["freqs"]
            attenuation_settings = self.lynx_config.paths[path]["Signal Analyzer Bandwidth"]["attenuation_settings"]
            bandwidths = self.lynx_config.paths[path]["Signal Analyzer Bandwidth"]["bandwidths"]
            waveforms = self.lynx_config.paths[path]["Signal Analyzer Bandwidth"]["waveforms"]
            harmonic_start_stop = self.lynx_config.paths[path]["Signal Analyzer Bandwidth"]["harmonic_start_stop"]
            wideband_start_stop = self.lynx_config.paths[path]["Signal Analyzer Bandwidth"]["wideband_start_stop"]
            harmonic_results_filepath = self.lynx_config.paths[path]["Signal Analyzer Bandwidth"]["harmonic_results_filepath"]
            standard_results_filepath = self.lynx_config.paths[path]["Signal Analyzer Bandwidth"]["standard_results_filepath"]
            power_meter_filepath = self.lynx_config.paths[path]["Signal Analyzer Bandwidth"]["power_meter_filepath"]
            wideband_results_filepath = self.lynx_config.paths[path]["Signal Analyzer Bandwidth"]["wideband_results_filepath"]


            self.switch_bank.set_all_switches(switchpath)

            for frequency in freqs:
                output_loss = self.sig_a_test.config.get_output_loss_by_path_and_freq(path, freq=frequency)
                input_loss = self.sig_a_test.config.get_input_loss_by_path_and_freq(path, freq=frequency)

                rfsg_input_power = self.sig_a_test.input_power_validation(frequency, target_power=-10, start_power=-20, input_loss=input_loss)

                self.rfsg.set_frequency(frequency=frequency)
                self.rfsg.set_amplitude(rfsg_input_power)

                for attenuation_setting in attenuation_settings:
                    for bandwidth in bandwidths:
                        waveform = "OQPSK"
                        standard_bucket = self.sig_a_test.get_standard_bandwidth_by_frequency(
                            frequency=frequency,
                            bandwidth=bandwidth,
                            gain_setting=attenuation_setting,
                            waveform=waveform
                        )

                        self.process_and_write_module_standard_bandwidth_tests(standard_bucket, standard_results_filepath)
                    
                    for waveform in waveforms:

                        if frequency in [1.95E+9, 3E+9, 4E+9, 10E+9, 12.5E+9, 15E+9]:
                            harmonic_bucket = self.sig_a_test.get_harmonics_by_frequency_and_switchpath(
                                frequency=frequency,
                                harmonic_start_stop=harmonic_start_stop,
                                waveform=waveform,
                                gain_setting=attenuation_setting,
                            )
                            self.process_and_write_module_harmonic_tests(harmonic_bucket, harmonic_results_filepath)

                        wideband_bucket = self.sig_a_test.get_harmonics_by_frequency_and_switchpath(
                            frequency=frequency,
                            harmonic_start_stop=wideband_start_stop,
                            waveform=waveform,
                            gain_setting=attenuation_setting
                        )
                        self.process_and_write_module_harmonic_tests(wideband_bucket, wideband_results_filepath)

                        power_meter_bucket = self.sig_a_test.get_power_meter_by_frequency_and_switchpath(
                            frequency=frequency,
                            waveform=waveform,
                            gain_setting=attenuation_setting,
                            output_loss=output_loss,
                        )
                        self.process_and_write_module_power_meter_tests(power_meter_bucket, power_meter_filepath)

                self.rfsg.stop()
                noise_bucket = self.sig_a_test.get_harmonics_by_frequency_and_switchpath(
                    frequency=frequency,
                    harmonic_start_stop=wideband_start_stop,
                    waveform="CW",
                    gain_setting=attenuation_setting,
                )
                self.process_and_write_module_harmonic_tests(noise_bucket, wideband_results_filepath)

        if na_tests:
            # 31 Steps of attenuation
            s21_gain_results_filepath = self.lynx_config.paths[path]["S21"]["gain_results_filepath"]
            s21_phase_results_filepath = self.lynx_config.paths[path]["S21"]["phase_results_filepath"]
            s21_statefilepath = self.lynx_config.paths[path]["S21"]["state_filepath"]
            s21_switchpath = self.lynx_config.paths[path]["S21"]["switchpath"]
            attenuation_settings = range(0, 32, 1)
            self.switch_bank.set_all_switches(s21_switchpath)
            for attenuation_setting in attenuation_settings:

                gain = self.na_test.get_ratioed_power_measurement(gain_setting=attenuation_setting, ratioed_power="S21", format="MLOG", statefilepath=s21_statefilepath)
                phase = self.na_test.get_ratioed_power_measurement(gain_setting=attenuation_setting, ratioed_power="S21", format="PHASE", statefilepath=s21_statefilepath)

                if attenuation_setting == 0:
                    headers = True
                else:
                    headers = False 

                self.process_and_write_module_S_param(filepath=s21_gain_results_filepath, bucket=gain, headers=headers)
                self.process_and_write_module_S_param(filepath=s21_phase_results_filepath, bucket=phase, headers=headers)



            s11_state_filepath = self.lynx_config.paths[path]["S11"]["state_filepath"]
            s11_results_filepath = self.lynx_config.paths[path]["S11"]["results_filepath"]
            s11_switchpath = self.lynx_config.paths[path]["S11"]["switchpath"]
            self.switch_bank.set_all_switches(s11_switchpath)
            gain = self.na_test.get_ratioed_power_measurement(gain_setting=attenuation_setting, ratioed_power="S11", format="MLOG", statefilepath=s11_state_filepath)
            self.process_and_write_module_S_param(filepath=s11_results_filepath, bucket=gain, headers=True)


            s22_state_filepath = self.lynx_config.paths[path]["S22"]["state_filepath"]
            s22_results_filepath = self.lynx_config.paths[path]["S22"]["results_filepath"]
            s22_switchpath = self.lynx_config.paths[path]["S22"]["switchpath"]
            self.switch_bank.set_all_switches(s22_switchpath)
            gain = self.na_test.get_ratioed_power_measurement(gain_setting=attenuation_setting, ratioed_power="S22", format="MLOG", statefilepath=s22_state_filepath)
            self.process_and_write_module_S_param(filepath=s22_results_filepath, bucket=gain, headers=True)


        self.clean_up()

if __name__ == "__main__":
    manager = PaModuleTestManager(sim=False)

    import os 

    def query_user_for_path():
            
        for i, path in enumerate(manager.paths):
            log_message(i, " ", path)

        select = input("SELECT PATH")
        log_message(f"You have selected > {select}")
        answer = input("Are you sure? y/n")

        if answer.lower() == "y":
            return select
        else:
            os.system("cls")
            query_user_for_path()

    select = query_user_for_path()


    manager.run_and_process_tests(switchpath=manager.paths[int(select)])
