import json
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional


class TraceLogger:
    """Structured JSONL trace logger for thermal test sessions."""

    def __init__(self, base_dir: str, sno: str, label: str = "trace") -> None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        traces_dir = os.path.join(base_dir, "logs", "traces")
        os.makedirs(traces_dir, exist_ok=True)
        fname = f"{label}_{sno}_{ts}.jsonl" if sno else f"{label}_{ts}.jsonl"
        self.filepath = os.path.join(traces_dir, fname)
        self._f = open(self.filepath, "a", encoding="utf-8")

    def _now(self) -> Dict[str, Any]:
        return {"ts": time.time(), "iso": datetime.now().isoformat(timespec="seconds")}

    def event(self, name: str, **fields: Any) -> None:
        rec: Dict[str, Any] = {"event": name, **self._now(), **fields}
        self._f.write(json.dumps(rec) + "\n")
        self._f.flush()

    # Convenience wrappers
    def session_start(self, profile: str, paths: list[str], params: Optional[Dict[str, Any]] = None) -> None:
        self.event("session_start", profile=profile, paths=paths, params=params or {})

    def session_end(self, status: str = "ok") -> None:
        self.event("session_end", status=status)

    def chamber(self, state: bool) -> None:
        self.event("chamber", state="on" if state else "off")

    def step_start(self, idx: int, step_name: str, cycle_type: str, target_c: float, meta: Optional[Dict[str, Any]] = None) -> None:
        self.event("step_start", index=idx, step_name=step_name, type=cycle_type, target_c=target_c, meta=meta or {})

    def step_end(self, idx: int, status: str = "ok") -> None:
        self.event("step_end", index=idx, status=status)

    def temp(self, channel: int, setpoint_c: float, actual_c: Optional[float], err_c: Optional[float], in_tol: bool, stable_elapsed_s: float) -> None:
        self.event(
            "temp_read",
            channel=channel,
            setpoint_c=setpoint_c,
            actual_c=actual_c,
            error_c=err_c,
            in_tolerance=in_tol,
            stable_elapsed_s=stable_elapsed_s,
        )

    def dwell(self, action: str, seconds: int) -> None:
        self.event("dwell", action=action, seconds=seconds)

    def tests(self, action: str, path: Optional[str] = None, sig_a: Optional[bool] = None, na: Optional[bool] = None, golden: Optional[bool] = None) -> None:
        self.event("tests", action=action, path=path, sig_a=sig_a, na=na, golden=golden)

    def close(self) -> None:
        try:
            self._f.close()
        except OSError:
            pass
