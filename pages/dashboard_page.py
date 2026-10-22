from typing import Tuple
from selenium.webdriver.common.by import By
from config.config import Config
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("dashboard_page")


class DashboardPage(BasePage):
    """
    Page Object Model representing the authenticated application shell,
    sidebar navigation, and user session management.
    """

    # --- Header & User Session Locators (Verified from live DOM inspection) ---
    USER_PROFILE_BUTTON: Tuple[str, str] = (By.ID, "page-header-user-dropdown")
    USER_PROFILE_AVATAR: Tuple[str, str] = (By.CSS_SELECTOR, "#page-header-user-dropdown img.header-profile-user")
    USER_DROPDOWN_MENU: Tuple[str, str] = (By.CSS_SELECTOR, ".user-dropdown-header, .dropdown-menu.show")
    USER_NAME_LABEL: Tuple[str, str] = (By.CSS_SELECTOR, ".user-name")
    LOGOUT_LINK: Tuple[str, str] = (By.CSS_SELECTOR, ".dropdown-item.logout-item, a.logout-item")

    # --- Sidebar Parent Accordion Locators (Verified from live DOM inspection) ---
    PARENT_MAINTENANCE: Tuple[str, str] = (By.XPATH, "//li[contains(@class, 'nav-item')][.//span[contains(text(), 'Maintenance')]]/a")
    PARENT_ASSETS: Tuple[str, str] = (By.XPATH, "//li[contains(@class, 'nav-item')][.//span[contains(text(), 'Asset Management')]]/a")
    PARENT_LOCATIONS: Tuple[str, str] = (By.XPATH, "//li[contains(@class, 'nav-item')][.//span[contains(text(), 'Location')]]/a")
    PARENT_PROCUREMENT: Tuple[str, str] = (By.XPATH, "//li[contains(@class, 'nav-item')][.//span[contains(text(), 'Procurement')]]/a")
    PARENT_USERS: Tuple[str, str] = (By.XPATH, "//li[contains(@class, 'nav-item')][.//span[contains(text(), 'User')]]/a")
    PARENT_SETTINGS: Tuple[str, str] = (By.XPATH, "//li[contains(@class, 'nav-item')][.//span[contains(text(), 'Settings')]]/a")

    # --- Sidebar Child Navigation Links (Verified from Angular Routing chunks) ---
    NAV_ASSETS: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='/asset']")
    NAV_USERS: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='user-management/user']")
    NAV_SERVICE_REQUESTS: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='/maintenance/service-request']")
    NAV_PREVENTIVE_MAINTENANCE: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='/maintenance/preventive-maintenance-configuration']")
    NAV_PURCHASE_ORDERS: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='/purchase-order']")
    NAV_REQUEST_BOM: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='/request-bom']")
    NAV_SETTINGS_PREFIX: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='/settings/prefix']")
    NAV_KAIZEN: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='/kaizen/suggestions']")
    NAV_FIVE_S_AUDIT: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='/five-s-audit/audits']")
    NAV_POKA_YOKE: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='/poka-yoke']")
    NAV_AMC_WARRANTY: Tuple[str, str] = (By.CSS_SELECTOR, "a[href*='/amc-management/amc-warranty']")

    def __init__(self, driver):
        super().__init__(driver)

    def is_dashboard_displayed(self) -> bool:
        """
        Verifies if the user is authenticated and the header profile button is visible.
        """
        return self.is_visible(self.USER_PROFILE_BUTTON, timeout=10)

    def get_logged_in_user_text(self) -> str:
        """
        Returns the displayed username inside the user menu dropdown.
        """
        if self.is_visible(self.USER_NAME_LABEL, timeout=3):
            return self.get_text(self.USER_NAME_LABEL)
        return ""

    def is_user_menu_open(self) -> bool:
        """Checks if the user profile dropdown is currently open."""
        try:
            btn = self.find_element(self.USER_PROFILE_BUTTON, timeout=2)
            return btn.get_attribute("aria-expanded") == "true" or self.is_visible(self.USER_DROPDOWN_MENU, timeout=1)
        except Exception:
            return False

    def open_user_menu(self) -> "DashboardPage":
        """
        Clicks the user profile button to open the user menu dropdown if not already open.
        Waits for transient toasts to clear first to prevent click interception.
        """
        if not self.is_user_menu_open():
            self.wait_for_toasts_to_clear(timeout=4)
            self.click(self.USER_PROFILE_BUTTON)
            self.find_visible_element(self.USER_DROPDOWN_MENU, timeout=5)
        return self

    def logout(self) -> None:
        """
        Executes user logout from the profile dropdown.
        """
        logger.info("Executing logout...")
        self.open_user_menu()
        self.click(self.LOGOUT_LINK)
        self.wait_for_angular_loader()

    # --- Navigation Helpers with SPA Route Synchronization ---

    def navigate_to_route(self, route_part: str) -> None:
        """
        Navigates to an authenticated application route within the Angular SPA.
        Triggers router link activation with direct fallback, explicitly waiting
        for the route change to complete and Angular loaders to dismiss.
        """
        logger.info(f"Navigating to route: '{route_part}'")
        from selenium.webdriver.support.ui import WebDriverWait
        
        # 1. Attempt router link click via JS
        self.driver.execute_script(f"""
            let a = document.querySelector("a[href*='{route_part}']");
            if (a) a.click();
        """)

        # 2. Verify route transition; if not triggered within 3s, navigate directly
        try:
            WebDriverWait(self.driver, 3).until(lambda d: route_part in d.current_url.lower())
        except Exception:
            full_url = f"{Config.BASE_URL.rstrip('/')}/{route_part.lstrip('/')}"
            self.driver.get(full_url)

        # 3. Synchronize: Wait for URL and Angular loaders
        WebDriverWait(self.driver, 10).until(
            lambda d: route_part in d.current_url.lower(),
            message=f"Timed out waiting for route transition to '{route_part}'. Current URL: '{self.driver.current_url}'"
        )
        self.wait_for_angular_loader()

    def navigate_to_dashboard(self) -> None:
        """Navigates to the main Dashboard view."""
        self.navigate_to_route("dashboard")

    def navigate_to_assets(self) -> None:
        """Navigates to Asset Management (/asset)."""
        self.navigate_to_route("asset")

    def navigate_to_users(self) -> None:
        """Navigates to User Management (user-management/user)."""
        self.navigate_to_route("user-management/user")

    def navigate_to_service_requests(self) -> None:
        """Navigates to Breakdown Service Requests (/maintenance/service-request)."""
        self.navigate_to_route("maintenance/service-request")

    def navigate_to_preventive_maintenance(self) -> None:
        """Navigates to Preventive Maintenance Configuration."""
        self.navigate_to_route("maintenance/preventive-maintenance-configuration")

    def navigate_to_purchase_orders(self) -> None:
        """Navigates to Purchase Orders (/purchase-order)."""
        self.navigate_to_route("purchase-order")

    def navigate_to_request_bom(self) -> None:
        """Navigates to Request BOM (/request-bom)."""
        self.navigate_to_route("request-bom")

    def navigate_to_kaizen(self) -> None:
        """Navigates to Kaizen Suggestions (/kaizen/suggestions)."""
        self.navigate_to_route("kaizen/suggestions")

    def navigate_to_five_s_audit(self) -> None:
        """Navigates to 5S Workplace Audits (/five-s-audit/audits)."""
        self.navigate_to_route("five-s-audit/audits")

    def navigate_to_poka_yoke(self) -> None:
        """Navigates to Poka-Yoke error proofing (/poka-yoke)."""
        self.navigate_to_route("poka-yoke")

    def navigate_to_amc_warranty(self) -> None:
        """Navigates to AMC & Warranty contracts (/amc-management/amc-warranty)."""
        self.navigate_to_route("amc-management/amc-warranty")

    def navigate_to_settings_prefix(self) -> None:
        """Navigates to System Prefix Settings (/settings/prefix)."""
        self.navigate_to_route("settings/prefix")

    def navigate_to_location(self) -> None:
        """Navigates to Location & Plant Hierarchy (/location)."""
        self.navigate_to_route("location")

    def navigate_to_floor_plan(self) -> None:
        """Navigates to Floor Plan & Live Monitor (/floor-plan)."""
        self.navigate_to_route("floor-plan")

    def navigate_to_masters_checklist(self) -> None:
        """Navigates to Master Checklists (/masters/checklist)."""
        self.navigate_to_route("masters/checklist")

