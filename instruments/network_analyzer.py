# rm = pyvisa.ResourceManager()
# list = rm.list_resources()

# pna_x = rm.open_resource("GPIB0::6::INSTR")
# pna_x.write(")
# print(list)
import pyvisa
import time
import datetime
import csv
import logging

class PNAXNetworkAnalyzer:
    def __init__(self, address, clear=False):
        rm = pyvisa.ResourceManager()
        self._res = rm.open_resource(address)
        self._res.timeout = 2500
        if clear:
            self._res.write("*CLS")
            self._res.write("*WAI")
            self._res.write("*RST")
        self.trace_dir = "Lynx"
        print("SuCCEssfull Cionnection")

    def set_amplitude(self, port, amplitude):
        self.send_cmd(f"SOUR{port}:POW:LEV {amplitude}")
    
    def set_center_frequency_and_span(self, port, center, span):
        self.send_cmd(f"SENS{port}:FREQ:CENT {center}")
        self.send_cmd(f"SENS{port}:FREQ:SPAN {span}")

    def set_start_and_stop_frequency(self, port, start, stop):
        self.send_cmd(f"SENS{port}:FREQ:STAR {start}")
        self.send_cmd(f"SENS{port}:FREQ:STOP {stop}")

    def clear_all_traces(self): 
        self.send_cmd("CALC:PAR:DEL:ALL")

    def start_trace(self, port, trace_num, measurement_type, format):
        self.send_cmd("DISP:WIND1:STAT ON")

        self.send_cmd(f"CALC{port}:MEAS{trace_num}:DEF '{measurement_type}'")
        self.send_cmd(f"CALC{port}:FORM {format}")
        self.send_cmd(f"DISP:MEAS{trace_num}:FEED 1")


    def parse_list_of_traces(self, port):
        channel_raw = self.query_pna(f'CALC{port}:PAR:CAT?')
        channel_traces_raw = channel_raw.replace('"', '')
        channel_traces_raw = channel_traces_raw.split(',')

        traces = []

        for x in channel_traces_raw:
            if len(x) > 5:
                traces.append(x)

        return traces
    
    def convert_sci_num_str_to_float(self, array, rounding=1):
        new_arr = []
        for element in array:
            new_arr.append(round(float(element), rounding))

        return new_arr

    def calc_and_stream_trace(self, port, tracenum, format, delay=0):
        self.send_cmd(f"SENS{port}:AVER:CLE")
        self.send_cmd(f"CALC{port}:PAR:MNUM {tracenum}")
        self.send_cmd(f"CALC{port}:FORM {format}")
        self.send_cmd(f"OUTP:STAT ON")
        # Set data transfer format to ASCII
        time.sleep(delay)
        
        myTraceData = self.query_pna(f"CALC{port}:MEAS{tracenum}:DATA:FDATA?")
        frequencies = self.query_pna(f"SENS{port}:X?")

        data = myTraceData.split(",")
        frequencies = frequencies.split(",")

        data = self.convert_sci_num_str_to_float(data, 3)

        return data, frequencies
    
    def calc_and_stream_mlog_phase_trace(self, port, tracenum):
        bucket = []
        for format in ["MLOG", "PHASE"]:
            self.send_cmd(f"SENS{port}:AVER:CLE")
            self.send_cmd(f"CALC{port}:PAR:MNUM {tracenum}")
            self.send_cmd(f"CALC{port}:FORM {format}")
            # Set data transfer format to ASCII

            myTraceData = self.query_pna(f"CALC{port}:MEAS{tracenum}:DATA:FDATA?")
            frequencies = self.query_pna(f"SENS{port}:X?")

            data = myTraceData.split(",")
            frequencies = frequencies.split(",")
            bucket.append([data, frequencies])

        return bucket[0], bucket[1]
    
    def calc_and_stream_ip3(self, port, tracenum):
        self.send_cmd(f"CALC{port}:PAR:MNUM {tracenum}")
        self.send_cmd(f"CALC{port}:FORM MLOG")
        self.send_cmd(f"CALC{port}:FORM:UNIT MLOG,DBM")

        data = self.query_pna(f"CALC{port}:MEAS{tracenum}:DATA:FDATA?")
        frequencies = self.query_pna(f"SENS{port}:X?")

        return data, frequencies

    def send_cmd(self, string):
        self._res.write(string)

    def query_pna(self, string):
        response = self._res.query(string)
        return response
    
    def load_saved_cal_and_state(self, state_filepath):
        state_filepath = str(state_filepath)
        print(state_filepath)
        self.send_cmd(f"MMEM:LOAD:CSAR '{state_filepath}'")

if __name__ == "__main__":
    na = PNAXNetworkAnalyzer("TCPIP0::K-Instr0000.local::hislip0::INSTR")
    pwers, freqs = na.calc_and_stream_trace(1, 1)

    import csv
    import os
    base = os.getcwd()
    file = "path4_noise_inputloss_LOWBAND.csv"

    with open(os.path.join(base, file), mode="w", newline="") as f:
        writer = csv.writer(f)
        for index, power in enumerate(pwers):
            writer.writerow([freqs[index], power])

        f.close()
