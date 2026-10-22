from typing import List, Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("location_page")


class LocationPage(BasePage):
    """
    Page Object Model representing Location & Plant Hierarchy Management (/location).
    """

    # --- Locators (Verified from live DOM inspection) ---
    SEARCH_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input.box-shadow-effect, input[type='search'], input[placeholder*='Search'], input[placeholder*='search']")
    ADD_LOCATION_BUTTON: Tuple[str, str] = (By.XPATH, "//button[contains(., 'add')] | //button[contains(., 'Add')] | //button[contains(@class, 'btn-soft-primary')]")
    LOCATION_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row, .tree-node, .treeview")
    PARENT_LOCATION_DROPDOWN: Tuple[str, str] = (By.CSS_SELECTOR, "mat-select[formcontrolname='parent_id'], select[formcontrolname='parent_id']")

    # Modal Form Fields
    MODAL_LOCATION_NAME: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='location_name'], #location_name")
    MODAL_LOCATION_CODE: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='code'], #code")
    MODAL_SAVE_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[type='submit'], .modal-footer button.btn-primary")

    def __init__(self, driver):
        super().__init__(driver)

    def is_location_table_displayed(self) -> bool:
        """
        Verifies visibility of the Location hierarchy grid.
        """
        return self.is_visible(self.SEARCH_INPUT, timeout=10)

    def open_add_location_modal(self) -> "LocationPage":
        """
        Opens Add Location dialog.
        """
        logger.info("Opening Add Location modal...")
        self.click(self.ADD_LOCATION_BUTTON)
        self.wait_for_angular_loader()
        return self

    def get_location_count(self) -> int:
        """
        Returns number of locations registered.
        """
        return len(self.find_all_elements(self.LOCATION_ROWS, timeout=5))
