"""
Income collection — gathers all sources of income through simplified prompts.
Covers W-2, GSU/RSU, stock sales, freelance/1099, interest, dividends,
rental income, retirement distributions, and other income.
"""

from dataclasses import dataclass, field


@dataclass
class W2Income:
    employer_name: str = ""
    gross_wages: float = 0.0  # Box 1 — includes vested GSU/RSU income
    federal_tax_withheld: float = 0.0  # Box 2
    state_tax_withheld: float = 0.0  # Box 17
    social_security_wages: float = 0.0  # Box 3
    social_security_tax: float = 0.0  # Box 4
    medicare_wages: float = 0.0  # Box 5
    medicare_tax: float = 0.0  # Box 6
    retirement_contrib_401k: float = 0.0  # Box 12 code D
    hsa_employer_contrib: float = 0.0  # Box 12 code W


@dataclass
class StockIncome:
    """Covers RSU/GSU vesting and stock sales."""
    rsu_gsu_vesting_income: float = 0.0  # Already included in W-2 wages, tracked for awareness
    short_term_gains: float = 0.0  # Held <= 1 year
    short_term_losses: float = 0.0  # Held <= 1 year (enter as positive)
    long_term_gains: float = 0.0   # Held > 1 year
    long_term_losses: float = 0.0  # Held > 1 year (enter as positive)
    espp_discount_income: float = 0.0  # ESPP ordinary income portion
    qualified_dividends: float = 0.0
    ordinary_dividends: float = 0.0  # Non-qualified dividends


@dataclass
class SelfEmploymentIncome:
    gross_income: float = 0.0
    business_expenses: float = 0.0  # Deductible business expenses
    home_office_sqft: float = 0.0
    total_home_sqft: float = 0.0
    home_expenses: float = 0.0  # Rent/mortgage, utilities, insurance for home office

    @property
    def net_income(self) -> float:
        home_office = 0.0
        if self.total_home_sqft > 0 and self.home_office_sqft > 0:
            # Simplified method: $5/sqft up to 300 sqft
            simplified = min(self.home_office_sqft, 300) * 5
            # Regular method
            ratio = self.home_office_sqft / self.total_home_sqft
            regular = self.home_expenses * ratio
            home_office = max(simplified, regular)
        return max(0, self.gross_income - self.business_expenses - home_office)


@dataclass
class OtherIncome:
    interest_income: float = 0.0       # Bank interest, bonds
    rental_income_net: float = 0.0     # Net rental income after expenses
    retirement_distributions: float = 0.0  # 401k/IRA withdrawals (taxable portion)
    social_security_benefits: float = 0.0
    unemployment_income: float = 0.0
    gambling_winnings: float = 0.0
    alimony_received: float = 0.0      # Pre-2019 agreements only
    crypto_gains_short: float = 0.0
    crypto_gains_long: float = 0.0
    crypto_losses_short: float = 0.0
    crypto_losses_long: float = 0.0
    other_income: float = 0.0


@dataclass
class AllIncome:
    w2s: list = field(default_factory=list)  # List of W2Income
    stocks: StockIncome = field(default_factory=StockIncome)
    self_employment: SelfEmploymentIncome = field(default_factory=SelfEmploymentIncome)
    other: OtherIncome = field(default_factory=OtherIncome)

    @property
    def total_w2_wages(self) -> float:
        return sum(w.gross_wages for w in self.w2s)

    @property
    def total_federal_withheld(self) -> float:
        return sum(w.federal_tax_withheld for w in self.w2s)

    @property
    def total_state_withheld(self) -> float:
        return sum(w.state_tax_withheld for w in self.w2s)

    @property
    def total_ss_tax_paid(self) -> float:
        return sum(w.social_security_tax for w in self.w2s)

    @property
    def total_medicare_tax_paid(self) -> float:
        return sum(w.medicare_tax for w in self.w2s)

    @property
    def total_401k_contributions(self) -> float:
        return sum(w.retirement_contrib_401k for w in self.w2s)

    @property
    def net_short_term_gains(self) -> float:
        stock = self.stocks.short_term_gains - self.stocks.short_term_losses
        crypto = self.other.crypto_gains_short - self.other.crypto_losses_short
        return stock + crypto

    @property
    def net_long_term_gains(self) -> float:
        stock = self.stocks.long_term_gains - self.stocks.long_term_losses
        crypto = self.other.crypto_gains_long - self.other.crypto_losses_long
        return stock + crypto

    @property
    def net_capital_gains(self) -> float:
        total = self.net_short_term_gains + self.net_long_term_gains
        # Capital loss deduction limited to $3,000/year; excess carries forward
        if total < -3_000:
            return -3_000
        return total

    @property
    def capital_loss_carryforward(self) -> float:
        total = self.net_short_term_gains + self.net_long_term_gains
        if total < -3_000:
            return abs(total) - 3_000
        return 0.0

    @property
    def total_ordinary_income(self) -> float:
        """All income taxed at ordinary rates (before deductions)."""
        ordinary = (
            self.total_w2_wages
            + self.self_employment.net_income
            + max(self.net_short_term_gains, 0)
            + self.stocks.ordinary_dividends
            + self.stocks.espp_discount_income
            + self.other.interest_income
            + self.other.rental_income_net
            + self.other.retirement_distributions
            + self.other.unemployment_income
            + self.other.gambling_winnings
            + self.other.alimony_received
            + self.other.other_income
            + max(self.other.crypto_gains_short - self.other.crypto_losses_short, 0)
        )
        # Apply capital loss deduction if net gains are negative
        net_total = self.net_short_term_gains + self.net_long_term_gains
        if net_total < 0:
            ordinary += max(net_total, -3_000)
        return max(0, ordinary)

    @property
    def total_investment_income(self) -> float:
        """For NIIT calculation."""
        return (
            self.stocks.ordinary_dividends
            + self.stocks.qualified_dividends
            + self.other.interest_income
            + self.other.rental_income_net
            + max(self.net_short_term_gains + self.net_long_term_gains, 0)
        )

    @property
    def total_agi_estimate(self) -> float:
        """Rough AGI before above-the-line deductions."""
        ss_taxable = self.other.social_security_benefits * 0.85  # Simplified
        return (
            self.total_ordinary_income
            + max(self.net_long_term_gains, 0)
            + self.stocks.qualified_dividends
            + ss_taxable
        )


def ask_float(prompt: str, default: float = 0.0) -> float:
    """Prompt user for a dollar amount."""
    try:
        val = input(f"  {prompt} [${default:,.0f}]: ").strip()
        if not val:
            return default
        return float(val.replace(",", "").replace("$", ""))
    except ValueError:
        print("    Invalid number, using default.")
        return default


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    d = "Y/n" if default else "y/N"
    val = input(f"  {prompt} [{d}]: ").strip().lower()
    if not val:
        return default
    return val in ("y", "yes")


def collect_w2_income() -> list:
    """Collect W-2 income from one or more employers."""
    w2s = []
    print("\n--- W-2 Employment Income ---")
    print("(If your GSUs/RSUs vest through your employer, that income is already")
    print(" included in your W-2 Box 1 wages. We'll track it separately too.)\n")

    while True:
        w2 = W2Income()
        w2.employer_name = input("  Employer name (or press Enter to skip): ").strip()
        if not w2.employer_name and w2s:
            break
        if not w2.employer_name:
            w2.employer_name = "Employer 1"

        w2.gross_wages = ask_float(f"Total wages from {w2.employer_name} (W-2 Box 1)")
        w2.federal_tax_withheld = ask_float("Federal tax withheld (Box 2)")
        w2.state_tax_withheld = ask_float("State tax withheld (Box 17)")
        w2.social_security_tax = ask_float("Social Security tax withheld (Box 4)")
        w2.medicare_tax = ask_float("Medicare tax withheld (Box 6)")
        w2.retirement_contrib_401k = ask_float("401(k) contributions (Box 12 code D)")
        w2.hsa_employer_contrib = ask_float("HSA employer contributions (Box 12 code W)")

        w2s.append(w2)
        if not ask_yes_no("Do you have another W-2?"):
            break

    return w2s


def collect_stock_income() -> StockIncome:
    """Collect stock/equity compensation and investment income."""
    stocks = StockIncome()
    print("\n--- Stocks, RSUs/GSUs & Investment Income ---")

    if ask_yes_no("Did you have RSU/GSU vesting this year?"):
        stocks.rsu_gsu_vesting_income = ask_float(
            "RSU/GSU vesting income (for reference — already in W-2)"
        )
        print("    (This is tracked for awareness; it's already in your W-2 wages.)")

    if ask_yes_no("Did you sell any stocks, ETFs, or mutual funds?"):
        print("\n  -- Stock Sales --")
        stocks.short_term_gains = ask_float("Short-term capital gains (held <= 1 year)")
        stocks.short_term_losses = ask_float("Short-term capital losses (enter as positive)")
        stocks.long_term_gains = ask_float("Long-term capital gains (held > 1 year)")
        stocks.long_term_losses = ask_float("Long-term capital losses (enter as positive)")

    if ask_yes_no("Do you participate in an ESPP (Employee Stock Purchase Plan)?"):
        stocks.espp_discount_income = ask_float(
            "ESPP discount (ordinary income portion from selling ESPP shares)"
        )

    if ask_yes_no("Did you receive dividends?"):
        stocks.qualified_dividends = ask_float("Qualified dividends")
        stocks.ordinary_dividends = ask_float("Non-qualified (ordinary) dividends")

    return stocks


def collect_self_employment_income() -> SelfEmploymentIncome:
    """Collect freelance / 1099 / self-employment income."""
    se = SelfEmploymentIncome()
    print("\n--- Self-Employment / Freelance / 1099 Income ---")

    if not ask_yes_no("Did you have any self-employment or freelance income?"):
        return se

    se.gross_income = ask_float("Total self-employment / freelance gross income")
    se.business_expenses = ask_float("Total deductible business expenses")

    if ask_yes_no("Did you use a home office?"):
        se.home_office_sqft = ask_float("Home office square footage")
        se.total_home_sqft = ask_float("Total home square footage")
        se.home_expenses = ask_float("Annual home expenses (rent/mortgage + utilities + insurance)")

    return se


def collect_other_income() -> OtherIncome:
    """Collect miscellaneous income sources."""
    other = OtherIncome()
    print("\n--- Other Income ---")

    other.interest_income = ask_float("Bank/bond interest income (1099-INT)")

    if ask_yes_no("Did you have rental property income?"):
        other.rental_income_net = ask_float("Net rental income (after expenses)")

    if ask_yes_no("Did you take retirement account distributions (401k/IRA)?"):
        other.retirement_distributions = ask_float("Taxable retirement distributions")

    if ask_yes_no("Did you receive Social Security benefits?"):
        other.social_security_benefits = ask_float("Total Social Security benefits")

    if ask_yes_no("Did you sell cryptocurrency?"):
        other.crypto_gains_short = ask_float("Crypto short-term gains")
        other.crypto_losses_short = ask_float("Crypto short-term losses (enter as positive)")
        other.crypto_gains_long = ask_float("Crypto long-term gains")
        other.crypto_losses_long = ask_float("Crypto long-term losses (enter as positive)")

    other.unemployment_income = ask_float("Unemployment compensation")
    other.gambling_winnings = ask_float("Gambling winnings")
    other.other_income = ask_float("Any other taxable income")

    return other


def collect_all_income() -> AllIncome:
    """Run through all income collection prompts."""
    income = AllIncome()
    income.w2s = collect_w2_income()
    income.stocks = collect_stock_income()
    income.self_employment = collect_self_employment_income()
    income.other = collect_other_income()
    return income
