import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys


@pytest.fixture(scope="module")
def driver():
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    yield driver
    driver.quit()


def test_maximal_values(driver):
    # Values set for testing that exceed the maximum limits
    test_amount = 40000  
    test_period = 200   

    maximum_amount = 30000  # Maximum amount
    maximum_period = 120    # Maximum period

    expected_amount = maximum_amount  # Expected amount if the page correctly applies limits
    expected_period = maximum_period  # Expected period if the page correctly applies limits
    expected_monthly_payment = 526.05  # Maximum expected payment amount

    tolerance = 10.0  # Tolerance ±10 with the amount

    # Open the loan application page
    driver.get(f"https://laenutaotlus.bigbank.ee/?amount={test_amount}&period={test_period}&productName=SMALL_LOAN&loanPurpose=DAILY_SETTLEMENTS")

    wait = WebDriverWait(driver, 30)
    modal = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "bb-modal__body")))

    # Enter the amount
    amount_input = modal.find_element(By.NAME, "header-calculator-amount")
    amount_input.clear()
    amount_input.send_keys(str(test_amount))

    # Enter the period
    period_input = modal.find_element(By.NAME, "header-calculator-period")
    period_input.send_keys(Keys.CONTROL + "a")
    period_input.send_keys(Keys.BACKSPACE)  # Remove value using BACKSPACE
    period_input.send_keys(str(test_period))

    # Click outside to trigger automatic update of the value
    driver.find_element(By.TAG_NAME, 'body').click()
    time.sleep(2)  # Wait for the webpage to process the automatic change

    # Check the period value
    period_input_value = float(period_input.get_attribute("value").replace(",", "."))
    print(f"Final Period Input Value: {period_input_value}")

    assert period_input_value <= expected_period, \
        f"Expected maximum period to be {expected_period} or less, but got {period_input_value}"

    # Check the monthly payment
    monthly_payment_element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "bb-labeled-value__value"))
    )
    WebDriverWait(driver, 30).until(
        EC.text_to_be_present_in_element((By.CLASS_NAME, "bb-labeled-value__value"), "€")
    )

    monthly_payment_ui = monthly_payment_element.text.strip()
    if not monthly_payment_ui:
        raise ValueError("Monthly payment UI text is empty.")

    try:
        # Removes commas before conversion
        monthly_payment_ui_value = float(monthly_payment_ui.replace("€", "").replace(",", "").replace(" ", ""))
    except ValueError as e:
        raise

    # Print the monthly payment value
    print(f"Monthly Payment (UI): {monthly_payment_ui_value}")

    # Check if the monthly payment value falls within the expected limits with tolerance
    min_expected_payment = expected_monthly_payment - tolerance
    max_expected_payment = expected_monthly_payment + tolerance

    assert min_expected_payment <= monthly_payment_ui_value <= max_expected_payment, \
        f"Expected monthly payment to be between {min_expected_payment} and {max_expected_payment}, but got {monthly_payment_ui_value}"

    amount_input_value = float(amount_input.get_attribute("value").replace(",", ""))
    print(f"Amount Input Value (UI): {amount_input_value}")

    assert amount_input_value <= expected_amount, \
        f"Expected maximum amount to be {expected_amount} or less, but got {amount_input_value}"
