#!/usr/bin/env python3
"""
Test runner for Lynx Thermal Cycle system with simulated DAQ.
This script allows you to run thermal cycle tests using simulated instruments.
"""

import sys
import os
import time
import datetime
import traceback

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.lynx_thermal_cycle import LynxThermalCycleManager
from instruments.hardware_config import print_hardware_status, get_hardware_status
from src.utils.logging_utils import log_message

class ThermalCycleTestRunner:
    """Test runner for thermal cycle tests with simulated instruments."""
    
    def __init__(self, simulation_mode=True):
        """
        Initialize the test runner.
        
        Args:
            simulation_mode (bool): Whether to use simulated instruments
        """
        self.simulation_mode = simulation_mode
        self.thermal_manager = None
        
        print("=" * 60)
        print("   Lynx Thermal Cycle Test Runner")
        print("=" * 60)
        
        # Show hardware configuration
        print_hardware_status()
        print()

    def initialize_system(self):
        """Initialize the thermal cycle system."""
        print("Initializing thermal cycle system...")
        
        try:
            # Initialize the thermal cycle manager
            self.thermal_manager = LynxThermalCycleManager(simulation_mode=self.simulation_mode)
            
            # Verify DAQ is available
            if hasattr(self.thermal_manager.test_manager, 'daq') and self.thermal_manager.test_manager.daq:
                print("✓ DAQ initialized successfully")
                
                # Test basic DAQ functionality
                if hasattr(self.thermal_manager.test_manager.daq, 'read_status_return'):
                    status = self.thermal_manager.test_manager.daq.read_status_return()
                    rf_status, fault_status, band, gain, timestamp, temp = status
                    print(f"✓ DAQ Status: RF={rf_status}, Band={band}, Gain={gain}dB, Temp={temp:.1f}°C")
                    
                    if fault_status != "No Faults":
                        print(f"⚠ DAQ Fault Detected: {fault_status}")
                else:
                    print("⚠ DAQ doesn't have expected interface")
            else:
                print("✗ DAQ not available")
                
            print("✓ System initialization complete")
            return True
            
        except Exception as e:
            print(f"✗ System initialization failed: {e}")
            traceback.print_exc()
            return False

    def run_basic_daq_test(self):
        """Run a basic DAQ functionality test."""
        print("\n" + "=" * 50)
        print("   Basic DAQ Functionality Test")
        print("=" * 50)
        
        if not self.thermal_manager or not hasattr(self.thermal_manager.test_manager, 'daq'):
            print("✗ DAQ not available for testing")
            return False
            
        daq = self.thermal_manager.test_manager.daq
        
        try:
            # Test 1: Read initial status
            print("\n1. Reading initial DAQ status...")
            rf_status, fault_status, band, gain, timestamp, temp = daq.read_status_return()
            print(f"   RF: {rf_status}, Band: {band}, Gain: {gain}dB")
            print(f"   Temperature: {temp:.1f}°C, Faults: {fault_status}")
            
            # Test 2: RF control
            print("\n2. Testing RF control...")
            print("   Enabling RF...")
            result = daq.enable_rf()
            print(f"   Result: {result}")
            
            time.sleep(0.5)
            
            print("   Reading status after RF enable...")
            rf_status, _, _, _, _, _ = daq.read_status_return()
            print(f"   RF Status: {rf_status}")
            
            print("   Disabling RF...")
            daq.disable_rf()
            time.sleep(0.5)
            
            rf_status, _, _, _, _, _ = daq.read_status_return()
            print(f"   RF Status after disable: {rf_status}")
            
            # Test 3: Band control
            print("\n3. Testing band control...")
            test_bands = ["L", "M", "H", "NONE"]
            for test_band in test_bands:
                print(f"   Setting band to {test_band}...")
                result = daq.set_band(test_band)
                print(f"   Result: {result}")
                
                _, _, current_band, _, _, _ = daq.read_status_return()
                print(f"   Current band: {current_band}")
                time.sleep(0.3)
            
            # Test 4: Gain control
            print("\n4. Testing gain control...")
            test_gains = [15, 25, 35, 20]  # Return to 20dB
            for test_gain in test_gains:
                print(f"   Setting gain to {test_gain}dB...")
                result = daq.change_gain(test_gain)
                print(f"   Result: {result}")
                
                _, _, _, current_gain, _, _ = daq.read_status_return()
                print(f"   Current gain: {current_gain}dB")
                time.sleep(0.3)
            
            print("\n✓ Basic DAQ test completed successfully")
            return True
            
        except Exception as e:
            print(f"\n✗ Basic DAQ test failed: {e}")
            traceback.print_exc()
            return False

    def run_temperature_monitoring_test(self):
        """Run a temperature monitoring test."""
        print("\n" + "=" * 50)
        print("   Temperature Monitoring Test")
        print("=" * 50)
        
        if not self.thermal_manager or not hasattr(self.thermal_manager.test_manager, 'daq'):
            print("✗ DAQ not available for temperature monitoring")
            return False
            
        daq = self.thermal_manager.test_manager.daq
        
        try:
            print("\nMonitoring temperature for 30 seconds...")
            print("Time     | Temperature | RF | Band | Gain | Faults")
            print("---------|-------------|----| -----|------|--------")
            
            start_time = time.time()
            readings = 0
            
            while time.time() - start_time < 30:  # Run for 30 seconds
                rf_status, fault_status, band, gain, timestamp, temp = daq.read_status_return()
                
                time_str = timestamp.strftime("%H:%M:%S")
                fault_short = fault_status[:8] + "..." if len(fault_status) > 8 else fault_status
                
                print(f"{time_str} | {temp:>10.1f}°C | {rf_status:>2} | {band:>4} | {gain:>2}dB | {fault_short}")
                
                readings += 1
                time.sleep(2)  # Read every 2 seconds
            
            print(f"\n✓ Temperature monitoring completed ({readings} readings)")
            return True
            
        except Exception as e:
            print(f"\n✗ Temperature monitoring failed: {e}")
            traceback.print_exc()
            return False

    def run_thermal_cycle_simulation(self):
        """Run a simulated thermal cycle test."""
        print("\n" + "=" * 50)
        print("   Thermal Cycle Simulation Test")
        print("=" * 50)
        
        if not self.simulation_mode:
            print("⚠ Thermal cycle simulation only available in simulation mode")
            return False
            
        if not self.thermal_manager or not hasattr(self.thermal_manager.test_manager, 'daq'):
            print("✗ DAQ not available for thermal cycle simulation")
            return False
            
        daq = self.thermal_manager.test_manager.daq
        
        # Check if we have simulation-specific features
        if not hasattr(daq, 'set_base_temperature'):
            print("✗ DAQ doesn't support thermal simulation features")
            return False
            
        try:
            print("\nSimulating thermal cycle: 25°C → 85°C → -40°C → 25°C")
            
            # Define thermal cycle points
            thermal_points = [
                (25.0, "Room Temperature"),
                (50.0, "Warming Up"),
                (75.0, "High Temperature Approach"),
                (85.0, "Maximum Temperature"),
                (60.0, "Cooling Down"),
                (25.0, "Room Temperature"),
                (0.0, "Cold Temperature Approach"),
                (-20.0, "Low Temperature"),
                (-40.0, "Minimum Temperature"),
                (-20.0, "Warming From Cold"),
                (0.0, "Approaching Room Temp"),
                (25.0, "Final Room Temperature")
            ]
            
            print("\nTemp Target | Measured   | Description           | RF | Band | Gain")
            print("------------|------------|---------------------- |----| -----|-----")
            
            for target_temp, description in thermal_points:
                # Set target temperature
                daq.set_base_temperature(target_temp)
                time.sleep(1)  # Allow temperature to "settle"
                
                # Read current status
                rf_status, fault_status, band, gain, timestamp, measured_temp = daq.read_status_return()
                
                print(f"{target_temp:>10.1f}°C | {measured_temp:>9.1f}°C | {description:<20} | {rf_status:>2} | {band:>4} | {gain:>2}dB")
                
                # Check for faults during thermal cycling
                if fault_status != "No Faults":
                    print(f"    ⚠ Fault detected: {fault_status}")
                
                time.sleep(1)
            
            print("\n✓ Thermal cycle simulation completed successfully")
            return True
            
        except Exception as e:
            print(f"\n✗ Thermal cycle simulation failed: {e}")
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """Run all available tests."""
        print("\n" + "=" * 60)
        print("   Running All Tests")
        print("=" * 60)
        
        if not self.initialize_system():
            print("✗ System initialization failed - cannot run tests")
            return False
        
        test_results = []
        
        # Run basic DAQ test
        test_results.append(("Basic DAQ Test", self.run_basic_daq_test()))
        
        # Run temperature monitoring test
        test_results.append(("Temperature Monitoring", self.run_temperature_monitoring_test()))
        
        # Run thermal cycle simulation (only in simulation mode)
        if self.simulation_mode:
            test_results.append(("Thermal Cycle Simulation", self.run_thermal_cycle_simulation()))
        
        # Print test summary
        print("\n" + "=" * 60)
        print("   Test Summary")
        print("=" * 60)
        
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "PASS" if result else "FAIL"
            print(f"{test_name:<30}: {status}")
            if result:
                passed += 1
        
        print(f"\nOverall Result: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! The system is ready for thermal cycling.")
        else:
            print("⚠ Some tests failed. Please check the errors above.")
        
        return passed == total

def main():
    """Main function to run the test suite."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Lynx Thermal Cycle Test Runner')
    parser.add_argument('--real-hardware', action='store_true', 
                       help='Use real hardware instead of simulation')
    parser.add_argument('--test', choices=['basic', 'temp', 'thermal', 'all'], 
                       default='all', help='Which test to run')
    
    args = parser.parse_args()
    
    # Determine simulation mode
    simulation_mode = not args.real_hardware
    
    # Create test runner
    runner = ThermalCycleTestRunner(simulation_mode=simulation_mode)
    
    try:
        # Run requested test
        if args.test == 'all':
            success = runner.run_all_tests()
        elif args.test == 'basic':
            success = runner.initialize_system() and runner.run_basic_daq_test()
        elif args.test == 'temp':
            success = runner.initialize_system() and runner.run_temperature_monitoring_test()
        elif args.test == 'thermal':
            success = runner.initialize_system() and runner.run_thermal_cycle_simulation()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
