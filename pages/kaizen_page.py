from typing import List, Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("kaizen_page")


class KaizenPage(BasePage):
    """
    Page Object Model representing the Kaizen Continuous Improvement module:
    - Kaizen Suggestions (/kaizen/suggestions)
    - Kaizen Dashboard (/kaizen/dashboard)
    - Kaizen Events (/kaizen/events)
    - Gemba Walks (/kaizen/gemba-walks)
    """

    # --- Locators ---
    SEARCH_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input[type='search'], input[placeholder*='Search']")
    NEW_SUGGESTION_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button.btn-primary, button[data-bs-target*='kaizen'], .add-btn")
    SUGGESTION_ROWS: Tuple[str, str] = (By.CSS_SELECTOR, "table tbody tr, mat-row")
    STATUS_BADGES: Tuple[str, str] = (By.CSS_SELECTOR, ".badge, mat-chip")
    KAIZEN_TABS: Tuple[str, str] = (By.CSS_SELECTOR, ".nav-tabs .nav-link, mat-tab-header")

    # Suggestion Modal Form Fields [Confirmed Angular formControlName patterns]
    MODAL_TITLE: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='title'], #title")
    MODAL_CATEGORY_SELECT: Tuple[str, str] = (By.CSS_SELECTOR, "mat-select[formcontrolname='category_id'], select[formcontrolname='category']")
    MODAL_PROBLEM_STATEMENT: Tuple[str, str] = (By.CSS_SELECTOR, "textarea[formcontrolname='problem_statement'], textarea[formcontrolname='before_state'], textarea")
    MODAL_PROPOSED_IMPROVEMENT: Tuple[str, str] = (By.CSS_SELECTOR, "textarea[formcontrolname='proposed_improvement'], textarea[formcontrolname='after_state']")
    MODAL_SAVE_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[type='submit'], .modal-footer button.btn-primary")

    def __init__(self, driver):
        super().__init__(driver)

    def is_kaizen_grid_displayed(self) -> bool:
        """
        Verifies presence of the Kaizen suggestions grid.
        """
        return self.is_visible(self.SEARCH_INPUT, timeout=10)

    def open_new_suggestion_modal(self) -> "KaizenPage":
        """
        Clicks the 'New Suggestion' button.
        """
        logger.info("Opening Kaizen New Suggestion modal...")
        self.click(self.NEW_SUGGESTION_BUTTON)
        self.wait_for_angular_loader()
        return self

    def fill_suggestion(self, title: str, problem: str, improvement: str) -> "KaizenPage":
        """
        Fills the Kaizen suggestion modal fields.
        """
        logger.info(f"Filling Kaizen suggestion: '{title}'")
        self.type_text(self.MODAL_TITLE, title)
        self.type_text(self.MODAL_PROBLEM_STATEMENT, problem)
        self.type_text(self.MODAL_PROPOSED_IMPROVEMENT, improvement)
        return self

    def submit_suggestion(self) -> None:
        """
        Submits the Kaizen suggestion.
        """
        self.click(self.MODAL_SAVE_BUTTON)
        self.wait_for_angular_loader()

    def get_suggestions_count(self) -> int:
        """
        Returns the number of suggestion rows listed in table.
        """
        return len(self.find_all_elements(self.SUGGESTION_ROWS, timeout=5))
