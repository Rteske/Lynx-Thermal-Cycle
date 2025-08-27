import time
import re
from typing import Optional, Callable, Dict, Any, Tuple
import os
import datetime as dt

class SerialException(Exception):
    pass
try:
    from pyvisa.errors import VisaIOError  # type: ignore
except ImportError:
    class VisaIOError(Exception):
        pass

from instruments.temp_probe import Agilent34401A
from src.core.lynx_pa_top_level_test_manager import PaTopLevelTestManager
from src.core.temp import TempProfileManager
from instruments.temp_controller import TempController
from src.utils.logging_utils import log_message

class LynxThermalCycleManager:
    def __init__(self, simulation_mode=False):
        """
        Initialize the Lynx Thermal Cycle Manager.
        
        Args:
            simulation_mode (bool): If True, uses simulated instruments. If False, uses real hardware.
        """
        self.simulation_mode = simulation_mode
        self.test_manager = PaTopLevelTestManager(sim=simulation_mode)
        self.temp_profile_manager = None
        self.telemetry_callback = None  # set via set_telemetry_callback

        # Initialize temperature controller and turn chamber ON
        try:
            if not simulation_mode:
                self.temp_controller = TempController()
                self.temp_controller.set_chamber_state(True)
                self.temp_channel = 1
            else:
                # Use simulated temperature controller
                self.temp_controller = None  # Will be replaced with simulated version
                self.temp_channel = 1
                print("Using simulated temperature controller")
            log_message("TempController initialized and chamber turned ON")
        except (SerialException, OSError, RuntimeError) as e:
            # If we can't connect, keep None and operate in no-op mode
            self.temp_controller = None
            self.temp_channel = 1
            log_message(f"TempController not available: {e}")

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
                        "psu_voltage,psu_current,psu_output,tc1_temp,tc2_temp,tests_sig_a_enabled,tests_na_enabled," \
                        "tests_sig_a_executed,tests_na_executed\n"
                    )
            log_message(f"Telemetry CSV -> {self.telemetry_path}")
        except OSError as e:
            log_message(f"Failed to initialize telemetry CSV: {e}")
            self.telemetry_path = None
        self._telemetry_last_ts = 0.0
        # track current step for telemetry
        self.current_step = None

        # PID runtime state (per-step)
        self._pid_enabled = False
        self._pid_base_setpoint = None
        self._pid_sp_current = None
        self._pid_last_ts = None
        self._pid_source = "avg"  # 'avg' | 'any' | 'controller'
        self._pid_deadband = 0.0
        self._pid = None
        # Upgrades
        self._pid_interval_sec = 0.0
        self._pid_last_update = None
        self._pid_meas_ema = None
        self._pid_filter_alpha = 0.0
        self._pid_deriv_on_meas = False
        self._pid_integral_band = None
        self._pid_backcalc_k = 0.0
        self._pid_sp_rate_limit = None
        self._pid_last_sp_ts = None
        
        # Two-stage PID control state
        self._pid_two_stage_enabled = False
        self._pid_approach_params = None
        self._pid_stabilization_params = None
        self._stabilization_trigger_delta = 2.0
        self._stabilization_time_required = 45
        self._stabilization_consecutive_readings = 10
        self._current_pid_phase = "approach"  # "approach" or "stabilization"
        self._stabilization_start_time = None
        self._stabilization_consecutive_count = 0
        self._stabilization_achieved = False

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
        except (SerialException, ValueError, OSError) as e:
            log_message(f"Failed to set setpoint: {e}")

    def _read_actual_temp(self) -> Optional[float]:
        if self.temp_controller is None:
            return None
        try:
            raw = self.temp_controller.query_actual(self.temp_channel)
            # raw may be bytes like b' +25.3' or similar; try to extract a float
            if isinstance(raw, (bytes, bytearray)):
                text = raw.decode(errors="ignore")
            else:
                text = str(raw)
            m = re.search(r"[-+]?\d+(?:\.\d+)?", text)
            return float(m.group(0)) if m else None
        except (SerialException, ValueError, OSError):
            return None

    def _tcs_within_band(self, target_c: float, tol_c: float) -> tuple[bool, int, list[float]]:
        """Check if available thermocouples are within target±tol.
        Returns (all_ok, count_present, values_present). If no TCs present, (False, 0, [])."""
        tc1, tc2 = self._get_tc_snapshot()
        # Use only the primary temp_probe (tc1) for control decisions
        vals: list[float] = [float(tc1)] if isinstance(tc1, (int, float)) else []
        if not vals:
            return False, 0, []
        all_ok = all(abs(v - target_c) <= tol_c for v in vals)
        return all_ok, len(vals), vals

    # --------- PID helpers ---------
    class SimplePID:
        def __init__(self, kp: float, ki: float, kd: float,
                     output_limits: Tuple[float, float] = (-10.0, 10.0),
                     derivative_on_meas: bool = False,
                     backcalc_k: float = 0.0,
                     integral_band: Optional[float] = None):
            self.kp = float(kp)
            self.ki = float(ki)
            self.kd = float(kd)
            self.out_min, self.out_max = output_limits
            self.integral = 0.0
            self.prev_error: Optional[float] = None
            self.prev_meas: Optional[float] = None
            self.derivative_on_meas = bool(derivative_on_meas)
            self.backcalc_k = float(backcalc_k)
            self.integral_band = float(integral_band) if isinstance(integral_band, (int, float)) else None

        def reset(self):
            self.integral = 0.0
            self.prev_error = None
            self.prev_meas = None

        def compute(self, error: float, delta_t: float, meas: Optional[float] = None) -> float:
            delta_t = max(0.05, float(delta_t))
            # Proportional
            p = self.kp * error
            # Integral with simple anti-windup clamp
            do_integrate = True
            if self.integral_band is not None and abs(error) > self.integral_band:
                do_integrate = False
            if do_integrate:
                self.integral += error * delta_t
            # Clamp integral reasonably so it doesn't run away
            max_int = 10.0 / (self.ki if self.ki != 0 else 1.0)
            if self.integral > max_int:
                self.integral = max_int
            elif self.integral < -max_int:
                self.integral = -max_int
            i = self.ki * self.integral
            # Derivative (on error)
            if self.derivative_on_meas and meas is not None and self.prev_meas is not None:
                d_meas = (meas - self.prev_meas) / delta_t
                d = -self.kd * d_meas  # negative sign for derivative on measurement
            else:
                d_err = 0.0 if self.prev_error is None else (error - self.prev_error) / delta_t
                d = self.kd * d_err
            self.prev_error = error
            if meas is not None:
                self.prev_meas = meas
            u = p + i + d
            # Anti-windup back-calculation and clamp
            u_clamped = max(self.out_min, min(self.out_max, u))
            if self.backcalc_k > 0.0:
                self.integral += self.backcalc_k * (u_clamped - u)
                # Recompute with updated integral
                i = self.ki * self.integral
                u = p + i + d
                u_clamped = max(self.out_min, min(self.out_max, u))
            return u_clamped

    def _switch_pid_phase(self, new_phase: str, target_c: float):
        """Switch between approach and stabilization PID phases."""
        if not self._pid_two_stage_enabled or new_phase == self._current_pid_phase:
            return
            
        self._current_pid_phase = new_phase
        log_message(f"Switching PID to {new_phase} phase")
        
        if new_phase == "stabilization":
            params = self._pid_stabilization_params
            self._stabilization_start_time = time.time()
            self._stabilization_consecutive_count = 0
        else:
            params = self._pid_approach_params
            self._stabilization_start_time = None
            self._stabilization_consecutive_count = 0
            
        # Update PID parameters
        if params:
            self._pid.kp = params.get("pid_kp", 0.6)
            self._pid.ki = params.get("pid_ki", 0.05) 
            self._pid.kd = params.get("pid_kd", 0.0)
            max_off = params.get("pid_max_offset", 8.0)
            self._pid.out_min = -abs(max_off)
            self._pid.out_max = abs(max_off)
            self._pid_sp_rate_limit = params.get("pid_sp_rate_limit", 1.0)
            
            log_message(f"PID {new_phase} params: kp={self._pid.kp}, ki={self._pid.ki}, kd={self._pid.kd}, "
                       f"max_offset=±{max_off}, rate_limit={self._pid_sp_rate_limit}")
    
    def _check_stabilization_status(self, target_c: float, meas: float) -> bool:
        """Check if we should switch phases or if stabilization is complete."""
        if not self._pid_two_stage_enabled:
            return True  # Always stable if not using two-stage
        
        # Determine effective trigger delta for switching:
        # Prefer step's target_temp_delta or settlement_tolerance if available, else use configured stabilization_trigger_delta
        eff_trigger = float(self._stabilization_trigger_delta)
        step = getattr(self, "current_step", None)
        try:
            if step is not None:
                step_target_delta = getattr(step, "target_temp_delta", None)
                step_tol = getattr(step, "settlement_tolerance", None)
                cand = []
                if isinstance(step_target_delta, (int, float)):
                    cand.append(float(step_target_delta))
                if isinstance(step_tol, (int, float)):
                    cand.append(float(step_tol))
                if cand:
                    # Use the larger of available step thresholds to switch sooner
                    eff_trigger = max([eff_trigger] + cand)
        except Exception:
            pass
        within_trigger = abs(meas - target_c) <= eff_trigger
        
        if self._current_pid_phase == "approach" and within_trigger:
            # Switch to stabilization phase
            try:
                err = abs(meas - target_c)
                log_message(f"Two-stage PID: entering stabilization (|Δ|={err:.2f}°C <= trigger {eff_trigger:.2f}°C)")
            except Exception:
                pass
            self._switch_pid_phase("stabilization", target_c)
            return False
            
        elif self._current_pid_phase == "stabilization":
            if within_trigger:
                self._stabilization_consecutive_count += 1
                if self._stabilization_consecutive_count >= self._stabilization_consecutive_readings:
                    # Check if we've been stable long enough
                    if self._stabilization_start_time is not None:
                        stable_time = time.time() - self._stabilization_start_time
                        if stable_time >= self._stabilization_time_required:
                            self._stabilization_achieved = True
                            log_message(f"Stabilization complete: {self._stabilization_consecutive_count} readings over {stable_time:.1f}s (trigger ±{eff_trigger}°C)")
                            return True
            else:
                # Reset consecutive count if outside tolerance
                self._stabilization_consecutive_count = 0
                
        return self._stabilization_achieved

    def _get_pid_measurement(self, target_c: float) -> Optional[float]:
        """Get temperature measurement for PID control - uses only temp_probe"""
        # Use only the primary temp_probe for the real temperature measurement
        try:
            tc = getattr(self.test_manager, "temp_probe", None)
            if isinstance(tc, Agilent34401A):
                temp = tc.measure_temp()
                if isinstance(temp, (int, float)):
                    return float(temp)
        except Exception as e:
            log_message(f"Error reading temp_probe: {e}")
        
        # Fallback to controller reading if temp_probe not available
        return self._read_actual_temp()

    def _pid_update_if_enabled(self, target_c: float, poll_s: float) -> Optional[float]:
        """If PID is enabled, compute a new setpoint and push it to the chamber.
        Returns the setpoint used (or None if not updated)."""
        if not self._pid_enabled or self._pid is None or self._pid_base_setpoint is None:
            return None
        # Apply interval gating for PID compute
        now = time.time()
        if isinstance(self._pid_interval_sec, (int, float)) and self._pid_interval_sec > 0:
            if self._pid_last_update is not None and (now - self._pid_last_update) < float(self._pid_interval_sec):
                return self._pid_sp_current
        meas = self._get_pid_measurement(target_c)
        if meas is None:
            return None
            
        # Check two-stage PID status if enabled
        if self._pid_two_stage_enabled:
            self._check_stabilization_status(target_c, meas)
            
        # Optional EMA filtering of measurement
        if isinstance(self._pid_filter_alpha, (int, float)) and 0.0 < float(self._pid_filter_alpha) <= 1.0:
            alpha = float(self._pid_filter_alpha)
            self._pid_meas_ema = meas if self._pid_meas_ema is None else (alpha * meas + (1.0 - alpha) * self._pid_meas_ema)
            meas_f = self._pid_meas_ema
        else:
            meas_f = meas
        # Deadband: reduce chattering
        error = float(target_c) - float(meas_f)
        if self._pid_deadband and abs(error) < self._pid_deadband:
            error = 0.0
        delta_t = poll_s if self._pid_last_ts is None else (now - self._pid_last_ts)
        self._pid_last_ts = now
        u = self._pid.compute(error, delta_t, meas=meas_f)
        # Proposed setpoint
        new_sp = self._pid_base_setpoint + u
        # Rate limit setpoint movement if requested
        if isinstance(self._pid_sp_rate_limit, (int, float)) and self._pid_sp_rate_limit > 0 and self._pid_sp_current is not None and self._pid_last_sp_ts is not None:
            dt_sp = max(0.05, now - self._pid_last_sp_ts)
            max_delta = float(self._pid_sp_rate_limit) * dt_sp
            delta_sp = new_sp - self._pid_sp_current
            if abs(delta_sp) > max_delta:
                new_sp = self._pid_sp_current + (max_delta if delta_sp > 0 else -max_delta)
        # Avoid spamming the controller if change is tiny
        if self._pid_sp_current is None or abs(new_sp - self._pid_sp_current) >= 0.05:
            self._set_setpoint(new_sp)
            self._pid_sp_current = new_sp
            self._pid_last_sp_ts = now
        self._pid_last_update = now
        return self._pid_sp_current

    def _wait_until_stable(self, target_c: float, tol_c: float, window_s: int, poll_s: int, initial_delay_s: int):
        # Initial wait before monitoring
        if initial_delay_s and initial_delay_s > 0:
            log_message(f"Initial delay {initial_delay_s}s before stability monitoring…")
            # Log during initial delay as well
            end = time.time() + initial_delay_s
            while time.time() < end:
                # PID tracking during initial delay if enabled
                sp = self._pid_update_if_enabled(target_c, poll_s=float(poll_s))
                self._maybe_log_telemetry(phase="stabilize", step=self.current_step, setpoint_c=sp)
                time.sleep(min(5, initial_delay_s))
        
        # If no thermocouples and no controller, fallback to timed wait
        _, tc_count, _ = self._tcs_within_band(target_c, tol_c)
        if tc_count == 0 and self.temp_controller is None:
            log_message(f"[SIM] No temperature feedback; sleeping {window_s}s as stability window")
            end = time.time() + window_s
            while time.time() < end:
                sp = self._pid_update_if_enabled(target_c, poll_s=float(poll_s))
                self._maybe_log_telemetry(phase="stabilize", step=self.current_step, setpoint_c=sp)
                time.sleep(5)
            return

        # Two-stage PID uses its own stabilization logic
        if self._pid_two_stage_enabled:
            log_message("Using two-stage PID stabilization logic")
            while not self._stabilization_achieved:
                # Get measurement and update PID (includes phase switching logic)
                sp = self._pid_update_if_enabled(target_c, poll_s=float(poll_s))
                
                # Log current status
                meas = self._get_pid_measurement(target_c)
                if meas is not None:
                    delta = abs(meas - target_c)
                    phase_info = f"Phase: {self._current_pid_phase}"
                    if self._current_pid_phase == "stabilization":
                        phase_info += f", Stable readings: {self._stabilization_consecutive_count}/{self._stabilization_consecutive_readings}"
                        if self._stabilization_start_time:
                            stable_time = time.time() - self._stabilization_start_time
                            phase_info += f", Stable time: {stable_time:.1f}/{self._stabilization_time_required}s"
                    log_message(f"Two-stage PID: {meas:.2f}°C (Δ={delta:.2f}°C) | {phase_info}")
                
                self._maybe_log_telemetry(phase="stabilize", step=self.current_step, setpoint_c=sp)
                time.sleep(max(1, int(poll_s)))
            
            log_message("Two-stage PID stabilization complete")
            return

        # Original single-stage stability logic
        end_required = time.time() + window_s
        while True:
            # Prefer thermocouple readings for stability
            _, count_present, vals = self._tcs_within_band(target_c, tol_c)
            if count_present > 0:
                any_ok = any(abs(v - target_c) <= tol_c for v in vals)
                msg_vals = ", ".join(f"{v:.2f}" for v in vals)
                log_message(f"TCs [{msg_vals}] C vs target {target_c:.2f} C (tol ±{tol_c:.2f} C) -> {'OK' if any_ok else 'OUT'} (any)")
                if any_ok:
                    if time.time() >= end_required:
                        log_message("Thermocouples (any) stable within tolerance window")
                        return
                else:
                    end_required = time.time() + window_s
                    log_message("Thermocouples (any) outside tolerance; resetting stability window")
            else:
                # Fallback to controller reading if no TCs available
                curr = self._read_actual_temp()
                if curr is not None:
                    delta = abs(curr - target_c)
                    log_message(f"Controller temp {curr:.2f} C (target {target_c:.2f} C, |Δ|={delta:.2f} C, tol={tol_c:.2f} C)")
                    if delta <= tol_c:
                        if time.time() >= end_required:
                            log_message("Controller temperature stable within tolerance window")
                            return
                    else:
                        end_required = time.time() + window_s
                        log_message("Controller outside tolerance; resetting stability window")
                else:
                    log_message("No temperature feedback available; continuing")
            sp = self._pid_update_if_enabled(target_c, poll_s=float(poll_s))
            self._maybe_log_telemetry(phase="stabilize", step=self.current_step, setpoint_c=sp)
            time.sleep(max(1, int(poll_s)))

    # --------- Telemetry helpers ---------
    def _init_telemetry(self):
        # No-op (telemetry initialized in __init__)
        return

    def set_telemetry_callback(self, callback: Optional[Callable[[Dict[str, Any]], None]]):
        """Register a callback that receives a dict of telemetry values whenever we log a row."""
        self.telemetry_callback = callback

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
            if isinstance(tc1, Agilent34401A):
                tc1_temp = tc1.measure_temp() if tc1 is not None else None
        except (OSError, ValueError):
            pass

        try:
            if isinstance(tc2, Agilent34401A):
                tc2_temp = tc2.measure_temp() if tc2 is not None else None
        except (OSError, ValueError):
            pass

        return tc1_temp, tc2_temp

    def _log_telemetry(self, phase: str, step=None, setpoint_c: Optional[float] = None,
                        sig_a_enabled: Optional[bool] = None, na_enabled: Optional[bool] = None,
                        sig_a_executed: Optional[bool] = None, na_executed: Optional[bool] = None):
        if self.telemetry_path is None:
            return
        try:
            idx = getattr(step, "_index", None)
            name = getattr(step, "step_name", "") if step is not None else ""
            cycle = getattr(step, "temp_cycle_type", "") if step is not None else ""
            target = getattr(step, "temperature", None) if step is not None else None
            if setpoint_c is not None:
                sp = setpoint_c
            elif step is not None and isinstance(target, (int, float)):
                try:
                    sp = target + float(getattr(step, "temp_controller_offset", 0.0) or 0.0)
                except (TypeError, ValueError):
                    sp = None
            else:
                sp = None
            actual = self._read_actual_temp()
            v, c, out = self._get_psu_snapshot()
            tc1, tc2 = self._get_tc_snapshot()

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
                str(bool(sig_a_enabled)) if sig_a_enabled is not None else "",
                str(bool(na_enabled)) if na_enabled is not None else "",
                str(bool(sig_a_executed)) if sig_a_executed is not None else "",
                str(bool(na_executed)) if na_executed is not None else "",
            ]
            with open(self.telemetry_path, "a", encoding="utf-8") as f:
                f.write(",".join(map(str, line)) + "\n")

            # Also emit to live callback if any
            if self.telemetry_callback is not None:
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
                        "tests_sig_a_enabled": bool(sig_a_enabled) if sig_a_enabled is not None else None,
                        "tests_na_enabled": bool(na_enabled) if na_enabled is not None else None,
                        "tests_sig_a_executed": bool(sig_a_executed) if sig_a_executed is not None else None,
                        "tests_na_executed": bool(na_executed) if na_executed is not None else None,
                    }
                    self.telemetry_callback(payload)
                except (RuntimeError, ValueError, TypeError):
                    # Never allow GUI callback failures to break the cycle
                    pass
        except (OSError, ValueError):
            # Do not break cycle on telemetry failure
            pass

    def _maybe_log_telemetry(self, phase: str, step=None, setpoint_c: Optional[float] = None,
                              sig_a_enabled: Optional[bool] = None, na_enabled: Optional[bool] = None,
                              sig_a_executed: Optional[bool] = None, na_executed: Optional[bool] = None):
        now = time.time()
        if now - self._telemetry_last_ts >= 2.5:
            self._log_telemetry(phase=phase, step=step, setpoint_c=setpoint_c,
                                sig_a_enabled=sig_a_enabled, na_enabled=na_enabled,
                                sig_a_executed=sig_a_executed, na_executed=na_executed)
            self._telemetry_last_ts = now

    # --------- Tests integration ---------
    def _map_step_tests(self, step) -> tuple[bool, bool]:
        # SIG_A if any of these content flags are enabled
        sig_a = any([
            getattr(step, "psat_tests", False),
            getattr(step, "gain_tests", False),
            getattr(step, "phase_tests", False),
            getattr(step, "IP3_tests", False),
            getattr(step, "noise_figure_tests", False),
            getattr(step, "pin_pout_tests", False),
        ])
        # NA category
        na = any([
            getattr(step, "na_tests", False),
            getattr(step, "S11_tests", False),
            getattr(step, "S22_tests", False),
        ])
        return sig_a, na

    def _run_tests_for_step(self, step) -> tuple[bool, bool]:
        sig_a_enabled, na_enabled = self._map_step_tests(step)
        if not (sig_a_enabled or na_enabled):
            return False, False

        sig_a_exec = False
        na_exec = False
        # Choose a representative path for now
        try:
            path = self.test_manager.paths[0]
        except (AttributeError, IndexError):
            path = None

        if path is None:
            return False, False

        # Respect instrument connectivity flags
        if sig_a_enabled and not self.test_manager.instruments_connection.get("rfsa", True):
            sig_a_enabled = False
        if na_enabled and not self.test_manager.instruments_connection.get("na", True):
            na_enabled = False

        if not (sig_a_enabled or na_enabled):
            return False, False

        self._log_telemetry(phase="testing", step=step, sig_a_enabled=sig_a_enabled, na_enabled=na_enabled)
        try:
            self.test_manager.run_and_process_tests(
                path=path,
                sno="",
                sig_a_tests=sig_a_enabled,
                na_tests=na_enabled,
                golden_tests=False,
                options={},
            )
            sig_a_exec = sig_a_enabled
            na_exec = na_enabled
        except (RuntimeError, OSError, ValueError) as e:
            log_message(f"Tests failed to execute: {e}")
        finally:
            self._log_telemetry(phase="testing", step=step, sig_a_enabled=sig_a_enabled, na_enabled=na_enabled,
                                sig_a_executed=sig_a_exec, na_executed=na_exec)

        return sig_a_exec, na_exec

    def run_thermal_cycle(self, profile_path):
        """Execute the temperature steps defined in a profile JSON file."""
        self.temp_profile_manager = TempProfileManager(profile_path)
        all_steps = self.temp_profile_manager.get_all_steps()

        log_message(f"Loaded thermal profile '{profile_path}' with {len(all_steps)} steps")

        for idx, step in enumerate(all_steps, start=1):
            # store index for telemetry
            setattr(step, "_index", idx)
            target_c = float(getattr(step, "temperature", 0.0) or 0.0)
            offset_c = float(getattr(step, "temp_controller_offset", 0.0) or 0.0)
            setpoint_c = target_c + offset_c
            tol_c = float(getattr(step, "settlement_tolerance", 0.6) or 0.6)
            window_s = int(getattr(step, "settlement_window", 300) or 300)
            poll_s = int(getattr(step, "monitoring_interval", 3) or 3)
            initial_delay_s = int(getattr(step, "initial_delay", 60) or 60)
            dwell_min = float(getattr(step, "total_time", 0) or 0)
            dwell_s = int(dwell_min * 60)
            cycle_type = getattr(step, "temp_cycle_type", "").upper()
            self.current_step = step
            log_message("-" * 60)
            log_message(f"Step {idx}/{len(all_steps)} | {getattr(step, 'step_name', 'Unnamed')} | {cycle_type}")
            log_message(f"Target {target_c:.2f} C (setpoint {setpoint_c:.2f} C, tol ±{tol_c:.2f} C)")

            sig_a_enabled, na_enabled = self._map_step_tests(step)
            # Prime an initial telemetry line at step start
            self._log_telemetry(phase="start", step=step, setpoint_c=setpoint_c,
                                sig_a_enabled=sig_a_enabled, na_enabled=na_enabled)

            # Apply PSU state per step
            self._apply_power_for_step(getattr(step, "voltage", 0.0) or 0.0, getattr(step, "current", 0.0) or 0.0)

            # Set chamber setpoint
            self._set_setpoint(setpoint_c)

            # Initialize optional cascade PID (adjusting setpoint to hit DUT/TC target)
            self._pid_enabled = bool(getattr(step, "pid_enable", False))
            if self._pid_enabled:
                # Check if two-stage PID is enabled
                self._pid_two_stage_enabled = bool(getattr(step, "pid_two_stage_enable", False))
                
                if self._pid_two_stage_enabled:
                    # Load two-stage parameters
                    self._pid_approach_params = getattr(step, "pid_approach_phase", {})
                    self._pid_stabilization_params = getattr(step, "pid_stabilization_phase", {})
                    self._stabilization_trigger_delta = float(getattr(step, "stabilization_trigger_delta", 2.0))
                    self._stabilization_time_required = float(getattr(step, "stabilization_time_required", 45))
                    self._stabilization_consecutive_readings = int(getattr(step, "stabilization_consecutive_readings", 10))
                    
                    # Initialize with approach phase parameters
                    self._current_pid_phase = "approach"
                    self._stabilization_start_time = None
                    self._stabilization_consecutive_count = 0
                    self._stabilization_achieved = False
                    
                    # Use approach phase parameters for initial PID setup
                    kp = float(self._pid_approach_params.get("pid_kp", 0.6))
                    ki = float(self._pid_approach_params.get("pid_ki", 0.05))
                    kd = float(self._pid_approach_params.get("pid_kd", 0.0))
                    max_off = float(self._pid_approach_params.get("pid_max_offset", 15.0))
                    self._pid_sp_rate_limit = float(self._pid_approach_params.get("pid_sp_rate_limit", 1.0))
                    
                    log_message(f"Two-stage PID enabled:")
                    log_message(f"  Approach: kp={kp}, ki={ki}, kd={kd}, max_offset=±{max_off}, rate_limit={self._pid_sp_rate_limit}")
                    stab_kp = self._pid_stabilization_params.get("pid_kp", 0.8)
                    stab_ki = self._pid_stabilization_params.get("pid_ki", 0.03)
                    stab_kd = self._pid_stabilization_params.get("pid_kd", 0.1)
                    stab_max_off = self._pid_stabilization_params.get("pid_max_offset", 6.0)
                    stab_rate_limit = self._pid_stabilization_params.get("pid_sp_rate_limit", 1.0)
                    log_message(f"  Stabilization: kp={stab_kp}, ki={stab_ki}, kd={stab_kd}, max_offset=±{stab_max_off}, rate_limit={stab_rate_limit}")
                    log_message(f"  Trigger: ±{self._stabilization_trigger_delta}°C, Time: {self._stabilization_time_required}s, Readings: {self._stabilization_consecutive_readings}")
                else:
                    # Single-stage PID (original behavior)
                    kp = float(getattr(step, "pid_kp", 0.6) or 0.6)
                    ki = float(getattr(step, "pid_ki", 0.05) or 0.05)
                    kd = float(getattr(step, "pid_kd", 0.0) or 0.0)
                    max_off = float(getattr(step, "pid_max_offset", 15.0) or 15.0)
                    self._pid_sp_rate_limit = float(getattr(step, "pid_sp_rate_limit", 1.0))
                
                self._pid_source = str(getattr(step, "pid_source", "avg") or "avg")
                self._pid_deadband = float(getattr(step, "pid_deadband", 0.0) or 0.0)
                # Upgraded options with sensible defaults
                self._pid_interval_sec = float(getattr(step, "pid_interval", 1.0) or 1.0)
                self._pid_filter_alpha = float(getattr(step, "pid_filter_alpha", 0.0) or 0.0)
                self._pid_deriv_on_meas = bool(getattr(step, "pid_derivative_on_measurement", True))
                self._pid_integral_band = float(getattr(step, "pid_integral_band", 0.8))
                self._pid_backcalc_k = float(getattr(step, "pid_backcalc_k", 0.1))
                
                self._pid = LynxThermalCycleManager.SimplePID(
                    kp, ki, kd,
                    output_limits=(-abs(max_off), abs(max_off)),
                    derivative_on_meas=self._pid_deriv_on_meas,
                    backcalc_k=self._pid_backcalc_k,
                    integral_band=self._pid_integral_band,
                )
                self._pid.reset()
                self._pid_base_setpoint = setpoint_c
                self._pid_sp_current = setpoint_c
                self._pid_last_ts = None
                self._pid_last_update = None
                self._pid_meas_ema = None
                self._pid_last_sp_ts = None
                
                if not self._pid_two_stage_enabled:
                    log_message(
                        f"PID enabled (kp={kp}, ki={ki}, kd={kd}, source={self._pid_source}, max_offset=±{max_off} C, "
                        f"interval={self._pid_interval_sec}s, filter_alpha={self._pid_filter_alpha}, deriv_on_meas={self._pid_deriv_on_meas}, "
                        f"integral_band={self._pid_integral_band}, backcalc_k={self._pid_backcalc_k}, sp_rate_limit={self._pid_sp_rate_limit} C/s)"
                    )
            else:
                # Clear any previous PID state
                self._pid = None
                self._pid_base_setpoint = None
                self._pid_sp_current = None
                self._pid_last_ts = None
                self._pid_last_update = None
                self._pid_meas_ema = None
                self._pid_last_sp_ts = None
                self._pid_two_stage_enabled = False

            # Handle by step type
            if cycle_type == "RAMP":
                # For ramps, wait until we're within target +/- target_temp_delta or for configured dwell time
                target_delta = float(getattr(step, "target_temp_delta", tol_c) or tol_c)
                log_message(f"RAMP: waiting for thermocouples within ±{target_delta} C of target")
                # Use a shorter window for ramp approach: hold within band for 2 consecutive polls
                consecutive_needed = 2
                consecutive = 0
                while consecutive < consecutive_needed:
                    _, count_present, vals = self._tcs_within_band(target_c, target_delta)
                    if count_present > 0:
                        any_ok = any(abs(v - target_c) <= target_delta for v in vals)
                        consecutive = consecutive + 1 if any_ok else 0
                        msg_vals = ", ".join(f"{v:.2f}" for v in vals)
                        log_message(f"RAMP TC check [{msg_vals}] vs {target_c:.2f} ±{target_delta:.2f} -> {'OK' if any_ok else 'OUT'} (any) ({consecutive}/{consecutive_needed})")
                    else:
                        # Fallback to controller if no TCs available
                        curr = self._read_actual_temp()
                        if curr is not None and abs(curr - target_c) <= target_delta:
                            consecutive += 1
                            log_message(f"RAMP controller {curr:.2f} within band ({consecutive}/{consecutive_needed})")
                        else:
                            consecutive = 0
                    self._maybe_log_telemetry(phase="ramp", step=step, setpoint_c=setpoint_c, sig_a_enabled=sig_a_enabled, na_enabled=na_enabled)
                    time.sleep(max(1, int(poll_s)))
                log_message("RAMP: target band reached via thermocouples")
            elif cycle_type in ("DWELL", "SOAK"):
                # Wait to be stable within tolerance window, then dwell for the specified time
                self._wait_until_stable(target_c=target_c, tol_c=tol_c, window_s=window_s, poll_s=poll_s, initial_delay_s=initial_delay_s)

                # Run tests (if any) once stable
                sig_a_exec = na_exec = False
                if sig_a_enabled or na_enabled:
                    sig_a_exec, na_exec = self._run_tests_for_step(step)

                if dwell_s > 0:
                    log_message(f"Dwelling at target for {dwell_s}s")
                    end = time.time() + dwell_s
                    while time.time() < end:
                        sp = self._pid_update_if_enabled(target_c, poll_s=float(max(2.5, poll_s)))
                        self._maybe_log_telemetry(phase="dwell", step=step, setpoint_c=sp if sp is not None else setpoint_c,
                                                  sig_a_enabled=sig_a_enabled, na_enabled=na_enabled,
                                                  sig_a_executed=sig_a_exec, na_executed=na_exec)
                        time.sleep(2.5)
            else:
                # Unknown/unspecified type: do a conservative wait
                log_message("Unknown step type; performing conservative stability wait")
                self._wait_until_stable(target_c=target_c, tol_c=tol_c, window_s=window_s, poll_s=poll_s, initial_delay_s=initial_delay_s)
                if dwell_s > 0:
                    end = time.time() + dwell_s
                    while time.time() < end:
                        sp = self._pid_update_if_enabled(target_c, poll_s=float(max(2.5, poll_s)))
                        self._maybe_log_telemetry(phase="dwell", step=step, setpoint_c=sp if sp is not None else setpoint_c,
                                                  sig_a_enabled=sig_a_enabled, na_enabled=na_enabled)
                        time.sleep(2.5)

            # Optional: turn off power after this step
            if getattr(step, "power_off_after", False):
                self._power_off()

            # Log end of step
            final_sp = self._pid_sp_current if (self._pid_enabled and self._pid_sp_current is not None) else setpoint_c
            self._log_telemetry(phase="step_complete", step=step, setpoint_c=final_sp,
                                sig_a_enabled=sig_a_enabled, na_enabled=na_enabled)

            # Clear PID after each step
            self._pid_enabled = False
            self._pid = None
            self._pid_base_setpoint = None
            self._pid_sp_current = None
            self._pid_last_ts = None

        log_message("Thermal cycle complete")