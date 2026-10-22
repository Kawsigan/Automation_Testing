import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.config import Config
from utils.logger import get_logger

logger = get_logger("test_smoke")


@pytest.mark.smoke
class TestSmoke:
    """
    Smoke test suite validating application availability and core page rendering.
    """

    def test_app_launch_and_login_page_rendered(self, driver):
        """
        TC-SMOKE-01: Verify Keepwisely CMMS opens successfully, renders the
        Angular application, and displays the login form with email input.
        """
        logger.info(f"Navigating to Base URL: {Config.BASE_URL}")
        driver.get(Config.BASE_URL)

        wait = WebDriverWait(driver, timeout=Config.EXPLICIT_WAIT)

        # 1. Verify page title matches Keepwisely branding
        logger.info("Waiting for page title verification...")
        is_title_correct = wait.until(
            EC.title_contains("Keep Wisely"),
            message=f"Page title did not contain 'Keep Wisely'. Current title: '{driver.title}'"
        )
        assert is_title_correct, f"Expected title to contain 'Keep Wisely', but got '{driver.title}'"
        logger.info(f"Page title verified successfully: '{driver.title}'")

        # 2. Wait for Angular application root component to mount
        logger.info("Waiting for Angular <app-root> component to attach...")
        app_root = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "app-root")),
            message="Angular <app-root> component was not found in the DOM."
        )
        assert app_root is not None, "Angular <app-root> failed to mount."

        # 3. Wait for the initial loading overlay (#global-loader) to disappear if present
        try:
            wait.until(
                EC.invisibility_of_element_located((By.ID, "global-loader")),
                message="Global loader did not disappear within timeout."
            )
            logger.info("Global loading screen dismissed.")
        except Exception:
            logger.info("Global loader was already absent or dismissed quickly.")

        # 4. Explicitly wait for the Email/Username input field to become visible and interactive
        logger.info("Verifying login form email/username input field...")
        email_input = wait.until(
            EC.visibility_of_element_located((
                By.CSS_SELECTOR,
                "#email, #useremail, input[formcontrolname='email'], input[type='email'], input[placeholder*='email']"
            )),
            message="Login email/username input field was not visible on the login page."
        )

        assert email_input.is_displayed(), "Email input field is not displayed on the screen."
        assert email_input.is_enabled(), "Email input field is disabled and cannot accept input."
        logger.info("Smoke verification passed: Keepwisely login page loaded and interactive.")
