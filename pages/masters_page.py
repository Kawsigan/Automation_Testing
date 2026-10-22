from typing import List, Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("masters_page")


class MastersPage(BasePage):
    """
    Page Object Model representing Master Data Management:
    - Checklists (/masters/checklist)
    - Maintenance Masters (/masters/maintenance-master)
    - Asset Categories (/masters/asset-category)
    - Suppliers (/masters/supplier)
    - Task Types (/masters/task-type)
    """

    # --- Locators ---
    SEARCH_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input[type='search'], input[placeholder*='Search']")
    ADD_MASTER_ITEM_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button.btn-primary, button[data-bs-target*='master'], .add-btn")
    MASTER_TABLE_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")
    
    # Checklist Items
    CHECKLIST_TASK_NAME: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='task_name'], #task_name")
    CHECKLIST_TYPE_SELECT: Tuple[str, str] = (By.CSS_SELECTOR, "mat-select[formcontrolname='task_type'], select[formcontrolname='task_type']")
    SAVE_MASTER_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[type='submit'], .modal-footer button.btn-primary")

    def __init__(self, driver):
        super().__init__(driver)

    def is_masters_grid_displayed(self) -> bool:
        """
        Verifies visibility of Master Data table.
        """
        return self.is_visible(self.SEARCH_INPUT, timeout=10)

    def open_add_master_modal(self) -> "MastersPage":
        """
        Clicks 'Add' button for the current master entity.
        """
        logger.info("Opening Add Master Item modal...")
        self.click(self.ADD_MASTER_ITEM_BUTTON)
        self.wait_for_angular_loader()
        return self

    def get_items_count(self) -> int:
        """
        Returns count of rows in active master table.
        """
        return len(self.find_all_elements(self.MASTER_TABLE_ROWS, timeout=5))
