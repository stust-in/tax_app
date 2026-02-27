"""Tests for the tax calculator engine."""

import pytest
from tax_app.tax_data import SINGLE, MARRIED_JOINT, HEAD_OF_HOUSEHOLD
from tax_app.income import AllIncome, W2Income, StockIncome, SelfEmploymentIncome, OtherIncome
from tax_app.deductions import (
    AllDeductions, PersonalInfo, AboveTheLineDeductions,
    ItemizedDeductions, TaxCredits,
    compute_standard_deduction, compute_child_tax_credit,
    compute_child_care_credit, compute_education_credit,
    compute_qbi_deduction,
)
from tax_app.calculator import (
    compute_bracket_tax, get_marginal_rate, compute_ltcg_tax,
    compute_niit, compute_self_employment_tax, compute_state_tax,
    calculate_taxes, TaxResult,
)
from tax_app.tips import generate_tips


# --- Helper to build test scenarios ---

def make_income(w2_wages=0, federal_withheld=0, state_withheld=0,
                ss_tax=0, medicare_tax=0, k401=0,
                st_gains=0, st_losses=0, lt_gains=0, lt_losses=0,
                qual_div=0, ord_div=0, interest=0,
                se_gross=0, se_expenses=0, rsu_income=0) -> AllIncome:
    income = AllIncome()
    if w2_wages > 0:
        w2 = W2Income(
            employer_name="Test Corp",
            gross_wages=w2_wages,
            federal_tax_withheld=federal_withheld,
            state_tax_withheld=state_withheld,
            social_security_tax=ss_tax,
            medicare_tax=medicare_tax,
            retirement_contrib_401k=k401,
        )
        income.w2s = [w2]
    income.stocks = StockIncome(
        rsu_gsu_vesting_income=rsu_income,
        short_term_gains=st_gains,
        short_term_losses=st_losses,
        long_term_gains=lt_gains,
        long_term_losses=lt_losses,
        qualified_dividends=qual_div,
        ordinary_dividends=ord_div,
    )
    income.self_employment = SelfEmploymentIncome(
        gross_income=se_gross,
        business_expenses=se_expenses,
    )
    income.other = OtherIncome(interest_income=interest)
    return income


def make_deductions(filing_status=SINGLE, age=30, state="CA",
                    ira=0, hsa=0, student_loan=0,
                    salt=0, property_tax=0, mortgage=0,
                    charitable=0, children=0,
                    estimated_paid=0) -> AllDeductions:
    d = AllDeductions()
    d.personal = PersonalInfo(
        filing_status=filing_status,
        age=age,
        state=state,
        has_employer_retirement_plan=True,
    )
    d.above_the_line = AboveTheLineDeductions(
        traditional_ira_contribution=ira,
        hsa_contribution=hsa,
        student_loan_interest=student_loan,
    )
    d.itemized = ItemizedDeductions(
        state_local_income_tax=salt,
        property_tax=property_tax,
        mortgage_interest=mortgage,
        charitable_cash=charitable,
    )
    d.credits = TaxCredits(
        num_children_under_17=children,
        estimated_taxes_paid=estimated_paid,
    )
    return d


# =====================================================================
# BRACKET TAX TESTS
# =====================================================================

class TestBracketTax:
    def test_zero_income(self):
        from tax_app.tax_data import FEDERAL_BRACKETS
        assert compute_bracket_tax(0, FEDERAL_BRACKETS[SINGLE]) == 0

    def test_lowest_bracket_single(self):
        from tax_app.tax_data import FEDERAL_BRACKETS
        # $10,000 in the 10% bracket
        tax = compute_bracket_tax(10_000, FEDERAL_BRACKETS[SINGLE])
        assert tax == 10_000 * 0.10

    def test_two_brackets_single(self):
        from tax_app.tax_data import FEDERAL_BRACKETS
        # $30,000: first $11,925 at 10%, rest at 12%
        tax = compute_bracket_tax(30_000, FEDERAL_BRACKETS[SINGLE])
        expected = 11_925 * 0.10 + (30_000 - 11_925) * 0.12
        assert abs(tax - expected) < 0.01

    def test_high_income_hits_multiple_brackets(self):
        from tax_app.tax_data import FEDERAL_BRACKETS
        tax = compute_bracket_tax(200_000, FEDERAL_BRACKETS[SINGLE])
        assert tax > 0
        # Should be > 10% flat but < 37% flat
        assert tax > 200_000 * 0.10
        assert tax < 200_000 * 0.37

    def test_marginal_rate_low_income(self):
        from tax_app.tax_data import FEDERAL_BRACKETS
        assert get_marginal_rate(5_000, FEDERAL_BRACKETS[SINGLE]) == 0.10

    def test_marginal_rate_mid_income(self):
        from tax_app.tax_data import FEDERAL_BRACKETS
        assert get_marginal_rate(80_000, FEDERAL_BRACKETS[SINGLE]) == 0.22

    def test_marginal_rate_high_income(self):
        from tax_app.tax_data import FEDERAL_BRACKETS
        assert get_marginal_rate(700_000, FEDERAL_BRACKETS[SINGLE]) == 0.37


# =====================================================================
# CAPITAL GAINS TAX TESTS
# =====================================================================

class TestCapitalGains:
    def test_zero_ltcg(self):
        from tax_app.tax_data import LTCG_BRACKETS
        assert compute_ltcg_tax(0, 50_000, LTCG_BRACKETS[SINGLE]) == 0

    def test_ltcg_in_zero_bracket(self):
        from tax_app.tax_data import LTCG_BRACKETS
        # Ordinary income = 0, LTCG = $10,000 (all in 0% bracket)
        tax = compute_ltcg_tax(10_000, 0, LTCG_BRACKETS[SINGLE])
        assert tax == 0

    def test_ltcg_stacks_on_ordinary(self):
        from tax_app.tax_data import LTCG_BRACKETS
        # Ordinary income = $45,000, LTCG = $10,000
        # $45k ordinary pushes some gains into 15% bracket
        tax = compute_ltcg_tax(10_000, 45_000, LTCG_BRACKETS[SINGLE])
        # Some at 0%, some at 15%
        assert tax > 0
        assert tax < 10_000 * 0.15


# =====================================================================
# NIIT TESTS
# =====================================================================

class TestNIIT:
    def test_below_threshold(self):
        assert compute_niit(50_000, 150_000, SINGLE) == 0

    def test_above_threshold(self):
        # AGI $250k, investment income $80k, threshold $200k for single
        niit = compute_niit(80_000, 250_000, SINGLE)
        expected = 0.038 * min(80_000, 50_000)  # min(investment, excess over threshold)
        assert abs(niit - expected) < 0.01


# =====================================================================
# SELF-EMPLOYMENT TAX TESTS
# =====================================================================

class TestSelfEmploymentTax:
    def test_zero_se_income(self):
        total, deduction, _ = compute_self_employment_tax(0, 0)
        assert total == 0
        assert deduction == 0

    def test_basic_se_tax(self):
        total, deduction, _ = compute_self_employment_tax(100_000, 0)
        taxable = 100_000 * 0.9235
        expected_ss = taxable * 0.124
        expected_med = taxable * 0.029
        expected_total = expected_ss + expected_med
        assert abs(total - expected_total) < 1

    def test_deductible_half(self):
        total, deduction, _ = compute_self_employment_tax(100_000, 0)
        assert abs(deduction - total / 2) < 0.01


# =====================================================================
# DEDUCTION TESTS
# =====================================================================

class TestDeductions:
    def test_standard_deduction_single(self):
        info = PersonalInfo(filing_status=SINGLE, age=30)
        assert compute_standard_deduction(info) == 15_000

    def test_standard_deduction_married_joint(self):
        info = PersonalInfo(filing_status=MARRIED_JOINT, age=30)
        assert compute_standard_deduction(info) == 30_000

    def test_standard_deduction_age_65(self):
        info = PersonalInfo(filing_status=SINGLE, age=65)
        assert compute_standard_deduction(info) == 15_000 + 2_000

    def test_standard_deduction_married_both_65(self):
        info = PersonalInfo(filing_status=MARRIED_JOINT, age=65, spouse_age=65)
        assert compute_standard_deduction(info) == 30_000 + 1_600 * 2

    def test_itemized_salt_cap(self):
        item = ItemizedDeductions(
            state_local_income_tax=15_000,
            property_tax=8_000,
        )
        total = item.total(100_000)
        # SALT capped at $10,000
        assert total == 10_000


# =====================================================================
# CREDIT TESTS
# =====================================================================

class TestCredits:
    def test_child_tax_credit_basic(self):
        credits = TaxCredits(num_children_under_17=2)
        ctc = compute_child_tax_credit(credits, SINGLE, 100_000)
        assert ctc == 4_000  # 2 x $2,000

    def test_child_tax_credit_phaseout(self):
        credits = TaxCredits(num_children_under_17=1)
        # Single, AGI $210,000 — $10k over threshold, lose $500
        ctc = compute_child_tax_credit(credits, SINGLE, 210_000)
        assert ctc == 2_000 - 500

    def test_child_care_credit(self):
        credits = TaxCredits(child_care_expenses=5_000, num_children_for_care=1)
        cc = compute_child_care_credit(credits, 50_000)
        # Max expenses for 1 child is $3,000, rate at $50k AGI = 20%
        assert cc == 3_000 * 0.20

    def test_education_credit_aotc(self):
        credits = TaxCredits(education_expenses=4_000, years_of_aotc_claimed=0)
        ec = compute_education_credit(credits, 60_000, SINGLE)
        # 100% of first $2k + 25% of next $2k = $2,500
        assert ec == 2_500

    def test_qbi_deduction(self):
        qbi = compute_qbi_deduction(50_000, 80_000, SINGLE)
        # 20% of SE income = $10,000, but capped at 20% of taxable = $16,000
        assert qbi == 10_000


# =====================================================================
# FULL CALCULATION TESTS
# =====================================================================

class TestFullCalculation:
    def test_simple_w2_single(self):
        """Single filer, $75k W-2 income, standard deduction."""
        income = make_income(
            w2_wages=75_000,
            federal_withheld=8_000,
            state_withheld=3_000,
            ss_tax=4_650,
            medicare_tax=1_088,
        )
        deductions = make_deductions(filing_status=SINGLE, state="CA")
        result = calculate_taxes(income, deductions)

        # Taxable = 75,000 - 15,000 = 60,000
        assert result.agi == 75_000
        assert result.deduction_type == "Standard"
        assert result.total_tax_liability > 0
        assert result.effective_rate > 0
        assert result.effective_rate < 0.40

    def test_high_earner_with_rsu(self):
        """High earner with RSU income and stock sales."""
        income = make_income(
            w2_wages=250_000,
            federal_withheld=50_000,
            state_withheld=15_000,
            ss_tax=10_918,
            medicare_tax=3_625,
            k401=23_500,
            rsu_income=80_000,
            lt_gains=30_000,
            qual_div=5_000,
        )
        deductions = make_deductions(
            filing_status=SINGLE, state="CA", age=35,
        )
        result = calculate_taxes(income, deductions)

        assert result.agi > 250_000
        assert result.ltcg_tax > 0
        assert result.total_federal_tax > 0

    def test_self_employed(self):
        """Self-employed individual."""
        income = make_income(se_gross=120_000, se_expenses=20_000)
        deductions = make_deductions(filing_status=SINGLE, state="TX")
        # SE tax deduction
        se_net = 100_000
        se_tax = se_net * 0.9235 * 0.153
        deductions.above_the_line.self_employment_tax_deduction = se_tax / 2

        result = calculate_taxes(income, deductions)

        assert result.self_employment_tax > 0
        assert result.state_tax_estimate == 0  # Texas

    def test_married_with_children_gets_ctc(self):
        """Married couple with kids gets Child Tax Credit."""
        income = make_income(
            w2_wages=100_000,
            federal_withheld=10_000,
            state_withheld=4_000,
            ss_tax=6_200,
            medicare_tax=1_450,
        )
        deductions = make_deductions(
            filing_status=MARRIED_JOINT, state="FL",
            children=2,
        )
        result = calculate_taxes(income, deductions)

        assert result.child_tax_credit == 4_000
        assert result.state_tax_estimate == 0  # Florida

    def test_capital_loss_limited(self):
        """Capital losses limited to $3,000 deduction."""
        income = make_income(
            w2_wages=80_000,
            st_losses=10_000,
        )
        deductions = make_deductions(filing_status=SINGLE)
        result = calculate_taxes(income, deductions)

        # Net capital loss = -$10,000 but only $3,000 deductible
        assert income.capital_loss_carryforward == 7_000

    def test_refund_scenario(self):
        """Over-withheld taxes result in refund."""
        income = make_income(
            w2_wages=50_000,
            federal_withheld=15_000,  # Way over-withheld
            state_withheld=5_000,
            ss_tax=3_100,
            medicare_tax=725,
        )
        deductions = make_deductions(filing_status=SINGLE, state="FL")
        result = calculate_taxes(income, deductions)

        assert result.balance_due < 0  # Refund


# =====================================================================
# TIPS TESTS
# =====================================================================

class TestTips:
    def test_tips_generated(self):
        income = make_income(w2_wages=100_000, k401=10_000)
        deductions = make_deductions(filing_status=SINGLE, state="CA")
        result = calculate_taxes(income, deductions)
        tips = generate_tips(income, deductions, result)

        assert len(tips) > 0
        categories = [t["category"] for t in tips]
        assert "Retirement" in categories  # Should suggest maxing 401k

    def test_rsu_tips(self):
        income = make_income(w2_wages=200_000, rsu_income=60_000, lt_gains=20_000)
        deductions = make_deductions(filing_status=SINGLE, state="WA")
        result = calculate_taxes(income, deductions)
        tips = generate_tips(income, deductions, result)

        categories = [t["category"] for t in tips]
        assert "RSU/GSU" in categories

    def test_no_income_state_tip(self):
        income = make_income(w2_wages=100_000)
        deductions = make_deductions(filing_status=SINGLE, state="TX")
        result = calculate_taxes(income, deductions)
        tips = generate_tips(income, deductions, result)

        # Should not suggest moving to no-tax state since already in one
        state_tips = [t for t in tips if t["category"] == "State Tax"]
        assert len(state_tips) == 0


# =====================================================================
# STATE TAX TESTS
# =====================================================================

class TestStateTax:
    def test_no_tax_state(self):
        assert compute_state_tax(100_000, "TX") == 0
        assert compute_state_tax(100_000, "FL") == 0
        assert compute_state_tax(100_000, "WA") == 0

    def test_california(self):
        tax = compute_state_tax(100_000, "CA")
        assert tax == 100_000 * 0.133

    def test_new_york(self):
        tax = compute_state_tax(100_000, "NY")
        assert tax == 100_000 * 0.109
