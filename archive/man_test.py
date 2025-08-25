import time
from power_meter import E4418BPowerMeter, GigatronixPowerMeter
from signal_generator import SynthesizedCWGenerator
from power_supply import PowerSupply
from daq import RS422_DAQ
from temp_probe import DracalTempProbe, Agilent34401A
from calibration import Calibration
from temp_controller import TempController
from calibration import Calibration
from scribe import Scribe
import datetime
import csv
import logging
import os
import shutil


class ManTest:
    def __init__(self, rfpm1="SIM", rfpm2="SIM", rfpm3="SIM", rfsg="SIM", psu="SIM", daq="SIM", cal="SIM", sno="SIM"):
        self.logger = logging.getLogger("Test")

        if isinstance(rfpm1, E4418BPowerMeter):
            self.rfpm1 = rfpm1
            self.logger.debug("Succesfully connected to rfpm1 (E4418BPowerMeter)")
        else:
            raise TypeError()
        
        if isinstance(rfpm2, E4418BPowerMeter):
            self.rfpm2 = rfpm2
            self.logger.debug("Succesfully connected to rfpm2 (E4418BPowerMeter)")
        else:
            raise TypeError()
        
        if isinstance(rfpm3, E4418BPowerMeter):
            self.rfpm3 = rfpm3
        else:
            raise TypeError()
        
        if isinstance(psu, PowerSupply):
            self.psu = psu
        else:
            raise TypeError()

        if isinstance(rfsg, SynthesizedCWGenerator):
            self.rfsg = rfsg
            self.logger.debug("Successfully connected to rfsg (SynthesizedCWGenerator)")
        else:
            raise TypeError()
        
        if isinstance(daq, RS422_DAQ):
            self.daq = daq
            self.logger.debug("Succesfully connected to daq and DUT (ARDUINO)")
        else:
            raise TypeError
        
        # if isinstance(temp_probe, Agilent34401A):
        #     self.temp_probe = temp_probe
        # else:
        #     raise TypeError
        
        # if isinstance(temp_probe2, Agilent34401A):
        #     self.temp_probe2 = temp_probe2
        # else:
        #     raise TypeError
        
        # if isinstance(temp_controller, TempController):
        #     self.temp_controller = temp_controller
        # else:
        #     raise TypeError
        
        if isinstance(cal, Calibration):
            self.cal = cal
        else:
            raise TypeError

        dt = datetime.datetime.now()
        self.session_date_string = dt.strftime("%d_%m_%Y_%H_%M_%S")
        self.dir_name = os.getcwd()

        self.scribe = Scribe("Test")

        self.sno = sno

        self.line_count = 0

        self.current_flie_count = 1


    def make_a_copy(self):
        dt = datetime.datetime.now()
        date_string = dt.strftime("%d_%m_%Y_%H_%M_%S")

        path = self.dir_name + "\\data" + "\\accessible_data" + f"\\{self.sno}" + f"\\{self.session_date_string}" + f"\\{date_string}" + ".csv"
        if not os.path.exists(self.dir_name + "\\data" + "\\accessible_data" + f"\\{self.sno}"):
            os.mkdir(self.dir_name + "\\data" + "\\accessible_data" + f"\\{self.sno}")
            os.mkdir(self.dir_name + "\\data" + "\\accessible_data" + f"\\{self.sno}" + f"\\{self.session_date_string}")

        shutil.copy(self.data_filepath, path)

    def set_sno(self, sno):
        self.sno = sno
        self.data_filepath = self.dir_name + "\\data" + f"\\{sno}" + f"\\{self.session_date_string}" + f"\\{self.current_flie_count}" + ".csv"
        if not os.path.exists(self.dir_name + "\\data" + f"\\{sno}"):
            os.mkdir(self.dir_name + "\\data" + f"\\{sno}")
        
        os.mkdir(self.dir_name + "\\data" + f"\\{sno}" + f"\\{self.session_date_string}")

    def write2file(self, array):
        if self.line_count < 1e+6:
            with open(self.data_filepath, 'a', encoding="utf-8", newline='') as ff:
                writer = csv.writer(ff)

                if self.line_count == 0:
                    writer.writerow(["frequency", "rfpm1_dBm", "rfpm2_dBm", "psu_voltage", "psu_current", "rfpm3_dBm", "daq_rf_on_off", "daq_fault_status", "daq_bandpath", "daq_datetime", "daq_gain_value", "daq_temp_value", "temp_probe_value", "temp_probe2_value", "temp_plate_value"])
                print(array)
                writer.writerow(array)
                ff.close()

                self.line_count += 1
        else:
            self.current_flie_count += 1
            self.data_filepath = self.dir_name + "\\data" + f"\\{self.sno}" + f"\\{self.session_date_string}" + f"\\{self.current_flie_count}" + ".csv"
            with open(self.data_filepath, 'a', encoding="utf-8", newline='') as ff:
                writer = csv.writer(ff)
                writer.writerow(["frequency", "rfpm1_dBm", "rfpm2_dBm", "psu_voltage", "psu_current", "rfpm3_dBm", "daq_rf_on_off", "daq_fault_status", "daq_bandpath", "daq_datetime", "daq_gain_value", "daq_temp_value", "temp_probe_value", "temp_probe2_value", "temp_plate_value"])
                writer.writerow(array)
                ff.close()

                self.line_count = 0

    def set_up_measurement(self, frequency, temperature, bandpath, gain_setting, voltage=28, current=5):
        self.psu.set_voltage(voltage)
        self.psu.set_current(current)
        self.psu.set_output_state(True)
        print("Setting up measurement")

        self.rfpm1.set_frequency(frequency)
        self.rfpm2.set_frequency(frequency)

        self.rfpm3.set_frequency(frequency)

        horizontal, vertical = self.cal.get_input_loss_at_frequency(frequency)
        input_loss = round((horizontal + vertical) / 2, 3)
        rfsg_input_power = self.input_power_validation(frequency, target_power=-10, start_power=-30, input_loss=input_loss)

        self.rfsg.set_amplitude(rfsg_input_power)
        self.daq.enable_rf()
        self.daq.set_band(bandpath)
        self.daq.change_gain(gain_setting)
        print("Completed setting up measurement")

    def clean_up_measurement(self):
        self.daq.disable_rf()
        self.daq.set_band("NONE")
        self.rfsg.stop_output()

    def measure_and_record(self, time_total, temp_target, temp_delta=3, frequency=None, voltage=28):
        t_end = time.time() + (time_total * 60)
        while time.time() < t_end:
            horizontal, vertical = self.cal.get_input_loss_at_frequency(frequency)
            input_loss = round((horizontal + vertical) / 2, 3)
            
            errors, rfpm1_dBm, rfpm2_dBm, rfpm3_dBm, psu_current, psu_voltage = self.validate_power(frequency, max_gain=33, min_gain=29, max_current=2.1, min_current=.5, max_voltage=voltage + 1.5, min_voltage=voltage - 1.5, input_loss=input_loss, max_input=6)

            rf_on_off, fault_status, bandpath, gain_value, date_string, _ = self.daq.read_status_return()

            _, completed, probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value = self.validate_tempature(temp_target, temp_delta)
            os.system('cls')
            print("\n")
            if errors:
                print("ERRORS DETECTED")
                print(errors)
                self.write2file(errors)
                break

            frame = [frequency, rfpm1_dBm, rfpm2_dBm, psu_voltage, psu_current, rfpm3_dBm, rf_on_off, fault_status, bandpath, date_string, gain_value, dut_temp_value, probe_temp_value, probe_temp_value2, temp_plate_value]
            if completed:
                self.write2file(frame)
            else:
                self.write2file(["FAILED TEMP"])
                time_taken = self.wait_for_temp_change(temp_target, temp_delta)
                t_end += time_taken

        self.clean_up_measurement()

    def input_power_validation(self, frequency, target_power, start_power, input_loss):
        # Calibration Stage Making sure -10 is going into the unit
        rfsg_input_power = start_power
        self.rfsg.set_frequency(frequency)
        self.rfsg.set_amplitude(rfsg_input_power)
        self.rfsg.start_output()

        time.sleep(1)

        power_increments = [1, .5, .25, .1, .75]
        power_inc_index = 0

        power_delta = 10000
        power_delta_limit = .1

        output_power = self.rfpm3.get_power_measurement() + input_loss

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

            output_power = self.rfpm3.get_power_measurement() + input_loss

            power_delta = abs(target_power - output_power)  
            print(f"INPUT POWER VALIDATION (output_power: {output_power}, power_delta: {power_delta})")
            time.sleep(.2)

        print(f"INPUT POWER VALIDATION COMPLETE (output_power: {output_power}, power_delta: {power_delta})")
        return rfsg_input_power

    def validate_tempature(self, target_temp, target_temp_delta):
        probe_temp_value = self.temp_probe.measure_temp()
        print(f"Probe Temp Value: {probe_temp_value}")

        probe_temp_value2 = self.temp_probe2.measure_temp()
        print(f"Probe Temp Value 2: {probe_temp_value2}")

        _, _, _, _, _, dut_temp_value = self.daq.read_status_return()
        print(f"DUT Temp Value: {dut_temp_value}")

        temp_plate_value = self.temp_controller.query_actual(1)
        print(f"Temp Plate Value: {temp_plate_value}")

        temp_delta = abs(target_temp - float(probe_temp_value))
        print(f"Temp Delta: {temp_delta}")

        complete = float(probe_temp_value) < target_temp + target_temp_delta and float(probe_temp_value) > target_temp - target_temp_delta
        print(f"Temp Complete: {complete}")

        print(f"{target_temp} target temp, {target_temp_delta} target temp delta")

        return temp_delta, complete, probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value
    
    def wait_for_temp_change(self, target_temp, target_temp_delta=3):
        temp_delta, completed, probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value = self.validate_tempature(target_temp, target_temp_delta) 
        t_start = time.time()

        tries = 0

        temp_increments = [2, 1, .5]

        current_temp_inc_indx = 0

        while not completed:
            os.system('cls')
            print("\n")
            print("\n")
            print(f"Waiting for temperature to stabilize at {target_temp} target temp")

            if tries > 200:
                print("Temperature confirmation failed")
                self.temp_controller.set_chamber_state("OFF")

                if target_temp + target_temp_delta < float(probe_temp_value):
                    self.running_temp = self.running_temp - temp_increments[current_temp_inc_indx]
                elif target_temp - target_temp_delta > float(probe_temp_value):
                    self.running_temp = self.running_temp + temp_increments[current_temp_inc_indx]
                
                if not current_temp_inc_indx > len(temp_increments) - 1:
                    current_temp_inc_indx += 1

                self.temp_controller.set_setpoint(1, self.running_temp) 
                self.temp_controller.set_chamber_state("ON")


                print("Waiting for Correction to take place")

                time.sleep(60)


                tries = 0


            tries += 1
            rf_on_off, fault_status, bandpath, gain_value, date_string, _ = self.daq.read_status_return()
            temp_delta, completed, probe_temp_value, probe_temp_value2, dut_temp_value, temp_plate_value = self.validate_tempature(target_temp, target_temp_delta)

            frame = ["", "", "", "", "", "", rf_on_off, fault_status, bandpath, date_string, gain_value, dut_temp_value, probe_temp_value, probe_temp_value2, temp_plate_value]
            self.write2file(frame)
            
            time.sleep(3)
            if completed:
                break

        print(f"Temperature confirmation completed with {temp_delta} delta @ {target_temp} target temp")
        return time.time() - t_start
    
    def set_temp(self, timer, target_temp, target_temp_delta=3, temp_controller_offset=0):
        self.temp_controller.set_setpoint(1, target_temp + temp_controller_offset)
        self.temp_controller.set_chamber_state(True)

        elapsed_time = self.wait_for_temp_change(target_temp, target_temp_delta)
        print(f"Temperature confirmation t0ok {elapsed_time} seconds ")
        return elapsed_time

    def validate_power(self, frequency, max_input, max_gain, min_gain, max_current, min_current, max_voltage, min_voltage, input_loss):
        errors = []
        output_horizontal, output_vertical = self.cal.get_output_loss_at_frequency(frequency)
        rfpm1_dBm = self.rfpm1.get_power_measurement() - output_horizontal 
        rfpm2_dBm = self.rfpm2.get_power_measurement() - output_vertical 
        rfpm3_dBm = self.rfpm3.get_power_measurement() + input_loss

        psu_current = self.psu.get_current()
        psu_voltage = self.psu.get_voltage()

        if rfpm1_dBm < min_gain or rfpm1_dBm > max_gain:
            errors.append("rfpm1_dBm_output_range_error")

        if rfpm2_dBm < min_gain or rfpm2_dBm > max_gain:
            errors.append("rfpm2_dBm_output_range_error")

        if rfpm3_dBm > max_input:
            errors.append("rfpm3_dBm_output_range_error")

        if psu_current < min_current or psu_current > max_current:
            errors.append("psu_current_range_error")

        if psu_voltage < min_voltage or psu_voltage > max_voltage:
            errors.append("psu_voltage_range_error")

        print(errors, rfpm1_dBm, rfpm2_dBm, rfpm3_dBm, psu_current, psu_voltage)

        return errors, rfpm1_dBm, rfpm2_dBm, rfpm3_dBm, psu_current, psu_voltage