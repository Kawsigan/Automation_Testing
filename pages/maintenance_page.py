from typing import List, Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("maintenance_page")


class MaintenancePage(BasePage):
    """
    Page Object Model representing Maintenance Management modules:
    - Breakdown Service Requests (/maintenance/service-request)
    - Preventive Maintenance Configuration (/maintenance/preventive-maintenance-configuration)
    """

    # --- Service Request Grid Locators (Verified from live DOM inspection) ---
    SEARCH_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input.box-shadow-effect, input[type='search'], input[placeholder*='Search'], input[placeholder*='search']")
    CREATE_REQUEST_BUTTON: Tuple[str, str] = (By.XPATH, "//button[contains(., 'Create Ticket')] | //button[contains(., 'Create Request')] | //button[contains(@class, 'btn-soft-primary')]")
    TICKET_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")
    STATUS_BADGES: Tuple[str, str] = (By.CSS_SELECTOR, ".badge, mat-chip")

    # Service Request Modal Fields
    MODAL_DESCRIPTION: Tuple[str, str] = (By.CSS_SELECTOR, "textarea[formcontrolname='description'], textarea[formcontrolname='problem_description'], textarea")
    MODAL_PRIORITY_SELECT: Tuple[str, str] = (By.CSS_SELECTOR, "mat-select[formcontrolname='priority'], select[formcontrolname='priority']")
    MODAL_SUBMIT_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[type='submit'], .modal-footer button.btn-primary")

    # --- Preventive Maintenance Configuration Locators ---
    NEW_PM_BUTTON: Tuple[str, str] = (By.XPATH, "//button[contains(., 'Add Configuration')] | //button[contains(., 'New')] | button.btn-primary")
    PM_SCHEDULE_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")

    def __init__(self, driver):
        super().__init__(driver)

    def is_service_requests_table_displayed(self) -> bool:
        """
        Verifies presence of the service requests grid.
        """
        return self.is_visible(self.SEARCH_INPUT, timeout=10)

    def open_create_request_modal(self) -> "MaintenancePage":
        """
        Clicks the 'Create Request' button to report a breakdown incident.
        """
        logger.info("Opening Create Service Request modal...")
        self.click(self.CREATE_REQUEST_BUTTON)
        self.wait_for_angular_loader()
        return self

    def get_tickets_count(self) -> int:
        """
        Returns number of breakdown tickets listed in table.
        """
        return len(self.find_all_elements(self.TICKET_ROWS, timeout=5))
