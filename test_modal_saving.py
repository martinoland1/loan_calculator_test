import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope="module")
def driver():
    service = ChromeService(ChromeDriverManager().install())
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode if needed
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()

def test_modal_saving(driver):
    # Step 1: Open the loan application page
    driver.get("https://taotlus.bigbank.ee/?amount=5000&period=60&productName=SMALL_LOAN&loanPurpose=DAILY_SETTLEMENTS")

    # Wait for the modal to be visible
    wait = WebDriverWait(driver, 20)
    modal = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "bb-modal__body")))

    # Step 2: Modify loan amount and period
    amount_input = modal.find_element(By.NAME, "header-calculator-amount")
    period_input = modal.find_element(By.NAME, "header-calculator-period")
    
    # Clear existing values and input new values
    amount_input.clear()
    amount_input.send_keys("30000")

    period_input.clear()
    period_input.send_keys(Keys.CONTROL + "a")
    period_input.send_keys(Keys.BACKSPACE)  # Clear the existing value
    period_input.send_keys("100")

    # Allow some time for the values to be updated
    time.sleep(1)

    # Step 2.1: Verify values in the modal UI
    try:
        amount_display_modal = modal.find_element(By.XPATH, "//input[@name='header-calculator-amount']")
        updated_amount_modal = amount_display_modal.get_attribute("value").strip()
    except Exception as e:
        print("Error locating amount display in modal:", e)
        driver.quit()
        pytest.fail("Unable to locate amount display in modal.")

    # Print the updated amount value from the modal input
    print(f"Updated Amount in Modal (Input): {updated_amount_modal}")
    assert updated_amount_modal == "30,000", f"Expected amount to be '30,000', but got {updated_amount_modal}"

    try:
        period_display_modal = modal.find_element(By.XPATH, "//input[@name='header-calculator-period']")
        updated_period_modal = period_display_modal.get_attribute("value").strip()
    except Exception as e:
        print("Error locating period display in modal:", e)
        driver.quit()
        pytest.fail("Unable to locate period display in modal.")

    # Print the updated period value from the modal input
    print(f"Updated Period in Modal (Input): {updated_period_modal}")
    assert updated_period_modal == "100", f"Expected period to be '100', but got {updated_period_modal}"

    # Simulate closing the modal without saving changes
    close_button = modal.find_element(By.XPATH, "//button[contains(@class, 'bb-modal__close') and contains(@class, 'bb-button--icon')]")
    close_button.click()

    # Allow some time for the modal to close and UI to update
    time.sleep(2)

    # Step 4: Check the UI for the loan amount
    try:
        amount_display_element = driver.find_element(By.CLASS_NAME, "bb-edit-amount__amount")
        amount_display_text = amount_display_element.text.strip()
        amount_display_value = float(amount_display_text.replace("€", "").replace(",", ""))
    except Exception as e:
        print("Error locating amount display on UI:", e)
        driver.quit()
        pytest.fail("Unable to locate amount display on UI.")

    # Print the amount display value
    print(f"Amount Display Value (UI): {amount_display_value}")

    # Assert that the displayed amount is still the original value
    assert amount_display_value == 5000, f"Expected amount to be 5000, but got {amount_display_value}"

    # Step 5: Click on the displayed amount
    amount_display_element.click()

    # Step 6: Check input value for amount
    try:
        amount_input_value = driver.find_element(By.NAME, "header-calculator-amount").get_attribute("value")
        amount_input_value = float(amount_input_value.replace(",", ""))
    except Exception as e:
        print("Error locating amount input value:", e)
        driver.quit()
        pytest.fail("Unable to locate amount input value.")

    # Print the amount input value
    print(f"Amount Input Value: {amount_input_value}")

    assert amount_input_value == 5000, f"Expected amount input value to be 5000, but got {amount_input_value}"

    # Step 7: Check input value for period
    try:
        period_input_value = driver.find_element(By.NAME, "header-calculator-period").get_attribute("value")
        period_input_value = float(period_input_value.replace(",", ""))
    except Exception as e:
        print("Error locating period input value:", e)
        driver.quit()
        pytest.fail("Unable to locate period input value.")

    # Print the period input value
    print(f"Period Input Value: {period_input_value}")

    assert period_input_value == 60, f"Expected period input value to be 60, but got {period_input_value}"
