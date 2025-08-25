import json
import logging
import time
from typing import Optional, Dict, Any, List

from instruments.temp_controller import TempController
from lynx_pa_top_level_test_manager import PaTopLevelTestManager

logger = logging.getLogger(__name__)

class LynxThermalCycleRunner:
    """
    Runs Lynx PA top-level tests at temperature plateaus defined in a JSON profile.

    JSON profile schema (example):
    {
      "channel": 1,                   # optional, defaults to init arg
      "tolerance_c": 1.0,            # optional, overrides init tolerance
      "stability_seconds": 60,       # optional, overrides init stability
      "poll_interval_seconds": 5,    # optional, overrides init poll interval
      "steps": [
        {"temperature": -20, "dwell_seconds": 300, "label": "cold soak"},
        {"temperature": 25,  "dwell_seconds": 180, "label": "room"},
        {"temperature": 70,  "dwell_seconds": 300, "label": "hot soak"}
      ]
    }
    """

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

    # ----- Public API -----
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

        # Determine which paths to run
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

        # Ensure chamber ON
        try:
            self.temp_controller.set_chamber_state(True)
        except (OSError, TimeoutError, ValueError, RuntimeError) as exc:
            logger.error("Failed to enable chamber: %s", exc)
            raise

        for idx, step in enumerate(steps):
            target = step.get("temperature")
            dwell = int(step.get("dwell_seconds", 0))
            label = step.get("label")
            if target is None:
                logger.warning("Step %d missing 'temperature', skipping", idx)
                continue

            logger.info(
                "Step %d: setpoint=%s°C dwell=%ss label=%s", idx, target, dwell, label
            )
            self._set_setpoint_and_wait(
                channel=channel,
                setpoint_c=float(target),
                tolerance_c=tolerance,
                stability_seconds=stability_secs,
                poll_interval=poll_interval,
            )

            if dwell > 0:
                logger.info("Dwelling at %s°C for %s seconds", target, dwell)
                time.sleep(dwell)

            logger.info("Running tests at plateau %s°C for %d path(s)", target, len(paths))
            for test_path in paths:
                logger.info("Running path: %s", test_path)
                self.test_manager.run_and_process_tests(
                    path=test_path,
                    sno=sno,
                    sig_a_tests=sig_a_tests,
                    na_tests=na_tests,
                    golden_tests=golden_tests,
                    options=options or {},
                )

        logger.info("Completed thermal cycle profile: %s", profile_path)

    # ----- Internal helpers -----
    def _load_profile(self, profile_path: str) -> Dict[str, Any]:
        with open(profile_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _decode_temp(self, raw: bytes) -> Optional[float]:
        try:
            text = raw.decode("ascii", errors="ignore")
            # Extract a float-like substring
            # Common instrument formats: "+023.4", "-20.0", "25.0\r\n"
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
        # Apply setpoint (TempController clamps internally to device limits)
        self.temp_controller.set_setpoint(channel, setpoint_c)

        logger.info(
            "Waiting for stability: setpoint=%s°C ±%s°C for %ss",
            setpoint_c,
            tolerance_c,
            stability_seconds,
        )

        stable_start: Optional[float] = None
        deadline: Optional[float] = None  # No global timeout unless desired

        while True:
            actual = self._get_actual_temp(channel)
            if actual is None:
                logger.debug("Temp read failed; retrying in %ss", poll_interval)
                time.sleep(poll_interval)
                continue

            error = abs(actual - setpoint_c)
            logger.debug("Actual=%s°C error=%s°C", actual, error)

            if error <= tolerance_c:
                if stable_start is None:
                    stable_start = time.time()
                elapsed = time.time() - stable_start
                if elapsed >= stability_seconds:
                    logger.info("Temperature stable: actual=%s°C", actual)
                    return
            else:
                stable_start = None  # reset stability timer

            if deadline and time.time() > deadline:
                logger.warning(
                    "Stability timeout reached; proceeding. last_actual=%s°C", actual
                )
                return

            time.sleep(poll_interval)

if __name__ == "__main__":
    # Optional quick smoke (adjust args before real use)
    logging.basicConfig(level=logging.INFO)
    runner = LynxThermalCycleRunner()
    # Example usage (edit with real values):
    # runner.run_profile(
    #     profile_path="configs/thermal_profile.json",
    #     path="HIGH_BAND_PATH1 (Vertical)",
    #     sno="DUT-1234",
    #     sig_a_tests=False,
    #     na_tests=True,
    #     golden_tests=False,
    # )
