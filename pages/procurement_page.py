from typing import List, Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("procurement_page")


class ProcurementPage(BasePage):
    """
    Page Object Model representing Procurement Management:
    - Purchase Orders (/purchase-order)
    - Request BOM (/request-bom)
    """

    # --- Purchase Order Locators ---
    PO_SEARCH_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input[type='search'], input[placeholder*='Search']")
    CREATE_PO_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button.btn-primary, button[data-bs-target*='po'], .add-btn")
    PO_TABLE_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")

    # --- BOM Request Locators ---
    REQUEST_BOM_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button.btn-primary, button[data-bs-target*='bom'], .add-btn")
    BOM_TABLE_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")

    def __init__(self, driver):
        super().__init__(driver)

    def is_po_table_displayed(self) -> bool:
        """
        Verifies visibility of Purchase Order grid.
        """
        return self.is_visible(self.PO_SEARCH_INPUT, timeout=10)

    def open_create_po_modal(self) -> "ProcurementPage":
        """
        Clicks Create PO button.
        """
        logger.info("Opening Create PO modal...")
        self.click(self.CREATE_PO_BUTTON)
        self.wait_for_angular_loader()
        return self

    def get_po_count(self) -> int:
        """
        Returns count of PO records in table.
        """
        return len(self.find_all_elements(self.PO_TABLE_ROWS, timeout=5))
