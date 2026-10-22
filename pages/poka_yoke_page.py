from typing import List, Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("poka_yoke_page")


class PokaYokePage(BasePage):
    """
    Page Object Model representing the Poka-Yoke (Mistake-Proofing) module (/poka-yoke).
    """

    # --- Locators ---
    SEARCH_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input[type='search'], input[placeholder*='Search']")
    ADD_POKA_YOKE_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button.btn-primary, button[data-bs-target*='poka'], .add-btn")
    POKA_YOKE_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")
    MECHANISM_TYPE_FILTER: Tuple[str, str] = (By.CSS_SELECTOR, "mat-select[formcontrolname='mechanism_type'], select.filter-select")

    # Form Fields
    MODAL_NAME_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='name'], #name")
    MODAL_ASSET_SELECT: Tuple[str, str] = (By.CSS_SELECTOR, "mat-select[formcontrolname='asset_id'], select[formcontrolname='asset_id']")
    MODAL_METHOD_SELECT: Tuple[str, str] = (By.CSS_SELECTOR, "mat-select[formcontrolname='method'], select[formcontrolname='method']")
    MODAL_SAVE_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[type='submit'], .modal-footer button.btn-primary")

    def __init__(self, driver):
        super().__init__(driver)

    def is_poka_yoke_table_displayed(self) -> bool:
        """
        Verifies visibility of the Poka-Yoke register table.
        """
        return self.is_visible(self.SEARCH_INPUT, timeout=10)

    def open_add_poka_yoke_modal(self) -> "PokaYokePage":
        """
        Opens registration modal.
        """
        logger.info("Opening Add Poka-Yoke modal...")
        self.click(self.ADD_POKA_YOKE_BUTTON)
        self.wait_for_angular_loader()
        return self

    def get_poka_yoke_count(self) -> int:
        """
        Returns number of Poka-Yoke mechanisms registered.
        """
        return len(self.find_all_elements(self.POKA_YOKE_ROWS, timeout=5))
