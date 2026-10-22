#!/usr/bin/env python3
"""
Keepwisely CMMS - Load Testing Orchestrator
-------------------------------------------
Executes Locust-based load & performance benchmarks for Keepwisely CMMS:
- Headless automated runs with self-contained HTML reports and CSV stats
- Interactive live Web UI dashboard at http://localhost:8089
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOCUSTFILE = BASE_DIR / "load_tests" / "locustfile.py"
REPORTS_DIR = BASE_DIR / "reports"
DEFAULT_HTML_REPORT = REPORTS_DIR / "load_test_report.html"
DEFAULT_CSV_PREFIX = REPORTS_DIR / "load_test_stats"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Keepwisely CMMS Load & Performance Tests via Locust"
    )
    parser.add_argument(
        "-u", "--users",
        type=int,
        default=25,
        help="Number of concurrent virtual users to simulate (default: 25)",
    )
    parser.add_argument(
        "-r", "--spawn-rate",
        type=int,
        default=5,
        help="Rate to spawn users per second (default: 5)",
    )
    parser.add_argument(
        "-t", "--run-time",
        type=str,
        default="30s",
        help="Test duration (e.g., 15s, 30s, 1m, 5m) (default: 30s)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="https://api.keepwisely.com",
        help="Target base host URL (default: https://api.keepwisely.com)",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch interactive Locust Web UI at http://localhost:8089 instead of headless",
    )
    parser.add_argument(
        "--html",
        type=str,
        default=str(DEFAULT_HTML_REPORT),
        help=f"Path for generated HTML report (default: {DEFAULT_HTML_REPORT})",
    )
    parser.add_argument(
        "--user-class",
        type=str,
        default="KeepwiselyAuthUser",
        choices=["KeepwiselyAuthUser", "KeepwiselyBurstStressUser"],
        help="User class to simulate (default: KeepwiselyAuthUser)",
    )
    parser.add_argument(
        "--tags",
        type=str,
        default=None,
        help="Filter tasks by tag (e.g. auth, resilience, handshake)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Determine python / locust executable
    venv_locust = BASE_DIR / "venv" / "Scripts" / "locust.exe"
    if venv_locust.exists():
        locust_cmd = str(venv_locust)
    else:
        locust_cmd = "locust"

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=" * 70)
    print("[LOAD TEST] Keepwisely CMMS Load Testing Runner")
    print("=" * 70)
    print(f"Locustfile : {LOCUSTFILE}")
    print(f"Target Host: {args.host}")
    print(f"User Class : {args.user_class}")

    if args.web:
        print("\n[WEB UI] Starting Interactive Locust Web Dashboard...")
        print("Open your browser and navigate to: http://localhost:8089")
        print("Press Ctrl+C in terminal to stop.")
        cmd = [
            locust_cmd,
            "-f", str(LOCUSTFILE),
            "--host", args.host,
            args.user_class,
        ]
    else:
        print(f"Users      : {args.users} concurrent VUs")
        print(f"Spawn Rate : {args.spawn_rate} users/sec")
        print(f"Run Time   : {args.run_time}")
        print(f"HTML Report: {args.html}")
        print(f"CSV Stats  : {DEFAULT_CSV_PREFIX}_*.csv")
        print("\nExecuting headless load test. Please wait...\n")

        cmd = [
            locust_cmd,
            "-f", str(LOCUSTFILE),
            "--headless",
            "-u", str(args.users),
            "-r", str(args.spawn_rate),
            "--run-time", args.run_time,
            "--host", args.host,
            "--html", args.html,
            "--csv", str(DEFAULT_CSV_PREFIX),
            args.user_class,
        ]

    if args.tags:
        cmd.extend(["--tags", args.tags])

    # Run Locust
    try:
        proc = subprocess.run(cmd, cwd=str(BASE_DIR))
        exit_code = proc.returncode

        if not args.web:
            if exit_code == 0:
                print("\n[SUCCESS] Load Test Completed Successfully!")
                print(f"HTML Performance Report: file:///{Path(args.html).resolve().as_posix()}")
                print(f"CSV Statistical Logs   : file:///{DEFAULT_CSV_PREFIX.resolve().as_posix()}_stats.csv")
            else:
                print(f"\n[WARNING] Load test finished with exit code {exit_code}")
        sys.exit(exit_code)

    except KeyboardInterrupt:
        print("\n[ABORTED] Load test interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Error executing load test: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
