import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope="module")
def driver():
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    yield driver
    driver.quit()

def get_loan_calculation_data(amount, period):
    url = "https://taotlus.bigbank.ee/api/v1/loan/calculate"
    payload = {
        "productType": "SMALL_LOAN_EE01",
        "maturity": period,
        "amount": amount,
        "interestRate": 16.8,
        "administrationFee": 3.49,
        "conclusionFee": 100,
        "monthlyPaymentDay": 15,
        "currency": "EUR"
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # See viskab veateate, kui vastus ei ole 200 OK

    # Prindi response välja
    print("API Response on:", response.json())

    return response.json()


def test_loan_calculator(driver):
    amount = 5000
    period = 60

    # Fetch data from API
    api_data = get_loan_calculation_data(amount, period)
    expected_monthly_payment = api_data['monthlyPayment']
    expected_apr = api_data['apr']
    print(f"APRC from API: {expected_apr}")

    # Open the loan application page
    driver.get(f"https://laenutaotlus.bigbank.ee/?amount={amount}&period={period}&productName=SMALL_LOAN&loanPurpose=DAILY_SETTLEMENTS")

    wait = WebDriverWait(driver, 20)
    modal = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "bb-modal__body")))

    # Input values into the calculator
    amount_input = modal.find_element(By.NAME, "header-calculator-amount")
    amount_input.clear()
    amount_input.send_keys(str(amount))

    period_input = modal.find_element(By.NAME, "header-calculator-period")
    period_input.clear()
    period_input.send_keys(str(period))

    # Additional wait to ensure results are fully loaded
    WebDriverWait(driver, 50).until(
        EC.presence_of_element_located((By.CLASS_NAME, "bb-labeled-value__value"))
    )

    # Ensure that the element is not empty
    monthly_payment_element = driver.find_element(By.CLASS_NAME, "bb-labeled-value__value")
    WebDriverWait(driver, 50).until(
        EC.text_to_be_present_in_element((By.CLASS_NAME, "bb-labeled-value__value"), "€")
    )

    # Extract and clean the text
    monthly_payment_ui = monthly_payment_element.text.strip()  # Remove extra whitespace

    if not monthly_payment_ui:
        print("Monthly payment UI text is empty. Check if the calculator results are loaded properly.")
        raise ValueError("Monthly payment UI text is empty. Check if the calculator results are loaded properly.")

    try:
        # Convert the value to float
        monthly_payment_ui_value = float(monthly_payment_ui.replace("€", "").replace(",", "."))
    except ValueError as e:
        print(f"Error converting monthly payment UI text to float: {e}")
        raise

    print(f"Monthly Payment (UI): {monthly_payment_ui_value}")
    
    assert abs(monthly_payment_ui_value - expected_monthly_payment) < 0.1, \
    f"Expected {expected_monthly_payment}, but got {monthly_payment_ui_value}"
    
    # Check APRC value with ±1% tolerance around 21%
    target_apr = 21.0
    tolerance_percentage = 1  # ±1%
    tolerance = tolerance_percentage  # ±1% of target APR
    min_apr = target_apr - tolerance
    max_apr = target_apr + tolerance

    print(f"Expected APR range: {min_apr} - {max_apr}")
    assert min_apr <= expected_apr <= max_apr, \
        f"Expected APR to be within range {min_apr} - {max_apr}, but got {expected_apr}"



if __name__ == "__main__":
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    service = Service("bigbank/chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        test_loan_calculator(driver)
    finally:
        driver.quit()
