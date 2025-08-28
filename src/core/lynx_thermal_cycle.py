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
        self.telemetry_callback = None  # set via set_telemetry_callback

        # Initialize temperature controller and turn chamber ON
        try:
            if not simulation_mode:
                # Lazy import to avoid requiring pyserial in simulation mode
                from instruments.temp_controller import TempController  # type: ignore
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
                        "psu_voltage,psu_current,psu_output,tc1_temp,tc2_temp," \
                        "tests_pin_pout_functional,tests_sig_a_performance,tests_na_performance\n"
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
        """Set the setpoint, then wait until movement is within tolerance for a full window and inside the target band.

        If variance (window span) is low (<= 0.08C) but the temperature is stabilizing outside the target band,
        a conservative PID nudge adjusts the setpoint toward the target until in-band stability is achieved.
        """
        # Apply setpoint once (target + offset)
        sp = float(target_c + (temp_offset or 0.0))
        self._set_setpoint(sp)

        # Lightweight PID state for "stable in wrong place" correction
        pid_enabled = True
        pid_variance_threshold = 0.1  # C; when window span <= this and not in band, nudge setpoint
        Kp, Ki, Kd = 0.6, 0.02, 0.0  # conservative gains; derivative disabled by default
        integ = 0.0
        last_err: Optional[float] = None
        last_pid_ts: Optional[float] = None
        min_pid_interval_s = max(5, int(poll_s))  # don't adjust more often than this
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
                    # Fast apply without long wait to avoid blocking
                    self.temp_controller.set_setpoint(self.temp_channel, sp)
                    log_message(f"PID: setpoint -> {sp:.2f} C (CH{self.temp_channel})")
            except (SerialException, ValueError, OSError) as e:
                log_message(f"PID: failed to set setpoint: {e}")

        # Measurement function (prefer TC1; fallback to controller)
        def read_meas() -> Optional[float]:
            v = self._get_pid_measurement(target_c)
            return v if isinstance(v, (int, float)) else self._read_actual_temp()

        # Optional initial delay
        # Apply dwell scaling to initial delay
        try:
            scaled_initial_delay = int(max(0, float(initial_delay_s)) * max(0.01, float(self.dwell_scale)))
        except (TypeError, ValueError):
            scaled_initial_delay = int(initial_delay_s)
        if scaled_initial_delay and scaled_initial_delay > 0:
            log_message(
                f"INIT: delay={scaled_initial_delay}s before settlement | target={target_c:.2f}C, band=±{float(target_temp_delta_c):.2f}C, tol={tol_c:.2f}C"
            )
            end = time.time() + scaled_initial_delay
            while time.time() < end:
                self._maybe_log_telemetry(phase="init-delay", step=self.current_step, setpoint_c=sp)
                time.sleep(min(5, max(1, int(poll_s))))

        # Settlement by movement within window AND inside target band
        window_values: list[tuple[float, float]] = []
        window_duration = max(1, int(window_s))
        poll = max(1, int(poll_s))
        end_required = time.time() + window_duration
        missing_meas_count = 0
        settle_start = time.time()
        max_settle_time_s = max(60 * 60, 2 * window_duration)
        while True:
            meas = read_meas()
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
            band_err = abs(float(meas) - float(target_c))
            in_band = band_err <= float(target_temp_delta_c)
            # Rolling window coverage (how many seconds of data are in the current window)
            coverage_s = (now - window_values[0][0]) if window_values else 0.0

            log_message(
                f"SETTLE: n={len(vals)} span={span:.3f}C tol={float(tol_c):.3f}C band_err={band_err:.3f}C band=±{float(target_temp_delta_c):.2f}C in_band={in_band} window={window_duration}s cov={coverage_s:.1f}s"
            )
            self._maybe_log_telemetry(phase="settle", step=self.current_step, setpoint_c=sp)

            # If we're stabilizing (low span) but outside the target band, apply a PID nudge
            pid_window_ready = (coverage_s >= window_duration) and (len(vals) >= 3)
            if pid_enabled and pid_window_ready and span <= pid_variance_threshold and not in_band:
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
                        f"PID: stable outside band (span {span:.3f}C, err {err:.3f}C). Adjusting setpoint by {output:.3f}C to {new_sp:.2f}C"
                    )
                    _apply_sp_nudge(new_sp)
                    last_pid_ts = now
                    last_err = err
                    # After changing setpoint, require a fresh full window of stability
                    end_required = now + window_duration

            if span <= float(tol_c) and in_band:
                if now >= end_required:
                    log_message("SETTLE: Stable — within tolerance and band for the full window")
                    return
            else:
                end_required = now + window_duration

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
                        pin_pout_functional: Optional[bool] = None,
                        sig_a_performance: Optional[bool] = None,
                        na_performance: Optional[bool] = None):
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
                str(bool(pin_pout_functional)) if pin_pout_functional is not None else "",
                str(bool(sig_a_performance)) if sig_a_performance is not None else "",
                str(bool(na_performance)) if na_performance is not None else "",
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
                        "tests_pin_pout_functional": bool(pin_pout_functional) if pin_pout_functional is not None else None,
                        "tests_sig_a_performance": bool(sig_a_performance) if sig_a_performance is not None else None,
                        "tests_na_performance": bool(na_performance) if na_performance is not None else None,
                    }
                    self.telemetry_callback(payload)
                except (RuntimeError, ValueError, TypeError):
                    # Never allow GUI callback failures to break the cycle
                    pass
        except (OSError, ValueError):
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
                runner = getattr(self.test_manager, "run_and_process_tests", None)
                if callable(runner):
                    # Pass explicit flags; concrete manager decides what to run
                    runner(path=path, pin_pout_functional=pin_func, sig_a_performance=sig_a_perf, na_performance=na_perf)
                else:
                    log_message("No public test runner available; skipping tests for this step.")
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
                # Use a shorter window for ramp approach: hold within band for 2 consecutive polls
                consecutive_needed = 2
                if self.simulation_mode:
                    log_message("RAMP: SIM mode — treating band reached immediately")
                else:
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