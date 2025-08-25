import argparse
import logging
import os
import sys

from logging_utils import configure_logging, log_message
from src.lynx_thermal.thermal_cycle_runner import LynxThermalCycleRunner
from lynx_pa_top_level_test_manager import PaTopLevelTestManager


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run Lynx PA tests at temperature plateaus defined in a JSON profile."
    )
    p.add_argument("--profile", required=True, help="Path to thermal profile JSON")
    p.add_argument("--path", dest="paths", action="append", help="Measurement path name. Repeat for multiple. If omitted, uses profile 'paths' list.")
    p.add_argument("--sno", required=True, help="DUT serial number for logs")

    # Test selection flags
    p.add_argument("--sig-a-tests", action="store_true", help="Run Signal Analyzer tests")
    p.add_argument("--no-na-tests", action="store_true", help="Disable Network Analyzer tests")
    p.add_argument("--golden-tests", action="store_true", help="Run golden unit tests")

    # Runner overrides (optional; profile can also specify)
    p.add_argument("--channel", type=int, default=None, help="Chamber channel to use (overrides profile)")
    p.add_argument("--tolerance", type=float, default=None, help="Temperature tolerance in C (overrides profile)")
    p.add_argument("--stability", type=int, default=None, help="Stability time in seconds (overrides profile)")
    p.add_argument("--poll", type=float, default=None, help="Polling interval seconds (overrides profile)")

    # Simulation mode for instruments
    p.add_argument("--sim", action="store_true", help="Use instrument simulation mode")

    return p.parse_args()


def main() -> int:
    args = parse_args()

    if not os.path.exists(args.profile):
        print(f"Profile not found: {args.profile}", file=sys.stderr)
        return 2

    # Configure logging to file + console via logging_utils
    configure_logging(args.sno)
    logging.getLogger().setLevel(logging.INFO)

    # Initialize manager (respect sim flag)
    test_manager = PaTopLevelTestManager(sim=args.sim)

    # Allow CLI overrides by constructing runner with parameters if provided
    runner_kwargs = {}
    if args.channel is not None:
        runner_kwargs["temp_channel"] = args.channel
    if args.tolerance is not None:
        runner_kwargs["tolerance_c"] = args.tolerance
    if args.stability is not None:
        runner_kwargs["stability_seconds"] = args.stability
    if args.poll is not None:
        runner_kwargs["poll_interval_seconds"] = args.poll

    runner = LynxThermalCycleRunner(test_manager=test_manager, **runner_kwargs)

    try:
        runner.run_profile(
            profile_path=args.profile,
            path=args.paths,
            sno=args.sno,
            sig_a_tests=args.sig_a_tests,
            na_tests=not args.no_na_tests,
            golden_tests=args.golden_tests,
            options={},
        )
        log_message("Thermal cycle completed successfully.")
        return 0
    except KeyboardInterrupt:
        log_message("Interrupted by user.")
        return 130
    except (OSError, RuntimeError, ValueError) as exc:
        logging.exception("Thermal cycle failed: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
