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

    # --- Filter & Action Locators ---
    DATE_RANGE_PICKER: Tuple[str, str] = (By.CSS_SELECTOR, "input[bsdaterangepicker], input.flatpickr-input, .date-range")
    GENERATE_REPORT_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button.btn-primary, button[type='submit']")
    EXPORT_EXCEL_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button.btn-success, button[title*='Excel'], .bx-file")
    EXPORT_CSV_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[title*='CSV'], .export-csv")
    EXPORT_PDF_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button.btn-danger, button[title*='PDF']")

    # Report Data Output Locators
    KPI_SUMMARY_CARDS: Tuple[str, str] = (By.CSS_SELECTOR, ".card .card-body, .metric-box, .kpi-widget")
    REPORT_TABLE_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")
    NO_DATA_ALERT: Tuple[str, str] = (By.CSS_SELECTOR, ".noresult, .empty-data, td[colspan]")

    def __init__(self, driver):
        super().__init__(driver)

    def is_report_page_displayed(self) -> bool:
        """
        Verifies presence of Report filter controls.
        """
        return self.is_visible(self.GENERATE_REPORT_BUTTON, timeout=10)

    def generate_report(self) -> None:
        """
        Clicks the button to run report aggregation.
        """
        logger.info("Generating report data...")
        self.click(self.GENERATE_REPORT_BUTTON)
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
