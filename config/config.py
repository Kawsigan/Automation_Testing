import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from the project root if it exists
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    # Fallback to .env.example defaults if .env not yet created
    load_dotenv(BASE_DIR / ".env.example")


class Config:
    """
    Central framework configuration reading from environment variables with sensible defaults.
    """
    # Application URLs
    BASE_URL = os.getenv("BASE_URL", "https://app.keepwisely.com").rstrip("/")
    LOGIN_URL = f"{BASE_URL}/auth/login"

    # Browser execution settings
    BROWSER = os.getenv("BROWSER", "chrome").lower()
    HEADLESS = os.getenv("HEADLESS", "false").lower() in ("true", "1", "yes")

    # Timeouts (in seconds)
    EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", "15"))
    PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))

    # Directory Paths
    REPORTS_DIR = BASE_DIR / "reports"
    SCREENSHOTS_DIR = BASE_DIR / "screenshots"
    LOGS_DIR = BASE_DIR / "logs"

    # Test Credentials (read from environment, sanitized of accidental whitespace)
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip()
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
