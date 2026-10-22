from typing import List, Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("asset_page")


class AssetPage(BasePage):
    """
    Page Object Model representing the Asset Management module (/asset).
    Provides methods for asset search, inventory grid inspection, and asset creation.
    """

    # --- Locators (Verified from live DOM inspection) ---
    SEARCH_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input.box-shadow-effect, input[type='search'], input[placeholder*='Search'], input[placeholder*='search']")
    ADD_ASSET_BUTTON: Tuple[str, str] = (By.XPATH, "//button[contains(., 'Add Asset')] | //button[contains(@class, 'btn-soft-primary')]")
    TABLE_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")
    TABLE_HEADERS: Tuple[str, str] = (By.CSS_SELECTOR, "table thead th, mat-header-cell")
    NO_RECORDS_MESSAGE: Tuple[str, str] = (By.CSS_SELECTOR, ".noresult, .text-center.no-data, td[colspan]")

    # Modal Form Fields [Angular formControlName patterns]
    MODAL_ASSET_NAME: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='asset_name'], #asset_name")
    MODAL_ASSET_TAG: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='asset_tag'], #asset_tag")
    MODAL_CATEGORY_SELECT: Tuple[str, str] = (By.CSS_SELECTOR, "mat-select[formcontrolname='category_id'], select[formcontrolname='category_id']")
    MODAL_SAVE_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[type='submit'], .modal-footer button.btn-primary")

    def __init__(self, driver):
        super().__init__(driver)

    def is_asset_table_displayed(self) -> bool:
        """
        Verifies that the Asset grid/table container is present.
        """
        return self.is_visible(self.SEARCH_INPUT, timeout=10)

    def search_asset(self, query: str) -> None:
        """
        Enters a search string into the asset search field.
        """
        logger.info(f"Filtering assets with query: '{query}'")
        self.type_text(self.SEARCH_INPUT, query)
        self.wait_for_angular_loader()

    def get_asset_count(self) -> int:
        """
        Returns the number of rows currently displayed in the asset table.
        """
        rows = self.find_all_elements(self.TABLE_ROWS, timeout=5)
        return len(rows)

    def open_add_asset_modal(self) -> "AssetPage":
        """
        Clicks the 'Add Asset' button to launch the registration modal.
        """
        self.click(self.ADD_ASSET_BUTTON)
        self.wait_for_angular_loader()
        return self
