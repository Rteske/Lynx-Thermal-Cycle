"""
Hardware configuration for Lynx Thermal Cycle system.
This file controls whether to use real hardware or simulated devices.
"""

# Global hardware simulation settings
SIMULATION_MODE = False  # Set to False to use real hardware

# Individual device simulation settings
SIMULATE_DAQ = False
SIMULATE_TEMP_CONTROLLER = False
SIMULATE_TEMP_PROBE = False
SIMULATE_POWER_SUPPLY = False
SIMULATE_SIGNAL_GENERATOR = False
SIMULATE_NETWORK_ANALYZER = False

# Hardware connection settings
DAQ_SETTINGS = {
    'real': {
        'port': 'COM4',
        'baudrate': 230400,
        'parity': 'EVEN',
        'stopbits': 1,
        'timeout': 1,
        'bytesize': 8
    },
    'simulated': {
        'port': 'SIMULATED_COM4',
        'response_delay': 0.005,  # seconds
        'fault_probability': 0.01,  # 1% chance of random faults
        'temp_variation': 2.0  # ±2°C temperature variation
    }
}

def get_daq_instance():
    """
    Factory function to get the appropriate DAQ instance based on configuration.
    
    Returns:
        DAQ instance (real or simulated)
    """
    if SIMULATION_MODE or SIMULATE_DAQ:
        from .simulated_daq import SimulatedRS422_DAQ
        return SimulatedRS422_DAQ()
    else:
        try:
            from .daq import RS422_DAQ
            return RS422_DAQ()
        except Exception as e:
            print(f"Failed to initialize real DAQ, falling back to simulation: {e}")
            from .simulated_daq import SimulatedRS422_DAQ
            return SimulatedRS422_DAQ()

def set_simulation_mode(enable_simulation=True):
    """
    Enable or disable simulation mode globally.
    
    Args:
        enable_simulation (bool): True to enable simulation, False for real hardware
    """
    global SIMULATION_MODE
    SIMULATION_MODE = enable_simulation
    print(f"Simulation mode {'enabled' if enable_simulation else 'disabled'}")

def get_hardware_status():
    """
    Get the current hardware configuration status.
    
    Returns:
        dict: Current hardware configuration
    """
    return {
        'simulation_mode': SIMULATION_MODE,
        'daq': 'simulated' if (SIMULATION_MODE or SIMULATE_DAQ) else 'real',
        'temp_controller': 'simulated' if (SIMULATION_MODE or SIMULATE_TEMP_CONTROLLER) else 'real',
        'temp_probe': 'simulated' if (SIMULATION_MODE or SIMULATE_TEMP_PROBE) else 'real',
        'power_supply': 'simulated' if (SIMULATION_MODE or SIMULATE_POWER_SUPPLY) else 'real',
        'signal_generator': 'simulated' if (SIMULATION_MODE or SIMULATE_SIGNAL_GENERATOR) else 'real',
        'network_analyzer': 'simulated' if (SIMULATION_MODE or SIMULATE_NETWORK_ANALYZER) else 'real'
    }

def print_hardware_status():
    """Print the current hardware configuration in a readable format."""
    status = get_hardware_status()
    print("\n=== Hardware Configuration ===")
    print(f"Global Simulation Mode: {'ON' if status['simulation_mode'] else 'OFF'}")
    print("\nDevice Status:")
    for device, mode in status.items():
        if device != 'simulation_mode':
            print(f"  {device.replace('_', ' ').title()}: {mode.upper()}")
    print("=" * 31)

if __name__ == "__main__":
    # Demo the configuration system
    print_hardware_status()
    
    # Test DAQ creation
    print("\nTesting DAQ creation...")
    daq = get_daq_instance()
    
    # Test a simple operation
    if hasattr(daq, 'read_status_return'):
        status = daq.read_status_return()
        print(f"DAQ Status: {status}")
    
    print("\nConfiguration test complete.")
