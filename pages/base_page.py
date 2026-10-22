from typing import List, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException
)
from config.config import Config
from utils.logger import get_logger

logger = get_logger("base_page")


class BasePage:
    """
    Foundational Page Object encapsulating robust explicit wait strategies,
    safe DOM interactions, and Angular SPA synchronization.
    All application page objects inherit from this class.
    """

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.timeout = Config.EXPLICIT_WAIT

    def open_url(self, url: str) -> None:
        """Navigates to URL and waits for Angular loaders to clear."""
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)
        self.wait_for_angular_loader()

    def get_title(self) -> str:
        """Returns the current page title."""
        return self.driver.title

    def get_current_url(self) -> str:
        """Returns current URL."""
        return self.driver.current_url

    def wait_for_angular_loader(self, timeout: int = 15) -> None:
        """
        Waits for the Angular global loading overlay (#global-loader) to disappear.
        Eliminates flakiness without using hardcoded time.sleep().
        """
        try:
            from selenium.webdriver.common.by import By
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((By.ID, "global-loader"))
            )
        except Exception:
            pass

    def wait_for_toasts_to_clear(self, timeout: int = 5) -> None:
        """
        Waits for transient toast notifications (.ngx-toastr, #toast-container)
        to disappear so that top-right header elements are not occluded.
        """
        try:
            from selenium.webdriver.common.by import By
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, ".ngx-toastr, #toast-container"))
            )
        except Exception:
            pass

    def take_screenshot(
        self,
        name: str = "capture",
        highlight_locator: Tuple[str, str] = None,
        highlight_element: WebElement = None
    ) -> str:
        """
        Captures an immediate screenshot of the current page state,
        optionally highlighting a problematic DOM element with a red glowing outline.
        Attaches the captured base64 and URL directly to the WebDriver instance
        so test reporting hooks capture the exact point of failure.
        """
        import base64
        from datetime import datetime
        try:
            Config.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
            target_el = highlight_element
            if target_el is None and highlight_locator is not None:
                try:
                    target_el = self.driver.find_element(*highlight_locator)
                except Exception:
                    pass

            if target_el is not None:
                try:
                    self.driver.execute_script("""
                        arguments[0].scrollIntoView({block: 'center', inline: 'center'});
                        arguments[0].style.outline = '3px solid #ef4444';
                        arguments[0].style.boxShadow = '0 0 14px rgba(239, 68, 68, 0.85)';
                        arguments[0].style.transition = 'all 0.2s ease-in-out';
                    """, target_el)
                except Exception:
                    pass

            clean_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{clean_name}_{timestamp}.png"
            filepath = Config.SCREENSHOTS_DIR / filename

            self.driver.save_screenshot(str(filepath))
            logger.info(f"Captured screenshot: {filepath} (URL: {self.driver.current_url})")

            with open(filepath, "rb") as f:
                b64_data = base64.b64encode(f.read()).decode("utf-8")

            # Store on driver instance for conftest reporting hook
            self.driver._last_failure_screenshot = b64_data
            self.driver._last_failure_url = self.driver.current_url
            self.driver._last_screenshot_filename = filename
            return b64_data
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return ""

    def find_element(self, locator: Tuple[str, str], timeout: int = None) -> WebElement:
        """Waits for presence of element in DOM, capturing screenshot on timeout."""
        wait_time = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located(locator),
                message=f"Element {locator} was not present in DOM after {wait_time}s"
            )
        except TimeoutException as e:
            logger.error(f"Timeout waiting for presence of element: {locator}")
            self.take_screenshot(f"fail_presence_{locator[1][:25]}", highlight_locator=locator)
            raise e

    def find_visible_element(self, locator: Tuple[str, str], timeout: int = None) -> WebElement:
        """Waits for visibility of element on screen, capturing screenshot on timeout."""
        wait_time = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located(locator),
                message=f"Element {locator} was not visible after {wait_time}s"
            )
        except TimeoutException as e:
            logger.error(f"Timeout waiting for visibility of element: {locator}")
            self.take_screenshot(f"fail_visibility_{locator[1][:25]}", highlight_locator=locator)
            raise e

    def find_all_elements(self, locator: Tuple[str, str], timeout: int = None) -> List[WebElement]:
        """Returns all matching elements or empty list if none found."""
        wait_time = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_all_elements_located(locator),
                message=f"No elements found matching {locator} after {wait_time}s"
            )
        except TimeoutException:
            return []

    def click(self, locator: Tuple[str, str], timeout: int = None) -> None:
        """
        Waits until element is clickable, then clicks.
        Handles both stale element and click interception scenarios gracefully.
        """
        wait_time = timeout or self.timeout
        logger.info(f"Clicking element: {locator}")
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.element_to_be_clickable(locator),
                message=f"Element {locator} was not clickable after {wait_time}s"
            )
            element.click()
        except (StaleElementReferenceException, ElementClickInterceptedException):
            logger.warning(f"Click issue on {locator}. Scrolling into view and retrying via JS click...")
            element = WebDriverWait(self.driver, wait_time).until(EC.presence_of_element_located(locator))
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", element)
            self.driver.execute_script("arguments[0].click();", element)
        except TimeoutException as e:
            logger.error(f"TimeoutException while clicking {locator}")
            self.take_screenshot(f"fail_click_{locator[1][:25]}", highlight_locator=locator)
            raise e

    def type_text(self, locator: Tuple[str, str], text: str, clear_first: bool = True, timeout: int = None) -> None:
        """Waits for input visibility, clears it, and types text with stale reference recovery."""
        wait_time = timeout or self.timeout
        display_text = "********" if "password" in locator[1].lower() else text
        logger.info(f"Typing '{display_text}' into: {locator}")

        try:
            element = self.find_visible_element(locator, wait_time)
            if clear_first:
                element.clear()
            element.send_keys(text)
        except StaleElementReferenceException:
            logger.warning(f"StaleElementReferenceException typing into {locator}. Re-locating and retrying...")
            element = self.find_visible_element(locator, wait_time)
            if clear_first:
                element.clear()
            element.send_keys(text)
        except Exception as e:
            self.take_screenshot(f"fail_type_{locator[1][:25]}", highlight_locator=locator)
            raise e

    def get_text(self, locator: Tuple[str, str], timeout: int = None) -> str:
        """Gets visible text from element."""
        element = self.find_visible_element(locator, timeout)
        return element.text.strip()

    def get_attribute(self, locator: Tuple[str, str], attribute_name: str, timeout: int = None) -> str:
        """Retrieves attribute value from element."""
        element = self.find_element(locator, timeout)
        return element.get_attribute(attribute_name)

    def is_visible(self, locator: Tuple[str, str], timeout: int = 3) -> bool:
        """Checks visibility safely without throwing unhandled exceptions."""
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    # --- UI Layout, Spacing, & Alignment Verification Helpers ---

    def get_element_rect(self, locator: Tuple[str, str], timeout: int = 5) -> dict:
        """
        Returns the bounding client rectangle {x, y, width, height, top, bottom, left, right}
        of a visible element for geometry and alignment validations.
        """
        el = self.find_visible_element(locator, timeout)
        return self.driver.execute_script("""
            const rect = arguments[0].getBoundingClientRect();
            return {
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height,
                top: rect.top,
                bottom: rect.bottom,
                left: rect.left,
                right: rect.right
            };
        """, el)

    def get_computed_style(self, locator: Tuple[str, str], css_property: str, timeout: int = 5) -> str:
        """Returns the computed CSS style property of an element."""
        el = self.find_visible_element(locator, timeout)
        return self.driver.execute_script("""
            return window.getComputedStyle(arguments[0]).getPropertyValue(arguments[1]);
        """, el, css_property)

    def verify_no_horizontal_overflow(self) -> bool:
        """
        Verifies that the document body does not experience unwanted horizontal scrollbar overflow.
        """
        return self.driver.execute_script("""
            return document.documentElement.scrollWidth <= window.innerWidth;
        """)

    # --------------------------------------------------------------------------
    # Error Capturing & Health Verification ("Don't miss any error")
    # --------------------------------------------------------------------------
    def get_browser_console_errors(self) -> List[dict]:
        """
        Retrieves SEVERE browser console logs (uncaught JavaScript exceptions,
        failed network requests, Angular runtime errors).
        """
        try:
            logs = self.driver.get_log("browser")
            severe_errors = [log for log in logs if log.get("level") == "SEVERE"]
            if severe_errors:
                logger.warning(f"Detected {len(severe_errors)} SEVERE console error(s): {severe_errors}")
            return severe_errors
        except Exception as e:
            logger.debug(f"Browser logs not supported or unavailable: {e}")
            return []

    def verify_page_health(self) -> bool:
        """
        Verifies that the page is healthy and not in an unhandled crash or HTTP 5xx/404 state.
        """
        source = self.driver.page_source.lower()
        crash_signatures = [
            "internal server error",
            "502 bad gateway",
            "503 service unavailable",
            "504 gateway timeout",
            "an unhandled error has occurred",
            "cannot read properties of undefined"
        ]
        for signature in crash_signatures:
            if signature in source:
                logger.error(f"Page health check failed! Found crash signature: '{signature}'")
                self.take_screenshot(f"fail_page_health_{signature.replace(' ', '_')}")
                return False
        return True

    # --------------------------------------------------------------------------
    # Monkey & Chaos Testing Utilities
    # --------------------------------------------------------------------------
    def execute_monkey_fuzz(self, locator: Tuple[str, str], payload: str, clear_first: bool = True) -> bool:
        """
        Types a chaos/fuzz payload into a target input, testing layout resilience,
        boundary limits, and absence of browser runtime errors.
        """
        try:
            el = self.find_visible_element(locator, timeout=5)
            if clear_first:
                el.clear()
            safe_payload = str(payload).replace("\n", " ").replace("\r", " ")
            el.send_keys(safe_payload)
            return self.verify_page_health()
        except Exception as e:
            logger.error(f"Monkey fuzz input failed on locator {locator}: {e}")
            self.take_screenshot(f"fail_monkey_fuzz_{locator[1][:20]}")
            return False

    def execute_monkey_rapid_clicks(self, locator: Tuple[str, str], clicks: int = 5) -> bool:
        """
        Performs rapid consecutive clicks on a button/link to stress-test debounce,
        event listeners, and modal handling without unhandled exceptions.
        """
        try:
            el = self.find_visible_element(locator, timeout=5)
            for i in range(clicks):
                self.driver.execute_script("arguments[0].click();", el)
            return self.verify_page_health()
        except Exception as e:
            logger.warning(f"Rapid monkey click interrupted on {locator}: {e}")
            return False

