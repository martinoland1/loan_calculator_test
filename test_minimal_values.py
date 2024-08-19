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


def test_minimal_values(driver):
    minimum_amount = 400  # Minimum amount
    minimum_period = 5    # Minimum period

    expected_minimum_amount = 500
    expected_minimum_period = 6
    expected_monthly_payment = 91.11
    allowed_deviation = 10  # Allowed deviation

    # Open the loan application page
    driver.get(f"https://laenutaotlus.bigbank.ee/?amount={minimum_amount}&period={minimum_period}&productName=SMALL_LOAN&loanPurpose=DAILY_SETTLEMENTS")

    wait = WebDriverWait(driver, 30)
    modal = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "bb-modal__body")))

    # Enter the amount
    amount_input = modal.find_element(By.NAME, "header-calculator-amount")
    amount_input.clear()
    amount_input.send_keys(str(minimum_amount))

    # Enter the period
    period_input = modal.find_element(By.NAME, "header-calculator-period")
    period_input.send_keys(Keys.CONTROL + "a")
    period_input.send_keys(Keys.BACKSPACE)  # Remove value using BACKSPACE
    period_input.send_keys(str(minimum_period))

    # Click outside to trigger automatic update of the value
    driver.find_element(By.TAG_NAME, 'body').click()
    time.sleep(2)  # Wait for the webpage to process the automatic change

    # Check the period value
    period_input_value = float(period_input.get_attribute("value").replace(",", "."))
    print(f"Final Period Input Value: {period_input_value}")

    assert period_input_value >= expected_minimum_period, \
        f"Expected minimum period to be {expected_minimum_period} or higher, but got {period_input_value}"

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
        monthly_payment_ui_value = float(monthly_payment_ui.replace("€", "").replace(",", "."))
    except ValueError as e:
        raise

    # Print the monthly payment value
    print(f"Monthly Payment (UI): {monthly_payment_ui_value}")

    # Check the monthly payment, allowing ±10 deviation
    assert abs(monthly_payment_ui_value - expected_monthly_payment) <= allowed_deviation, \
        f"Expected {expected_monthly_payment} ± {allowed_deviation}, but got {monthly_payment_ui_value}"

    amount_input_value = float(amount_input.get_attribute("value").replace(",", "."))
    print(f"Amount Input Value (UI): {amount_input_value}")

    assert amount_input_value == expected_minimum_amount, \
        f"Expected minimum amount to be {expected_minimum_amount}, but got {amount_input_value}"
