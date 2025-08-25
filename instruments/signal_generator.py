import pyvisa
import time
import logging
import numpy as np
logger = logging.getLogger().setLevel(logging.INFO)

class SynthesizedCWGenerator:
    def __init__(self, visa_address):
        self.visa_address = visa_address
        rm = pyvisa.ResourceManager()
        self.instrument = rm.open_resource(visa_address)
        self.instrument.write("*RST")
        print(f"Synthesized CW Generator validated")
        
    def send_command(self, command):
        if self.instrument:
            try:
                res = self.instrument.write(command)
                print(res)
            except Exception as e:
                print(f"Error sending command: {str(e)}")
                return None
        else:
            print("Not connected to any instrument.")
            return None

    def set_frequency(self, frequency):
        command = f"FREQ:CW {frequency} Hz"
        return self.send_command(command)

    def set_amplitude(self, amplitude):
        command = f"POW:LEV {amplitude} dBm"
        return self.send_command(command)

    def start_output(self):
        command = "POW:STAT ON;"
        return self.send_command(command)

    def stop_output(self):
        command = "OUTP:STAT OFF;"
        return self.send_command(command)

class E4438CSignalGenerator:
    """General class for interacting with E4438C lab bench signal generator"""
    def __init__(self, adrress, max_power=0, simulate=False):
        self._simulate = simulate
        self._running = False
        self._max_power = max_power
        self._current_waveform = None
        if not self._simulate:
            rm = pyvisa.ResourceManager()
            self._res = rm.open_resource(adrress)
            self._res.write("*CLS")
            self._res.write("*WAI")
            self._res.write("*RST")
            time.sleep(3)
            self._res.timeout = 25000 #timeout given in milliseconds

    def stop(self):
        # logger.info('Stopping signal generation')
        self._running = False
        if not self._simulate:
            self._res.write(":OUTPUT:STATE OFF")

    def set_frequency(self, frequency):
        print(f"RFSG CHANGING FREQ TO {frequency}")
        self._res.write(f"FREQ:FIX {int(frequency)}Hz")

    def set_amplitude(self, amplitude):
        self._res.write(f"POW:LEV {amplitude} dBm")

    def start_output(self):
        self._res.write("POW:STAT ON;")

    def gen_cw(self, frequency, power):
        """Start generating CW signal"""
        if power > self._max_power:
            raise TestException('RFSG: Power %0.3f dBm is above maximum allowed!' % power)
        if self._running:
            self.stop()
        # logger.info('Generating CW signal at %0.1f MHz, power = %0.3f dBm' % (MHz(frequency), power))
        self._current_waveform = 'cw'
        if not self._simulate:
            self.enable_modulation("OFF")
            self._res.write(f":Frequency:FIXed {frequency}Hz" )
            self._res.write(f"POW:AMPL {power} dBm")
            self._res.write(":OUTPut:STATe ON")
            self._running = True
        else:
            self._frequency = frequency
            self._power = power

    def gen_arb(self, wf_fname, frequency, power):
        """Start generating ARB signal from waveform file"""
        if power > self._max_power:
            raise TestException('RFSG: Power %0.1f dBm is above maximum allowed!' % power)
        if self._running:
            self.stop()
        # logger.info('Generating ARB signal at %0.1f MHz, power = %d dBm, file: %s'
                    # % (MHz(frequency), power, op.basename(wf_fname)))
        if not self._simulate:
            if wf_fname != self._current_waveform:
                self._current_waveform = wf_fname
                volatile_mem_waveforms = self._res.query(':MMEMory:CATalog? "WFM1:"')
                if self._current_waveform not in volatile_mem_waveforms and "@DWCDMA" not in self._current_waveform:
                    self.load_waveform(self._current_waveform)
                    #Give time to load waveform to volatile memory
                    
                self.select_waveform(self._current_waveform)
                
                logger.debug('Uploaded ARB waveform.')

            self.enable_modulation("ON")
            self._res.write(f":Frequency:FIXed {frequency}")
            self._res.write(f"POW:AMPL {power} dBm")
            self.enable_modulation("ON")
            self._res.write(":OUTPut:STATe ON")
            self._running = True
        else:
            self._frequency = frequency
            self._power = power

    def get_dmod_files(self):
        dmod_files = self._res.query(":MEMory:CATalog:DMOD?")
        return dmod_files
            
    def change_amplitude(self, value, unit="dBm"):
        response = self._res.write(":SOURce:POWer:LEVel:IMMediate:AMPLitude {} {}".format(value, unit))
        if response == 50:
            print("in da clear")

    def get_waveforms(self):
        if not self._simulate:
            waveforms = self._res.query(':MEMory:CATalog:ALL?').split(",")
            for response in waveforms[:]:
                if "@DWCDMA" not in response and "@NVWFM" not in response:
                    
                    #For now we will only be able to play WCDMA or ARB waveforms to avoid clutter
                    waveforms.remove(response)
            waveforms = [waveform.replace('"', '').replace('@NVWFM', '') for waveform in waveforms] #remove any lingering quotation marks from the response and remove @NVWFM from wavefroms used for dual arb gen

            return waveforms
        
    def select_demod_filter(self, dmod):
        # ([:SOURce]:RADio:DMODulation:ARB)
        # self._res.write(f"RAD:DMOD:ARB:FLIT {dmod}")
        # self._res.write(":SOURce:RADio:CUSTom:MODulation:TYPE OQPSK")
        self._res.write(f"RAD:DMOD:ARB:SET '{dmod}'")

    def select_waveform(self, waveform):
        if not self._simulate:
            if "@DWCDMA" in waveform:
                self._res.write(f':SOURce:RADio:WCDMa:TGPP:ARB:LINK:DOWN:SETup "{waveform}"')
            else:
                #Waveforms used in ARB GEN
                self._res.write(f':SOURce:RADio:ARB:WAVeform "WFM1:{waveform}"')
                

    def enable_modulation(self, state):
        self._res.write(f"RAD:DMOD:ARB {state}")

if __name__ == "__main__":
    fuc = E4438CSignalGenerator("GPIB0::30::INSTR")
    dmo = fuc.get_dmod_files()
    print(dmo)

    fuc.select_demod_filter("OQPSK")