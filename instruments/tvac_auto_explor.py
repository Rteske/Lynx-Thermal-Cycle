import socket
import json
import threading
from enum import Enum, IntFlag

class IPClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = None
        self.lock = threading.Lock()

    def connect(self):
        with self.lock:
            if self.socket is None:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # Enable TCP socket options for better reliability
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                try:
                    self.socket.connect((self.ip, self.port))
                    self.socket.settimeout(5)
                except socket.error as e:
                    print(f"Connection failed: {e}")
                    self.socket.close()
                    self.socket = None
                    raise

    def disconnect(self):
        with self.lock:
            if self.socket:
                self.socket.close()
                self.socket = None

    def send(self, message):
        with self.lock:
            if self.socket:
                try:
                    self.socket.sendall(message.encode("utf-8"))
                except socket.error as e:
                    print(f"Send failed: {e}")
                    raise

    def receive(self, buffer_size=1024):
        with self.lock:
            if self.socket:
                try:
                    data = self.socket.recv(buffer_size)
                    if not data:
                        # Connection closed by remote host
                        return None
                    return data.decode("utf-8").strip()
                except socket.timeout:
                    print("Receive timeout")
                    return None
                except socket.error as e:
                    print(f"Receive failed: {e}")
                    return None
            return None

    def run_discovery_scan(self, discovery_port=23514):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.settimeout(5)
            message = b"AutoExplor Discovery"
            s.sendto(message, (self.ip, discovery_port))
            try:
                data, addr = s.recvfrom(1024)
                print(f"Received response from {addr}: {data}")
                return data
            except socket.timeout:
                print("No response received.")
                return None


class AutoExplorStatus(Enum):
    SUCCESS = 0


class DeviceID(IntFlag):
    """Table 1: DEVICEIDS bitmask mapping.

    Use with decode_device_mask(mask) to list active devices.
    """
    VENT_VALVE = 1                 # Vent valve properties.
    GATE_VALVE = 2                 # Gate valve properties.
    ROUGH_VALVE = 4                # Roughing line valve properties.
    T_CUBE = 8                     # TCube solid state cooling system properties.
    TURBO_WATER_CHILLER = 16       # Liquid-cooled turbo chiller properties.
    ROUGH_PUMP = 32                # Roughing pump properties.
    CRYO_PLATEN_PUMP = 64          # Coolant pump properties (ethanol cooled systems).
    COMPRESSOR = 128               # Air compressor properties.
    TURBO = 256                    # Turbo pump properties.
    PURGE_VALVE = 512              # Purge valve properties.
    CHAMBER_HEATER = 1024          # Chamber heating properties.
    PLATEN_HEATER = 2048           # Platen heating properties.
    VAPOR_TRAP = 4096              # Vapor trap bath properties (ethanol cooled systems).
    CHAMBER_SYSTEM = 8192          # Overall system properties.
    LN2_SYSTEM = 16384             # Liquid nitrogen powered cooling system properties.
    HC_RECIRCULATOR = 32768        # Recirculating heating & cooling system.


def decode_device_mask(mask_value):
    """Decode a bitmask (int or numeric string) into a list of DeviceID names.

    Returns a list of strings like ["VENT_VALVE", "ROUGH_PUMP", ...].
    """
    if mask_value is None:
        return []
    if isinstance(mask_value, str):
        try:
            # Support decimal or hex strings (e.g., "0x101")
            mask = int(mask_value, 0)
        except ValueError:
            return []
    elif isinstance(mask_value, (int,)):
        mask = mask_value
    else:
        try:
            mask = int(mask_value)
        except (ValueError, TypeError):
            return []

    present = []
    for member in DeviceID:
        if member & mask:
            present.append(member.name)
    return present


class ReadoutID(IntFlag):
    """Table 2: READOUTIDS bitmask mapping."""
    CHILLER_BATH = 8               # Temperature of bath (ethanol cooled systems).
    PLATEN_TC = 16                 # Temperature of the platen thermocouple (attached under platen)
    SAMPLE_1 = 32                  # Optional thermocouple readout.
    PRESSURE = 64                  # Pressure readout on non-pressure-controlled systems.
    CUSTOM_RO_1 = 128              # Custom ExploraVac readout.
    CUSTOM_RO_2 = 256              # Custom ExploraVac readout.
    CUSTOM_RO_3 = 512              # Custom ExploraVac readout.
    SAMPLE_2 = 1024
    SAMPLE_3 = 2048
    SAMPLE_4 = 4096
    SAMPLE_5 = 8192
    SAMPLE_6 = 16384
    SAMPLE_7 = 32768
    SAMPLE_8 = 65536
    SAMPLE_9 = 131072
    SAMPLE_10 = 262144
    SAMPLE_11 = 524288
    SAMPLE_12 = 1048576
    SAMPLE_13 = 2097152
    SAMPLE_14 = 4194304
    SAMPLE_15 = 8388608
    SAMPLE_16 = 16777216
    SAMPLE_17 = 33554432
    SAMPLE_18 = 67108864
    SAMPLE_19 = 134217728
    SAMPLE_20 = 268435456


def decode_readout_mask(mask_value):
    """Decode a bitmask (int or numeric string) into a list of ReadoutID names."""
    if mask_value is None:
        return []
    if isinstance(mask_value, str):
        try:
            mask = int(mask_value, 0)
        except ValueError:
            return []
    elif isinstance(mask_value, (int,)):
        mask = mask_value
    else:
        try:
            mask = int(mask_value)
        except (ValueError, TypeError):
            return []

    present = []
    for member in ReadoutID:
        if member & mask:
            present.append(member.name)
    return present


class ButtonID(IntFlag):
    """Table 3: BUTTONIDS bitmask mapping."""
    POWER = 1                # On/Off switch for the system.
    HIGH_VAC = 2             # On/Off switch for high vacuum mode.
    VENT = 4                 # On/Off switch for vent mode.
    PURGE = 128              # On/Off switch for purge mode.
    LIGHT = 256              # On/Off switch for chamber lighting.
    CHILLER = 512            # On/Off switch for prechilling the ethanol bath.
    ROUGH = 1024             # On/Off switch for rough vacuum mode.
    AUX_1 = 2048             # On/Off relay for auxiliary port 1.
    AUX_2 = 4096             # On/Off switch for auxiliary port 2.
    CUSTOM_BUTTON1 = 8192    # Custom Button.
    CUSTOM_BUTTON2 = 16384   # Custom Button.
    CUSTOM_BUTTON3 = 32768   # Custom Button.
    CUSTOM_BUTTON4 = 65536   # Custom Button.
    CUSTOM_BUTTON5 = 131072  # Custom Button.


def decode_button_mask(mask_value):
    """Decode a bitmask (int or numeric string) into a list of ButtonID names."""
    if mask_value is None:
        return []
    if isinstance(mask_value, str):
        try:
            mask = int(mask_value, 0)
        except ValueError:
            return []
    elif isinstance(mask_value, (int,)):
        mask = mask_value
    else:
        try:
            mask = int(mask_value)
        except (ValueError, TypeError):
            return []

    present = []
    for member in ButtonID:
        if member & mask:
            present.append(member.name)
    return present


class SetpointID(IntFlag):
    """Table 4: SETPOINTIDS bitmask mapping."""
    CHAMBER_HEATING_CONTROL = 8     # Chamber wall heating setpoint control.
    PLATEN_HEATING_CONTROL = 16     # Platen heating/cooling setpoint control.
    PRESSURE_CONTROL = 64           # Roughing range setpoint pressure control.
    CUSTOM_SP1 = 262144             # Custom setpoint.
    CUSTOM_SP2 = 524288             # Custom setpoint.


def decode_setpoint_mask(mask_value):
    """Decode a bitmask (int or numeric string) into a list of SetpointID names."""
    if mask_value is None:
        return []
    if isinstance(mask_value, str):
        try:
            mask = int(mask_value, 0)
        except ValueError:
            return []
    elif isinstance(mask_value, (int,)):
        mask = mask_value
    else:
        try:
            mask = int(mask_value)
        except (ValueError, TypeError):
            return []

    present = []
    for member in SetpointID:
        if member & mask:
            present.append(member.name)
    return present


class AutoExplor:
    def __init__(self, ip, main_port=23513, discovery_port=23514):
        self.client = IPClient(ip, main_port)
        self.discovery_port = discovery_port
        self.machine_id = None

        self.client.connect()

    def request_control(self):
        self.client.send('RequestControl\r\n')
        response = self.client.receive(1024)
        if response:
            status_code, _payload = self.parse_message(response)
            return AutoExplorStatus(status_code) if status_code is not None else None
        return None

    def parse_message(self, message: str | None):
        # Gracefully handle None/empty inputs
        if not message:
            return None, None
        if ":" in message:
            status_str, payload = message.split(":", 1)
            return int(status_str), payload
        return None, message

    def query_subsystem_config(self, subsystem: str):
        msg = f"Get{subsystem}Configuration\r\n"
        self.client.send(msg)
        response = self.client.receive(1024)
        status_code, payload = self.parse_message(response)
        return status_code, payload

    def send_custom_command(self, command: str):
        # Add line terminator if not present
        if not command.endswith('\r\n'):
            command += '\r\n'
        self.client.send(command)
        response = self.client.receive(1024)
        status_code, payload = self.parse_message(response)
        return status_code, payload

    # --- Configuration helpers ---
    def _get_configuration(self, command: str, buffer_size: int = 1024):
        """Send a configuration query command and try to parse JSON body.

        Returns (status_code:int|None, body:dict|str|None)
        """
        # Ensure proper line ending
        if not command.endswith("\r\n"):
            command = command + "\r\n"

        self.client.send(command)
        raw = self.client.receive(buffer_size)
        status_code, body = self.parse_message(raw if raw is not None else "")

        # Try to parse JSON if present
        if body is not None:
            try:
                parsed = json.loads(body)
                return status_code, parsed
            except (json.JSONDecodeError, TypeError):
                # Return raw body if not JSON
                return status_code, body
        return status_code, None

    def get_device_configuration(self):
        """GetDeviceConfiguration -> returns status, config (dict or raw str)."""
        return self._get_configuration("GetDeviceConfiguration")

    def get_readout_configuration(self):
        """GetReadoutConfiguration -> returns status, config (dict or raw str)."""
        return self._get_configuration("GetReadoutConfiguration")

    def get_button_configuration(self):
        """GetButtonConfiguration -> returns status, config (dict or raw str)."""
        return self._get_configuration("GetButtonConfiguration")

    def get_setpoint_configuration(self):
        """GetSetpointConfiguration -> returns status, config (dict or raw str)."""
        return self._get_configuration("GetSetpointConfiguration")

    def __del__(self):
        self.client.disconnect()

if __name__ == "__main__":
    auto_explor = AutoExplor('192.168.20.12')
    auto_explor.client.run_discovery_scan()
    device_status, device_cfg = auto_explor.get_device_configuration()
    print("DeviceConfiguration status:", device_status)
    print("DeviceConfiguration:", device_cfg)

    if isinstance(device_cfg, dict):
        # Heuristic keys that might contain the mask
        for key in ("DEVICEIDS", "DeviceIds", "device_ids", "devices", "config"):
            if key in device_cfg:
                print("DeviceIDs present:", decode_device_mask(device_cfg[key]))
                break

    readout_status, readout_cfg = auto_explor.get_readout_configuration()
    print("ReadoutConfiguration status:", readout_status)
    print("ReadoutConfiguration:", readout_cfg)
    if isinstance(readout_cfg, dict):
        for key in ("READOUTIDS", "ReadoutIds", "readout_ids", "readouts", "config"):
            if key in readout_cfg:
                print("ReadoutIDs present:", decode_readout_mask(readout_cfg[key]))
                break

    button_status, button_cfg = auto_explor.get_button_configuration()
    print("ButtonConfiguration status:", button_status)
    print("ButtonConfiguration:", button_cfg)
    if isinstance(button_cfg, dict):
        for key in ("BUTTONIDS", "ButtonIds", "button_ids", "buttons", "config"):
            if key in button_cfg:
                print("ButtonIDs present:", decode_button_mask(button_cfg[key]))
                break

    setpoint_status, setpoint_cfg = auto_explor.get_setpoint_configuration()
    print("SetpointConfiguration status:", setpoint_status)
    print("SetpointConfiguration:", setpoint_cfg)
    if isinstance(setpoint_cfg, dict):
        for key in ("SETPOINTIDS", "SetpointIds", "setpoint_ids", "setpoints", "config"):
            if key in setpoint_cfg:
                print("SetpointIDs present:", decode_setpoint_mask(setpoint_cfg[key]))
                break