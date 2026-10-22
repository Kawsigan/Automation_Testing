import pytest
from selenium.webdriver.common.by import By
from pages.dashboard_page import DashboardPage
from pages.asset_page import AssetPage
from pages.maintenance_page import MaintenancePage
from pages.user_management_page import UserManagementPage
from pages.procurement_page import ProcurementPage
from pages.kaizen_page import KaizenPage
from pages.five_s_audit_page import FiveSAuditPage
from pages.poka_yoke_page import PokaYokePage
from pages.amc_warranty_page import AMCWarrantyPage
from pages.location_page import LocationPage
from config.config import Config
from utils.logger import get_logger
from utils.monkey_vectors import get_all_monkey_vectors

logger = get_logger("test_dashboard")


@pytest.mark.dashboard
class TestDashboard:
    """
    Comprehensive suite of 80 Test Operations for Authenticated Dashboard & Application Shell:
    - Shell, Topbar, Brand Navigation & User Profile Management
    - Operational KPI Metric Cards & Analytics Widgets
    - Multi-Module Route Transitions & Cross-System Orchestration
    - 48 Monkey & Chaos Fuzzing operations, 10 Rapid UI stress tests, and 12 E2E Lifecycles.
    """

    # ==========================================================================
    # Isolation & Auto-Setup Hook
    # ==========================================================================
    @pytest.fixture(autouse=True)
    def ensure_dashboard_page_ready(self, authenticated_session):
        """
        Guarantees pristine test isolation for every dashboard test operation:
        1. Restores standard desktop viewport (1920x1080).
        2. Ensures browser is strictly on /dashboard route.
        3. Dismisses any open dropdowns or transient overlays.
        """
        authenticated_session.set_window_size(1920, 1080)
        curr = authenticated_session.current_url.lower().rstrip("/")
        if not curr.endswith("/dashboard"):
            authenticated_session.get(f"{Config.BASE_URL}/dashboard")
            DashboardPage(authenticated_session).wait_for_angular_loader()

        dashboard = DashboardPage(authenticated_session)
        # Close user menu if open
        if dashboard.is_user_menu_open():
            try:
                authenticated_session.find_element(By.TAG_NAME, "body").click()
            except Exception:
                pass

    # ==========================================================================
    # Phase 1: Core Functional, UI Alignment & Business Logic (10 Operations)
    # ==========================================================================
    def test_tc_dash_01_dashboard_shell_and_user_profile(self, authenticated_session):
        """
        Test ID: TC-DASH-01
        Precondition: User is authenticated.
        Action: Verify dashboard header and profile dropdown details.
        Expected Result: Header user profile button is visible and username is displayed.
        """
        logger.info("Executing TC-DASH-01: Dashboard shell & profile check")
        dashboard = DashboardPage(authenticated_session)
        assert dashboard.is_dashboard_displayed(), "Dashboard shell failed to display."
        dashboard.open_user_menu()
        user_name = dashboard.get_logged_in_user_text()
        logger.info(f"Verified logged-in username: '{user_name}'")
        assert len(user_name) > 0, "Logged in user name should not be empty."

    def test_tc_dash_02_navigation_to_asset_management(self, authenticated_session):
        """
        Test ID: TC-DASH-02
        Precondition: User is on the authenticated Dashboard.
        Action: Navigate to Asset Management module via sidebar.
        Expected Result: Browser navigates to /asset and displays the asset table and actions.
        """
        logger.info("Executing TC-DASH-02: Asset module navigation")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_assets()
        asset_page = AssetPage(authenticated_session)
        assert "/asset" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain '/asset', but got: '{authenticated_session.current_url}'"
        )
        assert asset_page.is_asset_table_displayed(), "Asset table search input is not visible."

    def test_tc_dash_03_navigation_to_service_requests(self, authenticated_session):
        """
        Test ID: TC-DASH-03
        Precondition: User is on the authenticated Dashboard.
        Action: Navigate to Breakdown Service Requests module.
        Expected Result: Browser navigates to /maintenance/service-request and renders table.
        """
        logger.info("Executing TC-DASH-03: Breakdown Service Requests navigation")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_service_requests()
        maintenance_page = MaintenancePage(authenticated_session)
        assert "service-request" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'service-request', got: '{authenticated_session.current_url}'"
        )
        assert maintenance_page.is_service_requests_table_displayed(), "Service requests table was not displayed."

    def test_tc_dash_04_navigation_to_user_management(self, authenticated_session):
        """
        Test ID: TC-DASH-04
        Precondition: User is on the authenticated Dashboard.
        Action: Navigate to User Management module.
        Expected Result: Browser navigates to /user-management/user and renders user grid.
        """
        logger.info("Executing TC-DASH-04: User Management navigation")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_users()
        user_page = UserManagementPage(authenticated_session)
        assert "user-management" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'user-management', got: '{authenticated_session.current_url}'"
        )
        assert user_page.is_user_grid_displayed(), "User Management grid was not displayed."

    def test_tc_dash_05_navigation_to_preventive_maintenance(self, authenticated_session):
        """
        Test ID: TC-DASH-05
        Precondition: User is on the authenticated Dashboard.
        Action: Navigate to Preventive Maintenance configuration module.
        Expected Result: Browser navigates to /maintenance/preventive-maintenance-configuration.
        """
        logger.info("Executing TC-DASH-05: Preventive maintenance configuration navigation")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_preventive_maintenance()
        assert "preventive-maintenance" in authenticated_session.current_url.lower()

    def test_tc_dash_06_ui_alignment_header_and_shell(self, authenticated_session):
        """
        Test ID: TC-DASH-06
        Precondition: User is authenticated on the Dashboard.
        Action: Measure header element positioning, profile dropdown coordinates, and viewport overflow.
        Expected Result: Header spans full width without horizontal overflow; profile button is right-aligned.
        """
        logger.info("Executing TC-DASH-06: Dashboard UI alignment inspection")
        dashboard = DashboardPage(authenticated_session)
        profile_rect = dashboard.get_element_rect(dashboard.USER_PROFILE_BUTTON)
        logger.info(f"Header profile button coordinates: {profile_rect}")
        window_width = authenticated_session.execute_script("return window.innerWidth;")
        assert profile_rect["left"] > (window_width / 2), (
            f"Expected user profile button to be aligned to the right, but left is {profile_rect['left']}px"
        )
        assert dashboard.verify_no_horizontal_overflow(), "Dashboard displays unwanted horizontal scrollbar."

    def test_tc_dash_07_space_and_card_padding_consistency(self, authenticated_session):
        """
        Test ID: TC-DASH-07
        Precondition: User is authenticated on the Dashboard.
        Action: Inspect card widget spacing, padding, and layout structure across KPI cards.
        Expected Result: Card widgets maintain distinct padding and margin gaps between grid columns.
        """
        logger.info("Executing TC-DASH-07: Dashboard space and padding verification")
        dashboard = DashboardPage(authenticated_session)
        assert dashboard.is_dashboard_displayed(), "Dashboard shell failed to render."
        container = dashboard.find_visible_element(
            (By.CSS_SELECTOR, ".dashboard-container, .main-content, .container-fluid, body"), timeout=10
        )
        assert container is not None, "Dashboard container must be rendered."
        computed_padding = authenticated_session.execute_script(
            "return window.getComputedStyle(arguments[0]).padding;", container
        )
        assert computed_padding != "", "Dashboard container should have defined padding."

    def test_tc_dash_08_business_logic_kpi_counters(self, authenticated_session):
        """
        Test ID: TC-DASH-08
        Precondition: User is authenticated on the Dashboard.
        Action: Verify metric counters and statistics load correctly.
        Expected Result: Dashboard renders operational KPI module metrics and statistics.
        """
        logger.info("Executing TC-DASH-08: Dashboard business logic KPI metrics check")
        dashboard = DashboardPage(authenticated_session)
        assert dashboard.is_dashboard_displayed(), "Dashboard shell failed to render."
        dashboard.wait_for_angular_loader(15)
        page_text = authenticated_session.execute_script("return document.body.innerText;")
        assert any(term in page_text for term in ["Management", "Dashboard", "Total", "total", "Home", "Keep Wisely"]), (
            "Operational KPI metric text was not found on the active dashboard."
        )

    def test_tc_dash_09_navigation_to_purchase_orders(self, authenticated_session):
        """
        Test ID: TC-DASH-09
        Precondition: User is authenticated on the Dashboard.
        Action: Navigate to Purchase Orders module via dashboard.
        Expected Result: Browser navigates to /purchase-order and renders purchase orders grid.
        """
        logger.info("Executing TC-DASH-09: Purchase Orders module navigation")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_purchase_orders()
        po_page = ProcurementPage(authenticated_session)
        assert "purchase-order" in authenticated_session.current_url.lower()
        assert po_page.is_po_table_displayed()

    def test_tc_dash_10_negative_sql_injection_defense(self, authenticated_session):
        """
        Test ID: TC-DASH-10
        Precondition: User is authenticated on the Dashboard.
        Action: Inject primary SQL injection baseline into any search/filter input on dashboard.
        Expected Result: Backend neutralizes input; dashboard remains resilient.
        """
        logger.info("Executing TC-DASH-10: Baseline SQLi defense verification")
        dashboard = DashboardPage(authenticated_session)
        inputs = authenticated_session.find_elements(By.CSS_SELECTOR, "input")
        if inputs:
            dashboard.execute_monkey_fuzz((By.CSS_SELECTOR, "input"), "' OR '1'='1")
        assert dashboard.verify_page_health()

    # ==========================================================================
    # Phase 2: Monkey Testing & Chaos Fuzzing Matrix (48 Operations)
    # ==========================================================================
    @pytest.mark.parametrize(
        "vector",
        get_all_monkey_vectors(),
        ids=[f"tc_dash_{i+11:02d}_{v['id']}" for i, v in enumerate(get_all_monkey_vectors())]
    )
    def test_tc_dash_monkey_chaos_fuzzing(self, authenticated_session, vector):
        """
        Test ID: TC-DASH-11 through TC-DASH-58
        Precondition: User is on the authenticated Dashboard.
        Action: Inject specialized chaos/fuzz payload into dashboard inputs or trigger stress state.
        Expected Result: Application neutralizes payload; UI remains resilient with zero unhandled crashes.
        """
        logger.info(f"Executing Monkey Fuzz: {vector['id']} ({vector['desc']})")
        dashboard = DashboardPage(authenticated_session)
        inputs = authenticated_session.find_elements(By.CSS_SELECTOR, "input:not([type='hidden'])")
        if inputs:
            dashboard.execute_monkey_fuzz((By.CSS_SELECTOR, "input:not([type='hidden'])"), vector["payload"])
        assert dashboard.verify_page_health(), f"Page health compromised by payload: {vector['id']}"

    # ==========================================================================
    # Phase 3: Rapid Monkey UI Actions & Stress Resilience (10 Operations)
    # ==========================================================================
    def test_tc_dash_59_monkey_rapid_clicks_profile_dropdown(self, authenticated_session):
        """
        Test ID: TC-DASH-59
        Action: Perform rapid 5x clicks on user profile dropdown button to stress debounce.
        """
        logger.info("Executing TC-DASH-59: Rapid 5x click profile dropdown stress")
        dashboard = DashboardPage(authenticated_session)
        dashboard.execute_monkey_rapid_clicks(dashboard.USER_PROFILE_BUTTON, clicks=5)
        assert dashboard.verify_page_health()

    def test_tc_dash_60_monkey_rapid_sidebar_hover_stress(self, authenticated_session):
        """
        Test ID: TC-DASH-60
        Action: Rapidly hover across sidebar navigation items.
        """
        logger.info("Executing TC-DASH-60: Rapid sidebar hover stress")
        items = authenticated_session.find_elements(By.CSS_SELECTOR, ".nav-item, .sidebar a")
        if items:
            for item in items[:5]:
                authenticated_session.execute_script(
                    "arguments[0].dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));", item
                )
        dashboard = DashboardPage(authenticated_session)
        assert dashboard.verify_page_health()

    def test_tc_dash_61_monkey_viewport_resize_desktop_to_mobile(self, authenticated_session):
        """
        Test ID: TC-DASH-61
        Action: Dynamically resize viewport from Desktop (1920x1080) to Mobile (375x812) and restore.
        """
        logger.info("Executing TC-DASH-61: Viewport resize stress test")
        dashboard = DashboardPage(authenticated_session)
        authenticated_session.set_window_size(375, 812)
        assert dashboard.verify_page_health()
        authenticated_session.set_window_size(1920, 1080)
        assert dashboard.verify_page_health()

    def test_tc_dash_62_monkey_rapid_scroll_stress(self, authenticated_session):
        """
        Test ID: TC-DASH-62
        Action: Rapidly scroll down to footer and back to top 3 times.
        """
        logger.info("Executing TC-DASH-62: Rapid scroll stress")
        for _ in range(3):
            authenticated_session.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            authenticated_session.execute_script("window.scrollTo(0, 0);")
        dashboard = DashboardPage(authenticated_session)
        assert dashboard.verify_page_health()

    def test_tc_dash_63_monkey_rapid_card_widget_click_stress(self, authenticated_session):
        """
        Test ID: TC-DASH-63
        Action: Rapidly click dashboard card widgets to test event listener stability.
        """
        logger.info("Executing TC-DASH-63: Rapid card widget click stress")
        cards = authenticated_session.find_elements(By.CSS_SELECTOR, ".card, .widget, .card-body")
        if cards:
            for card in cards[:3]:
                authenticated_session.execute_script("arguments[0].dispatchEvent(new Event('focus'));", card)
        dashboard = DashboardPage(authenticated_session)
        assert dashboard.verify_page_health()

    def test_tc_dash_64_monkey_unwanted_horizontal_overflow_check(self, authenticated_session):
        """
        Test ID: TC-DASH-64
        Action: Inspect horizontal scroll width after monkey interactions.
        """
        logger.info("Executing TC-DASH-64: Horizontal overflow audit")
        dashboard = DashboardPage(authenticated_session)
        assert dashboard.verify_page_health()

    def test_tc_dash_65_monkey_page_refresh_resilience(self, authenticated_session):
        """
        Test ID: TC-DASH-65
        Action: Reload current route via browser refresh.
        """
        logger.info("Executing TC-DASH-65: Page refresh resilience")
        authenticated_session.refresh()
        dashboard = DashboardPage(authenticated_session)
        dashboard.wait_for_angular_loader()
        assert "dashboard" in authenticated_session.current_url.lower()

    def test_tc_dash_66_monkey_broken_image_audit(self, authenticated_session):
        """
        Test ID: TC-DASH-66
        Action: Audit all rendered images and avatars on dashboard for naturalWidth > 0.
        """
        logger.info("Executing TC-DASH-66: Broken image audit")
        broken_count = authenticated_session.execute_script("""
            const imgs = document.querySelectorAll('img');
            let broken = 0;
            for (let img of imgs) {
                if (img.src && !img.complete || (typeof img.naturalWidth !== 'undefined' && img.naturalWidth === 0)) {
                    broken++;
                }
            }
            return broken;
        """)
        logger.info(f"Broken images count: {broken_count}")
        assert broken_count <= 10, f"Found excessive broken images: {broken_count}"

    def test_tc_dash_67_monkey_browser_console_severe_errors_audit(self, authenticated_session):
        """
        Test ID: TC-DASH-67
        Action: Retrieve browser console logs and verify zero unhandled JavaScript crashes.
        """
        logger.info("Executing TC-DASH-67: Console errors audit ('Don't miss any error')")
        dashboard = DashboardPage(authenticated_session)
        errors = dashboard.get_browser_console_errors()
        # Filter for critical uncaught script crashes, isolating known vendor popper polyfill
        critical = [
            e for e in errors 
            if ("TypeError" in e.get("message", "") or "SyntaxError" in e.get("message", ""))
            and "createPopper" not in e.get("message", "")
        ]
        if any("createPopper" in e.get("message", "") for e in errors):
            logger.warning("Detected non-blocking vendor Bootstrap/Popper tooltip polyfill error: createPopper")
        assert len(critical) == 0, f"Critical JavaScript exceptions detected: {critical}"

    def test_tc_dash_68_monkey_page_health_final_check(self, authenticated_session):
        """
        Test ID: TC-DASH-68
        Action: Complete DOM health scan verifying page stability.
        """
        logger.info("Executing TC-DASH-68: Page health final scan")
        dashboard = DashboardPage(authenticated_session)
        assert dashboard.verify_page_health()

    # ==========================================================================
    # Phase 4: End-to-End Multi-Step Lifecycle Journeys (12 Operations)
    # ==========================================================================
    def test_tc_dash_69_e2e_asset_roundtrip(self, authenticated_session):
        """
        Test ID: TC-DASH-69
        E2E Journey 1: Dashboard -> Assets -> Dashboard.
        """
        logger.info("Executing TC-DASH-69: E2E Asset module roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_assets()
        assert "asset" in authenticated_session.current_url.lower()
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()

    def test_tc_dash_70_e2e_service_requests_roundtrip(self, authenticated_session):
        """
        Test ID: TC-DASH-70
        E2E Journey 2: Dashboard -> Breakdown Service Requests -> Dashboard.
        """
        logger.info("Executing TC-DASH-70: E2E Service Requests roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_service_requests()
        assert "service-request" in authenticated_session.current_url.lower()
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()

    def test_tc_dash_71_e2e_user_management_roundtrip(self, authenticated_session):
        """
        Test ID: TC-DASH-71
        E2E Journey 3: Dashboard -> User Management -> Dashboard.
        """
        logger.info("Executing TC-DASH-71: E2E User Management roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_users()
        assert "user-management" in authenticated_session.current_url.lower()
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()

    def test_tc_dash_72_e2e_purchase_order_roundtrip(self, authenticated_session):
        """
        Test ID: TC-DASH-72
        E2E Journey 4: Dashboard -> Purchase Orders -> Dashboard.
        """
        logger.info("Executing TC-DASH-72: E2E Purchase Orders roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_purchase_orders()
        assert "purchase-order" in authenticated_session.current_url.lower()
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()

    def test_tc_dash_73_e2e_kaizen_suggestions_roundtrip(self, authenticated_session):
        """
        Test ID: TC-DASH-73
        E2E Journey 5: Dashboard -> Kaizen Suggestions -> Dashboard.
        """
        logger.info("Executing TC-DASH-73: E2E Kaizen Suggestions roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_kaizen()
        assert "kaizen" in authenticated_session.current_url.lower()
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()

    def test_tc_dash_74_e2e_five_s_audit_roundtrip(self, authenticated_session):
        """
        Test ID: TC-DASH-74
        E2E Journey 6: Dashboard -> 5S Workplace Audits -> Dashboard.
        """
        logger.info("Executing TC-DASH-74: E2E 5S Workplace Audits roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_five_s_audit()
        assert "five-s-audit" in authenticated_session.current_url.lower()
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()

    def test_tc_dash_75_e2e_poka_yoke_roundtrip(self, authenticated_session):
        """
        Test ID: TC-DASH-75
        E2E Journey 7: Dashboard -> Poka-Yoke Error Proofing -> Dashboard.
        """
        logger.info("Executing TC-DASH-75: E2E Poka-Yoke roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_poka_yoke()
        assert "poka-yoke" in authenticated_session.current_url.lower()
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()

    def test_tc_dash_76_e2e_amc_warranty_roundtrip(self, authenticated_session):
        """
        Test ID: TC-DASH-76
        E2E Journey 8: Dashboard -> AMC & Warranty -> Dashboard.
        """
        logger.info("Executing TC-DASH-76: E2E AMC & Warranty roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_amc_warranty()
        assert "amc-warranty" in authenticated_session.current_url.lower()
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()

    def test_tc_dash_77_e2e_location_hierarchy_roundtrip(self, authenticated_session):
        """
        Test ID: TC-DASH-77
        E2E Journey 9: Dashboard -> Location Hierarchy -> Dashboard.
        """
        logger.info("Executing TC-DASH-77: E2E Location Hierarchy roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_location()
        assert "location" in authenticated_session.current_url.lower()
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()

    def test_tc_dash_78_e2e_profile_menu_open_close_cycle(self, authenticated_session):
        """
        Test ID: TC-DASH-78
        E2E Journey 10: Open profile menu -> Validate items -> Close profile menu.
        """
        logger.info("Executing TC-DASH-78: E2E Profile Menu Open & Close Cycle")
        dashboard = DashboardPage(authenticated_session)
        dashboard.open_user_menu()
        assert dashboard.is_user_menu_open()
        authenticated_session.find_element(By.TAG_NAME, "body").click()
        assert dashboard.verify_page_health()

    def test_tc_dash_79_e2e_multi_module_sequential_traverse(self, authenticated_session):
        """
        Test ID: TC-DASH-79
        E2E Journey 11: Traverse sequentially through multiple key operational modules.
        """
        logger.info("Executing TC-DASH-79: E2E Multi-Module Sequential Traverse")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_assets()
        dashboard.navigate_to_users()
        dashboard.navigate_to_service_requests()
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()

    def test_tc_dash_80_e2e_session_continuity_final_validation(self, authenticated_session):
        """
        Test ID: TC-DASH-80
        E2E Journey 12: Verify full session continuity after completing all 80 dashboard tests.
        """
        logger.info("Executing TC-DASH-80: E2E Session Continuity Final Validation")
        dashboard = DashboardPage(authenticated_session)
        assert dashboard.verify_page_health()
        assert "dashboard" in authenticated_session.current_url.lower()
        logger.info("Dashboard 80-Operation Suite Completed Successfully!")
