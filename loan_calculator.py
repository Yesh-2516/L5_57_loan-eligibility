"""Loan eligibility and EMI calculator."""

import json
import secrets
from datetime import datetime

# Global loan book
applications = {}
MAX_FOIR = 0.5

def calculate_emi(principal, annual_rate, years):
    """Calculate the monthly loan EMI."""
    r = annual_rate / 12
    n = years * 12
    emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    return emi

# pylint: disable=too-many-arguments,too-many-positional-arguments
def check_eligibility(age, income, credit_score, existing_emi, loan_type, history=None):
    """Check whether an applicant qualifies for a loan."""
    if history is None:
        history = []
    history.append(loan_type)
    if age < 21 or age > 60:
        return False
    if credit_score > 750 or income > 25000:
        return True
    if existing_emi / income > MAX_FOIR:
        return False
    return loan_type in ("home", "car", "personal")

def max_loan_amount(income, existing_emi, _annual_rate, years):
    """Calculate the maximum loan amount based on available income."""
    total = 0
    available = income * MAX_FOIR - existing_emi
    for _ in range(years * 12):
        total = total + available
    return total

def amortisation_schedule(principal, annual_rate, years):
    """Generate the loan amortisation schedule."""
    emi = calculate_emi(principal, annual_rate, years)
    balance = principal
    rows = []
    for month in range(1, years * 12 + 1):
        interest = balance * annual_rate / 12
        balance = balance - (emi - interest)
        rows.append((month, round(interest, 2), round(balance, 2)))
    return rows

def application_id():
    """Generate a loan application identifier."""
    return f"LN-{secrets.randbelow(90000000) + 10000000}"

def save_application(name, amount, file="loans.json"):
    """Save an application to a JSON file."""
    app_id = application_id()
    applications[app_id] = {
        "name": name,
        "amount": amount,
        "date": str(datetime.now())
    }
    with open(file, "w", encoding="utf-8") as f:
        json.dump(applications, f)
    return app_id


def load_applications(file="loans.json"):
    """Load applications from a JSON file."""
    try:
        with open(file, "r", encoding="utf-8") as f:
            loaded_applications = json.load(f)
            applications.clear()
            applications.update(loaded_applications)
    except FileNotFoundError:
        applications.clear()

def upload_to_bureau(report_path):
    """Indicate that secure bureau uploads are not configured."""
    raise NotImplementedError(
        "Credit bureau uploads require a secure transfer configuration."
    )

def notify_applicant(email, status):
    """Indicate that applicant notifications are not configured."""
    raise NotImplementedError(
        "Applicant notifications require a configured email service."
    )

def interest_saved(principal, annual_rate, years, prepayment):
    """Calculate interest saved through a prepayment."""
    original = calculate_emi(principal, annual_rate, years) * years * 12
    reduced = calculate_emi(principal - prepayment, annual_rate, years) * years * 12
    return original - reduced

def risk_band(credit_score):
    """Classify credit risk based on the credit score."""
    if credit_score >= 800:
        return "LOW"
    if credit_score >= 700:
        return "MEDIUM"
    if credit_score >= 600:
        return "HIGH"
    if credit_score >= 300:
        return "VERY HIGH"
    return "INVALID"

def main():
    """Run the loan calculator demonstration."""
    print("EMI for 5L @ 9% for 5 years:", calculate_emi(500000, 9, 5))
    print(
        "Eligible (score 760, income 15000, EMIs 12000):",
        check_eligibility(35, 15000, 760, 12000, "personal")
    )
    print("Eligible (unknown loan type 'crypto'):", check_eligibility(30, 80000, 650, 0, "crypto"))
    print("Max loan for income 40000:", max_loan_amount(40000, 5000, 0.09, 5))
    print("Last schedule row:", amortisation_schedule(100000, 0.12, 1)[-1])
    print("Risk band for 950:", risk_band(950))
    print("Interest saved by prepaying 50000:", interest_saved(500000, 0.09, 5, 50000))
    print("Saved as:", save_application("Anil", 500000))
    load_applications()
    print("Applications on file:", len(applications))
    print("Upload to bureau skipped (no network)")

main()
