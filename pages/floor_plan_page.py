from typing import List, Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("floor_plan_page")


class FloorPlanPage(BasePage):
    """
    Page Object Model representing the Visual Floor Plan & Live Monitor:
    - 2D Blueprint Layout (/floor-plan)
    - Live Real-time Asset Monitor (/floor-plan/live-monitor)
    """

    # --- Locators ---
    FLOOR_PLAN_CANVAS: Tuple[str, str] = (By.CSS_SELECTOR, "table, .table, canvas, .floor-plan-container, svg.floor-plan-map")
    ADD_FLOOR_PLAN_BUTTON: Tuple[str, str] = (By.XPATH, "//*[contains(text(), 'Add Floor Plan')]")
    LIVE_MONITOR_TAB: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='live-monitor'], .nav-link[data-bs-target*='monitor']")
    ASSET_PINS: Tuple[str, str] = (By.CSS_SELECTOR, ".asset-marker, .map-pin, .marker-pin")
    ACTIVE_ALERT_PINS: Tuple[str, str] = (By.CSS_SELECTOR, ".marker-pin.breakdown, .marker-pin.alert, .pin-danger")
    ZOOM_IN_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[title*='Zoom In'], .btn-zoom-in")
    ZOOM_OUT_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[title*='Zoom Out'], .btn-zoom-out")
    SAVE_LAYOUT_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button.btn-primary, button.save-layout")

    def __init__(self, driver):
        super().__init__(driver)

    def is_floor_plan_displayed(self) -> bool:
        """
        Verifies visibility of the interactive floor plan map or floor plan register table.
        """
        return self.is_visible(self.FLOOR_PLAN_CANVAS, timeout=10) or self.is_visible(self.ADD_FLOOR_PLAN_BUTTON, timeout=5)

    def switch_to_live_monitor(self) -> None:
        """
        Switches view to the live machine status monitor.
        """
        logger.info("Switching to Floor Plan Live Monitor...")
        self.click(self.LIVE_MONITOR_TAB)
        self.wait_for_angular_loader()

    def get_placed_assets_count(self) -> int:
        """
        Returns count of asset markers plotted on the layout.
        """
        return len(self.find_all_elements(self.ASSET_PINS, timeout=5))
