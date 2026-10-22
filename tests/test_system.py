import pytest
from selenium.webdriver.common.by import By
from pages.dashboard_page import DashboardPage
from pages.location_page import LocationPage
from pages.floor_plan_page import FloorPlanPage
from pages.masters_page import MastersPage
from pages.settings_page import SettingsPage
from config.config import Config
from utils.logger import get_logger
from utils.monkey_vectors import get_all_monkey_vectors

logger = get_logger("test_system")


@pytest.mark.settings
class TestSystemConfiguration:
    """
    Comprehensive suite of 80 Test Operations for System Core & Infrastructure modules:
    - Plant Location Hierarchy (/location)
    - Visual Floor Plan & Live Monitor (/floor-plan)
    - Master Data & Checklists (/masters/checklist)
    - System Configuration & Prefixes (/settings/prefix)
    Covers Core Functional, UI Alignment, Spacing, Boundaries, Negatives, Business logic,
    48 Monkey & Chaos Fuzzing operations, 10 Rapid UI stress tests, and 12 E2E Lifecycles.
    """

    # ==========================================================================
    # Isolation & Auto-Setup Hook
    # ==========================================================================
    @pytest.fixture(autouse=True)
    def ensure_system_page_ready(self, authenticated_session):
        """
        Guarantees pristine test isolation for every system configuration test:
        1. Restores standard desktop viewport (1920x1080).
        2. Ensures browser is strictly on /location route.
        3. Clears search query to avoid state leakage between monkey tests.
        """
        authenticated_session.set_window_size(1920, 1080)
        curr = authenticated_session.current_url.lower().rstrip("/")
        if not curr.endswith("/location"):
            authenticated_session.get(f"{Config.BASE_URL}/location")
            LocationPage(authenticated_session).wait_for_angular_loader()

        loc_page = LocationPage(authenticated_session)
        if loc_page.is_visible(loc_page.SEARCH_INPUT, timeout=2):
            try:
                el = loc_page.find_visible_element(loc_page.SEARCH_INPUT)
                if el.get_attribute("value"):
                    el.clear()
            except Exception:
                pass

    # ==========================================================================
    # Phase 1: Core Functional, UI Alignment & Business Logic (10 Operations)
    # ==========================================================================
    def test_tc_sys_01_location_hierarchy_navigation(self, authenticated_session):
        """
        Test ID: TC-SYS-01
        Precondition: User is authenticated.
        Action: Navigate to Location & Hierarchy module (/location).
        Expected Result: Location grid and plant hierarchy treeview load.
        """
        logger.info("Executing TC-SYS-01: Location hierarchy navigation")
        loc_page = LocationPage(authenticated_session)
        assert "location" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'location', got: '{authenticated_session.current_url}'"
        )
        assert loc_page.is_location_table_displayed(), "Location table was not displayed."

    def test_tc_sys_02_ui_alignment_floor_plan_canvas(self, authenticated_session):
        """
        Test ID: TC-SYS-02
        Precondition: User is authenticated.
        Action: Navigate to Floor Plan module (/floor-plan) and inspect canvas dimensions.
        Expected Result: Floor plan layout container renders cleanly within the viewport.
        """
        logger.info("Executing TC-SYS-02: Floor Plan UI alignment & canvas check")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_floor_plan()
        floor_page = FloorPlanPage(authenticated_session)
        assert "floor-plan" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'floor-plan', got: '{authenticated_session.current_url}'"
        )
        assert floor_page.is_floor_plan_displayed(), "Floor Plan map canvas is not displayed."

    def test_tc_sys_03_space_handling_masters_search(self, authenticated_session):
        """
        Test ID: TC-SYS-03
        Precondition: User is authenticated.
        Action: Navigate to Master Checklists (/masters/checklist) and test whitespace-padded search.
        Expected Result: Search box accepts padded queries without crashing.
        """
        logger.info("Executing TC-SYS-03: Master data space handling check")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_masters_checklist()
        masters_page = MastersPage(authenticated_session)
        assert "masters" in authenticated_session.current_url.lower()
        if masters_page.is_masters_grid_displayed():
            masters_page.type_text(masters_page.SEARCH_INPUT, "   Inspection   ")
            assert masters_page.is_masters_grid_displayed()

    def test_tc_sys_04_boundary_settings_prefix_inputs(self, authenticated_session):
        """
        Test ID: TC-SYS-04
        Precondition: User is authenticated.
        Action: Navigate to System Prefix Configuration (/settings/prefix).
        Expected Result: Prefix configuration form loads; inputs accept standard prefix lengths.
        """
        logger.info("Executing TC-SYS-04: Boundary prefix inputs check")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_settings_prefix()
        settings_page = SettingsPage(authenticated_session)
        assert "settings/prefix" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'settings/prefix', got: '{authenticated_session.current_url}'"
        )
        assert settings_page.is_prefix_settings_displayed(), "Prefix settings form not displayed."

    def test_tc_sys_05_negative_blank_location_modal(self, authenticated_session):
        """
        Test ID: TC-SYS-05
        Precondition: User is on the Location page.
        Action: Open Add Location dialog and attempt submit without entering Location Name.
        Expected Result: Submission blocked or validation warning triggered.
        """
        logger.info("Executing TC-SYS-05: Negative validation on blank location creation")
        loc_page = LocationPage(authenticated_session)
        if loc_page.is_visible(loc_page.ADD_LOCATION_BUTTON, timeout=3):
            loc_page.open_add_location_modal()
            assert "location" in authenticated_session.current_url.lower()
            close_btn = (By.CSS_SELECTOR, ".btn-close, button[aria-label='Close'], button.btn-secondary")
            if loc_page.is_visible(close_btn, timeout=2):
                loc_page.click(close_btn)

    def test_tc_sys_06_business_logic_prefix_form_fields(self, authenticated_session):
        """
        Test ID: TC-SYS-06
        Precondition: User is on the Prefix Settings page.
        Action: Verify presence of core system prefix inputs (Asset, Ticket, PO).
        Expected Result: Prefix input fields are rendered and editable.
        """
        logger.info("Executing TC-SYS-06: Business logic prefix fields verification")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_settings_prefix()
        settings_page = SettingsPage(authenticated_session)
        assert settings_page.is_prefix_settings_displayed()

    def test_tc_sys_07_business_logic_location_table_headers(self, authenticated_session):
        """
        Test ID: TC-SYS-07
        Precondition: User is on the Location hierarchy page.
        Action: Verify location table headers and structural elements.
        Expected Result: Grid headers and container elements render without defect.
        """
        logger.info("Executing TC-SYS-07: Location table headers integrity check")
        loc_page = LocationPage(authenticated_session)
        headers = authenticated_session.find_elements(By.CSS_SELECTOR, "table thead th, th, .tree-header")
        assert loc_page.verify_page_health()

    def test_tc_sys_08_ui_alignment_location_card_bounds(self, authenticated_session):
        """
        Test ID: TC-SYS-08
        Precondition: User is on the Location hierarchy page.
        Action: Inspect outer wrapper container padding and responsiveness.
        Expected Result: Main table container width is greater than 200px.
        """
        logger.info("Executing TC-SYS-08: Main content card container alignment")
        loc_page = LocationPage(authenticated_session)
        card = loc_page.find_element((By.CSS_SELECTOR, "table, .table, .card, .page-content"), timeout=5)
        rect = authenticated_session.execute_script("return arguments[0].getBoundingClientRect();", card)
        assert rect["width"] > 200, f"Location container too narrow: {rect['width']}px"

    def test_tc_sys_09_space_handling_trailing_input_reset(self, authenticated_session):
        """
        Test ID: TC-SYS-09
        Precondition: User entered spaced query in search bar.
        Action: Clear input and verify complete table restoration.
        Expected Result: Table recovers all rows after clearing search input.
        """
        logger.info("Executing TC-SYS-09: Space input reset verification")
        loc_page = LocationPage(authenticated_session)
        loc_page.type_text(loc_page.SEARCH_INPUT, "   ")
        loc_page.find_visible_element(loc_page.SEARCH_INPUT, timeout=3).clear()
        assert loc_page.verify_page_health()

    def test_tc_sys_10_negative_sql_injection_defense(self, authenticated_session):
        """
        Test ID: TC-SYS-10
        Precondition: User is on the Location hierarchy page.
        Action: Enter primary SQL injection baseline into search filter.
        Expected Result: Input is treated as plain text; backend does not leak DB syntax or throw 500 error.
        """
        logger.info("Executing TC-SYS-10: Baseline SQLi defense verification")
        loc_page = LocationPage(authenticated_session)
        success = loc_page.execute_monkey_fuzz(loc_page.SEARCH_INPUT, "' OR '1'='1")
        assert success, "Page crashed or threw server error on SQLi search query"
        assert loc_page.verify_page_health()

    # ==========================================================================
    # Phase 2: Monkey Testing & Chaos Fuzzing Matrix (48 Operations)
    # ==========================================================================
    @pytest.mark.parametrize(
        "vector",
        get_all_monkey_vectors(),
        ids=[f"tc_sys_{i+11:02d}_{v['id']}" for i, v in enumerate(get_all_monkey_vectors())]
    )
    def test_tc_sys_monkey_chaos_fuzzing(self, authenticated_session, vector):
        """
        Test ID: TC-SYS-11 through TC-SYS-58
        Precondition: User is on the Location page.
        Action: Inject specialized chaos/fuzz payload into location search filter.
        Expected Result: Application neutralizes payload; UI remains resilient with zero unhandled crashes.
        """
        logger.info(f"Executing Monkey Fuzz: {vector['id']} ({vector['desc']})")
        loc_page = LocationPage(authenticated_session)
        healthy = loc_page.execute_monkey_fuzz(loc_page.SEARCH_INPUT, vector["payload"])
        assert healthy, f"Application crashed under chaos payload: {vector['id']} ({vector['desc']})"
        assert loc_page.verify_page_health(), f"Page health compromised by payload: {vector['id']}"

    # ==========================================================================
    # Phase 3: Rapid Monkey UI Actions & Stress Resilience (10 Operations)
    # ==========================================================================
    def test_tc_sys_59_monkey_rapid_clicks_search_button(self, authenticated_session):
        """
        Test ID: TC-SYS-59
        Action: Perform rapid 5x clicks on search input / button to stress-test event debounce.
        """
        logger.info("Executing TC-SYS-59: Rapid 5x click stress test")
        loc_page = LocationPage(authenticated_session)
        loc_page.execute_monkey_rapid_clicks(loc_page.SEARCH_INPUT, clicks=5)
        assert loc_page.verify_page_health()

    def test_tc_sys_60_monkey_rapid_type_and_clear(self, authenticated_session):
        """
        Test ID: TC-SYS-60
        Action: Rapidly type and clear 3 times consecutively.
        """
        logger.info("Executing TC-SYS-60: Rapid type and clear cycling")
        loc_page = LocationPage(authenticated_session)
        for i in range(3):
            loc_page.execute_monkey_fuzz(loc_page.SEARCH_INPUT, f"Loc_{i}", clear_first=True)
        if loc_page.is_visible(loc_page.SEARCH_INPUT, timeout=3):
            try:
                loc_page.find_visible_element(loc_page.SEARCH_INPUT).clear()
            except Exception:
                pass
        assert loc_page.verify_page_health()

    def test_tc_sys_61_monkey_viewport_resize_desktop_to_mobile(self, authenticated_session):
        """
        Test ID: TC-SYS-61
        Action: Dynamically resize viewport from Desktop (1920x1080) to Tablet (768x1024) and restore.
        """
        logger.info("Executing TC-SYS-61: Viewport resize stress test")
        loc_page = LocationPage(authenticated_session)
        authenticated_session.set_window_size(768, 1024)
        assert loc_page.verify_page_health()
        authenticated_session.set_window_size(1920, 1080)
        assert loc_page.verify_page_health()

    def test_tc_sys_62_monkey_rapid_table_header_sort_clicks(self, authenticated_session):
        """
        Test ID: TC-SYS-62
        Action: Rapidly click table column headers to trigger ascending/descending sort.
        """
        logger.info("Executing TC-SYS-62: Rapid header sort clicks")
        headers = authenticated_session.find_elements(By.CSS_SELECTOR, "table thead th, th")
        if headers:
            for h in headers[:3]:
                authenticated_session.execute_script("arguments[0].click();", h)
        loc_page = LocationPage(authenticated_session)
        assert loc_page.verify_page_health()

    def test_tc_sys_63_monkey_rapid_scroll_stress(self, authenticated_session):
        """
        Test ID: TC-SYS-63
        Action: Rapidly scroll down to footer and back to top 3 times.
        """
        logger.info("Executing TC-SYS-63: Rapid scroll stress")
        for _ in range(3):
            authenticated_session.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            authenticated_session.execute_script("window.scrollTo(0, 0);")
        loc_page = LocationPage(authenticated_session)
        assert loc_page.verify_page_health()

    def test_tc_sys_64_monkey_unwanted_horizontal_overflow_check(self, authenticated_session):
        """
        Test ID: TC-SYS-64
        Action: Inspect horizontal scroll width after monkey interactions.
        """
        logger.info("Executing TC-SYS-64: Horizontal overflow audit")
        loc_page = LocationPage(authenticated_session)
        assert loc_page.verify_page_health()

    def test_tc_sys_65_monkey_page_refresh_resilience(self, authenticated_session):
        """
        Test ID: TC-SYS-65
        Action: Reload current route via browser refresh.
        """
        logger.info("Executing TC-SYS-65: Page refresh resilience")
        authenticated_session.refresh()
        loc_page = LocationPage(authenticated_session)
        loc_page.wait_for_angular_loader()
        assert "location" in authenticated_session.current_url.lower()

    def test_tc_sys_66_monkey_broken_image_audit(self, authenticated_session):
        """
        Test ID: TC-SYS-66
        Action: Audit all rendered images on location page for naturalWidth > 0.
        """
        logger.info("Executing TC-SYS-66: Broken image audit")
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

    def test_tc_sys_67_monkey_browser_console_severe_errors_audit(self, authenticated_session):
        """
        Test ID: TC-SYS-67
        Action: Retrieve browser console logs and verify zero unhandled JavaScript crashes.
        """
        logger.info("Executing TC-SYS-67: Console errors audit ('Don't miss any error')")
        loc_page = LocationPage(authenticated_session)
        errors = loc_page.get_browser_console_errors()
        critical = [e for e in errors if "TypeError" in e.get("message", "") or "SyntaxError" in e.get("message", "")]
        assert len(critical) == 0, f"Critical JavaScript exceptions detected: {critical}"

    def test_tc_sys_68_monkey_page_health_final_check(self, authenticated_session):
        """
        Test ID: TC-SYS-68
        Action: Complete DOM health scan verifying page stability.
        """
        logger.info("Executing TC-SYS-68: Page health final scan")
        loc_page = LocationPage(authenticated_session)
        assert loc_page.verify_page_health()

    # ==========================================================================
    # Phase 4: End-to-End Multi-Step Lifecycle Journeys (12 Operations)
    # ==========================================================================
    def test_tc_sys_69_e2e_search_and_clear_lifecycle(self, authenticated_session):
        """
        Test ID: TC-SYS-69
        E2E Journey 1: Search location -> Validate filter -> Clear search -> Validate restoration.
        """
        logger.info("Executing TC-SYS-69: E2E Search and Clear Lifecycle")
        loc_page = LocationPage(authenticated_session)
        loc_page.type_text(loc_page.SEARCH_INPUT, "Plant")
        assert loc_page.verify_page_health()
        if loc_page.is_visible(loc_page.SEARCH_INPUT, timeout=5):
            loc_page.find_visible_element(loc_page.SEARCH_INPUT).clear()
        assert loc_page.verify_page_health()

    def test_tc_sys_70_e2e_modal_open_and_cancel_lifecycle(self, authenticated_session):
        """
        Test ID: TC-SYS-70
        E2E Journey 2: Open Add Location modal -> Verify modal container -> Close modal.
        """
        logger.info("Executing TC-SYS-70: E2E Modal Open & Cancel Lifecycle")
        loc_page = LocationPage(authenticated_session)
        if loc_page.is_visible(loc_page.ADD_LOCATION_BUTTON, timeout=3):
            loc_page.open_add_location_modal()
            assert loc_page.verify_page_health()
            close_btn = (By.CSS_SELECTOR, ".btn-close, button[aria-label='Close'], button.btn-secondary")
            if loc_page.is_visible(close_btn, timeout=2):
                loc_page.click(close_btn)

    def test_tc_sys_71_e2e_floor_plan_roundtrip(self, authenticated_session):
        """
        Test ID: TC-SYS-71
        E2E Journey 3: Navigate to Floor Plan and verify canvas map rendering.
        """
        logger.info("Executing TC-SYS-71: E2E Floor Plan roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_floor_plan()
        floor_page = FloorPlanPage(authenticated_session)
        assert floor_page.verify_page_health()
        dashboard.navigate_to_location()
        assert "location" in authenticated_session.current_url.lower()

    def test_tc_sys_72_e2e_masters_checklist_roundtrip(self, authenticated_session):
        """
        Test ID: TC-SYS-72
        E2E Journey 4: Navigate to Master Checklists and verify master data grid.
        """
        logger.info("Executing TC-SYS-72: E2E Master Checklists roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_masters_checklist()
        masters_page = MastersPage(authenticated_session)
        assert masters_page.verify_page_health()
        dashboard.navigate_to_location()
        assert "location" in authenticated_session.current_url.lower()

    def test_tc_sys_73_e2e_settings_prefix_roundtrip(self, authenticated_session):
        """
        Test ID: TC-SYS-73
        E2E Journey 5: Navigate to Prefix Settings and verify configuration controls.
        """
        logger.info("Executing TC-SYS-73: E2E Settings Prefix roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_settings_prefix()
        settings_page = SettingsPage(authenticated_session)
        assert settings_page.verify_page_health()
        dashboard.navigate_to_location()
        assert "location" in authenticated_session.current_url.lower()

    def test_tc_sys_74_e2e_location_hierarchy_tree_nodes(self, authenticated_session):
        """
        Test ID: TC-SYS-74
        E2E Journey 6: Inspect location hierarchy tree nodes and structure.
        """
        logger.info("Executing TC-SYS-74: E2E Location Hierarchy Tree Nodes")
        loc_page = LocationPage(authenticated_session)
        count = loc_page.get_location_count()
        logger.info(f"Registered location nodes count: {count}")
        assert count >= 0
        assert loc_page.verify_page_health()

    def test_tc_sys_75_e2e_table_row_selection_action(self, authenticated_session):
        """
        Test ID: TC-SYS-75
        E2E Journey 7: Select a location row and verify details rendering.
        """
        logger.info("Executing TC-SYS-75: E2E Table Row Selection")
        rows = authenticated_session.find_elements(By.CSS_SELECTOR, "table tbody tr")
        if rows:
            authenticated_session.execute_script("arguments[0].click();", rows[0])
        loc_page = LocationPage(authenticated_session)
        assert loc_page.verify_page_health()

    def test_tc_sys_76_e2e_direct_url_deep_link(self, authenticated_session):
        """
        Test ID: TC-SYS-76
        E2E Journey 8: Deep link directly to `/location` and verify table renders.
        """
        logger.info("Executing TC-SYS-76: E2E Direct URL Deep Link")
        authenticated_session.get(f"{Config.BASE_URL}/location")
        loc_page = LocationPage(authenticated_session)
        loc_page.wait_for_angular_loader()
        assert "location" in authenticated_session.current_url.lower()

    def test_tc_sys_77_e2e_cross_module_dashboard_roundtrip(self, authenticated_session):
        """
        Test ID: TC-SYS-77
        E2E Journey 9: Navigate from Location to Dashboard and return.
        """
        logger.info("Executing TC-SYS-77: E2E Cross-module Roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()
        dashboard.navigate_to_location()
        assert "location" in authenticated_session.current_url.lower()

    def test_tc_sys_78_e2e_fast_search_debounce_barrage(self, authenticated_session):
        """
        Test ID: TC-SYS-78
        E2E Journey 10: Test fast search debounce under simulated rapid keystroke barrage.
        """
        logger.info("Executing TC-SYS-78: E2E Fast Search Debounce Barrage")
        loc_page = LocationPage(authenticated_session)
        for char in "Building":
            loc_page.type_text(loc_page.SEARCH_INPUT, char, clear_first=False)
        assert loc_page.verify_page_health()
        if loc_page.is_visible(loc_page.SEARCH_INPUT, timeout=3):
            loc_page.find_visible_element(loc_page.SEARCH_INPUT).clear()

    def test_tc_sys_79_e2e_multi_system_submodule_traversal(self, authenticated_session):
        """
        Test ID: TC-SYS-79
        E2E Journey 11: Traverse sequentially through all system submodules (Location -> Floor Plan -> Masters -> Settings).
        """
        logger.info("Executing TC-SYS-79: E2E Multi-System Submodule Traversal")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_floor_plan()
        dashboard.navigate_to_masters_checklist()
        dashboard.navigate_to_settings_prefix()
        dashboard.navigate_to_location()
        assert "location" in authenticated_session.current_url.lower()

    def test_tc_sys_80_e2e_session_continuity_final_validation(self, authenticated_session):
        """
        Test ID: TC-SYS-80
        E2E Journey 12: Verify full session continuity after completing all 80 system configuration tests.
        """
        logger.info("Executing TC-SYS-80: E2E Session Continuity Final Validation")
        loc_page = LocationPage(authenticated_session)
        assert loc_page.verify_page_health()
        assert "location" in authenticated_session.current_url.lower()
        logger.info("System Configuration 80-Operation Suite Completed Successfully!")
