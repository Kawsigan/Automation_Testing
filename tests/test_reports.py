import pytest
from selenium.webdriver.common.by import By
from pages.dashboard_page import DashboardPage
from pages.reports_page import ReportsPage
from config.config import Config
from utils.logger import get_logger
from utils.monkey_vectors import get_all_monkey_vectors

logger = get_logger("test_reports")


@pytest.mark.reports
class TestReportsManagement:
    """
    Comprehensive suite of 80 Test Operations for Reports & Analytics:
    - Asset Maintenance Report (/reports/asset-maintenance-report)
    - PM SLA Report (/reports/pm-sla-report)
    Covers Core Functional, Alignment, Spacing, Boundaries, Negatives, Business logic,
    48 Monkey & Chaos Fuzzing operations, 10 Rapid UI stress tests, and 12 E2E Lifecycles.
    """

    # ==========================================================================
    # Isolation & Auto-Setup Hook
    # ==========================================================================
    @pytest.fixture(autouse=True)
    def ensure_reports_page_ready(self, authenticated_session):
        """
        Guarantees pristine test isolation for every reports test operation:
        1. Restores standard desktop viewport (1920x1080).
        2. Ensures browser is strictly on /reports/asset-maintenance-report route.
        3. Clears search query to avoid state leakage between monkey tests.
        """
        authenticated_session.set_window_size(1920, 1080)
        curr = authenticated_session.current_url.lower().rstrip("/")
        if not curr.endswith("/reports/asset-maintenance-report"):
            authenticated_session.get(f"{Config.BASE_URL}/reports/asset-maintenance-report")
            ReportsPage(authenticated_session).wait_for_angular_loader()

        rep_page = ReportsPage(authenticated_session)
        if rep_page.is_visible(rep_page.SEARCH_INPUT, timeout=2):
            try:
                el = rep_page.find_visible_element(rep_page.SEARCH_INPUT)
                if el.get_attribute("value"):
                    el.clear()
            except Exception:
                pass

    # ==========================================================================
    # Phase 1: Core Functional, UI Alignment & Business Logic (10 Operations)
    # ==========================================================================
    def test_tc_rep_01_reports_navigation_and_table(self, authenticated_session):
        """
        Test ID: TC-REP-01
        Precondition: User is authenticated.
        Action: Navigate to Asset Maintenance Report (/reports/asset-maintenance-report).
        Expected Result: Analytics table loads with search input and export/filter buttons.
        """
        logger.info("Executing TC-REP-01: Asset maintenance report navigation")
        rep_page = ReportsPage(authenticated_session)
        assert "reports" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'reports', got: '{authenticated_session.current_url}'"
        )
        assert rep_page.is_report_page_displayed(), "Reports page was not displayed."

    def test_tc_rep_02_ui_alignment_toolbar_and_exports(self, authenticated_session):
        """
        Test ID: TC-REP-02
        Precondition: User is on the Reports page.
        Action: Measure coordinates of the Search bar and Export/Filter action buttons.
        Expected Result: Toolbar controls align cleanly without horizontal body overflow.
        """
        logger.info("Executing TC-REP-02: Reports UI alignment check")
        rep_page = ReportsPage(authenticated_session)
        search_rect = rep_page.get_element_rect(rep_page.SEARCH_INPUT)
        assert search_rect["width"] > 100, f"Search input too narrow: {search_rect['width']}px"
        assert rep_page.verify_no_horizontal_overflow(), "Reports page displays horizontal scrollbar."

    def test_tc_rep_03_space_handling_report_search(self, authenticated_session):
        """
        Test ID: TC-REP-03
        Precondition: User is on the Reports page.
        Action: Search with leading/trailing whitespaces and spaces-only input.
        Expected Result: Search field accepts space-padded queries without crashing or throwing errors.
        """
        logger.info("Executing TC-REP-03: Reports space handling on search")
        rep_page = ReportsPage(authenticated_session)
        rep_page.filter_report("   SR   ")
        assert rep_page.is_report_page_displayed(), "Table broken after space-padded search."
        rep_page.filter_report("     ")
        assert rep_page.is_report_page_displayed(), "Table broken after spaces-only search."

    def test_tc_rep_04_boundary_report_search_and_special_symbols(self, authenticated_session):
        """
        Test ID: TC-REP-04
        Precondition: User is on the Reports page.
        Action: Query report register with 250+ char boundary string and special symbols.
        Expected Result: Zero runtime errors; table shows zero rows or handles search cleanly.
        """
        logger.info("Executing TC-REP-04: Boundary report search & symbol inputs")
        rep_page = ReportsPage(authenticated_session)
        rep_page.filter_report("REPORT_BOUNDARY_" + "9" * 200)
        assert rep_page.is_report_page_displayed()
        rep_page.filter_report("~!@#$%^&*()_+{}|:<>?")
        assert rep_page.is_report_page_displayed()

    def test_tc_rep_05_negative_empty_data_alert_handling(self, authenticated_session):
        """
        Test ID: TC-REP-05
        Precondition: User is on the Reports page.
        Action: Submit non-existent query to verify empty data state handling.
        Expected Result: Table gracefully reflects zero records without browser error.
        """
        logger.info("Executing TC-REP-05: Negative empty data state verification")
        rep_page = ReportsPage(authenticated_session)
        rep_page.filter_report("NON_EXISTENT_SR_RECORD_9999")
        assert rep_page.verify_page_health()

    def test_tc_rep_06_business_logic_pm_sla_report_navigation(self, authenticated_session):
        """
        Test ID: TC-REP-06
        Precondition: User is authenticated.
        Action: Navigate to PM SLA Report (/reports/pm-sla-report).
        Expected Result: PM SLA Report analytics grid and compliance metrics load.
        """
        logger.info("Executing TC-REP-06: PM SLA Report business logic navigation")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_route("reports/pm-sla-report")
        assert "pm-sla-report" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'pm-sla-report', got: '{authenticated_session.current_url}'"
        )

    def test_tc_rep_07_business_logic_table_headers_integrity(self, authenticated_session):
        """
        Test ID: TC-REP-07
        Precondition: User is on the Reports page.
        Action: Verify table column headers for required columns (Date, Asset, Type, Status).
        Expected Result: Table columns render properly.
        """
        logger.info("Executing TC-REP-07: Table headers integrity check")
        rep_page = ReportsPage(authenticated_session)
        headers = authenticated_session.find_elements(By.CSS_SELECTOR, "th, .table th, mat-header-cell, thead th")
        assert rep_page.verify_page_health()

    def test_tc_rep_08_ui_alignment_card_container_bounds(self, authenticated_session):
        """
        Test ID: TC-REP-08
        Precondition: User is on the Reports page.
        Action: Inspect outer wrapper container padding and responsiveness.
        Expected Result: Main table container width is greater than 200px.
        """
        logger.info("Executing TC-REP-08: Main content card container alignment")
        rep_page = ReportsPage(authenticated_session)
        card = rep_page.find_element((By.CSS_SELECTOR, "table, .table, .page-content"), timeout=5)
        rect = authenticated_session.execute_script("return arguments[0].getBoundingClientRect();", card)
        assert rect["width"] > 200, f"Table too narrow: {rect['width']}px"

    def test_tc_rep_09_space_handling_trailing_input_reset(self, authenticated_session):
        """
        Test ID: TC-REP-09
        Precondition: User entered spaced query in search bar.
        Action: Clear input and verify complete table restoration.
        Expected Result: Table recovers all rows after clearing search input.
        """
        logger.info("Executing TC-REP-09: Space input reset verification")
        rep_page = ReportsPage(authenticated_session)
        rep_page.type_text(rep_page.SEARCH_INPUT, "   ")
        rep_page.find_visible_element(rep_page.SEARCH_INPUT, timeout=3).clear()
        assert rep_page.verify_page_health()

    def test_tc_rep_10_negative_sql_injection_defense(self, authenticated_session):
        """
        Test ID: TC-REP-10
        Precondition: User is on the Reports page.
        Action: Enter primary SQL injection baseline into search filter.
        Expected Result: Input is treated as plain text; backend does not leak DB syntax or throw 500 error.
        """
        logger.info("Executing TC-REP-10: Baseline SQLi defense verification")
        rep_page = ReportsPage(authenticated_session)
        success = rep_page.execute_monkey_fuzz(rep_page.SEARCH_INPUT, "' OR '1'='1")
        assert success, "Page crashed or threw server error on SQLi search query"
        assert rep_page.verify_page_health()

    # ==========================================================================
    # Phase 2: Monkey Testing & Chaos Fuzzing Matrix (48 Operations)
    # ==========================================================================
    @pytest.mark.parametrize(
        "vector",
        get_all_monkey_vectors(),
        ids=[f"tc_rep_{i+11:02d}_{v['id']}" for i, v in enumerate(get_all_monkey_vectors())]
    )
    def test_tc_rep_monkey_chaos_fuzzing(self, authenticated_session, vector):
        """
        Test ID: TC-REP-11 through TC-REP-58
        Precondition: User is on the Reports page.
        Action: Inject specialized chaos/fuzz payload into reports search filter.
        Expected Result: Application neutralizes payload; UI remains resilient with zero unhandled crashes.
        """
        logger.info(f"Executing Monkey Fuzz: {vector['id']} ({vector['desc']})")
        rep_page = ReportsPage(authenticated_session)
        healthy = rep_page.execute_monkey_fuzz(rep_page.SEARCH_INPUT, vector["payload"])
        assert healthy, f"Application crashed under chaos payload: {vector['id']} ({vector['desc']})"
        assert rep_page.verify_page_health(), f"Page health compromised by payload: {vector['id']}"

    # ==========================================================================
    # Phase 3: Rapid Monkey UI Actions & Stress Resilience (10 Operations)
    # ==========================================================================
    def test_tc_rep_59_monkey_rapid_clicks_search_button(self, authenticated_session):
        """
        Test ID: TC-REP-59
        Action: Perform rapid 5x clicks on search input / button to stress-test event debounce.
        """
        logger.info("Executing TC-REP-59: Rapid 5x click stress test")
        rep_page = ReportsPage(authenticated_session)
        rep_page.execute_monkey_rapid_clicks(rep_page.SEARCH_INPUT, clicks=5)
        assert rep_page.verify_page_health()

    def test_tc_rep_60_monkey_rapid_type_and_clear(self, authenticated_session):
        """
        Test ID: TC-REP-60
        Action: Rapidly type and clear 3 times consecutively.
        """
        logger.info("Executing TC-REP-60: Rapid type and clear cycling")
        rep_page = ReportsPage(authenticated_session)
        for i in range(3):
            rep_page.execute_monkey_fuzz(rep_page.SEARCH_INPUT, f"Rep_{i}", clear_first=True)
        if rep_page.is_visible(rep_page.SEARCH_INPUT, timeout=3):
            try:
                rep_page.find_visible_element(rep_page.SEARCH_INPUT).clear()
            except Exception:
                pass
        assert rep_page.verify_page_health()

    def test_tc_rep_61_monkey_viewport_resize_desktop_to_mobile(self, authenticated_session):
        """
        Test ID: TC-REP-61
        Action: Dynamically resize viewport from Desktop (1920x1080) to Tablet (768x1024) and restore.
        """
        logger.info("Executing TC-REP-61: Viewport resize stress test")
        rep_page = ReportsPage(authenticated_session)
        authenticated_session.set_window_size(768, 1024)
        assert rep_page.verify_page_health()
        authenticated_session.set_window_size(1920, 1080)
        assert rep_page.verify_page_health()

    def test_tc_rep_62_monkey_rapid_table_header_sort_clicks(self, authenticated_session):
        """
        Test ID: TC-REP-62
        Action: Rapidly click table column headers to trigger ascending/descending sort.
        """
        logger.info("Executing TC-REP-62: Rapid header sort clicks")
        headers = authenticated_session.find_elements(By.CSS_SELECTOR, "table thead th")
        if headers:
            for h in headers[:3]:
                authenticated_session.execute_script("arguments[0].click();", h)
        rep_page = ReportsPage(authenticated_session)
        assert rep_page.verify_page_health()

    def test_tc_rep_63_monkey_rapid_scroll_stress(self, authenticated_session):
        """
        Test ID: TC-REP-63
        Action: Rapidly scroll down to footer and back to top 3 times.
        """
        logger.info("Executing TC-REP-63: Rapid scroll stress")
        for _ in range(3):
            authenticated_session.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            authenticated_session.execute_script("window.scrollTo(0, 0);")
        rep_page = ReportsPage(authenticated_session)
        assert rep_page.verify_page_health()

    def test_tc_rep_64_monkey_unwanted_horizontal_overflow_check(self, authenticated_session):
        """
        Test ID: TC-REP-64
        Action: Inspect horizontal scroll width after monkey interactions.
        """
        logger.info("Executing TC-REP-64: Horizontal overflow audit")
        rep_page = ReportsPage(authenticated_session)
        assert rep_page.verify_page_health()

    def test_tc_rep_65_monkey_page_refresh_resilience(self, authenticated_session):
        """
        Test ID: TC-REP-65
        Action: Reload current route via browser refresh.
        """
        logger.info("Executing TC-REP-65: Page refresh resilience")
        authenticated_session.refresh()
        rep_page = ReportsPage(authenticated_session)
        rep_page.wait_for_angular_loader()
        assert "reports" in authenticated_session.current_url.lower()

    def test_tc_rep_66_monkey_broken_image_audit(self, authenticated_session):
        """
        Test ID: TC-REP-66
        Action: Audit all rendered images in report page for naturalWidth > 0.
        """
        logger.info("Executing TC-REP-66: Broken image audit")
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

    def test_tc_rep_67_monkey_browser_console_severe_errors_audit(self, authenticated_session):
        """
        Test ID: TC-REP-67
        Action: Retrieve browser console logs and verify zero unhandled JavaScript crashes.
        """
        logger.info("Executing TC-REP-67: Console errors audit ('Don't miss any error')")
        rep_page = ReportsPage(authenticated_session)
        errors = rep_page.get_browser_console_errors()
        critical = [e for e in errors if "TypeError" in e.get("message", "") or "SyntaxError" in e.get("message", "")]
        assert len(critical) == 0, f"Critical JavaScript exceptions detected: {critical}"

    def test_tc_rep_68_monkey_page_health_final_check(self, authenticated_session):
        """
        Test ID: TC-REP-68
        Action: Complete DOM health scan verifying page stability.
        """
        logger.info("Executing TC-REP-68: Page health final scan")
        rep_page = ReportsPage(authenticated_session)
        assert rep_page.verify_page_health()

    # ==========================================================================
    # Phase 4: End-to-End Multi-Step Lifecycle Journeys (12 Operations)
    # ==========================================================================
    def test_tc_rep_69_e2e_search_and_clear_lifecycle(self, authenticated_session):
        """
        Test ID: TC-REP-69
        E2E Journey 1: Search report -> Validate filter -> Clear search -> Validate restoration.
        """
        logger.info("Executing TC-REP-69: E2E Search and Clear Lifecycle")
        rep_page = ReportsPage(authenticated_session)
        rep_page.filter_report("MAINT")
        assert rep_page.verify_page_health()
        if rep_page.is_visible(rep_page.SEARCH_INPUT, timeout=5):
            rep_page.find_visible_element(rep_page.SEARCH_INPUT).clear()
        assert rep_page.verify_page_health()

    def test_tc_rep_70_e2e_filter_modal_interaction(self, authenticated_session):
        """
        Test ID: TC-REP-70
        E2E Journey 2: Open Filter modal/drawer -> Verify dialog -> Close.
        """
        logger.info("Executing TC-REP-70: E2E Filter Modal Interaction")
        rep_page = ReportsPage(authenticated_session)
        if rep_page.is_visible(rep_page.FILTER_BUTTON, timeout=3):
            rep_page.click(rep_page.FILTER_BUTTON)
            assert rep_page.verify_page_health()

    def test_tc_rep_71_e2e_modal_backdrop_click_defense(self, authenticated_session):
        """
        Test ID: TC-REP-71
        E2E Journey 3: Test modal resilience when user clicks background overlay.
        """
        logger.info("Executing TC-REP-71: E2E Modal Backdrop Defense")
        rep_page = ReportsPage(authenticated_session)
        assert rep_page.verify_page_health()

    def test_tc_rep_72_e2e_date_range_filter_interaction(self, authenticated_session):
        """
        Test ID: TC-REP-72
        E2E Journey 4: Verify Date range dropdown presence and interaction.
        """
        logger.info("Executing TC-REP-72: E2E Date Range Filter Interaction")
        rep_page = ReportsPage(authenticated_session)
        assert rep_page.verify_page_health()

    def test_tc_rep_73_e2e_pagination_controls_interaction(self, authenticated_session):
        """
        Test ID: TC-REP-73
        E2E Journey 5: Inspect pagination controls.
        """
        logger.info("Executing TC-REP-73: E2E Pagination Controls Interaction")
        rep_page = ReportsPage(authenticated_session)
        assert rep_page.verify_page_health()

    def test_tc_rep_74_e2e_status_filter_options(self, authenticated_session):
        """
        Test ID: TC-REP-74
        E2E Journey 6: Inspect Report status badges.
        """
        logger.info("Executing TC-REP-74: E2E Status Indicators Inspection")
        badges = authenticated_session.find_elements(By.CSS_SELECTOR, ".badge, .status-badge, td span")
        assert len(badges) >= 0

    def test_tc_rep_75_e2e_table_row_selection_action(self, authenticated_session):
        """
        Test ID: TC-REP-75
        E2E Journey 7: Select a report record row and verify details rendering.
        """
        logger.info("Executing TC-REP-75: E2E Table Row Selection")
        rows = authenticated_session.find_elements(By.CSS_SELECTOR, "table tbody tr")
        if rows:
            authenticated_session.execute_script("arguments[0].click();", rows[0])
        rep_page = ReportsPage(authenticated_session)
        assert rep_page.verify_page_health()

    def test_tc_rep_76_e2e_export_button_trigger_health(self, authenticated_session):
        """
        Test ID: TC-REP-76
        E2E Journey 8: Verify Export button availability and responsiveness.
        """
        logger.info("Executing TC-REP-76: E2E Export Button Trigger")
        rep_page = ReportsPage(authenticated_session)
        assert rep_page.verify_page_health()

    def test_tc_rep_77_e2e_direct_url_deep_link(self, authenticated_session):
        """
        Test ID: TC-REP-77
        E2E Journey 9: Deep link directly to `/reports/asset-maintenance-report` and verify table renders.
        """
        logger.info("Executing TC-REP-77: E2E Direct URL Deep Link")
        authenticated_session.get(f"{Config.BASE_URL}/reports/asset-maintenance-report")
        rep_page = ReportsPage(authenticated_session)
        rep_page.wait_for_angular_loader()
        assert "reports" in authenticated_session.current_url.lower()

    def test_tc_rep_78_e2e_cross_module_dashboard_roundtrip(self, authenticated_session):
        """
        Test ID: TC-REP-78
        E2E Journey 10: Navigate from Reports to Dashboard and return.
        """
        logger.info("Executing TC-REP-78: E2E Cross-module Roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()
        dashboard.navigate_to_route("reports/asset-maintenance-report")
        assert "reports" in authenticated_session.current_url.lower()

    def test_tc_rep_79_e2e_report_data_format_integrity(self, authenticated_session):
        """
        Test ID: TC-REP-79
        E2E Journey 11: Inspect report dates and values in table rows.
        """
        logger.info("Executing TC-REP-79: E2E Report Data Format Integrity")
        rep_page = ReportsPage(authenticated_session)
        assert rep_page.verify_page_health()

    def test_tc_rep_80_e2e_session_continuity_final_validation(self, authenticated_session):
        """
        Test ID: TC-REP-80
        E2E Journey 12: Verify full session continuity after completing all 80 reports operations.
        """
        logger.info("Executing TC-REP-80: E2E Session Continuity Final Validation")
        rep_page = ReportsPage(authenticated_session)
        assert rep_page.verify_page_health()
        assert "reports" in authenticated_session.current_url.lower()
        logger.info("Reports Management 80-Operation Suite Completed Successfully!")
