import argparse
import sys
from pathlib import Path

# Ensure repository root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from temp_new import TempProfileManager


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate and summarize a temperature profile JSON")
    ap.add_argument("--profile", required=True, help="Path to JSON profile")
    args = ap.parse_args()

    profile_path = Path(args.profile).resolve()
    if not profile_path.exists():
        print(f"ERROR: Profile not found: {profile_path}")
        return 2

    try:
        mgr = TempProfileManager(str(profile_path))
        steps = mgr.get_all_steps()
        print(f"OK: parsed steps = {len(steps)}")
        if steps:
            print(f"FIRST: {steps[0].step_name} {steps[0].temp_cycle_type} {steps[0].temperature}")
            print(f"LAST: {steps[-1].step_name} {steps[-1].temp_cycle_type} {steps[-1].temperature}")
            enabled = sum(1 for s in steps if s.has_any_tests())
            print(f"TEST_STEPS: {enabled}")
        return 0
    except Exception as exc:
        print(f"ERROR: Failed to parse profile: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
