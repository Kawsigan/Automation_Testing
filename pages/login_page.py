from typing import List, Tuple
from selenium.webdriver.common.by import By
from config.config import Config
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("login_page")


class LoginPage(BasePage):
    """
    Page Object Model representing the Keepwisely CMMS Authentication page.
    All locators are strictly confirmed from the live rendered DOM.
    """

    # --- Confirmed Exact Locators from Live DOM Inspection ---
    EMAIL_INPUT: Tuple[str, str] = (By.ID, "email")
    PASSWORD_INPUT: Tuple[str, str] = (By.ID, "password-input")
    PASSWORD_TOGGLE_BTN: Tuple[str, str] = (By.ID, "password-addon")
    SIGN_IN_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[type='submit']")
    FORGOT_PASSWORD_LINK: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='forgot-password']")
    
    # Inline validation and alerts
    INVALID_FEEDBACK: Tuple[str, str] = (By.CSS_SELECTOR, ".invalid-feedback")
    TOAST_ALERT: Tuple[str, str] = (By.CSS_SELECTOR, ".toast-message, .alert-danger, .alert-warning")
    GLOBAL_LOADER: Tuple[str, str] = (By.ID, "global-loader")

    def __init__(self, driver):
        super().__init__(driver)

    def open(self) -> "LoginPage":
        """
        Navigates to the Keepwisely Application Base URL (which serves the Login page).
        """
        logger.info(f"Opening Login Page at: {Config.BASE_URL}")
        self.open_url(Config.BASE_URL)
        return self

    def enter_email(self, email: str) -> "LoginPage":
        """
        Enters email or username into the email input field.
        """
        self.type_text(self.EMAIL_INPUT, email)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        """
        Enters password into the password input field.
        """
        self.type_text(self.PASSWORD_INPUT, password)
        return self

    def toggle_password_visibility(self) -> "LoginPage":
        """
        Clicks the eye toggle button to switch between password and text view.
        """
        self.click(self.PASSWORD_TOGGLE_BTN)
        return self

    def get_password_input_type(self) -> str:
        """
        Returns the HTML 'type' attribute ('password' or 'text').
        """
        return self.get_attribute(self.PASSWORD_INPUT, "type")

    def click_sign_in(self) -> None:
        """
        Submits the form by clicking the Sign In button.
        """
        self.click(self.SIGN_IN_BUTTON)
        self.wait_for_angular_loader()

    def login(self, email: str, password: str) -> None:
        """
        Convenience workflow method performing the full login sequence.
        """
        logger.info(f"Submitting login form for: {email}")
        self.enter_email(email)
        self.enter_password(password)
        self.click_sign_in()

    def wait_for_login_redirect(self, timeout: int = 15) -> bool:
        """
        Explicitly waits for the Angular authentication request to finish
        and redirect the browser away from /auth/login.
        """
        from selenium.webdriver.support.ui import WebDriverWait
        logger.info("Waiting for login authentication and route change...")
        return WebDriverWait(self.driver, timeout).until(
            lambda d: "/auth/login" not in d.current_url.lower(),
            message="Login redirection timed out: still on /auth/login after credentials submission."
        )

    def is_email_input_displayed(self) -> bool:
        """
        Verifies visibility of the email input field.
        """
        return self.is_visible(self.EMAIL_INPUT)

    def is_password_input_displayed(self) -> bool:
        """
        Verifies visibility of the password input field.
        """
        return self.is_visible(self.PASSWORD_INPUT)

    def is_sign_in_button_enabled(self) -> bool:
        """
        Checks whether the Sign In button is currently enabled.
        """
        button = self.find_visible_element(self.SIGN_IN_BUTTON)
        return button.is_enabled()

    def get_validation_errors(self) -> List[str]:
        """
        Returns a list of visible inline form validation error messages (.invalid-feedback).
        """
        elements = self.find_all_elements(self.INVALID_FEEDBACK, timeout=3)
        return [el.text.strip() for el in elements if el.is_displayed() and el.text.strip()]

    def get_toast_alert_text(self) -> str:
        """
        Returns error text from toast notifications if present.
        """
        if self.is_visible(self.TOAST_ALERT, timeout=5):
            return self.get_text(self.TOAST_ALERT)
        return ""

    def get_forgot_password_href(self) -> str:
        """
        Retrieves the target URL from the Forgot Password link.
        """
        return self.get_attribute(self.FORGOT_PASSWORD_LINK, "href")

    def click_forgot_password(self, switch_to_new_tab: bool = True) -> None:
        """
        Clicks the 'Forgot Password?' link (which has target='_blank')
        and switches to the newly opened tab if requested.
        """
        original_window = self.driver.current_window_handle
        self.click(self.FORGOT_PASSWORD_LINK)
        
        if switch_to_new_tab:
            from selenium.webdriver.support.ui import WebDriverWait
            WebDriverWait(self.driver, 5).until(lambda d: len(d.window_handles) > 1)
            new_window = [w for w in self.driver.window_handles if w != original_window][-1]
            self.driver.switch_to.window(new_window)
            self.wait_for_angular_loader()
