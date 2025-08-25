import logging
import time
from typing import List, Optional

from instruments.temp_controller import TempController
from lynx_pa_top_level_test_manager import PaTopLevelTestManager
from temp_new import TempProfileManager, DwellStep, RampStep, SoakStep, BaseTempStep

logger = logging.getLogger(__name__)

class TempStepsExecutor:
    """
    Executes temperature steps defined by temp_new.TempProfileManager and triggers
    Lynx PA tests per step across one or more paths.
    """

    def __init__(
        self,
        temp_controller: Optional[TempController] = None,
        test_manager: Optional[PaTopLevelTestManager] = None,
        default_paths: Optional[List[str]] = None,
    ) -> None:
        self.temp_controller = temp_controller or TempController()
        self.test_manager = test_manager or PaTopLevelTestManager(sim=False)
        self.default_paths = default_paths or [
            "HIGH_BAND_PATH1 (Vertical)",
            "HIGH_BAND_PATH2 (Vertical)",
            "LOW_BAND_PATH1 (Vertical)",
            "LOW_BAND_PATH2 (Vertical)",
        ]

    def run_profile(
        self,
        profile_path: str,
        sno: str,
        paths: Optional[List[str]] = None,
        golden_tests: bool = False,
    ) -> None:
        manager = TempProfileManager(profile_path)
        steps = manager.get_all_steps()
        if not steps:
            logger.warning("No steps found in profile: %s", profile_path)
            return

        # Chamber ON
        self._ensure_chamber_on()

        use_paths = paths or self.default_paths
        logger.info("Executing %d steps across %d paths", len(steps), len(use_paths))

        for idx, step in enumerate(steps):
            self._execute_step(idx, step)
            if step.has_any_tests():
                self._run_tests_for_step(step, sno, use_paths, golden_tests)

        logger.info("Completed steps profile: %s", profile_path)

    # ----- Internal helpers -----
    def _ensure_chamber_on(self) -> None:
        try:
            self.temp_controller.set_chamber_state(True)
        except (OSError, TimeoutError, ValueError, RuntimeError) as exc:
            logger.error("Failed to enable chamber: %s", exc)
            raise

    def _set_and_wait(
        self,
        setpoint_c: float,
        offset_c: float,
        initial_delay_s: int,
        tolerance_c: float,
        window_s: int,
        poll_s: int,
    ) -> None:
        target = float(setpoint_c) + float(offset_c or 0.0)
        self.temp_controller.set_setpoint(1, target)  # default channel 1; adjust if needed
        logger.info(
            "Setpoint %.2f°C (offset %.2f°C). Waiting initial %ss before settlement",
            target,
            offset_c or 0.0,
            initial_delay_s,
        )
        if initial_delay_s > 0:
            time.sleep(initial_delay_s)

        stable_start: Optional[float] = None
        while True:
            actual = self._read_actual()
            if actual is None:
                time.sleep(poll_s)
                continue
            err = abs(actual - target)
            logger.debug("Actual=%.2f°C err=%.2f°C", actual, err)

            if err <= tolerance_c:
                if stable_start is None:
                    stable_start = time.time()
                if (time.time() - stable_start) >= window_s:
                    logger.info("Temperature stable at %.2f°C", actual)
                    return
            else:
                stable_start = None

            time.sleep(poll_s)

    def _read_actual(self) -> Optional[float]:
        try:
            raw = self.temp_controller.query_actual(1)
            text = raw.decode("ascii", errors="ignore") if isinstance(raw, (bytes, bytearray)) else str(raw)
            cleaned = "".join(ch for ch in text if ch in "+-0123456789.")
            return float(cleaned) if cleaned and cleaned not in ("+", "-") else None
        except (ValueError, OSError, TimeoutError, RuntimeError):
            return None

    def _execute_step(self, idx: int, step: BaseTempStep) -> None:
        logger.info("Step %d: %s [%s] -> %s°C", idx, step.step_name, step.temp_cycle_type, step.temperature)
        if isinstance(step, RampStep):
            # For ramp, set setpoint and monitor until within a looser tolerance or duration based on ramp rate
            ramp_rate = getattr(step, "ramp_rate", None) or 1.0  # °C/min
            current = self._read_actual()
            est_minutes = abs((step.temperature - (current or step.temperature)) / ramp_rate) if ramp_rate else 0
            logger.info("Ramping approx %.1f minutes at %.2f°C/min", est_minutes, ramp_rate)
            # Use step's ramp tolerances if provided, else defaults
            self._set_and_wait(
                setpoint_c=step.temperature,
                offset_c=getattr(step, "temp_controller_offset", 0.0),
                initial_delay_s=getattr(step, "initial_delay", 60),
                tolerance_c=getattr(step, "settlement_tolerance", 1.0),
                window_s=getattr(step, "settlement_window", 900),
                poll_s=getattr(step, "monitoring_interval", 10),
            )
        elif isinstance(step, (DwellStep, SoakStep, BaseTempStep)):
            self._set_and_wait(
                setpoint_c=step.temperature,
                offset_c=getattr(step, "temp_controller_offset", 0.0),
                initial_delay_s=getattr(step, "initial_delay", 60),
                tolerance_c=getattr(step, "settlement_tolerance", 0.6),
                window_s=getattr(step, "settlement_window", 300),
                poll_s=getattr(step, "monitoring_interval", 3),
            )
            dwell_minutes = getattr(step, "total_time", 0)
            if dwell_minutes:
                logger.info("Dwelling for %s minutes", dwell_minutes)
                time.sleep(int(dwell_minutes) * 60)

    def _run_tests_for_step(
        self,
        step: BaseTempStep,
        sno: str,
        paths: List[str],
        golden_tests: bool,
    ) -> None:
        # Map step flags to test manager booleans
        sig_a_tests = any([
            getattr(step, "psat_tests", False),
            getattr(step, "gain_tests", False),
            getattr(step, "phase_tests", False),
            getattr(step, "pin_pout_tests", False),
        ])
        na_tests = any([
            getattr(step, "na_tests", False),
            getattr(step, "S11_tests", False),
            getattr(step, "S22_tests", False),
        ])

        logger.info(
            "Running tests: SIG_A=%s, NA=%s on %d paths", sig_a_tests, na_tests, len(paths)
        )
        for p in paths:
            self.test_manager.run_and_process_tests(
                path=p,
                sno=sno,
                sig_a_tests=sig_a_tests,
                na_tests=na_tests,
                golden_tests=golden_tests,
                options={},
            )
