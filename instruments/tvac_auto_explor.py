import socket
import threading
from enum import Enum

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
            status, response = self.parse_message(response)
            return AutoExplorStatus(status) if status is not None else None
        return None

    def parse_message(self, message):
        if ":" in message:
            status, response = message.split(":", 1)
            return int(status), response
        return None, message

    def query_subsystem_config(self, subsystem):
        msg = f"Get{subsystem}Configuration\r\n"
        self.client.send(msg)
        response = self.client.receive(1024)
        status, response = self.parse_message(response)
        return status, response

    def send_custom_command(self, command):
        # Add line terminator if not present
        if not command.endswith('\r\n'):
            command += '\r\n'
        self.client.send(command)
        response = self.client.receive(1024)
        status, response = self.parse_message(response)
        return status, response

    def __del__(self):
        self.client.disconnect()


# Example usage
auto_explor = AutoExplor('192.168.20.12')
auto_explor.client.run_discovery_scan()
status, response = auto_explor.send_custom_command('GetDeviceConfiguration\r\n')
print(status, response)