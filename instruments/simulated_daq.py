import time
import datetime
import random
import ast

class SimulatedRS422_DAQ:
    """
    Simulated version of RS422_DAQ for testing and development without hardware.
    Mimics all functionality of the real DAQ with realistic simulated responses.
    """
    
    def __init__(self):
        # Simulate connection initialization
        self.conn = SimulatedDtechRS422()
        
        # Command definitions (same as real DAQ)
        self.CMD_RF_ENABLE = 0x01
        self.CMD_RF_DISABLE = 0x00
        self.CMD_REPORT_STATUS = 0x20

        self.FAULTS = {
            "No Faults": 0x20,
            "Fault_+5V_Reg_Band_3": 0x21,
            "Fault_+8V_Reg_Band_2": 0x22,
            "Fault_+8V_Reg_Band_1": 0x24,
            "Fault_-5V_Reg": 0x28,
            "Fault_Command_Error": 0x30
        }

        self.BANDS = {
            "NONE": 0x40,
            "L": 0x41,
            "M": 0x42,
            "H": 0x43
        }

        self.BASE_NUMS = list(range(96, 128, 1))
        self.DBS = list(range(10, 42, 1))

        # Simulated state variables
        self.rf_enabled = False
        self.current_band = "NONE"
        self.current_gain = 20  # Default gain value
        self.fault_state = "No Faults"
        self.base_temperature = 25.0  # Base temperature in Celsius
        
        # Initialize and validate
        self.read_status_return()
        try:
            self.read_status_return()
            print("Simulated DAQ validated")
        except Exception as e:
            print(f"Failed to validate simulated DAQ: {e}")

    def gain_value_to_hex(self, value):
        """Convert gain value to hex representation"""
        hex_value = ''
        for index, db in enumerate(self.DBS):
            if value == db:
                hex_value = hex(self.BASE_NUMS[index])
                
        return hex_value
    
    def hex_to_gain_value(self, hex_value):
        """Convert hex value back to gain value"""
        gain_value = ''
        for index, base_value in enumerate(self.BASE_NUMS):
            if base_value == int(hex_value):
                gain_value = self.DBS[index]

        return gain_value
    
    def enable_rf(self):
        """Enable RF output"""
        print("Simulated: Enabling RF")
        self.conn.write_cmd(self.CMD_RF_ENABLE)
        self.rf_enabled = True
        
        # Simulate small delay
        time.sleep(0.1)
        
        rf_on_off, _, _, _, _, _ = self.read_status_return()

        if rf_on_off == "ON":
            print("Simulated: RF enabled successfully")
            return "COMPLETE"
        else:
            print("Simulated: RF enable failed")
            return "INCOMPLETE"
        
    def disable_rf(self):
        """Disable RF output"""
        print("Simulated: Disabling RF")
        self.conn.write_cmd(self.CMD_RF_DISABLE)
        self.rf_enabled = False
        time.sleep(0.1)

    def set_band(self, band):
        """Set the frequency band"""
        try:
            print(f"Simulated: Setting band to {band}")
            self.conn.write_cmd(self.BANDS[band])
            self.current_band = band
            
            # Simulate small delay
            time.sleep(0.1)
            
            _, _, bandpath, _, _, _ = self.read_status_return()
            if bandpath == band:
                print(f"Simulated: Band set to {band} successfully")
                return "COMPLETE"
            else:
                print(f"Simulated: Band setting failed")
                return "INCOMPLETE"
        except KeyError as e:
            print(f"Simulated error: {e}")
            print(f"FAILED TO SET BAND TO: {band}")
            return "INCOMPLETE"

    def change_gain(self, init_gain_value):
        """Change the gain value"""
        if init_gain_value <= 41:
            print(f"Simulated: Setting gain to {init_gain_value}")
            msg = self.gain_value_to_hex(init_gain_value)
            self.conn.write_cmd(msg)
            self.current_gain = init_gain_value
            
            # Simulate small delay
            time.sleep(0.1)
            
            _, _, _, gain_value, _, _ = self.read_status_return()
            if gain_value == init_gain_value + 10:
                print(f"Simulated: Gain set to {init_gain_value} successfully")
                return "COMPLETE"
            else:
                print(f"Simulated: Gain setting failed")
                return "INCOMPLETE"
        else:
            error_msg = f"Gain value is out of operating range: {init_gain_value}"
            print(f"Simulated error: {error_msg}")
            return error_msg

    def read_status_return(self):   
        """Read and return current status - simulated version"""
        # Simulate communication delay
        time.sleep(0.01)
        
        byte_arr = self.conn.query_status()

        # Parse RF status
        rf_on_off = "ON" if self.rf_enabled else "OFF"

        # Simulate occasional faults (1% chance)
        if random.random() < 0.01:
            fault_options = list(self.FAULTS.keys())
            fault_options.remove("No Faults")
            self.fault_state = random.choice(fault_options)
        else:
            self.fault_state = "No Faults"

        # Return current band
        bandpath = self.current_band

        # Return current gain (adding 10 as per original logic)
        gain_value = self.current_gain + 10

        # Generate simulated temperature reading
        # Add some realistic variation around base temperature
        temp_variation = random.uniform(-2.0, 3.0)  # Realistic temperature drift
        temp_value = self.base_temperature + temp_variation

        # Current timestamp
        date_string = datetime.datetime.now()

        print(f"Simulated Status: RF={rf_on_off}, Band={bandpath}, Gain={gain_value}dB, Temp={temp_value:.1f}°C")

        return rf_on_off, self.fault_state, bandpath, gain_value, date_string, temp_value

    def inject_fault(self, fault_name):
        """Utility method to inject specific faults for testing"""
        if fault_name in self.FAULTS:
            self.fault_state = fault_name
            print(f"Simulated: Injected fault - {fault_name}")
        else:
            print(f"Simulated error: Unknown fault type - {fault_name}")

    def set_base_temperature(self, temp):
        """Set the base temperature for simulation"""
        self.base_temperature = temp
        print(f"Simulated: Base temperature set to {temp}°C")

class SimulatedDtechRS422:
    """
    Simulated RS422 communication interface.
    Mimics serial communication without requiring actual hardware.
    """
    
    def __init__(self):
        self.port = "SIMULATED_COM4"
        self.connected = True
        print(f"Simulated: Connected to {self.port}")
        
        # Simulate connection parameters
        self.baudrate = 230400
        self.parity = "EVEN"
        self.stopbits = 1
        self.timeout = 1
        self.bytesize = 8

    def write_cmd(self, cmd):
        """Simulate writing a command"""
        if isinstance(cmd, str):
            cmd = int(cmd, 0)
        
        # Simulate command processing delay
        time.sleep(0.001)
        print(f"Simulated: Sent command 0x{cmd:02X}")

    def query_status(self):
        """Simulate status query response"""
        # Simulate communication delay
        time.sleep(0.005)
        
        # Return simulated 8-byte response
        # This would normally come from the actual hardware
        simulated_response = bytearray([
            0x01,  # RF status byte
            0x20,  # Fault status byte
            0x40,  # Band byte
            0x70,  # Gain byte
            0x80,  # Temperature bits 9-5
            0x10   # Temperature bits 4-0
        ])
        
        # Pad to 8 bytes
        while len(simulated_response) < 8:
            simulated_response.append(0x00)
            
        print(f"Simulated: Received status response: {[hex(b) for b in simulated_response]}")
        return simulated_response
    
    def bin_format(self, integer):
        """Convert integer to binary format"""
        return bin(integer)

class DAQFactory:
    """
    Factory class to create either real or simulated DAQ instances.
    Useful for switching between hardware and simulation modes.
    """
    
    @staticmethod
    def create_daq(simulate=True):
        """
        Create a DAQ instance.
        
        Args:
            simulate (bool): If True, creates simulated DAQ. If False, creates real DAQ.
            
        Returns:
            DAQ instance (simulated or real)
        """
        if simulate:
            print("Creating simulated DAQ...")
            return SimulatedRS422_DAQ()
        else:
            print("Creating real DAQ...")
            try:
                # Import the real DAQ only when needed
                from .daq import RS422_DAQ
                return RS422_DAQ()
            except ImportError as e:
                print(f"Failed to import real DAQ: {e}")
                print("Falling back to simulated DAQ...")
                return SimulatedRS422_DAQ()
            except Exception as e:
                print(f"Failed to initialize real DAQ: {e}")
                print("Falling back to simulated DAQ...")
                return SimulatedRS422_DAQ()

if __name__ == "__main__":
    # Demo the simulated DAQ
    print("=== Simulated DAQ Demo ===")
    
    # Create simulated DAQ
    daq = SimulatedRS422_DAQ()
    
    # Test basic operations
    print("\n--- Testing RF Control ---")
    daq.enable_rf()
    time.sleep(1)
    daq.disable_rf()
    
    print("\n--- Testing Band Control ---")
    for band in ["L", "M", "H", "NONE"]:
        daq.set_band(band)
        time.sleep(0.5)
    
    print("\n--- Testing Gain Control ---")
    for gain in [15, 25, 35]:
        daq.change_gain(gain)
        time.sleep(0.5)
    
    print("\n--- Testing Fault Injection ---")
    daq.inject_fault("Fault_+5V_Reg_Band_3")
    daq.read_status_return()
    
    print("\n--- Continuous Monitoring (5 readings) ---")
    for i in range(5):
        status = daq.read_status_return()
        time.sleep(1)
    
    print("\n=== Demo Complete ===")
