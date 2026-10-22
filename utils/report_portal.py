import base64
import html
import json
import os
import re
from datetime import datetime
from pathlib import Path


class ReportPortal:
    """
    Website-Level Executive Test Report Portal Generator for Keepwisely CMMS.
    Converts raw technical test results into an executive-friendly, professional,
    single-page web portal with module-wise analytics, plain-English explanations,
    and developer technical debug drawers.
    """

    MODULE_DEFINITIONS = {
        "auth": {
            "name": "Authentication & Access Control",
            "icon": "🔐",
            "description": "User login, session security, password controls, and credential validation",
        },
        "dashboard": {
            "name": "Dashboard & Navigation",
            "icon": "📊",
            "description": "Authenticated landing shell, KPI metrics, sidebar menus, and user profile",
        },
        "smoke": {
            "name": "Application Availability & Smoke",
            "icon": "⚡",
            "description": "Critical system launch, Angular DOM mounting, and login page rendering",
        },
        "users": {
            "name": "User Management & Roles",
            "icon": "👥",
            "description": "User directory, role assignments, permissions, and status controls",
        },
        "assets": {
            "name": "Asset Management & Registry",
            "icon": "🏢",
            "description": "Equipment tracking, location tagging, barcodes, and maintenance history",
        },
        "maintenance": {
            "name": "Breakdown & Maintenance",
            "icon": "🔧",
            "description": "Service requests, work orders, preventive tasks, and downtime tracking",
        },
        "procurement": {
            "name": "Procurement & BOM",
            "icon": "📦",
            "description": "Purchase requisitions, spare parts BOM, and vendor fulfillment",
        },
        "kaizen": {
            "name": "Continuous Improvement (Kaizen)",
            "icon": "💡",
            "description": "Operational efficiency ideas, approval workflows, and impact tracking",
        },
        "five_s": {
            "name": "5S Workplace Audits",
            "icon": "📋",
            "description": "Sort, Set in order, Shine, Standardize, Sustain workplace compliance",
        },
        "poka_yoke": {
            "name": "Poka-Yoke Error Proofing",
            "icon": "🛡️",
            "description": "Mistake-proofing checklists and preventive manufacturing safeguards",
        },
        "amc_warranty": {
            "name": "AMC & Warranty Management",
            "icon": "📜",
            "description": "Equipment service contracts, vendor guarantees, and renewal alerts",
        },
        "reports": {
            "name": "Analytics & Reports",
            "icon": "📈",
            "description": "Executive maintenance summaries, equipment MTBF/MTTR, and compliance",
        },
        "floor_plan": {
            "name": "Floor Plan & Spatial Layout",
            "icon": "🗺️",
            "description": "Facility spatial visualization, asset pinpoints, and workstation maps",
        },
        "masters": {
            "name": "Master Data Configuration",
            "icon": "⚙️",
            "description": "System lookup tables, categories, units of measure, and global dropdowns",
        },
        "settings": {
            "name": "System Configuration & Settings",
            "icon": "🛠️",
            "description": "Prefix definitions, notification rules, and enterprise preferences",
        },
        "general": {
            "name": "General & Regression Suite",
            "icon": "🧪",
            "description": "Cross-module regression validations and integration checks",
        },
    }

    @classmethod
    def detect_module(cls, test_id: str, markers: list[str]) -> str:
        """Classify a test into its business module based on markers, filename, or test path."""
        test_id_lower = test_id.lower()
        for marker in markers:
            m_lower = marker.lower()
            if m_lower in cls.MODULE_DEFINITIONS:
                return m_lower

        if "auth" in test_id_lower:
            return "auth"
        elif "dash" in test_id_lower:
            return "dashboard"
        elif "smoke" in test_id_lower:
            return "smoke"
        elif "user" in test_id_lower:
            return "users"
        elif "asset" in test_id_lower:
            return "assets"
        elif "maint" in test_id_lower or "service" in test_id_lower:
            return "maintenance"
        elif "procur" in test_id_lower or "bom" in test_id_lower:
            return "procurement"
        elif "kaizen" in test_id_lower:
            return "kaizen"
        elif "five_s" in test_id_lower or "5s" in test_id_lower:
            return "five_s"
        elif "poka" in test_id_lower:
            return "poka_yoke"
        elif "amc" in test_id_lower or "warranty" in test_id_lower:
            return "amc_warranty"
        elif "report" in test_id_lower:
            return "reports"
        elif "floor" in test_id_lower or "plan" in test_id_lower:
            return "floor_plan"
        elif "master" in test_id_lower:
            return "masters"
        elif "setting" in test_id_lower:
            return "settings"

        return "general"

    @classmethod
    def parse_docstring(cls, doc: str | None, test_name: str) -> dict:
        """Parse test docstrings into structured, human-readable non-tech explanations."""
        if not doc:
            clean_name = test_name.replace("test_", "").replace("_", " ").title()
            return {
                "test_id": clean_name[:12],
                "title": clean_name,
                "purpose": f"Automated functional validation of {clean_name}.",
                "precondition": "Application is accessible and test environment is ready.",
                "action": "Executes automated user actions and evaluates expected UI state.",
                "expected": "Expected application state is achieved without unexpected errors.",
                "assertion": "Application behaves in accordance with business requirements.",
            }

        lines = [line.strip() for line in doc.strip().split("\n")]
        title = ""
        test_id = ""
        purpose = ""
        precondition = ""
        action = ""
        expected = ""
        assertion = ""

        first_non_empty = [l for l in lines if l]
        if first_non_empty:
            purpose = first_non_empty[0]

        for line in lines:
            if line.lower().startswith("test id:"):
                test_id = line.split(":", 1)[1].strip()
            elif line.lower().startswith("precondition:"):
                precondition = line.split(":", 1)[1].strip()
            elif line.lower().startswith("action:"):
                action = line.split(":", 1)[1].strip()
            elif line.lower().startswith("expected result:"):
                expected = line.split(":", 1)[1].strip()
            elif line.lower().startswith("assertion:"):
                assertion = line.split(":", 1)[1].strip()

        # If test_id is empty, extract from name if possible (e.g. TC-AUTH-01)
        if not test_id:
            match = re.search(r"tc[_-][a-z0-9]+[_-][0-9]+", test_name, re.IGNORECASE)
            if match:
                test_id = match.group(0).upper().replace("_", "-")
            else:
                test_id = test_name.replace("test_", "")[:10].upper()

        # Human-friendly Title
        clean_name = test_name.replace("test_", "")
        if match:
            clean_name = clean_name.replace(match.group(0).lower(), "")
        clean_name = clean_name.replace("_", " ").strip().title()
        if not clean_name:
            clean_name = purpose[:50] or "Functional Verification"

        full_title = f"{test_id}: {clean_name}" if test_id else clean_name

        return {
            "test_id": test_id,
            "title": full_title,
            "purpose": purpose or f"Validates {clean_name} functionality according to specifications.",
            "precondition": precondition or "User session or browser context is initialized.",
            "action": action or "Performs standard user workflows in Keepwisely CMMS.",
            "expected": expected or "Application executes successfully without runtime exceptions.",
            "assertion": assertion or "Target elements and data match expected state.",
        }

    @classmethod
    def classify_failure(cls, exc_type: str, exc_message: str, when: str = "call") -> dict:
        """Translate complex Python/Selenium errors into non-technical plain English explanations."""
        exc_type_lower = exc_type.lower()
        exc_msg_lower = exc_message.lower()

        if when == "setup":
            return {
                "category": "Infrastructure / Environment Startup Issue",
                "badge_color": "#dc2626",
                "plain_cause": (
                    "The browser or test environment failed during initialization before the test could run. "
                    "This usually indicates a network connection drop or browser driver startup issue."
                ),
                "business_impact": "High (Environment Blocker) — Test could not start.",
                "action": "Ensure the application URL is reachable and the test environment is online.",
            }
        elif when == "teardown":
            return {
                "category": "Cleanup / Teardown Interruption",
                "badge_color": "#ea580c",
                "plain_cause": (
                    "The test finished executing, but the browser encountered an issue during session cleanup."
                ),
                "business_impact": "Low — Functional test result was recorded before cleanup.",
                "action": "Ensure browser processes have sufficient OS memory to terminate cleanly.",
            }

        # Call phase exceptions
        if "timeoutexception" in exc_type_lower or "timed out" in exc_msg_lower:
            return {
                "category": "Application Response Timeout",
                "badge_color": "#c2410c",
                "plain_cause": (
                    "The application took longer than the allocated time limit (explicit timeout) to respond. "
                    "The web page or component did not finish loading, or a server request experienced high latency."
                ),
                "business_impact": "High (Performance / Responsiveness) — End users would experience delays.",
                "action": "Investigate server API response times and verify CDN / network connectivity.",
            }
        elif "assertionerror" in exc_type_lower:
            return {
                "category": "Business Rule Verification Mismatch",
                "badge_color": "#b91c1c",
                "plain_cause": (
                    "The application behaved differently than required by the business specification. "
                    "An expected button, status message, URL, or data value did not match the expected state."
                ),
                "business_impact": "Medium to High (Functional Defect) — Business logic mismatch detected.",
                "action": "Review the requirement and compare the actual UI state with expected specifications.",
            }
        elif "nosuchelement" in exc_type_lower or "elementnotinteractable" in exc_type_lower:
            return {
                "category": "UI Element Not Visible / Disabled",
                "badge_color": "#ea580c",
                "plain_cause": (
                    "An expected button, input field, or menu option was not found on screen. "
                    "The element may have moved, failed to render, or required different user permissions."
                ),
                "business_impact": "Medium (UI Navigation Issue) — Expected control unavailable.",
                "action": "Verify if recent UI layout changes occurred or if the logged-in user lacks permissions.",
            }
        elif "webdriverexception" in exc_type_lower or "connection" in exc_msg_lower:
            return {
                "category": "Browser Communication Error",
                "badge_color": "#dc2626",
                "plain_cause": (
                    "Lost communication with the automated browser session. "
                    "The browser window may have closed unexpectedly or the server closed the connection."
                ),
                "business_impact": "High (Automation Interruption) — Test could not complete.",
                "action": "Restart the browser session and verify available system resources.",
            }
        else:
            return {
                "category": f"Unexpected Runtime Error ({exc_type})",
                "badge_color": "#c2410c",
                "plain_cause": (
                    f"An unhandled error ({exc_type}) occurred while executing test actions."
                ),
                "business_impact": "Medium — Unexpected exception encountered.",
                "action": "Inspect the technical logs and stack trace below for debugging details.",
            }

    @classmethod
    def generate_html(cls, report_data: dict) -> str:
        """
        Build the comprehensive, website-level single HTML report.
        Self-contained with inline CSS and JS.
        """
        tests = report_data.get("tests", [])
        metadata = report_data.get("metadata", {})
        execution_time = metadata.get("execution_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        target_url = metadata.get("base_url", "https://app.keepwisely.com")
        browser = metadata.get("browser", "Chrome")
        mode = metadata.get("mode", "Headless")
        duration_total = metadata.get("total_duration", "0s")

        # Compute summary metrics
        total_tests = len(tests)
        passed_tests = sum(1 for t in tests if t["outcome"] == "passed")
        failed_tests = sum(1 for t in tests if t["outcome"] == "failed")
        skipped_tests = sum(1 for t in tests if t["outcome"] == "skipped")
        pass_rate = round((passed_tests / total_tests * 100), 1) if total_tests > 0 else 0

        # Health status badge
        if failed_tests == 0 and total_tests > 0:
            health_status = "SYSTEM STABLE — PRODUCTION READY"
            health_color = "#10b981"
            health_bg = "rgba(16, 185, 129, 0.15)"
        elif failed_tests <= 2:
            health_status = f"ATTENTION NEEDED — {failed_tests} ISSUES DETECTED"
            health_color = "#f59e0b"
            health_bg = "rgba(245, 158, 11, 0.15)"
        else:
            health_status = f"CRITICAL DEFECTS — {failed_tests} FAILURES"
            health_color = "#ef4444"
            health_bg = "rgba(239, 68, 68, 0.15)"

        # Group tests by module
        module_stats = {}
        for mod_key, mod_info in cls.MODULE_DEFINITIONS.items():
            module_stats[mod_key] = {
                "key": mod_key,
                "name": mod_info["name"],
                "icon": mod_info["icon"],
                "description": mod_info["description"],
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "tests": [],
            }

        for t in tests:
            mod_key = t.get("module", "general")
            if mod_key not in module_stats:
                mod_key = "general"
            module_stats[mod_key]["total"] += 1
            if t["outcome"] == "passed":
                module_stats[mod_key]["passed"] += 1
            elif t["outcome"] == "failed":
                module_stats[mod_key]["failed"] += 1
            elif t["outcome"] == "skipped":
                module_stats[mod_key]["skipped"] += 1
            module_stats[mod_key]["tests"].append(t)

        # Active modules (those with tests)
        active_modules = [m for m in module_stats.values() if m["total"] > 0]
        # Also keep registered modules available in tabs
        all_display_modules = active_modules if active_modules else list(module_stats.values())[:4]

        # Calculate circular SVG dashoffset for gauge (radius 52 => circumference ~ 326.7)
        circumference = 326.7
        dashoffset = circumference - (circumference * (pass_rate / 100))

        # Generate Test Cards HTML
        test_cards_html = []
        for idx, t in enumerate(tests, 1):
            outcome = t["outcome"]
            outcome_upper = outcome.upper()
            if outcome == "passed":
                status_badge = '<span class="status-badge passed">✓ PASSED</span>'
                card_accent = "border-passed"
                status_icon = "🟢"
            elif outcome == "failed":
                status_badge = '<span class="status-badge failed">✕ FAILED</span>'
                card_accent = "border-failed"
                status_icon = "🔴"
            else:
                status_badge = '<span class="status-badge skipped">⏸ SKIPPED</span>'
                card_accent = "border-skipped"
                status_icon = "🟡"

            mod_key = t.get("module", "general")
            mod_meta = cls.MODULE_DEFINITIONS.get(mod_key, cls.MODULE_DEFINITIONS["general"])
            duration_str = t.get("duration", "0.00s")
            test_id_code = t.get("test_id", f"TEST-{idx}")
            test_title = html.escape(t.get("title", "Test Scenario"))
            purpose = html.escape(t.get("purpose", ""))
            precondition = html.escape(t.get("precondition", ""))
            action = html.escape(t.get("action", ""))
            expected = html.escape(t.get("expected", ""))
            actual = html.escape(t.get("actual", ""))
            assertion = html.escape(t.get("assertion", ""))

            # Failure details
            failure_html = ""
            if outcome == "failed":
                fail_cat = html.escape(t.get("failure_category", "Execution Failure"))
                fail_cause = html.escape(t.get("plain_cause", "An unexpected failure occurred."))
                fail_impact = html.escape(t.get("business_impact", "Medium"))
                fail_action = html.escape(t.get("action_recommendation", "Investigate application logs."))
                badge_color = t.get("badge_color", "#ef4444")

                screenshot_html = ""
                if t.get("screenshot_b64"):
                    s_b64 = t["screenshot_b64"]
                    screenshot_html = f"""
                    <div class="screenshot-container">
                        <div class="screenshot-title">
                            <span class="icon">📷</span>
                            <span>Visual Failure Evidence (Captured at moment of failure):</span>
                        </div>
                        <div class="screenshot-preview" onclick="openLightbox('{s_b64}', '{test_title}')">
                            <img src="data:image/png;base64,{s_b64}" alt="Failure Screenshot" />
                            <div class="screenshot-overlay">
                                <span class="zoom-icon">🔍</span>
                                <span>Click to View Full Resolution Screenshot</span>
                            </div>
                        </div>
                    </div>
                    """

                failure_html = f"""
                <div class="failure-diagnosis-box" style="border-left-color: {badge_color};">
                    <div class="diagnosis-header">
                        <div class="diagnosis-title" style="color: {badge_color};">
                            <span>⚠️ Root Cause Analysis:</span> <strong>{fail_cat}</strong>
                        </div>
                        <span class="impact-badge">{fail_impact}</span>
                    </div>
                    <div class="diagnosis-explanation">
                        <strong>Plain-English Summary:</strong> {fail_cause}
                    </div>
                    <div class="diagnosis-recommendation">
                        <strong>Recommended Next Step:</strong> {fail_action}
                    </div>
                    {screenshot_html}
                </div>
                """

            # Technical traceback details (collapsible)
            technical_html = ""
            if t.get("traceback") or t.get("logs"):
                tb_content = html.escape(t.get("traceback", "No traceback available."))
                logs_content = html.escape(t.get("logs", "No logs recorded."))
                technical_html = f"""
                <details class="tech-drawer">
                    <summary class="tech-summary">
                        <span class="tech-tag">🔧 Technical Details (For Automation Engineers & Developers)</span>
                        <span class="chevron">▾</span>
                    </summary>
                    <div class="tech-content">
                        {f'''<div class="tech-block">
                            <div class="tech-label">Python Exception & Stack Trace:</div>
                            <pre class="code-block"><code>{tb_content}</code></pre>
                        </div>''' if t.get("traceback") else ''}
                        {f'''<div class="tech-block">
                            <div class="tech-label">Selenium & Pytest Logs:</div>
                            <pre class="code-block"><code>{logs_content}</code></pre>
                        </div>''' if t.get("logs") else ''}
                    </div>
                </details>
                """

            card_markup = f"""
            <div class="test-card {card_accent}" data-module="{mod_key}" data-outcome="{outcome}" data-search="{test_title.lower()} {test_id_code.lower()} {purpose.lower()}">
                <div class="card-header" onclick="toggleCardDetails(this)">
                    <div class="header-left">
                        <span class="status-indicator">{status_icon}</span>
                        {status_badge}
                        <span class="module-chip">{mod_meta['icon']} {mod_meta['name']}</span>
                        <span class="test-id-badge">{test_id_code}</span>
                        <h3 class="test-heading">{test_title}</h3>
                    </div>
                    <div class="header-right">
                        <span class="duration-badge">⏱️ {duration_str}</span>
                        <button class="expand-btn" aria-label="Toggle details">
                            <span class="expand-icon">▾</span>
                        </button>
                    </div>
                </div>

                <div class="card-summary">
                    <p class="purpose-text"><strong>Objective:</strong> {purpose}</p>
                </div>

                <div class="card-body">
                    <div class="business-flow-grid">
                        <div class="flow-step">
                            <span class="flow-label">1. Precondition</span>
                            <p class="flow-value">{precondition}</p>
                        </div>
                        <div class="flow-step">
                            <span class="flow-label">2. Action Performed</span>
                            <p class="flow-value">{action}</p>
                        </div>
                        <div class="flow-step">
                            <span class="flow-label">3. Expected Result</span>
                            <p class="flow-value">{expected}</p>
                        </div>
                        <div class="flow-step">
                            <span class="flow-label">4. Business Assertion</span>
                            <p class="flow-value">{assertion}</p>
                        </div>
                    </div>

                    {failure_html}
                    {technical_html}
                </div>
            </div>
            """
            test_cards_html.append(card_markup)

        tests_rendered_markup = "\n".join(test_cards_html) if test_cards_html else """
        <div class="empty-state">
            <div class="empty-icon">📂</div>
            <h3>No Test Results Match Current Filters</h3>
            <p>Try resetting the search query or selecting a different module tab above.</p>
        </div>
        """

        # Generate Module Cards HTML
        module_cards_html = []
        for m in all_display_modules:
            m_key = m["key"]
            m_total = m["total"]
            m_passed = m["passed"]
            m_failed = m["failed"]
            m_rate = round((m_passed / m_total * 100), 1) if m_total > 0 else 0
            if m_total == 0:
                mod_status = '<span class="mod-pill neutral">Ready</span>'
            elif m_failed == 0:
                mod_status = '<span class="mod-pill pass">100% Passed</span>'
            else:
                mod_status = f'<span class="mod-pill fail">{m_failed} Issues</span>'

            module_card = f"""
            <div class="module-card" data-module="{m_key}" onclick="filterByModule('{m_key}')">
                <div class="module-card-top">
                    <span class="module-card-icon">{m['icon']}</span>
                    {mod_status}
                </div>
                <div class="module-card-title">{m['name']}</div>
                <div class="module-card-desc">{m['description']}</div>
                <div class="module-card-stats">
                    <span><strong>{m_total}</strong> tests</span>
                    <span><strong style="color: #10b981;">{m_passed}</strong> pass &bull; <strong style="color: #ef4444;">{m_failed}</strong> fail</span>
                </div>
                <div class="module-progress-bar">
                    <div class="module-progress-fill" style="width: {m_rate}%; background: {'#10b981' if m_failed == 0 else '#f59e0b'};"></div>
                </div>
            </div>
            """
            module_cards_html.append(module_card)
        modules_rendered_markup = "\n".join(module_cards_html)

        # Build complete HTML
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Keepwisely CMMS — Enterprise Automation Portal</title>
    <style>
        :root {{
            --bg-body: #090d16;
            --bg-surface: #111827;
            --bg-card: #162033;
            --bg-card-hover: #1c2942;
            --border-color: rgba(255, 255, 255, 0.08);
            --border-highlight: rgba(56, 189, 248, 0.3);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-blue: #38bdf8;
            --accent-cyan: #06b6d4;
            --color-passed: #10b981;
            --color-passed-bg: rgba(16, 185, 129, 0.12);
            --color-failed: #ef4444;
            --color-failed-bg: rgba(239, 68, 68, 0.12);
            --color-skipped: #f59e0b;
            --color-skipped-bg: rgba(245, 158, 11, 0.12);
            --font-main: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            --font-mono: ui-monospace, SFMono-Regular, "Cascadia Code", "Roboto Mono", Consolas, monospace;
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 16px;
            --shadow-card: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
        }}

        [data-theme="light"] {{
            --bg-body: #f8fafc;
            --bg-surface: #ffffff;
            --bg-card: #ffffff;
            --bg-card-hover: #f1f5f9;
            --border-color: #e2e8f0;
            --border-highlight: rgba(14, 165, 233, 0.4);
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-muted: #94a3b8;
            --shadow-card: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background-color: var(--bg-body);
            color: var(--text-primary);
            font-family: var(--font-main);
            line-height: 1.5;
            -webkit-font-smoothing: antialiased;
            min-height: 100vh;
        }}

        /* Header Navbar */
        .portal-header {{
            position: sticky;
            top: 0;
            z-index: 50;
            background: rgba(17, 24, 39, 0.85);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-color);
            padding: 12px 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }}

        .brand-container {{
            display: flex;
            align-items: center;
            gap: 14px;
        }}

        .brand-logo {{
            width: 40px;
            height: 40px;
            border-radius: var(--radius-sm);
            background: linear-gradient(135deg, #0284c7, #38bdf8);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 22px;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        }}

        .brand-info h1 {{
            font-size: 18px;
            font-weight: 700;
            letter-spacing: -0.3px;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .brand-info p {{
            font-size: 12px;
            color: var(--text-secondary);
        }}

        .header-search {{
            flex: 1;
            max-width: 480px;
            position: relative;
        }}

        .header-search input {{
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            border-radius: 9999px;
            padding: 9px 18px 9px 40px;
            color: var(--text-primary);
            font-size: 13px;
            outline: none;
            transition: all 0.2s ease;
        }}

        .header-search input:focus {{
            background: var(--bg-surface);
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15);
        }}

        .search-icon {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-muted);
            pointer-events: none;
            font-size: 14px;
        }}

        .header-actions {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .health-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.3px;
            background: {health_bg};
            color: {health_color};
            border: 1px solid {health_color}40;
        }}

        .action-btn {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            cursor: pointer;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }}

        .action-btn:hover {{
            background: rgba(255, 255, 255, 0.12);
            color: var(--text-primary);
        }}

        /* Container */
        .portal-main {{
            max-width: 1440px;
            margin: 0 auto;
            padding: 28px 24px 60px 24px;
        }}

        /* Executive KPI Section */
        .kpi-section {{
            display: grid;
            grid-template-columns: 280px repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }}

        .kpi-gauge-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            box-shadow: var(--shadow-card);
            position: relative;
            overflow: hidden;
        }}

        .gauge-svg {{
            width: 130px;
            height: 130px;
            transform: rotate(-90deg);
        }}

        .gauge-bg {{
            fill: none;
            stroke: rgba(255, 255, 255, 0.06);
            stroke-width: 10;
        }}

        .gauge-progress {{
            fill: none;
            stroke: {'#10b981' if pass_rate >= 90 else ('#f59e0b' if pass_rate >= 75 else '#ef4444')};
            stroke-width: 10;
            stroke-linecap: round;
            stroke-dasharray: 326.7;
            stroke-dashoffset: {dashoffset};
            transition: stroke-dashoffset 1s ease-in-out;
        }}

        .gauge-center-text {{
            position: absolute;
            top: 48%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }}

        .gauge-value {{
            font-size: 26px;
            font-weight: 800;
            color: var(--text-primary);
        }}

        .gauge-label {{
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }}

        .kpi-gauge-title {{
            margin-top: 10px;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-secondary);
        }}

        .kpi-metric-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: var(--shadow-card);
            transition: transform 0.2s, border-color 0.2s;
        }}

        .kpi-metric-card:hover {{
            transform: translateY(-2px);
            border-color: var(--border-highlight);
        }}

        .kpi-metric-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
        }}

        .kpi-title {{
            font-size: 13px;
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .kpi-icon-pill {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 15px;
        }}

        .kpi-number {{
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -1px;
            color: var(--text-primary);
            line-height: 1;
        }}

        .kpi-subtext {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 8px;
        }}

        /* Section Headings */
        .section-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 32px 0 16px 0;
        }}

        .section-title {{
            font-size: 18px;
            font-weight: 700;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .section-desc {{
            font-size: 13px;
            color: var(--text-secondary);
            margin-top: 2px;
        }}

        /* Module Grid */
        .module-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
        }}

        .module-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 16px;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
        }}

        .module-card:hover, .module-card.active {{
            background: var(--bg-card-hover);
            border-color: var(--accent-blue);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px -4px rgba(56, 189, 248, 0.15);
        }}

        .module-card.active {{
            border-width: 2px;
        }}

        .module-card-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}

        .module-card-icon {{
            font-size: 24px;
        }}

        .mod-pill {{
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 9999px;
            text-transform: uppercase;
        }}

        .mod-pill.pass {{
            background: var(--color-passed-bg);
            color: var(--color-passed);
        }}

        .mod-pill.fail {{
            background: var(--color-failed-bg);
            color: var(--color-failed);
        }}

        .mod-pill.neutral {{
            background: rgba(255, 255, 255, 0.08);
            color: var(--text-secondary);
        }}

        .module-card-title {{
            font-size: 15px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 4px;
        }}

        .module-card-desc {{
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 12px;
            line-height: 1.4;
            height: 34px;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }}

        .module-card-stats {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-muted);
            margin-bottom: 6px;
        }}

        .module-progress-bar {{
            height: 5px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 9999px;
            overflow: hidden;
        }}

        .module-progress-fill {{
            height: 100%;
            border-radius: 9999px;
            transition: width 0.5s ease;
        }}

        /* Filter Controls */
        .controls-toolbar {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 12px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 20px;
        }}

        .filter-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .filter-btn {{
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 6px 14px;
            border-radius: 9999px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s;
        }}

        .filter-btn:hover {{
            color: var(--text-primary);
            border-color: rgba(255, 255, 255, 0.2);
        }}

        .filter-btn.active {{
            background: var(--accent-blue);
            color: #090d16;
            border-color: var(--accent-blue);
            font-weight: 700;
        }}

        .filter-counter {{
            background: rgba(0, 0, 0, 0.2);
            padding: 1px 6px;
            border-radius: 9999px;
            font-size: 11px;
        }}

        .active-filter-indicator {{
            font-size: 13px;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        /* Test Cards */
        .tests-stream {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}

        .test-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-left: 5px solid #64748b;
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: var(--shadow-card);
            transition: border-color 0.2s ease, transform 0.15s ease;
        }}

        .test-card.border-passed {{
            border-left-color: var(--color-passed);
        }}

        .test-card.border-failed {{
            border-left-color: var(--color-failed);
        }}

        .test-card.border-skipped {{
            border-left-color: var(--color-skipped);
        }}

        .card-header {{
            padding: 14px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            cursor: pointer;
            user-select: none;
            background: rgba(255, 255, 255, 0.01);
            transition: background 0.15s;
        }}

        .card-header:hover {{
            background: rgba(255, 255, 255, 0.03);
        }}

        .header-left {{
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 10px;
            flex: 1;
        }}

        .status-badge {{
            font-size: 11px;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 4px;
            letter-spacing: 0.4px;
        }}

        .status-badge.passed {{
            background: var(--color-passed-bg);
            color: var(--color-passed);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        .status-badge.failed {{
            background: var(--color-failed-bg);
            color: var(--color-failed);
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}

        .status-badge.skipped {{
            background: var(--color-skipped-bg);
            color: var(--color-skipped);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}

        .module-chip {{
            background: rgba(56, 189, 248, 0.1);
            color: var(--accent-blue);
            font-size: 11px;
            font-weight: 600;
            padding: 3px 8px;
            border-radius: 4px;
            border: 1px solid rgba(56, 189, 248, 0.2);
        }}

        .test-id-badge {{
            font-family: var(--font-mono);
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 600;
        }}

        .test-heading {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
        }}

        .header-right {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .duration-badge {{
            font-size: 12px;
            color: var(--text-muted);
            font-family: var(--font-mono);
        }}

        .expand-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 14px;
            cursor: pointer;
            transition: transform 0.2s;
        }}

        .test-card.expanded .expand-icon {{
            transform: rotate(180deg);
            display: inline-block;
        }}

        .card-summary {{
            padding: 0 20px 12px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }}

        .purpose-text {{
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.4;
        }}

        .card-body {{
            padding: 18px 20px;
            display: none;
            background: rgba(0, 0, 0, 0.15);
        }}

        .test-card.expanded .card-body {{
            display: block;
        }}

        /* Business Flow Grid */
        .business-flow-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin-bottom: 18px;
        }}

        .flow-step {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 12px;
        }}

        .flow-label {{
            display: block;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--accent-blue);
            margin-bottom: 4px;
        }}

        .flow-value {{
            font-size: 12.5px;
            color: var(--text-secondary);
            line-height: 1.4;
        }}

        /* Failure Diagnosis Box */
        .failure-diagnosis-box {{
            background: rgba(239, 68, 68, 0.06);
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-left: 5px solid var(--color-failed);
            border-radius: var(--radius-sm);
            padding: 16px;
            margin-bottom: 18px;
        }}

        .diagnosis-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}

        .diagnosis-title {{
            font-size: 13.5px;
            font-weight: 700;
        }}

        .impact-badge {{
            font-size: 11px;
            font-weight: 700;
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            padding: 2px 8px;
            border-radius: 4px;
        }}

        .diagnosis-explanation {{
            font-size: 13px;
            color: var(--text-primary);
            line-height: 1.4;
            margin-bottom: 8px;
        }}

        .diagnosis-recommendation {{
            font-size: 12.5px;
            color: var(--text-secondary);
        }}

        /* Screenshot */
        .screenshot-container {{
            margin-top: 14px;
        }}

        .screenshot-title {{
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .screenshot-preview {{
            position: relative;
            max-width: 480px;
            border-radius: var(--radius-sm);
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}

        .screenshot-preview img {{
            width: 100%;
            height: auto;
            display: block;
        }}

        .screenshot-overlay {{
            position: absolute;
            inset: 0;
            background: rgba(0, 0, 0, 0.6);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.2s;
            color: #ffffff;
            font-size: 12px;
            font-weight: 600;
            gap: 4px;
        }}

        .screenshot-preview:hover .screenshot-overlay {{
            opacity: 1;
        }}

        .zoom-icon {{
            font-size: 20px;
        }}

        /* Tech Drawer */
        .tech-drawer {{
            margin-top: 12px;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            background: rgba(0, 0, 0, 0.25);
            overflow: hidden;
        }}

        .tech-summary {{
            padding: 10px 14px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            justify-content: space-between;
            user-select: none;
            background: rgba(255, 255, 255, 0.02);
        }}

        .tech-summary:hover {{
            color: var(--text-primary);
        }}

        .tech-content {{
            padding: 14px;
            border-top: 1px solid var(--border-color);
        }}

        .tech-block {{
            margin-bottom: 12px;
        }}

        .tech-block:last-child {{
            margin-bottom: 0;
        }}

        .tech-label {{
            font-size: 11px;
            font-weight: 700;
            color: var(--text-muted);
            margin-bottom: 4px;
            text-transform: uppercase;
        }}

        .code-block {{
            background: #050811;
            padding: 12px;
            border-radius: var(--radius-sm);
            font-family: var(--font-mono);
            font-size: 11.5px;
            color: #e2e8f0;
            overflow-x: auto;
            white-space: pre-wrap;
            line-height: 1.5;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}

        /* Empty State */
        .empty-state {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 60px 20px;
            text-align: center;
        }}

        .empty-icon {{
            font-size: 48px;
            margin-bottom: 12px;
        }}

        .empty-state h3 {{
            font-size: 16px;
            margin-bottom: 6px;
            color: var(--text-primary);
        }}

        .empty-state p {{
            font-size: 13px;
            color: var(--text-muted);
        }}

        /* Modal Lightbox */
        .lightbox-modal {{
            position: fixed;
            inset: 0;
            z-index: 100;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(8px);
            display: none;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }}

        .lightbox-modal.active {{
            display: flex;
        }}

        .lightbox-content {{
            max-width: 90vw;
            max-height: 90vh;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
        }}

        .lightbox-header {{
            padding: 12px 20px;
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .lightbox-title {{
            font-size: 14px;
            font-weight: 600;
            color: var(--text-primary);
        }}

        .lightbox-close {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 20px;
            cursor: pointer;
            line-height: 1;
        }}

        .lightbox-image-wrap {{
            overflow: auto;
            padding: 16px;
            text-align: center;
        }}

        .lightbox-image-wrap img {{
            max-width: 100%;
            max-height: 75vh;
            border-radius: var(--radius-sm);
        }}

        /* Footer */
        .portal-footer {{
            border-top: 1px solid var(--border-color);
            padding: 24px;
            text-align: center;
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 40px;
        }}

        @media print {{
            .portal-header, .controls-toolbar, .action-btn, .header-search {{
                display: none !important;
            }}
            .portal-main {{
                max-width: 100%;
                padding: 0;
            }}
            .card-body {{
                display: block !important;
            }}
        }}
    </style>
</head>
<body>

    <!-- Top Sticky Header -->
    <header class="portal-header">
        <div class="brand-container">
            <div class="brand-logo">⚙️</div>
            <div class="brand-info">
                <h1>Keepwisely CMMS <span style="font-size: 12px; font-weight: 400; color: var(--accent-blue);">&bull; Test Automation Portal</span></h1>
                <p>Enterprise Quality Assurance &amp; Regression Analytics</p>
            </div>
        </div>

        <div class="header-search">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchInput" placeholder="Search tests, modules, keywords, or error codes..." oninput="handleSearch(this.value)" />
        </div>

        <div class="header-actions">
            <div class="health-badge">
                <span style="font-size: 10px;">●</span>
                <span>{health_status}</span>
            </div>
            <button class="action-btn" onclick="toggleTheme()" title="Toggle Dark/Light Mode">
                <span id="themeIcon">☀️</span>
            </button>
            <button class="action-btn" onclick="toggleAllCards()" title="Expand or Collapse All Test Details">
                <span>↕</span> <span id="expandAllText">Expand All</span>
            </button>
            <button class="action-btn" onclick="window.print()" title="Print or Export to PDF">
                <span>🖨️</span> <span>PDF</span>
            </button>
        </div>
    </header>

    <!-- Main Content Container -->
    <main class="portal-main">

        <!-- Executive KPI Overview -->
        <section class="kpi-section">
            <div class="kpi-gauge-card">
                <svg class="gauge-svg" viewBox="0 0 120 120">
                    <circle class="gauge-bg" cx="60" cy="60" r="52"></circle>
                    <circle class="gauge-progress" cx="60" cy="60" r="52"></circle>
                </svg>
                <div class="gauge-center-text">
                    <div class="gauge-value">{pass_rate}%</div>
                    <div class="gauge-label">Pass Rate</div>
                </div>
                <div class="kpi-gauge-title">Overall Test Health</div>
            </div>

            <div class="kpi-metric-card">
                <div class="kpi-metric-top">
                    <span class="kpi-title">Total Tests</span>
                    <span class="kpi-icon-pill" style="background: rgba(56, 189, 248, 0.15); color: var(--accent-blue);">📊</span>
                </div>
                <div class="kpi-number">{total_tests}</div>
                <div class="kpi-subtext">Comprehensive regression suite</div>
            </div>

            <div class="kpi-metric-card">
                <div class="kpi-metric-top">
                    <span class="kpi-title">Passed Tests</span>
                    <span class="kpi-icon-pill" style="background: var(--color-passed-bg); color: var(--color-passed);">✓</span>
                </div>
                <div class="kpi-number" style="color: var(--color-passed);">{passed_tests}</div>
                <div class="kpi-subtext">{pass_rate}% functional stability</div>
            </div>

            <div class="kpi-metric-card">
                <div class="kpi-metric-top">
                    <span class="kpi-title">Failed / Issues</span>
                    <span class="kpi-icon-pill" style="background: var(--color-failed-bg); color: var(--color-failed);">✕</span>
                </div>
                <div class="kpi-number" style="color: {'#ef4444' if failed_tests > 0 else 'var(--text-muted)'};">{failed_tests}</div>
                <div class="kpi-subtext">{'Action items requiring attention' if failed_tests > 0 else 'Zero functional defects detected'}</div>
            </div>

            <div class="kpi-metric-card">
                <div class="kpi-metric-top">
                    <span class="kpi-title">Environment &amp; Browser</span>
                    <span class="kpi-icon-pill" style="background: rgba(147, 51, 234, 0.15); color: #c084fc;">🌐</span>
                </div>
                <div style="font-size: 16px; font-weight: 700; color: var(--text-primary);">{browser} ({mode})</div>
                <div class="kpi-subtext" style="word-break: break-all;">
                    URL: <strong style="color: var(--text-primary);">{target_url}</strong><br />
                    Executed: {execution_time} &bull; Total Duration: <strong>{duration_total}</strong>
                </div>
            </div>
        </section>

        <!-- Module-Wise Navigation Hub -->
        <section>
            <div class="section-header">
                <div>
                    <h2 class="section-title">
                        <span>📑 Keepwisely Application Modules</span>
                    </h2>
                    <p class="section-desc">Select any business module card below to filter its individual test execution report</p>
                </div>
                <button class="filter-btn active" id="btnAllModules" onclick="filterByModule('all')">
                    <span>Show All Modules</span>
                    <span class="filter-counter">{total_tests}</span>
                </button>
            </div>

            <div class="module-grid" id="moduleGrid">
                {modules_rendered_markup}
            </div>
        </section>

        <!-- Filter & Search Toolbar -->
        <section>
            <div class="controls-toolbar">
                <div class="filter-group">
                    <button class="filter-btn active" data-filter="all" onclick="filterByStatus('all')">
                        <span>All Tests</span>
                        <span class="filter-counter">{total_tests}</span>
                    </button>
                    <button class="filter-btn" data-filter="passed" onclick="filterByStatus('passed')">
                        <span style="color: var(--color-passed);">✓</span>
                        <span>Passed</span>
                        <span class="filter-counter">{passed_tests}</span>
                    </button>
                    <button class="filter-btn" data-filter="failed" onclick="filterByStatus('failed')">
                        <span style="color: var(--color-failed);">✕</span>
                        <span>Failed</span>
                        <span class="filter-counter">{failed_tests}</span>
                    </button>
                    <button class="filter-btn" data-filter="skipped" onclick="filterByStatus('skipped')">
                        <span style="color: var(--color-skipped);">⏸</span>
                        <span>Skipped</span>
                        <span class="filter-counter">{skipped_tests}</span>
                    </button>
                </div>

                <div class="active-filter-indicator" id="filterStatusIndicator">
                    Showing <strong>{total_tests}</strong> test scenarios across all modules
                </div>
            </div>
        </section>

        <!-- Tests Stream -->
        <section class="tests-stream" id="testStream">
            {tests_rendered_markup}
        </section>

    </main>

    <!-- Modal Lightbox for Screenshot Zoom -->
    <div class="lightbox-modal" id="lightboxModal" onclick="closeLightbox(event)">
        <div class="lightbox-content" onclick="event.stopPropagation()">
            <div class="lightbox-header">
                <span class="lightbox-title" id="lightboxTitle">Failure Screenshot Evidence</span>
                <button class="lightbox-close" onclick="closeLightbox()">&times;</button>
            </div>
            <div class="lightbox-image-wrap">
                <img id="lightboxImg" src="" alt="Enlarged Screenshot" />
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="portal-footer">
        <p>Keepwisely CMMS Automation Framework &bull; Designed for Executive &amp; Technical Teams &bull; Generated on {execution_time}</p>
    </footer>

    <!-- Interactive Logic -->
    <script>
        let currentModule = 'all';
        let currentStatus = 'all';
        let searchQuery = '';
        let allExpanded = false;

        function toggleCardDetails(headerEl) {{
            const card = headerEl.closest('.test-card');
            card.classList.toggle('expanded');
        }}

        function toggleAllCards() {{
            allExpanded = !allExpanded;
            const cards = document.querySelectorAll('.test-card');
            cards.forEach(c => {{
                if (allExpanded) c.classList.add('expanded');
                else c.classList.remove('expanded');
            }});
            document.getElementById('expandAllText').innerText = allExpanded ? 'Collapse All' : 'Expand All';
        }}

        function filterByModule(modKey) {{
            currentModule = modKey;
            // Update active state on module cards
            document.querySelectorAll('.module-card').forEach(card => {{
                if (card.dataset.module === modKey) {{
                    card.classList.add('active');
                }} else {{
                    card.classList.remove('active');
                }}
            }});

            const allBtn = document.getElementById('btnAllModules');
            if (modKey === 'all') {{
                allBtn.classList.add('active');
            }} else {{
                allBtn.classList.remove('active');
            }}

            applyFilters();
        }}

        function filterByStatus(statusKey) {{
            currentStatus = statusKey;
            document.querySelectorAll('.filter-group .filter-btn').forEach(btn => {{
                if (btn.dataset.filter === statusKey) {{
                    btn.classList.add('active');
                }} else {{
                    btn.classList.remove('active');
                }}
            }});
            applyFilters();
        }}

        function handleSearch(query) {{
            searchQuery = query.toLowerCase().trim();
            applyFilters();
        }}

        function applyFilters() {{
            const cards = document.querySelectorAll('.test-card');
            let visibleCount = 0;

            cards.forEach(card => {{
                const cardMod = card.dataset.module;
                const cardOutcome = card.dataset.outcome;
                const cardSearch = card.dataset.search || '';

                const matchesMod = (currentModule === 'all' || cardMod === currentModule);
                const matchesStatus = (currentStatus === 'all' || cardOutcome === currentStatus);
                const matchesSearch = (!searchQuery || cardSearch.includes(searchQuery));

                if (matchesMod && matchesStatus && matchesSearch) {{
                    card.style.display = 'block';
                    visibleCount++;
                }} else {{
                    card.style.display = 'none';
                }}
            }});

            const indicator = document.getElementById('filterStatusIndicator');
            let modLabel = currentModule === 'all' ? 'all modules' : `the "${{currentModule}}" module`;
            indicator.innerHTML = `Showing <strong>${{visibleCount}}</strong> test scenario${{visibleCount !== 1 ? 's' : ''}} in ${{modLabel}}`;
        }}

        function openLightbox(b64Data, title) {{
            const modal = document.getElementById('lightboxModal');
            const img = document.getElementById('lightboxImg');
            const titleEl = document.getElementById('lightboxTitle');
            img.src = 'data:image/png;base64,' + b64Data;
            titleEl.innerText = title ? 'Failure Evidence: ' + title : 'Failure Screenshot';
            modal.classList.add('active');
        }}

        function closeLightbox() {{
            const modal = document.getElementById('lightboxModal');
            modal.classList.remove('active');
        }}

        function toggleTheme() {{
            const isLight = document.documentElement.getAttribute('data-theme') === 'light';
            if (isLight) {{
                document.documentElement.removeAttribute('data-theme');
                document.getElementById('themeIcon').innerText = '☀️';
            }} else {{
                document.documentElement.setAttribute('data-theme', 'light');
                document.getElementById('themeIcon').innerText = '🌙';
            }}
        }}

        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') closeLightbox();
        }});
    </script>
</body>
</html>
"""
        return html_content

    @classmethod
    def save_report(cls, report_data: dict, output_file: str | Path) -> Path:
        """Render and write the complete self-contained website report to target file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        html_code = cls.generate_html(report_data)
        output_path.write_text(html_code, encoding="utf-8")
        return output_path
