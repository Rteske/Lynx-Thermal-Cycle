import serial
import time

class TempController:
    def __init__(self):
        port = "COM5"
        self.connector = DtechRS232(port)

    def set_setpoint(self, channel, value):
        if value > 85:
            print("Value too high, setting to 85")
            value = 85
        elif value < -50:
            print("Value too low, setting to -45")
            value = -50

        cmd = f"= SP{channel} {value}"
        self.connector.write_cmd(cmd)

    def set_chamber_state(self, state):
        if state:
            state = "ON"
        else:
            state = "OFF"

        cmd = "= " + state
        self.connector.write_cmd(cmd)

    def query_chamber_state(self):
        cmd = "? ON"
        return self.connector.query(cmd)

    def query_setpoint(self, channel):
        cmd = f"? SP{channel}"
        return self.connector.query(cmd)

    def query_actual(self, channel):
        cmd = f"? C{channel}"
        return self.connector.query(cmd)

    def set_sensor(self, channel, sensor_id):
        cmd = f"= CH{channel}SENSOR {sensor_id}"
        self.connector.write_cmd(cmd)

    def query_sensor(self, channel):
        cmd = f"? CH{channel}SENSOR"
        return self.connector.query(cmd)

    def query_cooling_output(self, channel):
        cmd = f"? {channel}LO"
        return self.connector.query(cmd)

    def query_heating_output(self, channel):
        cmd = f"? {channel}HI"
        return self.connector.query(cmd)

    def set_temp(self, temp):
        self.temp = temp

class DtechRS232:
    def __init__(self, port):
        self.ser = serial.Serial(port, baudrate=19200, timeout=2, bytesize=serial.EIGHTBITS, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE)

    def read_to_clear(self):
        buffer = self.ser.read(8)
        print(buffer)
        return buffer

    def write_cmd(self, cmd):
        self.ser.write(bytearray(cmd, "ascii"))
        start_time = time.time()
        while True:
            res_buffer = self.ser.read(8)
            if res_buffer or time.time() - start_time > 5:  # Set the timeout to 5 seconds
                break
        self.ser.flush()
        print(res_buffer)
        return res_buffer

    def query(self, cmd):
        self.ser.write(bytearray(cmd, "ascii"))
        buffer = self.ser.read(8)
        self.ser.flush()
        return buffer 
    
if __name__ == "__main__":
    tc = TempController()
    tc.set_setpoint(1, 25)
    time.sleep(1)
    print(tc.query_setpoint(1))
    print(tc.query_actual(1))
    tc.set_chamber_state(True)
    time.sleep(1)
    print(tc.query_chamber_state())
    tc.set_chamber_state(False)
    time.sleep(1)
    print(tc.query_chamber_state())