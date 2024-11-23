from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging

class FormFieldLocator:
    """Class to handle multiple locator strategies for a single field"""
    def __init__(self, name, locator_strategies):
        self.name = name
        self.locator_strategies = locator_strategies

class FormTester:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.wait_time = 10
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Define field locators with multiple fallback strategies
        self.fields = {
            'name': FormFieldLocator('name', [
                (By.ID, 'name'),
                (By.NAME, 'name'),
                (By.CSS_SELECTOR, 'input[placeholder*="name" i]'),
                (By.XPATH, "//input[contains(@placeholder, 'name') or contains(@label, 'name')]"),
                (By.XPATH, "//label[contains(text(), 'Name')]/following::input[1]")
            ]),
            
            'email': FormFieldLocator('email', [
                (By.ID, 'email'),
                (By.NAME, 'email'),
                (By.CSS_SELECTOR, 'input[type="email"]'),
                (By.CSS_SELECTOR, 'input[placeholder*="email" i]'),
                (By.XPATH, "//label[contains(text(), 'Email')]/following::input[1]")
            ]),
            
            'phone': FormFieldLocator('phone', [
                (By.ID, 'mobile'),
                (By.NAME, 'mobile'),
                (By.CSS_SELECTOR, 'input[type="tel"]'),
                (By.CSS_SELECTOR, 'input[placeholder*="phone" i]'),
                (By.CSS_SELECTOR, 'input[placeholder*="mobile" i]'),
                (By.XPATH, "//label[contains(text(), 'phone')]/following::input[1]"),
                (By.XPATH, "//label[contains(text(), 'mobile')]/following::input[1]"),
            ])
        }

    def setup(self):
        """Initialize the webdriver"""
        self.driver = webdriver.Chrome()  # Make sure you have chromedriver installed
        self.driver.maximize_window()

    def teardown(self):
        """Clean up after tests"""
        if self.driver:
            self.driver.quit()

    def find_element_with_fallback(self, field_locator):
        """Try multiple locator strategies until one works"""
        for strategy, value in field_locator.locator_strategies:
            try:
                # First wait for element to be present
                element = WebDriverWait(self.driver, self.wait_time).until(
                    EC.presence_of_element_located((strategy, value))
                )
                # Then wait for it to be clickable
                element = WebDriverWait(self.driver, self.wait_time).until(
                    EC.element_to_be_clickable((strategy, value))
                )
                self.logger.info(f"Found {field_locator.name} field using {strategy}: {value}")
                return element
            except TimeoutException:
                continue
        
        raise Exception(f"Could not find {field_locator.name} field using any strategy")

    def test_form_fields(self):
        """Test the form fields"""
        try:
            # Navigate to the form
            self.driver.get(self.url)
            self.logger.info(f"Navigated to {self.url}")

            # Test data
            test_data = {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'phone': '1234567890'
            }

            # Test each field
            for field_name, test_value in test_data.items():
                field = self.find_element_with_fallback(self.fields[field_name])
                
                # Clear any existing value
                field.clear()
                
                # Enter test data
                field.send_keys(test_value)
                
                # Verify the entered value
                actual_value = field.get_attribute('value')
                assert actual_value == test_value, f"Value mismatch for {field_name}: expected {test_value}, got {actual_value}"
                
                self.logger.info(f"Successfully tested {field_name} field with value: {test_value}")

            self.logger.info("All form fields tested successfully!")
            return True

        except Exception as e:
            self.logger.error(f"Error during testing: {str(e)}")
            return False

def main():
    # URL of the form to test
    form_url = "http://app.cloudqa.io/home/AutomationPracticeForm"
    
    # Create and run the form tester
    tester = FormTester(form_url)
    
    try:
        tester.setup()
        success = tester.test_form_fields()
        print("Test completed successfully!" if success else "Test failed!")
    finally:
        tester.teardown()

if __name__ == "__main__":
    main()