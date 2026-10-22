from typing import List, Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("five_s_audit_page")


class FiveSAuditPage(BasePage):
    """
    Page Object Model representing the 5S Audit Management module:
    - 5S Audits Execution (/five-s-audit/audits)
    - 5S Templates (/five-s-audit/templates)
    - 5S Non-Conformances (/five-s-audit/non-conformances)
    - 5S Schedules (/five-s-audit/schedules)
    - 5S Dashboard (/five-s-audit/dashboard)
    """

    # --- Locators ---
    SEARCH_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input[type='search'], input[placeholder*='Search']")
    START_AUDIT_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button.btn-primary, button[data-bs-target*='audit'], .add-btn")
    AUDIT_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")
    SCORE_CARDS: Tuple[str, str] = (By.CSS_SELECTOR, ".card-body .fs-4, .score-badge, .kpi-card")
    NON_CONFORMANCE_TAB: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='non-conformances'], .nav-link[data-bs-target*='nc']")
    NC_TABLE_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")

    # Audit Form Checkpoints (Sort, Set in order, Shine, Standardize, Sustain)
    SCORE_RADIO_BUTTONS: Tuple[str, str] = (By.CSS_SELECTOR, "input[type='radio'], mat-radio-button")
    AUDIT_NOTES_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "textarea[formcontrolname='notes'], textarea")
    SUBMIT_AUDIT_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[type='submit'], button.btn-success")

    def __init__(self, driver):
        super().__init__(driver)

    def is_audit_table_displayed(self) -> bool:
        """
        Verifies presence of 5S Audit data table.
        """
        return self.is_visible(self.SEARCH_INPUT, timeout=10)

    def open_start_audit_modal(self) -> "FiveSAuditPage":
        """
        Clicks the 'Start Audit' or 'New Audit' button.
        """
        logger.info("Opening 5S Audit creation dialog...")
        self.click(self.START_AUDIT_BUTTON)
        self.wait_for_angular_loader()
        return self

    def navigate_to_non_conformances(self) -> None:
        """
        Switches to the Non-Conformances view.
        """
        logger.info("Navigating to 5S Non-Conformances...")
        self.click(self.NON_CONFORMANCE_TAB)
        self.wait_for_angular_loader()

    def get_audits_count(self) -> int:
        """
        Returns count of audits in current view.
        """
        return len(self.find_all_elements(self.AUDIT_ROWS, timeout=5))
