#!/usr/bin/env python3
"""
Generate a comprehensive HTML visual report combining rental analysis
and building projections for Al Satwa.
Also generates additional summary dashboard visuals.
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
import base64
import os
import warnings
warnings.filterwarnings('ignore')

OUTPUT_DIR = 'report'
CSV_FILE = 'al-satwa-market-data-mhaegan-aclan-eva-real-estate-llc-11-03-2026-e48bd6c4cce45cc9c132ad7cbc904b9023f19a57.csv'

# ── Load data ──
df = pd.read_csv(CSV_FILE, encoding='latin-1')
df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')
df['annualised_rental_price'] = pd.to_numeric(df['annualised_rental_price'], errors='coerce')
df['rent_price_sqft_unit'] = pd.to_numeric(df['rent_price_sqft_unit'], errors='coerce')
df['unit_size'] = pd.to_numeric(df['unit_size'], errors='coerce')
df['bed_type'] = df['beds'].astype(str).str.strip()

studio = df[df['bed_type'] == 's'].copy()
one_bed = df[df['bed_type'] == '1'].copy()

plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {'Studio': '#2196F3', '1 Bedroom': '#FF9800', 'highlight': '#4CAF50', 'danger': '#EF5350'}

# ══════════════════════════════════════════════════════════════════════
# ADDITIONAL VISUALS
# ══════════════════════════════════════════════════════════════════════

# ── Fig 16: Executive Dashboard - KPI Cards ──
fig, axes = plt.subplots(2, 4, figsize=(20, 8))
fig.suptitle('AL SATWA RENTAL MARKET - KEY METRICS DASHBOARD', fontsize=18, fontweight='bold', y=1.02)

kpis = [
    ('Total Contracts', '6,414', 'In Dataset', '#1565C0'),
    ('Studio Contracts', '224', '3.5% of total', COLORS['Studio']),
    ('1-Bed Contracts', '2,883', '44.9% of total', COLORS['1 Bedroom']),
    ('Date Range', 'Sep 25\nto Mar 26', '7 months', '#7B1FA2'),
    ('Studio Avg Rent', 'AED 71K', 'AED 50K median', COLORS['Studio']),
    ('1-Bed Avg Rent', 'AED 79K', 'AED 80K median', COLORS['1 Bedroom']),
    ('Furnished Premium', '+73% Studio\n+42% 1-Bed', 'vs unfurnished', COLORS['highlight']),
    ('Best Strategy Net', 'AED 3.37M', 'AED 281K/month', '#FF6F00'),
]

for ax, (title, value, subtitle, color) in zip(axes.flatten(), kpis):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])

    # Background
    rect = mpatches.FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.05",
                                     facecolor=color, alpha=0.12, edgecolor=color, linewidth=2)
    ax.add_patch(rect)

    ax.text(0.5, 0.82, title, ha='center', va='center', fontsize=11, fontweight='bold', color='#333')
    ax.text(0.5, 0.48, value, ha='center', va='center', fontsize=18, fontweight='bold', color=color)
    ax.text(0.5, 0.18, subtitle, ha='center', va='center', fontsize=10, color='#666')

fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/16_dashboard_kpis.png', dpi=150, bbox_inches='tight')
plt.close()
print("Created: 16_dashboard_kpis.png")

# ── Fig 17: Price Trend Over Time ──
fig, axes = plt.subplots(1, 2, figsize=(18, 6))
for ax, (label, data, color) in zip(axes, [('Studio', studio, COLORS['Studio']), ('1 Bedroom', one_bed, COLORS['1 Bedroom'])]):
    monthly = data.set_index('start_date').resample('ME').agg(
        avg_rent=('annualised_rental_price', 'mean'),
        median_rent=('annualised_rental_price', 'median'),
        count=('annualised_rental_price', 'count')
    ).dropna()
    if len(monthly) > 1:
        ax.plot(monthly.index, monthly['avg_rent']/1000, color=color, linewidth=2.5, marker='o', markersize=8, label='Average')
        ax.plot(monthly.index, monthly['median_rent']/1000, color=color, linewidth=2, marker='s', markersize=6, linestyle='--', alpha=0.7, label='Median')
        ax.fill_between(monthly.index, monthly['avg_rent']/1000, monthly['median_rent']/1000, color=color, alpha=0.1)

        for i, (idx, row) in enumerate(monthly.iterrows()):
            ax.annotate(f"AED {row['avg_rent']/1000:.0f}K\n({int(row['count'])})",
                       (idx, row['avg_rent']/1000), textcoords="offset points",
                       xytext=(0, 15), ha='center', fontsize=8, fontweight='bold')

    ax.set_title(f'{label} - Monthly Rent Trend', fontsize=13, fontweight='bold')
    ax.set_ylabel('Rent (AED Thousands)')
    ax.set_xlabel('Month')
    ax.legend()
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/17_price_trend.png', dpi=150, bbox_inches='tight')
plt.close()
print("Created: 17_price_trend.png")

# ── Fig 18: Size vs Rent Scatter ──
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
for ax, (label, data, color) in zip(axes, [('Studio', studio, COLORS['Studio']), ('1 Bedroom', one_bed, COLORS['1 Bedroom'])]):
    valid = data.dropna(subset=['unit_size', 'annualised_rental_price'])
    valid = valid[(valid['unit_size'] > 0) & (valid['unit_size'] < 3000)]
    ax.scatter(valid['unit_size'], valid['annualised_rental_price']/1000, c=color, alpha=0.4, s=30, edgecolors='white', linewidth=0.5)

    # Trend line
    if len(valid) > 5:
        z = np.polyfit(valid['unit_size'], valid['annualised_rental_price']/1000, 1)
        p = np.poly1d(z)
        x_range = np.linspace(valid['unit_size'].min(), valid['unit_size'].max(), 100)
        ax.plot(x_range, p(x_range), color='red', linewidth=2, linestyle='--', label=f'Trend: AED {z[0]*1000:.0f}/sqft')

    ax.set_title(f'{label} - Unit Size vs Rent', fontsize=13, fontweight='bold')
    ax.set_xlabel('Unit Size (sqft)')
    ax.set_ylabel('Annual Rent (AED Thousands)')
    ax.legend()
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/18_size_vs_rent.png', dpi=150, bbox_inches='tight')
plt.close()
print("Created: 18_size_vs_rent.png")

# ── Fig 19: Building Projection Summary ──
fig = plt.figure(figsize=(20, 10))

# Main comparison
ax1 = fig.add_subplot(121)
strategies = {
    'All Unfurnished\nLong-Term': 2520000,
    'All Furnished\nLong-Term': 3362920,
    'All Holiday\nHomes': 3122766,
    'Hybrid Light\n5+5 Holiday': 3372592,
    'Hybrid Medium\n8+8 Holiday': 3285862,
    'Hybrid Heavy\n10+10 Holiday': 3228043,
    'Hybrid Optimized\n5S+10B Holiday': 3313915,
}
colors_strat = ['#90CAF9', '#2196F3', '#EF5350', '#4CAF50', '#81C784', '#A5D6A7', '#66BB6A']
bars = ax1.bar(range(len(strategies)), [v/1e6 for v in strategies.values()], color=colors_strat, edgecolor='white', width=0.7)

# Highlight winner
bars[3].set_edgecolor('#FF6F00')
bars[3].set_linewidth(3)

for bar, (name, val) in zip(bars, strategies.items()):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
             f'AED {val/1e6:.2f}M\n({val/12/1000:.0f}K/mo)', ha='center', fontsize=8, fontweight='bold')

ax1.set_xticks(range(len(strategies)))
ax1.set_xticklabels(strategies.keys(), fontsize=8, rotation=0)
ax1.set_ylabel('Net Annual Revenue (AED Millions)')
ax1.set_title('NET Revenue by Strategy', fontsize=14, fontweight='bold')
ax1.set_ylim(0, max(strategies.values())/1e6 * 1.2)

# Pricing for occupancy targets
ax2 = fig.add_subplot(122)
categories = ['Studio\nUnfurn', 'Studio\nFurn', '1-Bed\nUnfurn', '1-Bed\nFurn']
occ80 = [53000, 91849, 70000, 99050]
occ90 = [40000, 69320, 60000, 84900]

x = np.arange(len(categories))
width = 0.35
b1 = ax2.bar(x - width/2, [v/1000 for v in occ90], width, label='90% Occupancy', color='#4CAF50', alpha=0.85)
b2 = ax2.bar(x + width/2, [v/1000 for v in occ80], width, label='80% Occupancy', color='#FF9800', alpha=0.85)

for bar, val in zip(b1, occ90):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'AED {val/1000:.0f}K', ha='center', fontsize=9, fontweight='bold')
for bar, val in zip(b2, occ80):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f'AED {val/1000:.0f}K', ha='center', fontsize=9, fontweight='bold')

ax2.set_xticks(x)
ax2.set_xticklabels(categories, fontsize=10)
ax2.set_ylabel('Annual Rent per Unit (AED Thousands)')
ax2.set_title('Optimal Pricing by Occupancy Target', fontsize=14, fontweight='bold')
ax2.legend(fontsize=11)
ax2.set_ylim(0, 130)

fig.suptitle('AL SATWA BUILDING: 24 Studios + 32 One-Beds', fontsize=16, fontweight='bold', y=1.01)
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/19_building_summary.png', dpi=150, bbox_inches='tight')
plt.close()
print("Created: 19_building_summary.png")

# ── Fig 20: Holiday Home Seasonal Revenue Waterfall ──
fig, ax = plt.subplots(figsize=(16, 7))

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
occupancy = [0.82, 0.85, 0.78, 0.68, 0.45, 0.35, 0.38, 0.40, 0.48, 0.72, 0.80, 0.88]
days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

# 10 holiday units: 5 studios + 5 one-beds
studio_rates = [450, 450, 450, 350, 250, 250, 250, 250, 350, 450, 450, 450]
onebed_rates = [600, 600, 600, 480, 350, 350, 350, 350, 480, 600, 600, 600]

monthly_rev = []
for i in range(12):
    s_rev = days[i] * occupancy[i] * 5 * studio_rates[i]
    b_rev = days[i] * occupancy[i] * 5 * onebed_rates[i]
    monthly_rev.append(s_rev + b_rev)

colors_month = ['#4CAF50' if occupancy[i] >= 0.72 else '#FF9800' if occupancy[i] >= 0.48 else '#EF5350' for i in range(12)]

bars = ax.bar(months, [r/1000 for r in monthly_rev], color=colors_month, edgecolor='white', width=0.7)

# Occupancy line on secondary axis
ax2 = ax.twinx()
ax2.plot(months, [o*100 for o in occupancy], color='#1565C0', linewidth=3, marker='D', markersize=8, zorder=5)
ax2.set_ylabel('Occupancy Rate (%)', color='#1565C0', fontsize=12)
ax2.set_ylim(0, 100)
ax2.tick_params(axis='y', labelcolor='#1565C0')

for bar, rev, occ in zip(bars, monthly_rev, occupancy):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'AED {rev/1000:.0f}K\n{occ:.0%}', ha='center', fontsize=9, fontweight='bold')

ax.set_ylabel('Revenue (AED Thousands)', fontsize=12)
ax.set_title('Holiday Home Monthly Revenue & Occupancy (10 Units: 5 Studios + 5 One-Beds)', fontsize=14, fontweight='bold')

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#4CAF50', label='Peak Season'),
                   Patch(facecolor='#FF9800', label='Shoulder Season'),
                   Patch(facecolor='#EF5350', label='Low Season')]
ax.legend(handles=legend_elements, loc='upper left', fontsize=10)

fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/20_holiday_seasonal.png', dpi=150, bbox_inches='tight')
plt.close()
print("Created: 20_holiday_seasonal.png")

# ── Fig 21: Furnished ROI Visualization ──
fig, ax = plt.subplots(figsize=(14, 7))

years = [0, 1, 2, 3, 4, 5]
furn_investment = 1880000
annual_furn_premium_80 = 994381  # Net extra revenue from furnishing at 80% occ
annual_furn_premium_90 = 842920  # at 90% occ

cumulative_80 = [-furn_investment + annual_furn_premium_80 * y for y in years]
cumulative_90 = [-furn_investment + annual_furn_premium_90 * y for y in years]

ax.plot(years, [v/1e6 for v in cumulative_80], color='#FF9800', linewidth=3, marker='o', markersize=10, label='At 80% Occupancy')
ax.plot(years, [v/1e6 for v in cumulative_90], color='#4CAF50', linewidth=3, marker='s', markersize=10, label='At 90% Occupancy')
ax.axhline(0, color='red', linewidth=2, linestyle='--', alpha=0.7)
ax.fill_between(years, [v/1e6 for v in cumulative_80], 0, alpha=0.1, color='#FF9800')
ax.fill_between(years, [v/1e6 for v in cumulative_90], 0, alpha=0.1, color='#4CAF50')

for y in years:
    ax.annotate(f'AED {cumulative_80[y]/1e6:.2f}M', (y, cumulative_80[y]/1e6),
               textcoords="offset points", xytext=(10, 10), fontsize=9, fontweight='bold', color='#FF9800')
    ax.annotate(f'AED {cumulative_90[y]/1e6:.2f}M', (y, cumulative_90[y]/1e6),
               textcoords="offset points", xytext=(10, -15), fontsize=9, fontweight='bold', color='#4CAF50')

# Breakeven markers
be_80 = furn_investment / annual_furn_premium_80
be_90 = furn_investment / annual_furn_premium_90
ax.axvline(be_80, color='#FF9800', linestyle=':', alpha=0.5)
ax.axvline(be_90, color='#4CAF50', linestyle=':', alpha=0.5)
ax.text(be_80, ax.get_ylim()[0] * 0.9, f'Breakeven\n{be_80:.1f} yrs', ha='center', fontsize=9, color='#FF9800')
ax.text(be_90, ax.get_ylim()[0] * 0.7, f'Breakeven\n{be_90:.1f} yrs', ha='center', fontsize=9, color='#4CAF50')

ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Cumulative Net Benefit (AED Millions)', fontsize=12)
ax.set_title('Furnished Investment ROI Over Time\n(Investment: AED 1.88M for 56 units)', fontsize=14, fontweight='bold')
ax.legend(fontsize=12)
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/21_furnished_roi.png', dpi=150, bbox_inches='tight')
plt.close()
print("Created: 21_furnished_roi.png")

# ── Fig 22: Demand Curve Visualization ──
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

studio_demand = {
    30000: 0.95, 35000: 0.93, 40000: 0.90, 45000: 0.87,
    50000: 0.83, 55000: 0.78, 60000: 0.72, 65000: 0.65,
    70000: 0.58, 75000: 0.52, 80000: 0.47, 85000: 0.42,
    90000: 0.38, 95000: 0.34, 100000: 0.30, 110000: 0.25,
    120000: 0.20,
}
onebed_demand = {
    50000: 0.95, 55000: 0.93, 60000: 0.90, 65000: 0.86,
    70000: 0.80, 75000: 0.75, 80000: 0.68, 85000: 0.60,
    90000: 0.52, 95000: 0.45, 100000: 0.38, 105000: 0.32,
    110000: 0.27, 115000: 0.23, 120000: 0.20,
}

for ax, (label, demand, color, opt_price) in zip(axes, [
    ('Studio', studio_demand, COLORS['Studio'], 60000),
    ('1 Bedroom', onebed_demand, COLORS['1 Bedroom'], 75000)
]):
    prices = list(demand.keys())
    occs = [demand[p]*100 for p in prices]
    revs = [p * demand[p] / 1000 for p in prices]

    ax2 = ax.twinx()
    ax.fill_between([p/1000 for p in prices], occs, alpha=0.15, color=color)
    ax.plot([p/1000 for p in prices], occs, color=color, linewidth=3, marker='o', markersize=6, label='Occupancy %')
    ax2.plot([p/1000 for p in prices], revs, color='#EF5350', linewidth=2.5, marker='s', markersize=5, linestyle='--', label='Revenue/unit (AED K)')

    # Mark 80% and 90% lines
    ax.axhline(80, color='green', linestyle=':', alpha=0.6, linewidth=1.5)
    ax.axhline(90, color='blue', linestyle=':', alpha=0.6, linewidth=1.5)
    ax.text(prices[-1]/1000, 81, '80%', fontsize=9, color='green', fontweight='bold')
    ax.text(prices[-1]/1000, 91, '90%', fontsize=9, color='blue', fontweight='bold')

    # Mark optimal
    ax.axvline(opt_price/1000, color='#FF6F00', linewidth=2, linestyle='-', alpha=0.7)
    ax.text(opt_price/1000 + 2, 50, f'Optimal\nAED {opt_price/1000:.0f}K', fontsize=10, color='#FF6F00', fontweight='bold')

    ax.set_xlabel('Annual Rent (AED Thousands)', fontsize=11)
    ax.set_ylabel('Occupancy Rate (%)', color=color, fontsize=11)
    ax2.set_ylabel('Revenue per Unit (AED Thousands)', color='#EF5350', fontsize=11)
    ax.set_title(f'{label} - Demand Curve & Revenue', fontsize=13, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')

fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/22_demand_curves.png', dpi=150, bbox_inches='tight')
plt.close()
print("Created: 22_demand_curves.png")

# ══════════════════════════════════════════════════════════════════════
# BUILD HTML REPORT
# ══════════════════════════════════════════════════════════════════════

def img_to_base64(filepath):
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def embed_img(filename, alt=""):
    path = f'{OUTPUT_DIR}/{filename}'
    if os.path.exists(path):
        b64 = img_to_base64(path)
        return f'<img src="data:image/png;base64,{b64}" alt="{alt}" style="width:100%; max-width:1200px; margin: 20px auto; display:block; border-radius:8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">'
    return f'<p style="color:red;">Image not found: {filename}</p>'

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Al Satwa Rental Market Analysis & Building Projections Report</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background: #f5f5f5;
        color: #333;
        line-height: 1.6;
    }}
    .header {{
        background: linear-gradient(135deg, #1565C0, #0D47A1);
        color: white;
        padding: 60px 40px;
        text-align: center;
    }}
    .header h1 {{ font-size: 2.4em; margin-bottom: 10px; letter-spacing: 1px; }}
    .header .subtitle {{ font-size: 1.2em; opacity: 0.9; }}
    .header .meta {{ margin-top: 20px; font-size: 0.95em; opacity: 0.8; }}
    .container {{ max-width: 1300px; margin: 0 auto; padding: 20px; }}
    .section {{
        background: white;
        margin: 30px 0;
        padding: 40px;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }}
    .section h2 {{
        color: #1565C0;
        font-size: 1.8em;
        margin-bottom: 25px;
        padding-bottom: 10px;
        border-bottom: 3px solid #1565C0;
    }}
    .section h3 {{
        color: #333;
        font-size: 1.3em;
        margin: 25px 0 15px 0;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 0.95em;
    }}
    th {{
        background: #1565C0;
        color: white;
        padding: 14px 18px;
        text-align: left;
        font-weight: 600;
    }}
    td {{
        padding: 12px 18px;
        border-bottom: 1px solid #e0e0e0;
    }}
    tr:nth-child(even) {{ background: #f8f9fa; }}
    tr:hover {{ background: #e3f2fd; }}
    .highlight {{ background: #E8F5E9 !important; font-weight: bold; }}
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 20px;
        margin: 25px 0;
    }}
    .kpi-card {{
        background: white;
        border-radius: 10px;
        padding: 25px;
        text-align: center;
        border-left: 4px solid #1565C0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }}
    .kpi-card .value {{ font-size: 1.8em; font-weight: bold; color: #1565C0; margin: 10px 0; }}
    .kpi-card .label {{ font-size: 0.9em; color: #666; }}
    .kpi-card.green {{ border-left-color: #4CAF50; }}
    .kpi-card.green .value {{ color: #4CAF50; }}
    .kpi-card.orange {{ border-left-color: #FF9800; }}
    .kpi-card.orange .value {{ color: #FF9800; }}
    .kpi-card.red {{ border-left-color: #EF5350; }}
    .kpi-card.red .value {{ color: #EF5350; }}
    .recommendation {{
        background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
        border: 2px solid #4CAF50;
        border-radius: 12px;
        padding: 30px;
        margin: 25px 0;
    }}
    .recommendation h3 {{ color: #2E7D32; margin-bottom: 15px; }}
    .warning {{
        background: #FFF3E0;
        border-left: 4px solid #FF9800;
        padding: 20px;
        margin: 15px 0;
        border-radius: 0 8px 8px 0;
    }}
    .insight {{
        background: #E3F2FD;
        border-left: 4px solid #2196F3;
        padding: 15px 20px;
        margin: 15px 0;
        border-radius: 0 8px 8px 0;
        font-style: italic;
    }}
    .footer {{
        text-align: center;
        padding: 40px;
        color: #666;
        font-size: 0.9em;
    }}
    .toc {{
        background: #FAFAFA;
        padding: 25px 30px;
        border-radius: 8px;
        margin: 20px 0;
    }}
    .toc a {{ color: #1565C0; text-decoration: none; }}
    .toc a:hover {{ text-decoration: underline; }}
    .toc ol {{ padding-left: 25px; }}
    .toc li {{ margin: 8px 0; }}
</style>
</head>
<body>

<div class="header">
    <h1>Al Satwa Rental Market Analysis</h1>
    <div class="subtitle">Comprehensive Market Study & Building Investment Projections</div>
    <div class="meta">
        March 12, 2026 | Based on 6,414 rental contracts | Al Satwa, Dubai<br>
        Building Model: 24 Studios + 32 One-Bedrooms = 56 Units
    </div>
</div>

<div class="container">

<!-- TABLE OF CONTENTS -->
<div class="section">
    <h2>Table of Contents</h2>
    <div class="toc">
        <ol>
            <li><a href="#dashboard">Executive Dashboard</a></li>
            <li><a href="#market">Market Analysis: Studio & 1-Bedroom Rents</a></li>
            <li><a href="#distribution">Price Distribution (AED 5,000 Increments)</a></li>
            <li><a href="#sqft">Rent per Square Foot Analysis</a></li>
            <li><a href="#communities">Top Communities & Highest-Paying Comments</a></li>
            <li><a href="#occupancy">Occupancy Rate Analysis</a></li>
            <li><a href="#projections">Building Projections: Optimal Pricing</a></li>
            <li><a href="#furnished">Furnished vs Unfurnished ROI</a></li>
            <li><a href="#holiday">Holiday Home / Airbnb Analysis</a></li>
            <li><a href="#strategy">Strategy Comparison & Recommendation</a></li>
        </ol>
    </div>
</div>

<!-- SECTION 1: DASHBOARD -->
<div class="section" id="dashboard">
    <h2>1. Executive Dashboard</h2>

    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="label">Total Contracts Analyzed</div>
            <div class="value">6,414</div>
            <div class="label">Sep 2025 - Mar 2026</div>
        </div>
        <div class="kpi-card">
            <div class="label">Studio Average Rent</div>
            <div class="value">AED 71K</div>
            <div class="label">224 contracts | Median AED 50K</div>
        </div>
        <div class="kpi-card orange">
            <div class="label">1-Bed Average Rent</div>
            <div class="value">AED 79K</div>
            <div class="label">2,883 contracts | Median AED 80K</div>
        </div>
        <div class="kpi-card green">
            <div class="label">Best Strategy Net Revenue</div>
            <div class="value">AED 3.37M/yr</div>
            <div class="label">Hybrid: 46 long-term + 10 holiday</div>
        </div>
    </div>

    {embed_img('16_dashboard_kpis.png', 'KPI Dashboard')}
</div>

<!-- SECTION 2: MARKET ANALYSIS -->
<div class="section" id="market">
    <h2>2. Market Analysis: Studio & 1-Bedroom Rents</h2>

    <h3>Price Statistics</h3>
    <table>
        <tr>
            <th>Metric</th><th>Studio (224 contracts)</th><th>1-Bedroom (2,883 contracts)</th>
        </tr>
        <tr class="highlight"><td>Highest Rent</td><td>AED 961,000 (Sep 20, 2025 - KAY 1 Building, JGC)</td><td>AED 289,895 (Feb 2, 2026 - Eden House)</td></tr>
        <tr><td>Lowest Rent</td><td>AED 10,928 (Feb 1, 2026)</td><td>AED 20,000 (Jan 1, 2026)</td></tr>
        <tr><td>Average Rent</td><td>AED 71,000</td><td>AED 78,992</td></tr>
        <tr><td>Median Rent</td><td>AED 50,000</td><td>AED 79,999</td></tr>
        <tr><td>Std Deviation</td><td>AED 79,186 (high variance)</td><td>AED 20,262 (consistent)</td></tr>
    </table>

    {embed_img('01_price_distribution.png', 'Price Distribution')}

    <div class="insight">Studio rents show extremely high variance (std AED 79K on avg AED 71K) due to a wide range from basic units (AED 35-50K) to premium furnished units (AED 100-150K+). One-bedroom pricing is much more consistent, tightly clustered around AED 70-90K.</div>

    {embed_img('02_boxplot_comparison.png', 'Box Plot Comparison')}

    <h3>Price Trend Over Time</h3>
    {embed_img('17_price_trend.png', 'Price Trend')}
</div>

<!-- SECTION 3: PRICE DISTRIBUTION -->
<div class="section" id="distribution">
    <h2>3. Price Distribution (AED 5,000 Increments)</h2>

    <h3>Studio - Most Common: AED 45,000 - 50,000 (39 contracts, 17.4%)</h3>
    <table>
        <tr><th>Price Range</th><th>Contracts</th><th>Share</th></tr>
        <tr class="highlight"><td>AED 45,000 - 50,000</td><td>39</td><td>17.4%</td></tr>
        <tr><td>AED 40,000 - 45,000</td><td>34</td><td>15.2%</td></tr>
        <tr><td>AED 50,000 - 55,000</td><td>25</td><td>11.2%</td></tr>
        <tr><td>AED 60,000 - 65,000</td><td>23</td><td>10.3%</td></tr>
        <tr><td>AED 35,000 - 40,000</td><td>18</td><td>8.0%</td></tr>
        <tr><td>AED 55,000 - 60,000</td><td>18</td><td>8.0%</td></tr>
    </table>

    <h3>1-Bedroom - Most Common: AED 80,000 - 85,000 (544 contracts, 18.9%)</h3>
    <table>
        <tr><th>Price Range</th><th>Contracts</th><th>Share</th></tr>
        <tr class="highlight"><td>AED 80,000 - 85,000</td><td>544</td><td>18.9%</td></tr>
        <tr><td>AED 75,000 - 80,000</td><td>392</td><td>13.6%</td></tr>
        <tr><td>AED 70,000 - 75,000</td><td>286</td><td>9.9%</td></tr>
        <tr><td>AED 85,000 - 90,000</td><td>260</td><td>9.0%</td></tr>
        <tr><td>AED 60,000 - 65,000</td><td>201</td><td>7.0%</td></tr>
        <tr><td>AED 65,000 - 70,000</td><td>181</td><td>6.3%</td></tr>
    </table>
</div>

<!-- SECTION 4: SQFT -->
<div class="section" id="sqft">
    <h2>4. Rent per Square Foot Analysis</h2>

    <table>
        <tr><th>Metric</th><th>Studio</th><th>1-Bedroom</th></tr>
        <tr><td>Average Rent/sqft</td><td>AED 158</td><td>AED 102</td></tr>
        <tr><td>Median Rent/sqft</td><td>AED 150</td><td>AED 100</td></tr>
        <tr><td>Max Rent/sqft</td><td>AED 402</td><td>AED 340</td></tr>
        <tr><td>Avg Unit Size</td><td>428 sqft</td><td>809 sqft</td></tr>
        <tr class="highlight"><td>Studio Premium per sqft</td><td colspan="2">+55% (AED 158 vs AED 102)</td></tr>
    </table>

    {embed_img('04_rent_per_sqft.png', 'Rent per Sqft')}

    <h3>Unit Size vs Rent Relationship</h3>
    {embed_img('18_size_vs_rent.png', 'Size vs Rent Scatter')}

    <div class="insight">Studios command a 55% premium per square foot despite being half the size. This makes studios more efficient from a landlord yield perspective - a key consideration for the building strategy.</div>
</div>

<!-- SECTION 5: COMMUNITIES -->
<div class="section" id="communities">
    <h2>5. Top Communities & Highest-Paying Comments</h2>

    <h3>Top Communities by Average Rent</h3>
    <table>
        <tr><th>Community</th><th>Type</th><th>Avg Rent</th><th>Max Rent</th><th>Contracts</th><th>Avg/sqft</th></tr>
        <tr class="highlight"><td>Eden House</td><td>Studio</td><td>AED 146,005</td><td>AED 282,000</td><td>24</td><td>AED 265</td></tr>
        <tr class="highlight"><td>Eden House</td><td>1-Bed</td><td>AED 130,613</td><td>AED 289,895</td><td>279</td><td>AED 140</td></tr>
        <tr><td>Jumeirah Garden City</td><td>Studio</td><td>AED 65,746</td><td>AED 961,000</td><td>82</td><td>AED 162</td></tr>
        <tr><td>Jumeirah Garden City</td><td>1-Bed</td><td>AED 82,043</td><td>AED 270,000</td><td>1,097</td><td>AED 105</td></tr>
        <tr><td>South Heights Tower</td><td>Studio</td><td>AED 46,749</td><td>AED 63,000</td><td>29</td><td>AED 120</td></tr>
        <tr><td>South Heights Tower</td><td>1-Bed</td><td>AED 68,310</td><td>AED 93,000</td><td>378</td><td>AED 85</td></tr>
    </table>

    {embed_img('03_top_communities.png', 'Top Communities')}
    {embed_img('08_community_comparison.png', 'Community Comparison')}

    <h3>Comments Associated with Highest Rents</h3>
    <div class="insight">Listings with keywords "Furnished", "Brand New", "Burj Khalifa View" consistently command premiums of AED 150,000-290,000 - roughly 2-3x the market average.</div>

    {embed_img('09_comments_highest_rents.png', 'Comments & Rents')}
</div>

<!-- SECTION 6: OCCUPANCY -->
<div class="section" id="occupancy">
    <h2>6. Occupancy Rate Analysis</h2>

    <h3>Contract Type Distribution (Occupancy Proxy)</h3>
    <table>
        <tr><th>Metric</th><th>Studio</th><th>1-Bedroom</th><th>All Types</th></tr>
        <tr><td>Renewals</td><td>113 (50.4%)</td><td>946 (32.8%)</td><td>2,390 (37.3%)</td></tr>
        <tr><td>New Contracts</td><td>70 (31.2%)</td><td>570 (19.8%)</td><td>1,145 (17.9%)</td></tr>
        <tr class="highlight"><td>Est. Occupancy (Renewal Rate)</td><td>50.4%</td><td>32.8%</td><td>37.3%</td></tr>
    </table>

    <div class="insight">Studios show notably higher tenant retention (50.4% renewal) vs 1-bedrooms (32.8%), suggesting the studio market is tighter with fewer alternatives for tenants.</div>

    {embed_img('05_occupancy_new_vs_renewal.png', 'Occupancy Indicators')}
    {embed_img('06_monthly_volume.png', 'Monthly Volume')}

    <h3>Contract Duration</h3>
    <table>
        <tr><th>Duration</th><th>Count</th><th>Share</th></tr>
        <tr><td>Short-term (&lt;6 months)</td><td>1,416</td><td>45.6%</td></tr>
        <tr><td>Standard (6-12 months)</td><td>1,583</td><td>50.9%</td></tr>
        <tr><td>Long-term (&gt;12 months)</td><td>108</td><td>3.5%</td></tr>
    </table>

    {embed_img('07_contract_duration.png', 'Contract Duration')}

    <h3>Airbnb / Short-Term Indicators</h3>
    <table>
        <tr><th>Indicator</th><th>Studio</th><th>1-Bedroom</th></tr>
        <tr><td>Furnished/All-bills listings</td><td>12 (5.4%)</td><td>263 (9.1%)</td></tr>
        <tr><td>Avg rent (furnished keywords)</td><td>AED 118,375</td><td>AED 107,625</td></tr>
        <tr class="highlight"><td>Premium vs market average</td><td>+67%</td><td>+36%</td></tr>
    </table>

    {embed_img('10_airbnb_indicators.png', 'Airbnb Indicators')}
</div>

<!-- SECTION 7: PROJECTIONS -->
<div class="section" id="projections">
    <h2>7. Building Projections: 24 Studios + 32 One-Beds</h2>

    <h3>Expected Rent Per Unit (Market Rate, 100% Occupancy)</h3>
    <table>
        <tr><th>Unit Type</th><th>Per Unit/Year</th><th>Per Unit/Month</th><th>All Units/Year</th></tr>
        <tr><td>Studio Unfurnished</td><td>AED 68,319</td><td>AED 5,693</td><td>AED 1,639,656</td></tr>
        <tr><td>Studio Furnished (+73.3%)</td><td>AED 118,375</td><td>AED 9,865</td><td>AED 2,841,000</td></tr>
        <tr><td>1-Bed Unfurnished</td><td>AED 76,132</td><td>AED 6,344</td><td>AED 2,436,224</td></tr>
        <tr><td>1-Bed Furnished (+41.5%)</td><td>AED 107,724</td><td>AED 8,977</td><td>AED 3,447,168</td></tr>
        <tr class="highlight"><td>TOTAL (Unfurnished)</td><td></td><td></td><td>AED 4,075,880</td></tr>
        <tr class="highlight"><td>TOTAL (Furnished)</td><td></td><td></td><td>AED 6,288,168</td></tr>
    </table>

    <h3>Optimal Pricing for Target Occupancy</h3>
    <table>
        <tr><th>Unit Type</th><th>90% Occ Price/yr</th><th>90% Occ Monthly</th><th>80% Occ Price/yr</th><th>80% Occ Monthly</th></tr>
        <tr><td>Studio Unfurnished</td><td>AED 40,000</td><td>AED 3,333</td><td>AED 53,000</td><td>AED 4,417</td></tr>
        <tr><td>Studio Furnished</td><td>AED 69,320</td><td>AED 5,777</td><td>AED 91,849</td><td>AED 7,654</td></tr>
        <tr><td>1-Bed Unfurnished</td><td>AED 60,000</td><td>AED 5,000</td><td>AED 70,000</td><td>AED 5,833</td></tr>
        <tr><td>1-Bed Furnished</td><td>AED 84,900</td><td>AED 7,075</td><td>AED 99,050</td><td>AED 8,254</td></tr>
    </table>

    <h3>Demand Curves & Revenue Optimization</h3>
    {embed_img('22_demand_curves.png', 'Demand Curves')}

    <div class="insight">The revenue-maximizing sweet spot is at 72-76% occupancy. Pushing for higher occupancy (90%) requires significant price cuts that reduce total revenue. The optimal balance is around 75% occupancy.</div>

    <h3>Revenue Maximization Sweet Spots</h3>
    <table>
        <tr><th>Unit Type</th><th>Optimal Price</th><th>Occupancy</th><th>Total Revenue/Year</th></tr>
        <tr class="highlight"><td>Studio Unfurnished</td><td>AED 60,000/yr</td><td>72%</td><td>AED 1,036,800</td></tr>
        <tr class="highlight"><td>Studio Furnished</td><td>AED 100,000/yr</td><td>75%</td><td>AED 1,794,142</td></tr>
        <tr class="highlight"><td>1-Bed Unfurnished</td><td>AED 75,000/yr</td><td>75%</td><td>AED 1,800,000</td></tr>
        <tr class="highlight"><td>1-Bed Furnished</td><td>AED 105,000/yr</td><td>76%</td><td>AED 2,546,714</td></tr>
    </table>

    {embed_img('13_revenue_optimization.png', 'Revenue Optimization')}
    {embed_img('19_building_summary.png', 'Building Summary')}
</div>

<!-- SECTION 8: FURNISHED VS UNFURNISHED -->
<div class="section" id="furnished">
    <h2>8. Furnished vs Unfurnished ROI</h2>

    <h3>Furnishing Investment</h3>
    <table>
        <tr><th>Item</th><th>Cost</th></tr>
        <tr><td>Studio furnishing (x24 @ AED 25,000)</td><td>AED 600,000</td></tr>
        <tr><td>1-Bed furnishing (x32 @ AED 40,000)</td><td>AED 1,280,000</td></tr>
        <tr class="highlight"><td>Total Investment</td><td>AED 1,880,000</td></tr>
        <tr><td>Annual amortization (4yr cycle)</td><td>AED 470,000/yr</td></tr>
    </table>

    <h3>Net Revenue Comparison</h3>
    <table>
        <tr><th>Metric</th><th>Unfurnished</th><th>Furnished</th><th>Difference</th></tr>
        <tr><td colspan="4" style="background:#1565C0;color:white;font-weight:bold;">At 80% Occupancy</td></tr>
        <tr><td>Net Revenue/Year</td><td>AED 2,757,000</td><td>AED 3,751,381</td><td style="color:green;font-weight:bold;">+AED 994,381</td></tr>
        <tr><td>Net Revenue/Month</td><td>AED 229,750</td><td>AED 312,615</td><td style="color:green;font-weight:bold;">+AED 82,865</td></tr>
        <tr><td>Year 1 ROI</td><td></td><td></td><td style="color:green;font-weight:bold;">77.9%</td></tr>
        <tr><td colspan="4" style="background:#1565C0;color:white;font-weight:bold;">At 90% Occupancy</td></tr>
        <tr><td>Net Revenue/Year</td><td>AED 2,520,000</td><td>AED 3,362,920</td><td style="color:green;font-weight:bold;">+AED 842,920</td></tr>
        <tr><td>Net Revenue/Month</td><td>AED 210,000</td><td>AED 280,243</td><td style="color:green;font-weight:bold;">+AED 70,243</td></tr>
        <tr><td>Year 1 ROI</td><td></td><td></td><td style="color:green;font-weight:bold;">69.8%</td></tr>
    </table>

    {embed_img('21_furnished_roi.png', 'Furnished ROI')}

    <div class="recommendation">
        <h3>Verdict: Furnished is clearly worth the investment</h3>
        <p>The AED 1.88M furnishing investment pays back within <strong>1.9-2.2 years</strong> and delivers an additional <strong>AED 843K-994K per year</strong> in net revenue. Over a 5-year period, the cumulative benefit is <strong>AED 3-4 million</strong>.</p>
    </div>
</div>

<!-- SECTION 9: HOLIDAY HOME -->
<div class="section" id="holiday">
    <h2>9. Holiday Home / Airbnb Analysis</h2>

    <h3>Seasonal Occupancy & Nightly Rates</h3>
    <table>
        <tr><th>Month</th><th>Season</th><th>Occupancy</th><th>Studio Rate</th><th>1-Bed Rate</th></tr>
        <tr style="background:#E8F5E9"><td>January</td><td>Peak</td><td>82%</td><td>AED 450</td><td>AED 600</td></tr>
        <tr style="background:#E8F5E9"><td>February</td><td>Peak</td><td>85%</td><td>AED 450</td><td>AED 600</td></tr>
        <tr style="background:#E8F5E9"><td>March</td><td>Peak</td><td>78%</td><td>AED 450</td><td>AED 600</td></tr>
        <tr style="background:#FFF3E0"><td>April</td><td>Shoulder</td><td>68%</td><td>AED 350</td><td>AED 480</td></tr>
        <tr style="background:#FFEBEE"><td>May</td><td>Low</td><td>45%</td><td>AED 250</td><td>AED 350</td></tr>
        <tr style="background:#FFEBEE"><td>June</td><td>Low</td><td>35%</td><td>AED 250</td><td>AED 350</td></tr>
        <tr style="background:#FFEBEE"><td>July</td><td>Low</td><td>38%</td><td>AED 250</td><td>AED 350</td></tr>
        <tr style="background:#FFEBEE"><td>August</td><td>Low</td><td>40%</td><td>AED 250</td><td>AED 350</td></tr>
        <tr style="background:#FFF3E0"><td>September</td><td>Shoulder</td><td>48%</td><td>AED 350</td><td>AED 480</td></tr>
        <tr style="background:#E8F5E9"><td>October</td><td>Peak</td><td>72%</td><td>AED 450</td><td>AED 600</td></tr>
        <tr style="background:#E8F5E9"><td>November</td><td>Peak</td><td>80%</td><td>AED 450</td><td>AED 600</td></tr>
        <tr style="background:#E8F5E9"><td>December</td><td>Peak</td><td>88%</td><td>AED 450</td><td>AED 600</td></tr>
    </table>

    {embed_img('20_holiday_seasonal.png', 'Holiday Seasonal Revenue')}
    {embed_img('12_holiday_home_monthly.png', 'Holiday Home Monthly')}

    <h3>Holiday Home Operating Costs (All 56 Units)</h3>
    <table>
        <tr><th>Cost Item</th><th>Amount</th></tr>
        <tr><td>Gross Revenue</td><td style="color:green;font-weight:bold;">AED 6,073,284</td></tr>
        <tr><td>Management fee (20%)</td><td>-AED 1,214,657</td></tr>
        <tr><td>Cleaning/turnovers (3,226 turnovers)</td><td>-AED 576,075</td></tr>
        <tr><td>Utilities</td><td>-AED 336,000</td></tr>
        <tr><td>DTCM Licensing</td><td>-AED 85,120</td></tr>
        <tr><td>Insurance</td><td>-AED 112,000</td></tr>
        <tr><td>Furniture replacement (3yr cycle)</td><td>-AED 626,667</td></tr>
        <tr style="border-top:3px solid #333"><td><strong>Total Costs</strong></td><td><strong>-AED 2,950,518</strong></td></tr>
        <tr class="highlight"><td><strong>NET Revenue</strong></td><td><strong>AED 3,122,766 (AED 260K/month)</strong></td></tr>
    </table>

    <div class="warning">
        <strong>Warning:</strong> While holiday homes generate the highest gross (AED 6.07M), operating costs consume 49% of revenue. Summer months (May-Aug) see occupancy drop to 35-45%, creating cash flow volatility.
    </div>
</div>

<!-- SECTION 10: STRATEGY -->
<div class="section" id="strategy">
    <h2>10. Strategy Comparison & Final Recommendation</h2>

    <table>
        <tr><th>Strategy</th><th>Gross Rev/yr</th><th>Costs/yr</th><th>Net Rev/yr</th><th>Net Rev/mo</th></tr>
        <tr><td>A: All Long-Term Unfurnished (90%)</td><td>AED 2,520,000</td><td>AED 0</td><td>AED 2,520,000</td><td>AED 210,000</td></tr>
        <tr><td>B: All Long-Term Furnished (90%)</td><td>AED 3,832,920</td><td>AED 470,000</td><td>AED 3,362,920</td><td>AED 280,243</td></tr>
        <tr><td>C: All Holiday Homes (56 units)</td><td>AED 6,073,284</td><td>AED 2,950,518</td><td>AED 3,122,766</td><td>AED 260,230</td></tr>
        <tr class="highlight"><td>D: Hybrid Light (5S+5B holiday)</td><td>AED 4,278,100</td><td>AED 905,508</td><td>AED 3,372,592</td><td>AED 281,049</td></tr>
        <tr><td>E: Hybrid Medium (8S+8B holiday)</td><td>AED 4,452,676</td><td>AED 1,166,814</td><td>AED 3,285,862</td><td>AED 273,822</td></tr>
        <tr><td>F: Hybrid Heavy (10S+10B holiday)</td><td>AED 4,569,060</td><td>AED 1,341,017</td><td>AED 3,228,043</td><td>AED 269,004</td></tr>
        <tr><td>G: Hybrid Optimized (5S+10B holiday)</td><td>AED 4,463,222</td><td>AED 1,149,307</td><td>AED 3,313,915</td><td>AED 276,160</td></tr>
    </table>

    {embed_img('11_strategy_comparison.png', 'Strategy Comparison')}
    {embed_img('14_all_strategies_comparison.png', 'All Strategies')}

    <div class="recommendation">
        <h3>RECOMMENDED: Strategy D - Hybrid Light</h3>
        <p style="font-size:1.1em; margin-bottom:15px;">
            <strong>19 Studios + 27 One-Beds as Long-Term Furnished</strong><br>
            <strong>5 Studios + 5 One-Beds as Holiday Homes</strong>
        </p>
        <table style="background:white; border-radius:8px;">
            <tr><th>Revenue Component</th><th>Amount</th></tr>
            <tr><td>Long-term rental income</td><td>AED 3,216,040</td></tr>
            <tr><td>Holiday home income</td><td>AED 1,062,060</td></tr>
            <tr><td>Total gross</td><td>AED 4,278,100</td></tr>
            <tr><td>Total costs</td><td>-AED 905,508</td></tr>
            <tr class="highlight"><td><strong>NET ANNUAL REVENUE</strong></td><td><strong>AED 3,372,592</strong></td></tr>
            <tr class="highlight"><td><strong>NET MONTHLY REVENUE</strong></td><td><strong>AED 281,049</strong></td></tr>
        </table>
        <p style="margin-top:15px;"><strong>+33.8% uplift</strong> vs all-unfurnished baseline (AED +852,592/yr additional revenue)</p>
    </div>

    {embed_img('15_hybrid_breakdown.png', 'Hybrid Breakdown')}

    <h3>Why This Strategy Wins</h3>
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:15px; margin-top:15px;">
        <div class="insight">
            <strong>1. Highest net revenue</strong> - AED 3.37M beats both pure long-term (AED 3.36M) and pure holiday home (AED 3.12M)
        </div>
        <div class="insight">
            <strong>2. Diversified income</strong> - 75% stable long-term + 25% variable short-term reduces risk
        </div>
        <div class="insight">
            <strong>3. Manageable complexity</strong> - Only 10 units need holiday home management vs 56 in all-HH strategy
        </div>
        <div class="insight">
            <strong>4. Summer protection</strong> - 46 long-term units provide steady income during May-Aug low season
        </div>
        <div class="insight">
            <strong>5. Lower costs</strong> - AED 906K vs AED 2.95M for all holiday homes; costs are only 21% of gross
        </div>
        <div class="insight">
            <strong>6. Upside optionality</strong> - Can convert more units to holiday homes during peak if demand justifies
        </div>
    </div>
</div>

</div> <!-- container -->

<div class="footer">
    <p>Al Satwa Rental Market Analysis & Building Projections Report</p>
    <p>Generated March 12, 2026 | Based on 6,414 rental contracts | Al Satwa, Dubai</p>
    <p>Data Source: Al Satwa Market Data (Eva Real Estate LLC)</p>
</div>

</body>
</html>
"""

with open('report/AL_SATWA_REPORT.html', 'w') as f:
    f.write(html)

print(f"\nHTML report generated: report/AL_SATWA_REPORT.html")
print(f"File size: {os.path.getsize('report/AL_SATWA_REPORT.html') / 1024 / 1024:.1f} MB")
print("All images embedded as base64 - report is fully self-contained.")
