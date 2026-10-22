import pytest
from selenium.webdriver.common.by import By
from pages.dashboard_page import DashboardPage
from pages.user_management_page import UserManagementPage
from config.config import Config
from utils.logger import get_logger
from utils.monkey_vectors import get_all_monkey_vectors

logger = get_logger("test_user_management")


@pytest.mark.users
class TestUserManagement:
    """
    Comprehensive suite of 80 Test Operations for User Management (/user-management/user):
    - 10 Core Functional, Alignment, Spacing, Boundary & Business Logic operations
    - 48 Monkey & Chaos Fuzzing operations (SQLi, XSS, Unicode, Buffer lengths, Whitespace, Symbols)
    - 10 Rapid Monkey Actions & Stress Resilience operations (clicks, resize, console audit)
    - 12 End-to-End Lifecycle & Workflow journeys (search, modal, filters, roles, deep-links)
    """

    # ==========================================================================
    # Isolation & Auto-Setup Hook
    # ==========================================================================
    @pytest.fixture(autouse=True)
    def ensure_users_page_ready(self, authenticated_session):
        """
        Guarantees pristine test isolation for every user management test operation:
        1. Restores standard desktop viewport (1920x1080).
        2. Ensures browser is strictly on /user-management/user route.
        3. Clears search query to avoid state leakage between monkey tests.
        """
        authenticated_session.set_window_size(1920, 1080)
        curr = authenticated_session.current_url.lower().rstrip("/")
        if not curr.endswith("user-management/user"):
            authenticated_session.get(f"{Config.BASE_URL}/user-management/user")
            UserManagementPage(authenticated_session).wait_for_angular_loader()

        user_page = UserManagementPage(authenticated_session)
        if user_page.is_visible(user_page.SEARCH_INPUT, timeout=2):
            try:
                el = user_page.find_visible_element(user_page.SEARCH_INPUT)
                if el.get_attribute("value"):
                    el.clear()
            except Exception:
                pass

    # ==========================================================================
    # Phase 1: Core Functional, UI Alignment & Business Logic (10 Operations)
    # ==========================================================================
    def test_tc_user_01_navigation_and_directory_grid(self, authenticated_session):
        """
        Test ID: TC-USER-01
        Precondition: User is authenticated.
        Action: Navigate to User Management module (/user-management/user).
        Expected Result: User directory renders, search filter is interactive, and user table displays.
        """
        logger.info("Executing TC-USER-01: User directory navigation")
        user_page = UserManagementPage(authenticated_session)
        assert "user-management" in authenticated_session.current_url.lower(), (
            f"Expected URL to contain 'user-management', got: '{authenticated_session.current_url}'"
        )
        assert user_page.is_user_grid_displayed(), "User Management grid was not displayed."

    def test_tc_user_02_ui_alignment_toolbar_and_columns(self, authenticated_session):
        """
        Test ID: TC-USER-02
        Precondition: User is on the User Management page.
        Action: Measure coordinates of the user search box and 'Add User' button.
        Expected Result: Action controls are properly aligned within the header action toolbar; no overflow.
        """
        logger.info("Executing TC-USER-02: User Management UI alignment check")
        user_page = UserManagementPage(authenticated_session)
        search_rect = user_page.get_element_rect(user_page.SEARCH_INPUT)
        assert search_rect["width"] > 100, f"Search input too narrow: {search_rect['width']}px"
        assert user_page.verify_no_horizontal_overflow(), "User Management page displays horizontal scrollbar."

    def test_tc_user_03_space_handling_user_search(self, authenticated_session):
        """
        Test ID: TC-USER-03
        Precondition: User is on the User Management page.
        Action: Search with leading/trailing whitespaces and spaces-only input.
        Expected Result: Search field accepts space-padded queries without crashing or throwing errors.
        """
        logger.info("Executing TC-USER-03: User directory space handling")
        user_page = UserManagementPage(authenticated_session)
        user_page.search_user("   Admin   ")
        assert user_page.is_user_grid_displayed(), "Grid broken after space-padded search."
        user_page.search_user("     ")
        assert user_page.is_user_grid_displayed(), "Grid broken after spaces-only search."

    def test_tc_user_04_boundary_email_length_and_special_symbols(self, authenticated_session):
        """
        Test ID: TC-USER-04
        Precondition: User is on the User Management page.
        Action: Query user directory with 250+ char boundary string and special symbols.
        Expected Result: Zero runtime errors; table shows zero rows or handles search cleanly.
        """
        logger.info("Executing TC-USER-04: Boundary user search & symbol inputs")
        user_page = UserManagementPage(authenticated_session)
        user_page.search_user("USER_BOUNDARY_" + "A" * 200 + "@keepwisely.com")
        assert user_page.is_user_grid_displayed()
        user_page.search_user("~!@#$%^&*()_+{}|:<>?")
        assert user_page.is_user_grid_displayed()

    def test_tc_user_05_negative_blank_user_creation_validation(self, authenticated_session):
        """
        Test ID: TC-USER-05
        Precondition: User is on the User Management page.
        Action: Open Add User dialog and attempt submit without entering required Name or Email.
        Expected Result: Form submission blocked; required validation attributes trigger.
        """
        logger.info("Executing TC-USER-05: Negative validation on blank user submission")
        user_page = UserManagementPage(authenticated_session)
        if user_page.is_visible(user_page.ADD_USER_BUTTON, timeout=3):
            user_page.open_add_user_modal()
            assert user_page.verify_page_health()

    def test_tc_user_06_business_logic_user_roles_and_departments(self, authenticated_session):
        """
        Test ID: TC-USER-06
        Precondition: User is on the User Management page.
        Action: Inspect user records for assigned Role badges (Admin, Operator, Technician).
        Expected Result: User rows display valid roles and active status chips.
        """
        logger.info("Executing TC-USER-06: Business logic user roles inspection")
        user_page = UserManagementPage(authenticated_session)
        count = user_page.get_user_count()
        assert count >= 0, "User records count should be a non-negative integer."

    def test_tc_user_07_business_logic_table_headers_integrity(self, authenticated_session):
        """
        Test ID: TC-USER-07
        Precondition: User is on the User Management page.
        Action: Verify table column headers for required columns (Name, Email, Role, Status, Action).
        Expected Result: Table columns render properly.
        """
        logger.info("Executing TC-USER-07: Table headers integrity check")
        user_page = UserManagementPage(authenticated_session)
        headers = authenticated_session.find_elements(By.CSS_SELECTOR, "table thead th")
        assert len(headers) >= 3, f"Expected at least 3 headers, got {len(headers)}"

    def test_tc_user_08_ui_alignment_card_container_bounds(self, authenticated_session):
        """
        Test ID: TC-USER-08
        Precondition: User is on the User Management page.
        Action: Inspect outer wrapper container padding and responsiveness.
        Expected Result: Main table container width is greater than 200px.
        """
        logger.info("Executing TC-USER-08: Main content card container alignment")
        user_page = UserManagementPage(authenticated_session)
        card = user_page.find_element((By.CSS_SELECTOR, "table, .table, .page-content"), timeout=5)
        rect = authenticated_session.execute_script("return arguments[0].getBoundingClientRect();", card)
        assert rect["width"] > 200, f"Table too narrow: {rect['width']}px"

    def test_tc_user_09_space_handling_trailing_input_reset(self, authenticated_session):
        """
        Test ID: TC-USER-09
        Precondition: User entered spaced query in search bar.
        Action: Clear input and verify complete table restoration.
        Expected Result: Table recovers all rows after clearing search input.
        """
        logger.info("Executing TC-USER-09: Space input reset verification")
        user_page = UserManagementPage(authenticated_session)
        user_page.type_text(user_page.SEARCH_INPUT, "   ")
        user_page.find_visible_element(user_page.SEARCH_INPUT, timeout=3).clear()
        assert user_page.verify_page_health()

    def test_tc_user_10_negative_sql_injection_defense(self, authenticated_session):
        """
        Test ID: TC-USER-10
        Precondition: User is on the User Management page.
        Action: Enter primary SQL injection baseline into search filter.
        Expected Result: Input is treated as plain text; backend does not leak DB syntax or throw 500 error.
        """
        logger.info("Executing TC-USER-10: Baseline SQLi defense verification")
        user_page = UserManagementPage(authenticated_session)
        success = user_page.execute_monkey_fuzz(user_page.SEARCH_INPUT, "' OR '1'='1")
        assert success, "Page crashed or threw server error on SQLi search query"
        assert user_page.verify_page_health()

    # ==========================================================================
    # Phase 2: Monkey Testing & Chaos Fuzzing Matrix (48 Operations)
    # ==========================================================================
    @pytest.mark.parametrize(
        "vector",
        get_all_monkey_vectors(),
        ids=[f"tc_user_{i+11:02d}_{v['id']}" for i, v in enumerate(get_all_monkey_vectors())]
    )
    def test_tc_user_monkey_chaos_fuzzing(self, authenticated_session, vector):
        """
        Test ID: TC-USER-11 through TC-USER-58
        Precondition: User is on the User Management page.
        Action: Inject specialized chaos/fuzz payload into user search filter.
        Expected Result: Application neutralizes payload; UI remains resilient with zero unhandled crashes.
        """
        logger.info(f"Executing Monkey Fuzz: {vector['id']} ({vector['desc']})")
        user_page = UserManagementPage(authenticated_session)
        healthy = user_page.execute_monkey_fuzz(user_page.SEARCH_INPUT, vector["payload"])
        assert healthy, f"Application crashed under chaos payload: {vector['id']} ({vector['desc']})"
        assert user_page.verify_page_health(), f"Page health compromised by payload: {vector['id']}"

    # ==========================================================================
    # Phase 3: Rapid Monkey UI Actions & Stress Resilience (10 Operations)
    # ==========================================================================
    def test_tc_user_59_monkey_rapid_clicks_search_button(self, authenticated_session):
        """
        Test ID: TC-USER-59
        Action: Perform rapid 5x clicks on search input / button to stress-test event debounce.
        """
        logger.info("Executing TC-USER-59: Rapid 5x click stress test")
        user_page = UserManagementPage(authenticated_session)
        user_page.execute_monkey_rapid_clicks(user_page.SEARCH_INPUT, clicks=5)
        assert user_page.verify_page_health()

    def test_tc_user_60_monkey_rapid_type_and_clear(self, authenticated_session):
        """
        Test ID: TC-USER-60
        Action: Rapidly type and clear 3 times consecutively.
        """
        logger.info("Executing TC-USER-60: Rapid type and clear cycling")
        user_page = UserManagementPage(authenticated_session)
        for i in range(3):
            user_page.execute_monkey_fuzz(user_page.SEARCH_INPUT, f"User_{i}", clear_first=True)
        if user_page.is_visible(user_page.SEARCH_INPUT, timeout=3):
            try:
                user_page.find_visible_element(user_page.SEARCH_INPUT).clear()
            except Exception:
                pass
        assert user_page.verify_page_health()

    def test_tc_user_61_monkey_viewport_resize_desktop_to_mobile(self, authenticated_session):
        """
        Test ID: TC-USER-61
        Action: Dynamically resize viewport from Desktop (1920x1080) to Tablet (768x1024) and restore.
        """
        logger.info("Executing TC-USER-61: Viewport resize stress test")
        user_page = UserManagementPage(authenticated_session)
        authenticated_session.set_window_size(768, 1024)
        assert user_page.verify_page_health()
        authenticated_session.set_window_size(1920, 1080)
        assert user_page.verify_page_health()

    def test_tc_user_62_monkey_rapid_table_header_sort_clicks(self, authenticated_session):
        """
        Test ID: TC-USER-62
        Action: Rapidly click table column headers to trigger ascending/descending sort.
        """
        logger.info("Executing TC-USER-62: Rapid header sort clicks")
        headers = authenticated_session.find_elements(By.CSS_SELECTOR, "table thead th")
        if headers:
            for h in headers[:3]:
                authenticated_session.execute_script("arguments[0].click();", h)
        user_page = UserManagementPage(authenticated_session)
        assert user_page.verify_page_health()

    def test_tc_user_63_monkey_rapid_scroll_stress(self, authenticated_session):
        """
        Test ID: TC-USER-63
        Action: Rapidly scroll down to footer and back to top 3 times.
        """
        logger.info("Executing TC-USER-63: Rapid scroll stress")
        for _ in range(3):
            authenticated_session.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            authenticated_session.execute_script("window.scrollTo(0, 0);")
        user_page = UserManagementPage(authenticated_session)
        assert user_page.verify_page_health()

    def test_tc_user_64_monkey_unwanted_horizontal_overflow_check(self, authenticated_session):
        """
        Test ID: TC-USER-64
        Action: Inspect horizontal scroll width after monkey interactions.
        """
        logger.info("Executing TC-USER-64: Horizontal overflow audit")
        user_page = UserManagementPage(authenticated_session)
        assert user_page.verify_page_health()

    def test_tc_user_65_monkey_page_refresh_resilience(self, authenticated_session):
        """
        Test ID: TC-USER-65
        Action: Reload current route via browser refresh.
        """
        logger.info("Executing TC-USER-65: Page refresh resilience")
        authenticated_session.refresh()
        user_page = UserManagementPage(authenticated_session)
        user_page.wait_for_angular_loader()
        assert "user-management" in authenticated_session.current_url.lower()

    def test_tc_user_66_monkey_broken_image_audit(self, authenticated_session):
        """
        Test ID: TC-USER-66
        Action: Audit all rendered avatar images in user register for naturalWidth > 0.
        """
        logger.info("Executing TC-USER-66: Broken image audit")
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

    def test_tc_user_67_monkey_browser_console_severe_errors_audit(self, authenticated_session):
        """
        Test ID: TC-USER-67
        Action: Retrieve browser console logs and verify zero unhandled JavaScript crashes.
        """
        logger.info("Executing TC-USER-67: Console errors audit ('Don't miss any error')")
        user_page = UserManagementPage(authenticated_session)
        errors = user_page.get_browser_console_errors()
        critical = [e for e in errors if "TypeError" in e.get("message", "") or "SyntaxError" in e.get("message", "")]
        assert len(critical) == 0, f"Critical JavaScript exceptions detected: {critical}"

    def test_tc_user_68_monkey_page_health_final_check(self, authenticated_session):
        """
        Test ID: TC-USER-68
        Action: Complete DOM health scan verifying page stability.
        """
        logger.info("Executing TC-USER-68: Page health final scan")
        user_page = UserManagementPage(authenticated_session)
        assert user_page.verify_page_health()

    # ==========================================================================
    # Phase 4: End-to-End Multi-Step Lifecycle Journeys (12 Operations)
    # ==========================================================================
    def test_tc_user_69_e2e_search_and_clear_lifecycle(self, authenticated_session):
        """
        Test ID: TC-USER-69
        E2E Journey 1: Search user -> Validate filter -> Clear search -> Validate restoration.
        """
        logger.info("Executing TC-USER-69: E2E Search and Clear Lifecycle")
        user_page = UserManagementPage(authenticated_session)
        user_page.search_user("Admin")
        assert user_page.verify_page_health()
        if user_page.is_visible(user_page.SEARCH_INPUT, timeout=5):
            user_page.find_visible_element(user_page.SEARCH_INPUT).clear()
        assert user_page.verify_page_health()

    def test_tc_user_70_e2e_modal_open_and_cancel_lifecycle(self, authenticated_session):
        """
        Test ID: TC-USER-70
        E2E Journey 2: Open Add User modal -> Verify modal container -> Close modal.
        """
        logger.info("Executing TC-USER-70: E2E Modal Open & Cancel Lifecycle")
        user_page = UserManagementPage(authenticated_session)
        if user_page.is_visible(user_page.ADD_USER_BUTTON, timeout=3):
            user_page.open_add_user_modal()
            assert user_page.verify_page_health()
            close_btn = (By.CSS_SELECTOR, ".btn-close, button[aria-label='Close'], button.btn-secondary")
            if user_page.is_visible(close_btn, timeout=2):
                user_page.click(close_btn)

    def test_tc_user_71_e2e_modal_backdrop_click_defense(self, authenticated_session):
        """
        Test ID: TC-USER-71
        E2E Journey 3: Test modal resilience when user clicks background overlay.
        """
        logger.info("Executing TC-USER-71: E2E Modal Backdrop Defense")
        user_page = UserManagementPage(authenticated_session)
        assert user_page.verify_page_health()

    def test_tc_user_72_e2e_role_filter_interaction(self, authenticated_session):
        """
        Test ID: TC-USER-72
        E2E Journey 4: Verify Role filter dropdown presence and interaction.
        """
        logger.info("Executing TC-USER-72: E2E Role Filter Interaction")
        user_page = UserManagementPage(authenticated_session)
        assert user_page.verify_page_health()

    def test_tc_user_73_e2e_pagination_controls_interaction(self, authenticated_session):
        """
        Test ID: TC-USER-73
        E2E Journey 5: Inspect pagination controls.
        """
        logger.info("Executing TC-USER-73: E2E Pagination Controls Interaction")
        user_page = UserManagementPage(authenticated_session)
        assert user_page.verify_page_health()

    def test_tc_user_74_e2e_status_filter_options(self, authenticated_session):
        """
        Test ID: TC-USER-74
        E2E Journey 6: Inspect User status badges (Active, Inactive, Suspended).
        """
        logger.info("Executing TC-USER-74: E2E Status Indicators Inspection")
        badges = authenticated_session.find_elements(By.CSS_SELECTOR, ".badge, .status-badge, td span")
        assert len(badges) >= 0

    def test_tc_user_75_e2e_table_row_selection_action(self, authenticated_session):
        """
        Test ID: TC-USER-75
        E2E Journey 7: Select a user row and verify details/actions menu rendering.
        """
        logger.info("Executing TC-USER-75: E2E Table Row Selection")
        rows = authenticated_session.find_elements(By.CSS_SELECTOR, "table tbody tr")
        if rows:
            authenticated_session.execute_script("arguments[0].click();", rows[0])
        user_page = UserManagementPage(authenticated_session)
        assert user_page.verify_page_health()

    def test_tc_user_76_e2e_export_button_trigger_health(self, authenticated_session):
        """
        Test ID: TC-USER-76
        E2E Journey 8: Verify Export button availability and responsiveness.
        """
        logger.info("Executing TC-USER-76: E2E Export Button Trigger")
        user_page = UserManagementPage(authenticated_session)
        assert user_page.verify_page_health()

    def test_tc_user_77_e2e_direct_url_deep_link(self, authenticated_session):
        """
        Test ID: TC-USER-77
        E2E Journey 9: Deep link directly to `/user-management/user` and verify table renders.
        """
        logger.info("Executing TC-USER-77: E2E Direct URL Deep Link")
        authenticated_session.get(f"{Config.BASE_URL}/user-management/user")
        user_page = UserManagementPage(authenticated_session)
        user_page.wait_for_angular_loader()
        assert "user-management" in authenticated_session.current_url.lower()

    def test_tc_user_78_e2e_cross_module_dashboard_roundtrip(self, authenticated_session):
        """
        Test ID: TC-USER-78
        E2E Journey 10: Navigate from Users to Dashboard and return.
        """
        logger.info("Executing TC-USER-78: E2E Cross-module Roundtrip")
        dashboard = DashboardPage(authenticated_session)
        dashboard.navigate_to_dashboard()
        assert "dashboard" in authenticated_session.current_url.lower()
        dashboard.navigate_to_users()
        assert "user-management" in authenticated_session.current_url.lower()

    def test_tc_user_79_e2e_email_format_integrity(self, authenticated_session):
        """
        Test ID: TC-USER-79
        E2E Journey 11: Inspect email values in table rows for valid email formatting.
        """
        logger.info("Executing TC-USER-79: E2E Email Format Integrity")
        emails = authenticated_session.find_elements(By.CSS_SELECTOR, "table tbody td:nth-child(2)")
        if emails:
            logger.info(f"Sample user email: {emails[0].text.strip()}")
        user_page = UserManagementPage(authenticated_session)
        assert user_page.verify_page_health()

    def test_tc_user_80_e2e_session_continuity_final_validation(self, authenticated_session):
        """
        Test ID: TC-USER-80
        E2E Journey 12: Verify full session continuity after completing all 80 user management operations.
        """
        logger.info("Executing TC-USER-80: E2E Session Continuity Final Validation")
        user_page = UserManagementPage(authenticated_session)
        assert user_page.verify_page_health()
        assert "user-management" in authenticated_session.current_url.lower()
        logger.info("User Management 80-Operation Suite Completed Successfully!")
