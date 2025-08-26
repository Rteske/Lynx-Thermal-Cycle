"""
Example integration of simulated DAQ with the Lynx Thermal Cycle system.
This shows how to use the simulated DAQ in place of real hardware.
"""

import time
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instruments.hardware_config import get_daq_instance, print_hardware_status, set_simulation_mode

class LynxDAQIntegrationExample:
    """
    Example class showing how to integrate the simulated DAQ
    with the existing Lynx Thermal Cycle system.
    """
    
    def __init__(self, use_simulation=True):
        """
        Initialize the DAQ integration.
        
        Args:
            use_simulation (bool): Whether to use simulated or real hardware
        """
        print("=== Lynx DAQ Integration Example ===")
        
        # Set simulation mode
        set_simulation_mode(use_simulation)
        print_hardware_status()
        
        # Get DAQ instance (real or simulated based on configuration)
        print("\nInitializing DAQ...")
        self.daq = get_daq_instance()
        
        # Verify DAQ is working
        print("Verifying DAQ connection...")
        try:
            status = self.daq.read_status_return()
            print(f"✓ DAQ connection verified")
        except Exception as e:
            print(f"✗ DAQ connection failed: {e}")
            raise
    
    def run_test_sequence(self):
        """Run a comprehensive test sequence on the DAQ."""
        print("\n=== Running Test Sequence ===")
        
        # Test 1: Basic status reading
        print("\n1. Reading initial status...")
        rf_status, fault_status, band, gain, timestamp, temp = self.daq.read_status_return()
        print(f"   RF: {rf_status}, Band: {band}, Gain: {gain}dB, Temp: {temp:.1f}°C")
        
        # Test 2: RF Control
        print("\n2. Testing RF control...")
        print("   Enabling RF...")
        result = self.daq.enable_rf()
        print(f"   Result: {result}")
        
        time.sleep(0.5)
        
        print("   Disabling RF...")
        self.daq.disable_rf()
        
        # Test 3: Band switching
        print("\n3. Testing band control...")
        bands_to_test = ["L", "M", "H", "NONE"]
        for band in bands_to_test:
            print(f"   Setting band to {band}...")
            result = self.daq.set_band(band)
            print(f"   Result: {result}")
            time.sleep(0.3)
        
        # Test 4: Gain control
        print("\n4. Testing gain control...")
        gains_to_test = [15, 25, 35, 20]  # Return to 20dB at end
        for gain in gains_to_test:
            print(f"   Setting gain to {gain}dB...")
            result = self.daq.change_gain(gain)
            print(f"   Result: {result}")
            time.sleep(0.3)
        
        # Test 5: Continuous monitoring
        print("\n5. Continuous monitoring (10 readings)...")
        print("   Time     | RF | Band | Gain | Temp  | Faults")
        print("   ---------|----| -----|------|-------|--------")
        
        for i in range(10):
            rf_status, fault_status, band, gain, timestamp, temp = self.daq.read_status_return()
            time_str = timestamp.strftime("%H:%M:%S")
            print(f"   {time_str} | {rf_status:>2} | {band:>4} | {gain:>2}dB | {temp:>5.1f}°C | {fault_status}")
            time.sleep(0.5)
        
        print("\n=== Test Sequence Complete ===")
    
    def demonstrate_fault_injection(self):
        """Demonstrate fault injection capabilities (simulated DAQ only)."""
        if hasattr(self.daq, 'inject_fault'):
            print("\n=== Fault Injection Demo ===")
            print("(This feature is only available with simulated DAQ)")
            
            # Test different fault types
            faults_to_test = [
                "Fault_+5V_Reg_Band_3",
                "Fault_+8V_Reg_Band_2", 
                "Fault_-5V_Reg",
                "No Faults"  # Clear faults
            ]
            
            for fault in faults_to_test:
                print(f"\nInjecting fault: {fault}")
                self.daq.inject_fault(fault)
                
                # Read status to see the fault
                rf_status, fault_status, band, gain, timestamp, temp = self.daq.read_status_return()
                print(f"Current fault status: {fault_status}")
                time.sleep(1)
        else:
            print("\n=== Fault Injection Not Available ===")
            print("(Fault injection is only available with simulated DAQ)")
    
    def thermal_cycle_simulation(self):
        """Simulate a thermal cycling scenario."""
        if hasattr(self.daq, 'set_base_temperature'):
            print("\n=== Thermal Cycle Simulation ===")
            print("Simulating temperature changes during thermal cycling...")
            
            # Simulate temperature cycle: 25°C -> 85°C -> -40°C -> 25°C
            temp_points = [25.0, 40.0, 60.0, 85.0, 70.0, 50.0, 25.0, 10.0, -20.0, -40.0, -20.0, 0.0, 25.0]
            
            print("\nTemperature Cycle Progress:")
            print("Target Temp | Measured Temp | RF | Band | Gain")
            print("------------|---------------|----| -----|-----")
            
            for target_temp in temp_points:
                # Set the target temperature for simulation
                self.daq.set_base_temperature(target_temp)
                
                # Read actual temperature (will have some variation)
                rf_status, fault_status, band, gain, timestamp, measured_temp = self.daq.read_status_return()
                
                print(f"{target_temp:>10.1f}°C | {measured_temp:>12.1f}°C | {rf_status:>2} | {band:>4} | {gain:>2}dB")
                time.sleep(0.5)
            
            print("\nThermal cycle simulation complete.")
        else:
            print("\n=== Thermal Cycle Simulation Not Available ===")
            print("(Temperature control is only available with simulated DAQ)")

def main():
    """Main demonstration function."""
    try:
        # Create the integration example with simulation enabled
        integration = LynxDAQIntegrationExample(use_simulation=True)
        
        # Run comprehensive tests
        integration.run_test_sequence()
        
        # Demonstrate fault injection
        integration.demonstrate_fault_injection()
        
        # Simulate thermal cycling
        integration.thermal_cycle_simulation()
        
        print("\n=== Integration Example Complete ===")
        print("The simulated DAQ is ready for use in your thermal cycle tests!")
        
    except Exception as e:
        print(f"\nError during integration example: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
