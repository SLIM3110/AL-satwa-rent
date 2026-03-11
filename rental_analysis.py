#!/usr/bin/env python3
"""
Al Satwa Rental Market Analysis
Analyzes 1-bedroom and studio rental data from Al Satwa, Dubai
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# ── Configuration ──
CSV_FILE = 'al-satwa-market-data-mhaegan-aclan-eva-real-estate-llc-11-03-2026-e48bd6c4cce45cc9c132ad7cbc904b9023f19a57.csv'
OUTPUT_DIR = 'report'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load Data ──
df = pd.read_csv(CSV_FILE, encoding='latin-1')
df['start_date'] = pd.to_datetime(df['start_date'], errors='coerce')
df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')
df['annualised_rental_price'] = pd.to_numeric(df['annualised_rental_price'], errors='coerce')
df['rent_price_sqft_unit'] = pd.to_numeric(df['rent_price_sqft_unit'], errors='coerce')
df['unit_size'] = pd.to_numeric(df['unit_size'], errors='coerce')

# Studio is coded as 's' in beds column
df['bed_type'] = df['beds'].astype(str).str.strip()

# Filter for 1-bedroom and studio only
studio = df[df['bed_type'] == 's'].copy()
one_bed = df[df['bed_type'] == '1'].copy()
filtered = pd.concat([studio, one_bed])
filtered['bed_label'] = filtered['bed_type'].map({'s': 'Studio', '1': '1 Bedroom'})

print(f"Total records: {len(df)}")
print(f"Studio records: {len(studio)}")
print(f"1 Bedroom records: {len(one_bed)}")
print(f"Combined (filtered): {len(filtered)}")
print()

# ══════════════════════════════════════════════════════════════════════
# SECTION 1: Price Statistics (Highest, Lowest, Average, When)
# ══════════════════════════════════════════════════════════════════════

def price_stats(data, label):
    prices = data['annualised_rental_price'].dropna()
    if len(prices) == 0:
        return None

    idx_max = data['annualised_rental_price'].idxmax()
    idx_min = data['annualised_rental_price'].idxmin()
    row_max = data.loc[idx_max]
    row_min = data.loc[idx_min]

    stats = {
        'label': label,
        'count': len(prices),
        'highest': prices.max(),
        'highest_date': row_max['start_date'],
        'highest_location': f"{row_max['sub_loc_1']} / {row_max['sub_loc_2']}".strip(' /'),
        'highest_sequence': row_max['rent_sequence'],
        'lowest': prices.min(),
        'lowest_date': row_min['start_date'],
        'lowest_location': f"{row_min['sub_loc_1']} / {row_min['sub_loc_2']}".strip(' /'),
        'lowest_sequence': row_min['rent_sequence'],
        'average': prices.mean(),
        'median': prices.median(),
        'std': prices.std(),
    }
    return stats

stats_studio = price_stats(studio, 'Studio')
stats_1bed = price_stats(one_bed, '1 Bedroom')
stats_all = price_stats(filtered, 'Studio + 1 Bedroom Combined')

for s in [stats_studio, stats_1bed, stats_all]:
    if s:
        print(f"── {s['label']} ({s['count']} contracts) ──")
        print(f"  Highest Rent: AED {s['highest']:,.0f} on {s['highest_date'].strftime('%Y-%m-%d') if pd.notna(s['highest_date']) else 'N/A'} at {s['highest_location']} ({s['highest_sequence']})")
        print(f"  Lowest Rent:  AED {s['lowest']:,.0f} on {s['lowest_date'].strftime('%Y-%m-%d') if pd.notna(s['lowest_date']) else 'N/A'} at {s['lowest_location']} ({s['lowest_sequence']})")
        print(f"  Average:      AED {s['average']:,.0f}")
        print(f"  Median:       AED {s['median']:,.0f}")
        print(f"  Std Dev:      AED {s['std']:,.0f}")
        print()

# ══════════════════════════════════════════════════════════════════════
# SECTION 2: Most Common Price in 5,000 AED Increments
# ══════════════════════════════════════════════════════════════════════

def price_bucket_analysis(data, label):
    prices = data['annualised_rental_price'].dropna()
    # Create 5000-increment buckets
    buckets = (prices // 5000) * 5000
    bucket_counts = buckets.value_counts().sort_index()
    most_common_bucket = bucket_counts.idxmax()
    most_common_count = bucket_counts.max()

    print(f"── {label}: Price Distribution (AED 5,000 increments) ──")
    print(f"  Most common range: AED {most_common_bucket:,.0f} - {most_common_bucket + 5000:,.0f} ({most_common_count} contracts)")
    print(f"  Full distribution:")
    for bucket, count in bucket_counts.items():
        pct = count / len(prices) * 100
        bar = '█' * int(pct)
        print(f"    AED {bucket:>8,.0f} - {bucket+5000:>8,.0f}: {count:>4} ({pct:5.1f}%) {bar}")
    print()
    return bucket_counts

bucket_studio = price_bucket_analysis(studio, 'Studio')
bucket_1bed = price_bucket_analysis(one_bed, '1 Bedroom')

# ══════════════════════════════════════════════════════════════════════
# SECTION 3: Rent per Square Foot Analysis
# ══════════════════════════════════════════════════════════════════════

print("── Rent per Square Foot Analysis ──")
for label, data in [('Studio', studio), ('1 Bedroom', one_bed)]:
    sqft = data['rent_price_sqft_unit'].dropna()
    if len(sqft) > 0:
        print(f"  {label}:")
        print(f"    Average: AED {sqft.mean():.0f}/sqft")
        print(f"    Median:  AED {sqft.median():.0f}/sqft")
        print(f"    Min:     AED {sqft.min():.0f}/sqft")
        print(f"    Max:     AED {sqft.max():.0f}/sqft")
        print(f"    Avg Unit Size: {data['unit_size'].dropna().mean():.0f} sqft")
print()

# ══════════════════════════════════════════════════════════════════════
# SECTION 4: Communities (sub_loc_1) with Highest Rents
# ══════════════════════════════════════════════════════════════════════

print("── Top Communities/Sub-locations by Average Rent ──")
for label, data in [('Studio', studio), ('1 Bedroom', one_bed)]:
    community = data.groupby('sub_loc_1').agg(
        avg_rent=('annualised_rental_price', 'mean'),
        max_rent=('annualised_rental_price', 'max'),
        min_rent=('annualised_rental_price', 'min'),
        count=('annualised_rental_price', 'count'),
        avg_sqft=('rent_price_sqft_unit', 'mean'),
        avg_size=('unit_size', 'mean')
    ).sort_values('avg_rent', ascending=False)

    print(f"\n  {label} - All Communities:")
    for idx, row in community.iterrows():
        print(f"    {idx}: Avg AED {row['avg_rent']:,.0f} | Max AED {row['max_rent']:,.0f} | Min AED {row['min_rent']:,.0f} | {int(row['count'])} contracts | Avg {row['avg_sqft']:.0f}/sqft | Size {row['avg_size']:.0f}sqft")
print()

# ══════════════════════════════════════════════════════════════════════
# SECTION 5: Comments with Highest Rental Amounts
# ══════════════════════════════════════════════════════════════════════

print("── Comments Associated with Highest Rental Amounts ──")
for label, data in [('Studio', studio), ('1 Bedroom', one_bed)]:
    comments_data = data[data['comments'].notna() & (data['comments'].str.strip() != '')]
    if len(comments_data) > 0:
        top_by_rent = comments_data.nlargest(10, 'annualised_rental_price')[['annualised_rental_price', 'comments', 'sub_loc_1', 'start_date']]
        print(f"\n  {label} - Top 10 Highest Rent with Comments:")
        for _, row in top_by_rent.iterrows():
            print(f"    AED {row['annualised_rental_price']:,.0f} | {row['sub_loc_1']} | {row['start_date'].strftime('%Y-%m-%d') if pd.notna(row['start_date']) else 'N/A'}")
            print(f"      Comment: {row['comments'][:100]}")

# Also: Most common comments grouped with avg rent
print("\n── Most Common Comments & Their Average Rents ──")
for label, data in [('Studio', studio), ('1 Bedroom', one_bed)]:
    comments_data = data[data['comments'].notna() & (data['comments'].str.strip() != '')]
    if len(comments_data) > 0:
        comment_stats = comments_data.groupby('comments').agg(
            count=('annualised_rental_price', 'count'),
            avg_rent=('annualised_rental_price', 'mean'),
            max_rent=('annualised_rental_price', 'max')
        ).sort_values('avg_rent', ascending=False).head(15)
        print(f"\n  {label} - Top 15 Comments by Average Rent:")
        for idx, row in comment_stats.iterrows():
            print(f"    [{int(row['count'])}x] Avg AED {row['avg_rent']:,.0f} | Max AED {row['max_rent']:,.0f} | {idx[:80]}")
print()

# ══════════════════════════════════════════════════════════════════════
# SECTION 6: Occupancy Rate Analysis
# ══════════════════════════════════════════════════════════════════════

print("══ OCCUPANCY RATE ANALYSIS ══")
print()

# Analyze New vs Renewal contracts as proxy for occupancy
print("── Contract Type Distribution (Occupancy Proxy) ──")
for label, data in [('Studio', studio), ('1 Bedroom', one_bed), ('All Types', df)]:
    seq_counts = data['rent_sequence'].value_counts()
    total = len(data)
    renewals = seq_counts.get('Renewal', 0)
    new_contracts = seq_counts.get('New', 0)
    renewal_rate = renewals / total * 100 if total > 0 else 0
    new_rate = new_contracts / total * 100 if total > 0 else 0

    print(f"  {label} ({total} total contracts):")
    print(f"    Renewals:      {renewals} ({renewal_rate:.1f}%) - indicates tenant retention/occupancy")
    print(f"    New Contracts:  {new_contracts} ({new_rate:.1f}%) - indicates new tenants/turnover")
    for k, v in seq_counts.items():
        if k not in ('Renewal', 'New'):
            print(f"    {k}: {v} ({v/total*100:.1f}%)")

    # Estimated occupancy: renewals suggest units remain occupied
    # High renewal rate = high occupancy
    estimated_occupancy = renewal_rate  # Renewal rate as occupancy proxy
    print(f"    ➤ Estimated Occupancy Rate (based on renewals): {estimated_occupancy:.1f}%")
    print()

# Monthly contract volume analysis
print("── Monthly Contract Volume (Occupancy Trend Indicator) ──")
filtered['year_month'] = filtered['start_date'].dt.to_period('M')
monthly = filtered.groupby(['year_month', 'bed_label']).size().unstack(fill_value=0)
print(monthly.to_string())
print()

# Airbnb / Furnished / Short-term proxy analysis
print("══ AIRBNB / SHORT-TERM RENTAL OCCUPANCY ANALYSIS ══")
print()

# Hotel Apartments as Airbnb proxy
hotel_apts = df[df['unit_type'] == 'Hotel Apartment']
furnished = df[df['furnished'].notna() & (df['furnished'].str.strip() != '')]

print(f"── Hotel Apartments (Airbnb/Short-term proxy) ──")
print(f"  Total hotel apartment contracts: {len(hotel_apts)}")
if len(hotel_apts) > 0:
    print(f"  Average Annual Rent: AED {hotel_apts['annualised_rental_price'].mean():,.0f}")
    print(f"  Beds distribution: {hotel_apts['beds'].value_counts().to_dict()}")
    seq = hotel_apts['rent_sequence'].value_counts()
    if len(seq) > 0:
        renewal_pct = seq.get('Renewal', 0) / len(hotel_apts) * 100
        print(f"  Renewal Rate: {renewal_pct:.1f}% (higher = more stable/occupied)")
    print()

print(f"── Furnished Units (Higher Airbnb Potential) ──")
print(f"  Total furnished contracts: {len(furnished)}")
if len(furnished) > 0:
    print(f"  Furnished types: {furnished['furnished'].value_counts().to_dict()}")
    print(f"  Average Annual Rent: AED {furnished['annualised_rental_price'].mean():,.0f}")
    print()

# Short-term indicators from comments
short_term_keywords = ['furnished', 'all bills', 'included', 'monthly', 'flexible']
for label, data in [('Studio', studio), ('1 Bedroom', one_bed)]:
    comments_data = data[data['comments'].notna()]
    short_term = comments_data[comments_data['comments'].str.lower().str.contains('|'.join(short_term_keywords), na=False)]
    total = len(data)
    print(f"  {label} - Short-term/Furnished indicators in comments: {len(short_term)} of {total} ({len(short_term)/total*100:.1f}%)")
    if len(short_term) > 0:
        print(f"    Avg rent for these: AED {short_term['annualised_rental_price'].mean():,.0f} vs overall AED {data['annualised_rental_price'].mean():,.0f}")

# Contract duration analysis
print("\n── Contract Duration Analysis ──")
filtered['duration_days'] = (filtered['end_date'] - filtered['start_date']).dt.days
duration = filtered['duration_days'].dropna()
print(f"  Average contract duration: {duration.mean():.0f} days ({duration.mean()/30:.1f} months)")
print(f"  Median contract duration: {duration.median():.0f} days")
short = (duration < 180).sum()
medium = ((duration >= 180) & (duration <= 366)).sum()
long_term = (duration > 366).sum()
total_dur = len(duration)
print(f"  Short-term (<6 months): {short} ({short/total_dur*100:.1f}%)")
print(f"  Standard (6-12 months): {medium} ({medium/total_dur*100:.1f}%)")
print(f"  Long-term (>12 months): {long_term} ({long_term/total_dur*100:.1f}%)")
print()

# ══════════════════════════════════════════════════════════════════════
# SECTION 7: VISUALIZATIONS
# ══════════════════════════════════════════════════════════════════════

plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {'Studio': '#2196F3', '1 Bedroom': '#FF9800'}

# ── Fig 1: Price Distribution Histogram ──
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for ax, (label, data, color) in zip(axes, [('Studio', studio, COLORS['Studio']), ('1 Bedroom', one_bed, COLORS['1 Bedroom'])]):
    prices = data['annualised_rental_price'].dropna()
    bins = np.arange(0, prices.max() + 10000, 5000)
    ax.hist(prices, bins=bins, color=color, edgecolor='white', alpha=0.85)
    ax.axvline(prices.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: AED {prices.mean():,.0f}')
    ax.axvline(prices.median(), color='green', linestyle='--', linewidth=2, label=f'Median: AED {prices.median():,.0f}')
    ax.set_title(f'{label} - Annual Rent Distribution (AED 5,000 buckets)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Annual Rent (AED)')
    ax.set_ylabel('Number of Contracts')
    ax.legend(fontsize=10)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1000:.0f}K'))
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/01_price_distribution.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 2: Box Plot Comparison ──
fig, ax = plt.subplots(figsize=(10, 6))
box_data = [studio['annualised_rental_price'].dropna(), one_bed['annualised_rental_price'].dropna()]
bp = ax.boxplot(box_data, labels=['Studio', '1 Bedroom'], patch_artist=True, widths=0.6)
bp['boxes'][0].set_facecolor(COLORS['Studio'])
bp['boxes'][1].set_facecolor(COLORS['1 Bedroom'])
for box in bp['boxes']:
    box.set_alpha(0.7)
ax.set_ylabel('Annual Rent (AED)')
ax.set_title('Studio vs 1 Bedroom - Rent Comparison', fontsize=14, fontweight='bold')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/02_boxplot_comparison.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 3: Top Communities by Average Rent ──
fig, axes = plt.subplots(1, 2, figsize=(18, 8))
for ax, (label, data, color) in zip(axes, [('Studio', studio, COLORS['Studio']), ('1 Bedroom', one_bed, COLORS['1 Bedroom'])]):
    comm = data.groupby('sub_loc_1')['annualised_rental_price'].agg(['mean', 'count']).sort_values('mean', ascending=True)
    comm = comm[comm['count'] >= 2]  # At least 2 contracts
    comm_top = comm.tail(15)
    bars = ax.barh(range(len(comm_top)), comm_top['mean'], color=color, alpha=0.85, edgecolor='white')
    ax.set_yticks(range(len(comm_top)))
    ax.set_yticklabels([f"{n} ({int(c)})" for n, c in zip(comm_top.index, comm_top['count'])], fontsize=9)
    ax.set_xlabel('Average Annual Rent (AED)')
    ax.set_title(f'{label} - Top Communities by Avg Rent', fontsize=13, fontweight='bold')
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    for bar, val in zip(bars, comm_top['mean']):
        ax.text(val + 500, bar.get_y() + bar.get_height()/2, f'AED {val:,.0f}', va='center', fontsize=8)
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/03_top_communities.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 4: Rent per Square Foot ──
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for ax, (label, data, color) in zip(axes, [('Studio', studio, COLORS['Studio']), ('1 Bedroom', one_bed, COLORS['1 Bedroom'])]):
    sqft = data['rent_price_sqft_unit'].dropna()
    ax.hist(sqft, bins=30, color=color, edgecolor='white', alpha=0.85)
    ax.axvline(sqft.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: AED {sqft.mean():.0f}/sqft')
    ax.set_title(f'{label} - Rent per Sqft Distribution', fontsize=13, fontweight='bold')
    ax.set_xlabel('Rent per Sqft (AED)')
    ax.set_ylabel('Number of Contracts')
    ax.legend()
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/04_rent_per_sqft.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 5: Occupancy / New vs Renewal ──
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
for ax, (label, data) in zip(axes, [('Studio', studio), ('1 Bedroom', one_bed), ('All Types', df)]):
    seq = data['rent_sequence'].value_counts()
    colors_pie = ['#4CAF50', '#FF5722', '#9C27B0', '#607D8B']
    wedges, texts, autotexts = ax.pie(seq.values, labels=seq.index, autopct='%1.1f%%',
                                       colors=colors_pie[:len(seq)], startangle=90)
    ax.set_title(f'{label}\n({len(data)} contracts)', fontsize=12, fontweight='bold')
fig.suptitle('Contract Type Distribution (Occupancy Indicator)', fontsize=14, fontweight='bold', y=1.02)
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/05_occupancy_new_vs_renewal.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 6: Monthly Contract Volume Timeline ──
fig, ax = plt.subplots(figsize=(16, 6))
for label, data, color in [('Studio', studio, COLORS['Studio']), ('1 Bedroom', one_bed, COLORS['1 Bedroom'])]:
    monthly_data = data.set_index('start_date').resample('ME').size()
    if len(monthly_data) > 0:
        ax.plot(monthly_data.index, monthly_data.values, color=color, linewidth=2, marker='o', markersize=4, label=label)
ax.set_title('Monthly Contract Volume Over Time', fontsize=14, fontweight='bold')
ax.set_xlabel('Date')
ax.set_ylabel('Number of Contracts')
ax.legend()
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/06_monthly_volume.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 7: Contract Duration Distribution ──
fig, ax = plt.subplots(figsize=(12, 6))
for label, data, color in [('Studio', studio, COLORS['Studio']), ('1 Bedroom', one_bed, COLORS['1 Bedroom'])]:
    dur = (data['end_date'] - data['start_date']).dt.days.dropna()
    ax.hist(dur, bins=30, color=color, alpha=0.6, edgecolor='white', label=label)
ax.set_title('Contract Duration Distribution', fontsize=14, fontweight='bold')
ax.set_xlabel('Duration (Days)')
ax.set_ylabel('Number of Contracts')
ax.axvline(365, color='red', linestyle='--', label='1 Year', linewidth=2)
ax.legend()
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/07_contract_duration.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 8: Price Heatmap by Community and Type ──
fig, ax = plt.subplots(figsize=(14, 8))
pivot = filtered.groupby(['sub_loc_1', 'bed_label'])['annualised_rental_price'].mean().unstack(fill_value=0)
pivot = pivot.sort_values(pivot.columns[0] if len(pivot.columns) > 0 else pivot.index[0], ascending=True).tail(20)
pivot.plot(kind='barh', ax=ax, color=[COLORS.get(c, '#999') for c in pivot.columns], alpha=0.85)
ax.set_title('Average Rent by Community & Type (Top 20)', fontsize=14, fontweight='bold')
ax.set_xlabel('Average Annual Rent (AED)')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
ax.legend(title='Type')
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/08_community_comparison.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 9: Comments with Highest Rents ──
fig, axes = plt.subplots(2, 1, figsize=(16, 14))
for ax, (label, data) in zip(axes, [('Studio', studio), ('1 Bedroom', one_bed)]):
    comments_data = data[data['comments'].notna() & (data['comments'].str.strip() != '')]
    if len(comments_data) > 0:
        top_comments = comments_data.groupby('comments')['annualised_rental_price'].agg(['mean', 'max', 'count']).sort_values('mean', ascending=True)
        top_comments = top_comments[top_comments['count'] >= 2].tail(12)
        short_labels = [c[:60] + '...' if len(c) > 60 else c for c in top_comments.index]
        ax.barh(range(len(top_comments)), top_comments['mean'], color=COLORS[label], alpha=0.7, label='Avg Rent')
        ax.barh(range(len(top_comments)), top_comments['max'], color=COLORS[label], alpha=0.3, label='Max Rent')
        ax.set_yticks(range(len(top_comments)))
        ax.set_yticklabels(short_labels, fontsize=8)
        ax.set_xlabel('Annual Rent (AED)')
        ax.set_title(f'{label} - Top Comments by Average Rent (min 2 contracts)', fontsize=12, fontweight='bold')
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        ax.legend()
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/09_comments_highest_rents.png', dpi=150, bbox_inches='tight')
plt.close()

# ── Fig 10: Airbnb / Short-term Indicators ──
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: Short-term vs long-term
ax = axes[0]
for label, data, color in [('Studio', studio, COLORS['Studio']), ('1 Bedroom', one_bed, COLORS['1 Bedroom'])]:
    dur = (data['end_date'] - data['start_date']).dt.days.dropna()
    categories = ['<6 months', '6-12 months', '>12 months']
    counts = [(dur < 180).sum(), ((dur >= 180) & (dur <= 366)).sum(), (dur > 366).sum()]
    x = np.arange(len(categories))
    width = 0.35
    offset = -0.175 if label == 'Studio' else 0.175
    ax.bar(x + offset, counts, width, label=label, color=color, alpha=0.85)
ax.set_xticks(np.arange(len(categories)))
ax.set_xticklabels(categories)
ax.set_ylabel('Number of Contracts')
ax.set_title('Contract Duration Categories\n(Short-term = Higher Airbnb Potential)', fontsize=12, fontweight='bold')
ax.legend()

# Right: Furnished/All-bills indicators
ax = axes[1]
short_term_keywords = ['furnished', 'all bills', 'included']
labels_bar = []
values_bar = []
colors_bar = []
for label, data, color in [('Studio', studio, COLORS['Studio']), ('1 Bedroom', one_bed, COLORS['1 Bedroom'])]:
    comments_data = data[data['comments'].notna()]
    st = comments_data[comments_data['comments'].str.lower().str.contains('|'.join(short_term_keywords), na=False)]
    labels_bar.extend([f'{label}\nShort-term\nIndicators', f'{label}\nRegular'])
    values_bar.extend([len(st), len(data) - len(st)])
    colors_bar.extend([color, color])
alphas = [0.9, 0.4, 0.9, 0.4]
for i in range(len(labels_bar)):
    ax.bar(i, values_bar[i], color=colors_bar[i], alpha=alphas[i], edgecolor='white')
ax.set_xticks(range(len(labels_bar)))
ax.set_xticklabels(labels_bar, fontsize=9)
ax.set_ylabel('Number of Contracts')
ax.set_title('Furnished/All-Bills-Included Listings\n(Airbnb-style Indicators)', fontsize=12, fontweight='bold')
fig.tight_layout()
fig.savefig(f'{OUTPUT_DIR}/10_airbnb_indicators.png', dpi=150, bbox_inches='tight')
plt.close()

print(f"\n✓ All 10 charts saved to '{OUTPUT_DIR}/' directory")
print("\nDone! Report generation complete.")
