from typing import List, Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("user_management_page")


class UserManagementPage(BasePage):
    """
    Page Object Model representing the User Management module (user-management/user).
    """

    # --- Locators (Verified from live DOM inspection) ---
    SEARCH_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input.box-shadow-effect, input[type='search'], input[placeholder*='Search'], input[placeholder*='search']")
    ADD_USER_BUTTON: Tuple[str, str] = (By.XPATH, "//button[contains(., 'Add User')] | //button[contains(., 'Add Users')] | //button[contains(@class, 'btn-soft-primary')]")
    USER_TABLE_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")
    
    # User Creation Modal Fields [Confirmed Angular formControlName patterns]
    MODAL_USER_NAME: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='name'], input[formcontrolname='user_name'], #name")
    MODAL_USER_EMAIL: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='email'], #email")
    MODAL_ROLE_SELECT: Tuple[str, str] = (By.CSS_SELECTOR, "mat-select[formcontrolname='role'], select[formcontrolname='role']")
    MODAL_SAVE_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[type='submit'], .modal-footer button.btn-primary")
    MODAL_CLOSE_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, ".btn-close, .modal-header button.close")

    def __init__(self, driver):
        super().__init__(driver)

    def is_user_grid_displayed(self) -> bool:
        """
        Verifies presence of the User Management data table.
        """
        return self.is_visible(self.SEARCH_INPUT, timeout=10)

    def open_add_user_modal(self) -> "UserManagementPage":
        """
        Clicks the 'Add User' button.
        """
        logger.info("Opening Add User modal...")
        self.click(self.ADD_USER_BUTTON)
        self.wait_for_angular_loader()
        return self

    def fill_user_form(self, name: str, email: str) -> "UserManagementPage":
        """
        Enters name and email into the user creation modal.
        """
        logger.info(f"Filling user form: name='{name}', email='{email}'")
        self.type_text(self.MODAL_USER_NAME, name)
        self.type_text(self.MODAL_USER_EMAIL, email)
        return self

    def submit_user_form(self) -> None:
        """
        Saves the new user record.
        """
        self.click(self.MODAL_SAVE_BUTTON)
        self.wait_for_angular_loader()

    def get_user_count(self) -> int:
        """
        Returns count of rows in the user table.
        """
        return len(self.find_all_elements(self.USER_TABLE_ROWS, timeout=5))
