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

    def find_element(self, locator: Tuple[str, str], timeout: int = None) -> WebElement:
        """Waits for presence of element in DOM."""
        wait_time = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located(locator),
                message=f"Element {locator} was not present in DOM after {wait_time}s"
            )
        except TimeoutException as e:
            logger.error(f"Timeout waiting for presence of element: {locator}")
            raise e

    def find_visible_element(self, locator: Tuple[str, str], timeout: int = None) -> WebElement:
        """Waits for visibility of element on screen."""
        wait_time = timeout or self.timeout
        try:
            return WebDriverWait(self.driver, wait_time).until(
                EC.visibility_of_element_located(locator),
                message=f"Element {locator} was not visible after {wait_time}s"
            )
        except TimeoutException as e:
            logger.error(f"Timeout waiting for visibility of element: {locator}")
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
