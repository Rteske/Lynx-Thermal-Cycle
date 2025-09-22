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
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.connect((self.ip, self.port))
                self.socket.settimeout(5)

    def disconnect(self):
        with self.lock:
            if self.socket:
                self.socket.close()
                self.socket = None

    def send(self, message):
        with self.lock:
            if self.socket:
                self.socket.sendall(message.encode("utf-8"))

    def receive(self, buffer_size=1024):
        with self.lock:
            if self.socket:
                return self.socket.recv(buffer_size).decode("utf-8")
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

from enum import Enum
class AutoExplorStatus(Enum):
    SUCCESS = 0

class AutoExplor:
    def __init__(self, ip, main_port=23513, discovery_port=23514):
        self.client = IPClient(ip, main_port)
        self.discovery_port = discovery_port
        self.machine_id = None
        # data = self.client.run_discovery_scan()
        # if data:
        #     data = data.decode("utf-8").strip()
        #     self.machine_id = data.split(" ")[1]

        self.client.connect()

        self.request_control()

    def request_control(self):
        self.client.send("RequestControl")
        response = self.client.receive(1024)
        status, response = self.parse_message(response)
        return AutoExplorStatus[status]

    def parse_message(self, message):
        status, response = message.split(":")
        return int(status), response

    def query_subsystem_config(self, subsystem):
        msg = f"Get{subsystem}Configuration"
        self.client.send(msg)
        response = self.client.receive(1024)
        status, response = self.parse_message(response)
        return status, response

    def send_custom_command(self, command):
        """Send a custom command to the AutoExplor device"""
        self.client.send(command)
        response = self.client.receive(1024)
        try:
            status, response = self.parse_message(response)
            return status, response
        except ValueError:
            # If response doesn't follow status:response format
            return None, response

    def __del__(self):
        self.client.disconnect()

from tvac_auto_explor import AutoExplor

# Create instance and use
auto_explor = AutoExplor('192.168.20.12')

status, config = auto_explor.query_subsystem_config("Device")