import sys
import os
from src.utils.logging_utils import log_message
import json

class BaseTempStep:
    """Base class for all temperature test steps."""
    
    def __init__(
        self, step_name, temperature=0, target_temp_delta=0, temp_controller_offset=0,
        psat_tests=False, gain_tests=False, phase_tests=False,
        S22_tests=False, S11_tests=False, IP3_tests=False, noise_figure_tests=False, 
        pin_pout_tests=False, na_tests=False, temp_cycle_type="",
        total_time=0, actual_time=0, test_data_filepaths=None, time_per_path=0, log_filepath=None, 
        temp_change_time=0, voltage=0, current=0, settle_time=0, power_off_after=False,
        settlement_tolerance=0.6, settlement_window=300, monitoring_interval=3, initial_delay=60,
        description="", **kwargs
        ):
        """Initialize base temperature step with common parameters."""
        self.step_name = step_name
        self.temperature = temperature
        self.target_temp_delta = target_temp_delta
        self.temp_controller_offset = temp_controller_offset
        self.psat_tests = psat_tests
        self.gain_tests = gain_tests
        self.phase_tests = phase_tests
        self.S22_tests = S22_tests
        self.S11_tests = S11_tests
        self.IP3_tests = IP3_tests
        self.noise_figure_tests = noise_figure_tests
        self.pin_pout_tests = pin_pout_tests
        self.na_tests = na_tests
        self.temp_cycle_type = temp_cycle_type
        self.settle_time = settle_time
        self.total_time = total_time
        self.actual_time = actual_time
        self.temp_change_time = temp_change_time
        self.test_data_filepaths = test_data_filepaths if test_data_filepaths else []
        self.time_per_path = time_per_path
        self.log_filepath = log_filepath
        self.voltage = voltage
        self.current = current
        self.power_off_after = power_off_after
        self.description = description
        
        # Temperature settlement configuration
        self.settlement_tolerance = settlement_tolerance  # ±°C tight tolerance for settlement
        self.settlement_window = settlement_window        # seconds for settlement window
        self.monitoring_interval = monitoring_interval    # seconds between temperature checks
        self.initial_delay = initial_delay                # seconds to wait before starting settlement monitoring
        
        # Store any additional parameters
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def is_cycle_step(self):
        """Check if this is a cycle step that needs expansion."""
        return False
    
    def expand_cycles(self):
        """Base implementation - return self as single step."""
        return [self]
    
    def has_any_tests(self):
        """Check if any tests are enabled for this step."""
        return any([
            self.psat_tests, self.gain_tests, self.phase_tests,
            self.S22_tests, self.S11_tests, self.IP3_tests,
            self.noise_figure_tests, self.pin_pout_tests, self.na_tests
        ])
    
    def get_test_summary(self):
        """Get summary of enabled tests."""
        enabled_tests = []
        test_mapping = {
            'psat_tests': 'PSAT',
            'gain_tests': 'Gain',
            'phase_tests': 'Phase',
            'S22_tests': 'S22',
            'S11_tests': 'S11',
            'IP3_tests': 'IP3',
            'noise_figure_tests': 'Noise Figure',
            'pin_pout_tests': 'Pin-Pout',
            'na_tests': 'Network Analyzer'
        }
        
        for attr, name in test_mapping.items():
            if getattr(self, attr, False):
                enabled_tests.append(name)
        
        return enabled_tests
    
    def add_output_filepath(self, filepath):
        """Add output file path for the temperature step."""
        self.test_data_filepaths.append(filepath)

    def dump_to_json(self):
        """Dumps the temperature step data to a JSON string."""
        return json.dumps(self.__dict__, indent=4)

    def __repr__(self):
        return f"{self.__class__.__name__}(step_name='{self.step_name}', temperature={self.temperature}, temp_cycle_type='{self.temp_cycle_type}', voltage={self.voltage})"


class DwellStep(BaseTempStep):
    """Temperature step that dwells at a specific temperature for testing."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temp_cycle_type = "DWELL"


class RampStep(BaseTempStep):
    """Temperature step that ramps to a target temperature."""
    
    def __init__(self, ramp_rate=None, **kwargs):
        super().__init__(**kwargs)
        self.temp_cycle_type = "RAMP"
        self.ramp_rate = ramp_rate


class SoakStep(BaseTempStep):
    """Temperature step that soaks at temperature without active testing."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.temp_cycle_type = "SOAK"


class CycleStep(BaseTempStep):
    """Temperature step that cycles between high and low temperatures."""
    
    def __init__(
        self, cycle_count=None, ramp_rate=None, high_temp=None, low_temp=None,
        dwell_time_high=None, dwell_time_low=None, temp_controller_offset_high=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.temp_cycle_type = "CYCLE"
        self.cycle_count = cycle_count
        self.ramp_rate = ramp_rate
        self.high_temp = high_temp
        self.low_temp = low_temp
        self.dwell_time_high = dwell_time_high
        self.dwell_time_low = dwell_time_low
        self.temp_controller_offset_high = temp_controller_offset_high
    
    def is_cycle_step(self):
        """Check if this is a cycle step that needs expansion."""
        return True


class TempProfileManager:
    def __init__(self, temp_profile_filepath):
        """ Initializes the TempProfileManager with a JSON profile file. """
        self.temp_profile_filepath = temp_profile_filepath
        with open(temp_profile_filepath, 'r') as file:
            temp_profile = file.read()

            self.steps = self.parse_json_profile(temp_profile)
            self.expanded_steps = self.expand_all_cycles()

    def parse_json_profile(self, json_profile):
        """ Parses a JSON profile and returns a list of temperature steps. """
        try:
            profile_data = json.loads(json_profile)
            return [create_temp_step(**step) for step in profile_data]
        except json.JSONDecodeError as e:
            log_message(f"Error parsing JSON profile: {e}")
            return []
    
    def expand_all_cycles(self):
        """Expand all cycle steps into individual temperature steps."""
        expanded_steps = []
        
        for step in self.steps:
            if step.is_cycle_step():
                log_message(f"Expanding cycle step: {step.step_name} with {step.cycle_count} cycles")
                expanded_cycle_steps = step.expand_cycles()
                expanded_steps.extend(expanded_cycle_steps)
                log_message(f"Expanded into {len(expanded_cycle_steps)} individual steps")
            else:
                expanded_steps.append(step)
        
        return expanded_steps
    
    def get_all_steps(self):
        """Get all steps including expanded cycles."""
        return self.expanded_steps
    
    def get_original_steps(self):
        """Get original steps without cycle expansion."""
        return self.steps
    
    def get_step_count(self):
        """Get total number of steps after expansion."""
        return len(self.expanded_steps)
    
    def get_cycle_summary(self):
        """Get summary of cycles and step counts."""
        original_count = len(self.steps)
        expanded_count = len(self.expanded_steps)
        cycle_steps = [s for s in self.steps if s.is_cycle_step()]
        
        summary = {
            'original_steps': original_count,
            'expanded_steps': expanded_count,
            'cycle_steps_found': len(cycle_steps),
            'total_cycles_expanded': sum(s.cycle_count for s in cycle_steps if s.cycle_count)
        }
        
        return summary
    
    def get_steps_by_type(self, step_type=None):
        """Get steps filtered by type (DwellStep, RampStep, SoakStep, CycleStep)."""
        if step_type is None:
            return self.expanded_steps
        
        return [step for step in self.expanded_steps if isinstance(step, step_type)]
    
    def get_test_steps(self):
        """Get only steps that have tests enabled."""
        return [step for step in self.expanded_steps if step.has_any_tests()]
    
    def get_temperature_range(self):
        """Get the temperature range covered by all steps."""
        if not self.expanded_steps:
            return None
        
        temperatures = [step.temperature for step in self.expanded_steps]
        return {
            'min_temp': min(temperatures),
            'max_temp': max(temperatures),
            'range': max(temperatures) - min(temperatures)
        }
    
    def get_total_test_time(self):
        """Calculate total estimated test time in minutes."""
        return sum(step.total_time for step in self.expanded_steps)
    
    def get_step_types_summary(self):
        """Get summary of different step types."""
        type_counts = {}
        for step in self.expanded_steps:
            step_type = step.__class__.__name__
            type_counts[step_type] = type_counts.get(step_type, 0) + 1
        
        return type_counts


# Factory function to create appropriate step type based on temp_cycle_type
def create_temp_step(**step_data):
    """Factory function to create the appropriate temperature step type."""
    cycle_type = step_data.get('temp_cycle_type', '').upper()
    
    if cycle_type == 'CYCLE':
        return CycleStep(**step_data)
    elif cycle_type == 'DWELL':
        return DwellStep(**step_data)
    elif cycle_type == 'RAMP':
        return RampStep(**step_data)
    elif cycle_type == 'SOAK':
        return SoakStep(**step_data)
    else:
        # Default to base step
        return BaseTempStep(**step_data)


# Backward compatibility alias
TempStep = BaseTempStep
