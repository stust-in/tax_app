"""
Core tax calculation engine.
Computes federal income tax, capital gains tax, FICA/SE tax,
NIIT, AMT estimate, state tax estimate, and total tax liability.
"""

from .tax_data import (
    FEDERAL_BRACKETS, LTCG_BRACKETS, STANDARD_DEDUCTION,
    NIIT_RATE, NIIT_THRESHOLDS,
    SOCIAL_SECURITY_RATE_EMPLOYEE, SOCIAL_SECURITY_RATE_SELF,
    SOCIAL_SECURITY_WAGE_BASE,
    MEDICARE_RATE_EMPLOYEE, MEDICARE_RATE_SELF,
    MEDICARE_ADDITIONAL_RATE, MEDICARE_ADDITIONAL_THRESHOLDS,
    AMT_EXEMPTION, AMT_EXEMPTION_PHASEOUT_START, AMT_RATES,
    STATE_TAX_RATES, NO_INCOME_TAX_STATES,
    MARRIED_JOINT,
)
from .income import AllIncome
from .deductions import (
    AllDeductions,
    compute_standard_deduction, compute_child_tax_credit,
    compute_child_care_credit, compute_education_credit,
    compute_energy_credits, compute_savers_credit,
    compute_eitc, compute_qbi_deduction,
)


class TaxResult:
    """Container for all computed tax values."""

    def __init__(self):
        # Income
        self.gross_income = 0.0
        self.agi = 0.0
        self.taxable_ordinary_income = 0.0

        # Deductions
        self.above_the_line_deductions = 0.0
        self.standard_deduction = 0.0
        self.itemized_deduction = 0.0
        self.deduction_used = 0.0
        self.deduction_type = "Standard"
        self.qbi_deduction = 0.0

        # Federal taxes
        self.federal_income_tax = 0.0
        self.ltcg_tax = 0.0
        self.niit = 0.0
        self.amt_tentative = 0.0

        # FICA
        self.employee_ss_tax = 0.0
        self.employee_medicare_tax = 0.0
        self.additional_medicare_tax = 0.0
        self.self_employment_tax = 0.0

        # Credits
        self.child_tax_credit = 0.0
        self.child_care_credit = 0.0
        self.education_credit = 0.0
        self.energy_credits = 0.0
        self.savers_credit = 0.0
        self.eitc = 0.0
        self.foreign_tax_credit = 0.0
        self.total_credits = 0.0

        # State
        self.state_tax_estimate = 0.0

        # Payments
        self.federal_withheld = 0.0
        self.state_withheld = 0.0
        self.ss_tax_withheld = 0.0
        self.medicare_tax_withheld = 0.0
        self.estimated_payments = 0.0

        # Totals
        self.total_federal_tax = 0.0
        self.total_fica = 0.0
        self.total_tax_liability = 0.0
        self.total_payments = 0.0
        self.balance_due = 0.0  # Positive = owe, negative = refund

        # Rates
        self.effective_rate = 0.0
        self.marginal_rate = 0.0

        # Capital losses
        self.capital_loss_carryforward = 0.0


def compute_bracket_tax(taxable_income: float, brackets: list) -> float:
    """Compute tax using progressive brackets."""
    tax = 0.0
    prev_bound = 0
    for upper_bound, rate in brackets:
        if upper_bound is None:
            tax += (taxable_income - prev_bound) * rate
            break
        if taxable_income <= upper_bound:
            tax += (taxable_income - prev_bound) * rate
            break
        tax += (upper_bound - prev_bound) * rate
        prev_bound = upper_bound
    return tax


def get_marginal_rate(taxable_income: float, brackets: list) -> float:
    """Find the marginal tax rate for given income."""
    prev_bound = 0
    for upper_bound, rate in brackets:
        if upper_bound is None or taxable_income <= upper_bound:
            return rate
        prev_bound = upper_bound
    return brackets[-1][1]


def compute_ltcg_tax(ltcg: float, ordinary_taxable: float, brackets: list) -> float:
    """Compute long-term capital gains tax considering stacking on ordinary income."""
    if ltcg <= 0:
        return 0

    tax = 0.0
    total_income = ordinary_taxable
    remaining_gains = ltcg

    prev_bound = 0
    for upper_bound, rate in brackets:
        if upper_bound is None:
            tax += remaining_gains * rate
            break

        # How much room is in this bracket above ordinary income
        bracket_start = max(prev_bound, total_income)
        if bracket_start >= upper_bound:
            prev_bound = upper_bound
            continue

        room = upper_bound - bracket_start
        gains_in_bracket = min(remaining_gains, room)
        tax += gains_in_bracket * rate
        remaining_gains -= gains_in_bracket
        total_income += gains_in_bracket

        if remaining_gains <= 0:
            break
        prev_bound = upper_bound

    return tax


def compute_niit(investment_income: float, agi: float, filing_status: str) -> float:
    """Net Investment Income Tax (3.8%)."""
    threshold = NIIT_THRESHOLDS[filing_status]
    if agi <= threshold:
        return 0
    excess = agi - threshold
    return NIIT_RATE * min(investment_income, excess)


def compute_self_employment_tax(se_net_income: float, w2_wages: float) -> tuple:
    """Compute self-employment tax (Social Security + Medicare)."""
    if se_net_income <= 0:
        return 0.0, 0.0, 0.0

    taxable_se = se_net_income * 0.9235  # 92.35% is subject to SE tax

    # Social Security: 12.4% up to wage base, minus W-2 wages already taxed
    ss_remaining = max(0, SOCIAL_SECURITY_WAGE_BASE - w2_wages)
    ss_tax = min(taxable_se, ss_remaining) * SOCIAL_SECURITY_RATE_SELF

    # Medicare: 2.9% on all SE income
    medicare_tax = taxable_se * MEDICARE_RATE_SELF

    total = ss_tax + medicare_tax
    deductible_half = total / 2

    return total, deductible_half, taxable_se


def compute_amt(agi: float, filing_status: str, itemized_salt: float) -> float:
    """Simplified AMT calculation."""
    # Add back SALT deduction and other AMT preferences
    amti = agi + itemized_salt  # Simplified: just SALT add-back

    exemption = AMT_EXEMPTION[filing_status]
    phaseout_start = AMT_EXEMPTION_PHASEOUT_START[filing_status]

    if amti > phaseout_start:
        exemption_reduction = (amti - phaseout_start) * 0.25
        exemption = max(0, exemption - exemption_reduction)

    amt_base = max(0, amti - exemption)
    amt = compute_bracket_tax(amt_base, AMT_RATES)
    return amt


def compute_state_tax(taxable_income: float, state: str) -> float:
    """Simplified state tax estimate using top marginal rate."""
    if state in NO_INCOME_TAX_STATES:
        return 0.0
    rate = STATE_TAX_RATES.get(state, 0.05)
    return taxable_income * rate


def calculate_taxes(income: AllIncome, deductions: AllDeductions) -> TaxResult:
    """Main tax calculation bringing everything together."""
    r = TaxResult()
    fs = deductions.personal.filing_status
    brackets = FEDERAL_BRACKETS[fs]

    # --- Gross income ---
    r.gross_income = income.total_agi_estimate

    # --- Above-the-line deductions ---
    r.above_the_line_deductions = deductions.above_the_line.total

    # --- AGI ---
    r.agi = max(0, r.gross_income - r.above_the_line_deductions)

    # --- Standard vs Itemized ---
    r.standard_deduction = compute_standard_deduction(deductions.personal)
    r.itemized_deduction = deductions.itemized.total(r.agi)

    if r.itemized_deduction > r.standard_deduction:
        r.deduction_used = r.itemized_deduction
        r.deduction_type = "Itemized"
        deductions.use_itemized = True
    else:
        r.deduction_used = r.standard_deduction
        r.deduction_type = "Standard"

    # --- QBI Deduction ---
    se_net = income.self_employment.net_income
    preliminary_taxable = max(0, r.agi - r.deduction_used)
    r.qbi_deduction = compute_qbi_deduction(se_net, preliminary_taxable, fs)

    # --- Taxable ordinary income ---
    # Separate LTCG + qualified dividends (taxed at preferential rates)
    ltcg_and_qual_div = max(0, income.net_long_term_gains) + income.stocks.qualified_dividends
    total_taxable = max(0, r.agi - r.deduction_used - r.qbi_deduction)
    r.taxable_ordinary_income = max(0, total_taxable - ltcg_and_qual_div)

    # --- Federal income tax on ordinary income ---
    r.federal_income_tax = compute_bracket_tax(r.taxable_ordinary_income, brackets)
    r.marginal_rate = get_marginal_rate(r.taxable_ordinary_income, brackets)

    # --- Long-term capital gains + qualified dividends tax ---
    r.ltcg_tax = compute_ltcg_tax(
        ltcg_and_qual_div, r.taxable_ordinary_income, LTCG_BRACKETS[fs]
    )

    # --- NIIT ---
    r.niit = compute_niit(income.total_investment_income, r.agi, fs)

    # --- AMT estimate ---
    salt_addback = 0
    if deductions.use_itemized:
        salt_addback = min(
            deductions.itemized.state_local_income_tax + deductions.itemized.property_tax,
            10_000,
        )
    r.amt_tentative = compute_amt(r.agi, fs, salt_addback)
    # AMT only applies if tentative AMT > regular tax
    regular_tax = r.federal_income_tax + r.ltcg_tax
    amt_additional = max(0, r.amt_tentative - regular_tax)

    # --- Total federal income tax ---
    r.total_federal_tax = r.federal_income_tax + r.ltcg_tax + r.niit + amt_additional

    # --- FICA / Self-Employment Tax ---
    r.employee_ss_tax = income.total_ss_tax_paid
    r.employee_medicare_tax = income.total_medicare_tax_paid

    # Additional Medicare Tax
    medicare_threshold = MEDICARE_ADDITIONAL_THRESHOLDS[fs]
    total_wages = income.total_w2_wages + se_net
    if total_wages > medicare_threshold:
        r.additional_medicare_tax = (total_wages - medicare_threshold) * MEDICARE_ADDITIONAL_RATE

    # Self-employment tax
    se_tax, se_deduction, _ = compute_self_employment_tax(se_net, income.total_w2_wages)
    r.self_employment_tax = se_tax

    r.total_fica = (
        r.employee_ss_tax + r.employee_medicare_tax
        + r.additional_medicare_tax + r.self_employment_tax
    )

    # --- Credits ---
    r.child_tax_credit = compute_child_tax_credit(deductions.credits, fs, r.agi)
    r.child_care_credit = compute_child_care_credit(deductions.credits, r.agi)
    r.education_credit = compute_education_credit(deductions.credits, r.agi, fs)
    r.energy_credits = compute_energy_credits(deductions.credits)
    r.savers_credit = compute_savers_credit(deductions.credits, r.agi, fs)
    r.eitc = compute_eitc(fs, r.agi, deductions.credits.num_children_under_17)
    r.foreign_tax_credit = deductions.credits.foreign_tax_paid

    r.total_credits = (
        r.child_tax_credit + r.child_care_credit + r.education_credit
        + r.energy_credits + r.savers_credit + r.eitc + r.foreign_tax_credit
    )

    # Credits reduce federal tax (not below zero for non-refundable)
    # EITC and part of CTC are refundable — simplified here
    r.total_federal_tax = max(0, r.total_federal_tax - r.total_credits)

    # --- State tax estimate ---
    r.state_tax_estimate = compute_state_tax(total_taxable, deductions.personal.state)

    # --- Capital loss carryforward ---
    r.capital_loss_carryforward = income.capital_loss_carryforward

    # --- Total tax liability ---
    r.total_tax_liability = r.total_federal_tax + r.total_fica + r.state_tax_estimate

    # --- Payments already made ---
    r.federal_withheld = income.total_federal_withheld
    r.state_withheld = income.total_state_withheld
    r.ss_tax_withheld = income.total_ss_tax_paid
    r.medicare_tax_withheld = income.total_medicare_tax_paid
    r.estimated_payments = deductions.credits.estimated_taxes_paid

    r.total_payments = (
        r.federal_withheld + r.state_withheld
        + r.ss_tax_withheld + r.medicare_tax_withheld
        + r.estimated_payments
    )

    # --- Balance due / refund ---
    r.balance_due = r.total_tax_liability - r.total_payments

    # --- Effective rate ---
    if r.gross_income > 0:
        r.effective_rate = r.total_tax_liability / r.gross_income

    return r
