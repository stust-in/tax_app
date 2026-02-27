"""
Deductions and credits collection and calculation.
Handles standard vs. itemized deduction, above-the-line deductions,
and all major tax credits.
"""

from dataclasses import dataclass, field
from .tax_data import (
    STANDARD_DEDUCTION, ADDITIONAL_STD_DEDUCTION, SALT_CAP,
    STUDENT_LOAN_INTEREST_MAX, STUDENT_LOAN_PHASEOUT,
    EDUCATOR_EXPENSE_MAX, RETIREMENT_LIMITS,
    CHILD_TAX_CREDIT, CHILD_TAX_CREDIT_OTHER_DEPENDENT,
    CTC_PHASEOUT_START, CTC_PHASEOUT_RATE,
    EITC_MAX, EITC_INCOME_LIMITS_SINGLE, EITC_INCOME_LIMITS_JOINT,
    QBI_DEDUCTION_RATE, QBI_INCOME_THRESHOLD,
    SINGLE, MARRIED_JOINT, MARRIED_SEPARATE, HEAD_OF_HOUSEHOLD,
)
from .income import ask_float, ask_yes_no


@dataclass
class AboveTheLineDeductions:
    """Deductions taken before AGI (reduce AGI directly)."""
    traditional_ira_contribution: float = 0.0
    hsa_contribution: float = 0.0  # Personal contributions (not employer)
    student_loan_interest: float = 0.0
    educator_expenses: float = 0.0
    self_employment_tax_deduction: float = 0.0  # Calculated automatically
    self_employment_health_insurance: float = 0.0
    alimony_paid: float = 0.0  # Pre-2019 agreements only
    moving_expenses_military: float = 0.0

    @property
    def total(self) -> float:
        return (
            self.traditional_ira_contribution
            + self.hsa_contribution
            + self.student_loan_interest
            + self.educator_expenses
            + self.self_employment_tax_deduction
            + self.self_employment_health_insurance
            + self.alimony_paid
            + self.moving_expenses_military
        )


@dataclass
class ItemizedDeductions:
    """Schedule A itemized deductions."""
    state_local_income_tax: float = 0.0  # Or sales tax
    property_tax: float = 0.0
    mortgage_interest: float = 0.0  # On up to $750k of debt
    mortgage_insurance_premiums: float = 0.0
    charitable_cash: float = 0.0
    charitable_non_cash: float = 0.0
    medical_expenses: float = 0.0  # Only amount exceeding 7.5% of AGI
    casualty_losses_disaster: float = 0.0  # Federally declared disasters only

    def total(self, agi: float) -> float:
        # SALT capped at $10,000
        salt = min(self.state_local_income_tax + self.property_tax, SALT_CAP)

        # Medical: only portion exceeding 7.5% of AGI
        medical = max(0, self.medical_expenses - 0.075 * agi)

        return (
            salt
            + self.mortgage_interest
            + self.mortgage_insurance_premiums
            + self.charitable_cash
            + self.charitable_non_cash
            + medical
            + self.casualty_losses_disaster
        )


@dataclass
class TaxCredits:
    """Tax credits that reduce tax owed dollar-for-dollar."""
    num_children_under_17: int = 0
    num_other_dependents: int = 0
    child_care_expenses: float = 0.0
    num_children_for_care: int = 0  # 1 or 2+
    education_expenses: float = 0.0  # For American Opportunity / Lifetime Learning
    years_of_aotc_claimed: int = 0  # American Opportunity is max 4 years
    energy_efficient_improvements: float = 0.0
    ev_purchase: bool = False
    ev_purchase_amount: float = 0.0
    residential_solar: float = 0.0
    adoption_expenses: float = 0.0
    savers_credit_eligible: bool = False
    retirement_contributions_for_savers: float = 0.0
    foreign_tax_paid: float = 0.0
    estimated_taxes_paid: float = 0.0


@dataclass
class PersonalInfo:
    filing_status: str = SINGLE
    age: int = 30
    spouse_age: int = 0
    is_blind: bool = False
    spouse_is_blind: bool = False
    state: str = "CA"
    is_educator: bool = False
    has_employer_retirement_plan: bool = False


@dataclass
class AllDeductions:
    personal: PersonalInfo = field(default_factory=PersonalInfo)
    above_the_line: AboveTheLineDeductions = field(default_factory=AboveTheLineDeductions)
    itemized: ItemizedDeductions = field(default_factory=ItemizedDeductions)
    credits: TaxCredits = field(default_factory=TaxCredits)
    use_itemized: bool = False  # Set after comparison


def collect_personal_info() -> PersonalInfo:
    """Gather filing status and basic info."""
    info = PersonalInfo()
    print("\n" + "=" * 60)
    print("PERSONAL INFORMATION")
    print("=" * 60)

    print("\nFiling status:")
    print("  1) Single")
    print("  2) Married Filing Jointly")
    print("  3) Married Filing Separately")
    print("  4) Head of Household")
    choice = input("  Choose [1-4, default 1]: ").strip()
    statuses = {"1": SINGLE, "2": MARRIED_JOINT, "3": MARRIED_SEPARATE, "4": HEAD_OF_HOUSEHOLD}
    info.filing_status = statuses.get(choice, SINGLE)

    try:
        age_input = input("  Your age [30]: ").strip()
        info.age = int(age_input) if age_input else 30
    except ValueError:
        info.age = 30

    if info.filing_status in (MARRIED_JOINT, MARRIED_SEPARATE):
        try:
            age_input = input("  Spouse's age [30]: ").strip()
            info.spouse_age = int(age_input) if age_input else 30
        except ValueError:
            info.spouse_age = 30
        info.spouse_is_blind = ask_yes_no("Is your spouse legally blind?")

    info.is_blind = ask_yes_no("Are you legally blind?")

    state_input = input("  Your state (2-letter code) [CA]: ").strip().upper()
    info.state = state_input if len(state_input) == 2 else "CA"

    info.is_educator = ask_yes_no("Are you a K-12 educator?")
    info.has_employer_retirement_plan = ask_yes_no("Are you covered by an employer retirement plan (401k, pension)?")

    return info


def collect_above_the_line(personal: PersonalInfo, se_net_income: float) -> AboveTheLineDeductions:
    """Collect above-the-line (adjustments to income) deductions."""
    atl = AboveTheLineDeductions()
    print("\n" + "=" * 60)
    print("ABOVE-THE-LINE DEDUCTIONS (reduce your AGI)")
    print("=" * 60)

    # Traditional IRA
    limit = RETIREMENT_LIMITS["ira"]
    if personal.age >= 50:
        limit += RETIREMENT_LIMITS["ira_catchup_50"]
    print(f"\n  Traditional IRA contribution limit: ${limit:,.0f}")
    atl.traditional_ira_contribution = min(
        ask_float("Traditional IRA contributions this year"),
        limit,
    )

    # HSA
    if ask_yes_no("Do you have a High Deductible Health Plan (HDHP) for HSA?"):
        if personal.filing_status == MARRIED_JOINT:
            hsa_limit = RETIREMENT_LIMITS["hsa_family"]
        else:
            hsa_limit = RETIREMENT_LIMITS["hsa_single"]
        if personal.age >= 55:
            hsa_limit += RETIREMENT_LIMITS["hsa_catchup_55"]
        print(f"  HSA contribution limit: ${hsa_limit:,.0f}")
        atl.hsa_contribution = min(
            ask_float("Your HSA contributions (not employer's)"),
            hsa_limit,
        )

    # Student loan interest
    atl.student_loan_interest = min(
        ask_float("Student loan interest paid"),
        STUDENT_LOAN_INTEREST_MAX,
    )

    # Educator expenses
    if personal.is_educator:
        atl.educator_expenses = min(
            ask_float("Unreimbursed educator expenses"),
            EDUCATOR_EXPENSE_MAX,
        )

    # Self-employment deductions
    if se_net_income > 0:
        # Deductible half of SE tax
        se_tax = se_net_income * 0.9235 * 0.153
        atl.self_employment_tax_deduction = se_tax / 2
        print(f"  Auto-calculated SE tax deduction: ${atl.self_employment_tax_deduction:,.0f}")

        if ask_yes_no("Did you pay for your own health insurance (self-employed)?"):
            atl.self_employment_health_insurance = ask_float(
                "Self-employed health insurance premiums"
            )

    return atl


def collect_itemized_deductions() -> ItemizedDeductions:
    """Collect Schedule A itemized deductions."""
    item = ItemizedDeductions()
    print("\n" + "=" * 60)
    print("ITEMIZED DEDUCTIONS (we'll compare to standard deduction)")
    print("=" * 60)

    print(f"\n  Note: State/local + property taxes capped at ${SALT_CAP:,} (SALT cap)")
    item.state_local_income_tax = ask_float("State/local income taxes paid")
    item.property_tax = ask_float("Property taxes paid")

    if ask_yes_no("Do you have a mortgage?"):
        item.mortgage_interest = ask_float("Mortgage interest paid (on up to $750k loan)")
        item.mortgage_insurance_premiums = ask_float("Mortgage insurance premiums (PMI)")

    print("\n  Charitable donations:")
    item.charitable_cash = ask_float("Cash donations to qualified charities")
    item.charitable_non_cash = ask_float("Non-cash donations (clothing, goods — fair market value)")

    item.medical_expenses = ask_float("Total medical/dental expenses (only amount > 7.5% AGI counts)")

    return item


def collect_tax_credits() -> TaxCredits:
    """Collect info needed for tax credit calculations."""
    credits = TaxCredits()
    print("\n" + "=" * 60)
    print("TAX CREDITS (reduce your tax bill dollar-for-dollar)")
    print("=" * 60)

    # Dependents
    print("\n--- Dependents ---")
    try:
        val = input("  Number of children under 17 [0]: ").strip()
        credits.num_children_under_17 = int(val) if val else 0
    except ValueError:
        credits.num_children_under_17 = 0
    try:
        val = input("  Number of other dependents (17+, elderly parents, etc.) [0]: ").strip()
        credits.num_other_dependents = int(val) if val else 0
    except ValueError:
        credits.num_other_dependents = 0

    # Child/Dependent Care
    if credits.num_children_under_17 > 0 or credits.num_other_dependents > 0:
        if ask_yes_no("Did you pay for child/dependent care so you could work?"):
            credits.child_care_expenses = ask_float("Total child/dependent care expenses")
            try:
                val = input("  Number of children in care (1 or 2+) [1]: ").strip()
                credits.num_children_for_care = int(val) if val else 1
            except ValueError:
                credits.num_children_for_care = 1

    # Education
    if ask_yes_no("Did you pay college tuition or education expenses?"):
        credits.education_expenses = ask_float("Qualified education expenses")
        try:
            val = input("  Years of American Opportunity Credit already claimed (max 4) [0]: ").strip()
            credits.years_of_aotc_claimed = int(val) if val else 0
        except ValueError:
            credits.years_of_aotc_claimed = 0

    # Energy / EV
    if ask_yes_no("Did you make energy-efficient home improvements?"):
        credits.energy_efficient_improvements = ask_float(
            "Energy-efficient improvement costs (insulation, windows, heat pumps, etc.)"
        )

    if ask_yes_no("Did you purchase a qualifying electric vehicle?"):
        credits.ev_purchase = True
        credits.ev_purchase_amount = ask_float("EV purchase price")

    if ask_yes_no("Did you install residential solar panels?"):
        credits.residential_solar = ask_float("Total solar installation cost")

    # Saver's Credit
    if ask_yes_no("Is your AGI under ~$40k (single) / ~$80k (joint)? (for Saver's Credit)"):
        credits.savers_credit_eligible = True
        credits.retirement_contributions_for_savers = ask_float(
            "Total retirement contributions (IRA + 401k employee portion)"
        )

    # Foreign tax
    credits.foreign_tax_paid = ask_float("Foreign taxes paid on investments")

    # Estimated taxes
    credits.estimated_taxes_paid = ask_float("Estimated tax payments made this year")

    return credits


def compute_standard_deduction(personal: PersonalInfo) -> float:
    """Calculate standard deduction including additional amounts for age/blindness."""
    base = STANDARD_DEDUCTION[personal.filing_status]
    additional = 0
    add_amount = ADDITIONAL_STD_DEDUCTION[personal.filing_status]

    if personal.age >= 65:
        additional += add_amount
    if personal.is_blind:
        additional += add_amount
    if personal.filing_status in (MARRIED_JOINT, MARRIED_SEPARATE):
        if personal.spouse_age >= 65:
            additional += add_amount
        if personal.spouse_is_blind:
            additional += add_amount

    return base + additional


def compute_child_tax_credit(credits: TaxCredits, filing_status: str, agi: float) -> float:
    """Compute Child Tax Credit with phaseout."""
    base = (
        credits.num_children_under_17 * CHILD_TAX_CREDIT
        + credits.num_other_dependents * CHILD_TAX_CREDIT_OTHER_DEPENDENT
    )
    if base == 0:
        return 0

    threshold = CTC_PHASEOUT_START[filing_status]
    if agi > threshold:
        excess = agi - threshold
        reduction = (excess // 1000) * CTC_PHASEOUT_RATE
        base = max(0, base - reduction)

    return base


def compute_child_care_credit(credits: TaxCredits, agi: float) -> float:
    """Compute Child and Dependent Care Credit."""
    if credits.child_care_expenses <= 0 or credits.num_children_for_care <= 0:
        return 0

    max_expenses = 3_000 if credits.num_children_for_care == 1 else 6_000
    eligible = min(credits.child_care_expenses, max_expenses)

    # Credit percentage: 35% for AGI <= $15k, decreasing to 20% for AGI > $43k
    if agi <= 15_000:
        rate = 0.35
    elif agi >= 43_000:
        rate = 0.20
    else:
        rate = 0.35 - ((agi - 15_000) // 2_000) * 0.01
        rate = max(0.20, rate)

    return eligible * rate


def compute_education_credit(credits: TaxCredits, agi: float, filing_status: str) -> float:
    """Compute American Opportunity or Lifetime Learning Credit."""
    if credits.education_expenses <= 0:
        return 0

    # American Opportunity Tax Credit (if < 4 years claimed)
    if credits.years_of_aotc_claimed < 4:
        # 100% of first $2,000 + 25% of next $2,000 = max $2,500
        aotc = min(credits.education_expenses, 2_000) + 0.25 * max(
            0, min(credits.education_expenses - 2_000, 2_000)
        )
        # Phaseout
        if filing_status == MARRIED_JOINT:
            phase_start, phase_end = 160_000, 180_000
        else:
            phase_start, phase_end = 80_000, 90_000

        if agi > phase_end:
            aotc = 0
        elif agi > phase_start:
            aotc *= 1 - (agi - phase_start) / (phase_end - phase_start)
        return aotc

    # Lifetime Learning Credit: 20% of up to $10,000
    llc = 0.20 * min(credits.education_expenses, 10_000)
    if filing_status == MARRIED_JOINT:
        phase_start, phase_end = 160_000, 180_000
    else:
        phase_start, phase_end = 80_000, 90_000
    if agi > phase_end:
        llc = 0
    elif agi > phase_start:
        llc *= 1 - (agi - phase_start) / (phase_end - phase_start)
    return llc


def compute_energy_credits(credits: TaxCredits) -> float:
    """Energy Efficient Home Improvement + EV + Solar credits."""
    total = 0

    # Energy Efficient Home Improvement Credit: 30% up to $3,200/year
    if credits.energy_efficient_improvements > 0:
        total += min(credits.energy_efficient_improvements * 0.30, 3_200)

    # Clean Vehicle Credit: up to $7,500
    if credits.ev_purchase:
        total += min(7_500, credits.ev_purchase_amount * 0.10)  # Simplified

    # Residential Clean Energy Credit: 30% of solar costs
    if credits.residential_solar > 0:
        total += credits.residential_solar * 0.30

    return total


def compute_savers_credit(credits: TaxCredits, agi: float, filing_status: str) -> float:
    """Retirement Savings Contributions Credit (Saver's Credit)."""
    if not credits.savers_credit_eligible:
        return 0

    contrib = min(credits.retirement_contributions_for_savers, 2_000)

    if filing_status == MARRIED_JOINT:
        if agi <= 47_500:
            rate = 0.50
        elif agi <= 51_000:
            rate = 0.20
        elif agi <= 78_750:
            rate = 0.10
        else:
            return 0
    elif filing_status == HEAD_OF_HOUSEHOLD:
        if agi <= 35_625:
            rate = 0.50
        elif agi <= 38_250:
            rate = 0.20
        elif agi <= 59_062:
            rate = 0.10
        else:
            return 0
    else:
        if agi <= 23_750:
            rate = 0.50
        elif agi <= 25_500:
            rate = 0.20
        elif agi <= 39_375:
            rate = 0.10
        else:
            return 0

    return contrib * rate


def compute_eitc(filing_status: str, agi: float, num_children: int) -> float:
    """Earned Income Tax Credit (simplified)."""
    kids = min(num_children, 3)
    if filing_status in (MARRIED_JOINT,):
        limits = EITC_INCOME_LIMITS_JOINT
    else:
        limits = EITC_INCOME_LIMITS_SINGLE

    if agi > limits.get(kids, 0):
        return 0

    return EITC_MAX.get(kids, 0)


def compute_qbi_deduction(se_net_income: float, taxable_income: float, filing_status: str) -> float:
    """Qualified Business Income deduction (Section 199A)."""
    if se_net_income <= 0:
        return 0

    qbi_deduction = se_net_income * QBI_DEDUCTION_RATE
    threshold = QBI_INCOME_THRESHOLD[filing_status]

    if taxable_income <= threshold:
        return min(qbi_deduction, taxable_income * QBI_DEDUCTION_RATE)

    # Simplified: phase out above threshold
    return 0


def collect_all_deductions(se_net_income: float) -> AllDeductions:
    """Run through all deduction/credit collection."""
    all_ded = AllDeductions()
    all_ded.personal = collect_personal_info()
    all_ded.above_the_line = collect_above_the_line(all_ded.personal, se_net_income)
    all_ded.itemized = collect_itemized_deductions()
    all_ded.credits = collect_tax_credits()
    return all_ded
