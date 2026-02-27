#!/usr/bin/env python3
"""
2025 Tax Year Calculator (for filing in 2026)
A comprehensive federal + state tax estimator with personalized optimization tips.

Covers: W-2 income, RSU/GSU, stock sales, ESPP, crypto, freelance/1099,
        dividends, interest, rental income, retirement distributions,
        all major deductions, credits, and tax-saving strategies.

DISCLAIMER: This is an estimator for educational purposes. Consult a qualified
tax professional for official tax advice.
"""

import sys
from .income import collect_all_income, AllIncome
from .deductions import collect_all_deductions, AllDeductions
from .calculator import calculate_taxes, TaxResult
from .tips import generate_tips, print_tips
from .tax_data import FILING_STATUS_LABELS, STATE_TAX_RATES, NO_INCOME_TAX_STATES


BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║              2025 TAX CALCULATOR & OPTIMIZER                 ║
║              ──────────────────────────────                  ║
║              For Tax Year 2025 (Filing 2026)                 ║
║                                                              ║
║  Covers: W-2 · RSU/GSU · Stocks · ESPP · Crypto · 1099     ║
║          Dividends · Interest · Rental · Retirement          ║
║          All major deductions, credits & tax tips            ║
║                                                              ║
║  DISCLAIMER: This is an estimator. Consult a tax pro        ║
║  for official advice.                                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""


def print_summary(result: TaxResult, deductions: AllDeductions, income: AllIncome):
    """Print a detailed, formatted tax summary."""
    fs_label = FILING_STATUS_LABELS[deductions.personal.filing_status]
    state = deductions.personal.state

    print("\n")
    print("=" * 60)
    print("              YOUR 2025 TAX SUMMARY")
    print("=" * 60)

    # --- Filing Info ---
    print(f"\n  Filing Status:    {fs_label}")
    print(f"  State:            {state}")
    print(f"  Age:              {deductions.personal.age}")

    # --- Income Breakdown ---
    print("\n" + "-" * 60)
    print("  INCOME")
    print("-" * 60)
    if income.total_w2_wages > 0:
        print(f"  W-2 Wages:                        ${income.total_w2_wages:>12,.0f}")
    if income.stocks.rsu_gsu_vesting_income > 0:
        print(f"    (includes RSU/GSU vesting:       ${income.stocks.rsu_gsu_vesting_income:>12,.0f})")
    if income.self_employment.net_income > 0:
        print(f"  Self-Employment (net):             ${income.self_employment.net_income:>12,.0f}")
    if income.net_short_term_gains != 0:
        print(f"  Short-Term Capital Gains:          ${income.net_short_term_gains:>12,.0f}")
    if income.net_long_term_gains != 0:
        print(f"  Long-Term Capital Gains:           ${income.net_long_term_gains:>12,.0f}")
    if income.stocks.qualified_dividends > 0:
        print(f"  Qualified Dividends:               ${income.stocks.qualified_dividends:>12,.0f}")
    if income.stocks.ordinary_dividends > 0:
        print(f"  Ordinary Dividends:                ${income.stocks.ordinary_dividends:>12,.0f}")
    if income.stocks.espp_discount_income > 0:
        print(f"  ESPP Discount Income:              ${income.stocks.espp_discount_income:>12,.0f}")
    if income.other.interest_income > 0:
        print(f"  Interest Income:                   ${income.other.interest_income:>12,.0f}")
    if income.other.rental_income_net != 0:
        print(f"  Rental Income (net):               ${income.other.rental_income_net:>12,.0f}")
    if income.other.retirement_distributions > 0:
        print(f"  Retirement Distributions:          ${income.other.retirement_distributions:>12,.0f}")
    if income.other.crypto_gains_short - income.other.crypto_losses_short != 0:
        net_crypto_st = income.other.crypto_gains_short - income.other.crypto_losses_short
        print(f"  Crypto Short-Term (net):           ${net_crypto_st:>12,.0f}")
    if income.other.crypto_gains_long - income.other.crypto_losses_long != 0:
        net_crypto_lt = income.other.crypto_gains_long - income.other.crypto_losses_long
        print(f"  Crypto Long-Term (net):            ${net_crypto_lt:>12,.0f}")
    if income.other.other_income > 0:
        print(f"  Other Income:                      ${income.other.other_income:>12,.0f}")

    print(f"                                     {'─' * 13}")
    print(f"  Gross Income:                      ${result.gross_income:>12,.0f}")

    # --- Deductions ---
    print("\n" + "-" * 60)
    print("  DEDUCTIONS")
    print("-" * 60)
    if result.above_the_line_deductions > 0:
        print(f"  Above-the-Line Deductions:        -${result.above_the_line_deductions:>12,.0f}")
        atl = deductions.above_the_line
        if atl.traditional_ira_contribution > 0:
            print(f"    Traditional IRA:                 ${atl.traditional_ira_contribution:>12,.0f}")
        if atl.hsa_contribution > 0:
            print(f"    HSA Contribution:                ${atl.hsa_contribution:>12,.0f}")
        if atl.student_loan_interest > 0:
            print(f"    Student Loan Interest:           ${atl.student_loan_interest:>12,.0f}")
        if atl.self_employment_tax_deduction > 0:
            print(f"    SE Tax Deduction (50%):          ${atl.self_employment_tax_deduction:>12,.0f}")
        if atl.self_employment_health_insurance > 0:
            print(f"    SE Health Insurance:             ${atl.self_employment_health_insurance:>12,.0f}")
        if atl.educator_expenses > 0:
            print(f"    Educator Expenses:               ${atl.educator_expenses:>12,.0f}")

    print(f"\n  Adjusted Gross Income (AGI):       ${result.agi:>12,.0f}")

    print(f"\n  Standard Deduction:                ${result.standard_deduction:>12,.0f}")
    print(f"  Itemized Deductions:               ${result.itemized_deduction:>12,.0f}")
    print(f"  >>> Using {result.deduction_type} Deduction:       -${result.deduction_used:>12,.0f}")
    if result.qbi_deduction > 0:
        print(f"  QBI Deduction (Sec 199A):         -${result.qbi_deduction:>12,.0f}")

    taxable = max(0, result.agi - result.deduction_used - result.qbi_deduction)
    print(f"\n  Taxable Income:                    ${taxable:>12,.0f}")

    # --- Federal Tax ---
    print("\n" + "-" * 60)
    print("  FEDERAL TAX")
    print("-" * 60)
    print(f"  Income Tax (ordinary rates):       ${result.federal_income_tax:>12,.0f}")
    print(f"  Long-Term CG / Qual Div Tax:       ${result.ltcg_tax:>12,.0f}")
    if result.niit > 0:
        print(f"  Net Investment Income Tax (3.8%):  ${result.niit:>12,.0f}")
    if result.amt_tentative > result.federal_income_tax + result.ltcg_tax:
        amt_extra = result.amt_tentative - result.federal_income_tax - result.ltcg_tax
        print(f"  AMT (additional):                  ${amt_extra:>12,.0f}")
    print(f"  Marginal Tax Rate:                  {result.marginal_rate * 100:>11.1f}%")

    # --- Credits ---
    if result.total_credits > 0:
        print(f"\n  Tax Credits:")
        if result.child_tax_credit > 0:
            print(f"    Child Tax Credit:               -${result.child_tax_credit:>12,.0f}")
        if result.child_care_credit > 0:
            print(f"    Child/Dependent Care Credit:    -${result.child_care_credit:>12,.0f}")
        if result.education_credit > 0:
            print(f"    Education Credit:               -${result.education_credit:>12,.0f}")
        if result.energy_credits > 0:
            print(f"    Energy Credits:                 -${result.energy_credits:>12,.0f}")
        if result.savers_credit > 0:
            print(f"    Saver's Credit:                 -${result.savers_credit:>12,.0f}")
        if result.eitc > 0:
            print(f"    Earned Income Credit:           -${result.eitc:>12,.0f}")
        if result.foreign_tax_credit > 0:
            print(f"    Foreign Tax Credit:             -${result.foreign_tax_credit:>12,.0f}")
        print(f"    Total Credits:                  -${result.total_credits:>12,.0f}")

    print(f"\n  Federal Tax After Credits:          ${result.total_federal_tax:>12,.0f}")

    # --- FICA ---
    print("\n" + "-" * 60)
    print("  FICA / SELF-EMPLOYMENT TAX")
    print("-" * 60)
    print(f"  Social Security Tax (withheld):     ${result.employee_ss_tax:>12,.0f}")
    print(f"  Medicare Tax (withheld):            ${result.employee_medicare_tax:>12,.0f}")
    if result.additional_medicare_tax > 0:
        print(f"  Additional Medicare Tax (0.9%):    ${result.additional_medicare_tax:>12,.0f}")
    if result.self_employment_tax > 0:
        print(f"  Self-Employment Tax:               ${result.self_employment_tax:>12,.0f}")
    print(f"  Total FICA:                         ${result.total_fica:>12,.0f}")

    # --- State Tax ---
    print("\n" + "-" * 60)
    print("  STATE TAX ESTIMATE")
    print("-" * 60)
    if state in NO_INCOME_TAX_STATES:
        print(f"  {state} has no state income tax!     ${0:>12,.0f}")
    else:
        rate = STATE_TAX_RATES.get(state, 0.05)
        print(f"  {state} estimated ({rate*100:.1f}% simplified): ${result.state_tax_estimate:>12,.0f}")

    # --- Grand Total ---
    print("\n" + "=" * 60)
    print("  TOTAL TAX LIABILITY")
    print("=" * 60)
    print(f"  Federal Tax:                       ${result.total_federal_tax:>12,.0f}")
    print(f"  FICA:                              ${result.total_fica:>12,.0f}")
    print(f"  State Tax:                         ${result.state_tax_estimate:>12,.0f}")
    print(f"                                     {'═' * 13}")
    print(f"  TOTAL TAX:                         ${result.total_tax_liability:>12,.0f}")
    print(f"  Effective Tax Rate:                  {result.effective_rate * 100:>11.1f}%")

    # --- Payments & Balance ---
    print("\n" + "-" * 60)
    print("  PAYMENTS & WITHHOLDING")
    print("-" * 60)
    print(f"  Federal Tax Withheld:              ${result.federal_withheld:>12,.0f}")
    print(f"  State Tax Withheld:                ${result.state_withheld:>12,.0f}")
    print(f"  SS + Medicare Withheld:            ${result.ss_tax_withheld + result.medicare_tax_withheld:>12,.0f}")
    if result.estimated_payments > 0:
        print(f"  Estimated Payments:                ${result.estimated_payments:>12,.0f}")
    print(f"                                     {'─' * 13}")
    print(f"  Total Payments:                    ${result.total_payments:>12,.0f}")

    print("\n" + "=" * 60)
    if result.balance_due > 0:
        print(f"  >>> YOU OWE:                       ${result.balance_due:>12,.0f}")
    elif result.balance_due < 0:
        print(f"  >>> ESTIMATED REFUND:              ${abs(result.balance_due):>12,.0f}")
    else:
        print(f"  >>> YOU'RE EVEN!                   ${0:>12,.0f}")
    print("=" * 60)

    if result.capital_loss_carryforward > 0:
        print(f"\n  Note: Capital loss carryforward to next year: ${result.capital_loss_carryforward:,.0f}")


def main():
    """Main entry point for the tax calculator."""
    print(BANNER)

    try:
        # Step 1: Collect all income
        print("\n" + "=" * 60)
        print("STEP 1 OF 3: INCOME")
        print("=" * 60)
        income = collect_all_income()

        # Step 2: Collect deductions, credits, and personal info
        print("\n" + "=" * 60)
        print("STEP 2 OF 3: DEDUCTIONS & CREDITS")
        print("=" * 60)
        deductions = collect_all_deductions(income.self_employment.net_income)

        # Step 3: Calculate and display results
        print("\n" + "=" * 60)
        print("STEP 3 OF 3: CALCULATING YOUR TAXES...")
        print("=" * 60)
        result = calculate_taxes(income, deductions)
        print_summary(result, deductions, income)

        # Step 4: Tax optimization tips
        tips = generate_tips(income, deductions, result)
        print_tips(tips)

        print("\n" + "=" * 60)
        print("  Thank you for using the 2025 Tax Calculator!")
        print("  Remember: this is an estimate. Consult a CPA or")
        print("  use official tax software for filing.")
        print("=" * 60 + "\n")

    except KeyboardInterrupt:
        print("\n\n  Calculation cancelled. Goodbye!")
        sys.exit(0)
    except EOFError:
        print("\n\n  Input ended. Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
