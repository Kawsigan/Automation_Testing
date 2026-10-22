from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from config.config import Config
from utils.logger import get_logger

logger = get_logger("driver_factory")


class DriverFactory:
    """
    Factory class responsible for instantiating Selenium 4 WebDrivers.
    Uses Selenium 4's native Selenium Manager for automatic driver binary management.
    """

    @staticmethod
    def get_driver(browser_name: str = None, headless: bool = None) -> webdriver.Remote:
        """
        Creates and returns a configured WebDriver instance.

        :param browser_name: 'chrome', 'firefox', or 'edge'. Defaults to Config.BROWSER.
        :param headless: Boolean flag for headless execution. Defaults to Config.HEADLESS.
        :return: Initialized WebDriver instance.
        """
        browser = (browser_name or Config.BROWSER).lower()
        is_headless = Config.HEADLESS if headless is None else headless

        logger.info(f"Initializing WebDriver for browser='{browser}', headless={is_headless}")

        if browser == "chrome":
            options = ChromeOptions()
            options.page_load_strategy = "eager"
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-notifications")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
            if is_headless:
                options.add_argument("--headless=new")
            driver = webdriver.Chrome(options=options)

        elif browser == "firefox":
            options = FirefoxOptions()
            options.page_load_strategy = "eager"
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            if is_headless:
                options.add_argument("-headless")
            driver = webdriver.Firefox(options=options)

        elif browser == "edge":
            options = EdgeOptions()
            options.page_load_strategy = "eager"
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-notifications")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            if is_headless:
                options.add_argument("--headless=new")
            driver = webdriver.Edge(options=options)

        else:
            raise ValueError(f"Unsupported browser: '{browser}'. Supported options: 'chrome', 'firefox', 'edge'.")

        # Timeouts & settings
        driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)
        # Implicit wait is set to 0 to prevent conflicts with Selenium explicit waits
        driver.implicitly_wait(0)

        if not is_headless:
            try:
                driver.maximize_window()
            except Exception as e:
                logger.warning(f"Could not maximize browser window: {e}")

        logger.info(f"WebDriver successfully initialized for {browser}")
        return driver
