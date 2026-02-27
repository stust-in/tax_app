# 2025 Tax Calculator & Optimizer

A comprehensive, interactive command-line tax estimator for **Tax Year 2025** (filing in 2026). Enter your income, deductions, and credits through simplified yes/no prompts, and receive a detailed tax breakdown plus personalized strategies to legally reduce what you owe.

> **Disclaimer:** This is an estimator for educational and planning purposes only. Always consult a qualified tax professional or use official tax preparation software for filing.

---

## Table of Contents

- [Quick Start](#quick-start)
- [What You'll Need](#what-youll-need)
- [Features](#features)
  - [Income Sources](#income-sources)
  - [Tax Calculations](#tax-calculations)
  - [Deductions](#deductions)
  - [Tax Credits](#tax-credits)
  - [Tax Optimization Tips](#tax-optimization-tips)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Module Reference](#module-reference)
- [Example Output](#example-output)
- [Running Tests](#running-tests)
- [2025 Tax Reference](#2025-tax-reference)
- [Limitations](#limitations)
- [Contributing](#contributing)

---

## Quick Start

```bash
# Clone and enter the project
git clone <your-repo-url>
cd tax_app

# Run the calculator (no dependencies required for the app itself)
python3 run.py
```

That's it. The program walks you through three guided steps, then prints your full tax summary and personalized savings tips.

---

## What You'll Need

Have these documents handy before you start — the prompts will tell you exactly which box to look at:

| Document | What It Tells the Calculator |
|---|---|
| **W-2** (from each employer) | Wages, taxes withheld, 401(k) contributions, HSA contributions |
| **1099-B** (brokerage statement) | Stock sales, capital gains/losses, cost basis |
| **1099-DIV** | Qualified and ordinary dividends |
| **1099-INT** | Bank and bond interest income |
| **1099-NEC / 1099-MISC** | Freelance and self-employment income |
| **1098** (mortgage statement) | Mortgage interest paid |
| **Property tax bills** | Property taxes paid |
| **Charitable donation receipts** | Cash and non-cash donation totals |
| **RSU/GSU vesting statements** | Equity compensation income (already on W-2, tracked separately) |
| **ESPP purchase/sale records** | Employee Stock Purchase Plan discount income |
| **Crypto exchange reports** | Cryptocurrency gains and losses |

---

## Features

### Income Sources

The calculator handles virtually every common income type:

- **W-2 Employment** — supports multiple employers; references specific W-2 box numbers
- **RSU/GSU Vesting** — tracked separately for planning purposes (already included in W-2 Box 1)
- **Stock Sales** — short-term and long-term capital gains and losses
- **ESPP** — Employee Stock Purchase Plan ordinary income portion
- **Dividends** — qualified (lower tax rate) and ordinary (non-qualified)
- **Cryptocurrency** — short-term and long-term gains/losses, treated as property
- **Self-Employment / Freelance / 1099** — gross income, business expenses, home office deduction (simplified *and* regular method auto-compared)
- **Interest Income** — bank accounts, bonds, CDs
- **Rental Income** — net rental income after expenses
- **Retirement Distributions** — taxable 401(k)/IRA withdrawals
- **Social Security Benefits** — with simplified taxability calculation
- **Other** — unemployment, gambling winnings, alimony (pre-2019), and catch-all

### Tax Calculations

The engine computes taxes across multiple systems:

| Tax Type | Details |
|---|---|
| **Federal Income Tax** | All 7 progressive brackets (10% through 37%) for all 4 filing statuses |
| **Long-Term Capital Gains** | 0%/15%/20% rates with proper stacking on top of ordinary income |
| **Net Investment Income Tax** | 3.8% NIIT on investment income above AGI thresholds |
| **Alternative Minimum Tax** | Simplified AMT estimate with SALT add-back and exemption phaseout |
| **Social Security Tax** | 6.2% employee share up to the $176,100 wage base |
| **Medicare Tax** | 1.45% employee share + 0.9% Additional Medicare Tax on high earners |
| **Self-Employment Tax** | 15.3% (12.4% SS + 2.9% Medicare) on 92.35% of net SE income, with deductible half |
| **State Income Tax** | Simplified estimate for all 50 states + DC using top marginal rates |
| **Capital Loss Limits** | $3,000 annual deduction cap with carryforward tracking |

### Deductions

The calculator collects both above-the-line and below-the-line deductions, then **automatically picks whichever is larger** — standard or itemized:

**Above-the-Line (reduce AGI directly):**
- Traditional IRA contributions (with age-based limits)
- HSA contributions (single vs. family limits, age 55+ catch-up)
- Student loan interest (up to $2,500)
- Educator expenses (up to $300 for K-12 teachers)
- 50% of self-employment tax (auto-calculated)
- Self-employed health insurance premiums

**Standard Deduction (2025):**

| Filing Status | Base | Age 65+ / Blind (additional per person) |
|---|---|---|
| Single | $15,000 | +$2,000 |
| Married Filing Jointly | $30,000 | +$1,600 |
| Married Filing Separately | $15,000 | +$1,600 |
| Head of Household | $22,500 | +$2,000 |

**Itemized (Schedule A):**
- State and local taxes + property taxes (SALT capped at $10,000)
- Mortgage interest (on up to $750,000 of debt)
- Mortgage insurance premiums (PMI)
- Charitable donations — cash and non-cash
- Medical expenses (only the amount exceeding 7.5% of AGI)

**Other Deductions:**
- Qualified Business Income / Section 199A (20% of self-employment income below threshold)

### Tax Credits

Credits reduce your tax bill dollar-for-dollar:

- **Child Tax Credit** — $2,000 per child under 17 (+ $500 per other dependent), with income phaseout
- **Child and Dependent Care Credit** — 20-35% of up to $3,000/$6,000 in care expenses
- **American Opportunity Tax Credit** — up to $2,500/year for college (max 4 years), with phaseout
- **Lifetime Learning Credit** — 20% of up to $10,000 in education expenses
- **Energy Efficient Home Improvement Credit** — 30% of costs, up to $3,200/year
- **Clean Vehicle (EV) Credit** — up to $7,500 for qualifying electric vehicles
- **Residential Clean Energy (Solar) Credit** — 30% of solar installation costs
- **Saver's Credit** — up to 50% of retirement contributions for lower-income filers
- **Earned Income Tax Credit (EITC)** — up to $8,046 for qualifying families
- **Foreign Tax Credit** — dollar-for-dollar credit for foreign taxes paid on investments

### Tax Optimization Tips

After calculating your taxes, the program analyzes your specific situation and generates prioritized, actionable advice. Each tip includes estimated dollar savings where applicable.

**Retirement Strategies:**
- Max out 401(k) — including age 50+ catch-up ($7,500) and age 60-63 super catch-up ($11,250)
- Traditional IRA contributions
- HSA triple tax advantage (deductible in, tax-free growth, tax-free medical withdrawals)
- Backdoor Roth IRA for high earners
- Mega Backdoor Roth (if employer plan allows)
- Roth conversions during low-income years
- Solo 401(k) / SEP-IRA for self-employed

**Investment Strategies:**
- Tax-loss harvesting (with wash-sale rule warnings)
- Capital loss carryforward tracking
- Donate appreciated stock instead of cash to charity
- Donor-Advised Funds for deduction bunching
- ESPP holding period optimization

**RSU/GSU-Specific Strategies:**
- Sell-to-cover timing considerations
- Offset vesting income with pre-tax retirement contributions
- Charitable giving of appreciated vested shares
- Holding period planning for long-term capital gains rates

**Deduction Strategies:**
- Standard vs. itemized deduction bunching (alternate years)
- Donor-Advised Fund for multi-year charitable giving
- Section 199A QBI deduction awareness

**Timing and Planning:**
- Year-end tax moves checklist (accelerate deductions, defer income, harvest losses)
- Estimated tax payment warnings to avoid underpayment penalties
- Filing status optimization (MFJ vs. MFS comparison suggestion)
- State tax impact awareness for remote workers
- 529 plan for education savings + Roth IRA rollover
- ACA Premium Tax Credit for self-employed

---

## How It Works

The program runs in three interactive steps:

```
STEP 1: INCOME
  Answer simplified yes/no questions about each income source.
  Enter dollar amounts when prompted (press Enter to skip with $0 default).

STEP 2: DEDUCTIONS & CREDITS
  Enter your personal info (filing status, age, state).
  Answer questions about retirement contributions, home expenses,
  charitable giving, dependents, education, energy improvements, etc.

STEP 3: RESULTS
  View your complete tax summary:
  - Income breakdown
  - Deductions comparison (standard vs. itemized — auto-selects the better one)
  - Federal tax, capital gains tax, NIIT, AMT, FICA
  - All applicable credits
  - State tax estimate
  - Total tax liability and effective tax rate
  - Withholding and estimated payments vs. what you owe
  - Balance due or estimated refund

  Then: Personalized tax optimization tips sorted by priority and estimated savings.
```

---

## Project Structure

```
tax_app/
├── run.py                          # Entry point
├── requirements.txt                # Test dependencies
├── README.md
│
├── tax_app/
│   ├── __init__.py
│   ├── main.py                     # CLI interface, summary display, program flow
│   ├── tax_data.py                 # 2025 tax brackets, rates, limits, constants
│   ├── income.py                   # Income data models and collection prompts
│   ├── deductions.py               # Deduction/credit models, collection, and computation
│   ├── calculator.py               # Core tax calculation engine
│   └── tips.py                     # Personalized tax optimization advisor
│
└── tests/
    ├── __init__.py
    └── test_calculator.py          # 37 unit tests covering all modules
```

---

## Module Reference

### `tax_data.py` — Tax Constants
All 2025 tax year numbers in one place: federal brackets (all 4 filing statuses), standard deductions, long-term capital gains brackets, NIIT thresholds, FICA rates and wage bases, AMT exemptions, retirement contribution limits (401k, IRA, HSA with catch-up), IRA phaseouts, Child Tax Credit and EITC tables, QBI thresholds, SALT cap, and state income tax rates for all 50 states + DC.

### `income.py` — Income Collection
Dataclass models for every income type (`W2Income`, `StockIncome`, `SelfEmploymentIncome`, `OtherIncome`) wrapped in `AllIncome` with computed properties for net capital gains, ordinary income, investment income, AGI estimate, and capital loss carryforward. Includes the interactive collection functions with yes/no gating so users only answer questions relevant to their situation.

### `deductions.py` — Deductions & Credits
Dataclass models for above-the-line deductions, itemized deductions (with SALT cap and 7.5% AGI medical threshold), tax credits, and personal info. Contains computation functions for: standard deduction (with age/blindness additions), Child Tax Credit (with phaseout), Child Care Credit, American Opportunity and Lifetime Learning Credits, energy credits (home improvement, EV, solar), Saver's Credit, EITC, and QBI deduction.

### `calculator.py` — Tax Engine
The core `calculate_taxes()` function that orchestrates everything: computes AGI, compares standard vs. itemized, separates ordinary income from preferential-rate income (LTCG + qualified dividends), applies progressive brackets, stacks capital gains on ordinary income for proper rate calculation, computes NIIT, estimates AMT, calculates FICA and self-employment tax, applies all credits, estimates state tax, and determines balance due or refund.

### `tips.py` — Optimization Advisor
The `generate_tips()` function analyzes your complete tax picture and generates a prioritized list of actionable strategies with estimated dollar savings. Tips are sorted by priority (HIGH/MEDIUM/INFO) and potential savings amount.

### `main.py` — CLI Interface
The user-facing program flow: displays the banner, orchestrates the three collection steps, calls the calculator, prints a detailed formatted summary, and displays optimization tips.

---

## Example Output

```
============================================================
              YOUR 2025 TAX SUMMARY
============================================================

  Filing Status:    Single
  State:            CA
  Age:              32

------------------------------------------------------------
  INCOME
------------------------------------------------------------
  W-2 Wages:                        $     180,000
    (includes RSU/GSU vesting:       $      60,000)
  Long-Term Capital Gains:           $      25,000
  Qualified Dividends:               $       3,000
                                     ─────────────
  Gross Income:                      $     208,000

  ...

============================================================
  TOTAL TAX LIABILITY
============================================================
  Federal Tax:                       $      30,247
  FICA:                              $      15,006
  State Tax:                         $      25,679
                                     ═════════════
  TOTAL TAX:                         $      70,932
  Effective Tax Rate:                         34.1%

  ...

  >>> YOU OWE:                       $       2,150

============================================================
TAX OPTIMIZATION TIPS & STRATEGIES
============================================================

  Potential total savings identified: $12,430

  [!!!] 1. [Retirement] Max out your 401(k)
       Estimated savings: $5,170
       You contributed $10,000 to your 401(k) but the limit is
       $23,500. Contributing $13,500 more could save you ~$5,170
       in federal taxes this year.

  [!!!] 2. [RSU/GSU] RSU/GSU tax planning strategies
       Your RSU/GSU vesting income of $60,000 is taxed as ordinary
       income. Key strategies:
         1. SELL-TO-COVER TIMING: Check if your company lets you choose vest dates
         2. MAXIMIZE 401(k): Offset vesting income by maxing pre-tax contributions
         3. CHARITABLE GIVING: Donate appreciated RSU shares (held >1 year)...
  ...
```

---

## Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all 37 tests
python3 -m pytest tests/ -v
```

**Test coverage includes:**
- Progressive bracket tax computation (zero income, single bracket, multi-bracket)
- Marginal rate identification at various income levels
- Long-term capital gains stacking on ordinary income
- NIIT threshold and calculation
- Self-employment tax with deductible half
- Standard deduction for all filing statuses, age 65+, and blindness
- SALT cap enforcement on itemized deductions
- Child Tax Credit with phaseout
- Child and Dependent Care Credit
- American Opportunity Tax Credit
- QBI / Section 199A deduction
- Full end-to-end scenarios: simple W-2, high earner with RSUs, self-employed, married with children, capital loss limits, refund scenarios
- Tax tip generation and category verification
- State tax for no-tax states, California, and New York

---

## 2025 Tax Reference

<details>
<summary><strong>Federal Income Tax Brackets (click to expand)</strong></summary>

**Single:**

| Taxable Income | Rate |
|---|---|
| $0 - $11,925 | 10% |
| $11,926 - $48,475 | 12% |
| $48,476 - $103,350 | 22% |
| $103,351 - $197,300 | 24% |
| $197,301 - $250,525 | 32% |
| $250,526 - $626,350 | 35% |
| Over $626,350 | 37% |

**Married Filing Jointly:**

| Taxable Income | Rate |
|---|---|
| $0 - $23,850 | 10% |
| $23,851 - $96,950 | 12% |
| $96,951 - $206,700 | 22% |
| $206,701 - $394,600 | 24% |
| $394,601 - $501,050 | 32% |
| $501,051 - $751,600 | 35% |
| Over $751,600 | 37% |

</details>

<details>
<summary><strong>Key 2025 Limits (click to expand)</strong></summary>

| Item | Limit |
|---|---|
| 401(k) employee contribution | $23,500 |
| 401(k) catch-up (age 50-59, 64+) | +$7,500 |
| 401(k) super catch-up (age 60-63) | +$11,250 |
| Traditional/Roth IRA | $7,000 |
| IRA catch-up (age 50+) | +$1,000 |
| HSA (self-only) | $4,300 |
| HSA (family) | $8,550 |
| HSA catch-up (age 55+) | +$1,000 |
| Social Security wage base | $176,100 |
| SALT deduction cap | $10,000 |
| Student loan interest deduction | $2,500 |
| Educator expense deduction | $300 |
| Child Tax Credit | $2,000/child |

</details>

---

## Limitations

This is an estimator, not a tax filing tool. Key simplifications:

- **State taxes** use a single top marginal rate per state rather than full progressive state brackets
- **AMT** is a simplified estimate using SALT add-back only (does not account for ISO exercises, depreciation, or other AMT preference items)
- **EITC** uses a simplified threshold check rather than the full credit calculation schedule
- **Social Security taxability** uses a flat 85% estimate rather than the provisional income formula
- **Phaseouts** for some deductions (Traditional IRA, student loan interest) are simplified
- **Does not handle**: itemized state deductions, state-specific credits, multi-state filing, part-year residency, foreign earned income exclusion, passive activity loss rules, or estate/gift tax
- **No filing**: this tool estimates taxes — it does not generate or file any tax forms

For situations involving ISOs with AMT implications, complex partnership/S-corp K-1 income, multi-state residency, or international tax treaties, consult a CPA.

---

## Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/add-state-brackets`)
3. Ensure tests pass (`python3 -m pytest tests/ -v`)
4. Add tests for any new calculation logic
5. Submit a pull request

To update for a new tax year, modify the constants in `tax_data.py` — all brackets, limits, and thresholds are centralized there.

---

*Built with Python 3.9+ — no external dependencies required to run (pytest needed for tests only).*
