from typing import List, Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("amc_warranty_page")


class AMCWarrantyPage(BasePage):
    """
    Page Object Model representing AMC & Warranty Management:
    - AMC & Warranty Contracts (/amc-management/amc-warranty)
    - Service Packages (/amc-management/service-package)
    """

    # --- Locators ---
    SEARCH_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input[type='search'], input[placeholder*='Search']")
    ADD_AMC_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button.btn-primary, button[data-bs-target*='amc'], .add-btn")
    CONTRACT_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")
    EXPIRY_ALERT_BADGES: Tuple[str, str] = (By.CSS_SELECTOR, ".badge.bg-danger, .badge.bg-warning, .badge-soft-danger")

    # Contract Registration Form Fields
    MODAL_VENDOR_SELECT: Tuple[str, str] = (By.CSS_SELECTOR, "mat-select[formcontrolname='vendor_id'], select[formcontrolname='vendor_id']")
    MODAL_ASSET_SELECT: Tuple[str, str] = (By.CSS_SELECTOR, "mat-select[formcontrolname='asset_id'], select[formcontrolname='asset_id']")
    MODAL_START_DATE: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='start_date'], input[type='date']")
    MODAL_END_DATE: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='end_date']")
    MODAL_FREE_VISITS: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='visits'], input[formcontrolname='free_service_visits']")
    MODAL_SAVE_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[type='submit'], .modal-footer button.btn-primary")

    def __init__(self, driver):
        super().__init__(driver)

    def is_contract_table_displayed(self) -> bool:
        """
        Verifies visibility of the AMC/Warranty contracts table.
        """
        return self.is_visible(self.SEARCH_INPUT, timeout=10)

    def open_add_amc_modal(self) -> "AMCWarrantyPage":
        """
        Opens the Add AMC Contract modal.
        """
        logger.info("Opening Add AMC Contract modal...")
        self.click(self.ADD_AMC_BUTTON)
        self.wait_for_angular_loader()
        return self

    def get_contract_count(self) -> int:
        """
        Returns number of active/expired contracts in table.
        """
        return len(self.find_all_elements(self.CONTRACT_ROWS, timeout=5))
