"""
Temp Offset Calibration Tool
---------------------------------
Iteratively adjust the temperature controller setpoint so that a probe (temp_probe1)
reads a desired target temperature. Reports and saves the resulting setpoint offset.

Usage (examples):
  python scripts/temp_offset_tool.py --target 40 --tol 0.3 --kp 0.8 --settle 120 \
    --channel 1 --visa GPIB0::29::INSTR

Notes:
- By default uses an Agilent 34401A over VISA for the probe. Provide --visa.
- Alternatively, you can use a Dracal probe via --dracal-sno.
- The TempController uses COM5 as defined in instruments/temp_controller.py.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from typing import Optional

from instruments.temp_controller import TempController
from instruments.temp_probe import Agilent34401A, DracalTempProbe


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def parse_controller_value(raw: object) -> Optional[float]:
    try:
        if isinstance(raw, (bytes, bytearray)):
            text = raw.decode(errors="ignore")
        else:
            text = str(raw)
        # Parse first float-like number in the string
        import re

        m = re.search(r"[-+]?\d+(?:\.\d+)?", text)
        return float(m.group(0)) if m else None
    except (ValueError, TypeError):
        return None


class ProbeReader:
    def __init__(self, visa: Optional[str] = None, dracal_sno: Optional[str] = None):
        if visa:
            self.kind = "agilent"
            self._probe = Agilent34401A(visa)
        elif dracal_sno:
            self.kind = "dracal"
            self._probe = DracalTempProbe(dracal_sno)
        else:
            raise SystemExit("Provide either --visa for Agilent 34401A or --dracal-sno for Dracal probe")

    def read_c(self) -> Optional[float]:
        try:
            val = self._probe.measure_temp()
            if val is None:
                return None
            # Agilent path returns a float already; Dracal returns bytes slice in current impl
            if isinstance(val, (bytes, bytearray)):
                try:
                    text = val.decode(errors="ignore")
                except (ValueError, AttributeError):
                    text = str(val)
                import re

                m = re.search(r"[-+]?\d+(?:\.\d+)?", text)
                return float(m.group(0)) if m else None
            # Some implementations might return strings
            if isinstance(val, str):
                try:
                    return float(val.strip())
                except (ValueError, TypeError):
                    import re

                    m = re.search(r"[-+]?\d+(?:\.\d+)?", val)
                    return float(m.group(0)) if m else None
            return float(val)
        except (ValueError, OSError, RuntimeError):
            return None


def calibrate_single(
    ctrl: TempController,
    probe: ProbeReader,
    chan: int,
    target: float,
    tol: float,
    kp: float,
    settle: int,
    max_iters: int,
    poll: float,
    csv_path: Optional[str] = None,
    start_setpoint: Optional[float] = None,
):
    """Run a single-point calibration to align probe to target.

    Returns dict with keys: target_c, final_setpoint_c, offset_c, csv, converged(bool), iterations(int).
    """
    # Determine starting setpoint
    current_sp = start_setpoint
    if current_sp is None:
        try:
            current_sp = parse_controller_value(ctrl.query_setpoint(chan))
        except (OSError, RuntimeError):
            current_sp = None
    if current_sp is None:
        current_sp = float(target)

    # Prepare logging
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    if csv_path is None:
        csv_path = os.path.join("logs", f"temp_offset_{ts}_T{int(round(target))}.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    if not os.path.exists(csv_path):
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(
                "timestamp,iter,setpoint_c,controller_actual_c,probe_c,delta_to_target_c,action,new_setpoint_c\n"
            )

    # Ensure starting setpoint is applied
    try:
        ctrl.set_setpoint(chan, float(current_sp))
    except (OSError, RuntimeError, ValueError):
        pass

    def read_controller_actual() -> Optional[float]:
        try:
            raw = ctrl.query_actual(chan)
            return parse_controller_value(raw)
        except (OSError, RuntimeError):
            return None

    iter_idx = 0
    consecutive_ok = 0

    # Initial settle before first measurement for this target
    time.sleep(max(0.5, min(settle, 5)))

    while iter_idx < int(max_iters):
        # Observe during settle window
        end = time.time() + float(settle)
        last_probe = None
        last_tc = None
        while time.time() < end:
            last_probe = probe.read_c()
            last_tc = read_controller_actual()
            ts_now = dt.datetime.now().isoformat()
            with open(csv_path, "a", encoding="utf-8") as f:
                f.write(
                    f"{ts_now},{iter_idx},{current_sp:.3f},{'' if last_tc is None else f'{last_tc:.3f}'},{'' if last_probe is None else f'{last_probe:.3f}'},,,\n"
                )
            time.sleep(max(0.5, float(poll)))

        # Compute adjustment using the most recent probe reading
        probe_c = probe.read_c()
        ctrl_c = read_controller_actual()
        if probe_c is None:
            print("Probe reading unavailable; cannot calibrate this point.")
            break

        delta = float(target) - probe_c
        within = abs(delta) <= float(tol)
        print(
            f"Target {target:.2f} C | Iter {iter_idx}: SP={current_sp:.2f} C, probe={probe_c:.2f} C, ctrl={'' if ctrl_c is None else f'{ctrl_c:.2f} C'}, Δ={delta:+.2f} C -> {'OK' if within else 'ADJUST'}"
        )

        if within:
            consecutive_ok += 1
            if consecutive_ok >= 2:
                print(f"Converged at target {target:.2f} C")
                break
        else:
            consecutive_ok = 0

        # Adjust setpoint
        new_sp = clamp(float(current_sp) + float(kp) * delta, -45.0, 85.0)
        action = f"set_setpoint({new_sp:.3f})"
        try:
            ctrl.set_setpoint(chan, new_sp)
        except (OSError, RuntimeError, ValueError) as e:
            print(f"Failed to set setpoint: {e}")
        ts_now = dt.datetime.now().isoformat()
        with open(csv_path, "a", encoding="utf-8") as f:
            f.write(
                f"{ts_now},{iter_idx},{current_sp:.3f},{'' if ctrl_c is None else f'{ctrl_c:.3f}'},{probe_c:.3f},{delta:.3f},{action},{new_sp:.3f}\n"
            )
        current_sp = new_sp
        iter_idx += 1

    final_probe = probe.read_c()
    final_ctrl = read_controller_actual()
    offset = float(current_sp) - float(target)
    print(
        f"Final @ {target:.2f} C: SP={current_sp:.2f} C, probe={'' if final_probe is None else f'{final_probe:.2f} C'}, ctrl={'' if final_ctrl is None else f'{final_ctrl:.2f} C'}"
    )

    converged = final_probe is not None and abs(float(final_probe) - float(target)) <= float(tol)
    return {
        "target_c": float(target),
        "final_setpoint_c": float(current_sp),
        "offset_c": float(offset),
        "csv": os.path.abspath(csv_path),
        "converged": bool(converged),
        "iterations": int(iter_idx),
    }


def main():
    parser = argparse.ArgumentParser(description="Calibrate temp controller setpoint offset using a probe")
    parser.add_argument("--target", type=float, help="Target probe temperature in C")
    parser.add_argument("--tol", type=float, default=0.3, help="Tolerance band on probe temperature (C)")
    parser.add_argument("--kp", type=float, default=0.8, help="Proportional gain for setpoint adjustment")
    parser.add_argument("--settle", type=int, default=120, help="Seconds to wait after each setpoint change")
    parser.add_argument("--max-iters", type=int, default=12, help="Maximum adjustment iterations")
    parser.add_argument("--poll", type=float, default=2.0, help="Seconds between probe/controller polls")
    parser.add_argument("--channel", type=int, default=1, help="Temp controller channel (default 1)")
    parser.add_argument("--visa", type=str, help="VISA resource for Agilent 34401A (e.g., GPIB0::29::INSTR)")
    parser.add_argument("--dracal-sno", type=str, help="Dracal serial number, alternative to --visa")
    parser.add_argument("--targets", type=str, help="Comma-separated list of targets for multi-point calibration, e.g. '0,10,25,55,71'")
    parser.add_argument("--standard-multipoint", action="store_true", help="Run multi-point at 0,10,25,55,71 C")
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Optional CSV log path; defaults to logs/temp_offset_YYYYmmdd_HHMMSS.csv",
    )
    parser.add_argument(
        "--save-json",
        type=str,
        default=os.path.join("configs", "temp_controller_offset.json"),
        help="Where to write resulting offset JSON",
    )
    parser.add_argument("--no-chamber-on", action="store_true", help="Skip turning the chamber ON at start")

    args = parser.parse_args()

    # Initialize hardware
    ctrl = TempController()
    chan = int(args.channel)
    if not args.no_chamber_on:
        try:
            ctrl.set_chamber_state(True)
        except (OSError, RuntimeError):
            pass

    probe = ProbeReader(visa=args.visa, dracal_sno=args.dracal_sno)
    # Determine if multi-point or single
    targets_list: Optional[list[float]] = None
    if args.standard_multipoint:
        targets_list = [0.0, 10.0, 25.0, 55.0, 71.0]
    elif args.targets:
        try:
            targets_list = [float(x.strip()) for x in args.targets.split(",") if x.strip() != ""]
        except (ValueError, AttributeError) as exc:
            raise SystemExit("Failed to parse --targets. Use format like: 0,10,25,55,71") from exc

    # Shared start setpoint from controller to smooth transitions
    try:
        start_sp = parse_controller_value(ctrl.query_setpoint(chan))
    except (OSError, RuntimeError):
        start_sp = None

    # Single-point mode
    if not targets_list:
        if args.target is None:
            raise SystemExit("Provide --target or use --standard-multipoint/--targets for multi-point calibration.")
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = args.csv or os.path.join("logs", f"temp_offset_{ts}.csv")
        print(
            f"Starting temp offset calibration -> target={args.target:.2f} C, tol=±{args.tol:.2f} C, channel={chan}"
        )
        result = calibrate_single(
            ctrl=ctrl,
            probe=probe,
            chan=chan,
            target=float(args.target),
            tol=float(args.tol),
            kp=float(args.kp),
            settle=int(args.settle),
            max_iters=int(args.max_iters),
            poll=float(args.poll),
            csv_path=csv_path,
            start_setpoint=start_sp,
        )
        offset = result["offset_c"]
        # Persist JSON
        try:
            os.makedirs(os.path.dirname(args.save_json), exist_ok=True)
            payload = {
                "timestamp": dt.datetime.now().isoformat(),
                "target_c": result["target_c"],
                "final_setpoint_c": result["final_setpoint_c"],
                "offset_c": offset,
                "controller_channel": chan,
                "tolerance_c": float(args.tol),
                "kp": float(args.kp),
                "settle_s": int(args.settle),
                "max_iters": int(args.max_iters),
                "probe": {
                    "type": "agilent" if args.visa else "dracal",
                    "visa": args.visa,
                    "dracal_sno": args.dracal_sno,
                },
                "csv": result["csv"],
            }
            with open(args.save_json, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            print(f"Saved offset JSON -> {args.save_json}")
        except (OSError, TypeError) as e:
            print(f"Warning: failed to save JSON: {e}")

        return 0 if result.get("converged") else 1

    # Multi-point mode
    print(
        f"Starting MULTI-POINT temp offset calibration -> targets={targets_list}, tol=±{args.tol:.2f} C, channel={chan}"
    )
    summary = []
    current_sp = start_sp
    for t in targets_list:
        res = calibrate_single(
            ctrl=ctrl,
            probe=probe,
            chan=chan,
            target=float(t),
            tol=float(args.tol),
            kp=float(args.kp),
            settle=int(args.settle),
            max_iters=int(args.max_iters),
            poll=float(args.poll),
            csv_path=None,  # auto-name per target
            start_setpoint=current_sp,
        )
        summary.append(res)
        current_sp = res.get("final_setpoint_c", current_sp)

    # Persist summary JSON (table of offsets)
    try:
        os.makedirs(os.path.dirname(args.save_json), exist_ok=True)
        table = {str(int(round(item["target_c"]))): item["offset_c"] for item in summary}
        payload = {
            "timestamp": dt.datetime.now().isoformat(),
            "controller_channel": chan,
            "tolerance_c": float(args.tol),
            "kp": float(args.kp),
            "settle_s": int(args.settle),
            "max_iters": int(args.max_iters),
            "probe": {
                "type": "agilent" if args.visa else "dracal",
                "visa": args.visa,
                "dracal_sno": args.dracal_sno,
            },
            "points": summary,
            "table": table,
        }
        with open(args.save_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"Saved multi-point offset JSON -> {args.save_json}")
    except (OSError, TypeError) as e:
        print(f"Warning: failed to save JSON: {e}")

    # Exit with success if all points converged
    all_ok = all(p.get("converged") for p in summary)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
