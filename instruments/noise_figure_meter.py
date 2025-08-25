import pyvisa
import time

import pyvisa.constants


class NoiseFigure8970B:
    def __init__(self, visa_address):
        self.rm = pyvisa.ResourceManager()
        self._res = self.rm.open_resource(visa_address)
        self._lib = self.rm.visalib
        self._res.timeout = 3000

    # def clear_status(self):
    #     print("SHIT")

    # def enable_status(self):
    #     # 48.0 enabling the noise figure meter to be controller
    #     self._res.write("SC")

    #     # PASS THROUGH OFF [DP]
    #     self._res.write("DP")

    #     self._res.write("CT")
    #     # ACTIVE CONTROL NEEDS ON [CT]
        

    #     # 42.3 MIN FREQUENCY 42.4 MAX FREQUENCY in detected 
    #     # Actual instrument measurement range set thru FA FB

    # def set_up(self):
    #     # ENABLE 1.1 MODE FOR HIGHER FREQS
    #     self._res.write("E1")

    #     # SET START [MN] AND STOP [MX]
    #     self._res.write(f"MN {18000} EN")
    #     self._res.write(f"MX {31000} EN")

    #     # SET 
    #     self._res.write(f"FA {18000} EN")
    #     self._res.write(f"FB {31000} EN")

    #     # SET STEPSIZE 
    #     self._res.write(f"SS {1000} EN")

    #     # SET INC [FN]
    #     self._res.write(f"FN {1000} EN")

    #     # SELECT ENR TABLE
    #     self._res.write("RC NR 1 EN NR")

    #     # CAL
    #     self._res.write(f"CA")



    #     # CORRETED VALUE [M2]
    #     self._res.write(f"M2")

    def deassert_ren(self):
        print(self._res.lock_state)

        self._lib.gpib_control_ren(self._res.session, pyvisa.constants.RENLineOperation.deassert)

    def set_and_measure(self, freqs):
        bucket = []
        res = self._res.query(f"M1")
        print(res)
        for freq in freqs:
            res = self._res.query(f"FR {freq} EN")
            print(res)
            time.sleep(2)
            noise_figure = self._res.query("MEASUREMENT")
            time.sleep(2)
            bucket.append([freq, float(noise_figure)])
            # self._lib.flush(self._res.session, pyvisa.constants.BufferOperation.flush_transmit_buffer)
        

            # self._lib.flush(self._res.session, pyvisa.constants.BufferOperation.discard_read_buffer)
            # self._lib.flush(self._res.session, pyvisa.constants.BufferOperation.discard_write_buffer)
            # self._lib.flush(self._res.session, pyvisa.constants.BufferOperation.discard_transmit_buffer)
            
        
            # self._lib.flush(self._res.session, pyvisa.constants.BufferOperation.discard_receive_buffer)
        return bucket
    
    # def get_noise_figure(self, freq):
    #     freq = int(freq / 1e6)
    #     self._res.write(f"FREQUENCY {freq} MHz")
    #     time.sleep(5)
    #     noise_figure = self._res.query("MEASUREMENT")
    #     noise_figure = float(noise_figure.strip())

    #     return noise_figure

    # def set_start_and_stop_freq_mghz(self, start_freq, stop_freq):
    #     start_freq = start_freq / 1e6
    #     stop_freq = stop_freq / 1e6

    #     self._res.write(f"START FREQ {start_freq} MHz")
    #     self._res.write(f"STOP FREQ {stop_freq} MHz")

if __name__ == "__main__":
    noise_figrue = NoiseFigure8970B(visa_address="GPIB0::8::INSTR")

    noise_figures = noise_figrue.set_and_measure(18000, 32000)
    print(noise_figures)
    noise_figrue._res.close()

    input_loss = [
        -4.303,
        -4.45,
        -4.64,
        -5.11,
        -5.01,
        -5.19,
        -5.11,
        -5.25,
        -5.33,
        -5.44,
        -5.67,
        -5.71,
        -5.91,
        -5.92
    ]

    for k, i in enumerate(noise_figures):
        print("FUCK:", i[0], " SHIT:", i[1] + input_loss[k]) 

    # rm = pyvisa.ResourceManager()
    # resources = rm.list_resources()
    # print(resources)