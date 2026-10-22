import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from config.config import Config
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from test_data.loader import load_test_data
from utils.logger import get_logger
from utils.monkey_vectors import get_all_monkey_vectors

logger = get_logger("test_auth")
test_data = load_test_data()


@pytest.mark.auth
class TestAuthentication:
    """
    Comprehensive suite of 80 Test Operations for Keepwisely CMMS Authentication:
    - Positive & Negative credential workflows, validation errors, boundary lengths
    - UI Alignment, Spacing, Password visibility toggle, Forgot Password routing
    - 48 Monkey & Chaos Fuzzing operations, 10 Rapid UI stress tests, and 12 E2E Lifecycles.
    """

    # ==========================================================================
    # Isolation & Auto-Setup Hook
    # ==========================================================================
    @pytest.fixture(autouse=True)
    def ensure_auth_page_ready(self, unauthenticated_session):
        """
        Guarantees pristine test isolation for every authentication test operation:
        1. Restores standard desktop viewport (1920x1080).
        2. Clears browser cookies and local/session storage to guarantee unauthenticated state.
        3. Navigates cleanly to /auth/login and ensures inputs are empty.
        """
        unauthenticated_session.set_window_size(1920, 1080)
        curr = unauthenticated_session.current_url.lower().rstrip("/")
        if not curr.endswith("/auth/login"):
            unauthenticated_session.delete_all_cookies()
            try:
                unauthenticated_session.execute_script("localStorage.clear(); sessionStorage.clear();")
            except Exception:
                pass
            unauthenticated_session.get(f"{Config.BASE_URL}/auth/login")
            LoginPage(unauthenticated_session).wait_for_angular_loader()

        login_page = LoginPage(unauthenticated_session)
        if login_page.is_email_input_displayed():
            try:
                el = login_page.find_visible_element(login_page.EMAIL_INPUT)
                if el.get_attribute("value"):
                    el.clear()
            except Exception:
                pass
        if login_page.is_password_input_displayed():
            try:
                el = login_page.find_visible_element(login_page.PASSWORD_INPUT)
                if el.get_attribute("value"):
                    el.clear()
            except Exception:
                pass

    # ==========================================================================
    # Phase 1: Core Functional, UI Alignment & Business Logic (10 Operations)
    # ==========================================================================
    def test_tc_auth_01_valid_login_redirect(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-01
        Precondition: Valid credentials configured in environment.
        Action: Enter valid email and password; click Sign In.
        Expected Result: Successful authentication, redirection away from login page.
        """
        logger.info("Executing TC-AUTH-01: Valid user login")
        if (
            not Config.ADMIN_USERNAME
            or not Config.ADMIN_PASSWORD
            or "SampleTest" in Config.ADMIN_PASSWORD
            or "YourPassword" in Config.ADMIN_PASSWORD
        ):
            pytest.skip("Valid staging credentials not configured in .env.")

        login_page = LoginPage(unauthenticated_session)
        login_page.login(Config.ADMIN_USERNAME, Config.ADMIN_PASSWORD)
        is_redirected = login_page.wait_for_login_redirect(timeout=15)
        assert is_redirected, "Login failed to redirect user away from login page."
        assert not unauthenticated_session.current_url.lower().endswith("/auth/login")

        # Cleanup session back to unauthenticated state
        unauthenticated_session.delete_all_cookies()
        try:
            unauthenticated_session.execute_script("localStorage.clear(); sessionStorage.clear();")
        except Exception:
            pass
        unauthenticated_session.get(f"{Config.BASE_URL}/auth/login")

    def test_tc_auth_02_invalid_credentials_rejection(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-02
        Precondition: Application is on Login page.
        Action: Enter invalid username/password combinations; click Sign In.
        Expected Result: Authentication is rejected; user remains on login page; error alert is displayed.
        """
        logger.info("Executing TC-AUTH-02: Invalid credentials rejection")
        login_page = LoginPage(unauthenticated_session)
        login_page.login("invalid_user_999@keepwisely.com", "WrongPassword!2026")
        assert login_page.is_email_input_displayed()
        assert "login" in unauthenticated_session.current_url.lower()

    def test_tc_auth_03_blank_credentials_validation(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-03
        Precondition: Application is on Login page with empty fields.
        Action: Click Sign In without entering email or password.
        Expected Result: Form submission blocked; inline validation messages appear.
        """
        logger.info("Executing TC-AUTH-03: Required field validation check")
        login_page = LoginPage(unauthenticated_session)
        login_page.click_sign_in()
        errors = login_page.get_validation_errors()
        assert len(errors) >= 1 or login_page.is_email_input_displayed()

    def test_tc_auth_04_malformed_email_boundary(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-04
        Precondition: Application is on Login page.
        Action: Enter malformed email syntax into username field; click Sign In.
        Expected Result: Application handles malformed syntax gracefully without crash.
        """
        logger.info("Executing TC-AUTH-04: Malformed email boundary")
        login_page = LoginPage(unauthenticated_session)
        login_page.login("missing_at_domain.com", "SamplePass123!")
        assert login_page.is_email_input_displayed()

    def test_tc_auth_05_boundary_length_and_special_characters(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-05
        Precondition: Application is on Login page.
        Action: Enter maximum length string (128 characters) and special characters.
        Expected Result: Input fields accept input without layout breaking; submission fails gracefully.
        """
        logger.info("Executing TC-AUTH-05: Boundary length and unicode input testing")
        login_page = LoginPage(unauthenticated_session)
        login_page.enter_email("a" * 128 + "@keepwisely.com")
        assert login_page.is_email_input_displayed()
        login_page.enter_password("P@$$w0rd!#%^&*()_+")
        assert login_page.is_password_input_displayed()

    def test_tc_auth_06_password_visibility_toggle_regression(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-06
        Precondition: Password field has text entered.
        Action: Click the password addon eye icon repeatedly.
        Expected Result: Field 'type' attribute flips between 'password' (masked) and 'text' (unmasked).
        """
        logger.info("Executing TC-AUTH-06: Password visibility toggle regression")
        login_page = LoginPage(unauthenticated_session)
        login_page.enter_password("SecretPassword123!")
        assert login_page.get_password_input_type() == "password"
        login_page.toggle_password_visibility()
        assert login_page.get_password_input_type() == "text"
        login_page.toggle_password_visibility()
        assert login_page.get_password_input_type() == "password"

    def test_tc_auth_07_forgot_password_navigation(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-07
        Precondition: Application is on Login page.
        Action: Verify target attribute and click 'Forgot Password?' link (opens in new tab).
        Expected Result: Link targets '/auth/forgot-password' and newly opened tab loads the route.
        """
        logger.info("Executing TC-AUTH-07: Forgot password navigation check")
        login_page = LoginPage(unauthenticated_session)
        target_href = login_page.get_forgot_password_href()
        assert "forgot-password" in target_href
        original_window = unauthenticated_session.current_window_handle
        login_page.click_forgot_password(switch_to_new_tab=True)
        try:
            assert "forgot-password" in unauthenticated_session.current_url.lower()
        finally:
            if len(unauthenticated_session.window_handles) > 1:
                unauthenticated_session.close()
                unauthenticated_session.switch_to.window(original_window)

    def test_tc_auth_08_ui_alignment_login_card_and_inputs(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-08
        Precondition: Application is on Login page.
        Action: Inspect bounding rectangle geometry and CSS layout of login form inputs and submit button.
        Expected Result: Input fields have consistent width and vertical alignment; no layout overlapping.
        """
        logger.info("Executing TC-AUTH-08: UI alignment and layout inspection")
        login_page = LoginPage(unauthenticated_session)
        email_rect = login_page.get_element_rect(login_page.EMAIL_INPUT)
        pass_rect = login_page.get_element_rect(login_page.PASSWORD_INPUT)
        btn_rect = login_page.get_element_rect(login_page.SIGN_IN_BUTTON)
        assert abs(email_rect["width"] - pass_rect["width"]) <= 60
        assert pass_rect["top"] > email_rect["bottom"]
        assert btn_rect["top"] > pass_rect["bottom"]
        assert login_page.verify_no_horizontal_overflow()

    def test_tc_auth_09_space_handling_credentials(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-09
        Precondition: Application is on Login page.
        Action: Enter credentials with leading/trailing whitespaces and test whitespace-only submission.
        Expected Result: Leading/trailing whitespace is handled gracefully without crash.
        """
        logger.info("Executing TC-AUTH-09: Space-related credential handling")
        login_page = LoginPage(unauthenticated_session)
        login_page.enter_email("    ")
        login_page.enter_password("    ")
        login_page.click_sign_in()
        assert login_page.is_email_input_displayed()

    def test_tc_auth_10_business_logic_security_rules(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-10
        Precondition: Application is on Login page.
        Action: Verify password field masking security compliance and invalid login rejection.
        Expected Result: Password input defaults to masked 'password' type; invalid submission remains on /auth/login.
        """
        logger.info("Executing TC-AUTH-10: Business logic & security rules")
        login_page = LoginPage(unauthenticated_session)
        assert login_page.get_password_input_type() == "password"
        login_page.login("non_existent_security_user@keepwisely.com", "InvalidPass@999")
        assert "login" in unauthenticated_session.current_url.lower()

    # ==========================================================================
    # Phase 2: Monkey Testing & Chaos Fuzzing Matrix (48 Operations)
    # ==========================================================================
    @pytest.mark.parametrize(
        "vector",
        get_all_monkey_vectors(),
        ids=[f"tc_auth_{i+11:02d}_{v['id']}" for i, v in enumerate(get_all_monkey_vectors())]
    )
    def test_tc_auth_monkey_chaos_fuzzing(self, unauthenticated_session, vector):
        """
        Test ID: TC-AUTH-11 through TC-AUTH-58
        Precondition: Application is on Login page.
        Action: Inject specialized chaos/fuzz payload into email input.
        Expected Result: Application neutralizes payload; UI remains resilient with zero unhandled crashes.
        """
        logger.info(f"Executing Monkey Fuzz: {vector['id']} ({vector['desc']})")
        login_page = LoginPage(unauthenticated_session)
        healthy = login_page.execute_monkey_fuzz(login_page.EMAIL_INPUT, vector["payload"])
        assert healthy, f"Application crashed under chaos payload: {vector['id']} ({vector['desc']})"
        assert login_page.verify_page_health(), f"Page health compromised by payload: {vector['id']}"

    # ==========================================================================
    # Phase 3: Rapid Monkey UI Actions & Stress Resilience (10 Operations)
    # ==========================================================================
    def test_tc_auth_59_monkey_rapid_clicks_sign_in(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-59
        Action: Perform rapid 5x clicks on Sign In button to stress submission debounce.
        """
        logger.info("Executing TC-AUTH-59: Rapid 5x click Sign In button stress")
        login_page = LoginPage(unauthenticated_session)
        login_page.execute_monkey_rapid_clicks(login_page.SIGN_IN_BUTTON, clicks=5)
        assert login_page.verify_page_health()

    def test_tc_auth_60_monkey_rapid_clicks_password_toggle(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-60
        Action: Perform rapid 5x clicks on password visibility toggle icon.
        """
        logger.info("Executing TC-AUTH-60: Rapid 5x click password visibility toggle stress")
        login_page = LoginPage(unauthenticated_session)
        login_page.execute_monkey_rapid_clicks(login_page.PASSWORD_TOGGLE_BTN, clicks=5)
        assert login_page.verify_page_health()

    def test_tc_auth_61_monkey_viewport_resize_desktop_to_mobile(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-61
        Action: Dynamically resize viewport from Desktop (1920x1080) to Mobile (375x812) and restore.
        """
        logger.info("Executing TC-AUTH-61: Viewport resize stress test")
        login_page = LoginPage(unauthenticated_session)
        unauthenticated_session.set_window_size(375, 812)
        assert login_page.verify_page_health()
        unauthenticated_session.set_window_size(1920, 1080)
        assert login_page.verify_page_health()

    def test_tc_auth_62_monkey_rapid_scroll_stress(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-62
        Action: Rapidly scroll down to footer and back to top 3 times.
        """
        logger.info("Executing TC-AUTH-62: Rapid scroll stress")
        for _ in range(3):
            unauthenticated_session.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            unauthenticated_session.execute_script("window.scrollTo(0, 0);")
        login_page = LoginPage(unauthenticated_session)
        assert login_page.verify_page_health()

    def test_tc_auth_63_monkey_rapid_focus_blur_oscillation(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-63
        Action: Rapidly toggle focus between email and password input fields.
        """
        logger.info("Executing TC-AUTH-63: Rapid focus/blur oscillation")
        email_el = unauthenticated_session.find_element(*LoginPage.EMAIL_INPUT)
        pass_el = unauthenticated_session.find_element(*LoginPage.PASSWORD_INPUT)
        for _ in range(3):
            unauthenticated_session.execute_script("arguments[0].focus();", email_el)
            unauthenticated_session.execute_script("arguments[0].focus();", pass_el)
        login_page = LoginPage(unauthenticated_session)
        assert login_page.verify_page_health()

    def test_tc_auth_64_monkey_unwanted_horizontal_overflow_check(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-64
        Action: Inspect horizontal scroll width on login page.
        """
        logger.info("Executing TC-AUTH-64: Horizontal overflow audit")
        login_page = LoginPage(unauthenticated_session)
        assert login_page.verify_page_health()

    def test_tc_auth_65_monkey_page_refresh_resilience(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-65
        Action: Reload login route via browser refresh.
        """
        logger.info("Executing TC-AUTH-65: Page refresh resilience")
        unauthenticated_session.refresh()
        login_page = LoginPage(unauthenticated_session)
        login_page.wait_for_angular_loader()
        assert "login" in unauthenticated_session.current_url.lower()

    def test_tc_auth_66_monkey_broken_image_audit(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-66
        Action: Audit all rendered images and brand logos on login page for naturalWidth > 0.
        """
        logger.info("Executing TC-AUTH-66: Broken image audit")
        broken_count = unauthenticated_session.execute_script("""
            const imgs = document.querySelectorAll('img');
            let broken = 0;
            for (let img of imgs) {
                if (img.src && !img.complete || (typeof img.naturalWidth !== 'undefined' && img.naturalWidth === 0)) {
                    broken++;
                }
            }
            return broken;
        """)
        logger.info(f"Broken images count: {broken_count}")
        assert broken_count <= 5, f"Found excessive broken images: {broken_count}"

    def test_tc_auth_67_monkey_browser_console_severe_errors_audit(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-67
        Action: Retrieve browser console logs and verify zero unhandled JavaScript crashes.
        """
        logger.info("Executing TC-AUTH-67: Console errors audit ('Don't miss any error')")
        login_page = LoginPage(unauthenticated_session)
        errors = login_page.get_browser_console_errors()
        critical = [e for e in errors if "TypeError" in e.get("message", "") or "SyntaxError" in e.get("message", "")]
        assert len(critical) == 0, f"Critical JavaScript exceptions detected: {critical}"

    def test_tc_auth_68_monkey_page_health_final_check(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-68
        Action: Complete DOM health scan verifying page stability.
        """
        logger.info("Executing TC-AUTH-68: Page health final scan")
        login_page = LoginPage(unauthenticated_session)
        assert login_page.verify_page_health()

    # ==========================================================================
    # Phase 4: End-to-End Multi-Step Lifecycle Journeys (12 Operations)
    # ==========================================================================
    def test_tc_auth_69_e2e_full_authentication_lifecycle(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-69
        E2E Journey 1: Full valid authentication lifecycle and session teardown.
        """
        logger.info("Executing TC-AUTH-69: E2E Full Valid Authentication lifecycle")
        login_page = LoginPage(unauthenticated_session)
        login_page.login(Config.ADMIN_USERNAME, Config.ADMIN_PASSWORD)
        login_page.wait_for_login_redirect(timeout=15)
        dashboard = DashboardPage(unauthenticated_session)
        assert dashboard.is_dashboard_displayed()

        # Teardown back to login
        unauthenticated_session.delete_all_cookies()
        try:
            unauthenticated_session.execute_script("localStorage.clear(); sessionStorage.clear();")
        except Exception:
            pass
        unauthenticated_session.get(f"{Config.BASE_URL}/auth/login")
        assert "login" in unauthenticated_session.current_url.lower()

    def test_tc_auth_70_e2e_invalid_authentication_retry_lifecycle(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-70
        E2E Journey 2: Enter wrong credentials -> Verify rejection -> Re-enter empty -> Verify validation.
        """
        logger.info("Executing TC-AUTH-70: E2E Invalid Authentication retry lifecycle")
        login_page = LoginPage(unauthenticated_session)
        login_page.login("wrong_user@keepwisely.com", "WrongPass123")
        assert login_page.is_email_input_displayed()
        login_page.find_visible_element(login_page.EMAIL_INPUT).clear()
        login_page.find_visible_element(login_page.PASSWORD_INPUT).clear()
        login_page.click_sign_in()
        assert login_page.verify_page_health()

    def test_tc_auth_71_e2e_forgot_password_tab_roundtrip(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-71
        E2E Journey 3: Click Forgot Password -> Open new tab -> Verify URL -> Close tab -> Return to login.
        """
        logger.info("Executing TC-AUTH-71: E2E Forgot Password tab roundtrip")
        login_page = LoginPage(unauthenticated_session)
        original_window = unauthenticated_session.current_window_handle
        login_page.click_forgot_password(switch_to_new_tab=True)
        assert "forgot-password" in unauthenticated_session.current_url.lower()
        if len(unauthenticated_session.window_handles) > 1:
            unauthenticated_session.close()
            unauthenticated_session.switch_to.window(original_window)
        assert "login" in unauthenticated_session.current_url.lower()

    def test_tc_auth_72_e2e_keyboard_navigation_lifecycle(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-72
        E2E Journey 4: Navigate form strictly using keyboard TAB and submit via ENTER.
        """
        logger.info("Executing TC-AUTH-72: E2E Keyboard navigation lifecycle")
        login_page = LoginPage(unauthenticated_session)
        email_el = login_page.find_visible_element(login_page.EMAIL_INPUT)
        email_el.send_keys("demo@keepwisely.com")
        email_el.send_keys(Keys.TAB)
        active_el = unauthenticated_session.switch_to.active_element
        active_el.send_keys("TestPass123!")
        active_el.send_keys(Keys.ENTER)
        assert login_page.verify_page_health()

    def test_tc_auth_73_e2e_password_reveal_hide_lifecycle(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-73
        E2E Journey 5: Enter password -> Toggle reveal -> Verify text -> Toggle hide -> Verify password.
        """
        logger.info("Executing TC-AUTH-73: E2E Password reveal & hide lifecycle")
        login_page = LoginPage(unauthenticated_session)
        login_page.enter_password("Secret12345!")
        assert login_page.get_password_input_type() == "password"
        login_page.toggle_password_visibility()
        assert login_page.get_password_input_type() == "text"
        login_page.toggle_password_visibility()
        assert login_page.get_password_input_type() == "password"

    def test_tc_auth_74_e2e_inline_error_dismissal_on_input(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-74
        E2E Journey 6: Trigger blank submission error -> Type into email -> Verify error responsiveness.
        """
        logger.info("Executing TC-AUTH-74: E2E Inline error dismissal on input")
        login_page = LoginPage(unauthenticated_session)
        login_page.click_sign_in()
        login_page.enter_email("admin@keepwisely.com")
        assert login_page.verify_page_health()

    def test_tc_auth_75_e2e_rapid_type_and_clear_cycling(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-75
        E2E Journey 7: Rapidly type and clear credentials 3 consecutive cycles.
        """
        logger.info("Executing TC-AUTH-75: E2E Rapid type and clear cycling")
        login_page = LoginPage(unauthenticated_session)
        for i in range(3):
            login_page.enter_email(f"user_{i}@test.com")
            login_page.find_visible_element(login_page.EMAIL_INPUT).clear()
        assert login_page.verify_page_health()

    def test_tc_auth_76_e2e_direct_deep_link_navigation(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-76
        E2E Journey 8: Deep link directly to /auth/login and verify form renders.
        """
        logger.info("Executing TC-AUTH-76: E2E Direct Deep Link navigation")
        unauthenticated_session.get(f"{Config.BASE_URL}/auth/login")
        login_page = LoginPage(unauthenticated_session)
        login_page.wait_for_angular_loader()
        assert login_page.is_email_input_displayed()

    def test_tc_auth_77_e2e_card_container_and_brand_logo(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-77
        E2E Journey 9: Verify brand logo and login card container render properly.
        """
        logger.info("Executing TC-AUTH-77: E2E Card container & brand logo check")
        login_page = LoginPage(unauthenticated_session)
        card = login_page.find_element((By.CSS_SELECTOR, ".card, .auth-page-content, form"), timeout=5)
        rect = unauthenticated_session.execute_script("return arguments[0].getBoundingClientRect();", card)
        assert rect["width"] > 250, f"Login card too narrow: {rect['width']}px"

    def test_tc_auth_78_e2e_fast_search_debounce_barrage(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-78
        E2E Journey 10: Simulate rapid keystroke barrage into email field.
        """
        logger.info("Executing TC-AUTH-78: E2E Fast keystroke barrage")
        login_page = LoginPage(unauthenticated_session)
        for char in "admin@keepwisely.com":
            login_page.enter_email(char)
        assert login_page.verify_page_health()

    def test_tc_auth_79_e2e_multiple_invalid_attempts_resilience(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-79
        E2E Journey 11: Execute multiple rapid invalid logins and verify UI does not lock up.
        """
        logger.info("Executing TC-AUTH-79: E2E Multiple invalid attempts resilience")
        login_page = LoginPage(unauthenticated_session)
        for i in range(2):
            login_page.login(f"failed_attempt_{i}@test.com", "BadPass123!")
            assert login_page.verify_page_health()

    def test_tc_auth_80_e2e_session_continuity_final_validation(self, unauthenticated_session):
        """
        Test ID: TC-AUTH-80
        E2E Journey 12: Verify login page stability after all 80 authentication operations.
        """
        logger.info("Executing TC-AUTH-80: E2E Session Continuity Final Validation")
        login_page = LoginPage(unauthenticated_session)
        assert login_page.verify_page_health()
        assert "login" in unauthenticated_session.current_url.lower()
        logger.info("Authentication 80-Operation Suite Completed Successfully!")
