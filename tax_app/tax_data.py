"""
2025 Tax Year Data (for filing in 2026).
Federal tax brackets, standard deductions, capital gains rates, FICA, etc.
"""

# --- Filing Statuses ---
SINGLE = "single"
MARRIED_JOINT = "married_joint"
MARRIED_SEPARATE = "married_separate"
HEAD_OF_HOUSEHOLD = "head_of_household"

FILING_STATUS_LABELS = {
    SINGLE: "Single",
    MARRIED_JOINT: "Married Filing Jointly",
    MARRIED_SEPARATE: "Married Filing Separately",
    HEAD_OF_HOUSEHOLD: "Head of Household",
}

# --- 2025 Federal Income Tax Brackets ---
# (upper_bound, rate) — income up to upper_bound is taxed at rate
# Last bracket has no upper bound (None = infinity)
FEDERAL_BRACKETS = {
    SINGLE: [
        (11_925, 0.10),
        (48_475, 0.12),
        (103_350, 0.22),
        (197_300, 0.24),
        (250_525, 0.32),
        (626_350, 0.35),
        (None, 0.37),
    ],
    MARRIED_JOINT: [
        (23_850, 0.10),
        (96_950, 0.12),
        (206_700, 0.22),
        (394_600, 0.24),
        (501_050, 0.32),
        (751_600, 0.35),
        (None, 0.37),
    ],
    MARRIED_SEPARATE: [
        (11_925, 0.10),
        (48_475, 0.12),
        (103_350, 0.22),
        (197_300, 0.24),
        (250_525, 0.32),
        (375_800, 0.35),
        (None, 0.37),
    ],
    HEAD_OF_HOUSEHOLD: [
        (17_000, 0.10),
        (64_850, 0.12),
        (103_350, 0.22),
        (197_300, 0.24),
        (250_500, 0.32),
        (626_350, 0.35),
        (None, 0.37),
    ],
}

# --- Standard Deduction 2025 ---
STANDARD_DEDUCTION = {
    SINGLE: 15_000,
    MARRIED_JOINT: 30_000,
    MARRIED_SEPARATE: 15_000,
    HEAD_OF_HOUSEHOLD: 22_500,
}

# Additional standard deduction for age 65+ or blind (per person)
ADDITIONAL_STD_DEDUCTION = {
    SINGLE: 2_000,
    MARRIED_JOINT: 1_600,
    MARRIED_SEPARATE: 1_600,
    HEAD_OF_HOUSEHOLD: 2_000,
}

# --- Long-Term Capital Gains Tax Brackets 2025 ---
LTCG_BRACKETS = {
    SINGLE: [
        (48_350, 0.00),
        (533_400, 0.15),
        (None, 0.20),
    ],
    MARRIED_JOINT: [
        (96_700, 0.00),
        (600_050, 0.15),
        (None, 0.20),
    ],
    MARRIED_SEPARATE: [
        (48_350, 0.00),
        (300_000, 0.15),
        (None, 0.20),
    ],
    HEAD_OF_HOUSEHOLD: [
        (64_750, 0.00),
        (566_700, 0.15),
        (None, 0.20),
    ],
}

# Short-term capital gains are taxed as ordinary income (use FEDERAL_BRACKETS)

# --- Net Investment Income Tax (NIIT) ---
NIIT_RATE = 0.038
NIIT_THRESHOLDS = {
    SINGLE: 200_000,
    MARRIED_JOINT: 250_000,
    MARRIED_SEPARATE: 125_000,
    HEAD_OF_HOUSEHOLD: 200_000,
}

# --- FICA / Self-Employment Tax 2025 ---
SOCIAL_SECURITY_RATE_EMPLOYEE = 0.062
SOCIAL_SECURITY_RATE_SELF = 0.124
SOCIAL_SECURITY_WAGE_BASE = 176_100

MEDICARE_RATE_EMPLOYEE = 0.0145
MEDICARE_RATE_SELF = 0.029
MEDICARE_ADDITIONAL_RATE = 0.009  # Additional Medicare on high earners
MEDICARE_ADDITIONAL_THRESHOLDS = {
    SINGLE: 200_000,
    MARRIED_JOINT: 250_000,
    MARRIED_SEPARATE: 125_000,
    HEAD_OF_HOUSEHOLD: 200_000,
}

# --- AMT (Alternative Minimum Tax) 2025 ---
AMT_EXEMPTION = {
    SINGLE: 88_100,
    MARRIED_JOINT: 137_000,
    MARRIED_SEPARATE: 68_500,
    HEAD_OF_HOUSEHOLD: 88_100,
}
AMT_EXEMPTION_PHASEOUT_START = {
    SINGLE: 626_350,
    MARRIED_JOINT: 1_252_700,
    MARRIED_SEPARATE: 626_350,
    HEAD_OF_HOUSEHOLD: 626_350,
}
AMT_RATES = [(232_600, 0.26), (None, 0.28)]  # Single/HoH
AMT_RATES_MFJ = [(232_600, 0.26), (None, 0.28)]

# --- Retirement Contribution Limits 2025 ---
RETIREMENT_LIMITS = {
    "401k": 23_500,
    "401k_catchup_50": 7_500,   # Age 50-59 or 64+
    "401k_catchup_60_63": 11_250,  # Age 60-63 super catch-up
    "ira": 7_000,
    "ira_catchup_50": 1_000,
    "hsa_single": 4_300,
    "hsa_family": 8_550,
    "hsa_catchup_55": 1_000,
}

# --- IRA Deduction Phase-out (Traditional IRA, covered by employer plan) ---
IRA_PHASEOUT = {
    SINGLE: (79_000, 89_000),
    MARRIED_JOINT: (126_000, 146_000),  # Contributor covered
    MARRIED_SEPARATE: (0, 10_000),
    HEAD_OF_HOUSEHOLD: (79_000, 89_000),
}

# --- Child Tax Credit 2025 ---
CHILD_TAX_CREDIT = 2_000  # per qualifying child under 17
CHILD_TAX_CREDIT_OTHER_DEPENDENT = 500  # per other dependent
CTC_PHASEOUT_START = {
    SINGLE: 200_000,
    MARRIED_JOINT: 400_000,
    MARRIED_SEPARATE: 200_000,
    HEAD_OF_HOUSEHOLD: 200_000,
}
CTC_PHASEOUT_RATE = 50  # $50 reduction per $1,000 over threshold

# --- Earned Income Tax Credit 2025 (approximate) ---
EITC_MAX = {
    0: 649,
    1: 4_328,
    2: 7_152,
    3: 8_046,
}
EITC_INCOME_LIMITS_SINGLE = {
    0: 19_104,
    1: 50_434,
    2: 57_310,
    3: 61_555,
}
EITC_INCOME_LIMITS_JOINT = {
    0: 26_214,
    1: 57_554,
    2: 64_430,
    3: 68_675,
}

# --- Qualified Business Income (QBI) Deduction ---
QBI_DEDUCTION_RATE = 0.20
QBI_INCOME_THRESHOLD = {
    SINGLE: 197_300,
    MARRIED_JOINT: 394_600,
    MARRIED_SEPARATE: 197_300,
    HEAD_OF_HOUSEHOLD: 197_300,
}

# --- Student Loan Interest Deduction ---
STUDENT_LOAN_INTEREST_MAX = 2_500
STUDENT_LOAN_PHASEOUT = {
    SINGLE: (85_000, 100_000),
    MARRIED_JOINT: (145_000, 175_000),
    MARRIED_SEPARATE: (0, 0),  # Not available
    HEAD_OF_HOUSEHOLD: (85_000, 100_000),
}

# --- SALT Deduction Cap ---
SALT_CAP = 10_000  # State and Local Tax deduction cap

# --- Educator Expense Deduction ---
EDUCATOR_EXPENSE_MAX = 300

# --- State Income Tax Rates (simplified flat/top marginal for estimation) ---
STATE_TAX_RATES = {
    "AL": 0.050, "AK": 0.000, "AZ": 0.025, "AR": 0.039, "CA": 0.133,
    "CO": 0.044, "CT": 0.069, "DE": 0.066, "FL": 0.000, "GA": 0.055,
    "HI": 0.110, "ID": 0.058, "IL": 0.0495, "IN": 0.0305, "IA": 0.0380,
    "KS": 0.057, "KY": 0.040, "LA": 0.0425, "ME": 0.0715, "MD": 0.0575,
    "MA": 0.050, "MI": 0.0425, "MN": 0.0985, "MS": 0.050, "MO": 0.048,
    "MT": 0.059, "NE": 0.0584, "NV": 0.000, "NH": 0.000, "NJ": 0.1075,
    "NM": 0.059, "NY": 0.109, "NC": 0.045, "ND": 0.0225, "OH": 0.035,
    "OK": 0.0475, "OR": 0.099, "PA": 0.0307, "RI": 0.0599, "SC": 0.064,
    "SD": 0.000, "TN": 0.000, "TX": 0.000, "UT": 0.0465, "VT": 0.0875,
    "VA": 0.0575, "WA": 0.000, "WV": 0.0512, "WI": 0.0765, "WY": 0.000,
    "DC": 0.1075,
}

NO_INCOME_TAX_STATES = {"AK", "FL", "NV", "NH", "SD", "TN", "TX", "WA", "WY"}
