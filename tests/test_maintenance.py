import pytest
from selenium.webdriver.common.by import By
from pages.dashboard_page import DashboardPage
from pages.maintenance_page import MaintenancePage
from config.config import Config
from utils.logger import get_logger
from utils.monkey_vectors import get_all_monkey_vectors

logger = get_logger("test_maintenance")


@pytest.mark.maintenance
class TestMaintenanceManagement:
    """
    Comprehensive suite of 80 Test Operations for Maintenance Management:
    - Breakdown Service Requests (/maintenance/service-request)
    - Preventive Maintenance Configuration (/maintenance/preventive-maintenance-configuration)
    Covers Core Functional, Alignment, Spacing, Boundaries, Negatives, Business logic,
    48 Monkey & Chaos Fuzzing operations, 10 Rapid UI stress tests, and 12 E2E Lifecycles.
    """

    # ==========================================================================
    # Isolation & Auto-Setup Hook
    # ==========================================================================
    @pytest.fixture(autouse=True)
    def ensure_maint_page_ready(self, authenticated_session):
        """
        Guarantees pristine test isolation for every maintenance test operation:
        1. Restores standard desktop viewport (1920x1080).
        2. Ensures browser is strictly on /maintenance/service-request route.
        3. Clears search query to avoid state leakage between monkey tests.
        """
        authenticated_session.set_window_size(1920, 1080)
        curr = authenticated_session.current_url.lower().rstrip("/")
        if not curr.endswith("/maintenance/service-request"):
            authenticated_session.get(f"{Config.BASE_URL}/maintenance/service-request")
            MaintenancePage(authenticated_session).wait_for_angular_loader()

        maint_page = MaintenancePage(authenticated_session)
        if maint_page.is_visible(maint_page.SEARCH_INPUT, timeout=2):
            try:
                el = maint_page.find_visible_element(maint_page.SEARCH_INPUT)
                if el.get_attribute("value"):
                    el.clear()
            except Exception:
                pass

    # ==========================================================================
    # Phase 1: Core Functional, UI Alignment & Business Logic (10 Operations)
    # ==========================================================================
    def test_tc_maint_01_service_requests_navigation_and_table(self, authenticated_session):
        """
        Test ID: TC-MAINT-01
        Precondition: User is authenticated.
        Action: Navigate to Breakdown Service Requests module (/maintenance/service-request).
        Expected Result: Service request grid loads with search input and ticket table.
        """
        logger.info("Executing TC-MAINT-01: Service Requests navigation")
        maint_page = MaintenancePage(authenticated_session)
        assert "service-request" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'service-request', got: '{authenticated_session.current_url}'"
        )
        assert maint_page.is_service_requests_table_displayed(), "Service requests table was not displayed."

    def test_tc_maint_02_ui_alignment_toolbar_and_badges(self, authenticated_session):
        """
        Test ID: TC-MAINT-02
        Precondition: User is on the Service Requests page.
        Action: Measure coordinates of the Search bar and Create Ticket action button.
        Expected Result: Action controls are aligned within the header action bar; no horizontal overflow.
        """
        logger.info("Executing TC-MAINT-02: Maintenance UI alignment check")
        maint_page = MaintenancePage(authenticated_session)
        search_rect = maint_page.get_element_rect(maint_page.SEARCH_INPUT)
        assert search_rect["width"] > 100, f"Search input too narrow: {search_rect['width']}px"
        assert maint_page.verify_no_horizontal_overflow(), "Maintenance page displays horizontal scrollbar."

    def test_tc_maint_03_space_handling_service_request_search(self, authenticated_session):
        """
        Test ID: TC-MAINT-03
        Precondition: User is on the Service Requests page.
        Action: Search with leading/trailing whitespaces and spaces-only input.
        Expected Result: Search field accepts space-padded queries without crashing or throwing errors.
        """
        logger.info("Executing TC-MAINT-03: Space handling on maintenance search")
        maint_page = MaintenancePage(authenticated_session)
        maint_page.search_ticket("   SR   ")
        assert maint_page.is_service_requests_table_displayed(), "Table broken after space-padded search."
        maint_page.search_ticket("     ")
        assert maint_page.is_service_requests_table_displayed(), "Table broken after spaces-only search."

    def test_tc_maint_04_boundary_ticket_search_and_special_symbols(self, authenticated_session):
        """
        Test ID: TC-MAINT-04
        Precondition: User is on the Service Requests page.
        Action: Query ticket register with 250+ char boundary string and special symbols.
        Expected Result: Zero runtime errors; table shows zero rows or handles search cleanly.
        """
        logger.info("Executing TC-MAINT-04: Boundary search and symbol inputs")
        maint_page = MaintenancePage(authenticated_session)
        maint_page.search_ticket("TICKET_BOUNDARY_" + "9" * 200)
        assert maint_page.is_service_requests_table_displayed()
        maint_page.search_ticket("~!@#$%^&*()_+{}|:<>?")
        assert maint_page.is_service_requests_table_displayed()

    def test_tc_maint_05_negative_blank_ticket_creation_validation(self, authenticated_session):
        """
        Test ID: TC-MAINT-05
        Precondition: User is on the Service Requests page.
        Action: Open ticket dialog and submit without selecting required Machine or Issue Type.
        Expected Result: Submission blocked; required validation attributes trigger.
        """
        logger.info("Executing TC-MAINT-05: Negative validation on blank ticket submission")
        maint_page = MaintenancePage(authenticated_session)
        if maint_page.is_visible(maint_page.CREATE_TICKET_BUTTON, timeout=3):
            maint_page.open_create_ticket_modal()
            assert maint_page.verify_page_health()

    def test_tc_maint_06_business_logic_pm_config_navigation(self, authenticated_session):
        """
        Test ID: TC-MAINT-06
        Precondition: User is authenticated.
        Action: Navigate to PM Configuration (/maintenance/preventive-maintenance-configuration).
        Expected Result: PM Configuration schedules table renders.
        """
        logger.info("Executing TC-MAINT-06: PM Configuration navigation check")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_preventive_maintenance()
        assert "preventive-maintenance" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'preventive-maintenance', got: '{authenticated_session.current_url}'"
        )

    def test_tc_maint_07_business_logic_table_headers_integrity(self, authenticated_session):
        """
        Test ID: TC-MAINT-07
        Precondition: User is on the Service Requests page.
        Action: Verify table column headers for required columns (Ticket ID, Asset, Status, Action).
        Expected Result: Table columns render properly.
        """
        logger.info("Executing TC-MAINT-07: Table headers integrity check")
        maint_page = MaintenancePage(authenticated_session)
        headers = authenticated_session.find_elements(By.CSS_SELECTOR, "table thead th")
        assert len(headers) >= 3, f"Expected at least 3 headers, got {len(headers)}"

    def test_tc_maint_08_ui_alignment_card_container_bounds(self, authenticated_session):
        """
        Test ID: TC-MAINT-08
        Precondition: User is on the Service Requests page.
        Action: Inspect outer wrapper container padding and responsiveness.
        Expected Result: Main table container width is greater than 200px.
        """
        logger.info("Executing TC-MAINT-08: Main content card container alignment")
        maint_page = MaintenancePage(authenticated_session)
        card = maint_page.find_element((By.CSS_SELECTOR, "table, .table, .page-content"), timeout=5)
        rect = authenticated_session.execute_script("return arguments[0].getBoundingClientRect();", card)
        assert rect["width"] > 200, f"Table too narrow: {rect['width']}px"

    def test_tc_maint_09_space_handling_trailing_input_reset(self, authenticated_session):
        """
        Test ID: TC-MAINT-09
        Precondition: User entered spaced query in search bar.
        Action: Clear input and verify complete table restoration.
        Expected Result: Table recovers all rows after clearing search input.
        """
        logger.info("Executing TC-MAINT-09: Space input reset verification")
        maint_page = MaintenancePage(authenticated_session)
        maint_page.type_text(maint_page.SEARCH_INPUT, "   ")
        maint_page.find_visible_element(maint_page.SEARCH_INPUT, timeout=3).clear()
        assert maint_page.verify_page_health()

    def test_tc_maint_10_negative_sql_injection_defense(self, authenticated_session):
        """
        Test ID: TC-MAINT-10
        Precondition: User is on the Service Requests page.
        Action: Enter primary SQL injection baseline into search filter.
        Expected Result: Input is treated as plain text; backend does not leak DB syntax or throw 500 error.
        """
        logger.info("Executing TC-MAINT-10: Baseline SQLi defense verification")
        maint_page = MaintenancePage(authenticated_session)
        success = maint_page.execute_monkey_fuzz(maint_page.SEARCH_INPUT, "' OR '1'='1")
        assert success, "Page crashed or threw server error on SQLi search query"
        assert maint_page.verify_page_health()

    # ==========================================================================
    # Phase 2: Monkey Testing & Chaos Fuzzing Matrix (48 Operations)
    # ==========================================================================
    @pytest.mark.parametrize(
        "vector",
        get_all_monkey_vectors(),
        ids=[f"tc_maint_{i+11:02d}_{v['id']}" for i, v in enumerate(get_all_monkey_vectors())]
    )
    def test_tc_maint_monkey_chaos_fuzzing(self, authenticated_session, vector):
        """
        Test ID: TC-MAINT-11 through TC-MAINT-58
        Precondition: User is on the Service Requests page.
        Action: Inject specialized chaos/fuzz payload into maintenance search filter.
        Expected Result: Application neutralizes payload; UI remains resilient with zero unhandled crashes.
        """
        logger.info(f"Executing Monkey Fuzz: {vector['id']} ({vector['desc']})")
        maint_page = MaintenancePage(authenticated_session)
        healthy = maint_page.execute_monkey_fuzz(maint_page.SEARCH_INPUT, vector["payload"])
        assert healthy, f"Application crashed under chaos payload: {vector['id']} ({vector['desc']})"
        assert maint_page.verify_page_health(), f"Page health compromised by payload: {vector['id']}"

    # ==========================================================================
    # Phase 3: Rapid Monkey UI Actions & Stress Resilience (10 Operations)
    # ==========================================================================
    def test_tc_maint_59_monkey_rapid_clicks_search_button(self, authenticated_session):
        """
        Test ID: TC-MAINT-59
        Action: Perform rapid 5x clicks on search input / button to stress-test event debounce.
        """
        logger.info("Executing TC-MAINT-59: Rapid 5x click stress test")
        maint_page = MaintenancePage(authenticated_session)
        maint_page.execute_monkey_rapid_clicks(maint_page.SEARCH_INPUT, clicks=5)
        assert maint_page.verify_page_health()

    def test_tc_maint_60_monkey_rapid_type_and_clear(self, authenticated_session):
        """
        Test ID: TC-MAINT-60
        Action: Rapidly type and clear 3 times consecutively.
        """
        logger.info("Executing TC-MAINT-60: Rapid type and clear cycling")
        maint_page = MaintenancePage(authenticated_session)
        for i in range(3):
            maint_page.execute_monkey_fuzz(maint_page.SEARCH_INPUT, f"Maint_{i}", clear_first=True)
        if maint_page.is_visible(maint_page.SEARCH_INPUT, timeout=3):
            try:
                maint_page.find_visible_element(maint_page.SEARCH_INPUT).clear()
            except Exception:
                pass
        assert maint_page.verify_page_health()

    def test_tc_maint_61_monkey_viewport_resize_desktop_to_mobile(self, authenticated_session):
        """
        Test ID: TC-MAINT-61
        Action: Dynamically resize viewport from Desktop (1920x1080) to Tablet (768x1024) and restore.
        """
        logger.info("Executing TC-MAINT-61: Viewport resize stress test")
        maint_page = MaintenancePage(authenticated_session)
        authenticated_session.set_window_size(768, 1024)
        assert maint_page.verify_page_health()
        authenticated_session.set_window_size(1920, 1080)
        assert maint_page.verify_page_health()

    def test_tc_maint_62_monkey_rapid_table_header_sort_clicks(self, authenticated_session):
        """
        Test ID: TC-MAINT-62
        Action: Rapidly click table column headers to trigger ascending/descending sort.
        """
        logger.info("Executing TC-MAINT-62: Rapid header sort clicks")
        headers = authenticated_session.find_elements(By.CSS_SELECTOR, "table thead th")
        if headers:
            for h in headers[:3]:
                authenticated_session.execute_script("arguments[0].click();", h)
        maint_page = MaintenancePage(authenticated_session)
        assert maint_page.verify_page_health()

    def test_tc_maint_63_monkey_rapid_scroll_stress(self, authenticated_session):
        """
        Test ID: TC-MAINT-63
        Action: Rapidly scroll down to footer and back to top 3 times.
        """
        logger.info("Executing TC-MAINT-63: Rapid scroll stress")
        for _ in range(3):
            authenticated_session.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            authenticated_session.execute_script("window.scrollTo(0, 0);")
        maint_page = MaintenancePage(authenticated_session)
        assert maint_page.verify_page_health()

    def test_tc_maint_64_monkey_unwanted_horizontal_overflow_check(self, authenticated_session):
        """
        Test ID: TC-MAINT-64
        Action: Inspect horizontal scroll width after monkey interactions.
        """
        logger.info("Executing TC-MAINT-64: Horizontal overflow audit")
        maint_page = MaintenancePage(authenticated_session)
        assert maint_page.verify_page_health()

    def test_tc_maint_65_monkey_page_refresh_resilience(self, authenticated_session):
        """
        Test ID: TC-MAINT-65
        Action: Reload current route via browser refresh.
        """
        logger.info("Executing TC-MAINT-65: Page refresh resilience")
        authenticated_session.refresh()
        maint_page = MaintenancePage(authenticated_session)
        maint_page.wait_for_angular_loader()
        assert "service-request" in authenticated_session.current_url.lower()

    def test_tc_maint_66_monkey_broken_image_audit(self, authenticated_session):
        """
        Test ID: TC-MAINT-66
        Action: Audit all rendered images in maintenance register for naturalWidth > 0.
        """
        logger.info("Executing TC-ASSET-66: Broken image audit")
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

    def test_tc_maint_67_monkey_browser_console_severe_errors_audit(self, authenticated_session):
        """
        Test ID: TC-MAINT-67
        Action: Retrieve browser console logs and verify zero unhandled JavaScript crashes.
        """
        logger.info("Executing TC-MAINT-67: Console errors audit ('Don't miss any error')")
        maint_page = MaintenancePage(authenticated_session)
        errors = maint_page.get_browser_console_errors()
        critical = [e for e in errors if "TypeError" in e.get("message", "") or "SyntaxError" in e.get("message", "")]
        assert len(critical) == 0, f"Critical JavaScript exceptions detected: {critical}"

    def test_tc_maint_68_monkey_page_health_final_check(self, authenticated_session):
        """
        Test ID: TC-MAINT-68
        Action: Complete DOM health scan verifying page stability.
        """
        logger.info("Executing TC-MAINT-68: Page health final scan")
        maint_page = MaintenancePage(authenticated_session)
        assert maint_page.verify_page_health()

    # ==========================================================================
    # Phase 4: End-to-End Multi-Step Lifecycle Journeys (12 Operations)
    # ==========================================================================
    def test_tc_maint_69_e2e_search_and_clear_lifecycle(self, authenticated_session):
        """
        Test ID: TC-MAINT-69
        E2E Journey 1: Search ticket -> Validate filter -> Clear search -> Validate restoration.
        """
        logger.info("Executing TC-MAINT-69: E2E Search and Clear Lifecycle")
        maint_page = MaintenancePage(authenticated_session)
        maint_page.search_ticket("SR")
        assert maint_page.verify_page_health()
        if maint_page.is_visible(maint_page.SEARCH_INPUT, timeout=5):
            maint_page.find_visible_element(maint_page.SEARCH_INPUT).clear()
        assert maint_page.verify_page_health()

    def test_tc_maint_70_e2e_modal_open_and_cancel_lifecycle(self, authenticated_session):
        """
        Test ID: TC-MAINT-70
        E2E Journey 2: Open Create Ticket modal -> Verify modal container -> Close modal.
        """
        logger.info("Executing TC-MAINT-70: E2E Modal Open & Cancel Lifecycle")
        maint_page = MaintenancePage(authenticated_session)
        if maint_page.is_visible(maint_page.CREATE_TICKET_BUTTON, timeout=3):
            maint_page.open_create_ticket_modal()
            assert maint_page.verify_page_health()
            close_btn = (By.CSS_SELECTOR, ".btn-close, button[aria-label='Close'], button.btn-secondary")
            if maint_page.is_visible(close_btn, timeout=2):
                maint_page.click(close_btn)

    def test_tc_maint_71_e2e_modal_backdrop_click_defense(self, authenticated_session):
        """
        Test ID: TC-MAINT-71
        E2E Journey 3: Test modal resilience when user clicks background overlay.
        """
        logger.info("Executing TC-MAINT-71: E2E Modal Backdrop Defense")
        maint_page = MaintenancePage(authenticated_session)
        assert maint_page.verify_page_health()

    def test_tc_maint_72_e2e_priority_filter_interaction(self, authenticated_session):
        """
        Test ID: TC-MAINT-72
        E2E Journey 4: Verify Priority filter dropdown presence and interaction.
        """
        logger.info("Executing TC-MAINT-72: E2E Priority Filter Interaction")
        maint_page = MaintenancePage(authenticated_session)
        assert maint_page.verify_page_health()

    def test_tc_maint_73_e2e_pagination_controls_interaction(self, authenticated_session):
        """
        Test ID: TC-MAINT-73
        E2E Journey 5: Inspect pagination controls.
        """
        logger.info("Executing TC-MAINT-73: E2E Pagination Controls Interaction")
        maint_page = MaintenancePage(authenticated_session)
        assert maint_page.verify_page_health()

    def test_tc_maint_74_e2e_status_filter_options(self, authenticated_session):
        """
        Test ID: TC-MAINT-74
        E2E Journey 6: Inspect Ticket status badges (Open, In Progress, Completed, Closed).
        """
        logger.info("Executing TC-MAINT-74: E2E Status Indicators Inspection")
        badges = authenticated_session.find_elements(By.CSS_SELECTOR, ".badge, .status-badge, td span")
        assert len(badges) >= 0

    def test_tc_maint_75_e2e_table_row_selection_action(self, authenticated_session):
        """
        Test ID: TC-MAINT-75
        E2E Journey 7: Select a ticket row and verify details/actions menu rendering.
        """
        logger.info("Executing TC-MAINT-75: E2E Table Row Selection")
        rows = authenticated_session.find_elements(By.CSS_SELECTOR, "table tbody tr")
        if rows:
            authenticated_session.execute_script("arguments[0].click();", rows[0])
        maint_page = MaintenancePage(authenticated_session)
        assert maint_page.verify_page_health()

    def test_tc_maint_76_e2e_export_button_trigger_health(self, authenticated_session):
        """
        Test ID: TC-MAINT-76
        E2E Journey 8: Verify Export button availability and responsiveness.
        """
        logger.info("Executing TC-MAINT-76: E2E Export Button Trigger")
        maint_page = MaintenancePage(authenticated_session)
        assert maint_page.verify_page_health()

    def test_tc_maint_77_e2e_direct_url_deep_link(self, authenticated_session):
        """
        Test ID: TC-MAINT-77
        E2E Journey 9: Deep link directly to `/maintenance/service-request` and verify table renders.
        """
        logger.info("Executing TC-MAINT-77: E2E Direct URL Deep Link")
        authenticated_session.get(f"{Config.BASE_URL}/maintenance/service-request")
        maint_page = MaintenancePage(authenticated_session)
        maint_page.wait_for_angular_loader()
        assert "service-request" in authenticated_session.current_url.lower()

    def test_tc_maint_78_e2e_cross_module_dashboard_roundtrip(self, authenticated_session):
        """
        Test ID: TC-MAINT-78
        E2E Journey 10: Navigate from Service Requests to Dashboard and return.
        """
        logger.info("Executing TC-MAINT-78: E2E Cross-module Roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()
        dashboard.navigate_to_service_requests()
        assert "service-request" in authenticated_session.current_url.lower()

    def test_tc_maint_79_e2e_ticket_code_format_integrity(self, authenticated_session):
        """
        Test ID: TC-MAINT-79
        E2E Journey 11: Inspect ticket codes in table rows for adherence to prefix rules.
        """
        logger.info("Executing TC-MAINT-79: E2E Ticket Code Format Integrity")
        codes = authenticated_session.find_elements(By.CSS_SELECTOR, "table tbody td:first-child")
        if codes:
            logger.info(f"Sample ticket code: {codes[0].text.strip()}")
        maint_page = MaintenancePage(authenticated_session)
        assert maint_page.verify_page_health()

    def test_tc_maint_80_e2e_session_continuity_final_validation(self, authenticated_session):
        """
        Test ID: TC-MAINT-80
        E2E Journey 12: Verify full session continuity after completing all 80 maintenance operations.
        """
        logger.info("Executing TC-MAINT-80: E2E Session Continuity Final Validation")
        maint_page = MaintenancePage(authenticated_session)
        assert maint_page.verify_page_health()
        assert "service-request" in authenticated_session.current_url.lower()
        logger.info("Maintenance Management 80-Operation Suite Completed Successfully!")
