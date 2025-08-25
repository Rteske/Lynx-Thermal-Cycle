import time
import datetime
import ast

class RS422_DAQ:
    def __init__(self):
        self.conn = DtechRS422()
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

        self.read_status_return()
        try:
            self.read_status_return()
            print("DAQ validated")
        except:
            print("Failed to validate daq")

    def gain_value_to_hex(self, value):
        hex_value = ''
        for index, db in enumerate(self.DBS):
            if value == db:
                hex_value = hex(self.BASE_NUMS[index])
                
        return hex_value
    
    def hex_to_gain_value(self, hex_value):
        gain_value = ''
        for index, base_value in enumerate(self.BASE_NUMS):
            if base_value == int(hex_value):
                gain_value = self.DBS[index]

        return gain_value
    
    def enable_rf(self):
        self.conn.write_cmd(self.CMD_RF_ENABLE)
        rf_on_off, _, _, _, _, _ = self.read_status_return()

        if rf_on_off == "ON":
            return "COMPLETE"
        else:
            return "INCOMPLETE"
        
    def disable_rf(self):
        self.conn.write_cmd(self.CMD_RF_DISABLE)

    def set_band(self, band):
        try:
            self.conn.write_cmd(self.BANDS[band])
            _, _, bandpath, _, _, _ = self.read_status_return()
            if bandpath == band:
                return "COMPLETE"
            else:
                return "INCOMPLETE"
        except KeyError as e:
            print(e)
            print(f"FAILED TO SET BAND TO: {bandpath}")

    def change_gain(self, init_gain_value):
        if init_gain_value <= 41:
            msg = self.gain_value_to_hex(init_gain_value)
            self.conn.write_cmd(msg)
            _, _, _, gain_value, _, _ = self.read_status_return()
            if gain_value == init_gain_value + 10:
                return "COMPLETE"
            else:
                return "INCOMPLETE"
        else:
            return f"Gain value is out of operating range: {gain_value}"

    def read_status_return(self):   
        byte_arr = self.conn.query_status()

        rf_on_off = ''
        if byte_arr[0] == self.CMD_RF_ENABLE:
            rf_on_off = "ON"
        elif byte_arr[0] == self.CMD_RF_DISABLE:
            rf_on_off = "OFF"

        fault_status = ''
        for fault, byte in self.FAULTS.items():
            if byte == byte_arr[1]:
                fault_status = fault

        bandpath = ''
        for band, byte in self.BANDS.items():
            if byte_arr[2] == byte:
                bandpath = band

        gain_value = self.hex_to_gain_value(byte_arr[3])

        bits_9_5 = self.conn.bin_format(byte_arr[4])
        bits_4_0 = self.conn.bin_format(byte_arr[5])

        bits_4_0 = bits_4_0[5:]
        bits_9_5 = bits_9_5[5:]

        bit_collection = bits_9_5 + bits_4_0

        temp_int = int(bit_collection, 2)

        w_offset = temp_int + 1410

        temp_value = (((w_offset / 4096) * 3.3) - 1.5685) / -0.0032

        date_string = datetime.datetime.now()

        return rf_on_off, fault_status, bandpath, gain_value, date_string, temp_value
        
import serial

class DtechRS422:
    def __init__(self):
        self.port = "COM4"
        self.ser = serial.Serial(self.port, baudrate=230400, parity=serial.PARITY_EVEN, stopbits=1, timeout=1, bytesize=serial.EIGHTBITS)

    def write_cmd(self, cmd):
        if isinstance(cmd, str):
            cmd = int(cmd, 0)

        self.ser.write([cmd])

    def query_status(self):
        self.ser.write([0x20])
        buffer = self.ser.read(size=8)
        return buffer
    
    def bin_format(self, integer):
        return bin(integer)
    
if __name__ == "__main__":
    daq = DtechRS422()
    buffer = daq.query_status()
    print(buffer)