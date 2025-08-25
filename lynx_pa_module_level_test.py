
import time
from instruments.power_meter import E4418BPowerMeter, GigatronixPowerMeter
from instruments.signal_generator import SynthesizedCWGenerator, E4438CSignalGenerator
from instruments.power_supply import PowerSupply
from instruments.daq import RS422_DAQ
from instruments.temp_probe import DracalTempProbe, Agilent34401A
from configs.calibration import Calibration
from instruments.temp_controller import TempController
from instruments.ztm import ZtmModular
from instruments.signal_analyzer import MXASignalAnalyzer
from instruments.network_analyzer import PNAXNetworkAnalyzer
from instruments.AIOUSB.aiousb import Aiousb
from configs.calibration import Calibration
from configs.scribe import Scribe
from configs.configs import LynxPaConfig
import datetime
import csv
import logging
import os

class RfTest:
    def __init__(self, rfpm1_input="SIM", rfpm2_output="SIM", rfsg="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", temp_controller="SIM", sno="SIM", switch_bank="SIM", na="SIM"):
        self.logger = logging.getLogger("Test")
        self.logger.setLevel(logging.DEBUG)
        
        self.sno = sno
        self.name = ""

class SignalAnalyzerTest(RfTest):
    def __init__(self, rfpm2_input="SIM", rfpm1_output="SIM" , rfsa="SIM", rfsg="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", sno="SIM", switch_bank="SIM", config="SIM"):
        if isinstance(rfpm2_input, E4418BPowerMeter):
            self.rfpm2_input = rfpm2_input
            # self.logger.debug("Succesfully connected to rfpm1 (E4418BPowerMeter)")
        else:
            raise TypeError()
        
        if isinstance(rfpm1_output, E4418BPowerMeter):
            self.rfpm1_output = rfpm1_output
            # self.logger.debug("Succesfully connected to rfpm2 (E4418BPowerMeter)")
        else:
            raise TypeError()
        
        if isinstance(psu, PowerSupply):
            self.psu = psu
        else:
            raise TypeError()
        
        if isinstance(rfsa, MXASignalAnalyzer):
            self.rfsa = rfsa
        else:
            raise TypeError()

        if isinstance(rfsg, E4438CSignalGenerator):
            self.rfsg = rfsg
            # self.logger.debug("Successfully connected to rfsg (SynthesizedCWGenerator)")
        else:
            raise TypeError()
        

        if isinstance(daq, RS422_DAQ) or isinstance(daq, Aiousb):
            self.daq = daq
        else:
            raise TypeError
        
        if isinstance(temp_probe, Agilent34401A):
            self.temp_probe = temp_probe
        else:
            raise TypeError
        
        if isinstance(temp_probe2, Agilent34401A):
            self.temp_probe2 = temp_probe2
        else:
            raise TypeError
        
        if isinstance(switch_bank, ZtmModular):
            self.switch_bank = switch_bank
        else:
            raise TypeError

        if isinstance(config, LynxPaConfig):
            self.config = config
        else:
            raise TypeError
        
        self.sno = sno
        self.name = ""

class NetworkAnalyzerTest(RfTest):
    def __init__(self, na="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", sno="SIM", switch_bank="SIM", config="SIM"):
        if isinstance(na, PNAXNetworkAnalyzer):
            self.na = na
        else:
            raise TypeError()
        
        if isinstance(psu, PowerSupply):
            self.psu = psu
        else:
            raise TypeError()
        
        if isinstance(daq, RS422_DAQ) or isinstance(daq, Aiousb):
            self.daq = daq
        else:
            raise TypeError
        
        if isinstance(temp_probe, Agilent34401A):
            self.temp_probe = temp_probe
        else:
            raise TypeError
        
        if isinstance(temp_probe2, Agilent34401A):
            self.temp_probe2 = temp_probe2
        else:
            raise TypeError
        
        if isinstance(switch_bank, ZtmModular):
            self.switch_bank = switch_bank
        else:
            raise TypeError
        
        if isinstance(config, LynxPaConfig):
            self.config = config
        else:
            raise TypeError
        
        self.sno = sno
        self.name = ""

class BandwithPowerModuleTest(SignalAnalyzerTest):
    def __init__(self, rfpm1="SIM", rfpm2="SIM", rfsg="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", sno="SIM", switch_bank="SIM", config="SIM", rfsa="SIM"): 
        super().__init__(rfpm2_input=rfpm2, rfpm1_output=rfpm1, rfsg=rfsg, rfsa=rfsa, psu=psu, daq=daq, temp_probe=temp_probe, temp_probe2=temp_probe2, sno=sno, switch_bank=switch_bank, config=config) 

    def recover_test_state(self, switchpath, bandwidth, frequency, gain_setting, waveform, input_loss):
        self.switch_bank.set_all_switches(switchpath)
        
        rfsg_input_power = self.input_power_validation(frequency, target_power=-10, start_power=-20, input_loss=input_loss)

        self.rfsg.set_frequency(frequency=frequency)
        self.rfsg.set_amplitude(rfsg_input_power)

        self.set_up_measurement(frequency=frequency, gain_setting=gain_setting, waveform=waveform)

        if isinstance(bandwidth, list):
            self.set_freq_and_bandwidth(freq=frequency, bandwidth=bandwidth, wideband=True)
        else:
            print("SHIT")
            self.set_freq_and_bandwidth(freq=frequency, bandwidth=bandwidth)
        
    def set_freq_and_bandwidth(self, freq, bandwidth, wideband=False):
        import matplotlib.pyplot as plt

        def plot_array(freqs, trace, title="Array Plot", xlabel="Index", ylabel="Value"):
            plt.figure(figsize=(10, 5))
            plt.plot(freqs, trace)
            plt.title(title)
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        if wideband:
            frequencies, powers = self.rfsa.get_sa_bandwidth_trace(start=bandwidth[0], stop=bandwidth[1])
        else:
            frequencies, powers = self.rfsa.get_channel_power_data(center=freq, span=bandwidth, points=401, avg=100)

        plot_array(freqs=frequencies, trace=powers)

    def set_up_measurement(self, frequency, gain_setting, waveform, harmonic=False):
        print(f"Setting up measurement @ FREQ:{frequency} GAIN SETTING:{gain_setting} WAVEFORM: {waveform}")

        if waveform == "CW":
            self.rfsg.enable_modulation("OFF")
        elif waveform == "OQPSK":
            self.rfsg.select_demod_filter(waveform)
            self.rfsg.enable_modulation("ON")

        self.daq.enable_rf()
        self.daq.set_attenuation(gain_setting)

        # self.rfsa.auto_set_reference_level()

        print("Completed setting up measurement")

    def input_power_validation(self, frequency, target_power, start_power, input_loss):
        # Calibration Stage Making sure -10 is going into the unit
        self.rfpm2_input.set_frequency(frequency)
        self.rfpm1_output.set_frequency(frequency)

        rfsg_input_power = start_power
        self.rfsg.set_frequency(frequency)
        self.rfsg.set_amplitude(rfsg_input_power)
        self.rfsg.start_output()

        time.sleep(1)

        power_increments = [1, .5, .25, .1, .75]
        power_inc_index = 0

        power_delta = 10000
        power_delta_limit = .1

        output_power = self.rfpm2_input.get_power_measurement() + input_loss

        while power_delta > power_delta_limit:
            if power_delta > power_increments[power_inc_index]:
                inc = power_increments[power_inc_index]
            else:
                if power_inc_index != len(power_increments) - 1:
                    power_inc_index += 1
                    inc = power_increments[power_inc_index]
                else:
                    inc = power_increments[power_inc_index]

            if target_power - output_power < 0:
                print("Increasing power")
                rfsg_input_power -= inc
            else:
                print("Decreasing power")
                rfsg_input_power += inc

            self.rfsg.set_amplitude(rfsg_input_power)

            output_power = self.rfpm2_input.get_power_measurement() + input_loss

            power_delta = abs(target_power - output_power)  
            print(f"INPUT POWER VALIDATION (output_power: {output_power}, power_delta: {power_delta})")
            time.sleep(.2)

        print(f"INPUT POWER VALIDATION COMPLETE (output_power: {output_power}, power_delta: {power_delta})")
        return rfsg_input_power
    
    def clean_up_measurement(self):
        self.rfsg.stop()
        self.daq.disable_rf()
        self.switch_bank.reset_all_switches()

    def get_standard_bandwidth_by_frequency(self, frequency, bandwidth, waveform, gain_setting):
        print("FREQ ", frequency)
        # self.rfsa.load_saved_cal_and_state_from_register(1)
        self.set_up_measurement(frequency=frequency, waveform=waveform, gain_setting=gain_setting)

        time.sleep(5)
        frequencies, powers = self.rfsa.get_channel_power_data(center=frequency, span=bandwidth, points=401, avg=100)
        voltage, current = self.get_voltage_and_current()
        probe_temp_value, probe_temp_value2 = self.get_temp_data()
        date_string = datetime.datetime.now()
        
        standard_bucket = {
            "frequency_center":frequency,
            "freqs":frequencies,
            "powers":powers,
            "bandwidth":bandwidth,
            "waveform": waveform,
            "gain_setting":gain_setting,
            "datetime_string":date_string,
            "temp_probe1_value": probe_temp_value,
            "temp_probe2_value": probe_temp_value2,
            "voltage": voltage,
            "current": current,
        }

        return standard_bucket 
    
    def get_harmonics_by_frequency_and_switchpath(self, frequency, harmonic_start_stop, waveform, gain_setting):
        self.rfsa.set_mode("SAN")
        self.rfsa._res.write("INIT:SAN")

        time.sleep(3)

        self.set_up_measurement(frequency=frequency, waveform=waveform, gain_setting=gain_setting, harmonic=True)

        time.sleep(2)
        frequencies, powers = self.rfsa.get_sa_bandwidth_trace(start=harmonic_start_stop[0], stop=harmonic_start_stop[1])
        voltage, current = self.get_voltage_and_current()
        probe_temp_value, probe_temp_value2 = self.get_temp_data()
        date_string = datetime.datetime.now()
        harmonic_bucket = {
            "frequency_center":frequency,
            "freqs":frequencies,
            "powers":powers,
            "bandwidth":"BLAml",
            "waveform": waveform,
            "gain_setting": gain_setting,
            "datetime_string":date_string,
            "temp_probe1_value": probe_temp_value,
            "temp_probe2_value": probe_temp_value2,
            "voltage": voltage,
            "current": current
        }

        return harmonic_bucket
    
    def get_power_meter_by_frequency_and_switchpath(self, frequency, waveform, gain_setting, output_loss):
        self.set_up_measurement(frequency=frequency, waveform=waveform, gain_setting=gain_setting)
        #NEED FOR 
        time.sleep(10)


        rfpm1_output_power = self.rfpm1_output.get_power_measurement()
        print(rfpm1_output_power)

        voltage, current = self.get_voltage_and_current()
        probe_temp_value, probe_temp_value2 = self.get_temp_data()
        date_string = datetime.datetime.now()

        rfpm1_bucket = {
            "frequency_center": frequency,
            "rfpm1_output_power_calibrated": rfpm1_output_power + output_loss,
            "rfpm1_output_power_uncalibrated": rfpm1_output_power,
            "rfpm1_output_loss_@_freq": output_loss,
            "waveform":waveform,
            "gain_setting":gain_setting,
            "datetime_string":date_string,
            "temp_probe1_value": probe_temp_value,
            "temp_probe2_value": probe_temp_value2,
            "voltage": voltage,
            "current": current
        }

        return rfpm1_bucket


    def get_voltage_and_current(self):
        current = self.psu.get_current()
        voltage = self.psu.get_voltage()

        return voltage, current 
    
    def get_temp_data(self):
        probe_temp_value = self.temp_probe.measure_temp()
        print(f"Probe Temp Value: {probe_temp_value}")

        probe_temp_value2 = self.temp_probe2.measure_temp()
        print(f"Probe Temp Value 2: {probe_temp_value2}")

        return probe_temp_value, probe_temp_value2

class NetworkAnalyzerModuleTest(NetworkAnalyzerTest):
    def __init__(self, na="SIM", psu="SIM", daq="SIM", temp_probe="SIM", temp_probe2="SIM", sno="SIM", switch_bank="SIM", config="SIM"):
        super().__init__(na, psu, daq, temp_probe, temp_probe2, sno, switch_bank, config)
        self.name = "Network Analyzer Standard Test"

    def set_up_measurement(self, gain_setting, statefilepath):
        print("Setting up measurement")
        self.na.load_saved_cal_and_state(statefilepath)

        self.daq.enable_rf()
        self.daq.set_attenuation(gain_setting)
        print("Completed setting up measurement")
        time.sleep(5)

    def clean_up_measurement(self):
        self.daq.disable_rf()

    def get_ratioed_power_measurement(self, gain_setting, ratioed_power, format, statefilepath):
        gain_bucket = []
        self.set_up_measurement(gain_setting, statefilepath=statefilepath)

        if ratioed_power == "S11":
            voltage, current = self.get_voltage_and_current()
            probe_temp_value, probe_temp_value2 = self.get_temp_data()
            date_string = datetime.datetime.now()
            gain, freqs = self.na.calc_and_stream_trace(1, 1, format)
            gain_bucket = {
            "gain_setting":gain_setting,
            "freqs":freqs,
            "gain":gain,
            "datetime_string":date_string,
            "temp_probe1_value": probe_temp_value,
            "temp_probe2_value": probe_temp_value2,
            "voltage": voltage,
            "current": current
            }
            
        elif ratioed_power == "S22":
            voltage, current = self.get_voltage_and_current()
            probe_temp_value, probe_temp_value2 = self.get_temp_data()
            date_string = datetime.datetime.now()
            gain, freqs = self.na.calc_and_stream_trace(1, 1, format)

            gain_bucket = {
            "gain_setting":gain_setting,
            "freqs":freqs,
            "gain":gain,
            "datetime_string":date_string,
            "temp_probe1_value": probe_temp_value,
            "temp_probe2_value": probe_temp_value2,
            "voltage": voltage,
            "current": current
            }
        elif ratioed_power == "S21":
            voltage, current = self.get_voltage_and_current()
            probe_temp_value, probe_temp_value2 = self.get_temp_data()

            date_string = datetime.datetime.now()

            gain, freqs = self.na.calc_and_stream_trace(1, 1, format)

            gain_bucket = {
            "gain_setting":gain_setting,
            "freqs":freqs,
            "gain":gain,
            "datetime_string":date_string,
            "temp_probe1_value": probe_temp_value,
            "temp_probe2_value": probe_temp_value2,
            "voltage": voltage,
            "current": current
            }

        return gain_bucket

    def recover_test_state(self, switchpath, gain_setting, statefile_path):
        self.switch_bank.set_all_switches(switchpath)
        self.set_up_measurement(gain_setting=gain_setting, statefilepath=statefile_path)
    
    def get_voltage_and_current(self):
        current = self.psu.get_current()
        voltage = self.psu.get_voltage()

        return voltage, current 
    
    def get_temp_data(self):
        probe_temp_value = self.temp_probe.measure_temp()
        print(f"Probe Temp Value: {probe_temp_value}")

        probe_temp_value2 = self.temp_probe2.measure_temp()
        print(f"Probe Temp Value 2: {probe_temp_value2}")

        return probe_temp_value, probe_temp_value2