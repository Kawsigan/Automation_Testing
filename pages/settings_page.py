from typing import Tuple
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("settings_page")


class SettingsPage(BasePage):
    """
    Page Object Model representing System Settings, focusing on
    Code Generation Prefixes (/settings/prefix).
    """

    # --- Prefix Configuration Locators ---
    PREFIX_TABLE: Tuple[str, str] = (By.CSS_SELECTOR, "table, .table, tr")
    EDIT_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button.btn-primary, button.btn-secondary, td button")
    ASSET_PREFIX_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='asset_prefix'], input[name='asset_prefix'], #asset_prefix")
    TICKET_PREFIX_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='ticket_prefix'], input[name='ticket_prefix'], #ticket_prefix")
    PO_PREFIX_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input[formcontrolname='po_prefix'], input[name='po_prefix'], #po_prefix")
    SAVE_PREFIX_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[type='submit'], .card-footer button.btn-primary, button.btn-success")

    def __init__(self, driver):
        super().__init__(driver)

    def is_prefix_settings_displayed(self) -> bool:
        """
        Verifies that the Prefix Settings table / form is visible.
        """
        return self.is_visible(self.PREFIX_TABLE, timeout=10) or self.is_visible(self.EDIT_BUTTON, timeout=5)

    def update_asset_prefix(self, new_prefix: str) -> "SettingsPage":
        """
        Updates the auto-numbering prefix for assets.
        """
        logger.info(f"Setting asset prefix to: '{new_prefix}'")
        self.type_text(self.ASSET_PREFIX_INPUT, new_prefix)
        return self

    def save_settings(self) -> None:
        """
        Saves updated prefix settings.
        """
        self.click(self.SAVE_PREFIX_BUTTON)
        self.wait_for_angular_loader()
