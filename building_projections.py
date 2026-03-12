#!/usr/bin/env python3
"""
Al Satwa Building Projection Model
Building: 24 Studios + 32 One-Bedrooms (56 units total)
Analyzes optimal pricing, occupancy targets, furnished vs unfurnished,
holiday home vs long-term, and hybrid strategies.
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from collections import OrderedDict
import os
import warnings
warnings.filterwarnings('ignore')

OUTPUT_DIR = 'report'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════
# BUILDING CONFIGURATION
# ══════════════════════════════════════════════════════════════════════
STUDIOS = 24
ONE_BEDS = 32
TOTAL_UNITS = STUDIOS + ONE_BEDS

# ══════════════════════════════════════════════════════════════════════
# MARKET DATA (from our analysis of 3,107 contracts)
# ══════════════════════════════════════════════════════════════════════

# ── Demand Curves: Price → Occupancy Rate (from renewal rate analysis) ──
# Higher renewal rate at lower prices = easier to fill = higher occupancy
# We model occupancy as a function of price using the observed data

# Studio: renewal rates by price bucket (from data)
# AED 30k=86%, 40k=63%, 50k=65%, 60k=7%, 90k=20%, 100k=14%
studio_demand = {
    30000: 0.95, 35000: 0.93, 40000: 0.90, 45000: 0.87,
    50000: 0.83, 55000: 0.78, 60000: 0.72, 65000: 0.65,
    70000: 0.58, 75000: 0.52, 80000: 0.47, 85000: 0.42,
    90000: 0.38, 95000: 0.34, 100000: 0.30, 110000: 0.25,
    120000: 0.20, 130000: 0.17, 140000: 0.14, 150000: 0.12,
}

# 1-Bed: renewal rates by price bucket (from data)
# AED 50k=82%, 60k=68%, 70k=31%, 80k=15%, 90k=10%, 100k=2%
onebed_demand = {
    50000: 0.95, 55000: 0.93, 60000: 0.90, 65000: 0.86,
    70000: 0.80, 75000: 0.75, 80000: 0.68, 85000: 0.60,
    90000: 0.52, 95000: 0.45, 100000: 0.38, 105000: 0.32,
    110000: 0.27, 115000: 0.23, 120000: 0.20, 130000: 0.15,
    140000: 0.12, 150000: 0.10,
}

def interpolate_occupancy(price, demand_curve):
    """Interpolate occupancy for a given price from demand curve."""
    prices = sorted(demand_curve.keys())
    if price <= prices[0]:
        return demand_curve[prices[0]]
    if price >= prices[-1]:
        return demand_curve[prices[-1]]
    for i in range(len(prices)-1):
        if prices[i] <= price <= prices[i+1]:
            ratio = (price - prices[i]) / (prices[i+1] - prices[i])
            return demand_curve[prices[i]] * (1 - ratio) + demand_curve[prices[i+1]] * ratio
    return 0.5

def find_price_for_occupancy(target_occ, demand_curve):
    """Find the price that achieves a target occupancy rate."""
    prices = sorted(demand_curve.keys())
    for p in range(prices[0], prices[-1], 500):
        occ = interpolate_occupancy(p, demand_curve)
        if occ <= target_occ:
            return p
    return prices[-1]

# ── Market Reference Prices ──
MARKET_DATA = {
    'Studio': {
        'unfurnished_median': 50000,
        'unfurnished_avg': 68319,
        'furnished_avg': 118375,
        'furnished_premium': 0.733,  # 73.3%
        'avg_size_sqft': 428,
        'avg_sqft_rate': 158,
    },
    '1 Bedroom': {
        'unfurnished_median': 80000,
        'unfurnished_avg': 76132,
        'furnished_avg': 107724,
        'furnished_premium': 0.415,  # 41.5%
        'avg_size_sqft': 809,
        'avg_sqft_rate': 102,
    }
}

# ══════════════════════════════════════════════════════════════════════
# SECTION 1: INDIVIDUAL UNIT RENT PROJECTIONS
# ══════════════════════════════════════════════════════════════════════

print("=" * 80)
print("AL SATWA BUILDING PROJECTION MODEL")
print(f"Building: {STUDIOS} Studios + {ONE_BEDS} One-Bedrooms = {TOTAL_UNITS} Units")
print("=" * 80)

print("\n" + "─" * 80)
print("SECTION 1: EXPECTED RENT PER UNIT (Market Rate)")
print("─" * 80)

for unit_type in ['Studio', '1 Bedroom']:
    m = MARKET_DATA[unit_type]
    count = STUDIOS if unit_type == 'Studio' else ONE_BEDS
    print(f"\n  ▶ {unit_type} (x{count} units)")
    print(f"    ┌─────────────────────┬──────────────┬──────────────┬──────────────┐")
    print(f"    │ Scenario            │ Per Unit/yr  │ Per Unit/mo  │ All Units/yr │")
    print(f"    ├─────────────────────┼──────────────┼──────────────┼──────────────┤")

    unfurn = m['unfurnished_avg']
    furn = m['furnished_avg']

    print(f"    │ Unfurnished         │ AED {unfurn:>8,.0f} │ AED {unfurn/12:>8,.0f} │ AED {unfurn*count:>8,.0f} │")
    print(f"    │ Furnished           │ AED {furn:>8,.0f} │ AED {furn/12:>8,.0f} │ AED {furn*count:>8,.0f} │")
    print(f"    │ Furnished Premium   │     +{m['furnished_premium']*100:.1f}%    │              │              │")
    print(f"    └─────────────────────┴──────────────┴──────────────┴──────────────┘")

# Total building projections at market rate
total_unfurn = MARKET_DATA['Studio']['unfurnished_avg'] * STUDIOS + MARKET_DATA['1 Bedroom']['unfurnished_avg'] * ONE_BEDS
total_furn = MARKET_DATA['Studio']['furnished_avg'] * STUDIOS + MARKET_DATA['1 Bedroom']['furnished_avg'] * ONE_BEDS

print(f"\n  ▶ TOTAL BUILDING (at 100% occupancy)")
print(f"    Unfurnished: AED {total_unfurn:,.0f}/year (AED {total_unfurn/12:,.0f}/month)")
print(f"    Furnished:   AED {total_furn:,.0f}/year (AED {total_furn/12:,.0f}/month)")

# ══════════════════════════════════════════════════════════════════════
# SECTION 2: OPTIMAL PRICING FOR 80% AND 90% OCCUPANCY
# ══════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("SECTION 2: OPTIMAL PRICING FOR TARGET OCCUPANCY")
print("─" * 80)

results_table = []

for target_occ in [0.80, 0.90]:
    print(f"\n  ▶ Target: {target_occ*100:.0f}% Occupancy")
    print(f"    ┌─────────────────────────┬──────────────┬──────────────┬───────────┬──────────────┐")
    print(f"    │ Unit Type               │ Optimal Rent │  Monthly     │ Occ Units │ Gross Rev/yr │")
    print(f"    ├─────────────────────────┼──────────────┼──────────────┼───────────┼──────────────┤")

    total_rev = 0

    for unit_type, demand, count, furn_mult in [
        ('Studio (Unfurn)', studio_demand, STUDIOS, 1.0),
        ('Studio (Furn)', studio_demand, STUDIOS, 1.733),
        ('1-Bed (Unfurn)', onebed_demand, ONE_BEDS, 1.0),
        ('1-Bed (Furn)', onebed_demand, ONE_BEDS, 1.415),
    ]:
        base_price = find_price_for_occupancy(target_occ, demand)
        price = int(base_price * furn_mult)
        occ_units = int(count * target_occ)
        annual_rev = price * occ_units
        total_rev += annual_rev

        results_table.append({
            'target_occ': target_occ,
            'unit_type': unit_type,
            'price': price,
            'occ_units': occ_units,
            'total_units': count,
            'annual_rev': annual_rev,
        })

        print(f"    │ {unit_type:<23} │ AED {price:>8,.0f} │ AED {price/12:>8,.0f} │ {occ_units:>4}/{count:<4} │ AED {annual_rev:>8,.0f} │")

    print(f"    └─────────────────────────┴──────────────┴──────────────┴───────────┴──────────────┘")

# ══════════════════════════════════════════════════════════════════════
# SECTION 3: REVENUE MAXIMIZATION ANALYSIS
# ══════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("SECTION 3: REVENUE MAXIMIZATION - FIND THE SWEET SPOT")
print("─" * 80)

def revenue_at_price(price, demand_curve, num_units, is_furnished=False, furn_premium=0):
    """Calculate expected annual revenue at a given price point."""
    # For furnished, we need to find the base price equivalent for occupancy
    if is_furnished and furn_premium > 0:
        base_price = price / (1 + furn_premium)
    else:
        base_price = price
    occ = interpolate_occupancy(base_price, demand_curve)
    occupied = num_units * occ
    revenue = price * occupied
    return revenue, occ, occupied

print("\n  ▶ Studio Revenue Curve (Unfurnished)")
print(f"    {'Price':>12} {'Occupancy':>10} {'Occupied':>10} {'Annual Rev':>14} {'Monthly Rev':>14}")
best_studio_unfurn = (0, 0, 0, 0)
for p in range(30000, 130001, 5000):
    rev, occ, occupied = revenue_at_price(p, studio_demand, STUDIOS)
    print(f"    AED {p:>8,} {occ:>9.0%} {occupied:>9.1f} AED {rev:>12,.0f} AED {rev/12:>12,.0f}")
    if rev > best_studio_unfurn[0]:
        best_studio_unfurn = (rev, p, occ, occupied)

print(f"\n    ★ OPTIMAL: AED {best_studio_unfurn[1]:,}/yr at {best_studio_unfurn[2]:.0%} occupancy = AED {best_studio_unfurn[0]:,.0f}/yr")

print("\n  ▶ Studio Revenue Curve (Furnished)")
best_studio_furn = (0, 0, 0, 0)
for p in range(50000, 220001, 5000):
    rev, occ, occupied = revenue_at_price(p, studio_demand, STUDIOS, True, 0.733)
    if occ >= 0.10:
        if rev > best_studio_furn[0]:
            best_studio_furn = (rev, p, occ, occupied)

print(f"    ★ OPTIMAL: AED {best_studio_furn[1]:,}/yr at {best_studio_furn[2]:.0%} occupancy = AED {best_studio_furn[0]:,.0f}/yr")

print("\n  ▶ 1-Bedroom Revenue Curve (Unfurnished)")
print(f"    {'Price':>12} {'Occupancy':>10} {'Occupied':>10} {'Annual Rev':>14} {'Monthly Rev':>14}")
best_1bed_unfurn = (0, 0, 0, 0)
for p in range(50000, 160001, 5000):
    rev, occ, occupied = revenue_at_price(p, onebed_demand, ONE_BEDS)
    print(f"    AED {p:>8,} {occ:>9.0%} {occupied:>9.1f} AED {rev:>12,.0f} AED {rev/12:>12,.0f}")
    if rev > best_1bed_unfurn[0]:
        best_1bed_unfurn = (rev, p, occ, occupied)

print(f"\n    ★ OPTIMAL: AED {best_1bed_unfurn[1]:,}/yr at {best_1bed_unfurn[2]:.0%} occupancy = AED {best_1bed_unfurn[0]:,.0f}/yr")

print("\n  ▶ 1-Bedroom Revenue Curve (Furnished)")
best_1bed_furn = (0, 0, 0, 0)
for p in range(70000, 250001, 5000):
    rev, occ, occupied = revenue_at_price(p, onebed_demand, ONE_BEDS, True, 0.415)
    if occ >= 0.10:
        if rev > best_1bed_furn[0]:
            best_1bed_furn = (rev, p, occ, occupied)

print(f"    ★ OPTIMAL: AED {best_1bed_furn[1]:,}/yr at {best_1bed_furn[2]:.0%} occupancy = AED {best_1bed_furn[0]:,.0f}/yr")

# ══════════════════════════════════════════════════════════════════════
# SECTION 4: FURNISHED vs UNFURNISHED COMPARISON
# ══════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("SECTION 4: FURNISHED vs UNFURNISHED - FULL COMPARISON")
print("─" * 80)

# Furnishing costs (estimates for Dubai)
FURN_COST_STUDIO = 25000   # AED to furnish a studio
FURN_COST_1BED = 40000     # AED to furnish a 1-bed
FURN_REPLACEMENT_YRS = 4   # Replace furniture every 4 years

print("\n  ▶ Furnishing Investment Required")
print(f"    Studio: AED {FURN_COST_STUDIO:,} x {STUDIOS} = AED {FURN_COST_STUDIO * STUDIOS:,}")
print(f"    1-Bed:  AED {FURN_COST_1BED:,} x {ONE_BEDS} = AED {FURN_COST_1BED * ONE_BEDS:,}")
total_furn_cost = FURN_COST_STUDIO * STUDIOS + FURN_COST_1BED * ONE_BEDS
print(f"    Total:  AED {total_furn_cost:,}")
print(f"    Amortized/yr (over {FURN_REPLACEMENT_YRS}yrs): AED {total_furn_cost/FURN_REPLACEMENT_YRS:,.0f}")

# Compare scenarios at 80% and 90% occupancy
for target_label, target_occ in [("80% Occupancy", 0.80), ("90% Occupancy", 0.90)]:
    print(f"\n  ▶ {target_label} Comparison")

    # Unfurnished
    s_price_u = find_price_for_occupancy(target_occ, studio_demand)
    b_price_u = find_price_for_occupancy(target_occ, onebed_demand)
    s_units_u = int(STUDIOS * target_occ)
    b_units_u = int(ONE_BEDS * target_occ)
    rev_unfurn = s_price_u * s_units_u + b_price_u * b_units_u

    # Furnished
    s_price_f = int(s_price_u * 1.733)
    b_price_f = int(b_price_u * 1.415)
    s_units_f = int(STUDIOS * target_occ)
    b_units_f = int(ONE_BEDS * target_occ)
    rev_furn = s_price_f * s_units_f + b_price_f * b_units_f
    furn_annual_cost = total_furn_cost / FURN_REPLACEMENT_YRS
    net_furn = rev_furn - furn_annual_cost

    print(f"    ┌────────────────────┬──────────────────┬──────────────────┬──────────────────┐")
    print(f"    │                    │   Unfurnished    │    Furnished     │   Difference     │")
    print(f"    ├────────────────────┼──────────────────┼──────────────────┼──────────────────┤")
    print(f"    │ Studio Rent/yr     │ AED {s_price_u:>10,} │ AED {s_price_f:>10,} │ +AED {s_price_f-s_price_u:>9,} │")
    print(f"    │ 1-Bed Rent/yr      │ AED {b_price_u:>10,} │ AED {b_price_f:>10,} │ +AED {b_price_f-b_price_u:>9,} │")
    print(f"    │ Gross Revenue/yr   │ AED {rev_unfurn:>10,} │ AED {rev_furn:>10,} │ +AED {rev_furn-rev_unfurn:>9,} │")
    print(f"    │ Furniture Cost/yr  │ AED {0:>10,} │ AED {furn_annual_cost:>10,.0f} │                  │")
    print(f"    │ Net Revenue/yr     │ AED {rev_unfurn:>10,} │ AED {net_furn:>10,.0f} │ +AED {net_furn-rev_unfurn:>9,.0f} │")
    print(f"    │ Net Revenue/mo     │ AED {rev_unfurn/12:>10,.0f} │ AED {net_furn/12:>10,.0f} │ +AED {(net_furn-rev_unfurn)/12:>9,.0f} │")
    print(f"    └────────────────────┴──────────────────┴──────────────────┴──────────────────┘")
    print(f"    ROI on furnishing investment: {(rev_furn - rev_unfurn) / total_furn_cost * 100:.1f}% in Year 1")

# ══════════════════════════════════════════════════════════════════════
# SECTION 5: HOLIDAY HOME / AIRBNB ANALYSIS
# ══════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("SECTION 5: HOLIDAY HOME (AIRBNB-STYLE) ANALYSIS")
print("─" * 80)

# Dubai holiday home market data (based on market indicators)
# Sources: Dubai Tourism data, Airbnb market reports, DTCM statistics
# Peak seasons: Oct-Apr (high), May-Sep (low/summer)

# Monthly occupancy rates for holiday homes in Dubai (industry benchmarks)
HOLIDAY_OCCUPANCY = {
    1: 0.82,   # January - peak tourist season
    2: 0.85,   # February - peak
    3: 0.78,   # March - high
    4: 0.68,   # April - shoulder
    5: 0.45,   # May - low season starts
    6: 0.35,   # June - summer low
    7: 0.38,   # July - summer low
    8: 0.40,   # August - summer low (some summer tourism)
    9: 0.48,   # September - recovering
    10: 0.72,  # October - high season starts
    11: 0.80,  # November - high season
    12: 0.88,  # December - peak (holidays, NYE)
}

# Nightly rates (AED) - based on furnished market data and Airbnb benchmarks
NIGHTLY_RATES = {
    'Studio': {
        'peak': 450,     # Oct-Mar
        'shoulder': 350, # Apr, Sep
        'low': 250,      # May-Aug
    },
    '1 Bedroom': {
        'peak': 600,
        'shoulder': 480,
        'low': 350,
    }
}

def get_season(month):
    if month in [10, 11, 12, 1, 2, 3]:
        return 'peak'
    elif month in [4, 9]:
        return 'shoulder'
    else:
        return 'low'

def calculate_holiday_revenue(unit_type, num_units):
    """Calculate annual revenue for holiday home units."""
    total_revenue = 0
    monthly_breakdown = []

    for month in range(1, 13):
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1]
        occ_rate = HOLIDAY_OCCUPANCY[month]
        season = get_season(month)
        nightly_rate = NIGHTLY_RATES[unit_type][season]

        occupied_nights = days_in_month * occ_rate * num_units
        monthly_rev = occupied_nights * nightly_rate
        total_revenue += monthly_rev

        monthly_breakdown.append({
            'month': month,
            'month_name': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month-1],
            'season': season,
            'occ_rate': occ_rate,
            'nightly_rate': nightly_rate,
            'occupied_nights': occupied_nights,
            'revenue': monthly_rev,
            'days': days_in_month,
        })

    return total_revenue, monthly_breakdown

print("\n  ▶ Holiday Home Nightly Rates (AED)")
print(f"    ┌─────────────┬──────────┬──────────┬──────────┐")
print(f"    │ Unit Type   │   Peak   │ Shoulder │   Low    │")
print(f"    │             │ Oct-Mar  │ Apr,Sep  │ May-Aug  │")
print(f"    ├─────────────┼──────────┼──────────┼──────────┤")
print(f"    │ Studio      │ AED  450 │ AED  350 │ AED  250 │")
print(f"    │ 1 Bedroom   │ AED  600 │ AED  480 │ AED  350 │")
print(f"    └─────────────┴──────────┴──────────┴──────────┘")

print("\n  ▶ Monthly Occupancy Rates (Holiday Home Market)")
for m in range(1, 13):
    name = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][m-1]
    occ = HOLIDAY_OCCUPANCY[m]
    bar = '█' * int(occ * 40)
    print(f"    {name}: {occ:>4.0%} {bar}")

# Calculate for ALL units as holiday homes
print("\n  ▶ If ALL Units Were Holiday Homes")
for unit_type, count in [('Studio', STUDIOS), ('1 Bedroom', ONE_BEDS)]:
    rev, breakdown = calculate_holiday_revenue(unit_type, count)
    avg_occ = sum(m['occ_rate'] for m in breakdown) / 12

    print(f"\n    {unit_type} (x{count}):")
    print(f"    {'Month':>5} {'Season':>8} {'Rate':>8} {'Occ%':>6} {'Occ Nights':>12} {'Revenue':>14}")
    for m in breakdown:
        print(f"    {m['month_name']:>5} {m['season']:>8} AED {m['nightly_rate']:>4} {m['occ_rate']:>5.0%} {m['occupied_nights']:>11.0f} AED {m['revenue']:>12,.0f}")
    print(f"    {'─'*65}")
    print(f"    TOTAL{' '*29} AED {rev:>12,.0f}")
    print(f"    Average occupancy: {avg_occ:.0%}")
    print(f"    Equivalent annual rent per unit: AED {rev/count:,.0f}")

# Holiday home operating costs
HH_MGMT_FEE = 0.20  # 20% management fee
HH_CLEANING = 150    # AED per turnover (studio)
HH_CLEANING_1B = 200 # AED per turnover (1-bed)
HH_UTILITIES = 500   # AED/month per unit
HH_DTCM_LICENSE = 1520  # AED/year per unit
HH_INSURANCE = 2000  # AED/year per unit

print("\n  ▶ Holiday Home Operating Costs")
s_rev_total, s_breakdown = calculate_holiday_revenue('Studio', STUDIOS)
b_rev_total, b_breakdown = calculate_holiday_revenue('1 Bedroom', ONE_BEDS)
total_hh_gross = s_rev_total + b_rev_total

# Estimate turnovers (avg stay 4 nights)
avg_stay = 4
s_total_nights = sum(m['occupied_nights'] for m in s_breakdown)
b_total_nights = sum(m['occupied_nights'] for m in b_breakdown)
s_turnovers = s_total_nights / avg_stay
b_turnovers = b_total_nights / avg_stay

mgmt_fee = total_hh_gross * HH_MGMT_FEE
cleaning_cost = s_turnovers * HH_CLEANING + b_turnovers * HH_CLEANING_1B
utilities = HH_UTILITIES * 12 * TOTAL_UNITS
licensing = HH_DTCM_LICENSE * TOTAL_UNITS
insurance = HH_INSURANCE * TOTAL_UNITS
furn_cost_annual = total_furn_cost / 3  # Faster replacement for holiday homes (3yr)
total_hh_costs = mgmt_fee + cleaning_cost + utilities + licensing + insurance + furn_cost_annual
net_hh = total_hh_gross - total_hh_costs

print(f"    Gross Revenue:      AED {total_hh_gross:>12,.0f}")
print(f"    Management (20%):  -AED {mgmt_fee:>12,.0f}")
print(f"    Cleaning/turnover: -AED {cleaning_cost:>12,.0f}  ({s_turnovers+b_turnovers:.0f} turnovers, avg {avg_stay}-night stay)")
print(f"    Utilities:         -AED {utilities:>12,.0f}  (AED {HH_UTILITIES}/unit/month)")
print(f"    DTCM Licensing:    -AED {licensing:>12,.0f}  (AED {HH_DTCM_LICENSE}/unit/yr)")
print(f"    Insurance:         -AED {insurance:>12,.0f}")
print(f"    Furniture (3yr):   -AED {furn_cost_annual:>12,.0f}")
print(f"    {'─'*45}")
print(f"    Total Costs:       -AED {total_hh_costs:>12,.0f}")
print(f"    NET REVENUE:        AED {net_hh:>12,.0f}")
print(f"    NET per month:      AED {net_hh/12:>12,.0f}")

# ══════════════════════════════════════════════════════════════════════
# SECTION 6: STRATEGY COMPARISON - LONG-TERM vs HOLIDAY HOME vs HYBRID
# ══════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("SECTION 6: STRATEGY COMPARISON")
print("─" * 80)

strategies = OrderedDict()

# Strategy A: All Long-Term Unfurnished (90% occ)
s_p = find_price_for_occupancy(0.90, studio_demand)
b_p = find_price_for_occupancy(0.90, onebed_demand)
rev_a = s_p * int(STUDIOS * 0.90) + b_p * int(ONE_BEDS * 0.90)
cost_a = 0  # Minimal operating costs for unfurnished
net_a = rev_a
strategies['A: All Long-Term\n   Unfurnished (90% occ)'] = {'gross': rev_a, 'costs': cost_a, 'net': net_a}

# Strategy B: All Long-Term Furnished (90% occ)
s_p_f = int(s_p * 1.733)
b_p_f = int(b_p * 1.415)
rev_b = s_p_f * int(STUDIOS * 0.90) + b_p_f * int(ONE_BEDS * 0.90)
cost_b = total_furn_cost / FURN_REPLACEMENT_YRS
net_b = rev_b - cost_b
strategies['B: All Long-Term\n   Furnished (90% occ)'] = {'gross': rev_b, 'costs': cost_b, 'net': net_b}

# Strategy C: All Holiday Homes
strategies['C: All Holiday Homes\n   (56 units)'] = {'gross': total_hh_gross, 'costs': total_hh_costs, 'net': net_hh}

# Strategy D-G: Hybrid scenarios
for hh_studios, hh_1beds, label_suffix in [
    (5, 5, 'D: Hybrid Light\n   5S + 5B holiday'),
    (8, 8, 'E: Hybrid Medium\n   8S + 8B holiday'),
    (10, 10, 'F: Hybrid Heavy\n   10S + 10B holiday'),
    (5, 10, 'G: Hybrid Optimized\n   5S + 10B holiday'),
]:
    lt_studios = STUDIOS - hh_studios
    lt_1beds = ONE_BEDS - hh_1beds

    # Long-term furnished revenue (90% occ)
    lt_s_price = int(find_price_for_occupancy(0.90, studio_demand) * 1.733)
    lt_b_price = int(find_price_for_occupancy(0.90, onebed_demand) * 1.415)
    lt_rev = lt_s_price * int(lt_studios * 0.90) + lt_b_price * int(lt_1beds * 0.90)
    lt_furn_cost = (FURN_COST_STUDIO * lt_studios + FURN_COST_1BED * lt_1beds) / FURN_REPLACEMENT_YRS

    # Holiday home revenue
    hh_s_rev, hh_s_bd = calculate_holiday_revenue('Studio', hh_studios)
    hh_b_rev, hh_b_bd = calculate_holiday_revenue('1 Bedroom', hh_1beds)
    hh_rev = hh_s_rev + hh_b_rev

    hh_s_nights = sum(m['occupied_nights'] for m in hh_s_bd)
    hh_b_nights = sum(m['occupied_nights'] for m in hh_b_bd)
    hh_turnovers_s = hh_s_nights / avg_stay
    hh_turnovers_b = hh_b_nights / avg_stay

    hh_total_units = hh_studios + hh_1beds
    hh_mgmt = hh_rev * HH_MGMT_FEE
    hh_clean = hh_turnovers_s * HH_CLEANING + hh_turnovers_b * HH_CLEANING_1B
    hh_util = HH_UTILITIES * 12 * hh_total_units
    hh_lic = HH_DTCM_LICENSE * hh_total_units
    hh_ins = HH_INSURANCE * hh_total_units
    hh_furn = (FURN_COST_STUDIO * hh_studios + FURN_COST_1BED * hh_1beds) / 3
    hh_costs = hh_mgmt + hh_clean + hh_util + hh_lic + hh_ins + hh_furn

    total_gross = lt_rev + hh_rev
    total_costs = lt_furn_cost + hh_costs
    total_net = total_gross - total_costs

    strategies[label_suffix] = {'gross': total_gross, 'costs': total_costs, 'net': total_net,
                                'lt_rev': lt_rev, 'hh_rev': hh_rev,
                                'hh_studios': hh_studios, 'hh_1beds': hh_1beds}

print(f"\n  ┌─{'─'*32}┬{'─'*16}┬{'─'*16}┬{'─'*16}┬{'─'*16}┐")
print(f"  │ {'Strategy':<32}│ {'Gross Rev/yr':>14} │ {'Costs/yr':>14} │ {'Net Rev/yr':>14} │ {'Net Rev/mo':>14} │")
print(f"  ├─{'─'*32}┼{'─'*16}┼{'─'*16}┼{'─'*16}┼{'─'*16}┤")

best_strategy = None
best_net = 0

for name, data in strategies.items():
    gross = data['gross']
    costs = data['costs']
    net = data['net']

    if net > best_net:
        best_net = net
        best_strategy = name

    # Handle multi-line names
    lines = name.split('\n')
    print(f"  │ {lines[0]:<32}│ AED {gross:>10,.0f} │ AED {costs:>10,.0f} │ AED {net:>10,.0f} │ AED {net/12:>10,.0f} │")
    for extra_line in lines[1:]:
        print(f"  │ {extra_line:<32}│{' '*16}│{' '*16}│{' '*16}│{' '*16}│")

print(f"  └─{'─'*32}┴{'─'*16}┴{'─'*16}┴{'─'*16}┴{'─'*16}┘")
print(f"\n  ★ BEST STRATEGY: {best_strategy.replace(chr(10), ' ')} → AED {best_net:,.0f}/yr (AED {best_net/12:,.0f}/mo)")

# ══════════════════════════════════════════════════════════════════════
# SECTION 7: DETAILED HYBRID RECOMMENDATION
# ══════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("SECTION 7: RECOMMENDED STRATEGY - DETAILED BREAKDOWN")
print("─" * 80)

# Find the best hybrid
best_hybrid_name = None
best_hybrid_net = 0
for name, data in strategies.items():
    if 'Hybrid' in name and data['net'] > best_hybrid_net:
        best_hybrid_net = data['net']
        best_hybrid_name = name

print(f"\n  Best Hybrid: {best_hybrid_name.replace(chr(10), ' ')}")
best_data = strategies[best_hybrid_name]

print(f"\n  ▶ Revenue Breakdown")
if 'lt_rev' in best_data:
    print(f"    Long-term Revenue:  AED {best_data['lt_rev']:>12,.0f}")
    print(f"    Holiday Home Rev:   AED {best_data['hh_rev']:>12,.0f}")
print(f"    Total Gross:        AED {best_data['gross']:>12,.0f}")
print(f"    Total Costs:       -AED {best_data['costs']:>12,.0f}")
print(f"    NET Revenue:        AED {best_data['net']:>12,.0f}")
print(f"    NET per month:      AED {best_data['net']/12:>12,.0f}")

# Compare vs all long-term unfurnished
base_net = strategies['A: All Long-Term\n   Unfurnished (90% occ)']['net']
uplift = best_data['net'] - base_net
uplift_pct = uplift / base_net * 100

print(f"\n  ▶ vs All Long-Term Unfurnished:")
print(f"    Additional revenue: +AED {uplift:,.0f}/yr (+{uplift_pct:.1f}%)")

# ══════════════════════════════════════════════════════════════════════
# SECTION 8: VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════

plt.style.use('seaborn-v0_8-whitegrid')

# ── Fig 11: Strategy Comparison Bar Chart ──
fig, ax = plt.subplots(figsize=(16, 8))
strat_names = [k.replace('\n', ' ') for k in strategies.keys()]
net_values = [v['net'] for v in strategies.values()]
gross_values = [v['gross'] for v in strategies.values()]
cost_values = [v['costs'] for v in strategies.values()]

x = np.arange(len(strat_names))
width = 0.35

bars1 = ax.bar(x - width/2, [g/1000 for g in gross_values], width, label='Gross Revenue', color='#4CAF50', alpha=0.7)
bars2 = ax.bar(x + width/2, [n/1000 for n in net_values], width, label='Net Revenue', color='#2196F3', alpha=0.85)

# Highlight the best
best_idx = net_values.index(max(net_values))
bars2[best_idx].set_color('#FF9800')
bars2[best_idx].set_alpha(1.0)

ax.set_ylabel('Revenue (AED Thousands)')
ax.set_title('Strategy Comparison: Annual Revenue', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(strat_names, rotation=25, ha='right', fontsize=9)
ax.legend()

for bar, val in zip(bars2, net_values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
            f'AED {val/1000:.0f}K', ha='center', va='bottom', fontsize=8, fontweight='bold')

fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/11_strategy_comparison.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 12: Holiday Home Monthly Revenue ──
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for ax, (unit_type, count) in zip(axes, [('Studio', STUDIOS), ('1 Bedroom', ONE_BEDS)]):
    rev, breakdown = calculate_holiday_revenue(unit_type, count)
    months = [m['month_name'] for m in breakdown]
    revenues = [m['revenue'] for m in breakdown]
    occ_rates = [m['occ_rate'] for m in breakdown]

    colors = ['#FF5722' if m['season'] == 'peak' else '#FF9800' if m['season'] == 'shoulder' else '#2196F3' for m in breakdown]

    ax2 = ax.twinx()
    ax.bar(months, [r/1000 for r in revenues], color=colors, alpha=0.7, edgecolor='white')
    ax2.plot(months, [o*100 for o in occ_rates], color='black', linewidth=2, marker='o', markersize=6)

    ax.set_ylabel('Revenue (AED Thousands)')
    ax2.set_ylabel('Occupancy Rate (%)')
    ax.set_title(f'{unit_type} (x{count}) - Holiday Home Monthly', fontsize=12, fontweight='bold')
    ax2.set_ylim(0, 100)

fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/12_holiday_home_monthly.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 13: Revenue Optimization Curves ──
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

for ax, (unit_type, demand, count, color) in zip(axes, [
    ('Studio', studio_demand, STUDIOS, '#2196F3'),
    ('1 Bedroom', onebed_demand, ONE_BEDS, '#FF9800')
]):
    prices = list(range(min(demand.keys()), max(demand.keys()), 2000))
    revenues_u = []
    revenues_f = []
    occupancies = []
    furn_prem = 0.733 if unit_type == 'Studio' else 0.415

    for p in prices:
        rev, occ, _ = revenue_at_price(p, demand, count)
        rev_f, _, _ = revenue_at_price(int(p * (1+furn_prem)), demand, count, True, furn_prem)
        revenues_u.append(rev / 1000)
        revenues_f.append(rev_f / 1000)
        occupancies.append(occ * 100)

    ax2 = ax.twinx()
    ax.plot(prices, revenues_u, color=color, linewidth=2, label='Unfurnished Rev')
    ax.plot(prices, revenues_f, color=color, linewidth=2, linestyle='--', label='Furnished Rev')
    ax2.plot(prices, occupancies, color='gray', linewidth=1.5, linestyle=':', label='Occupancy %')

    # Mark 80% and 90% lines
    ax2.axhline(80, color='red', linestyle='--', alpha=0.5, linewidth=1)
    ax2.axhline(90, color='green', linestyle='--', alpha=0.5, linewidth=1)
    ax2.text(prices[-1], 81, '80%', color='red', fontsize=9)
    ax2.text(prices[-1], 91, '90%', color='green', fontsize=9)

    ax.set_xlabel('Annual Rent per Unit (AED)')
    ax.set_ylabel('Total Revenue (AED Thousands)')
    ax2.set_ylabel('Occupancy Rate (%)')
    ax.set_title(f'{unit_type} (x{count}) - Revenue vs Price', fontsize=12, fontweight='bold')
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1000:.0f}K'))

fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/13_revenue_optimization.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 14: Furnished vs Unfurnished Comparison ──
fig, ax = plt.subplots(figsize=(14, 7))
scenarios = ['Unfurnished\n80% Occ', 'Unfurnished\n90% Occ', 'Furnished\n80% Occ', 'Furnished\n90% Occ', 'Holiday Home\nAll Units', 'Best Hybrid']

# Calculate all scenario values
s80u = find_price_for_occupancy(0.80, studio_demand)
b80u = find_price_for_occupancy(0.80, onebed_demand)
s90u = find_price_for_occupancy(0.90, studio_demand)
b90u = find_price_for_occupancy(0.90, onebed_demand)

scenario_net = [
    s80u * int(STUDIOS*0.80) + b80u * int(ONE_BEDS*0.80),  # Unfurn 80%
    s90u * int(STUDIOS*0.90) + b90u * int(ONE_BEDS*0.90),  # Unfurn 90%
    int(s80u*1.733)*int(STUDIOS*0.80) + int(b80u*1.415)*int(ONE_BEDS*0.80) - total_furn_cost/FURN_REPLACEMENT_YRS,  # Furn 80%
    int(s90u*1.733)*int(STUDIOS*0.90) + int(b90u*1.415)*int(ONE_BEDS*0.90) - total_furn_cost/FURN_REPLACEMENT_YRS,  # Furn 90%
    net_hh,  # Holiday home
    best_data['net'],  # Best hybrid
]

colors_bar = ['#90CAF9', '#2196F3', '#FFCC80', '#FF9800', '#EF5350', '#4CAF50']
bars = ax.bar(scenarios, [v/1000 for v in scenario_net], color=colors_bar, edgecolor='white', width=0.6)

for bar, val in zip(bars, scenario_net):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
            f'AED {val/1000:.0f}K\n({val/12/1000:.0f}K/mo)', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_ylabel('Net Annual Revenue (AED Thousands)')
ax.set_title('Net Revenue Comparison: All Strategies', fontsize=14, fontweight='bold')
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/14_all_strategies_comparison.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 15: Hybrid Breakdown Pie ──
if 'lt_rev' in best_data:
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Revenue sources
    ax = axes[0]
    ax.pie([best_data['lt_rev'], best_data['hh_rev']],
           labels=['Long-Term Lets', 'Holiday Homes'],
           autopct='%1.1f%%', colors=['#2196F3', '#FF9800'], startangle=90)
    ax.set_title('Revenue Split (Best Hybrid)', fontsize=12, fontweight='bold')

    # Unit allocation
    ax = axes[1]
    lt_s = STUDIOS - best_data.get('hh_studios', 0)
    lt_b = ONE_BEDS - best_data.get('hh_1beds', 0)
    hh_s = best_data.get('hh_studios', 0)
    hh_b = best_data.get('hh_1beds', 0)
    ax.pie([lt_s, lt_b, hh_s, hh_b],
           labels=[f'LT Studios ({lt_s})', f'LT 1-Beds ({lt_b})',
                   f'HH Studios ({hh_s})', f'HH 1-Beds ({hh_b})'],
           autopct='%1.1f%%',
           colors=['#90CAF9', '#2196F3', '#FFCC80', '#FF9800'], startangle=90)
    ax.set_title('Unit Allocation (Best Hybrid)', fontsize=12, fontweight='bold')

    fig.tight_layout()
    fig.savefig(f'{OUTPUT_DIR}/15_hybrid_breakdown.png', dpi=150, bbox_inches='tight')
    plt.close()

print(f"\n✓ All projection charts saved to '{OUTPUT_DIR}/' directory")
print("\nProjection model complete.")
