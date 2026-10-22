import os
import subprocess
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOCUSTFILE = BASE_DIR / "load_tests" / "locustfile.py"
REPORTS_DIR = BASE_DIR / "reports"


@pytest.mark.load
class TestLoadAndPerformance:
    """
    Automated Load & Performance Test Suite for Keepwisely CMMS.
    Validates server responsiveness, throughput (RPS), and failure resilience under concurrent virtual users.
    """

    def test_tc_load_01_auth_concurrency_benchmark(self):
        """
        Test ID: TC-LOAD-01
        Precondition: Locust load testing framework installed.
        Action: Simulate 15 concurrent virtual users performing authentication & session handshake for 15s.
        Expected Result: 
        - Load test executes without process failure
        - Self-contained HTML report generated at reports/load_test_report.html
        - No server crash (HTTP 500) detected
        """
        report_html = REPORTS_DIR / "load_test_report.html"
        csv_prefix = REPORTS_DIR / "load_test_stats"
        venv_locust = BASE_DIR / "venv" / "Scripts" / "locust.exe"
        locust_cmd = str(venv_locust) if venv_locust.exists() else "locust"

        cmd = [
            locust_cmd,
            "-f", str(LOCUSTFILE),
            "--headless",
            "-u", "15",
            "-r", "5",
            "--run-time", "15s",
            "--host", "https://api.keepwisely.com",
            "--html", str(report_html),
            "--csv", str(csv_prefix),
            "KeepwiselyAuthUser",
        ]

        result = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True)
        print("\n--- Locust Output ---")
        print(result.stdout)

        assert result.returncode == 0, f"Locust load test failed with exit code {result.returncode}: {result.stderr}"
        assert report_html.exists(), f"Load test report not found at {report_html}"
        assert report_html.stat().st_size > 1000, "Load test report HTML should not be empty"

    def test_tc_load_02_burst_spike_resilience(self):
        """
        Test ID: TC-LOAD-02
        Precondition: Locust load testing framework installed.
        Action: Execute high-throughput burst spike test using FastHttpUser for 10s.
        Expected Result:
        - Server maintains stability without unhandled exceptions
        - Preflight CORS and authentication endpoints respond cleanly
        """
        venv_locust = BASE_DIR / "venv" / "Scripts" / "locust.exe"
        locust_cmd = str(venv_locust) if venv_locust.exists() else "locust"

        cmd = [
            locust_cmd,
            "-f", str(LOCUSTFILE),
            "--headless",
            "-u", "20",
            "-r", "10",
            "--run-time", "10s",
            "--host", "https://api.keepwisely.com",
            "KeepwiselyBurstStressUser",
        ]

        result = subprocess.run(cmd, cwd=str(BASE_DIR), capture_output=True, text=True)
        print("\n--- Burst Stress Output ---")
        print(result.stdout)

        assert result.returncode == 0, f"Burst stress test failed: {result.stderr}"
