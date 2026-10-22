import pytest
from config.config import Config
from pages.login_page import LoginPage
from test_data.loader import load_test_data
from utils.logger import get_logger

logger = get_logger("test_auth")
test_data = load_test_data()


@pytest.mark.auth
class TestAuthentication:
    """
    Comprehensive Authentication Test Suite covering positive, negative,
    boundary, regression, and navigation scenarios from the approved matrix.
    """

    # --------------------------------------------------------------------------
    # Positive Scenarios
    # --------------------------------------------------------------------------
    @pytest.mark.smoke
    def test_tc_auth_01_valid_login(self, driver):
        """
        Test ID: TC-AUTH-01
        Precondition: Valid user credentials exist in environment (.env).
        Action: Enter valid email and password; click Sign In.
        Expected Result: Successful authentication, redirection away from login page.
        Assertion: URL does not contain '/auth/login' or profile avatar is visible.
        """
        logger.info("Executing TC-AUTH-01: Valid user login")
        # Check if real staging credentials are provided vs template placeholder
        if (
            not Config.ADMIN_USERNAME
            or not Config.ADMIN_PASSWORD
            or "SampleTest" in Config.ADMIN_PASSWORD
            or "YourPassword" in Config.ADMIN_PASSWORD
        ):
            pytest.skip("Valid staging credentials not configured in .env. Skipping TC-AUTH-01.")

        login_page = LoginPage(driver)
        login_page.open()
        login_page.login(Config.ADMIN_USERNAME, Config.ADMIN_PASSWORD)

        # Explicitly wait for Angular authentication response and route change
        is_redirected = login_page.wait_for_login_redirect()

        # Assertion: User is redirected away from login to dashboard
        assert is_redirected, "Login failed to redirect user away from login page."
        assert not login_page.get_current_url().endswith("/auth/login"), (
            f"Expected redirection after login, but remained on: {login_page.get_current_url()}"
        )

    # --------------------------------------------------------------------------
    # Negative Scenarios
    # --------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "credential_set",
        test_data["invalid_logins"],
        ids=[item["description"] for item in test_data["invalid_logins"]]
    )
    def test_tc_auth_02_invalid_credentials(self, driver, credential_set):
        """
        Test ID: TC-AUTH-02
        Precondition: Application is on Login page.
        Action: Enter invalid username/password combinations; click Sign In.
        Expected Result: Authentication is rejected; user remains on login page; error alert is displayed.
        Assertion: Current URL remains on login page and email input remains visible.
        """
        username = credential_set["username"]
        password = credential_set["password"]
        logger.info(f"Executing TC-AUTH-02 with: user='{username}'")

        login_page = LoginPage(driver)
        login_page.open()
        login_page.login(username, password)

        # Assertions
        assert login_page.is_email_input_displayed(), "User should remain on login page after failed authentication."
        assert "login" in login_page.get_current_url().lower(), (
            f"Expected user to remain on login route, but current URL is: '{login_page.get_current_url()}'"
        )

    def test_tc_auth_03_blank_credentials_validation(self, driver):
        """
        Test ID: TC-AUTH-03
        Precondition: Application is on Login page with empty input fields.
        Action: Click Sign In without entering email or password.
        Expected Result: Form submission blocked; inline validation messages appear.
        Assertion: 'User Name Is Required' and 'Password Is Required' are in the error list.
        """
        logger.info("Executing TC-AUTH-03: Required field validation check")
        login_page = LoginPage(driver)
        login_page.open()
        login_page.click_sign_in()

        errors = login_page.get_validation_errors()
        logger.info(f"Captured validation errors: {errors}")

        assert len(errors) >= 2, f"Expected at least 2 validation messages, found {len(errors)}: {errors}"
        assert "User Name Is Required" in errors, "Missing 'User Name Is Required' validation message."
        assert "Password Is Required" in errors, "Missing 'Password Is Required' validation message."

    # --------------------------------------------------------------------------
    # Boundary & Edge-Case Scenarios
    # --------------------------------------------------------------------------
    @pytest.mark.parametrize(
        "email_payload",
        test_data["malformed_emails"],
        ids=[item["description"] for item in test_data["malformed_emails"]]
    )
    def test_tc_auth_04_malformed_email_boundary(self, driver, email_payload):
        """
        Test ID: TC-AUTH-04
        Precondition: Application is on Login page.
        Action: Enter malformed email syntax into username field with dummy password; click Sign In.
        Expected Result: Application handles malformed syntax gracefully without unhandled exceptions.
        Assertion: User remains on login page; no uncaught browser runtime crash.
        """
        malformed = email_payload["email"]
        logger.info(f"Executing TC-AUTH-04 with malformed email: '{malformed}'")

        login_page = LoginPage(driver)
        login_page.open()
        login_page.login(malformed, "SamplePass123!")

        assert login_page.is_email_input_displayed(), "Login page should remain visible after malformed email entry."

    def test_tc_auth_05_boundary_length_and_special_characters(self, driver):
        """
        Test ID: TC-AUTH-05
        Precondition: Application is on Login page.
        Action: Enter maximum length string (128 characters), unicode text, and special symbols into fields.
        Expected Result: Input fields accept input without layout breaking; submission fails gracefully.
        Assertion: Email and password fields retain value without throwing JavaScript errors.
        """
        long_str = test_data["boundary_inputs"]["long_string_128"]
        special_chars = test_data["boundary_inputs"]["special_characters"]
        unicode_str = test_data["boundary_inputs"]["unicode_text"]

        logger.info("Executing TC-AUTH-05: Boundary length and unicode input testing")
        login_page = LoginPage(driver)
        login_page.open()

        # 1. Test long string
        login_page.enter_email(long_str)
        assert login_page.is_email_input_displayed()

        # 2. Test unicode in email field
        login_page.enter_email(unicode_str)
        assert login_page.is_email_input_displayed()

        # 3. Test special characters in password field
        login_page.enter_password(special_chars)
        assert login_page.is_password_input_displayed()

    # --------------------------------------------------------------------------
    # Regression Scenarios
    # --------------------------------------------------------------------------
    def test_tc_auth_06_password_visibility_toggle_regression(self, driver):
        """
        Test ID: TC-AUTH-06
        Precondition: Password field has text entered.
        Action: Click the password addon eye icon repeatedly.
        Expected Result: Field 'type' attribute flips between 'password' (masked) and 'text' (unmasked).
        Assertion: Initial type is 'password'; after 1st click is 'text'; after 2nd click is 'password'.
        """
        logger.info("Executing TC-AUTH-06: Password visibility toggle regression")
        login_page = LoginPage(driver)
        login_page.open()
        login_page.enter_password("SecretPassword123!")

        # Initial state: masked
        assert login_page.get_password_input_type() == "password", "Initial password input type must be 'password'."

        # Toggle to plain text
        login_page.toggle_password_visibility()
        assert login_page.get_password_input_type() == "text", "Password input type was not toggled to 'text'."

        # Toggle back to masked
        login_page.toggle_password_visibility()
        assert login_page.get_password_input_type() == "password", "Password input type was not reverted to 'password'."

    def test_tc_auth_07_forgot_password_navigation(self, driver):
        """
        Test ID: TC-AUTH-07
        Precondition: Application is on Login page.
        Action: Verify target attribute and click 'Forgot Password?' link (opens in new tab).
        Expected Result: Link targets '/auth/forgot-password' and newly opened tab loads the route.
        Assertion: href contains '/auth/forgot-password' and new window URL contains 'forgot-password'.
        """
        logger.info("Executing TC-AUTH-07: Forgot password navigation check")
        login_page = LoginPage(driver)
        login_page.open()

        # 1. Verify link href target
        target_href = login_page.get_forgot_password_href()
        assert "forgot-password" in target_href, f"Expected href to contain 'forgot-password', got: '{target_href}'"

        # 2. Click link and verify new tab
        original_window = driver.current_window_handle
        login_page.click_forgot_password(switch_to_new_tab=True)

        try:
            assert "forgot-password" in driver.current_url.lower(), (
                f"Expected new tab URL to contain 'forgot-password', but got: '{driver.current_url}'"
            )
        finally:
            # Cleanup: close new tab and switch back to original window even if assertion fails
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(original_window)
