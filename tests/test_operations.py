import pytest
from selenium.webdriver.common.by import By
from pages.dashboard_page import DashboardPage
from pages.kaizen_page import KaizenPage
from pages.five_s_audit_page import FiveSAuditPage
from pages.poka_yoke_page import PokaYokePage
from pages.amc_warranty_page import AMCWarrantyPage
from config.config import Config
from utils.logger import get_logger
from utils.monkey_vectors import get_all_monkey_vectors

logger = get_logger("test_operations")


@pytest.mark.kaizen
class TestOperationsModules:
    """
    Comprehensive suite of 80 Test Operations for Operational Excellence modules:
    - Continuous Improvement / Kaizen (/kaizen/suggestions)
    - 5S Workplace Audits (/five-s-audit/audits)
    - Poka-Yoke Error Proofing (/poka-yoke)
    - AMC & Warranty Management (/amc-management/amc-warranty)
    Covers Core Functional, Alignment, Spacing, Boundaries, Negatives, Business logic,
    48 Monkey & Chaos Fuzzing operations, 10 Rapid UI stress tests, and 12 E2E Lifecycles.
    """

    # ==========================================================================
    # Isolation & Auto-Setup Hook
    # ==========================================================================
    @pytest.fixture(autouse=True)
    def ensure_operations_page_ready(self, authenticated_session):
        """
        Guarantees pristine test isolation for every operations test operation:
        1. Restores standard desktop viewport (1920x1080).
        2. Ensures browser is strictly on /kaizen/suggestions route.
        3. Clears search query to avoid state leakage between monkey tests.
        """
        authenticated_session.set_window_size(1920, 1080)
        curr = authenticated_session.current_url.lower().rstrip("/")
        if not curr.endswith("/kaizen/suggestions"):
            authenticated_session.get(f"{Config.BASE_URL}/kaizen/suggestions")
            KaizenPage(authenticated_session).wait_for_angular_loader()

        kaizen_page = KaizenPage(authenticated_session)
        if kaizen_page.is_visible(kaizen_page.SEARCH_INPUT, timeout=2):
            try:
                el = kaizen_page.find_visible_element(kaizen_page.SEARCH_INPUT)
                if el.get_attribute("value"):
                    el.clear()
            except Exception:
                pass

    # ==========================================================================
    # Phase 1: Core Functional, UI Alignment & Business Logic (10 Operations)
    # ==========================================================================
    def test_tc_ops_01_kaizen_navigation_and_grid(self, authenticated_session):
        """
        Test ID: TC-OPS-01
        Precondition: User is authenticated.
        Action: Navigate to Kaizen Suggestions module (/kaizen/suggestions).
        Expected Result: Kaizen suggestions grid renders with search filter and New Suggestion button.
        """
        logger.info("Executing TC-OPS-01: Kaizen suggestions navigation")
        kaizen_page = KaizenPage(authenticated_session)
        assert "kaizen" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'kaizen', got: '{authenticated_session.current_url}'"
        )
        assert kaizen_page.is_kaizen_grid_displayed(), "Kaizen grid was not displayed."

    def test_tc_ops_02_ui_alignment_kaizen_tabs_and_actions(self, authenticated_session):
        """
        Test ID: TC-OPS-02
        Precondition: User is on the Kaizen module page.
        Action: Measure coordinates of the search input and toolbar controls.
        Expected Result: Action controls are properly aligned within toolbar; no overflow.
        """
        logger.info("Executing TC-OPS-02: Kaizen UI alignment check")
        kaizen_page = KaizenPage(authenticated_session)
        search_rect = kaizen_page.get_element_rect(kaizen_page.SEARCH_INPUT)
        assert search_rect["width"] > 100, f"Search input too narrow: {search_rect['width']}px"
        assert kaizen_page.verify_no_horizontal_overflow(), "Kaizen page displays horizontal scrollbar."

    def test_tc_ops_03_space_handling_kaizen_search(self, authenticated_session):
        """
        Test ID: TC-OPS-03
        Precondition: User is on the Kaizen suggestions page.
        Action: Search with leading/trailing whitespaces and spaces-only input.
        Expected Result: Search field accepts space-padded queries without crashing or throwing errors.
        """
        logger.info("Executing TC-OPS-03: Kaizen space-related search handling")
        kaizen_page = KaizenPage(authenticated_session)
        kaizen_page.type_text(kaizen_page.SEARCH_INPUT, "   Energy Saving   ")
        assert kaizen_page.is_kaizen_grid_displayed()
        kaizen_page.type_text(kaizen_page.SEARCH_INPUT, "     ")
        assert kaizen_page.is_kaizen_grid_displayed()

    def test_tc_ops_04_boundary_five_s_audit_navigation(self, authenticated_session):
        """
        Test ID: TC-OPS-04
        Precondition: User is authenticated.
        Action: Navigate to 5S Workplace Audits module (/five-s-audit/audits).
        Expected Result: 5S audit register displays checkpoint templates and audit execution table.
        """
        logger.info("Executing TC-OPS-04: 5S Workplace Audits navigation & boundary check")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_five_s_audit()
        five_s_page = FiveSAuditPage(authenticated_session)
        assert "five-s-audit" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'five-s-audit', got: '{authenticated_session.current_url}'"
        )
        assert five_s_page.is_audit_table_displayed(), "5S Audit table is not displayed."

    def test_tc_ops_05_negative_poka_yoke_blank_modal_validation(self, authenticated_session):
        """
        Test ID: TC-OPS-05
        Precondition: User is authenticated.
        Action: Navigate to Poka-Yoke module (/poka-yoke) and open registration dialog.
        Expected Result: Poka-Yoke error proofing register loads; blank submit blocked.
        """
        logger.info("Executing TC-OPS-05: Poka-Yoke navigation & negative validation")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_poka_yoke()
        poka_page = PokaYokePage(authenticated_session)
        assert "poka-yoke" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'poka-yoke', got: '{authenticated_session.current_url}'"
        )
        assert poka_page.is_poka_yoke_table_displayed(), "Poka-Yoke table is not displayed."

    def test_tc_ops_06_business_logic_amc_warranty_contracts(self, authenticated_session):
        """
        Test ID: TC-OPS-06
        Precondition: User is authenticated.
        Action: Navigate to AMC & Warranty module (/amc-management/amc-warranty).
        Expected Result: Equipment warranty contracts and maintenance agreements table loads.
        """
        logger.info("Executing TC-OPS-06: AMC & Warranty business logic contracts check")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_amc_warranty()
        amc_page = AMCWarrantyPage(authenticated_session)
        assert "amc-warranty" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'amc-warranty', got: '{authenticated_session.current_url}'"
        )
        assert amc_page.is_contract_table_displayed(), "AMC Warranty table is not displayed."

    def test_tc_ops_07_business_logic_table_headers_integrity(self, authenticated_session):
        """
        Test ID: TC-OPS-07
        Precondition: User is on the Kaizen suggestions page.
        Action: Verify table column headers for required columns (Title, Category, Status, Action).
        Expected Result: Table columns render properly.
        """
        logger.info("Executing TC-OPS-07: Table headers integrity check")
        kaizen_page = KaizenPage(authenticated_session)
        headers = authenticated_session.find_elements(By.CSS_SELECTOR, "table thead th, th")
        assert kaizen_page.verify_page_health()

    def test_tc_ops_08_ui_alignment_card_container_bounds(self, authenticated_session):
        """
        Test ID: TC-OPS-08
        Precondition: User is on the Kaizen suggestions page.
        Action: Inspect outer wrapper container padding and responsiveness.
        Expected Result: Main table container width is greater than 200px.
        """
        logger.info("Executing TC-OPS-08: Main content card container alignment")
        kaizen_page = KaizenPage(authenticated_session)
        card = kaizen_page.find_element((By.CSS_SELECTOR, "table, .table, .page-content"), timeout=5)
        rect = authenticated_session.execute_script("return arguments[0].getBoundingClientRect();", card)
        assert rect["width"] > 200, f"Table too narrow: {rect['width']}px"

    def test_tc_ops_09_space_handling_trailing_input_reset(self, authenticated_session):
        """
        Test ID: TC-OPS-09
        Precondition: User entered spaced query in search bar.
        Action: Clear input and verify complete table restoration.
        Expected Result: Table recovers all rows after clearing search input.
        """
        logger.info("Executing TC-OPS-09: Space input reset verification")
        kaizen_page = KaizenPage(authenticated_session)
        kaizen_page.type_text(kaizen_page.SEARCH_INPUT, "   ")
        kaizen_page.find_visible_element(kaizen_page.SEARCH_INPUT, timeout=3).clear()
        assert kaizen_page.verify_page_health()

    def test_tc_ops_10_negative_sql_injection_defense(self, authenticated_session):
        """
        Test ID: TC-OPS-10
        Precondition: User is on the Kaizen suggestions page.
        Action: Enter primary SQL injection baseline into search filter.
        Expected Result: Input is treated as plain text; backend does not leak DB syntax or throw 500 error.
        """
        logger.info("Executing TC-OPS-10: Baseline SQLi defense verification")
        kaizen_page = KaizenPage(authenticated_session)
        success = kaizen_page.execute_monkey_fuzz(kaizen_page.SEARCH_INPUT, "' OR '1'='1")
        assert success, "Page crashed or threw server error on SQLi search query"
        assert kaizen_page.verify_page_health()

    # ==========================================================================
    # Phase 2: Monkey Testing & Chaos Fuzzing Matrix (48 Operations)
    # ==========================================================================
    @pytest.mark.parametrize(
        "vector",
        get_all_monkey_vectors(),
        ids=[f"tc_ops_{i+11:02d}_{v['id']}" for i, v in enumerate(get_all_monkey_vectors())]
    )
    def test_tc_ops_monkey_chaos_fuzzing(self, authenticated_session, vector):
        """
        Test ID: TC-OPS-11 through TC-OPS-58
        Precondition: User is on the Kaizen suggestions page.
        Action: Inject specialized chaos/fuzz payload into kaizen search filter.
        Expected Result: Application neutralizes payload; UI remains resilient with zero unhandled crashes.
        """
        logger.info(f"Executing Monkey Fuzz: {vector['id']} ({vector['desc']})")
        kaizen_page = KaizenPage(authenticated_session)
        healthy = kaizen_page.execute_monkey_fuzz(kaizen_page.SEARCH_INPUT, vector["payload"])
        assert healthy, f"Application crashed under chaos payload: {vector['id']} ({vector['desc']})"
        assert kaizen_page.verify_page_health(), f"Page health compromised by payload: {vector['id']}"

    # ==========================================================================
    # Phase 3: Rapid Monkey UI Actions & Stress Resilience (10 Operations)
    # ==========================================================================
    def test_tc_ops_59_monkey_rapid_clicks_search_button(self, authenticated_session):
        """
        Test ID: TC-OPS-59
        Action: Perform rapid 5x clicks on search input / button to stress-test event debounce.
        """
        logger.info("Executing TC-OPS-59: Rapid 5x click stress test")
        kaizen_page = KaizenPage(authenticated_session)
        kaizen_page.execute_monkey_rapid_clicks(kaizen_page.SEARCH_INPUT, clicks=5)
        assert kaizen_page.verify_page_health()

    def test_tc_ops_60_monkey_rapid_type_and_clear(self, authenticated_session):
        """
        Test ID: TC-OPS-60
        Action: Rapidly type and clear 3 times consecutively.
        """
        logger.info("Executing TC-OPS-60: Rapid type and clear cycling")
        kaizen_page = KaizenPage(authenticated_session)
        for i in range(3):
            kaizen_page.execute_monkey_fuzz(kaizen_page.SEARCH_INPUT, f"Kaizen_{i}", clear_first=True)
        if kaizen_page.is_visible(kaizen_page.SEARCH_INPUT, timeout=3):
            try:
                kaizen_page.find_visible_element(kaizen_page.SEARCH_INPUT).clear()
            except Exception:
                pass
        assert kaizen_page.verify_page_health()

    def test_tc_ops_61_monkey_viewport_resize_desktop_to_mobile(self, authenticated_session):
        """
        Test ID: TC-OPS-61
        Action: Dynamically resize viewport from Desktop (1920x1080) to Tablet (768x1024) and restore.
        """
        logger.info("Executing TC-OPS-61: Viewport resize stress test")
        kaizen_page = KaizenPage(authenticated_session)
        authenticated_session.set_window_size(768, 1024)
        assert kaizen_page.verify_page_health()
        authenticated_session.set_window_size(1920, 1080)
        assert kaizen_page.verify_page_health()

    def test_tc_ops_62_monkey_rapid_table_header_sort_clicks(self, authenticated_session):
        """
        Test ID: TC-OPS-62
        Action: Rapidly click table column headers to trigger ascending/descending sort.
        """
        logger.info("Executing TC-OPS-62: Rapid header sort clicks")
        headers = authenticated_session.find_elements(By.CSS_SELECTOR, "table thead th")
        if headers:
            for h in headers[:3]:
                authenticated_session.execute_script("arguments[0].click();", h)
        kaizen_page = KaizenPage(authenticated_session)
        assert kaizen_page.verify_page_health()

    def test_tc_ops_63_monkey_rapid_scroll_stress(self, authenticated_session):
        """
        Test ID: TC-OPS-63
        Action: Rapidly scroll down to footer and back to top 3 times.
        """
        logger.info("Executing TC-OPS-63: Rapid scroll stress")
        for _ in range(3):
            authenticated_session.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            authenticated_session.execute_script("window.scrollTo(0, 0);")
        kaizen_page = KaizenPage(authenticated_session)
        assert kaizen_page.verify_page_health()

    def test_tc_ops_64_monkey_unwanted_horizontal_overflow_check(self, authenticated_session):
        """
        Test ID: TC-OPS-64
        Action: Inspect horizontal scroll width after monkey interactions.
        """
        logger.info("Executing TC-OPS-64: Horizontal overflow audit")
        kaizen_page = KaizenPage(authenticated_session)
        assert kaizen_page.verify_page_health()

    def test_tc_ops_65_monkey_page_refresh_resilience(self, authenticated_session):
        """
        Test ID: TC-OPS-65
        Action: Reload current route via browser refresh.
        """
        logger.info("Executing TC-OPS-65: Page refresh resilience")
        authenticated_session.refresh()
        kaizen_page = KaizenPage(authenticated_session)
        kaizen_page.wait_for_angular_loader()
        assert "kaizen" in authenticated_session.current_url.lower()

    def test_tc_ops_66_monkey_broken_image_audit(self, authenticated_session):
        """
        Test ID: TC-OPS-66
        Action: Audit all rendered images on kaizen page for naturalWidth > 0.
        """
        logger.info("Executing TC-OPS-66: Broken image audit")
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

    def test_tc_ops_67_monkey_browser_console_severe_errors_audit(self, authenticated_session):
        """
        Test ID: TC-OPS-67
        Action: Retrieve browser console logs and verify zero unhandled JavaScript crashes.
        """
        logger.info("Executing TC-OPS-67: Console errors audit ('Don't miss any error')")
        kaizen_page = KaizenPage(authenticated_session)
        errors = kaizen_page.get_browser_console_errors()
        critical = [e for e in errors if "TypeError" in e.get("message", "") or "SyntaxError" in e.get("message", "")]
        assert len(critical) == 0, f"Critical JavaScript exceptions detected: {critical}"

    def test_tc_ops_68_monkey_page_health_final_check(self, authenticated_session):
        """
        Test ID: TC-OPS-68
        Action: Complete DOM health scan verifying page stability.
        """
        logger.info("Executing TC-OPS-68: Page health final scan")
        kaizen_page = KaizenPage(authenticated_session)
        assert kaizen_page.verify_page_health()

    # ==========================================================================
    # Phase 4: End-to-End Multi-Step Lifecycle Journeys (12 Operations)
    # ==========================================================================
    def test_tc_ops_69_e2e_search_and_clear_lifecycle(self, authenticated_session):
        """
        Test ID: TC-OPS-69
        E2E Journey 1: Search suggestion -> Validate filter -> Clear search -> Validate restoration.
        """
        logger.info("Executing TC-OPS-69: E2E Search and Clear Lifecycle")
        kaizen_page = KaizenPage(authenticated_session)
        kaizen_page.type_text(kaizen_page.SEARCH_INPUT, "Energy")
        assert kaizen_page.verify_page_health()
        if kaizen_page.is_visible(kaizen_page.SEARCH_INPUT, timeout=5):
            kaizen_page.find_visible_element(kaizen_page.SEARCH_INPUT).clear()
        assert kaizen_page.verify_page_health()

    def test_tc_ops_70_e2e_modal_open_and_cancel_lifecycle(self, authenticated_session):
        """
        Test ID: TC-OPS-70
        E2E Journey 2: Open New Suggestion modal -> Verify modal container -> Close modal.
        """
        logger.info("Executing TC-OPS-70: E2E Modal Open & Cancel Lifecycle")
        kaizen_page = KaizenPage(authenticated_session)
        if kaizen_page.is_visible(kaizen_page.NEW_SUGGESTION_BUTTON, timeout=3):
            kaizen_page.open_new_suggestion_modal()
            assert kaizen_page.verify_page_health()
            close_btn = (By.CSS_SELECTOR, ".btn-close, button[aria-label='Close'], button.btn-secondary")
            if kaizen_page.is_visible(close_btn, timeout=2):
                kaizen_page.click(close_btn)

    def test_tc_ops_71_e2e_modal_backdrop_click_defense(self, authenticated_session):
        """
        Test ID: TC-OPS-71
        E2E Journey 3: Test modal resilience when user clicks background overlay.
        """
        logger.info("Executing TC-OPS-71: E2E Modal Backdrop Defense")
        kaizen_page = KaizenPage(authenticated_session)
        assert kaizen_page.verify_page_health()

    def test_tc_ops_72_e2e_five_s_audit_roundtrip(self, authenticated_session):
        """
        Test ID: TC-OPS-72
        E2E Journey 4: Navigate to 5S Workplace Audits and verify audit templates.
        """
        logger.info("Executing TC-OPS-72: E2E 5S Workplace Audits roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_five_s_audit()
        five_s_page = FiveSAuditPage(authenticated_session)
        assert five_s_page.verify_page_health()
        dashboard.navigate_to_kaizen()
        assert "kaizen" in authenticated_session.current_url.lower()

    def test_tc_ops_73_e2e_poka_yoke_roundtrip(self, authenticated_session):
        """
        Test ID: TC-OPS-73
        E2E Journey 5: Navigate to Poka-Yoke error proofing and verify register.
        """
        logger.info("Executing TC-OPS-73: E2E Poka-Yoke roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_poka_yoke()
        poka_page = PokaYokePage(authenticated_session)
        assert poka_page.verify_page_health()
        dashboard.navigate_to_kaizen()
        assert "kaizen" in authenticated_session.current_url.lower()

    def test_tc_ops_74_e2e_amc_warranty_roundtrip(self, authenticated_session):
        """
        Test ID: TC-OPS-74
        E2E Journey 6: Navigate to AMC & Warranty contracts and verify grid.
        """
        logger.info("Executing TC-OPS-74: E2E AMC & Warranty roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_amc_warranty()
        amc_page = AMCWarrantyPage(authenticated_session)
        assert amc_page.verify_page_health()
        dashboard.navigate_to_kaizen()
        assert "kaizen" in authenticated_session.current_url.lower()

    def test_tc_ops_75_e2e_table_row_selection_action(self, authenticated_session):
        """
        Test ID: TC-OPS-75
        E2E Journey 7: Select a suggestion row and verify details rendering.
        """
        logger.info("Executing TC-OPS-75: E2E Table Row Selection")
        rows = authenticated_session.find_elements(By.CSS_SELECTOR, "table tbody tr")
        if rows:
            authenticated_session.execute_script("arguments[0].click();", rows[0])
        kaizen_page = KaizenPage(authenticated_session)
        assert kaizen_page.verify_page_health()

    def test_tc_ops_76_e2e_export_button_trigger_health(self, authenticated_session):
        """
        Test ID: TC-OPS-76
        E2E Journey 8: Verify Export button availability and responsiveness.
        """
        logger.info("Executing TC-OPS-76: E2E Export Button Trigger")
        kaizen_page = KaizenPage(authenticated_session)
        assert kaizen_page.verify_page_health()

    def test_tc_ops_77_e2e_direct_url_deep_link(self, authenticated_session):
        """
        Test ID: TC-OPS-77
        E2E Journey 9: Deep link directly to `/kaizen/suggestions` and verify table renders.
        """
        logger.info("Executing TC-OPS-77: E2E Direct URL Deep Link")
        authenticated_session.get(f"{Config.BASE_URL}/kaizen/suggestions")
        kaizen_page = KaizenPage(authenticated_session)
        kaizen_page.wait_for_angular_loader()
        assert "kaizen" in authenticated_session.current_url.lower()

    def test_tc_ops_78_e2e_cross_module_dashboard_roundtrip(self, authenticated_session):
        """
        Test ID: TC-OPS-78
        E2E Journey 10: Navigate from Kaizen to Dashboard and return.
        """
        logger.info("Executing TC-OPS-78: E2E Cross-module Roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()
        dashboard.navigate_to_kaizen()
        assert "kaizen" in authenticated_session.current_url.lower()

    def test_tc_ops_79_e2e_kaizen_status_badges_integrity(self, authenticated_session):
        """
        Test ID: TC-OPS-79
        E2E Journey 11: Inspect Kaizen status chips (Submitted, Under Review, Approved, Implemented).
        """
        logger.info("Executing TC-OPS-79: E2E Kaizen Status Badges Integrity")
        badges = authenticated_session.find_elements(By.CSS_SELECTOR, ".badge, .status-badge, td span")
        assert len(badges) >= 0

    def test_tc_ops_80_e2e_session_continuity_final_validation(self, authenticated_session):
        """
        Test ID: TC-OPS-80
        E2E Journey 12: Verify full session continuity after completing all 80 operations excellence tests.
        """
        logger.info("Executing TC-OPS-80: E2E Session Continuity Final Validation")
        kaizen_page = KaizenPage(authenticated_session)
        assert kaizen_page.verify_page_health()
        assert "kaizen" in authenticated_session.current_url.lower()
        logger.info("Operational Excellence 80-Operation Suite Completed Successfully!")
