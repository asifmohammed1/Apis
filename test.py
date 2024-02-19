import os
from ats import aetest
from gui.UI import ApplicationUI
from gui.CommonUtils import CommonUtilities
from gui.BrowserWebdriver import *
from gui.global_var import *
from gui.GeoRedundancyManager import GRMUI
from lib.gui.global_var import WAIT_FOR_10_SEC, WAIT_FOR_5_SEC, WAIT_FOR_60_SEC
from lib.gui.yamiparser import username, password
from ats.log.utils import banner
from lib.utilities.cwork_logging_utils import cwork_logging

lib_name = os.path.basename(__file__)
logger = cwork_logging(file_name=lib_name)

class CommonSetup(aetest.CommonSetup):

    @aetest.subsection
    def connect_to_browser(self):
        CommonUtilities.login(self, username, password)

class SemanticsVerificationHome(aetest.Testcase):
    """
    Class to verify text semantics under administrator -> Geo Rendundarcy Mangager
    """
    groups = ['Sanity', 'Regression']

    @aetest.test
    def semantics_verification_test(self, driver):
        """
        1. Go to Admin - Geo Redundancy Manager
        2. Verify Text Semantics under Geo redundnacy page
        """
        try:
            try:
                ApplicationUI.go_to_admin_geo_redundancy_manager_page(self, driver)
            except:
                logger.error("Failed to navigate to Geo Redundancy Manage page")
                CommonUtilities.sleep_before_next_click(WAIT_FOR_5_SEC)
                logger.info("Retrying....")
                ApplicationUI.go_to_admin_geo_redundancy_manager_page(self, driver)
            CommonUtilities.sleep_before_next_click(WAIT_FOR_10_SEC)
            grm_ui_obj = GRMUI(driver)
            if not grm_ui_obj.validate_semantics():
                logger.error("The test failed due to exception")
                self.failed("Exception occurred: Failed to verify semantics")
        except Exception as e:
            logger.error("The test failed due to exception:" + repr(e))
            self.failed("Exception occurred: Failed to verify semantics")

    @aetest.test
    def import_inventory_button_semantics(self, driver):
        """
        1. Go to Admin Geo Redundancy Manager
        2. Verify Text Semantics under Geo redundnacy page -> Import Inventory file button
        """
        try:
            try:
                ApplicationUI.go_to_admin_geo_redundancy_manager_page(self, driver)
            except:
                logger.error("Failed to navigate to Geo Redundancy Manage page.")
                CommonUtilities.sleep_before_next_click(WAIT_FOR_5_SEC)
                logger.info("Retrying...")
                ApplicationUI.go_to_admin_geo_redundancy_manager_page(self, driver)
            CommonUtilities.sleep_before_next_click(WAIT_FOR_10_SEC)
            grm_ui_obj = GRMUI(driver)
            grm_ui_obj.click_inventory_button()
            CommonUtilities.sleep_before_next_click(WAIT_FOR_5_SEC)
            if not grm_ui_obj.validate_import_button_semantics():
                logger.error("The test failed due to exception")
                self.failed("Exception occurred: Failed to verify semantics")
        except Exception as e:
            logger.error("The test failed due to exception:" + repr(e))
            self.failed("Exception occurred: Failed to verify semantics")

@aetest.test
def how_it_works_semantics_verification_test(self, driver):
    """
    Method to test "How it works?" hyperlink
    This method open the dialog and scroll and close the dialog
    """
    try:
        try:
            ApplicationUI.go_to_admin_geo_redundancy_manager_page(self, driver)
        except:
            logger.error("Failed to navigate to Geo Redundancy Manage page.")
            CommonUtilities.sleep_before_next_click(WAIT_FOR_5_SEC)
            logger.info("Retrying...")
            ApplicationUI.go_to_admin_geo_redundancy_manager_page(self, driver)
        CommonUtilities.sleep_before_next_click(WAIT_FOR_10_SEC)
        grm_ui_obj = GRMUI(driver)
        grm_ui_obj.goto_how_it_works_page()
        CommonUtilities.sleep_before_next_click(WAIT_FOR_5_SEC)
        if not grm_ui_obj.validate_how_it_works_hyperlink_semantics():
            logger.error("The test failed due to exception")
            self.failed("Exception occurred: Failed to verify how it works semantics")
        if not grm_ui_obj.close_how_it_works_window():
            logger.error("The test failed due to exception")
            self.failed("Exception occurred: Failed to close the 'How it works?' window.")
    except Exception as e:
        logger.error("The test failed due to exception;"+repr(e))
        self.failed("Exception occurred: Failed to verify How_it_works_semantics")

class SemanticsVerificationJobsPage(aetest.Testcase):
    """
    Class to verify Text Semantics under Administrator -> Geo Redundancy Manager -> Jobs
    """
    groups = ['Sanity', 'Regression']

    @aetest.test
    def semantics_verification_jobs(self, driver):
        """
        1. Go to Admin-> Geo Redundancy Manager
        2. Verify Text Semantics under Geo redundnacy, Jobs page
        """
        try:
            try:
                ApplicationUI.go_to_admin_geo_redundancy_manager_page(self, driver)
            except:
                logger.error("Failed to navigate to Geo Redundancy Manage page.")
                CommonUtilities.sleep_before_next_click(WAIT_FOR_5_SEC)
                logger.info("Retrying....")
                ApplicationUI.go_to_admin_geo_redundancy_manager_page(self, driver)
            CommonUtilities.sleep_before_next_click(WAIT_FOR_5_SEC)
            logger.info("Clicking Jobs page")
            grm_ui_obj = GRMUI(driver)
            job_page_status = grm_ui_obj.goto_jobs_page()
            if not job_page_status:
                logger.error("Failed to navigate to Jobs page")
                self.failed("Exception occurred: Failed to navigate to Jobs page")
            if not grm_ui_obj.validate_job_section_semantics():
                logger.error("The test failed due to exception/semantics mismatch.")
                self.failed("Exception occurred: Failed to verify semantics")
        except Exception as e:
            logger.error("The test failed due to exception:" + repr(e))
            self.failed("Exception occurred: Failed to verify semantics")

class CommonCleanup(aetest.CommonCleanup):

    @aetest.subsection
    def common_cleanup(self, driver):
        msg = "Admin -> Geo Redundancy Manager Test Suite cleanup"
        logger.info(banner("Begin %s" % msg))
        CommonUtilities.logout(self, driver)
        driver.close()
        driver.quit()
        logger.info(banner("Done %s" % msg))



















import os
from ats import aetest
from gui.UI import ApplicationUI
from gui.CommonUtils import CommonUtilities
from gui.BrowserWebdriver import *
from gui.global_var import *
from ats.log.utils import banner
from lib.utilities.cwork_logging_utils import cwork_logging

lib_name = os.path.basename(__file__)
logger = cwork_logging(file_name=lib_name)

class GoogleSearchExtendedTest(aetest.Testcase):
    groups = ['Sanity']

    @aetest.setup
    def setup(self):
        try:
            # Open the browser and navigate to Google
            driver = ApplicationUI.open_browser(browser_type="chrome")  # Adjust this based on your actual method
            ApplicationUI.go_to_url(driver, "https://www.google.com")

            # Perform login (assuming there's a login method in ApplicationUI)
            ApplicationUI.login(driver, username="your_username", password="your_password")

            # Pass: Setup completed successfully
            pass

        except Exception as e:
            logger.error("Setup failed due to exception: " + repr(e))
            self.failed("Setup failed: " + repr(e))

    @aetest.test
    def perform_google_search_extended(self, driver):
        try:
            # Navigate to Google
            ApplicationUI.go_to_url(driver, "https://www.google.com")

            # Check if the search input is visible
            search_input_visible = ApplicationUI.is_element_visible(driver, "name", "q")
            assert search_input_visible, "Search input is not visible"

            # Enter a search query
            ApplicationUI.enter_text(driver, "name", "q", "OpenAI GPT-3")

            # Check if the search button is visible
            search_button_visible = ApplicationUI.is_element_visible(driver, "name", "btnK")
            assert search_button_visible, "Search button is not visible"

            # Click on the search button
            ApplicationUI.click_element(driver, "name", "btnK")

            # Wait for the search results page to load
            CommonUtilities.sleep_before_next_click(WAIT_FOR_10_SEC)

            # Check if the search results are visible
            search_results_visible = ApplicationUI.is_element_visible(driver, "id", "search")
            assert search_results_visible, "Search results are not visible"

            # Check visibility of links on the left side (search tools)
            search_tools_visible = ApplicationUI.is_element_visible(driver, "id", "hdtb")
            assert search_tools_visible, "Search tools are not visible"

            # Click on 'Tools' to expand search tools
            ApplicationUI.click_element(driver, "id", "hdtb-tls")
            CommonUtilities.sleep_before_next_click(WAIT_FOR_2_SEC)

            # Check visibility of additional search tools
            search_tools_expanded = ApplicationUI.is_element_visible(driver, "id", "hdtbMenus")
            assert search_tools_expanded, "Search tools are not expanded"

            # Check visibility of links on the right side (Google services)
            google_services_visible = ApplicationUI.is_element_visible(driver, "id", "gbw")
            assert google_services_visible, "Google services are not visible"

            # Hover over Google services to show the dropdown
            ApplicationUI.hover_over_element(driver, "id", "gbw")

            # Check if the Google services dropdown is visible
            google_services_dropdown_visible = ApplicationUI.is_element_visible(driver, "id", "gbwa")
            assert google_services_dropdown_visible, "Google services dropdown is not visible"

            # Pass: Interactions completed successfully
            pass

        except Exception as e:
            logger.error("Test failed due to exception: " + repr(e))
            self.failed("Test failed: " + repr(e))

    @aetest.cleanup
    def cleanup(self, driver):
        try:
            # Perform cleanup steps, e.g., logging out
            ApplicationUI.click_element(driver, "id", "gb_71")  # Assuming this is the logout button
            CommonUtilities.sleep_before_next_click(WAIT_FOR_5_SEC)

            # Close the browser
            driver.close()
            driver.quit()

        except Exception as e:
            logger.error("Cleanup failed due to exception: " + repr(e))
            self.failed("Cleanup failed: " + repr(e))

if __name__ == "__main__":
    aetest.main()
