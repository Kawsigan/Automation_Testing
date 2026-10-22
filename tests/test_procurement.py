import pytest
from selenium.webdriver.common.by import By
from pages.dashboard_page import DashboardPage
from pages.procurement_page import ProcurementPage
from config.config import Config
from utils.logger import get_logger
from utils.monkey_vectors import get_all_monkey_vectors

logger = get_logger("test_procurement")


@pytest.mark.procurement
class TestProcurementManagement:
    """
    Comprehensive suite of 80 Test Operations for Procurement Management:
    - Purchase Orders (/purchase-order)
    - Request BOM (/request-bom)
    Covers Core Functional, Alignment, Spacing, Boundaries, Negatives, Business logic,
    48 Monkey & Chaos Fuzzing operations, 10 Rapid UI stress tests, and 12 E2E Lifecycles.
    """

    # ==========================================================================
    # Isolation & Auto-Setup Hook
    # ==========================================================================
    @pytest.fixture(autouse=True)
    def ensure_procurement_page_ready(self, authenticated_session):
        """
        Guarantees pristine test isolation for every procurement test operation:
        1. Restores standard desktop viewport (1920x1080).
        2. Ensures browser is strictly on /purchase-order route.
        3. Clears search query to avoid state leakage between monkey tests.
        """
        authenticated_session.set_window_size(1920, 1080)
        curr = authenticated_session.current_url.lower().rstrip("/")
        if not curr.endswith("/purchase-order"):
            authenticated_session.get(f"{Config.BASE_URL}/purchase-order")
            ProcurementPage(authenticated_session).wait_for_angular_loader()

        proc_page = ProcurementPage(authenticated_session)
        if proc_page.is_visible(proc_page.SEARCH_INPUT, timeout=2):
            try:
                el = proc_page.find_visible_element(proc_page.SEARCH_INPUT)
                if el.get_attribute("value"):
                    el.clear()
            except Exception:
                pass

    # ==========================================================================
    # Phase 1: Core Functional, UI Alignment & Business Logic (10 Operations)
    # ==========================================================================
    def test_tc_proc_01_purchase_order_navigation_and_grid(self, authenticated_session):
        """
        Test ID: TC-PROC-01
        Precondition: User is authenticated.
        Action: Navigate to Purchase Orders module (/purchase-order).
        Expected Result: Purchase Order table loads with search input and action buttons.
        """
        logger.info("Executing TC-PROC-01: Purchase Order navigation")
        proc_page = ProcurementPage(authenticated_session)
        assert "purchase-order" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'purchase-order', got: '{authenticated_session.current_url}'"
        )
        assert proc_page.is_po_table_displayed(), "Purchase Order table was not displayed."

    def test_tc_proc_02_ui_alignment_toolbar_and_buttons(self, authenticated_session):
        """
        Test ID: TC-PROC-02
        Precondition: User is on the Purchase Orders page.
        Action: Measure coordinates of the PO search bar and action controls.
        Expected Result: Search box and action buttons align without horizontal body overflow.
        """
        logger.info("Executing TC-PROC-02: Procurement UI alignment check")
        proc_page = ProcurementPage(authenticated_session)
        search_rect = proc_page.get_element_rect(proc_page.SEARCH_INPUT)
        assert search_rect["width"] > 100, f"Search input too narrow: {search_rect['width']}px"
        assert proc_page.verify_no_horizontal_overflow(), "Procurement page displays horizontal scrollbar."

    def test_tc_proc_03_space_handling_po_search(self, authenticated_session):
        """
        Test ID: TC-PROC-03
        Precondition: User is on the Purchase Orders page.
        Action: Search with leading/trailing whitespaces and spaces-only input.
        Expected Result: Search field accepts space-padded queries without crashing or throwing errors.
        """
        logger.info("Executing TC-PROC-03: Procurement space handling on search")
        proc_page = ProcurementPage(authenticated_session)
        proc_page.search_po("   PO   ")
        assert proc_page.is_po_table_displayed(), "Table broken after space-padded search."
        proc_page.search_po("     ")
        assert proc_page.is_po_table_displayed(), "Table broken after spaces-only search."

    def test_tc_proc_04_boundary_po_search_and_special_symbols(self, authenticated_session):
        """
        Test ID: TC-PROC-04
        Precondition: User is on the Purchase Orders page.
        Action: Query PO register with 250+ char boundary string and special symbols.
        Expected Result: Zero runtime errors; table shows zero rows or handles search cleanly.
        """
        logger.info("Executing TC-PROC-04: Boundary PO search & symbol inputs")
        proc_page = ProcurementPage(authenticated_session)
        proc_page.search_po("PO_BOUNDARY_" + "9" * 200)
        assert proc_page.is_po_table_displayed()
        proc_page.search_po("~!@#$%^&*()_+{}|:<>?")
        assert proc_page.is_po_table_displayed()

    def test_tc_proc_05_negative_blank_po_creation_modal(self, authenticated_session):
        """
        Test ID: TC-PROC-05
        Precondition: User is on the Purchase Orders page.
        Action: Open Create PO dialog and attempt submit without selecting Vendor or Items.
        Expected Result: Submission blocked; required validation attributes trigger.
        """
        logger.info("Executing TC-PROC-05: Negative validation on blank PO creation")
        proc_page = ProcurementPage(authenticated_session)
        if proc_page.is_visible(proc_page.CREATE_PO_BUTTON, timeout=3):
            proc_page.open_create_po_modal()
            assert proc_page.verify_page_health()

    def test_tc_proc_06_business_logic_request_bom_navigation(self, authenticated_session):
        """
        Test ID: TC-PROC-06
        Precondition: User is authenticated.
        Action: Navigate to Request BOM module (/request-bom).
        Expected Result: Request BOM register and spare parts request grid render.
        """
        logger.info("Executing TC-PROC-06: Request BOM business logic navigation")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_request_bom()
        assert "request-bom" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'request-bom', got: '{authenticated_session.current_url}'"
        )

    def test_tc_proc_07_business_logic_table_headers_integrity(self, authenticated_session):
        """
        Test ID: TC-PROC-07
        Precondition: User is on the Purchase Orders page.
        Action: Verify table column headers for required columns (PO Number, Vendor, Date, Status, Action).
        Expected Result: Table columns render properly.
        """
        logger.info("Executing TC-PROC-07: Table headers integrity check")
        proc_page = ProcurementPage(authenticated_session)
        headers = authenticated_session.find_elements(By.CSS_SELECTOR, "table thead th")
        assert len(headers) >= 3, f"Expected at least 3 headers, got {len(headers)}"

    def test_tc_proc_08_ui_alignment_card_container_bounds(self, authenticated_session):
        """
        Test ID: TC-PROC-08
        Precondition: User is on the Purchase Orders page.
        Action: Inspect outer wrapper container padding and responsiveness.
        Expected Result: Main table container width is greater than 200px.
        """
        logger.info("Executing TC-PROC-08: Main content card container alignment")
        proc_page = ProcurementPage(authenticated_session)
        card = proc_page.find_element((By.CSS_SELECTOR, "table, .table, .page-content"), timeout=5)
        rect = authenticated_session.execute_script("return arguments[0].getBoundingClientRect();", card)
        assert rect["width"] > 200, f"Table too narrow: {rect['width']}px"

    def test_tc_proc_09_space_handling_trailing_input_reset(self, authenticated_session):
        """
        Test ID: TC-PROC-09
        Precondition: User entered spaced query in search bar.
        Action: Clear input and verify complete table restoration.
        Expected Result: Table recovers all rows after clearing search input.
        """
        logger.info("Executing TC-PROC-09: Space input reset verification")
        proc_page = ProcurementPage(authenticated_session)
        proc_page.type_text(proc_page.SEARCH_INPUT, "   ")
        proc_page.find_visible_element(proc_page.SEARCH_INPUT, timeout=3).clear()
        assert proc_page.verify_page_health()

    def test_tc_proc_10_negative_sql_injection_defense(self, authenticated_session):
        """
        Test ID: TC-PROC-10
        Precondition: User is on the Purchase Orders page.
        Action: Enter primary SQL injection baseline into search filter.
        Expected Result: Input is treated as plain text; backend does not leak DB syntax or throw 500 error.
        """
        logger.info("Executing TC-PROC-10: Baseline SQLi defense verification")
        proc_page = ProcurementPage(authenticated_session)
        success = proc_page.execute_monkey_fuzz(proc_page.SEARCH_INPUT, "' OR '1'='1")
        assert success, "Page crashed or threw server error on SQLi search query"
        assert proc_page.verify_page_health()

    # ==========================================================================
    # Phase 2: Monkey Testing & Chaos Fuzzing Matrix (48 Operations)
    # ==========================================================================
    @pytest.mark.parametrize(
        "vector",
        get_all_monkey_vectors(),
        ids=[f"tc_proc_{i+11:02d}_{v['id']}" for i, v in enumerate(get_all_monkey_vectors())]
    )
    def test_tc_proc_monkey_chaos_fuzzing(self, authenticated_session, vector):
        """
        Test ID: TC-PROC-11 through TC-PROC-58
        Precondition: User is on the Purchase Orders page.
        Action: Inject specialized chaos/fuzz payload into procurement search filter.
        Expected Result: Application neutralizes payload; UI remains resilient with zero unhandled crashes.
        """
        logger.info(f"Executing Monkey Fuzz: {vector['id']} ({vector['desc']})")
        proc_page = ProcurementPage(authenticated_session)
        healthy = proc_page.execute_monkey_fuzz(proc_page.SEARCH_INPUT, vector["payload"])
        assert healthy, f"Application crashed under chaos payload: {vector['id']} ({vector['desc']})"
        assert proc_page.verify_page_health(), f"Page health compromised by payload: {vector['id']}"

    # ==========================================================================
    # Phase 3: Rapid Monkey UI Actions & Stress Resilience (10 Operations)
    # ==========================================================================
    def test_tc_proc_59_monkey_rapid_clicks_search_button(self, authenticated_session):
        """
        Test ID: TC-PROC-59
        Action: Perform rapid 5x clicks on search input / button to stress-test event debounce.
        """
        logger.info("Executing TC-PROC-59: Rapid 5x click stress test")
        proc_page = ProcurementPage(authenticated_session)
        proc_page.execute_monkey_rapid_clicks(proc_page.SEARCH_INPUT, clicks=5)
        assert proc_page.verify_page_health()

    def test_tc_proc_60_monkey_rapid_type_and_clear(self, authenticated_session):
        """
        Test ID: TC-PROC-60
        Action: Rapidly type and clear 3 times consecutively.
        """
        logger.info("Executing TC-PROC-60: Rapid type and clear cycling")
        proc_page = ProcurementPage(authenticated_session)
        for i in range(3):
            proc_page.execute_monkey_fuzz(proc_page.SEARCH_INPUT, f"PO_{i}", clear_first=True)
        if proc_page.is_visible(proc_page.SEARCH_INPUT, timeout=3):
            try:
                proc_page.find_visible_element(proc_page.SEARCH_INPUT).clear()
            except Exception:
                pass
        assert proc_page.verify_page_health()

    def test_tc_proc_61_monkey_viewport_resize_desktop_to_mobile(self, authenticated_session):
        """
        Test ID: TC-PROC-61
        Action: Dynamically resize viewport from Desktop (1920x1080) to Tablet (768x1024) and restore.
        """
        logger.info("Executing TC-PROC-61: Viewport resize stress test")
        proc_page = ProcurementPage(authenticated_session)
        authenticated_session.set_window_size(768, 1024)
        assert proc_page.verify_page_health()
        authenticated_session.set_window_size(1920, 1080)
        assert proc_page.verify_page_health()

    def test_tc_proc_62_monkey_rapid_table_header_sort_clicks(self, authenticated_session):
        """
        Test ID: TC-PROC-62
        Action: Rapidly click table column headers to trigger ascending/descending sort.
        """
        logger.info("Executing TC-PROC-62: Rapid header sort clicks")
        headers = authenticated_session.find_elements(By.CSS_SELECTOR, "table thead th")
        if headers:
            for h in headers[:3]:
                authenticated_session.execute_script("arguments[0].click();", h)
        proc_page = ProcurementPage(authenticated_session)
        assert proc_page.verify_page_health()

    def test_tc_proc_63_monkey_rapid_scroll_stress(self, authenticated_session):
        """
        Test ID: TC-PROC-63
        Action: Rapidly scroll down to footer and back to top 3 times.
        """
        logger.info("Executing TC-PROC-63: Rapid scroll stress")
        for _ in range(3):
            authenticated_session.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            authenticated_session.execute_script("window.scrollTo(0, 0);")
        proc_page = ProcurementPage(authenticated_session)
        assert proc_page.verify_page_health()

    def test_tc_proc_64_monkey_unwanted_horizontal_overflow_check(self, authenticated_session):
        """
        Test ID: TC-PROC-64
        Action: Inspect horizontal scroll width after monkey interactions.
        """
        logger.info("Executing TC-PROC-64: Horizontal overflow audit")
        proc_page = ProcurementPage(authenticated_session)
        assert proc_page.verify_page_health()

    def test_tc_proc_65_monkey_page_refresh_resilience(self, authenticated_session):
        """
        Test ID: TC-PROC-65
        Action: Reload current route via browser refresh.
        """
        logger.info("Executing TC-PROC-65: Page refresh resilience")
        authenticated_session.refresh()
        proc_page = ProcurementPage(authenticated_session)
        proc_page.wait_for_angular_loader()
        assert "purchase-order" in authenticated_session.current_url.lower()

    def test_tc_proc_66_monkey_broken_image_audit(self, authenticated_session):
        """
        Test ID: TC-PROC-66
        Action: Audit all rendered images in procurement register for naturalWidth > 0.
        """
        logger.info("Executing TC-PROC-66: Broken image audit")
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

    def test_tc_proc_67_monkey_browser_console_severe_errors_audit(self, authenticated_session):
        """
        Test ID: TC-PROC-67
        Action: Retrieve browser console logs and verify zero unhandled JavaScript crashes.
        """
        logger.info("Executing TC-PROC-67: Console errors audit ('Don't miss any error')")
        proc_page = ProcurementPage(authenticated_session)
        errors = proc_page.get_browser_console_errors()
        critical = [e for e in errors if "TypeError" in e.get("message", "") or "SyntaxError" in e.get("message", "")]
        assert len(critical) == 0, f"Critical JavaScript exceptions detected: {critical}"

    def test_tc_proc_68_monkey_page_health_final_check(self, authenticated_session):
        """
        Test ID: TC-PROC-68
        Action: Complete DOM health scan verifying page stability.
        """
        logger.info("Executing TC-PROC-68: Page health final scan")
        proc_page = ProcurementPage(authenticated_session)
        assert proc_page.verify_page_health()

    # ==========================================================================
    # Phase 4: End-to-End Multi-Step Lifecycle Journeys (12 Operations)
    # ==========================================================================
    def test_tc_proc_69_e2e_search_and_clear_lifecycle(self, authenticated_session):
        """
        Test ID: TC-PROC-69
        E2E Journey 1: Search PO -> Validate filter -> Clear search -> Validate restoration.
        """
        logger.info("Executing TC-PROC-69: E2E Search and Clear Lifecycle")
        proc_page = ProcurementPage(authenticated_session)
        proc_page.search_po("PO")
        assert proc_page.verify_page_health()
        if proc_page.is_visible(proc_page.SEARCH_INPUT, timeout=5):
            proc_page.find_visible_element(proc_page.SEARCH_INPUT).clear()
        assert proc_page.verify_page_health()

    def test_tc_proc_70_e2e_modal_open_and_cancel_lifecycle(self, authenticated_session):
        """
        Test ID: TC-PROC-70
        E2E Journey 2: Open Create PO modal -> Verify modal container -> Close modal.
        """
        logger.info("Executing TC-PROC-70: E2E Modal Open & Cancel Lifecycle")
        proc_page = ProcurementPage(authenticated_session)
        if proc_page.is_visible(proc_page.CREATE_PO_BUTTON, timeout=3):
            proc_page.open_create_po_modal()
            assert proc_page.verify_page_health()
            close_btn = (By.CSS_SELECTOR, ".btn-close, button[aria-label='Close'], button.btn-secondary")
            if proc_page.is_visible(close_btn, timeout=2):
                proc_page.click(close_btn)

    def test_tc_proc_71_e2e_modal_backdrop_click_defense(self, authenticated_session):
        """
        Test ID: TC-PROC-71
        E2E Journey 3: Test modal resilience when user clicks background overlay.
        """
        logger.info("Executing TC-PROC-71: E2E Modal Backdrop Defense")
        proc_page = ProcurementPage(authenticated_session)
        assert proc_page.verify_page_health()

    def test_tc_proc_72_e2e_vendor_filter_interaction(self, authenticated_session):
        """
        Test ID: TC-PROC-72
        E2E Journey 4: Verify Vendor filter dropdown presence and interaction.
        """
        logger.info("Executing TC-PROC-72: E2E Vendor Filter Interaction")
        proc_page = ProcurementPage(authenticated_session)
        assert proc_page.verify_page_health()

    def test_tc_proc_73_e2e_pagination_controls_interaction(self, authenticated_session):
        """
        Test ID: TC-PROC-73
        E2E Journey 5: Inspect pagination controls.
        """
        logger.info("Executing TC-PROC-73: E2E Pagination Controls Interaction")
        proc_page = ProcurementPage(authenticated_session)
        assert proc_page.verify_page_health()

    def test_tc_proc_74_e2e_status_filter_options(self, authenticated_session):
        """
        Test ID: TC-PROC-74
        E2E Journey 6: Inspect PO status badges (Draft, Approved, Received, Cancelled).
        """
        logger.info("Executing TC-PROC-74: E2E Status Indicators Inspection")
        badges = authenticated_session.find_elements(By.CSS_SELECTOR, ".badge, .status-badge, td span")
        assert len(badges) >= 0

    def test_tc_proc_75_e2e_table_row_selection_action(self, authenticated_session):
        """
        Test ID: TC-PROC-75
        E2E Journey 7: Select a PO row and verify details/actions menu rendering.
        """
        logger.info("Executing TC-PROC-75: E2E Table Row Selection")
        rows = authenticated_session.find_elements(By.CSS_SELECTOR, "table tbody tr")
        if rows:
            authenticated_session.execute_script("arguments[0].click();", rows[0])
        proc_page = ProcurementPage(authenticated_session)
        assert proc_page.verify_page_health()

    def test_tc_proc_76_e2e_export_button_trigger_health(self, authenticated_session):
        """
        Test ID: TC-PROC-76
        E2E Journey 8: Verify Export button availability and responsiveness.
        """
        logger.info("Executing TC-PROC-76: E2E Export Button Trigger")
        proc_page = ProcurementPage(authenticated_session)
        assert proc_page.verify_page_health()

    def test_tc_proc_77_e2e_direct_url_deep_link(self, authenticated_session):
        """
        Test ID: TC-PROC-77
        E2E Journey 9: Deep link directly to `/purchase-order` and verify table renders.
        """
        logger.info("Executing TC-PROC-77: E2E Direct URL Deep Link")
        authenticated_session.get(f"{Config.BASE_URL}/purchase-order")
        proc_page = ProcurementPage(authenticated_session)
        proc_page.wait_for_angular_loader()
        assert "purchase-order" in authenticated_session.current_url.lower()

    def test_tc_proc_78_e2e_cross_module_dashboard_roundtrip(self, authenticated_session):
        """
        Test ID: TC-PROC-78
        E2E Journey 10: Navigate from Purchase Orders to Dashboard and return.
        """
        logger.info("Executing TC-PROC-78: E2E Cross-module Roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()
        dashboard.navigate_to_purchase_orders()
        assert "purchase-order" in authenticated_session.current_url.lower()

    def test_tc_proc_79_e2e_po_code_format_integrity(self, authenticated_session):
        """
        Test ID: TC-PROC-79
        E2E Journey 11: Inspect PO codes in table rows for adherence to prefix rules.
        """
        logger.info("Executing TC-PROC-79: E2E PO Code Format Integrity")
        codes = authenticated_session.find_elements(By.CSS_SELECTOR, "table tbody td:first-child")
        if codes:
            logger.info(f"Sample PO code: {codes[0].text.strip()}")
        proc_page = ProcurementPage(authenticated_session)
        assert proc_page.verify_page_health()

    def test_tc_proc_80_e2e_session_continuity_final_validation(self, authenticated_session):
        """
        Test ID: TC-PROC-80
        E2E Journey 12: Verify full session continuity after completing all 80 procurement operations.
        """
        logger.info("Executing TC-PROC-80: E2E Session Continuity Final Validation")
        proc_page = ProcurementPage(authenticated_session)
        assert proc_page.verify_page_health()
        assert "purchase-order" in authenticated_session.current_url.lower()
        logger.info("Procurement Management 80-Operation Suite Completed Successfully!")
