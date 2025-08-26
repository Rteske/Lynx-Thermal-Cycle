# Simulated DAQ for Lynx Thermal Cycle System

This directory contains a complete simulation of the RS422 DAQ hardware, allowing development and testing without physical hardware.

## Files Overview

### Core Files
- **`simulated_daq.py`** - Main simulated DAQ implementation
- **`hardware_config.py`** - Configuration system for switching between real/simulated hardware
- **`daq.py`** - Original real hardware DAQ implementation

### Examples
- **`../examples/daq_integration_example.py`** - Comprehensive demo of simulated DAQ capabilities

## Quick Start

### 1. Basic Usage

```python
from instruments.simulated_daq import SimulatedRS422_DAQ

# Create simulated DAQ
daq = SimulatedRS422_DAQ()

# Use exactly like the real DAQ
status = daq.read_status_return()
daq.enable_rf()
daq.set_band("H")
daq.change_gain(25)
```

### 2. Using Configuration System

```python
from instruments.hardware_config import get_daq_instance, set_simulation_mode

# Enable simulation mode (default)
set_simulation_mode(True)

# Get DAQ instance (automatically simulated)
daq = get_daq_instance()

# Use normally
daq.enable_rf()
```

### 3. Switch to Real Hardware

```python
from instruments.hardware_config import set_simulation_mode, get_daq_instance

# Disable simulation mode
set_simulation_mode(False)

# Get real DAQ instance (if hardware available)
daq = get_daq_instance()
```

## Features

### ✅ Complete API Compatibility
- All methods from original `RS422_DAQ` class
- Same return values and behavior
- Drop-in replacement for real hardware

### ✅ Realistic Simulation
- **Temperature readings** with realistic variation (±2°C)
- **RF control** state tracking
- **Band switching** (L, M, H, NONE)
- **Gain control** (10-41 dB range)
- **Fault injection** for testing error conditions

### ✅ Enhanced Testing Features
- **Fault injection**: `daq.inject_fault("Fault_+5V_Reg_Band_3")`
- **Temperature control**: `daq.set_base_temperature(85.0)`
- **Random fault simulation** (1% chance per reading)
- **Communication delays** to simulate real hardware timing

### ✅ Development Benefits
- **No hardware required** for development
- **Consistent behavior** for automated testing
- **Controllable conditions** for edge case testing
- **Fast iteration** without physical setup

## API Reference

### Core Methods (Same as Real DAQ)

```python
# Status and monitoring
rf_status, fault_status, band, gain, timestamp, temp = daq.read_status_return()

# RF Control
result = daq.enable_rf()      # Returns "COMPLETE" or "INCOMPLETE"
daq.disable_rf()

# Band Control
result = daq.set_band("H")    # "L", "M", "H", "NONE"

# Gain Control
result = daq.change_gain(25)  # 10-41 dB range
```

### Simulation-Only Methods

```python
# Inject specific faults for testing
daq.inject_fault("Fault_+5V_Reg_Band_3")
daq.inject_fault("No Faults")  # Clear faults

# Control base temperature for thermal cycling simulation
daq.set_base_temperature(85.0)  # Set to 85°C
daq.set_base_temperature(-40.0) # Set to -40°C
```

## Configuration Options

Edit `hardware_config.py` to control simulation behavior:

```python
# Global settings
SIMULATION_MODE = True  # Master simulation switch
SIMULATE_DAQ = True     # DAQ-specific simulation

# Simulation parameters
DAQ_SETTINGS = {
    'simulated': {
        'response_delay': 0.005,     # Communication delay (seconds)
        'fault_probability': 0.01,   # Random fault chance (1%)
        'temp_variation': 2.0        # Temperature variation (±2°C)
    }
}
```

## Integration with Thermal Cycle System

The simulated DAQ integrates seamlessly with the existing thermal cycle system:

```python
# In your thermal cycle code, just use the configuration system
from instruments.hardware_config import get_daq_instance

class ThermalCycleManager:
    def __init__(self):
        # This will automatically use simulated or real DAQ based on config
        self.daq = get_daq_instance()
    
    def run_cycle(self):
        # Same code works for both real and simulated DAQ
        self.daq.enable_rf()
        self.daq.set_band("H")
        # ... rest of your cycle logic
```

## Testing and Validation

Run the comprehensive test suite:

```bash
# Run basic simulation demo
python -m instruments.simulated_daq

# Run configuration system test
python -m instruments.hardware_config

# Run full integration example
python examples/daq_integration_example.py
```

## Troubleshooting

### Import Issues
If you get import errors, ensure you're running from the project root:
```bash
cd /path/to/Lynx-Thermal-Cycle
python -m instruments.simulated_daq
```

### Missing Dependencies
Install required packages:
```bash
pip install pyserial  # For serial communication simulation
```

### Real Hardware Fallback
The system automatically falls back to simulation if real hardware isn't available:
- Missing hardware drivers
- COM port not available  
- Hardware connection failures

## Development Notes

### Adding New Simulated Instruments
Follow the same pattern used for the DAQ:

1. Create `simulated_[instrument].py` with same API as real instrument
2. Add configuration options to `hardware_config.py`
3. Add factory function: `get_[instrument]_instance()`
4. Create integration example

### Extending Simulation Features
The simulated DAQ can be extended with additional testing features:
- **Network communication simulation**
- **Timing-based failures**
- **Configuration file-based scenarios**
- **Test data playback**

## License & Support

This simulation framework is part of the Lynx Thermal Cycle project. 
For questions or issues, contact the development team.
