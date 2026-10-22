"""
Page Object Model (POM) package for Keepwisely Automation framework.
Exports all page classes for direct and clean imports across test suites.
"""

from pages.base_page import BasePage
from pages.login_page import LoginPage
from pages.dashboard_page import DashboardPage
from pages.user_management_page import UserManagementPage
from pages.asset_page import AssetPage
from pages.location_page import LocationPage
from pages.maintenance_page import MaintenancePage
from pages.procurement_page import ProcurementPage
from pages.settings_page import SettingsPage
from pages.kaizen_page import KaizenPage
from pages.five_s_audit_page import FiveSAuditPage
from pages.poka_yoke_page import PokaYokePage
from pages.amc_warranty_page import AMCWarrantyPage
from pages.reports_page import ReportsPage
from pages.floor_plan_page import FloorPlanPage
from pages.masters_page import MastersPage

__all__ = [
    "BasePage",
    "LoginPage",
    "DashboardPage",
    "UserManagementPage",
    "AssetPage",
    "LocationPage",
    "MaintenancePage",
    "ProcurementPage",
    "SettingsPage",
    "KaizenPage",
    "FiveSAuditPage",
    "PokaYokePage",
    "AMCWarrantyPage",
    "ReportsPage",
    "FloorPlanPage",
    "MastersPage",
]
