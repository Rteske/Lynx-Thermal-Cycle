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

    def _wait_until_stable(self, target_c: float, target_temp_delta_c: float, tol_c: float, window_s: int, poll_s: int, initial_delay_s: int, temp_offset: float):
        """Approach target using P-control to within target_temp_delta, then require low movement within a window.

        - P-control phase adjusts chamber setpoint (sp) toward target using error = target - measured.
        - Settlement phase confirms that the temperature movement (max-min) over the last window_s seconds
          is <= tol_c, sampled every poll_s seconds. Resets timer if span exceeds tol.
        """
        # Parameters
        sp_min = -80.0
        sp_max = 120.0
        kp = float(getattr(self.current_step, "pid_kp", 0.6) or 0.6)
        sp_rate_limit = float(getattr(self.current_step, "pid_sp_rate_limit", 1.0) or 1.0)  # degC per poll

        # Initial setpoint with offset
        sp = float(target_c + (temp_offset or 0.0))
        self._set_setpoint(sp)

        # Lock a measurement source for the entire step (prefer TC1)
        def read_control_meas() -> Optional[float]:
            v = self._get_pid_measurement(target_c)
            return v if isinstance(v, (int, float)) else self._read_actual_temp()

        # Initial delay
        if initial_delay_s and initial_delay_s > 0:
            log_message(
                f"INIT: delay={initial_delay_s}s before control | target={target_c:.2f}C, delta={target_temp_delta_c:.2f}C, tol={tol_c:.2f}C"
            )
            end = time.time() + int(initial_delay_s)
            while time.time() < end:
                self._maybe_log_telemetry(phase="init-delay", step=self.current_step, setpoint_c=sp)
                time.sleep(min(5, max(1, int(poll_s))))

        # P-control approach to target band
        last_log = 0.0
        approach_start = time.time()
        # Max approach time: 30 min default; if quick windows, still give at least 2x window
        max_approach_time_s = max(30 * 60, 2 * int(window_s))
        missing_meas_count = 0

        # Detect control direction sign: positive means increasing setpoint increases measurement
        direction_sign = 1.0
        try:
            m0 = read_control_meas()
            # Log control source once
            if isinstance(m0, (int, float)):
                log_message("PCTRL: control source = TC1 (temp_probe)")
                self._set_setpoint(sp + 1.0)
                time.sleep(max(1, int(poll_s)))
                m1 = read_control_meas()
                if isinstance(m1, (int, float)) and m0 is not None:
                    if (m1 - m0) < 0:
                        direction_sign = -1.0
                        log_message("PCTRL: Auto-detected inverted response (direction_sign = -1)")
                # revert setpoint back near original
                sp = float(target_c + (temp_offset or 0.0))
                self._set_setpoint(sp)
            else:
                log_message("PCTRL: control source = controller (fallback)")
        except (RuntimeError, OSError, ValueError):
            pass
        while True:
            meas = read_control_meas()
            if meas is None:
                missing_meas_count += 1
                if self.simulation_mode and missing_meas_count >= 3:
                    log_message("PCTRL: No measurement (SIM) — skipping approach and proceeding to settlement")
                    break
                if (time.time() - approach_start) > max_approach_time_s:
                    log_message("PCTRL: No measurement; approach timeout reached — proceeding to settlement")
                    break
                time.sleep(max(1, int(poll_s)))
                continue

            # Error is target - measured; apply auto-detected direction sign so delta_sp pushes meas toward target
            error = float(target_c - float(meas))
            in_band = abs(error) <= float(target_temp_delta_c)

            # Compute proportional setpoint change with per-iteration clamp
            delta_sp = kp * error * direction_sign
            max_step = max(0.1, sp_rate_limit)
            if delta_sp > max_step:
                delta_sp = max_step
            elif delta_sp < -max_step:
                delta_sp = -max_step

            if not in_band:
                sp = max(sp_min, min(sp_max, sp + delta_sp))
                self._set_setpoint(sp)

            now = time.time()
            if now - last_log >= max(1, int(poll_s)):
                log_message(
                    f"PCTRL: tgt={target_c:.2f}C meas={float(meas):.2f}C err={error:.2f}C sp={sp:.2f}C d_sp={delta_sp:.2f}C kp={kp:.2f} lim={sp_rate_limit:.2f}/poll in_band={in_band}"
                )
                last_log = now

            self._maybe_log_telemetry(phase="pctrl", step=self.current_step, setpoint_c=sp)
            if in_band:
                log_message(f"PCTRL: Reached target band ±{float(target_temp_delta_c):.2f}C around {target_c:.2f}C")
                break

            time.sleep(max(1, int(poll_s)))

        # Settlement by movement within window
        window_values: list[tuple[float, float]] = []
        window_duration = max(1, int(window_s))
        poll = max(1, int(poll_s))
        end_required = time.time() + window_duration
        missing_meas_count = 0
        settle_start = time.time()
        max_settle_time_s = max(60 * 60, 2 * window_duration)  # 1 hour or 2x window, whichever larger
        while True:
            meas = read_control_meas()
            if meas is None:
                missing_meas_count += 1
                if self.simulation_mode and missing_meas_count >= 3:
                    log_message("SETTLE: No measurement (SIM) — treating as stable to avoid hang")
                    return
                if (time.time() - settle_start) > max_settle_time_s:
                    log_message("SETTLE: No measurement; settlement timeout reached — proceeding")
                    return
                log_message("SETTLE: No measurement; waiting…")
                time.sleep(poll)
                continue

            now = time.time()
            window_values.append((now, float(meas)))
            cutoff = now - window_duration
            window_values = [(ts, v) for ts, v in window_values if ts >= cutoff]

            vals = [v for _, v in window_values]
            span = (max(vals) - min(vals)) if len(vals) >= 2 else 0.0
            log_message(
                f"SETTLE: n={len(vals)} span={span:.3f}C <= tol={float(tol_c):.3f}C window={window_duration}s poll={poll}s sp={sp:.2f}C tgt={target_c:.2f}C last={float(meas):.2f}C"
            )
            self._maybe_log_telemetry(phase="settle", step=self.current_step, setpoint_c=sp)

            if span <= float(tol_c):
                if now >= end_required:
                    log_message("SETTLE: Stable — movement within tolerance for the full window")
                    return
            else:
                end_required = now + window_duration
                log_message("SETTLE: Movement exceeded tolerance — window timer reset")

            time.sleep(poll)

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
            target_temp_delta_c = float(getattr(step, "target_temp_delta", 0.0) or 0.0)
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
            # Apply setpoint once per step; control/wait happens below per type
            self._set_setpoint(setpoint_c=setpoint_c)

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
                self._wait_until_stable(target_c=target_c, target_temp_delta_c=target_temp_delta_c, tol_c=tol_c, window_s=window_s, poll_s=poll_s, initial_delay_s=initial_delay_s, temp_offset=offset_c)

                # Run tests (if any) once stable
                sig_a_exec = na_exec = False
                if sig_a_enabled or na_enabled:
                    sig_a_exec, na_exec = self._run_tests_for_step(step)

                if dwell_s > 0:
                    log_message(f"Dwelling at target for {dwell_s}s")
                    end = time.time() + dwell_s
                    while time.time() < end:
                        # sp = self._control_update_if_enabled(target_c, poll_s=float(max(2.5, poll_s)))
                        self._maybe_log_telemetry(phase="dwell", step=step, setpoint_c=setpoint_c,
                                                  sig_a_enabled=sig_a_enabled, na_enabled=na_enabled,
                                                  sig_a_executed=sig_a_exec, na_executed=na_exec)

            # Optional: turn off power after this step
            if getattr(step, "power_off_after", False):
                self._power_off()

            self._log_telemetry(phase="step_complete", step=step, setpoint_c=0,
                                sig_a_enabled=sig_a_enabled, na_enabled=na_enabled)


        log_message("Thermal cycle complete")