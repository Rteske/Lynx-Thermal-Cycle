import pyvisa
import serial
import time

class SerialPowerSupply:
    def __init__(self, port):
        self._res = serial.Serial(port=port, bytesize=serial.EIGHTBITS, baudrate=9600)
        print("Power Supply Validated")

    def _on_off_str(self, state):
        if state:
            state_str = 'ON'
        else:
            state_str = 'OFF'
        return state_str
    
    def query(self, arg):
        self.write_cmd(arg)
        value = self._res.read_all()
        return value
    
    def write_cmd(self, msg):
        msg = msg.encode('ASCII')
        self._res.write(msg)

    def get_voltage(self):
        """Get the voltage"""
        voltage = float(self.query('MEAS:VOLT?'))
        print('Read voltage: %0.2f V' % voltage)
        return voltage

    def set_voltage(self, voltage):
        """Set the voltage"""
        print('Set voltage to %0.2f V' % voltage)
        self.write_cmd(f'VOLT:LEV {voltage}V ')

    def get_current(self):
        """Get the current"""
        current = float(self.query('MEAS:CURR?'))

        print('Read current: %0.2f A' % current)
        return current

    def set_current(self, current):
        """Set the current limit"""
        print('Set current limit to %0.2f A' % current)
        self.write_cmd(f'CURR:LEV {current}')

    def get_output_state(self):
        """Get output state"""
        state = int(self.query(b'OUTPut:STATe?')) == 1
        print('Read output state: %d' % state)
        return state

    def set_output_state(self, state):
        """Set the output state"""
        print('Turning output %s' % self._on_off_str(state))
        self.write_cmd('OUTPut:STATe %s\n' % self._on_off_str(state))

    def set_overcurrent_protection(self, state):
        """Turn on/off over current protection"""
        print('Setting over current protection %s' % self._on_off_str(state))
        self.write_cmd('CURRent:PROTection:STATe %s' % self._on_off_str(state))

    def clear_output_protection(self):
        """Clear over current protection"""
        print('Clearing over current protection')
        self.write_cmd('OUTPut:PROTection:CLEar')

    def get_output_fault(self):
        """Get the output fault conditions that are set"""
        fault = None
        fault_code = int(self.query('STATus:QUEStionable?'))
        FAULT_CODES = {'over-voltage': 1, 'over-current': 2,
                        'power-failure': 4, 'over-temperature': 16}
        fault_list = []
        print(fault_code)
        for name, code in FAULT_CODES.items():
            if fault_code & code != 0:
                fault_list.append(name)
        if len(fault_list) > 0:
            print('Fault code: 0x%02x: %s' % (fault_code, ' '.join(fault_list)))
            fault = fault_list

        return fault

class PowerSupply:
    def __init__(self, visa_address):
        rm = pyvisa.ResourceManager()
        self._res = rm.open_resource(visa_address)

        self.max_voltage = 34.5
        self.max_current = 3
        print("Power Supply Validated")

    def _on_off_str(self, state):
        if state:
            state_str = 'ON'
        else:
            state_str = 'OFF'
        return state_str

    def get_voltage(self):
        """Get the voltage"""
        voltage = float(self._res.query('MEAS:VOLT?'))
        print('Read voltage: %0.2f V' % voltage)
        return voltage

    def set_voltage(self, voltage):
        """Set the voltage"""
        if voltage > self.max_voltage:
            raise ValueError(f"Voltage exceeds maximum limit of {self.max_voltage} V")
        print('Set voltage to %0.2f V' % voltage)
        self._res.write(f'VOLT:LEV {voltage}V')

    def get_current(self):
        """Get the current"""
        current = float(self._res.query('MEAS:CURR?'))

        print('Read current: %0.2f A' % current)
        return current

    def set_current(self, current):
        """Set the current limit"""
        if current > self.max_current:
            raise ValueError(f"Current exceeds maximum limit of {self.max_current} A")
        print('Set current limit to %0.2f A' % current)
        self._res.write(f'CURR:LEV {current}')

    def get_output_state(self):
        """Get output state"""
        state = int(self._res.query('OUTPut:STATe?')) == 1
        print('Read output state: %d' % state)
        return state

    def set_output_state(self, state):
        """Set the output state"""
        print('Turning output %s' % self._on_off_str(state))
        self._res.write('OUTPut:STATe %s' % self._on_off_str(state))

    def set_overcurrent_protection(self, state):
        """Turn on/off over current protection"""
        print('Setting over current protection %s' % self._on_off_str(state))
        self._res.write('CURRent:PROTection:STATe %s' % self._on_off_str(state))

    def clear_output_protection(self):
        """Clear over current protection"""
        print('Clearing over current protection')
        self._res.write('OUTPut:PROTection:CLEar')

    def get_output_fault(self):
        """Get the output fault conditions that are set"""
        fault = None
        fault_code = int(self._res.query('STATus:QUEStionable?'))
        FAULT_CODES = {'over-voltage': 1, 'over-current': 2,
                        'power-failure': 4, 'over-temperature': 16}
        fault_list = []
        print(fault_code)
        for name, code in FAULT_CODES.items():
            if fault_code & code != 0:
                fault_list.append(name)
        if len(fault_list) > 0:
            print('Fault code: 0x%02x: %s' % (fault_code, ' '.join(fault_list)))
            fault = fault_list

        return fault
    
if __name__ == "__main__":
    psu = PowerSupply("GPIB0::15::INSTR")

    voltage = psu.get_voltage()
    current = psu.get_current()

    psu.set_voltage(0)
    psu.set_current(0)
    psu.set_output_state(False)

    print(voltage, current)