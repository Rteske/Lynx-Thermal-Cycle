import pyvisa
import time
import logging
import numpy as np

# logger = logging.getLogger().setLevel(logging.INFO)

class MXASignalAnalyzer:
    """Class for interacting with MXA lab bench signal analyzer - Max"""

    def __init__(self, adress, simulate=False, simulated_dut=None, mode='SAN'):
        self._simulate = simulate
        self._simulated_dut = simulated_dut
        self._mode = mode
        self._name = "MXA"

        if not self._simulate:
            rm = pyvisa.ResourceManager()
            self._res = rm.open_resource(adress)
            self._res.timeout = 500000
            self._res.write("*CLS")                                  #clear status
            self._res.write("*WAI")                                  #wait to continue, causes mxa to wait until all pending commands complete before executing other commands
            self._res.write("*RST")                              #resets most sig gen functions to factory defined conditions (NOTE: Sets meas  mode to single meas rather than continuous)

    def set_mode(self, mode):
        # logger.info(f"Set to {mode} mode")
        if not self._simulate:
            self._res.write(f":CONF:{mode}:NDE")
        self._mode = mode

    def set_measurement_type(self, measurement):
        # logger.info(f"set to {measurement} measurement")
        self._measure = measurement
        if not self._simulate:
            measure = self._res.query(f":READ:{measurement}?")
            while int(self._res.query("*OPC?")) != 1: #waiting for operation to complete
                pass               

    def set_center_frequency(self, frequency):
        if not self._simulate:
            self._res.write(f'FREQ:CENT {frequency}Hz')
        self._center_frequency = frequency

    def set_center_span(self, frequency):
        # logger.info(f"setting center span {MHz(frequency)}")
        if not self._simulate:
            self._res.write(f"CHP:FREQ:SPAN {frequency}Hz")
        self._span = frequency

    def set_start_stop(self, start, stop):
        self._res.write(f"SENS:FREQ:STAR {start}Hz")
        self._res.write(f"SENS:FREQ:STOP {stop}Hz")

    def auto_set_reference_level(self): #set reference level and automatically adjust attenuation
        # logger.info(f"Setting reference level automatically")
        if not self._simulate:
            self._res.write(":SENS:POW:RF:ATT:AUTO ON")

    def set_reference_level_offset(self, offset):
        # logger.info(f"Setting reference level offset {offset}")
        if not self._simulate:
            if self._mode == "SA":
                self._res.write(f":SENS:CORR:SA:RF:GAIN {-1*offset}")
            else:
                self._res.write(f":SENS:CORR:BTS:RF:GAIN {-1*offset}")

    def set_attenuation_level(self, attenuation_level):
        # logger.info(f"setting attenuation level {attenuation_level}db")
        if not self._simulate:
            self._res.write(':SENS:POW:RF:ATT:AUTO OFF')
            self._res.write(f":SENS:POW:RF:ATT {attenuation_level}")

    def get_power_measurement(self):
        # logger.info("measuring power")
        if not self._simulate:
            time.sleep(.5)
            power_resp = self._res.query(":MEAS:CHP2").split(',')
            if self._mode != 'SA':
                acp_index = [3,4,6,8,10] #Ref carrier power, lower adjacent power, upper adjacent power, lower atlernate power, upper alternate power
            else:
                acp_index = [0, 1, 2] #Ref carrier power, lower adjacent power, upper adjacent power
            power = []
            for i in acp_index:
                power.append(round(float(power_resp[i]), 2)) #convert to float and round to second decimal place
            self.power_measurement = power

        else:
            self.power_measurement = self._simulated_dut.get_power_measurement()

    def get_channel_power_data(self, center, span, points, avg):
        time.sleep(.5)
        self._res.write(":CONF:CHP")
        self._res.write(":CHP:INIT")
        resp = self._res.query(":CONF?").strip()
        if resp == "CHP":
            self._res.write(f":SENS:FREQ:CENT {center}")
            self._res.write(f":CHP:FREQ:SPAN {span}")

            center_resp = self._res.query(":SENS:FREQ:CENT?").strip()
            span_resp = self._res.query(":CHP:FREQ:SPAN?").strip()

            if float(center_resp) == center and float(span_resp) == span:
                pass
            else:
                print(center_resp, span_resp)

            self._res.write(f":CHP:SWE:POIN {points}")
            # self._res.write(":CHP:INIT:CONT 0")
            self._res.write(f":CHP:AVER:COUNT {avg}")

            time.sleep(5)

            power_resp = self._res.query("READ:CHP2?").split(',')
            center_frequency = float(self._res.query("FREQ:CENT?"))
            span = float(self._res.query("CHP:FREQ:SPAN?")) 
            print("HERE", center_frequency, span)
            start_freq = center_frequency - (span / 2)
            step = span / 401
            freq_bucket = []
            power_bucket = []

            for idx, power in enumerate(power_resp):
                freq_bucket.append(start_freq + (idx * step))
                power_bucket.append(float(power))

            self._res.write("CHP:INIT:CONT 1")
            print(len(power_bucket), len(freq_bucket))

            return freq_bucket, power_bucket

    def get_sa_bandwidth_trace(self, start, stop, resolution_bandwidth=1e+5, video_bandwidth=1e+6, points=401, avgs=100):
        self._res.write(":CONF:SAN")
        self._res.write(":SAN:INIT")
        resp = self._res.query(":CONF?").strip()
        if resp == "SAN":
            self._res.write(f":SENS:FREQ:STAR {start}Hz")
            self._res.write(f":SENS:FREQ:STOP {stop}Hz")
            self._res.write(f":BAND {resolution_bandwidth}Hz")
            self._res.write(f":BAND:VID {video_bandwidth}Hz")
            self._res.write(f":SAN:SWE:POIN {401}")
            self._res.write(f":SAN:AVER:COUNT {avgs}")
            # self._res.write(":SAN:INIT:CONT 0")
            self._res.write(":TRAC1:TYPE MAXH")

            time.sleep(5)

            trace_data = self._res.query(":READ:SAN1?").split(",")

            trace_data_bucket = []
            freqs = []
            freq = True
            for data in trace_data:
                value = float(data)
                if freq:
                    freqs.append(value)
                    freq = False
                else:
                    trace_data_bucket.append(value)
                    freq = True

            # self._res.write(":SAN:INIT:CONT 1")

            return freqs, trace_data_bucket

    def get_amplitude_offset(self):
        if self._mode != 'SA':
            offset = self._res.query(":SENS:CORR:BTS:RF:GAIN?")
        else:
            offset = self._res.query("SENS:CORR:SA:RF:GAIN?")
        return -1 * float(offset)

    def set_acp_limits(self, acp_limit):
        self._res.write(f"ACP:OFFS1:LIST:RCAR {acp_limit}, {acp_limit}, {acp_limit}, {acp_limit}, {acp_limit}, {acp_limit}")
        self._res.write(f"ACP:OFFS1:LIST:RPSD {acp_limit}, {acp_limit}, {acp_limit}, {acp_limit}, {acp_limit}, {acp_limit}")

    def get_channel_power(self):
        return float(self.power_measurement[0])

    def get_acpr(self):
        acpr_res = list()
        acpr_res.append(self.power_measurement[1])
        acpr_res.append(self.power_measurement[2])
        return np.max(acpr_res)

    def get_screen(self, directory, file_name):
        if not self._simulate:
            self._res.write(f':MMEMory:STORe:SCReen "{directory}{file_name}"')

    def set_frequency_reference(self, source):
        ### valid sources INTernal | EXTernal | SENSe | PULSe
        if not self._simulate:
            self._res.write(f":SENSe:ROSCillator:SOURce:TYPE {source}")

    def set_offset_bandwidth(self, bandwidth):
        if not self._simulate:
            self._res.write(f"ACP:OFFS:LIST:BAND {bandwidth}Hz, {bandwidth}Hz, {bandwidth}Hz, {bandwidth}Hz, {bandwidth}Hz ")

    def set_carrier_bandwidth(self, bandwidth):
        if not self._simulate:
            self._res.write(f"ACP:CARR:LIST:BAND {bandwidth}Hz")

    def set_offset_frequencies(self, bandwidth):
        if not self._simulate:
            self._res.write(f"ACP:OFFS:LIST {bandwidth}Hz, {bandwidth * 2}Hz, 0, 0, 0, 0")

    def set_resolution_bandwidth(self, resolution_bandwidth):
        if not self._simulate:
            self._res.write(f":BAND {resolution_bandwidth}Hz")
        self._resolution_bandwidth = resolution_bandwidth

    def set_video_bandwidth(self, video_bandwidth):
        if not self._simulate:
            self._res.write(f":BAND:VID {video_bandwidth}Hz")
        self._video_bandwidth = video_bandwidth
            
    def get_peak_power(self):
        #resolution bandwidth is critical for this measurement
        if not self._simulate:
            _ , current_measurement , current_resolution_bandwidth, _ , _, _ = self.get_settings() 
            self.set_measurement_type("PST")
            self._res.write("PSTatistic:COUNts 1000000")
            self.set_resolution_bandwidth(5e6)
            ccdf = self._res.query("READ:PSTatistic?").split(",") #results in the form [average power(dBm), probability at the average (in %), power level that has 10% of the power, 1% , 0.1% , 0.01%, 0.001%, 0.0001%, peak power (in dB), count]
            while int(self._res.query("*OPC?")) != 1: #waiting for operation to complete
                pass 
            peak = float(ccdf[8])

            #finished with measurement, return to previous settings
            self.set_measurement_type(current_measurement)
            self.set_resolution_bandwidth(current_resolution_bandwidth)
        else:
            peak = 0

        return peak 

    def get_harmonics(self, frequency): #This will mess up all of our settings, so we will need to restore them after
        if not self._simulate:
            current_mode, current_measure, current_resolution_bandwidth, current_video_bandwidth, current_center_freqeuncy, current_span = self.get_settings()
            if current_mode != "SA":
                self.set_mode("SA")
            harmonics = []
            self.set_measurement_type("HARM")
            time.sleep(1)
            harmonics_resp = self._res.query("MEASure:HARMonics:AMPLitude:All?").split(",") #Gives the amplitudes of the first 10 harmonics. First value is fundamental and given in dBm, all remaing values are given in dBc
            while int(self._res.query("*OPC?")) != 1: #waiting for operation to complete
                pass
            for harmonic, amplitude in enumerate(harmonics_resp):
                harmonics.append(float(harmonics_resp[harmonic]))  

            self.set_mode(current_mode)
            self.set_measurement_type(current_measure)
            self.set_resolution_bandwidth(current_resolution_bandwidth)
            self.set_video_bandwidth(current_video_bandwidth)
            self.set_center_frequency(current_center_freqeuncy)
            self.set_center_span(current_span)

            while int(self._res.query("*OPC?")) != 1: #waiting for operation to complete
                pass              
        else:
            harmonics = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        return harmonics

    def get_settings(self):
        if not self._simulate:
            self._mode = self._res.query("INST:SEL?").strip()
            self._measure = self._res.query("CONF?").strip()
            self._resolution_bandwidth = float(self._res.query(f"{self._measure}:BAND?"))
            self._video_bandwidth = float(self._res.query(f"{self._measure}:BAND:VID?"))
            self._center_frequency = float(self._res.query("FREQ:CENT?"))
            self._span = float(self._res.query(f"{self._measure}:FREQ:SPAN?"))

        return self._mode, self._measure, self._resolution_bandwidth, self._video_bandwidth, self._center_frequency, self._span 
    


    def load_saved_cal_and_state_from_register(self, register):
        self._res.write(f"*RCL {register}")
