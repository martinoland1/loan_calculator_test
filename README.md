# Loan Calculator Automation Tests

This repository contains automated tests for verifying the functionality of the loan calculator on the Bigbank website.

## Requirements

- Python 3.x
- `pip` package manager
- ChromeDriver
- pytest


**Install Dependencies**

Install the required Python packages using pip:

`pip install -r requirements.txt`

Ensure you have ChromeDriver installed and its path added to your system's environment variables.

**Run the Tests**

To generate an HTML report using pytest-html, run the following command in your terminal:

`pytest --html=report.html --self-contained-html`

Test Scenarios

Loan Calculation: Validates that the monthly payment and APRC values are correctly calculated based on the provided input.
Boundary Testing: Verifies that the calculator enforces maximum limits on loan amount and period.
API Integration: Compares the UI results with the expected values from the API to ensure consistency.
