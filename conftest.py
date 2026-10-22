import base64
import os
import shutil
from datetime import datetime
from pathlib import Path
import pytest
from config.config import Config
from utils.driver_factory import DriverFactory
from utils.logger import get_logger

logger = get_logger("conftest")


def pytest_addoption(parser):
    """
    Register command line arguments for Pytest.
    """
    parser.addoption(
        "--browser",
        action="store",
        default=None,
        help="Target browser: chrome, firefox, or edge (overrides .env)"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=None,
        help="Run browser in headless mode (overrides .env)"
    )


from utils.report_portal import ReportPortal

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """
    Configure Pytest environment and ensure single unified website-level report target:
    1. Ensures reports and screenshots directories exist.
    2. Directs output strictly to the single unified report file (reports/report.html).
    3. Initializes the ReportPortal in-memory test collector and execution timer.
    """
    Config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    Config.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    # Enforce single unified report path - prevents creation of multiple cluttered files
    single_report_path = Config.REPORTS_DIR / "report.html"
    config.option.htmlpath = str(single_report_path)
    config._report_portal_tests = []
    config._report_portal_start_time = datetime.now()

    logger.info(f"Report target configured to single unified portal: {single_report_path}")

    # Populate metadata table in pytest-html report via pytest-metadata stash
    try:
        from pytest_metadata.plugin import metadata_key
        if metadata_key in config.stash:
            metadata = config.stash[metadata_key]
            metadata["Application"] = "Keepwisely CMMS"
            metadata["Base URL"] = Config.BASE_URL
            metadata["Target Browser"] = (config.getoption("--browser") or Config.BROWSER).capitalize()
            metadata["Execution Mode"] = "Headless" if (config.getoption("--headless") or Config.HEADLESS) else "Headed"
            metadata["Environment"] = "Staging / Production (app.keepwisely.com)"
            metadata["Execution Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Remove noisy environment variables from report view
            for redundant_key in ["JAVA_HOME", "Packages", "Plugins"]:
                metadata.pop(redundant_key, None)
    except Exception as e:
        logger.debug(f"Could not configure pytest metadata stash: {e}")


def pytest_html_report_title(report):
    """
    Set custom title for the report.
    """
    report.title = "Keepwisely CMMS - Test Execution Report"


def pytest_html_results_summary(prefix, summary, postfix, session):
    """
    Append an executive summary card to the top of the report.
    """
    browser_val = (session.config.getoption("--browser") or Config.BROWSER).capitalize()
    headless_val = session.config.getoption("--headless") or Config.HEADLESS
    prefix.append(
        "<div style='margin-bottom: 20px; padding: 16px 20px; background: linear-gradient(135deg, #1e293b, #0f172a); "
        "border-radius: 8px; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif; "
        "box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);'>"
        "<div style='font-size: 20px; font-weight: 700; color: #38bdf8; margin-bottom: 6px;'>"
        "Keepwisely CMMS Test Automation Suite"
        "</div>"
        "<div style='font-size: 13px; color: #94a3b8; line-height: 1.6;'>"
        f"Target Application: <strong style='color:#f1f5f9;'>{Config.BASE_URL}</strong> &nbsp;|&nbsp; "
        f"Browser: <strong style='color:#f1f5f9;'>{browser_val}</strong> &nbsp;|&nbsp; "
        f"Headless Mode: <strong style='color:#f1f5f9;'>{headless_val}</strong> &nbsp;|&nbsp; "
        f"Report Generated: <strong style='color:#f1f5f9;'>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</strong>"
        "</div>"
        "</div>"
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_sessionfinish(session, exitstatus):
    """
    Post-execution hook:
    Renders the website-level single executive report into reports/report.html
    merging with persistent module cache so all modules remain present in the single report.
    """
    yield
    try:
        import json
        single_path = Config.REPORTS_DIR / "report.html"
        cache_path = Config.REPORTS_DIR / ".report_portal_cache.json"
        collected_tests = getattr(session.config, "_report_portal_tests", [])

        # Load existing cached tests across modules if available
        all_tests_map = {}
        if cache_path.exists():
            try:
                cached_data = json.loads(cache_path.read_text(encoding="utf-8"))
                for t in cached_data.get("tests", []):
                    all_tests_map[t.get("node_id", t.get("test_id"))] = t
            except Exception:
                pass

        # Update with newly executed tests from this session
        for t in collected_tests:
            all_tests_map[t.get("node_id", t.get("test_id"))] = t

        # Calculate session execution duration
        start_time = getattr(session.config, "_report_portal_start_time", datetime.now())
        total_seconds = (datetime.now() - start_time).total_seconds()
        mins, secs = divmod(int(total_seconds), 60)
        duration_display = f"{mins:02d}m {secs:02d}s" if mins > 0 else f"{total_seconds:.2f}s"

        browser_val = (session.config.getoption("--browser") or Config.BROWSER).capitalize()
        headless_val = "Headless" if (session.config.getoption("--headless") or Config.HEADLESS) else "Headed"

        tests_to_render = list(all_tests_map.values()) if all_tests_map else collected_tests

        if tests_to_render:
            report_data = {
                "metadata": {
                    "base_url": Config.BASE_URL,
                    "browser": browser_val,
                    "mode": headless_val,
                    "execution_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_duration": duration_display,
                },
                "tests": tests_to_render,
            }
            # Save persistent cache
            cache_path.write_text(json.dumps(report_data, indent=2), encoding="utf-8")

            # Render website portal
            ReportPortal.save_report(report_data, single_path)
            logger.info(f"Website-level single executive report generated at: {single_path} ({len(tests_to_render)} tests across modules)")

        # Clean up any accidental timestamped files in reports folder
        for extra_report in Config.REPORTS_DIR.glob("report_*.html"):
            try:
                extra_report.unlink()
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Failed to generate website-level single executive report: {e}")


@pytest.fixture(scope="function")
def driver(request):
    """
    Pytest fixture that initializes WebDriver before each test function
    and safely terminates the browser session after execution.
    """
    # Read CLI options if provided, otherwise fallback to Config / .env
    cli_browser = request.config.getoption("--browser")
    cli_headless = request.config.getoption("--headless")

    browser_name = cli_browser if cli_browser is not None else Config.BROWSER
    headless = cli_headless if cli_headless is not None else Config.HEADLESS

    # Initialize WebDriver via Selenium 4 Driver Factory
    web_driver = DriverFactory.get_driver(browser_name=browser_name, headless=headless)

    # Attach driver to request node for screenshot hook access on failure
    request.node.driver = web_driver

    logger.info(f"Starting test: {request.node.name}")
    yield web_driver

    # Teardown: Safely quit the browser
    logger.info(f"Closing browser session for test: {request.node.name}")
    try:
        web_driver.quit()
    except Exception as e:
        logger.error(f"Error while quitting WebDriver: {e}")


@pytest.fixture(scope="function")
def authenticated_driver(driver):
    """
    Pytest fixture providing an authenticated WebDriver session on the Dashboard.
    Skips test if valid credentials are not configured in .env.
    """
    if (
        not Config.ADMIN_USERNAME
        or not Config.ADMIN_PASSWORD
        or "SampleTest" in Config.ADMIN_PASSWORD
        or "YourPassword" in Config.ADMIN_PASSWORD
    ):
        pytest.skip("Valid staging credentials not configured in .env.")

    from pages.login_page import LoginPage
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login(Config.ADMIN_USERNAME, Config.ADMIN_PASSWORD)
    login_page.wait_for_login_redirect()
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook executed after each test phase (setup, call, teardown).
    1. Distinguishes functional test failures from infrastructure/environment errors.
    2. Captures browser failure screenshots for browser-based tests.
    3. Feeds structured, non-tech friendly data into the ReportPortal generator.
    4. Attaches base64-encoded screenshots and diagnostic cards to pytest-html.
    """
    outcome = yield
    report = outcome.get_result()
    extras = getattr(report, "extras", [])

    encoded_img = None
    failure_category = "Execution Error"
    plain_cause = ""
    business_impact = ""
    action_rec = ""
    badge_color = "#64748b"
    badge_bg = "#f1f5f9"
    details = ""

    if report.failed:
        exc_type = call.excinfo.typename if call.excinfo else "Exception"
        exc_msg = str(call.excinfo.value) if call.excinfo else ""
        classification = ReportPortal.classify_failure(exc_type, exc_msg, when=report.when)

        failure_category = classification["category"]
        badge_color = classification["badge_color"]
        plain_cause = classification["plain_cause"]
        business_impact = classification["business_impact"]
        action_rec = classification["action"]
        details = plain_cause

        # Capture screenshot if WebDriver instance is available on test item
        web_driver = getattr(item, "driver", None)
        screenshot_html = ""
        if web_driver is not None:
            try:
                Config.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                clean_test_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in item.name)
                screenshot_filename = f"{clean_test_name}_{timestamp}.png"
                screenshot_path = Config.SCREENSHOTS_DIR / screenshot_filename

                web_driver.save_screenshot(str(screenshot_path))
                logger.warning(
                    f"Test failure captured for '{item.name}' [{failure_category}]. "
                    f"Saved screenshot: {screenshot_path}"
                )

                # Base64 encode for self-contained HTML embedding
                with open(screenshot_path, "rb") as img_file:
                    encoded_img = base64.b64encode(img_file.read()).decode("utf-8")

                pytest_html = item.config.pluginmanager.getplugin("html")
                if pytest_html is not None:
                    extras.append(pytest_html.extras.image(encoded_img, name=f"Screenshot: {screenshot_filename}"))

                screenshot_html = (
                    f"<div style='margin-top: 8px; font-size: 12px;'>"
                    f"<strong>Saved Screenshot:</strong> <code>screenshots/{screenshot_filename}</code>"
                    f"</div>"
                )
            except Exception as e:
                logger.error(f"Failed to capture failure screenshot: {e}")
                screenshot_html = f"<div style='margin-top: 8px; font-size: 12px; color: #dc2626;'>Screenshot capture error: {e}</div>"

        # Attach diagnostic classification card to pytest-html report
        pytest_html = item.config.pluginmanager.getplugin("html")
        if pytest_html is not None:
            card_html = (
                f"<div style='margin: 10px 0; padding: 12px 16px; border-radius: 6px; "
                f"border-left: 5px solid {badge_color}; background-color: {badge_bg}; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif;'>"
                f"<div style='font-size: 13px; font-weight: bold; color: {badge_color}; text-transform: uppercase; letter-spacing: 0.5px;'>"
                f"[{report.when.upper()}] {failure_category}"
                f"</div>"
                f"<div style='margin-top: 5px; font-size: 12px; color: #374151; line-height: 1.4;'>{details}</div>"
                f"{screenshot_html}"
                f"</div>"
            )
            extras.append(pytest_html.extras.html(card_html))

    report.extras = extras

    # Collect structured test result for ReportPortal website generator
    should_record = False
    if report.when == "call":
        should_record = True
    elif report.when == "setup" and (report.failed or report.skipped):
        should_record = True
    elif report.when == "teardown" and report.failed:
        should_record = True

    if should_record and hasattr(item.config, "_report_portal_tests"):
        markers = [m.name for m in item.iter_markers()]
        module_key = ReportPortal.detect_module(item.nodeid, markers)

        # Parse docstring & human-friendly metadata
        doc = getattr(item.function, "__doc__", None) if hasattr(item, "function") else None
        doc_info = ReportPortal.parse_docstring(doc, item.name)

        # Extract formatted traceback & logs
        tb_str = ""
        if call and call.excinfo:
            tb_str = str(call.excinfo.getrepr(style="short"))

        logs_list = []
        for section in getattr(report, "sections", []):
            title_sec, content_sec = section
            logs_list.append(f"--- {title_sec} ---\n{content_sec}")
        logs_str = "\n\n".join(logs_list)

        test_record = {
            "node_id": item.nodeid,
            "module": module_key,
            "test_id": doc_info["test_id"],
            "title": doc_info["title"],
            "purpose": doc_info["purpose"],
            "precondition": doc_info["precondition"],
            "action": doc_info["action"],
            "expected": doc_info["expected"],
            "assertion": doc_info["assertion"],
            "outcome": report.outcome,
            "duration": f"{report.duration:.2f}s",
            "screenshot_b64": encoded_img,
            "failure_category": failure_category,
            "plain_cause": plain_cause,
            "business_impact": business_impact,
            "action_recommendation": action_rec,
            "badge_color": badge_color,
            "traceback": tb_str,
            "logs": logs_str,
        }

        # Avoid duplicate records for the same test item if setup + call were both captured
        existing_indices = [i for i, t in enumerate(item.config._report_portal_tests) if t["node_id"] == item.nodeid]
        if existing_indices:
            # Update existing
            item.config._report_portal_tests[existing_indices[0]] = test_record
        else:
            item.config._report_portal_tests.append(test_record)


