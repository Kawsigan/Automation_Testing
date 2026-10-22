from typing import List, Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("reports_page")


class ReportsPage(BasePage):
    """
    Page Object Model representing Analytics and Reports modules:
    - Asset Maintenance Report (/reports/asset-maintenance-report)
    - PM SLA Report (/reports/pm-sla-report)
    - BOM Usage Report (/reports/bom-usage-report)
    - RCA & MTTR/MTBF Stability Reports (/reports/rca-report, /reports/repair-efficiency-report)
    """

    # --- Filter & Action Locators (Verified from live DOM) ---
    SEARCH_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input[placeholder*='Search'], input.form-control, input.box-shadow-effect")
    EXPORT_BUTTON: Tuple[str, str] = (By.XPATH, "//button[contains(., 'Export')] | //a[contains(., 'Export')] | //span[contains(text(), 'Export')]")
    FILTER_BUTTON: Tuple[str, str] = (By.XPATH, "//button[contains(., 'Filter')] | //a[contains(., 'Filter')] | //span[contains(text(), 'Filter')]")
    DATE_SELECT: Tuple[str, str] = (By.CSS_SELECTOR, "ng-select, .date-range, select, .custom-select")
    BREAKDOWN_TAB: Tuple[str, str] = (By.XPATH, "//button[contains(., 'Breakdown')] | //a[contains(., 'Breakdown')]")
    PM_TAB: Tuple[str, str] = (By.XPATH, "//button[contains(., 'Preventive Maintenance')] | //a[contains(., 'Preventive Maintenance')]")

    # Report Data Output Locators
    KPI_SUMMARY_CARDS: Tuple[str, str] = (By.CSS_SELECTOR, ".card .card-body, .metric-box, .kpi-widget")
    REPORT_TABLE_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")
    NO_DATA_ALERT: Tuple[str, str] = (By.CSS_SELECTOR, ".noresult, .empty-data, td[colspan]")

    def __init__(self, driver):
        super().__init__(driver)

    def is_report_page_displayed(self) -> bool:
        """
        Verifies presence of Report grid and toolbar controls.
        """
        return self.is_visible(self.SEARCH_INPUT, timeout=10) or self.is_visible(self.EXPORT_BUTTON, timeout=10)

    def filter_report(self, query: str) -> None:
        """
        Applies search filter to the report table.
        """
        logger.info(f"Filtering report with query: '{query}'")
        self.type_text(self.SEARCH_INPUT, query)
        self.wait_for_angular_loader()

    def export_excel(self) -> None:
        """
        Triggers Excel report download.
        """
        logger.info("Triggering Excel report download...")
        self.click(self.EXPORT_EXCEL_BUTTON)

    def get_report_rows_count(self) -> int:
        """
        Returns number of data records populated in the report grid.
        """
        return len(self.find_all_elements(self.REPORT_TABLE_ROWS, timeout=5))
