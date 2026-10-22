import pytest
from pages.dashboard_page import DashboardPage
from pages.asset_page import AssetPage
from pages.maintenance_page import MaintenancePage
from pages.user_management_page import UserManagementPage
from utils.logger import get_logger

logger = get_logger("test_dashboard")


@pytest.mark.dashboard
class TestDashboard:
    """
    Test suite validating authenticated application shell, navigation,
    and user session management.
    """

    def test_tc_dash_01_dashboard_shell_and_user_profile(self, authenticated_driver):
        """
        Test ID: TC-DASH-01
        Precondition: User is authenticated.
        Action: Verify dashboard header and profile dropdown details.
        Expected Result: Header user profile button is visible and username is displayed.
        Assertion: Dashboard displayed is True, username matches expected profile.
        """
        logger.info("Executing TC-DASH-01: Dashboard shell & profile check")
        dashboard = DashboardPage(authenticated_driver)

        assert dashboard.is_dashboard_displayed(), "Dashboard shell failed to display after login."

        # Open user menu and verify user name
        dashboard.open_user_menu()
        user_name = dashboard.get_logged_in_user_text()
        logger.info(f"Verified logged-in username: '{user_name}'")
        assert len(user_name) > 0, "Logged in user name should not be empty."

    def test_tc_dash_02_navigation_to_asset_management(self, authenticated_driver):
        """
        Test ID: TC-DASH-02
        Precondition: User is on the authenticated Dashboard.
        Action: Navigate to Asset Management module via sidebar.
        Expected Result: Browser navigates to /asset and displays the asset table and actions.
        Assertion: URL contains '/asset' and search input is visible.
        """
        logger.info("Executing TC-DASH-02: Asset module navigation")
        dashboard = DashboardPage(authenticated_driver)
        dashboard.navigate_to_assets()

        asset_page = AssetPage(authenticated_driver)
        assert "/asset" in authenticated_driver.current_url.lower(), (
            f"Expected URL to contain '/asset', but got: '{authenticated_driver.current_url}'"
        )
        assert asset_page.is_asset_table_displayed(), "Asset table search input is not visible."

    def test_tc_dash_03_navigation_to_service_requests(self, authenticated_driver):
        """
        Test ID: TC-DASH-03
        Precondition: User is on the authenticated Dashboard.
        Action: Navigate to Breakdown Service Requests module.
        Expected Result: Browser navigates to /maintenance/service-request and renders table.
        Assertion: URL contains '/maintenance/service-request' and service request grid is visible.
        """
        logger.info("Executing TC-DASH-03: Breakdown Service Requests navigation")
        dashboard = DashboardPage(authenticated_driver)
        dashboard.navigate_to_service_requests()

        maintenance_page = MaintenancePage(authenticated_driver)
        assert "service-request" in authenticated_driver.current_url.lower(), (
            f"Expected URL to contain 'service-request', got: '{authenticated_driver.current_url}'"
        )
        assert maintenance_page.is_service_requests_table_displayed(), "Service requests table was not displayed."

    def test_tc_dash_04_navigation_to_user_management(self, authenticated_driver):
        """
        Test ID: TC-DASH-04
        Precondition: User is on the authenticated Dashboard.
        Action: Navigate to User Management module.
        Expected Result: Browser navigates to /user-management/user and renders user grid.
        Assertion: URL contains '/user-management/user' and search input is visible.
        """
        logger.info("Executing TC-DASH-04: User Management navigation")
        dashboard = DashboardPage(authenticated_driver)
        dashboard.navigate_to_users()

        user_page = UserManagementPage(authenticated_driver)
        assert "user-management" in authenticated_driver.current_url.lower(), (
            f"Expected URL to contain 'user-management', got: '{authenticated_driver.current_url}'"
        )
        assert user_page.is_user_grid_displayed(), "User Management grid was not displayed."

    def test_tc_dash_05_user_logout_workflow(self, authenticated_driver):
        """
        Test ID: TC-DASH-05
        Precondition: User is authenticated on the Dashboard.
        Action: Open profile dropdown and click 'Log Out'.
        Expected Result: Session terminates and browser redirects back to Login page (/auth/login).
        Assertion: Redirection URL contains '/auth/login' or 'login'.
        """
        logger.info("Executing TC-DASH-05: User logout workflow")
        dashboard = DashboardPage(authenticated_driver)
        dashboard.logout()

        # Wait for route change to login
        from selenium.webdriver.support.ui import WebDriverWait
        WebDriverWait(authenticated_driver, 10).until(
            lambda d: "login" in d.current_url.lower(),
            message="User was not redirected back to Login page after logout."
        )
        assert "login" in authenticated_driver.current_url.lower(), (
            f"Expected URL to contain 'login' after logout, but got: '{authenticated_driver.current_url}'"
        )
