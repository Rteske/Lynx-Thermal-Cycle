"""
Run the quick (dummy) thermal cycle profile.

Defaults to 'profiles/dummy_thermal_cycle_1.json'.
Use --sim to run without hardware (simulation mode).
"""
from __future__ import annotations

import argparse
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the quick dummy thermal cycle profile")
    parser.add_argument(
        "--profile",
        default=os.path.join("profiles", "dummy_thermal_cycle_1.json"),
        help="Path to the profile JSON (default: profiles/dummy_thermal_cycle_1.json)",
    )
    parser.add_argument(
        "--sim",
        action="store_true",
        help="Run in simulation mode (no hardware)",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="Scale factor for delays/dwells (e.g., 0.02 makes 1 min -> ~1.2s)",
    )
    args = parser.parse_args()

    # Ensure repository root is on sys.path for 'src' and 'instruments' imports
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from src.core.lynx_thermal_cycle import LynxThermalCycleManager

    print(f"Starting thermal cycle: profile='{args.profile}', sim={args.sim}")
    mgr = LynxThermalCycleManager(simulation_mode=bool(args.sim), dwell_scale=float(args.scale))
    mgr.run_thermal_cycle(args.profile)
    print("Thermal cycle run complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
