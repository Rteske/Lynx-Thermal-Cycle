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
        print(f"[DEBUG] Initializing ProbeReader with visa={visa}, dracal_sno={dracal_sno}")
        if visa:
            self.kind = "agilent"
            print(f"[DEBUG] Creating Agilent34401A probe with VISA: {visa}")
            self._probe = Agilent34401A(visa)
            print(f"[DEBUG] Agilent34401A probe created successfully")
        elif dracal_sno:
            self.kind = "dracal"
            print(f"[DEBUG] Creating DracalTempProbe with serial: {dracal_sno}")
            self._probe = DracalTempProbe(dracal_sno)
            print(f"[DEBUG] DracalTempProbe created successfully")
        else:
            print(f"[ERROR] No probe specified - need either --visa or --dracal-sno")
            raise SystemExit("Provide either --visa for Agilent 34401A or --dracal-sno for Dracal probe")

    def read_c(self) -> Optional[float]:
        print(f"[DEBUG] Reading temperature from {self.kind} probe...")
        try:
            val = self._probe.measure_temp()
            print(f"[DEBUG] Raw probe reading: {val} (type: {type(val)})")
            if val is None:
                print(f"[DEBUG] Probe returned None")
                return None
            # Agilent path returns a float already; Dracal returns bytes slice in current impl
            if isinstance(val, (bytes, bytearray)):
                try:
                    text = val.decode(errors="ignore")
                    print(f"[DEBUG] Decoded bytes to text: '{text}'")
                except (ValueError, AttributeError):
                    text = str(val)
                    print(f"[DEBUG] Converted bytes to string: '{text}'")
                import re

                m = re.search(r"[-+]?\d+(?:\.\d+)?", text)
                result = float(m.group(0)) if m else None
                print(f"[DEBUG] Extracted float from text: {result}")
                return result
            # Some implementations might return strings
            if isinstance(val, str):
                print(f"[DEBUG] Got string value: '{val}'")
                try:
                    result = float(val.strip())
                    print(f"[DEBUG] Converted string to float: {result}")
                    return result
                except (ValueError, TypeError):
                    print(f"[DEBUG] Failed to convert string to float, trying regex...")
                    import re

                    m = re.search(r"[-+]?\d+(?:\.\d+)?", val)
                    result = float(m.group(0)) if m else None
                    print(f"[DEBUG] Regex extracted float: {result}")
                    return result
            result = float(val)
            print(f"[DEBUG] Direct float conversion: {result}")
            return result
        except (ValueError, OSError, RuntimeError) as e:
            print(f"[ERROR] Exception reading probe: {e}")
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
    print(f"[DEBUG] Starting calibrate_single for target={target}°C, tol=±{tol}°C, kp={kp}")
    print(f"[DEBUG] Parameters: settle={settle}s, max_iters={max_iters}, poll={poll}s, channel={chan}")
    
    # Determine starting setpoint
    current_sp = start_setpoint
    if current_sp is None:
        print(f"[DEBUG] No start setpoint provided, querying controller...")
        try:
            raw_sp = ctrl.query_setpoint(chan)
            print(f"[DEBUG] Controller returned setpoint: {raw_sp}")
            current_sp = parse_controller_value(raw_sp)
            print(f"[DEBUG] Parsed setpoint: {current_sp}")
        except (OSError, RuntimeError) as e:
            print(f"[ERROR] Failed to query setpoint: {e}")
            current_sp = None
    else:
        print(f"[DEBUG] Using provided start setpoint: {current_sp}")
        
    if current_sp is None:
        current_sp = float(target)
        print(f"[DEBUG] Defaulting to target temperature as setpoint: {current_sp}")

    # Prepare logging
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    if csv_path is None:
        csv_path = os.path.join("logs", f"temp_offset_{ts}_T{int(round(target))}.csv")
    print(f"[DEBUG] CSV log path: {csv_path}")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    if not os.path.exists(csv_path):
        print(f"[DEBUG] Creating new CSV file with headers")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(
                "timestamp,iter,setpoint_c,controller_actual_c,probe_c,delta_to_target_c,action,new_setpoint_c\n"
            )
    else:
        print(f"[DEBUG] CSV file already exists")

    # Ensure starting setpoint is applied
    print(f"[DEBUG] Setting initial setpoint to {current_sp}°C")
    try:
        ctrl.set_setpoint(chan, float(current_sp))
        print(f"[DEBUG] Setpoint set successfully")
    except (OSError, RuntimeError, ValueError) as e:
        print(f"[ERROR] Failed to set initial setpoint: {e}")

    def read_controller_actual() -> Optional[float]:
        try:
            raw = ctrl.query_actual(chan)
            print(f"[DEBUG] Controller actual raw: {raw}")
            result = parse_controller_value(raw)
            print(f"[DEBUG] Controller actual parsed: {result}")
            return result
        except (OSError, RuntimeError) as e:
            print(f"[ERROR] Failed to read controller actual: {e}")
            return None

    iter_idx = 0
    consecutive_ok = 0

    # Initial settle before first measurement for this target
    initial_settle = max(0.5, min(settle, 5))
    print(f"[DEBUG] Initial settle time: {initial_settle}s")
    time.sleep(initial_settle)
    print(f"[DEBUG] Initial settle complete, starting calibration loop")

    while iter_idx < int(max_iters):
        print(f"\n[DEBUG] === Iteration {iter_idx} ===")
        # Observe during settle window
        end = time.time() + float(settle)
        print(f"[DEBUG] Starting {settle}s settle period...")
        last_probe = None
        last_tc = None
        poll_count = 0
        while time.time() < end:
            poll_count += 1
            print(f"[DEBUG] Poll {poll_count} during settle...")
            last_probe = probe.read_c()
            last_tc = read_controller_actual()
            print(f"[DEBUG] Poll readings - probe: {last_probe}°C, controller: {last_tc}°C")
            ts_now = dt.datetime.now().isoformat()
            with open(csv_path, "a", encoding="utf-8") as f:
                f.write(
                    f"{ts_now},{iter_idx},{current_sp:.3f},{'' if last_tc is None else f'{last_tc:.3f}'},{'' if last_probe is None else f'{last_probe:.3f}'},,,\n"
                )
            time.sleep(max(0.5, float(poll)))
        
        print(f"[DEBUG] Settle period complete after {poll_count} polls")

        # Compute adjustment using the most recent probe reading
        print(f"[DEBUG] Taking final readings for iteration {iter_idx}...")
        probe_c = probe.read_c()
        ctrl_c = read_controller_actual()
        print(f"[DEBUG] Final readings - probe: {probe_c}°C, controller: {ctrl_c}°C")
        
        if probe_c is None:
            print("[ERROR] Probe reading unavailable; cannot calibrate this point.")
            break

        delta = float(target) - probe_c
        within = abs(delta) <= float(tol)
        print(f"[DEBUG] Delta calculation: target({target}) - probe({probe_c}) = {delta}")
        print(f"[DEBUG] Within tolerance? {within} (|{delta}| <= {tol})")
        
        print(
            f"Target {target:.2f} C | Iter {iter_idx}: SP={current_sp:.2f} C, probe={probe_c:.2f} C, ctrl={'' if ctrl_c is None else f'{ctrl_c:.2f} C'}, Δ={delta:+.2f} C -> {'OK' if within else 'ADJUST'}"
        )

        if within:
            consecutive_ok += 1
            print(f"[DEBUG] Within tolerance, consecutive_ok count: {consecutive_ok}")
            if consecutive_ok >= 2:
                print(f"Converged at target {target:.2f} C")
                break
        else:
            consecutive_ok = 0
            print(f"[DEBUG] Not within tolerance, reset consecutive_ok to 0")

        # Adjust setpoint
        adjustment = float(kp) * delta
        new_sp = clamp(float(current_sp) + adjustment, -45.0, 85.0)
        print(f"[DEBUG] Setpoint adjustment: current({current_sp}) + kp({kp}) * delta({delta}) = {current_sp + adjustment}")
        print(f"[DEBUG] Clamped new setpoint: {new_sp} (range: -45.0 to 85.0)")
        
        action = f"set_setpoint({new_sp:.3f})"
        print(f"[DEBUG] Applying new setpoint: {new_sp}°C")
        try:
            ctrl.set_setpoint(chan, new_sp)
            print(f"[DEBUG] Setpoint applied successfully")
        except (OSError, RuntimeError, ValueError) as e:
            print(f"[ERROR] Failed to set setpoint: {e}")
            
        ts_now = dt.datetime.now().isoformat()
        with open(csv_path, "a", encoding="utf-8") as f:
            f.write(
                f"{ts_now},{iter_idx},{current_sp:.3f},{'' if ctrl_c is None else f'{ctrl_c:.3f}'},{probe_c:.3f},{delta:.3f},{action},{new_sp:.3f}\n"
            )
        current_sp = new_sp
        iter_idx += 1
        print(f"[DEBUG] Iteration {iter_idx-1} complete, moving to next iteration")

    print(f"\n[DEBUG] Calibration loop finished after {iter_idx} iterations")
    print(f"[DEBUG] Taking final readings...")
    final_probe = probe.read_c()
    final_ctrl = read_controller_actual()
    offset = float(current_sp) - float(target)
    
    print(f"[DEBUG] Final calculations:")
    print(f"[DEBUG] - Final probe reading: {final_probe}°C")
    print(f"[DEBUG] - Final controller reading: {final_ctrl}°C")
    print(f"[DEBUG] - Final setpoint: {current_sp}°C")
    print(f"[DEBUG] - Target: {target}°C")
    print(f"[DEBUG] - Offset: {current_sp} - {target} = {offset}°C")
    
    print(
        f"Final @ {target:.2f} C: SP={current_sp:.2f} C, probe={'' if final_probe is None else f'{final_probe:.2f} C'}, ctrl={'' if final_ctrl is None else f'{final_ctrl:.2f} C'}"
    )

    converged = final_probe is not None and abs(float(final_probe) - float(target)) <= float(tol)
    print(f"[DEBUG] Converged: {converged} (final error: {None if final_probe is None else abs(final_probe - target):.3f}°C)")
    
    result = {
        "target_c": float(target),
        "final_setpoint_c": float(current_sp),
        "offset_c": float(offset),
        "csv": os.path.abspath(csv_path),
        "converged": bool(converged),
        "iterations": int(iter_idx),
    }
    print(f"[DEBUG] Returning result: {result}")
    return result


def main():
    print("[DEBUG] Starting temp_offset_tool main()")
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
    print(f"[DEBUG] Parsed arguments: {vars(args)}")

    # Initialize hardware
    print("[DEBUG] Initializing TempController...")
    ctrl = TempController()
    print("[DEBUG] TempController created successfully")
    
    chan = int(args.channel)
    print(f"[DEBUG] Using channel: {chan}")
    
    if not args.no_chamber_on:
        print("[DEBUG] Turning chamber ON...")
        try:
            ctrl.set_chamber_state(True)
            print("[DEBUG] Chamber turned ON successfully")
        except (OSError, RuntimeError) as e:
            print(f"[ERROR] Failed to turn chamber ON: {e}")
    else:
        print("[DEBUG] Skipping chamber ON due to --no-chamber-on flag")
        
    visa = "GPIB0::29::INSTR"
    print(f"[DEBUG] Using hardcoded VISA address: {visa}")
    probe = ProbeReader(visa=visa)
    # Determine if multi-point or single
    targets_list: Optional[list[float]] = None
    if args.standard_multipoint:
        targets_list = [0.0, 10.0, 25.0, 55.0, 71.0]
        print(f"[DEBUG] Using standard multipoint targets: {targets_list}")
    elif args.targets:
        print(f"[DEBUG] Parsing custom targets: '{args.targets}'")
        try:
            targets_list = [float(x.strip()) for x in args.targets.split(",") if x.strip() != ""]
            print(f"[DEBUG] Parsed custom targets: {targets_list}")
        except (ValueError, AttributeError) as exc:
            print(f"[ERROR] Failed to parse targets: {exc}")
            raise SystemExit("Failed to parse --targets. Use format like: 0,10,25,55,71") from exc
    else:
        print("[DEBUG] Single-point mode (no multi-point flags)")

    # Shared start setpoint from controller to smooth transitions
    print("[DEBUG] Querying initial setpoint from controller...")
    try:
        raw_start_sp = ctrl.query_setpoint(chan)
        print(f"[DEBUG] Raw start setpoint: {raw_start_sp}")
        start_sp = parse_controller_value(raw_start_sp)
        print(f"[DEBUG] Parsed start setpoint: {start_sp}")
    except (OSError, RuntimeError) as e:
        print(f"[ERROR] Failed to query start setpoint: {e}")
        start_sp = None

    # Single-point mode
    if not targets_list:
        print("[DEBUG] Running single-point calibration")
        if args.target is None:
            print("[ERROR] No target temperature specified for single-point mode")
            raise SystemExit("Provide --target or use --standard-multipoint/--targets for multi-point calibration.")
        
        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = args.csv or os.path.join("logs", f"temp_offset_{ts}.csv")
        print(f"[DEBUG] Single-point CSV path: {csv_path}")
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
        
        print(f"[DEBUG] Single-point calibration result: {result}")
        offset = result["offset_c"]
        
        # Persist JSON
        print(f"[DEBUG] Saving single-point results to JSON: {args.save_json}")
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
            print(f"[DEBUG] JSON payload: {payload}")
            with open(args.save_json, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2)
            print(f"Saved offset JSON -> {args.save_json}")
        except (OSError, TypeError) as e:
            print(f"Warning: failed to save JSON: {e}")

        exit_code = 0 if result.get("converged") else 1
        print(f"[DEBUG] Exiting with code: {exit_code}")
        return exit_code

    # Multi-point mode
    print("[DEBUG] Running multi-point calibration")
    print(
        f"Starting MULTI-POINT temp offset calibration -> targets={targets_list}, tol=±{args.tol:.2f} C, channel={chan}"
    )
    summary = []
    current_sp = start_sp
    
    for i, t in enumerate(targets_list):
        print(f"\n[DEBUG] === Multi-point calibration {i+1}/{len(targets_list)}: Target {t}°C ===")
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
        print(f"[DEBUG] Target {t}°C result: {res}")
        summary.append(res)
        current_sp = res.get("final_setpoint_c", current_sp)
        print(f"[DEBUG] Updated current setpoint for next target: {current_sp}°C")

    print(f"\n[DEBUG] Multi-point calibration complete. Summary: {summary}")
    
    # Persist summary JSON (table of offsets)
    print(f"[DEBUG] Saving multi-point results to JSON: {args.save_json}")
    try:
        os.makedirs(os.path.dirname(args.save_json), exist_ok=True)
        table = {str(int(round(item["target_c"]))): item["offset_c"] for item in summary}
        print(f"[DEBUG] Offset table: {table}")
        
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
        print(f"[DEBUG] Multi-point JSON payload: {payload}")
        
        with open(args.save_json, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        print(f"Saved multi-point offset JSON -> {args.save_json}")
    except (OSError, TypeError) as e:
        print(f"Warning: failed to save JSON: {e}")

    # Exit with success if all points converged
    all_ok = all(p.get("converged") for p in summary)
    print(f"[DEBUG] All points converged: {all_ok}")
    
    exit_code = 0 if all_ok else 1
    print(f"[DEBUG] Exiting with code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    print("[DEBUG] Script started")
    exit_code = main()
    print(f"[DEBUG] Script finished with exit code: {exit_code}")
    sys.exit(exit_code)
