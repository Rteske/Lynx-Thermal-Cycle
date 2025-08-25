import logging
import time
from typing import Optional, Dict, Any, List
from pathlib import Path

from instruments.temp_controller import TempController
from lynx_pa_top_level_test_manager import PaTopLevelTestManager
# Using standard logging; structured JSONL tracing removed per request

logger = logging.getLogger(__name__)


class LynxThermalCycleRunner:
    def __init__(
        self,
        temp_controller: Optional[TempController] = None,
        test_manager: Optional[PaTopLevelTestManager] = None,
        temp_channel: int = 1,
        tolerance_c: float = 1.0,
        stability_seconds: int = 60,
        poll_interval_seconds: float = 5.0,
    ) -> None:
        self.temp_controller = temp_controller or TempController()
        self.test_manager = test_manager or PaTopLevelTestManager(sim=False)
        self.temp_channel = temp_channel
        self.tolerance_c = tolerance_c
        self.stability_seconds = stability_seconds
        self.poll_interval_seconds = poll_interval_seconds

    def run_profile(
        self,
        profile_path: str,
        path: Optional[str | List[str]] = None,
        sno: str = "",
        sig_a_tests: bool = False,
        na_tests: bool = True,
        golden_tests: bool = False,
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        profile = self._load_profile(profile_path)
        channel = int(profile.get("channel", self.temp_channel))
        tolerance = float(profile.get("tolerance_c", self.tolerance_c))
        stability_secs = int(profile.get("stability_seconds", self.stability_seconds))
        poll_interval = float(profile.get("poll_interval_seconds", self.poll_interval_seconds))

        steps: List[Dict[str, Any]] = profile.get("steps", [])
        if not steps:
            logger.warning("No steps found in profile: %s", profile_path)
            return

        profile_paths = profile.get("paths")
        if profile_paths is not None and not isinstance(profile_paths, list):
            raise TypeError("profile 'paths' must be a list of strings")

        if profile_paths is None and path is None:
            raise ValueError("No paths provided. Specify 'paths' in the profile or pass --path/--paths via CLI.")

        paths: List[str] = []
        if profile_paths is not None:
            paths = [str(p) for p in profile_paths]
        elif isinstance(path, list):
            paths = [str(p) for p in path]
        elif isinstance(path, str):
            paths = [path]

        # Session start
        logger.info(
            "Thermal cycle start | profile=%s | paths=%s | params=%s",
            str(Path(profile_path).resolve()),
            paths,
            dict(channel=channel, tol=tolerance, stable=stability_secs, poll=poll_interval),
        )
        # Chamber on
        try:
            self.temp_controller.set_chamber_state(True)
            logger.info("Chamber enabled")
        except (OSError, TimeoutError, ValueError, RuntimeError) as exc:
            logger.error("Failed to enable chamber: %s", exc)
            raise

        # Execute steps
        for idx, step in enumerate(steps):
            target = step.get("temperature")
            dwell = int(step.get("dwell_seconds", 0))
            label = step.get("label")
            if target is None:
                logger.warning("Step %d missing 'temperature', skipping", idx)
                continue

            logger.info(
                "Step %d start | type=DWELL | setpoint=%.2f°C | dwell=%ds | label=%s",
                idx,
                float(target),
                dwell,
                label,
            )
            self._set_setpoint_and_wait(
                channel=channel,
                setpoint_c=float(target),
                tolerance_c=tolerance,
                stability_seconds=stability_secs,
                poll_interval=poll_interval,
            )

            if dwell > 0:
                logger.info("Dwell start | at %.2f°C for %d seconds", float(target), dwell)
                time.sleep(dwell)
                logger.info("Dwell end | at %.2f°C for %d seconds", float(target), dwell)

            logger.info(
                "Tests start | plateau=%.2f°C | paths=%d | flags={sig_a=%s, na=%s, golden=%s}",
                float(target),
                len(paths),
                sig_a_tests,
                na_tests,
                golden_tests,
            )
            for test_path in paths:
                logger.info("Tests path | %s", test_path)
                self.test_manager.run_and_process_tests(
                    path=test_path,
                    sno=sno,
                    sig_a_tests=sig_a_tests,
                    na_tests=na_tests,
                    golden_tests=golden_tests,
                    options=options or {},
                )
            logger.info("Tests end | plateau=%.2f°C", float(target))
            logger.info("Step %d end", idx)

        logger.info("Completed thermal cycle profile: %s", profile_path)
        logger.info("Thermal cycle end | status=ok")

    def _load_profile(self, profile_path: str) -> Dict[str, Any]:
        with open(profile_path, "r", encoding="utf-8") as f:
            import json
            return json.load(f)

    def _decode_temp(self, raw: bytes) -> Optional[float]:
        try:
            text = raw.decode("ascii", errors="ignore")
            cleaned = "".join(ch for ch in text if ch in "+-0123456789.")
            if not cleaned or cleaned in ("+", "-"):
                return None
            return float(cleaned)
        except (UnicodeDecodeError, ValueError):
            return None

    def _get_actual_temp(self, channel: int) -> Optional[float]:
        try:
            raw = self.temp_controller.query_actual(channel)
            return self._decode_temp(raw)
        except (OSError, TimeoutError, ValueError, RuntimeError):
            return None

    def _set_setpoint_and_wait(
        self,
        channel: int,
        setpoint_c: float,
        tolerance_c: float,
        stability_seconds: int,
        poll_interval: float,
    ) -> None:
        self.temp_controller.set_setpoint(channel, setpoint_c)
        logger.info(
            "Waiting for stability: setpoint=%s°C ±%s°C for %ss",
            setpoint_c,
            tolerance_c,
            stability_seconds,
        )
        stable_start: Optional[float] = None
        while True:
            actual = self._get_actual_temp(channel)
            if actual is None:
                logger.info("TEMP_POLL | ch=%d | setpoint=%.2f | actual=None | retry_in=%ss", channel, setpoint_c, poll_interval)
                time.sleep(poll_interval)
                continue
            error = abs(actual - setpoint_c)
            in_tol = error <= tolerance_c
            elapsed = time.time() - stable_start if stable_start is not None else 0.0
            logger.info(
                "TEMP_POLL | ch=%d | setpoint=%.2f | actual=%.2f | error=%.2f | in_tol=%s | elapsed_stable=%.1fs",
                channel,
                setpoint_c,
                actual,
                error,
                in_tol,
                elapsed,
            )

            if in_tol:
                if stable_start is None:
                    stable_start = time.time()
                elapsed = time.time() - stable_start
                if elapsed >= stability_seconds:
                    logger.info("Temperature stable: actual=%.2f°C", actual)
                    return
            else:
                stable_start = None
            time.sleep(poll_interval)
