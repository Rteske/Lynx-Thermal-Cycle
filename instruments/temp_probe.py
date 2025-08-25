import subprocess
import pathlib
import os
import pyvisa

# \\dracal-usb-get.exe

class DracalTempProbe:
    def __init__(self, sno):
        self.file_path = pathlib.Path("C:\\Program Files (x86)\\DracalView")
        os.path.exists(self.file_path)
        self.sno = sno
        try:
            self.measure_temp()
            print("Dracal Temp probe Validated")
        except:
            print("Dracal Temp probe not validated")

    def measure_temp(self):
        try:
            p = subprocess.run(["dracal-usb-get.exe", "-s", self.sno], capture_output=True, shell=True)
            print(p.stdout)
            temp = p.stdout[0:5]
            return temp
        except (subprocess.CalledProcessError):
            return "dracal-usb-get error"
        

class Agilent34401A:
    def __init__(self, resource_name):
        self.rm = pyvisa.ResourceManager()
        self.instrument = self.rm.open_resource(resource_name)

    def identify(self):
        """Returns the identification string of the instrument."""
        return self.instrument.query('*IDN?')

    def configure_voltage_dc(self, range=10, resolution=0.001):
        """Configures the instrument for DC voltage measurements."""
        self.instrument.write(f'CONF:VOLT:DC {range}, {resolution}')

    def measure_voltage_dc(self):
        """Performs a DC voltage measurement."""
        return float(self.instrument.query('MEAS:VOLT:DC?'))

    def configure_current_dc(self, range=1, resolution=0.0001):
        """Configures the instrument for DC current measurements."""
        self.instrument.write(f'CONF:CURR:DC {range}, {resolution}')

    def measure_current_dc(self):
        """Performs a DC current measurement."""
        return float(self.instrument.query('MEAS:CURR:DC?'))

    def configure_resistance(self, range=1000, resolution=0.1):
        """Configures the instrument for resistance measurements."""
        self.instrument.write(f'CONF:RES {range}, {resolution}')

    def measure_resistance(self):
        """Performs a resistance measurement."""
        return float(self.instrument.query('MEAS:RES?'))

    def close(self):
        """Closes the instrument connection."""
        self.instrument.close()

    def measure_temp(self):
        res = self.measure_voltage_dc()
        temp = float(res) * 1000
        return temp