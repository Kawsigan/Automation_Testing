import os
import sys
import json
import random
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from locust import HttpUser, FastHttpUser, task, between, events, tag
from config.config import Config


# API Endpoints
API_HOST = os.getenv("API_BASE_URL", "https://api.keepwisely.com")
APP_HOST = Config.BASE_URL.rstrip("/")

COMMON_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": APP_HOST,
    "Referer": f"{APP_HOST}/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=" * 70)
    print("[START] Keepwisely CMMS Load Test Initialized")
    print(f"Target API Host: {environment.host or API_HOST}")
    print(f"Target App Host: {APP_HOST}")
    print("Workflows: Authentication, Session Handshake & Brute-Force Resilience")
    print("=" * 70)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("\n" + "=" * 70)
    print("[STOP] Keepwisely CMMS Load Test Completed")
    total_reqs = environment.stats.total.num_requests
    total_fails = environment.stats.total.num_failures
    fail_rate = (total_fails / total_reqs * 100) if total_reqs > 0 else 0
    print(f"Total Requests: {total_reqs} | Failures: {total_fails} ({fail_rate:.2f}%)")
    print(f"Avg Response Time: {environment.stats.total.avg_response_time:.2f} ms")
    print(f"Max Response Time: {environment.stats.total.max_response_time:.2f} ms")
    print("=" * 70 + "\n")


class KeepwiselyAuthUser(HttpUser):
    """
    Simulates real user authentication behavior on Keepwisely CMMS:
    - Visits login portal frontend
    - Fetches language & menu configuration
    - Performs CORS preflight checks
    - Authenticates credentials
    - Tests brute-force and negative credential resilience under load
    """
    wait_time = between(1, 3)
    host = API_HOST

    def on_start(self):
        """Called when a virtual user starts running."""
        self.auth_token = None
        self.session_valid = False

    @tag("frontend", "portal")
    @task(2)
    def visit_login_portal(self):
        """Loads the Angular front-end application shell at /auth/login."""
        with self.client.get(
            f"{APP_HOST}/auth/login",
            headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"},
            name="[Frontend] GET /auth/login",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to load login page: HTTP {response.status_code}")

    @tag("config", "bootstrap")
    @task(3)
    def fetch_language_config(self):
        """Fetches bootstrap language & menu settings required by the login component."""
        params = {"data": json.dumps({"menu_model": "1"})}
        with self.client.get(
            "/language/en",
            params=params,
            headers=COMMON_HEADERS,
            name="[API] GET /language/en (Bootstrap Config)",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Language bootstrap failed: HTTP {response.status_code}")

    @tag("handshake", "cors")
    @task(2)
    def options_preflight_check(self):
        """Measures preflight CORS OPTIONS latency for the authentication route."""
        preflight_headers = {
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
            "Origin": APP_HOST,
        }
        with self.client.options(
            "/auths/login",
            headers=preflight_headers,
            name="[Handshake] OPTIONS /auths/login (CORS Preflight)",
            catch_response=True,
        ) as response:
            # OPTIONS typically responds 200 or 204
            if response.status_code in (200, 204):
                response.success()
            else:
                response.failure(f"OPTIONS preflight failed: HTTP {response.status_code}")

    @tag("auth", "positive")
    @task(3)
    def submit_valid_login(self):
        """
        Attempts legitimate authentication using configured admin credentials.
        If default placeholder credentials are used, checks for clean rejection.
        """
        username = Config.ADMIN_USERNAME or "admin@keepwisely.com"
        password = Config.ADMIN_PASSWORD or "Keepwisely@2026!"

        payload = {
            "username": username,
            "password": password,
        }

        with self.client.post(
            "/auths/login",
            json=payload,
            headers=COMMON_HEADERS,
            name="[Auth] POST /auths/login (Standard Auth)",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    self.auth_token = data.get("token") or data.get("access_token")
                    self.session_valid = True
                except Exception:
                    pass
                response.success()
            elif response.status_code in (400, 401):
                # Clean negative response (e.g. User not found / Invalid credentials)
                # is an expected functional validation when test credentials don't exist on live
                response.success()
            else:
                response.failure(f"Unexpected server error during login: HTTP {response.status_code} - {response.text[:100]}")

    @tag("resilience", "negative")
    @task(3)
    def submit_invalid_credentials_stress(self):
        """
        Stresses the authentication endpoint with randomized invalid credentials.
        Ensures the backend properly rejects attacks with HTTP 400/401 and does NOT crash with HTTP 500.
        """
        random_suffix = random.randint(1000, 999999)
        payload = {
            "username": f"stress_user_{random_suffix}@invalid-domain.test",
            "password": f"WrongPass_{random_suffix}!",
        }

        with self.client.post(
            "/auths/login",
            json=payload,
            headers=COMMON_HEADERS,
            name="[Resilience] POST /auths/login (Invalid User Stress)",
            catch_response=True,
        ) as response:
            # Expected response is 400 or 401
            if response.status_code in (400, 401):
                response.success()
            elif response.status_code == 500:
                response.failure(f"SERVER CRASH (HTTP 500) under negative authentication load: {response.text[:100]}")
            elif response.status_code == 429:
                # Rate limited - good security behavior!
                response.success()
            else:
                response.failure(f"Unexpected HTTP code {response.status_code}: {response.text[:100]}")

    @tag("session", "handshake")
    @task(2)
    def simulate_session_ping(self):
        """
        Simulates authenticated or guest session activity pinging the application.
        """
        headers = dict(COMMON_HEADERS)
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        with self.client.get(
            "/language/en",
            params={"data": json.dumps({"menu_model": "1"})},
            headers=headers,
            name="[Session] GET /language/en (Session Ping)",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 304):
                response.success()
            else:
                response.failure(f"Session ping failed: HTTP {response.status_code}")


class KeepwiselyBurstStressUser(FastHttpUser):
    """
    High-throughput virtual user for spike and stress testing using C-optimized FastHttpUser.
    Ideal for testing maximum server capacity and peak concurrency.
    """
    wait_time = between(0.1, 0.5)
    host = API_HOST

    @task(5)
    def burst_login_preflight(self):
        self.client.options(
            "/auths/login",
            headers={"Origin": APP_HOST},
            name="[Burst] OPTIONS /auths/login (Spike Preflight)",
        )

    @task(5)
    def burst_login_requests(self):
        payload = {
            "username": "burst_test@keepwisely.com",
            "password": "BurstPassword123!",
        }
        with self.client.post(
            "/auths/login",
            json=payload,
            headers=COMMON_HEADERS,
            name="[Burst] POST /auths/login (High-RPS Auth)",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 400, 401, 429):
                response.success()
            else:
                response.failure(f"Burst server error: {response.status_code}")
