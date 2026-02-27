"""
Tax optimization tips and strategies advisor.
Analyzes your tax situation and provides personalized recommendations
for reducing your tax burden legally.
"""

from .tax_data import (
    RETIREMENT_LIMITS, SALT_CAP, STANDARD_DEDUCTION,
    NO_INCOME_TAX_STATES, QBI_INCOME_THRESHOLD,
    MARRIED_JOINT, MARRIED_SEPARATE, HEAD_OF_HOUSEHOLD,
)
from .income import AllIncome
from .deductions import AllDeductions
from .calculator import TaxResult


def generate_tips(income: AllIncome, deductions: AllDeductions, result: TaxResult) -> list:
    """Generate personalized tax-saving tips based on the user's situation."""
    tips = []
    fs = deductions.personal.filing_status
    age = deductions.personal.age
    state = deductions.personal.state

    # =========================================================================
    # 401(k) OPTIMIZATION
    # =========================================================================
    total_401k = income.total_401k_contributions
    limit_401k = RETIREMENT_LIMITS["401k"]
    if 60 <= age <= 63:
        limit_401k += RETIREMENT_LIMITS["401k_catchup_60_63"]
    elif age >= 50:
        limit_401k += RETIREMENT_LIMITS["401k_catchup_50"]

    if total_401k < limit_401k:
        room = limit_401k - total_401k
        tax_saved = room * result.marginal_rate
        tips.append({
            "category": "Retirement",
            "priority": "HIGH",
            "title": "Max out your 401(k)",
            "detail": (
                f"You contributed ${total_401k:,.0f} to your 401(k) but the limit is "
                f"${limit_401k:,.0f}. Contributing ${room:,.0f} more could save you "
                f"~${tax_saved:,.0f} in federal taxes this year."
            ),
            "savings": tax_saved,
        })

    # =========================================================================
    # TRADITIONAL IRA
    # =========================================================================
    ira_contrib = deductions.above_the_line.traditional_ira_contribution
    ira_limit = RETIREMENT_LIMITS["ira"]
    if age >= 50:
        ira_limit += RETIREMENT_LIMITS["ira_catchup_50"]

    if ira_contrib < ira_limit:
        room = ira_limit - ira_contrib
        tax_saved = room * result.marginal_rate
        tips.append({
            "category": "Retirement",
            "priority": "HIGH",
            "title": "Contribute to a Traditional IRA",
            "detail": (
                f"You can contribute up to ${room:,.0f} more to a Traditional IRA. "
                f"This could reduce your taxable income and save ~${tax_saved:,.0f}. "
                f"Note: deductibility may be limited if you have an employer plan and "
                f"high income. Consider a Roth IRA if you're over the deduction phaseout."
            ),
            "savings": tax_saved,
        })

    # =========================================================================
    # HSA (Triple Tax Advantage)
    # =========================================================================
    hsa_contrib = deductions.above_the_line.hsa_contribution
    if hsa_contrib > 0 or any(w.hsa_employer_contrib > 0 for w in income.w2s):
        if fs == MARRIED_JOINT:
            hsa_limit = RETIREMENT_LIMITS["hsa_family"]
        else:
            hsa_limit = RETIREMENT_LIMITS["hsa_single"]
        if age >= 55:
            hsa_limit += RETIREMENT_LIMITS["hsa_catchup_55"]

        employer_hsa = sum(w.hsa_employer_contrib for w in income.w2s)
        total_hsa = hsa_contrib + employer_hsa
        if total_hsa < hsa_limit:
            room = hsa_limit - total_hsa
            tax_saved = room * result.marginal_rate
            tips.append({
                "category": "HSA",
                "priority": "HIGH",
                "title": "Max out your HSA (triple tax advantage)",
                "detail": (
                    f"HSAs are the BEST tax-advantaged account: tax-deductible going in, "
                    f"tax-free growth, and tax-free withdrawals for medical expenses. "
                    f"You have ${room:,.0f} of room left. Immediate tax savings: ~${tax_saved:,.0f}. "
                    f"Pro tip: Pay medical expenses out of pocket, invest your HSA, and "
                    f"reimburse yourself years later for maximum tax-free growth."
                ),
                "savings": tax_saved,
            })
    else:
        tips.append({
            "category": "HSA",
            "priority": "MEDIUM",
            "title": "Consider a High Deductible Health Plan + HSA",
            "detail": (
                "If your employer offers an HDHP, you can open an HSA and get the "
                "triple tax advantage: deductible contributions, tax-free growth, "
                "and tax-free withdrawals for medical expenses. It's essentially a "
                "stealth retirement account — after age 65, withdrawals for any "
                "purpose are penalty-free (just taxed like a Traditional IRA)."
            ),
            "savings": 0,
        })

    # =========================================================================
    # TAX-LOSS HARVESTING
    # =========================================================================
    net_gains = income.net_short_term_gains + income.net_long_term_gains
    if net_gains > 0:
        tips.append({
            "category": "Investments",
            "priority": "HIGH",
            "title": "Tax-loss harvesting",
            "detail": (
                f"You have ${net_gains:,.0f} in net capital gains. Before year-end, "
                f"review your portfolio for losing positions you could sell to offset gains. "
                f"This directly reduces your capital gains tax. Remember the wash-sale rule: "
                f"don't repurchase the same or 'substantially identical' security within "
                f"30 days. You can buy a similar (but not identical) ETF immediately."
            ),
            "savings": net_gains * 0.15,  # Rough estimate
        })

    if income.capital_loss_carryforward > 0:
        tips.append({
            "category": "Investments",
            "priority": "INFO",
            "title": "Capital loss carryforward",
            "detail": (
                f"You have ${income.capital_loss_carryforward:,.0f} in capital losses "
                f"exceeding the $3,000 annual deduction limit. This carries forward to "
                f"future tax years to offset future gains."
            ),
            "savings": 0,
        })

    # =========================================================================
    # RSU/GSU SPECIFIC TIPS
    # =========================================================================
    if income.stocks.rsu_gsu_vesting_income > 0:
        tips.append({
            "category": "RSU/GSU",
            "priority": "HIGH",
            "title": "RSU/GSU tax planning strategies",
            "detail": (
                f"Your RSU/GSU vesting income of ${income.stocks.rsu_gsu_vesting_income:,.0f} "
                f"is taxed as ordinary income. Key strategies:\n"
                f"  1. SELL-TO-COVER TIMING: Check if your company lets you choose vest dates\n"
                f"  2. MAXIMIZE 401(k): Offset vesting income by maxing pre-tax contributions\n"
                f"  3. CHARITABLE GIVING: Donate appreciated RSU shares (held >1 year) to "
                f"charity — avoid capital gains AND get the full fair market value deduction\n"
                f"  4. DIVERSIFY: Sell vested shares and reinvest to avoid concentration risk\n"
                f"  5. HOLD FOR LTCG: If you believe in the stock, hold vested shares >1 year "
                f"so future appreciation is taxed at lower long-term capital gains rates"
            ),
            "savings": 0,
        })

    # =========================================================================
    # STANDARD vs ITEMIZED DEDUCTION BUNCHING
    # =========================================================================
    std_ded = STANDARD_DEDUCTION[fs]
    itemized = result.itemized_deduction

    if abs(itemized - std_ded) < 5_000:
        tips.append({
            "category": "Deductions",
            "priority": "HIGH",
            "title": "Deduction bunching strategy",
            "detail": (
                f"Your itemized deductions (${itemized:,.0f}) are close to the standard "
                f"deduction (${std_ded:,.0f}). Consider 'bunching' — alternate years between "
                f"standard and itemized deductions. Bunch two years of charitable donations "
                f"into one year (or use a Donor-Advised Fund) to exceed the standard "
                f"deduction in the bunching year, then take the standard deduction the next year."
            ),
            "savings": (itemized - std_ded) * result.marginal_rate if itemized > std_ded else 0,
        })

    # =========================================================================
    # CHARITABLE GIVING WITH APPRECIATED STOCK
    # =========================================================================
    ltcg = income.net_long_term_gains
    if ltcg > 0 and deductions.itemized.charitable_cash > 0:
        tips.append({
            "category": "Charitable",
            "priority": "HIGH",
            "title": "Donate appreciated stock instead of cash",
            "detail": (
                "Instead of donating cash to charity, donate appreciated stock you've "
                "held over 1 year. You get the full fair market value deduction AND "
                "avoid paying capital gains tax on the appreciation. Then use the cash "
                "you would have donated to buy new shares (resetting your cost basis higher). "
                "This is one of the most powerful legal tax strategies available."
            ),
            "savings": ltcg * 0.15 * 0.3,  # Rough estimate
        })

    # =========================================================================
    # DONOR-ADVISED FUND
    # =========================================================================
    if deductions.itemized.charitable_cash >= 5_000:
        tips.append({
            "category": "Charitable",
            "priority": "MEDIUM",
            "title": "Use a Donor-Advised Fund (DAF)",
            "detail": (
                "A Donor-Advised Fund lets you make a large tax-deductible contribution "
                "now, invest the money tax-free, and distribute to charities over time. "
                "Perfect for 'deduction bunching' — contribute several years' worth of "
                "donations in a high-income year to maximize the tax benefit."
            ),
            "savings": 0,
        })

    # =========================================================================
    # MEGA BACKDOOR ROTH
    # =========================================================================
    if result.agi > 150_000:
        tips.append({
            "category": "Retirement",
            "priority": "MEDIUM",
            "title": "Mega Backdoor Roth (if your plan allows)",
            "detail": (
                "If your employer's 401(k) plan allows after-tax contributions and "
                "in-plan Roth conversions, you can contribute up to $70,000 total "
                "(including employer match) in 2025 via the 'Mega Backdoor Roth.' "
                "This gets more money growing tax-free in a Roth account. Check with "
                "your plan administrator if this is available."
            ),
            "savings": 0,
        })

    # =========================================================================
    # BACKDOOR ROTH IRA
    # =========================================================================
    if result.agi > 160_000 and fs != MARRIED_SEPARATE:
        tips.append({
            "category": "Retirement",
            "priority": "MEDIUM",
            "title": "Backdoor Roth IRA",
            "detail": (
                "Your income is too high for direct Roth IRA contributions. Use the "
                "'Backdoor Roth' strategy: contribute to a non-deductible Traditional "
                "IRA, then immediately convert to Roth. Warning: if you have existing "
                "Traditional IRA balances, the pro-rata rule applies and may cause "
                "partial taxation. Consider rolling Traditional IRA into your 401(k) first."
            ),
            "savings": 0,
        })

    # =========================================================================
    # ROTH CONVERSION IN LOW-INCOME YEARS
    # =========================================================================
    if result.marginal_rate <= 0.22:
        tips.append({
            "category": "Retirement",
            "priority": "MEDIUM",
            "title": "Consider Roth conversions while in a low bracket",
            "detail": (
                f"You're in the {result.marginal_rate*100:.0f}% bracket. If you have "
                f"Traditional IRA/401(k) funds, consider converting some to Roth now. "
                f"You'll pay tax at today's lower rate instead of potentially higher "
                f"rates in the future. Fill up to the top of your current bracket."
            ),
            "savings": 0,
        })

    # =========================================================================
    # ESPP STRATEGY
    # =========================================================================
    if income.stocks.espp_discount_income > 0:
        tips.append({
            "category": "ESPP",
            "priority": "MEDIUM",
            "title": "ESPP holding period strategy",
            "detail": (
                "For ESPP shares, holding for 2+ years from grant and 1+ year from "
                "purchase qualifies for favorable tax treatment — part of the gain "
                "becomes long-term capital gain instead of ordinary income. If you "
                "need the cash, at minimum hold past the 1-year mark for LTCG rates."
            ),
            "savings": 0,
        })

    # =========================================================================
    # SELF-EMPLOYMENT STRATEGIES
    # =========================================================================
    se_income = income.self_employment.net_income
    if se_income > 50_000:
        tips.append({
            "category": "Self-Employment",
            "priority": "HIGH",
            "title": "Solo 401(k) or SEP-IRA",
            "detail": (
                f"With ${se_income:,.0f} in self-employment income, you could shelter "
                f"a significant amount in a Solo 401(k) or SEP-IRA. A Solo 401(k) "
                f"allows up to $23,500 as 'employee' + 25% of net SE income as 'employer' "
                f"contributions (up to $70,000 total for 2025). This is one of the "
                f"biggest tax deductions available to the self-employed."
            ),
            "savings": min(se_income * 0.25, 46_500) * result.marginal_rate,
        })

    if se_income > 0:
        qbi_threshold = QBI_INCOME_THRESHOLD[fs]
        if result.agi < qbi_threshold:
            tips.append({
                "category": "Self-Employment",
                "priority": "HIGH",
                "title": "Section 199A QBI Deduction",
                "detail": (
                    f"Your self-employment income may qualify for the 20% Qualified "
                    f"Business Income deduction. This effectively reduces your self-employment "
                    f"income tax rate by 20%. Ensure you're properly tracking business income "
                    f"and expenses to maximize this deduction."
                ),
                "savings": se_income * 0.20 * result.marginal_rate,
            })

    # =========================================================================
    # STATE TAX STRATEGIES
    # =========================================================================
    if state not in NO_INCOME_TAX_STATES and result.state_tax_estimate > 5_000:
        tips.append({
            "category": "State Tax",
            "priority": "INFO",
            "title": f"State tax impact: {state}",
            "detail": (
                f"Your estimated {state} state tax is ${result.state_tax_estimate:,.0f}. "
                f"If you work remotely, consider that some states have no income tax "
                f"(AK, FL, NV, NH, SD, TN, TX, WA, WY). Also check if your state offers "
                f"its own deductions, credits, or retirement income exclusions."
            ),
            "savings": 0,
        })

    # =========================================================================
    # TIMING STRATEGIES
    # =========================================================================
    tips.append({
        "category": "Timing",
        "priority": "MEDIUM",
        "title": "Year-end tax moves (if before Dec 31)",
        "detail": (
            "Before year-end, consider:\n"
            "  1. ACCELERATE DEDUCTIONS: Prepay state taxes, property taxes, make "
            "charitable donations before Dec 31\n"
            "  2. DEFER INCOME: If possible, push bonuses or freelance invoices to January\n"
            "  3. HARVEST LOSSES: Sell losing investments to offset gains\n"
            "  4. MAX RETIREMENT: Make final 401(k)/IRA contributions\n"
            "  5. USE FSA: Spend remaining Flexible Spending Account funds\n"
            "  6. MEDICAL EXPENSES: If close to 7.5% AGI threshold, schedule procedures "
            "before year-end to bunch medical deductions"
        ),
        "savings": 0,
    })

    # =========================================================================
    # ESTIMATED TAX PAYMENTS
    # =========================================================================
    if result.balance_due > 1_000 and deductions.credits.estimated_taxes_paid == 0:
        tips.append({
            "category": "Penalties",
            "priority": "HIGH",
            "title": "Avoid underpayment penalties",
            "detail": (
                f"You may owe ${result.balance_due:,.0f}. If you didn't make estimated "
                f"tax payments, you could face an underpayment penalty. For next year, "
                f"make quarterly estimated payments (April 15, June 15, Sept 15, Jan 15) "
                f"or increase your W-4 withholding. Safe harbor: pay at least 100% of "
                f"last year's tax (110% if AGI > $150k)."
            ),
            "savings": 0,
        })

    # =========================================================================
    # MARRIAGE PENALTY / BONUS
    # =========================================================================
    if fs == MARRIED_JOINT and result.agi > 400_000:
        tips.append({
            "category": "Filing Strategy",
            "priority": "INFO",
            "title": "Check Married Filing Separately",
            "detail": (
                "At higher incomes, sometimes filing separately can reduce total tax, "
                "especially if one spouse has high medical expenses, student loans, or "
                "significant income differences. Run the numbers both ways. Note: filing "
                "separately disqualifies you from some credits (EITC, education credits)."
            ),
            "savings": 0,
        })

    # =========================================================================
    # HEALTH INSURANCE PREMIUM TAX CREDIT
    # =========================================================================
    if se_income > 0 and not any(w.gross_wages > 0 for w in income.w2s):
        tips.append({
            "category": "Healthcare",
            "priority": "MEDIUM",
            "title": "ACA Premium Tax Credit",
            "detail": (
                "If you buy health insurance through the marketplace, you may qualify "
                "for the Premium Tax Credit based on your income. This can significantly "
                "reduce your insurance costs. Managing your AGI (through retirement "
                "contributions) can help you qualify for larger subsidies."
            ),
            "savings": 0,
        })

    # =========================================================================
    # 529 PLAN
    # =========================================================================
    if deductions.credits.num_children_under_17 > 0:
        tips.append({
            "category": "Education",
            "priority": "MEDIUM",
            "title": "529 Education Savings Plan",
            "detail": (
                "529 plans offer tax-free growth for education expenses. Many states "
                "offer a state tax deduction for contributions. Funds can be used for "
                "K-12 tuition (up to $10k/year) and college expenses. Starting in 2024, "
                "unused 529 funds can be rolled into a Roth IRA (up to $35k lifetime, "
                "subject to annual Roth limits). Great for tax-free compounding."
            ),
            "savings": 0,
        })

    # Sort by estimated savings (highest first), then by priority
    priority_order = {"HIGH": 0, "MEDIUM": 1, "INFO": 2}
    tips.sort(key=lambda t: (priority_order.get(t["priority"], 3), -t["savings"]))

    return tips


def print_tips(tips: list):
    """Display tax tips in a formatted way."""
    print("\n" + "=" * 60)
    print("TAX OPTIMIZATION TIPS & STRATEGIES")
    print("=" * 60)

    if not tips:
        print("\n  No specific tips at this time.")
        return

    total_potential = sum(t["savings"] for t in tips)
    if total_potential > 0:
        print(f"\n  Potential total savings identified: ${total_potential:,.0f}")

    for i, tip in enumerate(tips, 1):
        priority_marker = {
            "HIGH": "!!!",
            "MEDIUM": " >> ",
            "INFO": " i  ",
        }.get(tip["priority"], "   ")

        print(f"\n  [{priority_marker}] {i}. [{tip['category']}] {tip['title']}")
        if tip["savings"] > 0:
            print(f"       Estimated savings: ${tip['savings']:,.0f}")

        # Word-wrap the detail text
        for line in tip["detail"].split("\n"):
            print(f"       {line}")
