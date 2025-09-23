import socket
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
    """AutoExplor command status codes."""
    SUCCESS = 0                # Command executed without issue.
    NOT_RUN = 1               # Command not executed for some reason.
    NOT_ALLOWED = 2           # Command not allowed to be run, due to configuration or state of system.
    INCORRECTLY_FORMED = 3    # Command could not be executed due to improper syntax.
    PERMISSIONS_ERROR = 4     # Command needs elevated permissions (Full Control) before executing.
    DISCONNECTED = 5          # ExploraVac disconnected from the host.
    SERVER_ERROR = 6          # Unexpected error occurred while executing the command.
    NOT_RECOGNIZED = 7        # Command not recognized by the server.


class ColorState(Enum):
    """Color states for buttons and setpoints."""
    NONE = 0           # Off/None
    SOLID_GREEN = 1    # On/Normal operation
    BLINK_GREEN = 2    # Startup sequence
    SOLID_YELLOW = 3   # Warning/Caution
    BLINK_YELLOW = 4   # Warning/Attention needed
    SOLID_RED = 5      # Error/Critical
    BLINK_RED = 6      # Critical error/Emergency


def get_color_state_description(color_state):
    """Get a human-readable description of the color state."""
    descriptions = {
        ColorState.NONE: "Off/None",
        ColorState.SOLID_GREEN: "On/Normal operation", 
        ColorState.BLINK_GREEN: "Startup sequence",
        ColorState.SOLID_YELLOW: "Warning/Caution",
        ColorState.BLINK_YELLOW: "Warning/Attention needed", 
        ColorState.SOLID_RED: "Error/Critical",
        ColorState.BLINK_RED: "Critical error/Emergency"
    }
    
    try:
        if isinstance(color_state, int):
            color_state = ColorState(color_state)
        return descriptions.get(color_state, f"Unknown state ({color_state})")
    except ValueError:
        return f"Unknown state ({color_state})"


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
        self.request_control()

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
        if ";" in message:
            status_str, payload = message.split(";")
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
        """Send a configuration query command and parse integer response.

        Returns (status_code:int|None, config_mask:int|None)
        """
        # Ensure proper line ending
        if not command.endswith("\r\n"):
            command = command + "\r\n"

        self.client.send(command)
        raw = self.client.receive(buffer_size)
        status_code, body = self.parse_message(raw if raw is not None else "")

        # Parse the body as an integer bitmask
        if body is not None:
            try:
                # Try to parse as integer (decimal or hex)
                config_mask = int(body, 0) if isinstance(body, str) else int(body)
                return status_code, config_mask
            except (ValueError, TypeError):
                # Return None if can't parse as integer
                return status_code, None
        return status_code, None

    def get_device_configuration(self):
        """GetDeviceConfiguration -> returns status, config_mask (int)."""
        return self._get_configuration("GetDeviceConfiguration")

    def get_readout_configuration(self):
        """GetReadoutConfiguration -> returns status, config_mask (int)."""
        return self._get_configuration("GetReadoutConfiguration")

    def get_button_configuration(self):
        """GetButtonConfiguration -> returns status, config_mask (int)."""
        return self._get_configuration("GetButtonConfiguration")

    def get_setpoint_configuration(self):
        """GetSetpointConfiguration -> returns status, config_mask (int)."""
        return self._get_configuration("GetSetpointConfiguration")

    def extract_device_mask(self, config_mask):
        """Extract device mask - config_mask IS the device mask."""
        return config_mask

    def extract_readout_mask(self, config_mask):
        """Extract readout mask - config_mask IS the readout mask."""
        return config_mask

    def extract_button_mask(self, config_mask):
        """Extract button mask - config_mask IS the button mask."""
        return config_mask

    def extract_setpoint_mask(self, config_mask):
        """Extract setpoint mask - config_mask IS the setpoint mask."""
        return config_mask

    # --- Button Control Methods ---
    def get_button_name(self, button_id):
        """Get the friendly name for a button.
        
        Args:
            button_id: Button identifier (int or ButtonID enum member)
            
        Returns:
            tuple: (status_code, button_name)
        """
        if hasattr(button_id, 'value'):
            button_id = button_id.value
        
        command = f"GetButtonName {button_id}"
        return self.send_custom_command(command)

    def get_button_state(self, button_id):
        """Get the state and color status of a button.
        
        Args:
            button_id: Button identifier (int or ButtonID enum member)
            
        Returns:
            tuple: (status_code, response_dict) where response_dict contains:
                   {'on_off': bool, 'color_state': int, 'color_description': str, 'raw_response': str}
                   Returns None as response_dict if parsing fails.
        """
        if hasattr(button_id, 'value'):
            button_id = button_id.value
        
        command = f"GetButtonState {button_id}"
        status_code, payload = self.send_custom_command(command)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            try:
                parts = payload.strip().split()
                if len(parts) >= 2:
                    on_off = bool(int(parts[0]))
                    color_state = int(parts[1])
                    color_description = get_color_state_description(color_state)
                    return status_code, {
                        'on_off': on_off,
                        'color_state': color_state,
                        'color_description': color_description,
                        'raw_response': payload
                    }
                else:
                    return status_code, None
            except (ValueError, IndexError):
                return status_code, None
        
        return status_code, None

    def set_button_state(self, button_id, on_off):
        """Set the state of a button.
        
        Args:
            button_id: Button identifier (int or ButtonID enum member)
            on_off: True/1 for On, False/0 for Off
            
        Returns:
            tuple: (status_code, payload)
        """
        if hasattr(button_id, 'value'):
            button_id = button_id.value
        
        state_value = 1 if on_off else 0
        command = f"SetButtonState {button_id} {state_value}"
        return self.send_custom_command(command)

    def get_all_button_info(self, button_mask=None):
        """Get complete information for all configured buttons.
        
        Args:
            button_mask: Optional bitmask, if None will query current config
            
        Returns:
            dict: Button info with button names as keys and their data as values
        """
        if button_mask is None:
            _, button_mask = self.get_button_configuration()
        
        if button_mask is None:
            return {}
        
        button_info = {}
        for button_enum in ButtonID:
            if button_enum & button_mask:
                button_id = button_enum.value
                
                # Get button name
                name_status, name = self.get_button_name(button_id)
                
                # Get button state
                state_status, state_info = self.get_button_state(button_id)
                
                button_info[button_enum.name] = {
                    'id': button_id,
                    'name': name if name_status == AutoExplorStatus.SUCCESS.value else 'Unknown',
                    'state_info': state_info if state_status == AutoExplorStatus.SUCCESS.value else None,
                    'enum': button_enum
                }
        
        return button_info
    
    def turn_on_off_chamber(self, state: bool):
        """Turn on or off the chamber heating."""
        status, _ = self.set_button_state(ButtonID.POWER, state)
        return status

    # --- Readout Control Methods ---
    def get_readout_name(self, readout_id):
        """Get the friendly name for a readout.
        
        Args:
            readout_id: Readout identifier (int or ReadoutID enum member)
            
        Returns:
            tuple: (status_code, readout_name)
        """
        if hasattr(readout_id, 'value'):
            readout_id = readout_id.value
        
        command = f"GetReadoutName {readout_id}"
        return self.send_custom_command(command)

    def get_readout_native_unit(self, readout_id):
        """Get the native unit for a readout (e.g., Torr, °C).
        
        Args:
            readout_id: Readout identifier (int or ReadoutID enum member)
            
        Returns:
            tuple: (status_code, unit_string)
        """
        if hasattr(readout_id, 'value'):
            readout_id = readout_id.value
        
        command = f"GetReadoutNativeUnit {readout_id}"
        return self.send_custom_command(command)

    def get_readout_process_value(self, readout_id):
        """Get the current value of a readout in native units.
        
        Args:
            readout_id: Readout identifier (int or ReadoutID enum member)
            
        Returns:
            tuple: (status_code, value) where value is float or None if invalid (NaN)
        """
        if hasattr(readout_id, 'value'):
            readout_id = readout_id.value
        
        command = f"GetReadoutProcessValue {readout_id}"
        status_code, payload = self.send_custom_command(command)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            try:
                # Handle NaN case
                if payload.strip().lower() == 'nan':
                    return status_code, None
                # Try to parse as float
                value = float(payload.strip())
                return status_code, value
            except ValueError:
                return status_code, None
        
        return status_code, None

    def get_readout_info(self, readout_id):
        """Get complete information for a readout.
        
        Args:
            readout_id: Readout identifier (int or ReadoutID enum member)
            
        Returns:
            dict: Complete readout information including name, unit, and value
        """
        if hasattr(readout_id, 'value'):
            actual_id = readout_id.value
            enum_name = readout_id.name
        else:
            actual_id = readout_id
            # Try to find enum name
            enum_name = None
            for member in ReadoutID:
                if member.value == readout_id:
                    enum_name = member.name
                    break
            if enum_name is None:
                enum_name = f"READOUT_{readout_id}"

        # Get all information
        name_status, name = self.get_readout_name(actual_id)
        unit_status, unit = self.get_readout_native_unit(actual_id)
        value_status, value = self.get_readout_process_value(actual_id)

        return {
            'id': actual_id,
            'enum_name': enum_name,
            'name': name if name_status == AutoExplorStatus.SUCCESS.value else 'Unknown',
            'unit': unit if unit_status == AutoExplorStatus.SUCCESS.value else 'Unknown',
            'value': value if value_status == AutoExplorStatus.SUCCESS.value else None,
            'is_valid': value is not None,
            'formatted_value': f"{value} {unit}" if value is not None and unit_status == AutoExplorStatus.SUCCESS.value else "Invalid/NaN"
        }

    def get_all_readout_info(self, readout_mask=None):
        """Get complete information for all configured readouts.
        
        Args:
            readout_mask: Optional bitmask, if None will query current config
            
        Returns:
            dict: Readout info with readout names as keys and their data as values
        """
        if readout_mask is None:
            _, readout_mask = self.get_readout_configuration()
        
        if readout_mask is None:
            return {}
        
        readout_info = {}
        for readout_enum in ReadoutID:
            if readout_enum & readout_mask:
                info = self.get_readout_info(readout_enum)
                readout_info[readout_enum.name] = info
        
        return readout_info

    def get_temperature_readings(self, readout_mask=None):
        """Get all temperature-related readouts.
        
        Returns:
            dict: Temperature readings with descriptive names
        """
        temp_readouts = {}
        readout_info = self.get_all_readout_info(readout_mask)
        
        # Common temperature readouts
        temp_keywords = ['tc', 'temp', 'sample', 'platen', 'bath', 'chiller']
        
        for readout_name, info in readout_info.items():
            # Check if this looks like a temperature readout
            name_lower = readout_name.lower()
            if any(keyword in name_lower for keyword in temp_keywords):
                if info['unit'] and '°c' in info['unit'].lower():
                    temp_readouts[readout_name] = info
        
        return temp_readouts
    
    def get_pressure_readings(self, device_mask=None):
        pass

    # --- Device Control Methods ---
    def get_device_name(self, device_id):
        """Get the friendly name for a device.
        
        Args:
            device_id: Device identifier (int or DeviceID enum member)
            
        Returns:
            tuple: (status_code, device_name)
        """
        if hasattr(device_id, 'value'):
            device_id = device_id.value
        
        command = f"GetDeviceName {device_id}"
        return self.send_custom_command(command)

    def get_device_state(self, device_id):
        """Get the state of a device.
        
        Args:
            device_id: Device identifier (int or DeviceID enum member)
            
        Returns:
            tuple: (status_code, state) where state is True/False or None if failed
        """
        if hasattr(device_id, 'value'):
            device_id = device_id.value
        
        command = f"GetDeviceState {device_id}"
        status_code, payload = self.send_custom_command(command)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            try:
                state = bool(int(payload.strip()))
                return status_code, state
            except ValueError:
                return status_code, None
        
        return status_code, None

    def get_device_properties(self, device_id):
        """Get all available property names for a device.
        
        Args:
            device_id: Device identifier (int or DeviceID enum member)
            
        Returns:
            tuple: (status_code, property_list) where property_list is list of property names
        """
        if hasattr(device_id, 'value'):
            device_id = device_id.value
        
        command = f"GetDeviceProperties {device_id}"
        status_code, payload = self.send_custom_command(command)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            # Parse comma-delimited properties, handling spaces carefully
            properties = [prop.strip() for prop in payload.split(',')]
            # Remove empty strings
            properties = [prop for prop in properties if prop]
            return status_code, properties
        
        return status_code, []

    def get_device_property(self, device_id, property_name, include_units=True):
        """Get a specific property value for a device.
        
        Args:
            device_id: Device identifier (int or DeviceID enum member)
            property_name: Name of the property to retrieve
            include_units: If True, uses GetDeviceProperty (with units), 
                          if False, uses GetDevicePropertyNoUnits
            
        Returns:
            tuple: (status_code, property_value)
        """
        if hasattr(device_id, 'value'):
            device_id = device_id.value
        
        # Use appropriate command based on units preference
        if include_units:
            command = f'GetDeviceProperty {device_id} "{property_name}"'
        else:
            command = f'GetDevicePropertyNoUnits {device_id} "{property_name}"'
        
        return self.send_custom_command(command)

    def get_device_property_no_units(self, device_id, property_name):
        """Get a specific property value for a device without units.
        
        Args:
            device_id: Device identifier (int or DeviceID enum member)
            property_name: Name of the property to retrieve
            
        Returns:
            tuple: (status_code, numeric_value) where numeric_value is float or None
        """
        status_code, payload = self.get_device_property(device_id, property_name, include_units=False)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            try:
                # Try to parse as numeric value
                value = float(payload.strip())
                return status_code, value
            except ValueError:
                return status_code, None
        
        return status_code, None

    def get_device_info(self, device_id):
        """Get complete information for a device including all properties.
        
        Args:
            device_id: Device identifier (int or DeviceID enum member)
            
        Returns:
            dict: Complete device information
        """
        if hasattr(device_id, 'value'):
            actual_id = device_id.value
            enum_name = device_id.name
        else:
            actual_id = device_id
            # Try to find enum name
            enum_name = None
            for member in DeviceID:
                if member.value == device_id:
                    enum_name = member.name
                    break
            if enum_name is None:
                enum_name = f"DEVICE_{device_id}"

        # Get basic device info
        name_status, name = self.get_device_name(actual_id)
        state_status, state = self.get_device_state(actual_id)
        props_status, properties = self.get_device_properties(actual_id)

        device_info = {
            'id': actual_id,
            'enum_name': enum_name,
            'name': name if name_status == AutoExplorStatus.SUCCESS.value else 'Unknown',
            'state': state if state_status == AutoExplorStatus.SUCCESS.value else None,
            'properties': {}
        }

        # Get all property values
        if props_status == AutoExplorStatus.SUCCESS.value and properties:
            for prop_name in properties:
                # Get both with and without units
                prop_status, prop_value = self.get_device_property(actual_id, prop_name, include_units=True)
                prop_num_status, prop_num_value = self.get_device_property(actual_id, prop_name, include_units=False)
                
                device_info['properties'][prop_name] = {
                    'value_with_units': prop_value if prop_status == AutoExplorStatus.SUCCESS.value else None,
                    'numeric_value': prop_num_value if prop_num_status == AutoExplorStatus.SUCCESS.value else None,
                    'raw_property_name': prop_name
                }

        return device_info

    def get_all_device_info(self, device_mask=None):
        """Get complete information for all configured devices.
        
        Args:
            device_mask: Optional bitmask, if None will query current config
            
        Returns:
            dict: Device info with device names as keys and their data as values
        """
        if device_mask is None:
            _, device_mask = self.get_device_configuration()
        
        if device_mask is None:
            return {}
        
        device_info = {}
        for device_enum in DeviceID:
            if device_enum & device_mask:
                info = self.get_device_info(device_enum)
                device_info[device_enum.name] = info
        
        return device_info

    def get_system_status_summary(self):
        """Get a summary of key system status information.
        
        Returns:
            dict: Summary of system status including devices, readouts, and buttons
        """
        summary = {
            'devices': {},
            'readouts': {},
            'buttons': {},
            'timestamp': None
        }
        
        try:
            # Get key device states
            device_info = self.get_all_device_info()
            for name, info in device_info.items():
                summary['devices'][name] = {
                    'name': info['name'],
                    'state': info['state'],
                    'key_properties': {}
                }
                
                # Extract some key properties
                for prop_name, prop_data in info['properties'].items():
                    if any(keyword in prop_name.lower() for keyword in ['temp', 'current', 'pressure', 'voltage']):
                        summary['devices'][name]['key_properties'][prop_name] = prop_data['value_with_units']

            # Get temperature readings
            temp_readings = self.get_temperature_readings()
            summary['readouts']['temperatures'] = temp_readings

            # Get pressure readings  
            pressure_readings = self.get_pressure_readings()
            summary['readouts']['pressures'] = pressure_readings

            # Get button states for key buttons
            key_buttons = [ButtonID.POWER, ButtonID.HIGH_VAC, ButtonID.VENT, ButtonID.ROUGH]
            for button in key_buttons:
                try:
                    status, state_info = self.get_button_state(button)
                    if status == AutoExplorStatus.SUCCESS.value and state_info:
                        summary['buttons'][button.name] = state_info
                except:
                    continue

        except Exception as e:
            summary['error'] = str(e)

        return summary

    # --- Setpoint Control Methods ---
    def get_setpoint_name(self, setpoint_id):
        """Get the friendly name for a setpoint.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            
        Returns:
            tuple: (status_code, setpoint_name)
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"GetSetpointName {setpoint_id}"
        return self.send_custom_command(command)

    def get_setpoint_native_unit(self, setpoint_id):
        """Get the native unit for a setpoint (e.g., Torr, °C).
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            
        Returns:
            tuple: (status_code, unit_string)
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"GetSetpointNativeUnit {setpoint_id}"
        return self.send_custom_command(command)

    def get_setpoint_is_in_altitude_mode_state(self, setpoint_id):
        """Get if the setpoint is in altitude mode.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            
        Returns:
            tuple: (status_code, is_altitude_mode) where is_altitude_mode is True/False or None
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"GetSetpointIsInAltitudeModeState {setpoint_id}"
        status_code, payload = self.send_custom_command(command)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            try:
                is_altitude = bool(int(payload.strip()))
                return status_code, is_altitude
            except ValueError:
                return status_code, None
        
        return status_code, None

    def get_setpoint_can_do_altitude(self, setpoint_id):
        """Get if the setpoint can be put into altitude mode.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            
        Returns:
            tuple: (status_code, can_do_altitude) where can_do_altitude is True/False or None
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"GetSetpointCanDoAltitude {setpoint_id}"
        status_code, payload = self.send_custom_command(command)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            try:
                can_do_altitude = bool(int(payload.strip()))
                return status_code, can_do_altitude
            except ValueError:
                return status_code, None
        
        return status_code, None

    def get_setpoint_state(self, setpoint_id):
        """Get the state and color status of a setpoint.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            
        Returns:
            tuple: (status_code, response_dict) where response_dict contains:
                   {'on_off': bool, 'color_state': int, 'color_description': str, 'raw_response': str}
                   Returns None as response_dict if parsing fails.
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"GetSetpointState {setpoint_id}"
        status_code, payload = self.send_custom_command(command)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            try:
                parts = payload.strip().split()
                if len(parts) >= 2:
                    on_off = bool(int(parts[0]))
                    color_state = int(parts[1])
                    color_description = get_color_state_description(color_state)
                    return status_code, {
                        'on_off': on_off,
                        'color_state': color_state,
                        'color_description': color_description,
                        'raw_response': payload
                    }
                else:
                    return status_code, None
            except (ValueError, IndexError):
                return status_code, None
        
        return status_code, None

    def get_setpoint_process_value(self, setpoint_id):
        """Get the current sensor value that the setpoint controller is monitoring.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            
        Returns:
            tuple: (status_code, process_value) where process_value is float or None
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"GetSetpointProcessValue {setpoint_id}"
        status_code, payload = self.send_custom_command(command)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            try:
                value = float(payload.strip())
                return status_code, value
            except ValueError:
                return status_code, None
        
        return status_code, None

    def get_setpoint_target_value(self, setpoint_id):
        """Get the setpoint target value.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            
        Returns:
            tuple: (status_code, target_value) where target_value is float or None
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"GetSetpointTargetValue {setpoint_id}"
        status_code, payload = self.send_custom_command(command)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            try:
                value = float(payload.strip())
                return status_code, value
            except ValueError:
                return status_code, None
        
        return status_code, None

    def get_setpoint_ttv(self, setpoint_id):
        """Get the Transient Target Value (TTV) of the setpoint.
        
        The TTV is the value the ExploraVac is attempting to reach at any given moment.
        When ramping, this differs from the target value.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            
        Returns:
            tuple: (status_code, ttv_value) where ttv_value is float or None
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"GetSetpointTTV {setpoint_id}"
        status_code, payload = self.send_custom_command(command)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            try:
                value = float(payload.strip())
                return status_code, value
            except ValueError:
                return status_code, None
        
        return status_code, None

    def get_setpoint_ramp_value(self, setpoint_id):
        """Get the ramp rate of the setpoint controller.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            
        Returns:
            tuple: (status_code, ramp_value) where ramp_value is float or None
                   0 = Max Ramp Rate
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"GetSetpointRampValue {setpoint_id}"
        status_code, payload = self.send_custom_command(command)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            try:
                value = float(payload.strip())
                return status_code, value
            except ValueError:
                return status_code, None
        
        return status_code, None

    def get_setpoint_soak_value(self, setpoint_id):
        """Get the soak duration of the setpoint controller.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            
        Returns:
            tuple: (status_code, soak_value) where soak_value is float or None
                   0 = No soak, value in seconds
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"GetSetpointSoakValue {setpoint_id}"
        status_code, payload = self.send_custom_command(command)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            try:
                value = float(payload.strip())
                return status_code, value
            except ValueError:
                return status_code, None
        
        return status_code, None

    def get_setpoint_mode_options(self, setpoint_id):
        """Get available operating modes for the setpoint controller.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            
        Returns:
            tuple: (status_code, mode_list) where mode_list is list of available modes
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"GetSetpointModeOptions {setpoint_id}"
        status_code, payload = self.send_custom_command(command)
        
        if status_code == AutoExplorStatus.SUCCESS.value and payload:
            if payload.strip():
                # Parse comma-delimited modes
                modes = [mode.strip() for mode in payload.split(',')]
                # Remove empty strings
                modes = [mode for mode in modes if mode]
                return status_code, modes
            else:
                return status_code, []
        
        return status_code, []

    def get_setpoint_mode(self, setpoint_id):
        """Get the current operating mode of the setpoint controller.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            
        Returns:
            tuple: (status_code, current_mode) where current_mode is string or None
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"GetSetpointMode {setpoint_id}"
        return self.send_custom_command(command)

    # --- Setpoint Control (Set) Methods ---
    def set_setpoint_target_value(self, setpoint_id, value, from_value=None):
        """Set the setpoint target value.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            value: Target value to ramp to
            from_value: Optional starting value for ramp (if None, ramps from current value)
            
        Returns:
            tuple: (status_code, payload)
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        if from_value is not None:
            command = f"SetSetpointTargetValue {setpoint_id} {value} {from_value}"
        else:
            command = f"SetSetpointTargetValue {setpoint_id} {value}"
        
        return self.send_custom_command(command)

    def set_setpoint_ramp(self, setpoint_id, ramp_rate):
        """Set the setpoint ramp rate.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            ramp_rate: Ramp rate in native units per minute (0 = max ramp rate)
            
        Returns:
            tuple: (status_code, payload)
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"SetSetpointRamp {setpoint_id} {ramp_rate}"
        return self.send_custom_command(command)

    def set_setpoint_soak(self, setpoint_id, soak_seconds):
        """Set the setpoint soak duration.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            soak_seconds: Soak duration in whole seconds (0 = no soak)
            
        Returns:
            tuple: (status_code, payload)
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"SetSetpointSoak {setpoint_id} {soak_seconds}"
        return self.send_custom_command(command)

    def set_setpoint_altitude_mode(self, setpoint_id, altitude_mode):
        """Set the setpoint altitude mode state.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            altitude_mode: True for altitude mode (ft.), False for standard mode (Torr)
            
        Returns:
            tuple: (status_code, payload)
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        mode_value = 1 if altitude_mode else 0
        command = f"SetSetpointIsInAltitudeModeState {setpoint_id} {mode_value}"
        return self.send_custom_command(command)

    def set_setpoint_state(self, setpoint_id, on_off):
        """Set the state of a setpoint controller.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            on_off: True/1 for On, False/0 for Off
            
        Returns:
            tuple: (status_code, payload)
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        state_value = 1 if on_off else 0
        command = f"SetSetpointState {setpoint_id} {state_value}"
        return self.send_custom_command(command)

    def set_setpoint_mode(self, setpoint_id, mode):
        """Set the operating mode of a setpoint controller.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            mode: Operating mode string (e.g., "vent", "purge", "actprg")
            
        Returns:
            tuple: (status_code, payload)
        """
        if hasattr(setpoint_id, 'value'):
            setpoint_id = setpoint_id.value
        
        command = f"SetSetpointMode {setpoint_id} {mode}"
        return self.send_custom_command(command)

    def get_setpoint_info(self, setpoint_id):
        """Get complete information for a setpoint controller.
        
        Args:
            setpoint_id: Setpoint identifier (int or SetpointID enum member)
            
        Returns:
            dict: Complete setpoint information
        """
        if hasattr(setpoint_id, 'value'):
            actual_id = setpoint_id.value
            enum_name = setpoint_id.name
        else:
            actual_id = setpoint_id
            # Try to find enum name
            enum_name = None
            for member in SetpointID:
                if member.value == setpoint_id:
                    enum_name = member.name
                    break
            if enum_name is None:
                enum_name = f"SETPOINT_{setpoint_id}"

        # Get all setpoint information
        name_status, name = self.get_setpoint_name(actual_id)
        unit_status, unit = self.get_setpoint_native_unit(actual_id)
        state_status, state_info = self.get_setpoint_state(actual_id)
        process_status, process_value = self.get_setpoint_process_value(actual_id)
        target_status, target_value = self.get_setpoint_target_value(actual_id)
        ttv_status, ttv_value = self.get_setpoint_ttv(actual_id)
        ramp_status, ramp_value = self.get_setpoint_ramp_value(actual_id)
        soak_status, soak_value = self.get_setpoint_soak_value(actual_id)
        altitude_status, altitude_mode = self.get_setpoint_is_in_altitude_mode_state(actual_id)
        can_altitude_status, can_altitude = self.get_setpoint_can_do_altitude(actual_id)
        mode_options_status, mode_options = self.get_setpoint_mode_options(actual_id)
        mode_status, current_mode = self.get_setpoint_mode(actual_id)

        setpoint_info = {
            'id': actual_id,
            'enum_name': enum_name,
            'name': name if name_status == AutoExplorStatus.SUCCESS.value else 'Unknown',
            'unit': unit if unit_status == AutoExplorStatus.SUCCESS.value else 'Unknown',
            'state': state_info if state_status == AutoExplorStatus.SUCCESS.value else None,
            'process_value': process_value if process_status == AutoExplorStatus.SUCCESS.value else None,
            'target_value': target_value if target_status == AutoExplorStatus.SUCCESS.value else None,
            'ttv_value': ttv_value if ttv_status == AutoExplorStatus.SUCCESS.value else None,
            'ramp_rate': ramp_value if ramp_status == AutoExplorStatus.SUCCESS.value else None,
            'soak_duration': soak_value if soak_status == AutoExplorStatus.SUCCESS.value else None,
            'altitude_mode': altitude_mode if altitude_status == AutoExplorStatus.SUCCESS.value else None,
            'can_do_altitude': can_altitude if can_altitude_status == AutoExplorStatus.SUCCESS.value else None,
            'available_modes': mode_options if mode_options_status == AutoExplorStatus.SUCCESS.value else [],
            'current_mode': current_mode if mode_status == AutoExplorStatus.SUCCESS.value else None,
            'is_ramping': None,  # Will be calculated below
            'formatted_values': {}
        }

        # Calculate if currently ramping
        if (setpoint_info['target_value'] is not None and 
            setpoint_info['ttv_value'] is not None):
            setpoint_info['is_ramping'] = abs(setpoint_info['target_value'] - setpoint_info['ttv_value']) > 0.001

        # Create formatted value strings
        unit_str = setpoint_info['unit'] if setpoint_info['unit'] != 'Unknown' else ''
        if setpoint_info['process_value'] is not None:
            setpoint_info['formatted_values']['process'] = f"{setpoint_info['process_value']:.2f} {unit_str}".strip()
        if setpoint_info['target_value'] is not None:
            setpoint_info['formatted_values']['target'] = f"{setpoint_info['target_value']:.2f} {unit_str}".strip()
        if setpoint_info['ttv_value'] is not None:
            setpoint_info['formatted_values']['ttv'] = f"{setpoint_info['ttv_value']:.2f} {unit_str}".strip()

        return setpoint_info

    def get_all_setpoint_info(self, setpoint_mask=None):
        """Get complete information for all configured setpoints.
        
        Args:
            setpoint_mask: Optional bitmask, if None will query current config
            
        Returns:
            dict: Setpoint info with setpoint names as keys and their data as values
        """
        if setpoint_mask is None:
            _, setpoint_mask = self.get_setpoint_configuration()
        
        if setpoint_mask is None:
            return {}
        
        setpoint_info = {}
        for setpoint_enum in SetpointID:
            if setpoint_enum & setpoint_mask:
                info = self.get_setpoint_info(setpoint_enum)
                setpoint_info[setpoint_enum.name] = info
        
        return setpoint_info

    def __del__(self):
        self.client.disconnect()

if __name__ == "__main__":
    auto_explor = AutoExplor('192.168.20.12')
    auto_explor.client.run_discovery_scan()
    auto_explor.request_control()
    res = auto_explor.get_temperature_readings()
    print("Temperature Readings:")
    for name, info in res.items():
        print(f"  {name}: {info['formatted_value']}")  

    # Get device info
    device_info = auto_explor.get_all_device_info()
    print("\nDevice Information:")
    for name, info in device_info.items():
        print(f"  {name}: State={info['state']}, Name={info['name']}")
        for prop_name, prop_data in info['properties'].items():
            print(f"    {prop_name}: {prop_data['value_with_units']}")

    pressure_info = auto_explor.get_setpoint_info(SetpointID.PRESSURE_CONTROL)
    print("\nPressure Setpoint Information:")
    for key, value in pressure_info['formatted_values'].items():
        print(f"  {key}: {value}")

    temp_info = auto_explor.get_setpoint_info(SetpointID.PLATEN_HEATING_CONTROL)
    print("\nPlaten Heating Setpoint Information:")
    for key, value in temp_info['formatted_values'].items():
        print(f"  {key}: {value}")
    
    auto_explor.set_setpoint_target_value(SetpointID.PLATEN_HEATING_CONTROL, 37.0)
    auto_explor.set_setpoint_ramp(SetpointID.PLATEN_HEATING_CONTROL, 4.0)
    auto_explor.set_setpoint_state(SetpointID.PLATEN_HEATING_CONTROL, True)
    temp_target = auto_explor.get_setpoint_target_value(SetpointID.PLATEN_HEATING_CONTROL)
    temp_mode = auto_explor.get_setpoint_mode(SetpointID.PLATEN_HEATING_CONTROL)
    print(f"\nSet Platen Heating Target to {temp_target[1]} and Mode to {temp_mode[1]}")

    process_value = auto_explor.get_setpoint_process_value(SetpointID.PLATEN_HEATING_CONTROL)
    print(f"Current Platen Heating Process Value: {process_value[1]}")
#     device_status, device_cfg = auto_explor.get_device_configuration()
#     print("DeviceConfiguration status:", device_status)
#     print("DeviceConfiguration:", device_cfg)
    
#     device_mask = auto_explor.extract_device_mask(device_cfg)
#     if device_mask is not None:
#         print("DeviceIDs present:", decode_device_mask(device_mask))
    
#     readout_status, readout_cfg = auto_explor.get_readout_configuration()
#     print("ReadoutConfiguration status:", readout_status)
#     print("ReadoutConfiguration:", readout_cfg)
    
#     readout_mask = auto_explor.extract_readout_mask(readout_cfg)
#     if readout_mask is not None:
#         print("ReadoutIDs present:", decode_readout_mask(readout_mask))
    
#     button_status, button_cfg = auto_explor.get_button_configuration()
#     print("ButtonConfiguration status:", button_status)
#     print("ButtonConfiguration:", button_cfg)
    
#     button_mask = auto_explor.extract_button_mask(button_cfg)
#     if button_mask is not None:
#         print("ButtonIDs present:", decode_button_mask(button_mask))
    
#     setpoint_status, setpoint_cfg = auto_explor.get_setpoint_configuration()
#     print("SetpointConfiguration status:", setpoint_status)
#     print("SetpointConfiguration:", setpoint_cfg)
    
#     setpoint_mask = auto_explor.extract_setpoint_mask(setpoint_cfg)
#     if setpoint_mask is not None:
#         print("SetpointIDs present:", decode_setpoint_mask(setpoint_mask))