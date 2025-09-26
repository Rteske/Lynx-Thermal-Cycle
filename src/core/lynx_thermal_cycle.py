import time
import re
from typing import Optional, Callable, Dict, Any
import os
import datetime as dt

class SerialException(Exception):
    pass
try:
    from pyvisa.errors import VisaIOError  # type: ignore
except ImportError:
    class VisaIOError(Exception):
        pass

# Temp probe accessed via duck typing (measure_temp())
from src.core.temp import TempProfileManager
from src.utils.logging_utils import log_message
from instruments.tvac_auto_explor import AutoExplor, SetpointID, ReadoutID, ButtonID, AutoExplorStatus

class LynxThermalCycleManager:
    def __init__(self, simulation_mode=False, dwell_scale: float = 1.0, tvac_ip: str = "192.168.20.12"):
        """
        Initialize the Lynx Thermal Cycle Manager with TVAC AutoExplor integration.
        
        Args:
            simulation_mode (bool): If True, uses simulated instruments. If False, uses real hardware.
            dwell_scale (float): Scale factor for dwell/initial delays
            tvac_ip (str): IP address of the TVAC AutoExplor system
        """
        self.simulation_mode = simulation_mode
        self.tvac_ip = tvac_ip
        # Scale factor for dwell/initial delays (e.g., 0.02 makes 1 minute -> ~1.2s)
        try:
            self.dwell_scale = float(dwell_scale)
        except (TypeError, ValueError):
            self.dwell_scale = 1.0
        # Minimal stub to allow simulation without importing heavy instrument stack
        class _SimPowerSupply:
            def __init__(self):
                self._v = None
                self._c = None
                self._out = False
            def set_voltage(self, v: float):
                self._v = float(v)
            def set_current(self, c: float):
                self._c = float(c)
            def set_output_state(self, on: bool):
                self._out = bool(on)
            def get_voltage(self):
                return self._v
            def get_current(self):
                return self._c
            def get_output_state(self):
                return self._out

        class _SimTestManager:
            def __init__(self):
                self.instruments_connection = {"rfsa": False, "na": False, "daq": False}
                self.paths = ["SIM_PATH"]
                self.power_supply = _SimPowerSupply()
            def run_and_process_tests(self, *args, **kwargs):
                _ = (args, kwargs)
                return None

        if simulation_mode:
            self.test_manager = _SimTestManager()
        else:
            # Lazy import to avoid pyvisa/serial requirements in simulation
            from src.core.lynx_pa_top_level_test_manager import PaTopLevelTestManager  # type: ignore
            self.test_manager = PaTopLevelTestManager(sim=False)

        self.temp_profile_manager = None
        # Public/user callback (GUI etc.). We keep this separate from the wrapper we forward to the test manager
        self._user_telemetry_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self.telemetry_callback = None  # Back-compat alias; will mirror user callback

        # Attach CSV+GUI composite telemetry callback to the test manager.
        self._attach_test_manager_csv_callback()

        # Initialize TVAC AutoExplor system for temperature control
        try:
            if not simulation_mode:
                self.tvac_controller = AutoExplor(self.tvac_ip)
                self.tvac_controller.request_control()
                
                # Get available setpoints for temperature control
                setpoint_status, setpoint_mask = self.tvac_controller.get_setpoint_configuration()
                if setpoint_status == AutoExplorStatus.SUCCESS.value:
                    setpoint_info = self.tvac_controller.get_all_setpoint_info(setpoint_mask)
                    log_message(f"TVAC setpoints available: {list(setpoint_info.keys())}")
                    
                    # Try to find platen heating control setpoint
                    self.temp_setpoint_id = None
                    self.pressure_setpoint_id = None
                    
                    for name, info in setpoint_info.items():
                        if 'platen' in name.lower() and 'heating' in name.lower():
                            self.temp_setpoint_id = info['id']
                            log_message(f"Using {name} (ID: {self.temp_setpoint_id}) for temperature control")
                        elif 'pressure' in name.lower() and 'control' in name.lower():
                            self.pressure_setpoint_id = info['id']
                            log_message(f"Using {name} (ID: {self.pressure_setpoint_id}) for pressure control")
                    
                    if self.temp_setpoint_id is None and setpoint_info:
                        # Use first available setpoint as fallback for temperature
                        first_setpoint = next(iter(setpoint_info.values()))
                        self.temp_setpoint_id = first_setpoint['id']
                        log_message(f"Using fallback setpoint {first_setpoint['name']} (ID: {self.temp_setpoint_id}) for temperature")
                    
                    if self.pressure_setpoint_id is None:
                        # Set default pressure setpoint ID
                        self.pressure_setpoint_id = SetpointID.PRESSURE_CONTROL.value
                        log_message(f"Using default pressure setpoint (ID: {self.pressure_setpoint_id})")
                else:
                    self.temp_setpoint_id = SetpointID.PLATEN_HEATING_CONTROL.value  # Default fallback
                    self.pressure_setpoint_id = SetpointID.PRESSURE_CONTROL.value
                    
                log_message("TVAC AutoExplor initialized for temperature control")
            else:
                # Use simulated TVAC controller
                self.tvac_controller = None
                self.temp_setpoint_id = SetpointID.PLATEN_HEATING_CONTROL.value
                self.pressure_setpoint_id = SetpointID.PRESSURE_CONTROL.value
                log_message("Using simulated TVAC controller")
                
        except (OSError, RuntimeError, ConnectionError) as e:
            # If we can't connect, keep None and operate in no-op mode
            self.tvac_controller = None
            self.temp_setpoint_id = SetpointID.PLATEN_HEATING_CONTROL.value
            self.pressure_setpoint_id = SetpointID.PRESSURE_CONTROL.value
            log_message(f"TVAC AutoExplor not available: {e}")

        # Provide TVAC controller reference to the top-level test manager
        if hasattr(self.test_manager, 'set_tvac_controller'):
            self.test_manager.set_tvac_controller(self.tvac_controller)
        
        # Note: Temperature measurements now come exclusively from TVAC ReadoutIDs
        # No external thermocouples are used - all temperature data from TVAC system
        # Telemetry CSV setup
        try:
            logs_dir = os.path.join(os.getcwd(), "logs")
            os.makedirs(logs_dir, exist_ok=True)
            ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.telemetry_path = os.path.join(logs_dir, f"thermal_cycle_telemetry_{ts}.csv")
            if not os.path.exists(self.telemetry_path):
                with open(self.telemetry_path, "w", encoding="utf-8") as f:
                    f.write(
                        "timestamp,step_index,step_name,cycle_type,phase,target_c,platen_setpoint_c,platen_temp_c," \
                        "psu_voltage,psu_current,psu_output,tc1_temp,tc2_temp," \
                        "pressure_torr,pressure_setpoint,pressure_mode," \
                        "tests_pin_pout_functional,tests_sig_a_performance,tests_na_performance,rf_on_off,fault_status,bandpath,gain_value,date_string,temp_value\n"
                    )
            log_message(f"Telemetry CSV -> {self.telemetry_path}")
        except OSError as e:
            log_message(f"Failed to initialize telemetry CSV: {e}")
            self.telemetry_path = None

        # Telemetry runtime state
        self._telemetry_last_ts = 0.0
        self.current_step = None

    # --------- Internal helpers ---------
    def _apply_power_for_step(self, voltage: float, current: float):
        try:
            psu = getattr(self.test_manager, "power_supply", None)
            if psu is None:
                return
            if voltage and voltage > 0:
                psu.set_voltage(voltage)
                if current and current > 0:
                    psu.set_current(current)
                psu.set_output_state(True)
                log_message(f"PSU set: {voltage:.2f} V, {current:.2f} A, output ON")
            else:
                psu.set_output_state(False)
                log_message("PSU output OFF")
        except (VisaIOError, AttributeError, ValueError, OSError) as e:
            log_message(f"Warning: PSU action failed: {e}")

    def _power_off(self):
        try:
            psu = getattr(self.test_manager, "power_supply", None)
            if psu is not None:
                psu.set_output_state(False)
                log_message("PSU output OFF (post-step)")
        except (VisaIOError, AttributeError, OSError) as e:
            log_message(f"Warning: PSU power off failed: {e}")

    def _set_setpoint(self, setpoint_c: float):
        if self.tvac_controller is None:
            log_message(f"[SIM] Would set TVAC setpoint to {setpoint_c:.2f} C")
            return
        try:
            # Set the target value for the temperature setpoint
            status, _ = self.tvac_controller.set_setpoint_target_value(self.temp_setpoint_id, setpoint_c)
            if status == AutoExplorStatus.SUCCESS.value:
                # Enable the setpoint controller
                status, _ = self.tvac_controller.set_setpoint_state(self.temp_setpoint_id, True)
                if status == AutoExplorStatus.SUCCESS.value:
                    log_message(f"TVAC setpoint -> {setpoint_c:.2f} C (ID: {self.temp_setpoint_id})")
                else:
                    log_message(f"Failed to enable TVAC setpoint controller (status: {status})")
            else:
                log_message(f"Failed to set TVAC setpoint value (status: {status})")

            # Wait until the setpoint is applied
            timeout = 30  # seconds
            start_time = time.time()
            while True:
                platen_temp = self._read_platen_temp()
                if platen_temp is not None:
                    break
                if time.time() - start_time >= timeout:
                    log_message("Setpoint applied; no readout available yet (timeout). Proceeding.")
                    break
                self._maybe_log_telemetry(phase="setpoint-wait", step=self.current_step, setpoint_c=setpoint_c)
                time.sleep(0.5)
        except (OSError, ValueError) as e:
            log_message(f"Failed to set TVAC setpoint: {e}")

    def _read_platen_temp(self) -> Optional[float]:
        if self.tvac_controller is None:
            return None
        try:
            status, process_value = self.tvac_controller.get_setpoint_process_value(SetpointID.PLATEN_HEATING_CONTROL)
            if status == AutoExplorStatus.SUCCESS.value and process_value is not None:
                return float(process_value)
        except (OSError, ValueError):
            pass
        return None

    def _read_platen_setpoint_temp(self) -> Optional[float]:
        """Read the current setpoint value from TVAC."""
        if self.tvac_controller is None:
            return None
        try:
            status, target_value = self.tvac_controller.get_setpoint_target_value(SetpointID.PLATEN_HEATING_CONTROL)
            if status == AutoExplorStatus.SUCCESS.value and target_value is not None:
                return float(target_value)
        except (OSError, ValueError):
            pass
        return None

    def _set_pressure_setpoint(self, pressure_torr: float):
        """Set the pressure setpoint in Torr."""
        if self.tvac_controller is None:
            log_message(f"[SIM] Would set TVAC pressure setpoint to {pressure_torr:.2f} Torr")
            return
        try:
            # Set the target value for the pressure setpoint
            status, _ = self.tvac_controller.set_setpoint_mode(self.pressure_setpoint_id, "vent")
            status, _ = self.tvac_controller.set_setpoint_target_value(self.pressure_setpoint_id, pressure_torr)
            if status == AutoExplorStatus.SUCCESS.value:
                # Enable the pressure setpoint controller
                status, _ = self.tvac_controller.set_setpoint_state(self.pressure_setpoint_id, True)
                if status == AutoExplorStatus.SUCCESS.value:
                    log_message(f"TVAC pressure setpoint -> {pressure_torr:.2f} Torr (ID: {self.pressure_setpoint_id})")
                else:
                    log_message(f"Failed to enable TVAC pressure setpoint controller (status: {status})")
            else:
                log_message(f"Failed to set TVAC pressure setpoint value (status: {status})")
        except (OSError, ValueError) as e:
            log_message(f"Failed to set TVAC pressure setpoint: {e}")

    def _read_actual_pressure(self) -> Optional[float]:
        """Read the current pressure from TVAC system."""
        if self.tvac_controller is None:
            return None
        try:
            # Fallback: try to read process value from the pressure setpoint controller itself
            status, process_value = self.tvac_controller.get_setpoint_process_value(self.pressure_setpoint_id)
            if status == AutoExplorStatus.SUCCESS.value and process_value is not None:
                return float(process_value)
                
        except (OSError, ValueError):
            pass
        return None

    def _read_pressure_setpoint(self) -> Optional[float]:
        """Read the current pressure setpoint value from TVAC."""
        if self.tvac_controller is None:
            return None
        try:
            status, target_value = self.tvac_controller.get_setpoint_target_value(self.pressure_setpoint_id)
            self.tvac_controller.set_button_state(ButtonID.HIGH_VAC, True)  # Ensure vent button is active
            if status == AutoExplorStatus.SUCCESS.value and target_value is not None:
                return float(target_value)
        except (OSError, ValueError):
            pass
        return None

    def _get_pressure_control_mode(self) -> Optional[str]:
        """Get the current pressure control mode (vent, purge, etc.)."""
        if self.tvac_controller is None:
            return None
        try:
            status, mode = self.tvac_controller.get_setpoint_mode(self.pressure_setpoint_id)
            if status == AutoExplorStatus.SUCCESS.value:
                return mode
        except (OSError, ValueError):
            pass
        return None

    def _set_pressure_control_mode(self, mode: str):
        """Set the pressure control mode (vent, purge, actprg, etc.)."""
        if self.tvac_controller is None:
            log_message(f"[SIM] Would set TVAC pressure control mode to {mode}")
            return
        try:
            status, _ = self.tvac_controller.set_setpoint_mode(self.pressure_setpoint_id, mode)
            if status == AutoExplorStatus.SUCCESS.value:
                log_message(f"TVAC pressure control mode -> {mode} (ID: {self.pressure_setpoint_id})")
            else:
                log_message(f"Failed to set TVAC pressure control mode (status: {status})")
        except (OSError, ValueError) as e:
            log_message(f"Failed to set TVAC pressure control mode: {e}")

    def _tcs_within_band(self, target_c: float, tol_c: float) -> tuple[bool, int, list[float]]:
        """Check if available TVAC temperature readouts are within target±tol.
        Returns (all_ok, count_present, values_present). If no TCs present, (False, 0, [])."""
        if self.tvac_controller is None:
            return False, 0, []
        
        try:
            # Get all temperature readings from TVAC
            temp_readings = self.tvac_controller.get_temperature_readings()
            vals: list[float] = []
            
            for name, info in temp_readings.items():
                if info['is_valid'] and info['value'] is not None:
                    vals.append(float(info['value']))
            
            if not vals:
                return False, 0, []
                
            all_ok = all(abs(v - target_c) <= tol_c for v in vals)
            return all_ok, len(vals), vals
        except (OSError, ValueError):
            return False, 0, []

    def _calculate_stability(self, window_values, window_s, min_time_s):
        """Calculate stability metrics for a rolling window of temperature values.
        
        Args:
            window_values: List of (timestamp, temperature) tuples
            window_duration: Expected window duration in seconds  
            min_time_s: Minimum time duration required for valid stability calculation
            
        Returns:
            (span, has_enough_time, coverage_seconds, sample_count)
        """
        if not window_values:
            return 0.0, False, 0.0, 0
            
        vals = [v for _, v in window_values]
        sample_count = len(vals)
        
        # Calculate actual time coverage
        if len(window_values) >= 2:
            coverage_s = window_values[-1][0] - window_values[0][0]
        else:
            coverage_s = 0.0
            
        # Time-based requirement: need at least min_time_s of data
        has_enough_time = coverage_s >= min_time_s
        
        # Calculate span (temperature variance) - need at least 2 samples
        if sample_count >= 2:
            span = max(vals) - min(vals)
        else:
            span = 0.0
            
        return span, has_enough_time, coverage_s, sample_count

    def _wait_until_stable(self, target_c: float, target_temp_delta_c: float, tol_c: float, window_s: int, poll_s: int, initial_delay_s: int, temp_offset: float):
        """Two-phase temperature stabilization:
        Phase 1: Wait for TC to get into target band, with PID adjustments based on stability outside band
        Phase 2: Settlement logic once in target band - wait for stable temperature within tolerance
        """
        # Apply setpoint once (target + offset)
        sp = float(target_c + (temp_offset or 0.0))
        self._set_setpoint(sp)

        # PID state for corrections when taking too long to reach target band
        pid_enabled = True
        Kp, Ki, Kd = 0.1, 0.02, 0.0  # conservative gains; derivative disabled by default
        integ = 0.0
        last_err: Optional[float] = None
        last_pid_ts: Optional[float] = None
        min_pid_interval_s = max(10, int(poll_s * 2))  # don't adjust too frequently
        max_step_per_adjust_c = 1.0  # clamp single adjustment magnitude
        max_sp_offset_c = 10.0  # clamp total deviation from (target + offset)
        base_sp = float(sp)

        def _apply_sp_nudge(new_sp: float):
            nonlocal sp
            sp = float(new_sp)
            try:
                if self.tvac_controller is None:
                    log_message(f"[SIM] PID: setpoint -> {sp:.2f} C")
                else:
                    status, _ = self.tvac_controller.set_setpoint_target_value(self.temp_setpoint_id, sp)
                    if status == AutoExplorStatus.SUCCESS.value:
                        # Wait until the setpoint is applie
                        status, temp = self.tvac_controller.get_setpoint_process_value(SetpointID.PLATEN_HEATING_CONTROL)  # Initial read
                        while abs(sp - temp) >= 0.1:
                            status, temp = self.tvac_controller.get_setpoint_process_value(SetpointID.PLATEN_HEATING_CONTROL)  # Force update
                            time.sleep(0.5)
                            self._maybe_log_telemetry(phase="pid-setpoint-wait", step=self.current_step, setpoint_c=sp)
                        log_message(f"PID: TVAC setpoint -> {sp:.2f} C (ID: {self.temp_setpoint_id})")
                    else:
                        log_message(f"PID: failed to set TVAC setpoint (status: {status})")
            except (OSError, ValueError) as e:
                log_message(f"PID: failed to set setpoint: {e}")

        # Measurement function (prefer TC1; fallback to controller)
        def read_meas() -> Optional[float]:
            temp = self._get_tvac_temp_snapshot_values()
            return temp[0]

        # Optional initial delay
        try:
            scaled_initial_delay = int(max(0, float(initial_delay_s)) * max(0.01, float(self.dwell_scale)))
        except (TypeError, ValueError):
            scaled_initial_delay = int(initial_delay_s)
        if scaled_initial_delay and scaled_initial_delay > 0:
            log_message(
                f"INIT: delay={scaled_initial_delay}s before stabilization | target={target_c:.2f}C, band=±{float(target_temp_delta_c):.2f}C, tol={tol_c:.2f}C"
            )
            end = time.time() + scaled_initial_delay
            while time.time() < end:
                self._maybe_log_telemetry(phase="init-delay", step=self.current_step, setpoint_c=sp)
                time.sleep(min(5, max(1, int(poll_s))))

        # PHASE 1: Wait for TC to get into target band
        log_message(f"PHASE 1: Waiting for TC to reach target band ±{target_temp_delta_c:.2f}C")
        poll = max(1, int(poll_s))
        phase1_start = time.time()
        max_phase1_time_s = 30 * 60  # 30 minutes max for phase 1
        missing_meas_count = 0
        
        # Phase 1 uses smaller rolling window for faster stability detection
        phase1_window_s = window_s / 2  # Half of main window
        phase1_window_values: list[tuple[float, float]] = []
        stability_threshold = 0.75  # Require 75% of tolerance for stability in phase 1

        while True:
            meas = read_meas()
            if meas is None:
                missing_meas_count += 1
                if self.simulation_mode and missing_meas_count >= 3:
                    log_message("PHASE 1: No measurement (SIM) — proceeding to phase 2")
                    break
                if (time.time() - phase1_start) > max_phase1_time_s:
                    log_message("PHASE 1: Timeout reached — proceeding to phase 2")
                    break
                log_message("PHASE 1: No measurement; waiting…")
                time.sleep(poll)
                continue

            now = time.time()
            band_err = abs(float(meas) - float(target_c))
            in_band = band_err <= float(target_temp_delta_c)
            phase1_elapsed = now - phase1_start
            
            # Update rolling window for phase 1
            phase1_window_values.append((now, float(meas)))
            cutoff = now - phase1_window_s
            phase1_window_values = [(ts, v) for ts, v in phase1_window_values if ts >= cutoff]
            
            # Calculate stability using reusable function
            min_stability_time =  phase1_window_s / 2 # At least 15s or half the window
            span, has_enough_time, coverage_s, sample_count = self._calculate_stability(
                phase1_window_values, phase1_window_s, min_time_s=min_stability_time
            )

            is_stable = span <= (float(tol_c) * 1.5)  # 150% of tolerance requirement

            if in_band and is_stable and has_enough_time:
                log_message(f"PHASE 1: Reached target band ±{target_temp_delta_c:.2f}C after {phase1_elapsed:.1f}s")
                break  # Proceed to phase 2

            log_message(
                f"PHASE 1: temp={meas:.2f}C target={target_c:.2f}C band_err={band_err:.3f}C in_band={in_band} "
                f"span={span:.3f}C stable={is_stable} cov={coverage_s:.1f}s time_ok={has_enough_time} elapsed={phase1_elapsed:.1f}s"
            )
            self._maybe_log_telemetry(phase="phase1-approach", step=self.current_step, setpoint_c=sp)

            # Enable PID adjustments if outside band AND temperature is stable (within 75% tolerance)
            if pid_enabled and not in_band and is_stable and has_enough_time:
                err = float(target_c) - float(meas)  # positive if too cold; increase setpoint
                # Rate limit PID adjustments
                if last_pid_ts is None or (now - last_pid_ts) >= min_pid_interval_s:
                    dt_s = (now - last_pid_ts) if last_pid_ts is not None else float(poll)
                    # Integrator with clamping to avoid wind-up
                    integ = max(-max_sp_offset_c, min(max_sp_offset_c, integ + err * dt_s))
                    deriv = 0.0 if (Kd == 0 or last_err is None or dt_s <= 0) else (err - last_err) / dt_s
                    output = Kp * err + Ki * integ + Kd * deriv
                    # Clamp single-step adjustment
                    output = max(-max_step_per_adjust_c, min(max_step_per_adjust_c, output))
                    # Clamp total deviation from the base setpoint
                    new_sp = base_sp + max(-max_sp_offset_c, min(max_sp_offset_c, (sp - base_sp) + output))
                    # Apply nudge
                    log_message(
                        f"PHASE 1 PID: Stable but outside band (err {err:.3f}C, span {span:.3f}C). Adjusting setpoint by {output:.3f}C to {new_sp:.2f}C"
                    )
                    _apply_sp_nudge(new_sp)
                    last_pid_ts = now
                    last_err = err
                    
                    # Give the system time to respond to the adjustment to prevent overcorrection
                    # Make settling time proportional to the magnitude of the adjustment
                    adjustment_magnitude = abs(output)
                    base_settle_time = 60  # Base minimum settling time in seconds
                    magnitude_factor = 420  # seconds per degree of adjustment (2 minutes per degree)
                    adjustment_settle_time = max(base_settle_time, int(base_settle_time + (adjustment_magnitude * magnitude_factor)))
                    # Cap the maximum settling time to prevent excessively long waits
                    max_settle_time = min_pid_interval_s // 2  # Half of the PID interval
                    adjustment_settle_time = min(adjustment_settle_time, max_settle_time)
                    
                    log_message(f"PHASE 1 PID: Waiting {adjustment_settle_time}s for {adjustment_magnitude:.3f}C adjustment to take effect...")
                    settle_end = time.time() + adjustment_settle_time
                    while time.time() < settle_end:
                        self._maybe_log_telemetry(phase="pid-adjustment-settle", step=self.current_step, setpoint_c=sp)
                        time.sleep(min(10, max(5, int(poll_s))))
                    log_message("PHASE 1 PID: Adjustment settling time complete, resuming monitoring")

            time.sleep(poll)

        # PHASE 2: Settlement logic - wait for stable temperature within tolerance
        log_message(f"PHASE 2: Settlement - waiting for stable temperature within ±{tol_c:.2f}C tolerance")
        window_duration = max(1, int(window_s))
        window_values: list[tuple[float, float]] = []
        end_required = time.time() + window_duration
        settle_start = time.time()
        max_settle_time_s = max(60 * 60, 2 * window_duration)

        while True:
            meas = read_meas()
            if meas is None:
                missing_meas_count += 1
                if self.simulation_mode and missing_meas_count >= 6:
                    log_message("PHASE 2: No measurement (SIM) — treating as stable")
                    return
                if (time.time() - settle_start) > max_settle_time_s:
                    log_message("PHASE 2: Settlement timeout reached — proceeding")
                    return
                log_message("PHASE 2: No measurement; waiting…")
                time.sleep(poll)
                continue

            now = time.time()
            window_values.append((now, float(meas)))
            # Allow window to grow slightly larger than target to ensure we can achieve 100% coverage
            # Use 110% of window duration to allow for some buffer
            cutoff = now - (window_duration * 1.1)
            window_values = [(ts, v) for ts, v in window_values if ts >= cutoff]

            # Use reusable stability calculation function
            # For Phase 2, require 100% of the window duration to be covered
            min_stability_time = float(window_duration)  # Require 100% coverage
            span, has_enough_time, coverage_s, sample_count = self._calculate_stability(
                window_values, window_duration, min_time_s=min_stability_time
            )
            band_err = abs(float(meas) - float(target_c))
            in_band = band_err <= float(target_temp_delta_c)
            span_within_tol = span <= float(tol_c)
            # For Phase 2, require full coverage (100% of window duration)
            has_full_coverage = coverage_s >= window_duration

            log_message(
                f"PHASE 2: n={sample_count} span={span:.3f}C tol={tol_c:.3f}C span_ok={span_within_tol} in_band={in_band} "
                f"cov={coverage_s:.1f}s/{window_duration}s time_ok={has_enough_time} full_cov={has_full_coverage}"
            )
            self._maybe_log_telemetry(phase="phase2-settle", step=self.current_step, setpoint_c=sp)

            # Primary stability check: in band and span within tolerance
            if span_within_tol and in_band:
                # Debug: Show why we're choosing each path
                log_message(f"PHASE 2 DEBUG: has_full_coverage={has_full_coverage} (need {window_duration:.1f}s, have {coverage_s:.1f}s)")
                log_message(f"PHASE 2 DEBUG: has_enough_time={has_enough_time} (same as full coverage)")
                log_message(f"PHASE 2 DEBUG: now >= end_required = {now >= end_required} (end_required={end_required:.1f}, now={now:.1f})")
                
                # If window has full coverage and enough time, we're stable
                if has_full_coverage and has_enough_time:
                    log_message(f"PHASE 2: Stable — window span {span:.3f}C ≤ tol {tol_c:.3f}C and in target band over full {coverage_s:.1f}s window")
                    return
                # Fallback: If coverage is close to full (95%) and we've been waiting long enough, accept it
                elif coverage_s >= window_duration * 0.95 and now >= end_required:
                    log_message(f"PHASE 2: Stable (near-full) — window span {span:.3f}C ≤ tol {tol_c:.3f}C and in target band over {coverage_s:.1f}s (95%+ coverage)")
                    return
                else:
                    remaining_time = max(0, end_required - now)
                    coverage_pct = (coverage_s / window_duration) * 100
                    log_message(f"PHASE 2: Good conditions, waiting {remaining_time:.1f}s more - need {coverage_pct:.1f}% -> 100% coverage")
            else:
                # Reset the settlement window if not stable
                end_required = time.time() + window_duration
                failed_conditions = []
                if not span_within_tol:
                    failed_conditions.append(f"span({span:.3f}>{tol_c:.3f})")
                if not in_band:
                    failed_conditions.append(f"not_in_band({band_err:.3f}>{target_temp_delta_c:.3f})")
                log_message(f"PHASE 2: Resetting window timer, failed: {', '.join(failed_conditions)}")

            time.sleep(poll)

    # --------- Telemetry helpers ---------
    def _init_telemetry(self):
        # No-op (telemetry initialized in __init__)
        return

    def get_live_snapshot(self) -> Dict[str, Any]:
        """Return a best-effort live snapshot of key telemetry values.

        Includes: setpoint_c, platen_temp_c, psu_voltage, psu_current, psu_output,
        tc1_temp, tc2_temp, and DAQ fields (rf_on_off, fault_status, bandpath,
        gain_value, date_string, temp_value). Missing values are returned as None.
        """
        snapshot: Dict[str, Any] = {}
        # Temp controller setpoint and actual
        try:
            sp = None
            if getattr(self, "tvac_controller", None) is not None:
                try:
                    sp = self._read_platen_setpoint_temp()
                except Exception:
                    sp = None
            snapshot["platen_setpoint_c"] = sp
        except Exception:
            snapshot["platen_setpoint_c"] = None

        try:
            snapshot["platen_temp_c"] = self._read_platen_temp()
        except Exception:
            snapshot["platen_temp_c"] = None

        # PSU
        try:
            v, c, out = self._get_psu_snapshot()
            snapshot["psu_voltage"] = v if isinstance(v, (int, float)) else None
            snapshot["psu_current"] = c if isinstance(c, (int, float)) else None
            snapshot["psu_output"] = bool(out) if out is not None else None
        except Exception:
            snapshot["psu_voltage"] = None
            snapshot["psu_current"] = None
            snapshot["psu_output"] = None

        try:
            # Get TVAC temperature readings instead of external TCs
            tvac_temps = self._get_tvac_temp_snapshot()
            snapshot["sample_1"] = tvac_temps.get('sample_1')
            snapshot["sample_2"] = tvac_temps.get('sample_2')  # Use first sample TC as TC2
        except Exception:
            snapshot["sample_1"] = None
            snapshot["sample_2"] = None

        # Pressure readings from TVAC
        try:
            snapshot["pressure_torr"] = self._read_actual_pressure()
            snapshot["pressure_setpoint"] = self._read_pressure_setpoint()
            snapshot["pressure_mode"] = self._get_pressure_control_mode()
        except Exception:
            snapshot["pressure_torr"] = None
            snapshot["pressure_setpoint"] = None
            snapshot["pressure_mode"] = None

        # DAQ fields
        try:
            daq = self._get_daq_snapshot()
            if isinstance(daq, dict):
                for k in ("rf_on_off", "fault_status", "bandpath", "gain_value", "date_string", "temp_value"):
                    snapshot[k] = daq.get(k)
            else:
                for k in ("rf_on_off", "fault_status", "bandpath", "gain_value", "date_string", "temp_value"):
                    snapshot[k] = None
        except Exception:
            for k in ("rf_on_off", "fault_status", "bandpath", "gain_value", "date_string", "temp_value"):
                snapshot[k] = None

        return snapshot

    def set_telemetry_callback(self, callback: Optional[Callable[[Dict[str, Any]], None]]):
        """Register a callback that receives a dict of telemetry values whenever we log a row."""
        # Store user callback and mirror legacy attribute
        self._user_telemetry_callback = callback
        self.telemetry_callback = callback

        # Define a wrapper: write to CSV, then invoke user callback.
        def _csv_proxy(payload: Dict[str, Any]):
            try:
                self._log_external_telemetry(payload)
            except Exception:
                # Never let CSV issues kill the callback chain
                pass
            # Finally, pass through to the user callback if present
            try:
                if self._user_telemetry_callback is not None:
                    self._user_telemetry_callback(payload)
            except Exception:
                pass

        # Also forward to the underlying test manager
        try:
            tm_cb_setter = getattr(self.test_manager, "set_telemetry_callback", None)
            tm_sink_setter = getattr(self.test_manager, "set_external_telemetry_sink", None)
            if callable(tm_cb_setter):
                tm_cb_setter(_csv_proxy)
            if callable(tm_sink_setter):
                tm_sink_setter(_csv_proxy)
        except Exception:
            pass

    def _attach_test_manager_csv_callback(self) -> None:
        """Ensure the test manager has a callback that logs to CSV and optionally to the user GUI."""
        try:
            tm_cb_setter = getattr(self.test_manager, "set_telemetry_callback", None)
            tm_sink_setter = getattr(self.test_manager, "set_external_telemetry_sink", None)
            if not callable(tm_cb_setter):
                return
            def _composite(payload: Dict[str, Any]):
                try:
                    self._log_external_telemetry(payload)
                except Exception:
                    pass
                try:
                    if self._user_telemetry_callback is not None:
                        self._user_telemetry_callback(payload)
                except Exception:
                    pass
            tm_cb_setter(_composite)
            # Also wire as an external sink if supported, providing redundancy
            if callable(tm_sink_setter):
                try:
                    tm_sink_setter(_composite)
                except Exception:
                    pass
        except Exception:
            # Keep silent; tests must not break on telemetry issues
            pass

    def _log_external_telemetry(self, payload: Dict[str, Any]):
        """Append a telemetry line from external sources (e.g., test manager) into the same CSV schema.

        The payload may include some of: timestamp, step_index, step_name, cycle_type, phase,
        target_c, setpoint_c, platen_temp_c, psu_voltage, psu_current, psu_output,
        tc1_temp, tc2_temp, rf_on_off, fault_status, bandpath, gain_value, date_string, temp_value.
        Missing fields are left blank in the CSV.
        """
        if self.telemetry_path is None:
            return
        try:
            # Prefer current step context when present
            idx = payload.get("step_index")
            if idx is None and self.current_step is not None:
                idx = getattr(self.current_step, "_index", None)
            name = payload.get("step_name")
            if not name and self.current_step is not None:
                name = getattr(self.current_step, "step_name", "")
            cycle = payload.get("cycle_type")
            if not cycle and self.current_step is not None:
                cycle = getattr(self.current_step, "temp_cycle_type", "")
            phase = payload.get("phase", "")

            target = payload.get("target_c", None)
            if target is None and self.current_step is not None:
                target = getattr(self.current_step, "temperature", None)

            platen_sp = payload.get("platen_setpoint_c")
            if platen_sp is None and self.tvac_controller is not None:
                try:
                    platen_sp = self._read_platen_setpoint_temp()
                except Exception:
                    platen_sp = None

            platen_temp = payload.get("platen_temp_c")
            if platen_temp is None:
                platen_temp = self._read_platen_temp()

            # PSU snapshots from payload with fallback to live reads
            v = payload.get("psu_voltage")
            c = payload.get("psu_current")
            out = payload.get("psu_output")
            if v is None or c is None or out is None:
                pv, pc, pout = self._get_psu_snapshot()
                v = v if isinstance(v, (int, float)) else pv
                c = c if isinstance(c, (int, float)) else pc
                out = out if isinstance(out, bool) else pout

            # TC: prefer payload, otherwise live from TVAC
            tc1 = payload.get("sample_1")
            tc2 = payload.get("sample_2")
            if tc1 is None or tc2 is None:
                tvac_temps = self._get_tvac_temp_snapshot()
                tc1 = tc1 if isinstance(tc1, (int, float)) else tvac_temps.get('sample_1')
                tc2 = tc2 if isinstance(tc2, (int, float)) else tvac_temps.get('sample_2')

            # Pressure: prefer payload, otherwise live from TVAC
            pressure_actual = payload.get("pressure_torr")
            pressure_setpoint = payload.get("pressure_setpoint")
            pressure_mode = payload.get("pressure_mode")
            if pressure_actual is None:
                pressure_actual = self._read_actual_pressure()
            if pressure_setpoint is None:
                pressure_setpoint = self._read_pressure_setpoint()
            if pressure_mode is None:
                pressure_mode = self._get_pressure_control_mode()

            # DAQ: prefer payload, otherwise live
            rf_on_off = payload.get("rf_on_off")
            fault_status = payload.get("fault_status")
            bandpath = payload.get("bandpath")
            gain_value = payload.get("gain_value")
            date_string = payload.get("date_string")
            temp_value = payload.get("temp_value")
            if any(x is None for x in (rf_on_off, fault_status, bandpath, gain_value, date_string, temp_value)):
                daq_snapshot = self._get_daq_snapshot()
                if isinstance(daq_snapshot, dict):
                    rf_on_off = rf_on_off if rf_on_off is not None else daq_snapshot.get("rf_on_off")
                    fault_status = fault_status if fault_status is not None else daq_snapshot.get("fault_status")
                    bandpath = bandpath if bandpath is not None else daq_snapshot.get("bandpath")
                    gain_value = gain_value if gain_value is not None else daq_snapshot.get("gain_value")
                    date_string = date_string if date_string is not None else daq_snapshot.get("date_string")
                    temp_value = temp_value if temp_value is not None else daq_snapshot.get("temp_value")

            # Timestamp: use payload timestamp or now
            ts = payload.get("timestamp")
            try:
                ts_str = (ts.isoformat() if hasattr(ts, "isoformat") else str(ts)) if ts else dt.datetime.now().isoformat()
            except Exception:
                ts_str = dt.datetime.now().isoformat()

            line = [
                ts_str,
                idx if idx is not None else "",
                name or "",
                cycle or "",
                phase or "",
                f"{float(target):.3f}" if isinstance(target, (int, float)) else "",
                f"{float(platen_sp):.3f}" if isinstance(platen_sp, (int, float)) else "",
                f"{float(platen_temp):.3f}" if isinstance(platen_temp, (int, float)) else "",
                f"{float(v):.3f}" if isinstance(v, (int, float)) else "",
                f"{float(c):.3f}" if isinstance(c, (int, float)) else "",
                str(bool(out)) if out is not None else "",
                f"{float(tc1):.3f}" if isinstance(tc1, (int, float)) else "",
                f"{float(tc2):.3f}" if isinstance(tc2, (int, float)) else "",
                f"{float(pressure_actual):.3f}" if isinstance(pressure_actual, (int, float)) else "",
                f"{float(pressure_setpoint):.3f}" if isinstance(pressure_setpoint, (int, float)) else "",
                str(pressure_mode) if pressure_mode is not None else "",
                "",  # tests_pin_pout_functional not provided by test manager snapshots
                "",  # tests_sig_a_performance
                "",  # tests_na_performance
                str(bool(rf_on_off)) if rf_on_off is not None else "",
                str(fault_status) if fault_status is not None else "",
                str(bandpath) if bandpath is not None else "",
                str(int(gain_value)) if isinstance(gain_value, (int, float)) else "",
                str(date_string) if date_string is not None else "",
                str(float(temp_value)) if isinstance(temp_value, (int, float)) else "",
            ]
            with open(self.telemetry_path, "a", encoding="utf-8") as f:
                f.write(",".join(map(str, line)) + "\n")
        except Exception as e:
            print(e)

    def _get_psu_snapshot(self):
        v = c = out = None
        psu = getattr(self.test_manager, "power_supply", None)
        if psu is None:
            return v, c, out
        try:
            v = psu.get_voltage()
        except (OSError, ValueError):
            pass
        try:
            c = psu.get_current()
        except (OSError, ValueError):
            pass
        try:
            out = psu.get_output_state()
        except (OSError, ValueError):
            pass
        return v, c, out

    def _get_tc_snapshot(self):
        """Read temperatures from TVAC temperature readouts instead of external TCs."""
        return self._get_tvac_temp_snapshot_values()

    def _get_tvac_temp_snapshot(self):
        """Get TVAC temperature readings as a dictionary."""
        if self.tvac_controller is None:
            return {}
        try:
            temp_readings = self.tvac_controller.get_temperature_readings()
            temp_dict = {}
            
            for name, info in temp_readings.items():
                if info['is_valid'] and info['value'] is not None:
                    # Map common TVAC readout names to simpler keys
                    if 'sample_1' == name.lower():
                        temp_dict['sample_1'] = info['value']
                    elif 'sample_2' == name.lower():
                        temp_dict['sample_2'] = info['value']
            
            return temp_dict
        except Exception:
            return {}

    def _get_tvac_temp_snapshot_values(self):
        """Read temperatures from TVAC readouts, returning tuple for compatibility."""
        tvac_temps = self._get_tvac_temp_snapshot()
        tc1_temp = tvac_temps.get('sample_1')
        tc2_temp = tvac_temps.get('sample_2')  # Use first sample as TC2
        return float(tc1_temp), float(tc2_temp)

    def _get_tvac_snapshot(self):
        """Read key TVAC system status."""
        if self.tvac_controller is None:
            return {}
        
        try:
            # Get temperature readings
            temp_readings = self.tvac_controller.get_temperature_readings()
            
            # Get pressure readings
            pressure_readings = self.tvac_controller.get_pressure_readings()
            
            # Get setpoint information
            setpoint_info = self.tvac_controller.get_setpoint_info(self.temp_setpoint_id)
            pressure_setpoint_info = self.tvac_controller.get_setpoint_info(self.pressure_setpoint_id)
            
            # Get key button states
            power_status, power_state = self.tvac_controller.get_button_state(ButtonID.POWER)
            vent_status, vent_state = self.tvac_controller.get_button_state(ButtonID.VENT)
            rough_status, rough_state = self.tvac_controller.get_button_state(ButtonID.ROUGH)
            
            return {
                'temp_readings': temp_readings,
                'pressure_readings': pressure_readings,
                'setpoint_info': setpoint_info,
                'pressure_setpoint_info': pressure_setpoint_info,
                'power_on': power_state['on_off'] if power_status == AutoExplorStatus.SUCCESS.value else None,
                'vent_open': vent_state['on_off'] if vent_status == AutoExplorStatus.SUCCESS.value else None,
                'rough_pump_on': rough_state['on_off'] if rough_status == AutoExplorStatus.SUCCESS.value else None,
                'setpoint_active': setpoint_info['state']['on_off'] if setpoint_info.get('state') else None,
                'pressure_setpoint_active': pressure_setpoint_info['state']['on_off'] if pressure_setpoint_info.get('state') else None,
                'current_target': setpoint_info.get('target_value'),
                'current_ttv': setpoint_info.get('ttv_value'),
                'is_ramping': setpoint_info.get('is_ramping'),
                'pressure_target': pressure_setpoint_info.get('target_value'),
                'pressure_mode': pressure_setpoint_info.get('current_mode')
            }
        except Exception as e:
            log_message(f"Error reading TVAC snapshot: {e}")
            return {}

    def _get_daq_snapshot(self):
        """Read data from the DAQ if available."""
        daq = getattr(self.test_manager, "daq", None)
        if daq is None:
            return None
        try:
            rf_on_off, fault_status, bandpath, gain_value, date_string, temp_value = daq.read_status_return()
            return {
                "rf_on_off": rf_on_off,
                "fault_status": fault_status,
                "bandpath": bandpath,
                "gain_value": gain_value,
                "date_string": date_string,
                "temp_value": temp_value,
            }
        except Exception:
            return None

    def _log_telemetry(self, phase: str, step=None, setpoint_c: Optional[float] = None,
                        pin_pout_functional: Optional[bool] = None,
                        sig_a_performance: Optional[bool] = None,
                        na_performance: Optional[bool] = None):
        if self.telemetry_path is None:
            return
        try:
            idx = getattr(self.current_step, "_index", None)
            name = getattr(self.current_step, "step_name", "") if self.current_step is not None else ""
            cycle = getattr(self.current_step, "temp_cycle_type", "") if self.current_step is not None else ""
            target = getattr(self.current_step, "temperature", None) if self.current_step is not None else None

            # Resolve setpoint for logging in a safe way
            platen_sp: Optional[float] = None
            if self.tvac_controller is not None:
                try:
                    platen_sp = self._read_platen_setpoint_temp()
                except (OSError, ValueError, RuntimeError, TypeError):
                    platen_sp = None
            if platen_sp is None and setpoint_c is not None:
                try:
                    platen_sp = float(setpoint_c)
                except (ValueError, TypeError):
                    platen_sp = None
            platen_temp = self._read_platen_temp()
            v, c, out = self._get_psu_snapshot()
            tc1, tc2 = self._get_tc_snapshot()
            
            # Get pressure data
            pressure_actual = self._read_actual_pressure()
            pressure_setpoint = self._read_pressure_setpoint()
            pressure_mode = self._get_pressure_control_mode()

            daq_snapshot = self._get_daq_snapshot()

            line = [
                dt.datetime.now().isoformat(),
                idx if idx is not None else "",
                name,
                cycle,
                phase,
                f"{target:.3f}" if isinstance(target, (int, float)) else "",
                f"{platen_sp:.3f}" if isinstance(platen_sp, (int, float)) else "",
                f"{platen_temp:.3f}" if isinstance(platen_temp, (int, float)) else "",
                f"{v:.3f}" if isinstance(v, (int, float)) else "",
                f"{c:.3f}" if isinstance(c, (int, float)) else "",
                str(bool(out)) if out is not None else "",
                f"{tc1:.3f}" if isinstance(tc1, (int, float)) else "",
                f"{tc2:.3f}" if isinstance(tc2, (int, float)) else "",
                f"{pressure_actual:.3f}" if isinstance(pressure_actual, (int, float)) else "",
                f"{pressure_setpoint:.3f}" if isinstance(pressure_setpoint, (int, float)) else "",
                str(pressure_mode) if pressure_mode is not None else "",
                str(bool(pin_pout_functional)) if pin_pout_functional is not None else "",
                str(bool(sig_a_performance)) if sig_a_performance is not None else "",
                str(bool(na_performance)) if na_performance is not None else "",
                # Optionally include DAQ data if available
                str(bool(daq_snapshot.get("rf_on_off"))) if isinstance(daq_snapshot, dict) and "rf_on_off" in daq_snapshot else "",
                str(daq_snapshot.get("fault_status")) if isinstance(daq_snapshot, dict) and "fault_status" in daq_snapshot else "",
                str(daq_snapshot.get("bandpath")) if isinstance(daq_snapshot, dict) and "bandpath" in daq_snapshot else "",
                str(int(daq_snapshot.get("gain_value"))) if isinstance(daq_snapshot, dict) and isinstance(daq_snapshot.get("gain_value"), (int, float)) else "",
                str(daq_snapshot.get("date_string")) if isinstance(daq_snapshot, dict) and "date_string" in daq_snapshot else "",
                str(float(daq_snapshot.get("temp_value"))) if isinstance(daq_snapshot, dict) and isinstance(daq_snapshot.get("temp_value"), (int, float)) else "",
            ]
            with open(self.telemetry_path, "a", encoding="utf-8") as f:
                f.write(",".join(map(str, line)) + "\n")

            # Also emit to live user callback if any (avoid the CSV proxy to prevent duplicate writes)
            if self._user_telemetry_callback is not None:
                try:
                    payload = {
                        "timestamp": dt.datetime.now(),
                        "step_index": idx,
                        "step_name": name,
                        "cycle_type": cycle,
                        "phase": phase,
                        "target_c": float(target) if isinstance(target, (int, float)) else None,
                        "platen_setpoint_c": float(platen_sp) if isinstance(platen_sp, (int, float)) else None,
                        "platen_temp_c": float(platen_temp) if isinstance(platen_temp, (int, float)) else None,
                        "psu_voltage": float(v) if isinstance(v, (int, float)) else None,
                        "psu_current": float(c) if isinstance(c, (int, float)) else None,
                        "psu_output": bool(out) if out is not None else None,
                        "sample_1": float(tc1) if isinstance(tc1, (int, float)) else None,
                        "sample_2": float(tc2) if isinstance(tc2, (int, float)) else None,
                        "pressure_torr": float(pressure_actual) if isinstance(pressure_actual, (int, float)) else None,
                        "pressure_setpoint": float(pressure_setpoint) if isinstance(pressure_setpoint, (int, float)) else None,
                        "tests_pin_pout_functional": bool(pin_pout_functional) if pin_pout_functional is not None else None,
                        "tests_sig_a_performance": bool(sig_a_performance) if sig_a_performance is not None else None,
                        "tests_na_performance": bool(na_performance) if na_performance is not None else None,
                    }
                    self._user_telemetry_callback(payload)
                except (RuntimeError, ValueError, TypeError):
                    # Never allow GUI callback failures to break the cycle
                    pass
        except (OSError, ValueError, TypeError):
            # Do not break cycle on telemetry failure
            pass

    def _maybe_log_telemetry(self, phase: str, step=None, setpoint_c: Optional[float] = None,
                              pin_pout_functional: Optional[bool] = None,
                              sig_a_performance: Optional[bool] = None,
                              na_performance: Optional[bool] = None):
        now = time.time()
        if now - self._telemetry_last_ts >= 2.5:
            self._log_telemetry(phase=phase, step=step, setpoint_c=setpoint_c,
                                pin_pout_functional=pin_pout_functional,
                                sig_a_performance=sig_a_performance,
                                na_performance=na_performance)
            self._telemetry_last_ts = now

    # --------- Tests integration ---------
    def _map_step_tests(self, step) -> tuple[bool, bool, bool]:
        """Map profile flags to test families and golden mode.

        Only the following flags are considered:
        - pin_pout_functional (or pin_pout_functional_tests) golden tests
        - sig_a_performance (or sig_a_performance_tests)
        - na_performance (or na_performance_tests)

        Returns (sig_a_enabled, na_enabled, golden_tests).
        """
        pin_func = bool(
            getattr(step, "pin_pout_functional_tests", False)
            or getattr(step, "pin_pout_functional", False)
        )
        sig_a_perf = bool(
            getattr(step, "sig_a_performance_tests", False)
            or getattr(step, "sig_a_performance", False)
        )
        na_perf = bool(
            getattr(step, "na_performance_tests", False)
            or getattr(step, "na_performance", False)
        )

        return sig_a_perf, na_perf, pin_func

    def _run_tests_for_step(self, step) -> None:
        sig_a_perf, na_perf, pin_func = self._map_step_tests(step)
        # Re-attach composite callback before tests in case something overwrote it
        self._attach_test_manager_csv_callback()

        # Paths list (may be None or empty)
        try:
            paths = getattr(self.test_manager, "paths", None)
            if not isinstance(paths, (list, tuple)):
                paths = []
        except (AttributeError, TypeError):
            paths = []

        # Run tests via the public aggregator if available
        for path in paths or [None]:
            self._log_telemetry(
                phase="testing",
                step=step,
                pin_pout_functional=pin_func,
                sig_a_performance=sig_a_perf,
                na_performance=na_perf,
            )
            try:
                if pin_func:
                    self.test_manager._run_pin_pout_functional_tests(path=path)

                if sig_a_perf:
                    self.test_manager._run_sig_a_performance_tests(path=path)

                if na_perf:
                    self.test_manager._run_na_performance_tests(path=path)

            except (RuntimeError, OSError, ValueError, TypeError) as e:
                log_message(f"Tests failed to execute: {e}")
            finally:
                self._log_telemetry(
                    phase="testing",
                    step=step,
                    pin_pout_functional=pin_func,
                    sig_a_performance=sig_a_perf,
                    na_performance=na_perf,
                )

    def _initialize_tvac_system(self):
        """Initialize TVAC system for thermal cycling."""
        if self.tvac_controller is None:
            log_message("TVAC controller not available - running in simulation mode")
            return
        
        try:
            # Ensure we have control
            status = self.tvac_controller.request_control()
            if status != AutoExplorStatus.SUCCESS:
                log_message(f"Warning: Could not request TVAC control (status: {status})")
            
            # Turn on main power if not already on
            power_status, power_state = self.tvac_controller.get_button_state(ButtonID.POWER)
            if power_status == AutoExplorStatus.SUCCESS.value and not power_state['on_off']:
                log_message("Turning on TVAC system power")
                self.tvac_controller.set_button_state(ButtonID.POWER, True)
                time.sleep(5)  # Wait for system to power up
            
            # Get system status
            tvac_snapshot = self._get_tvac_snapshot()
            log_message(f"TVAC system initialized - Power: {tvac_snapshot.get('power_on')}, Vent: {tvac_snapshot.get('vent_open')}, Rough: {tvac_snapshot.get('rough_pump_on')}")
            
            # Log available temperature readings
            temp_readings = tvac_snapshot.get('temp_readings', {})
            if temp_readings:
                log_message("Available TVAC temperature readings:")
                for name, info in temp_readings.items():
                    if info['is_valid']:
                        log_message(f"  {name}: {info['formatted_value']}")
            
            # Log available pressure readings
            pressure_readings = tvac_snapshot.get('pressure_readings', {})
            if pressure_readings:
                log_message("Available TVAC pressure readings:")
                for name, info in pressure_readings.items():
                    if info['is_valid']:
                        log_message(f"  {name}: {info['formatted_value']}")
            
            # Log pressure control mode and available modes
            pressure_info = tvac_snapshot.get('pressure_setpoint_info', {})
            if pressure_info:
                current_mode = pressure_info.get('current_mode')
                available_modes = pressure_info.get('available_modes', [])
                log_message(f"Pressure control mode: {current_mode}, Available modes: {available_modes}")
            
        except Exception as e:
            log_message(f"Error initializing TVAC system: {e}")

    def run_thermal_cycle(self, profile_path):
        """Execute the temperature steps defined in a profile JSON file."""
        # Initialize TVAC system before starting cycle
        self._initialize_tvac_system()
        
        self.temp_profile_manager = TempProfileManager(profile_path)
        all_steps = self.temp_profile_manager.get_all_steps()

        log_message(f"Loaded thermal profile '{profile_path}' with {len(all_steps)} steps")

        for idx, step in enumerate(all_steps, start=1):
            # store index for telemetry
            setattr(step, "_index", idx)
            target_c = float(getattr(step, "temperature", 0.0) or 0.0)
            target_temp_delta_c = float(getattr(step, "target_temp_delta", 0.0) or 0.0)
            offset_c = float(getattr(step, "temp_controller_offset", 0.0) or 0.0)
            setpoint_c = target_c + offset_c
            tol_c = float(getattr(step, "settlement_tolerance", 0.6) or 0.6)
            window_s = int(getattr(step, "settlement_window", 300) or 300)
            poll_s = int(getattr(step, "monitoring_interval", 3) or 3)
            initial_delay_s = int(getattr(step, "initial_delay", 60) or 60)
            dwell_min = float(getattr(step, "total_time", 0) or 0)
            try:
                dwell_s = int(float(dwell_min) * 60 * max(0.01, float(self.dwell_scale)))
            except (TypeError, ValueError):
                dwell_s = int(dwell_min * 60)
            cycle_type = getattr(step, "temp_cycle_type", "").upper()
            self.current_step = step
            log_message("-" * 60)
            log_message(f"Step {idx}/{len(all_steps)} | {getattr(step, 'step_name', 'Unnamed')} | {cycle_type}")
            log_message(f"Target {target_c:.2f} C (setpoint {setpoint_c:.2f} C, tol ±{tol_c:.2f} C)")

            sig_a_perf, na_perf, pin_func = self._map_step_tests(step)

            self._log_telemetry(
                phase="start",
                step=step,
                setpoint_c=setpoint_c,
                sig_a_performance=sig_a_perf,
                na_performance=na_perf,
                pin_pout_functional=pin_func
            )

            # Apply PSU state per step
            self._apply_power_for_step(getattr(step, "voltage", 0.0) or 0.0, getattr(step, "current", 0.0) or 0.0)
            
            # Apply pressure control if specified in step
            pressure_setpoint = getattr(step, "pressure_torr", None)
            pressure_mode = getattr(step, "pressure_mode", None)
            
                
            if pressure_setpoint is not None:
                try:
                    pressure_val = float(pressure_setpoint)
                    self._set_pressure_setpoint(pressure_val)
                    log_message(f"Pressure setpoint -> {pressure_val:.3f} Torr, mode: {pressure_mode}")
                except (ValueError, TypeError):
                    log_message(f"Invalid pressure setpoint: {pressure_setpoint}")
            
            # Apply setpoint once per step; control/wait happens below per type
            self._set_setpoint(setpoint_c=setpoint_c)

            # Handle by step type
            if cycle_type == "RAMP":
                # For ramps, wait until we're within target +/- target_temp_delta or for configured dwell time
                target_delta = float(getattr(step, "target_temp_delta", tol_c) or tol_c)
                log_message(f"RAMP: waiting for thermocouples within ±{target_delta} C of target")
                self._wait_until_stable(target_c=target_c, target_temp_delta_c=target_delta, tol_c=tol_c, window_s=window_s, poll_s=poll_s, initial_delay_s=initial_delay_s, temp_offset=offset_c)
                self._maybe_log_telemetry(
                    phase="ramp",
                    step=step,
                    setpoint_c=setpoint_c,
                    pin_pout_functional=pin_func,
                    sig_a_performance=sig_a_perf,
                    na_performance=na_perf,
                )
                time.sleep(max(1, int(poll_s)))
                log_message("RAMP: target band reached via thermocouples")
            elif cycle_type in ("DWELL", "SOAK"):
                # Wait to be stable within tolerance window, then dwell for the specified time
                self._wait_until_stable(target_c=target_c, target_temp_delta_c=target_temp_delta_c, tol_c=tol_c, window_s=window_s, poll_s=poll_s, initial_delay_s=initial_delay_s, temp_offset=offset_c)

                if dwell_s > 0:
                    log_message(f"Dwelling at target for {dwell_s}s")
                    end = time.time() + dwell_s
                    while time.time() < end:
                        # sp = self._control_update_if_enabled(target_c, poll_s=float(max(2.5, poll_s)))
                        self._maybe_log_telemetry(
                            phase="dwell",
                            step=step,
                            setpoint_c=setpoint_c,
                            pin_pout_functional=pin_func,
                            sig_a_performance=sig_a_perf,
                            na_performance=na_perf,
                        )

                self._run_tests_for_step(step)
            elif cycle_type == "INT_CYCLE":
                cycle_count = int(getattr(step, "num_cycles", 1) or 1)
                high_temp = float(getattr(step, "high_temp", 0.0) or 0.0)
                high_temp_offset = float(getattr(step, "high_temp_offset", 0.0) or 0.0)
                low_temp = float(getattr(step, "low_temp", 0.0) or 0.0)
                low_temp_offset = float(getattr(step, "low_temp_offset", 0.0) or 0.0)
                time_per_band = float(getattr(step, "time_per_path", 0.0) or 0.0) * 60.0  # minutes -> seconds
                paths = getattr(self.test_manager, "paths", [])
                even_cycle_voltage = float(getattr(step, "even_cycle_voltage", 0.0) or 0.0)
                odd_cycle_voltage = float(getattr(step, "odd_cycle_voltage", 0.0) or 0.0)
                soak_s = int(float(getattr(step, "soak_time_after_switch", 0) or 0) * 60)  # minutes -> seconds

                low_temp_sp = low_temp + low_temp_offset
                high_temp_sp = high_temp + high_temp_offset

                for i in range(cycle_count):
                    log_message(f"INT_CYCLE: Starting cycle {i + 1}/{cycle_count}")
                    if i % 2 == 0:
                        self._apply_power_for_step(even_cycle_voltage, getattr(step, "current", 0.0) or 0.0)
                    else:
                        self._apply_power_for_step(odd_cycle_voltage, getattr(step, "current", 0.0) or 0.0)

                    self._set_setpoint(setpoint_c=high_temp_sp)
                    self._wait_until_stable(target_c=high_temp, target_temp_delta_c=target_temp_delta_c, tol_c=tol_c, window_s=window_s, poll_s=poll_s, initial_delay_s=initial_delay_s, temp_offset=high_temp_offset)
                    for path in paths:
                        self.test_manager._run_pin_pout_functional_rolling(path=path, time_per_path=time_per_band)


                    log_message(f"Dwelling at target for {soak_s}s")
                    end = time.time() + soak_s
                    while time.time() < end:
                        # sp = self._control_update_if_enabled(target_c, poll_s=float(max(2.5, poll_s)))
                        self._maybe_log_telemetry(
                            phase="soak",
                            step=step,
                            setpoint_c=setpoint_c,
                            pin_pout_functional=pin_func,
                            sig_a_performance=sig_a_perf,
                            na_performance=na_perf,
                        )


                    self._apply_power_for_step(0.0, 0.0)  # turn off PSU between high and low

                    self._set_setpoint(setpoint_c=low_temp_sp)
                    self._wait_until_stable(target_c=low_temp, target_temp_delta_c=target_temp_delta_c, tol_c=tol_c, window_s=window_s, poll_s=poll_s, initial_delay_s=initial_delay_s, temp_offset=low_temp_offset)
                    if i % 2 == 0:
                        self._apply_power_for_step(even_cycle_voltage, getattr(step, "current", 0.0) or 0.0)
                    else:
                        self._apply_power_for_step(odd_cycle_voltage, getattr(step, "current", 0.0) or 0.0)


                    for path in paths:
                        self.test_manager._run_pin_pout_functional_rolling(path=path, time_per_path=time_per_band)

                    log_message(f"Dwelling at target for {soak_s}s")
                    end = time.time() + soak_s
                    while time.time() < end:
                        # sp = self._control_update_if_enabled(target_c, poll_s=float(max(2.5, poll_s)))
                        self._maybe_log_telemetry(
                            phase="soak",
                            step=step,
                            setpoint_c=setpoint_c,
                            pin_pout_functional=pin_func,
                            sig_a_performance=sig_a_perf,
                            na_performance=na_perf,
                        )

            # Optional: turn off power after this step
            if getattr(step, "power_off_after", False):
                self._power_off()

            self._log_telemetry(
                phase="step_complete",
                step=step,
                setpoint_c=0,
                pin_pout_functional=pin_func,
                sig_a_performance=sig_a_perf,
                na_performance=na_perf,
            )


        log_message("Thermal cycle complete")