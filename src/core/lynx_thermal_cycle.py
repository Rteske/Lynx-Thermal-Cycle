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

class LynxThermalCycleManager:
    def __init__(self, simulation_mode=False, dwell_scale: float = 1.0):
        """
        Initialize the Lynx Thermal Cycle Manager.
        
        Args:
            simulation_mode (bool): If True, uses simulated instruments. If False, uses real hardware.
        """
        self.simulation_mode = simulation_mode
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
                self.temp_probe = None
                self.temp_probe2 = None
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

        # Initialize temperature controller and turn chamber ON
        try:
            if not simulation_mode:
                # Lazy import to avoid requiring pyserial in simulation mode
                from instruments.temp_controller import TempController  # type: ignore
                self.temp_controller = TempController()
                self.temp_channel = 1
            else:
                # Use simulated temperature controller
                self.temp_controller = None
                self.temp_channel = 1
                print("Using simulated temperature controller")
            log_message("TempController initialized and chamber turned ON")
        except (SerialException, OSError, RuntimeError) as e:
            # If we can't connect, keep None and operate in no-op mode
            self.temp_controller = None
            self.temp_channel = 1
            log_message(f"TempController not available: {e}")

        # Provide temp controller reference to the top-level test manager so it can enrich telemetry safely
        self.test_manager.set_temp_controller(self.temp_controller, self.temp_channel)
        # Telemetry CSV setup
        try:
            logs_dir = os.path.join(os.getcwd(), "logs")
            os.makedirs(logs_dir, exist_ok=True)
            ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.telemetry_path = os.path.join(logs_dir, f"thermal_cycle_telemetry_{ts}.csv")
            if not os.path.exists(self.telemetry_path):
                with open(self.telemetry_path, "w", encoding="utf-8") as f:
                    f.write(
                        "timestamp,step_index,step_name,cycle_type,phase,target_c,setpoint_c,actual_temp_c," \
                        "psu_voltage,psu_current,psu_output,tc1_temp,tc2_temp," \
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
        if self.temp_controller is None:
            log_message(f"[SIM] Would set chamber setpoint to {setpoint_c:.2f} C")
            return
        try:
            self.temp_controller.set_setpoint(self.temp_channel, setpoint_c)
            log_message(f"Chamber setpoint -> {setpoint_c:.2f} C (CH{self.temp_channel})")
            # Wait until the temp_controller actual temperature of the plate finishes updating
            self.temp_controller.set_chamber_state(True)

            timeout = 30  # seconds
            start_time = time.time()
            while True:
                actual_temp = self._read_actual_temp()
                if actual_temp is not None:
                    break
                if time.time() - start_time >= timeout:
                    log_message("Setpoint applied; no controller reading yet (timeout). Proceeding.")
                    break
                self._maybe_log_telemetry(phase="setpoint-wait", step=self.current_step, setpoint_c=setpoint_c)
                time.sleep(0.5)
        except (SerialException, ValueError, OSError) as e:
            log_message(f"Failed to set setpoint: {e}")

    def _read_actual_temp(self) -> Optional[float]:
        if self.temp_controller is None:
            return None
        try:
            self.temp_controller.connector.read_to_clear()
            raw = self.temp_controller.query_actual(self.temp_channel)
            # raw may be bytes like b' +25.3' or similar; try to extract a floa
            return float(raw)
        except (SerialException, ValueError, OSError):
            return None

    def _tcs_within_band(self, target_c: float, tol_c: float) -> tuple[bool, int, list[float]]:
        """Check if available thermocouples are within target±tol.
        Returns (all_ok, count_present, values_present). If no TCs present, (False, 0, [])."""
        tc1, _ = self._get_tc_snapshot()
        # Use only the primary temp_probe (tc1) for control decisions
        vals: list[float] = [float(tc1)] if isinstance(tc1, (int, float)) else []
        if not vals:
            return False, 0, []
        all_ok = all(abs(v - target_c) <= tol_c for v in vals)
        return all_ok, len(vals), vals

    def _get_pid_measurement(self, _target_c: float) -> Optional[float]:
        """Get temperature measurement for PID control - prefers TC1 probe via duck typing."""
        try:
            tc = getattr(self.test_manager, "temp_probe", None)
            # Duck-typing: any object with measure_temp() is acceptable
            if tc is not None and hasattr(tc, "measure_temp"):
                temp = tc.measure_temp()  # type: ignore[attr-defined]
                if isinstance(temp, (int, float)):
                    return float(temp)
        except (RuntimeError, OSError, ValueError) as e:
            log_message(f"Error reading temp_probe: {e}")

    def _calculate_stability(self, window_values: list[tuple[float, float]], window_duration: int, min_time_s: float = 30.0) -> tuple[float, bool, float, int]:
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
                if self.temp_controller is None:
                    log_message(f"[SIM] PID: setpoint -> {sp:.2f} C")
                else:
                    self.temp_controller.set_setpoint(self.temp_channel, sp)
                    # Brief wait for setpoint to take effect
                    time.sleep(5)
                    log_message(f"PID: setpoint -> {sp:.2f} C (CH{self.temp_channel})")
            except (SerialException, ValueError, OSError) as e:
                log_message(f"PID: failed to set setpoint: {e}")

        # Measurement function (prefer TC1; fallback to controller)
        def read_meas() -> Optional[float]:
            v = self._get_pid_measurement(target_c)
            return v if isinstance(v, (int, float)) else self._read_actual_temp()

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
        phase1_window_s = max(30, window_s // 4)  # Quarter of main window, minimum 30s
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
            min_stability_time = max(15.0, phase1_window_s * 0.5)  # At least 15s or half the window
            span, has_enough_time, coverage_s, sample_count = self._calculate_stability(
                phase1_window_values, phase1_window_s, min_time_s=min_stability_time
            )
            is_stable = span <= (float(tol_c) * stability_threshold)  # 75% of tolerance requirement

            log_message(
                f"PHASE 1: temp={meas:.2f}C target={target_c:.2f}C band_err={band_err:.3f}C in_band={in_band} "
                f"span={span:.3f}C stable={is_stable} cov={coverage_s:.1f}s time_ok={has_enough_time} elapsed={phase1_elapsed:.1f}s"
            )
            self._maybe_log_telemetry(phase="phase1-approach", step=self.current_step, setpoint_c=sp)

            # Check if we're in the target band
            if in_band:
                log_message("PHASE 1: TC reached target band — proceeding to settlement phase")
                break

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
                    magnitude_factor = 120  # seconds per degree of adjustment (2 minutes per degree)
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

            # Check timeout
            if phase1_elapsed > max_phase1_time_s:
                log_message("PHASE 1: Maximum time reached — proceeding to phase 2")
                break

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

        Includes: setpoint_c, actual_temp_c, psu_voltage, psu_current, psu_output,
        tc1_temp, tc2_temp, and DAQ fields (rf_on_off, fault_status, bandpath,
        gain_value, date_string, temp_value). Missing values are returned as None.
        """
        snapshot: Dict[str, Any] = {}
        # Temp controller setpoint and actual
        try:
            sp = None
            if getattr(self, "temp_controller", None) is not None:
                try:
                    sp = float(self.temp_controller.query_setpoint(self.temp_channel))
                except Exception:
                    sp = None
            snapshot["setpoint_c"] = sp
        except Exception:
            snapshot["setpoint_c"] = None

        try:
            snapshot["actual_temp_c"] = self._read_actual_temp()
        except Exception:
            snapshot["actual_temp_c"] = None

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

        # Thermocouples
        try:
            tc1, tc2 = self._get_tc_snapshot()
            snapshot["tc1_temp"] = float(tc1) if isinstance(tc1, (int, float)) else None
            snapshot["tc2_temp"] = float(tc2) if isinstance(tc2, (int, float)) else None
        except Exception:
            snapshot["tc1_temp"] = None
            snapshot["tc2_temp"] = None

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
        target_c, setpoint_c, actual_temp_c, psu_voltage, psu_current, psu_output,
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

            sp = payload.get("setpoint_c")
            if sp is None and self.temp_controller is not None:
                try:
                    sp = float(self.temp_controller.query_setpoint(self.temp_channel))
                except Exception:
                    sp = None

            actual = payload.get("actual_temp_c")
            if actual is None:
                actual = self._read_actual_temp()

            # PSU/TC snapshots from payload with fallback to live reads
            v = payload.get("psu_voltage")
            c = payload.get("psu_current")
            out = payload.get("psu_output")
            if v is None or c is None or out is None:
                pv, pc, pout = self._get_psu_snapshot()
                v = v if isinstance(v, (int, float)) else pv
                c = c if isinstance(c, (int, float)) else pc
                out = out if isinstance(out, bool) else pout

            tc1 = payload.get("tc1_temp")
            tc2 = payload.get("tc2_temp")
            if tc1 is None or tc2 is None:
                _tc1, _tc2 = self._get_tc_snapshot()
                tc1 = tc1 if isinstance(tc1, (int, float)) else _tc1
                tc2 = tc2 if isinstance(tc2, (int, float)) else _tc2

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
                f"{float(sp):.3f}" if isinstance(sp, (int, float)) else "",
                f"{float(actual):.3f}" if isinstance(actual, (int, float)) else "",
                f"{float(v):.3f}" if isinstance(v, (int, float)) else "",
                f"{float(c):.3f}" if isinstance(c, (int, float)) else "",
                str(bool(out)) if out is not None else "",
                f"{float(tc1):.3f}" if isinstance(tc1, (int, float)) else "",
                f"{float(tc2):.3f}" if isinstance(tc2, (int, float)) else "",
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
        """Read temperatures from attached thermocouples if available."""
        tc1_temp = tc2_temp = None
        tc1 = getattr(self.test_manager, "temp_probe", None)
        tc2 = getattr(self.test_manager, "temp_probe2", None)
        try:
            if tc1 is not None and hasattr(tc1, "measure_temp"):
                tc1_temp = tc1.measure_temp()  # type: ignore[attr-defined]
        except (OSError, ValueError):
            pass

        try:
            if tc2 is not None and hasattr(tc2, "measure_temp"):
                tc2_temp = tc2.measure_temp()  # type: ignore[attr-defined]
        except (OSError, ValueError):
            pass

        return tc1_temp, tc2_temp

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
            sp: Optional[float] = None
            if self.temp_controller is not None:
                try:
                    sp = float(self.temp_controller.query_setpoint(self.temp_channel))
                except (OSError, ValueError, RuntimeError, TypeError):
                    sp = None
            if sp is None and setpoint_c is not None:
                try:
                    sp = float(setpoint_c)
                except (ValueError, TypeError):
                    sp = None
            actual = self._read_actual_temp()
            v, c, out = self._get_psu_snapshot()
            tc1, tc2 = self._get_tc_snapshot()

            daq_snapshot = self._get_daq_snapshot()

            line = [
                dt.datetime.now().isoformat(),
                idx if idx is not None else "",
                name,
                cycle,
                phase,
                f"{target:.3f}" if isinstance(target, (int, float)) else "",
                f"{sp:.3f}" if isinstance(sp, (int, float)) else "",
                f"{actual:.3f}" if isinstance(actual, (int, float)) else "",
                f"{v:.3f}" if isinstance(v, (int, float)) else "",
                f"{c:.3f}" if isinstance(c, (int, float)) else "",
                str(bool(out)) if out is not None else "",
                f"{tc1:.3f}" if isinstance(tc1, (int, float)) else "",
                f"{tc2:.3f}" if isinstance(tc2, (int, float)) else "",
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
                        "setpoint_c": float(sp) if isinstance(sp, (int, float)) else None,
                        "actual_temp_c": float(actual) if isinstance(actual, (int, float)) else None,
                        "psu_voltage": float(v) if isinstance(v, (int, float)) else None,
                        "psu_current": float(c) if isinstance(c, (int, float)) else None,
                        "psu_output": bool(out) if out is not None else None,
                        "tc1_temp": float(tc1) if isinstance(tc1, (int, float)) else None,
                        "tc2_temp": float(tc2) if isinstance(tc2, (int, float)) else None,
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

    def run_thermal_cycle(self, profile_path):
        """Execute the temperature steps defined in a profile JSON file."""
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

                # Run tests (if any) once stable
                self._run_tests_for_step(step)

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