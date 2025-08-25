import argparse
import logging
import os
import sys

from logging_utils import configure_logging
from src.lynx_thermal.temp_steps_runner import TempStepsExecutor
from lynx_pa_top_level_test_manager import PaTopLevelTestManager


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run steps-based thermal cycle (temp_new-style)")
    p.add_argument("--profile", required=True, help="Path to steps profile JSON")
    p.add_argument("--sno", required=True, help="DUT serial number for logs")
    p.add_argument("--path", dest="paths", action="append", help="Measurement path name. Repeat for multiple.")
    p.add_argument("--golden-tests", action="store_true", help="Run golden unit tests")
    p.add_argument("--sim", action="store_true", help="Use instrument simulation mode")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    if not os.path.exists(args.profile):
        print(f"Profile not found: {args.profile}", file=sys.stderr)
        return 2

    configure_logging(args.sno)
    logging.getLogger().setLevel(logging.INFO)

    mgr = PaTopLevelTestManager(sim=args.sim)
    runner = TempStepsExecutor(test_manager=mgr)
    try:
        runner.run_profile(
            profile_path=args.profile,
            sno=args.sno,
            paths=args.paths,
            golden_tests=args.golden_tests,
        )
        logging.info("Steps cycle completed successfully.")
        return 0
    except KeyboardInterrupt:
        logging.info("Interrupted by user.")
        return 130
    except (OSError, RuntimeError, ValueError) as exc:
        logging.exception("Steps cycle failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
