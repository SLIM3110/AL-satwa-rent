#!/usr/bin/env python3
"""
Generate a comprehensive Word (.docx) report for Al Satwa rental analysis
and building projections with embedded charts and formatted tables.
"""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import os

OUTPUT_DIR = 'report'
doc = Document()

# ══════════════════════════════════════════════════════════════════════
# STYLES
# ══════════════════════════════════════════════════════════════════════

style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)
style.paragraph_format.space_after = Pt(6)
style.paragraph_format.line_spacing = 1.15

for level in range(1, 4):
    heading_style = doc.styles[f'Heading {level}']
    heading_style.font.name = 'Calibri'
    heading_style.font.color.rgb = RGBColor(21, 101, 192)

def set_cell_shading(cell, color_hex):
    """Set background color of a table cell."""
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)

def add_table(doc, headers, rows, col_widths=None, highlight_rows=None):
    """Add a formatted table to the document."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(10)
        set_cell_shading(cell, '1565C0')

    # Data rows
    for r, row_data in enumerate(rows):
        for c, value in enumerate(row_data):
            cell = table.rows[r + 1].cells[c]
            cell.text = str(value)
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(10)
            if highlight_rows and r in highlight_rows:
                set_cell_shading(cell, 'E8F5E9')
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True

    if col_widths:
        for i, width in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Cm(width)

    doc.add_paragraph()
    return table

def add_image(doc, filename, width=6.2):
    """Add an image centered in the document."""
    path = f'{OUTPUT_DIR}/{filename}'
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(path, width=Inches(width))
        doc.add_paragraph()

def add_insight(doc, text):
    """Add an insight/callout paragraph."""
    p = doc.add_paragraph()
    run = p.add_run('Key Insight: ')
    run.font.bold = True
    run.font.color.rgb = RGBColor(21, 101, 192)
    run.font.size = Pt(11)
    run = p.add_run(text)
    run.font.italic = True
    run.font.size = Pt(11)

def add_recommendation(doc, title, text):
    """Add a recommendation block."""
    p = doc.add_paragraph()
    run = p.add_run(f'RECOMMENDATION: {title}')
    run.font.bold = True
    run.font.color.rgb = RGBColor(46, 125, 50)
    run.font.size = Pt(13)
    p = doc.add_paragraph(text)

# ══════════════════════════════════════════════════════════════════════
# COVER PAGE
# ══════════════════════════════════════════════════════════════════════

# Add some spacing before title
for _ in range(6):
    doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('AL SATWA RENTAL MARKET')
run.font.size = Pt(32)
run.font.bold = True
run.font.color.rgb = RGBColor(21, 101, 192)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Analysis & Building Investment Projections')
run.font.size = Pt(20)
run.font.color.rgb = RGBColor(21, 101, 192)

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Comprehensive Market Study')
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(100, 100, 100)

doc.add_paragraph()

details = [
    'Date: March 12, 2026',
    'Data Source: 6,414 Rental Contracts | Al Satwa, Dubai',
    'Building Model: 24 Studios + 32 One-Bedrooms (56 Units)',
    'Prepared by: Eva Real Estate LLC / Market Analysis Division',
]
for d in details:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(d)
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(100, 100, 100)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ══════════════════════════════════════════════════════════════════════

doc.add_heading('Table of Contents', level=1)
toc_items = [
    '1. Executive Dashboard',
    '2. Market Analysis: Studio & 1-Bedroom Rents',
    '3. Price Distribution (AED 5,000 Increments)',
    '4. Rent per Square Foot Analysis',
    '5. Top Communities & Highest-Paying Comments',
    '6. Occupancy Rate Analysis',
    '7. Building Projections: Optimal Pricing',
    '8. Furnished vs Unfurnished ROI',
    '9. Holiday Home / Airbnb Analysis',
    '10. Strategy Comparison & Recommendation',
]
for item in toc_items:
    p = doc.add_paragraph(item)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Cm(1)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 1: EXECUTIVE DASHBOARD
# ══════════════════════════════════════════════════════════════════════

doc.add_heading('1. Executive Dashboard', level=1)

add_image(doc, '16_dashboard_kpis.png', 6.5)

add_table(doc,
    ['Metric', 'Value'],
    [
        ['Total Contracts Analyzed', '6,414'],
        ['Studio Contracts', '224 (3.5%)'],
        ['1-Bedroom Contracts', '2,883 (44.9%)'],
        ['Date Range', 'September 2025 - March 2026'],
        ['Studio Average Rent', 'AED 71,000 / year'],
        ['1-Bed Average Rent', 'AED 78,992 / year'],
        ['Furnished Premium (Studio)', '+73.3%'],
        ['Furnished Premium (1-Bed)', '+41.5%'],
        ['Best Strategy Net Revenue', 'AED 3,372,592 / year (AED 281,049 / month)'],
    ],
    highlight_rows=[8]
)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 2: MARKET ANALYSIS
# ══════════════════════════════════════════════════════════════════════

doc.add_heading('2. Market Analysis: Studio & 1-Bedroom Rents', level=1)

doc.add_heading('Price Statistics', level=2)

add_table(doc,
    ['Metric', 'Studio (224 contracts)', '1-Bedroom (2,883 contracts)'],
    [
        ['Highest Rent', 'AED 961,000 (Sep 20, 2025 - KAY 1 Building, JGC)', 'AED 289,895 (Feb 2, 2026 - Eden House)'],
        ['Lowest Rent', 'AED 10,928 (Feb 1, 2026)', 'AED 20,000 (Jan 1, 2026)'],
        ['Average Rent', 'AED 71,000', 'AED 78,992'],
        ['Median Rent', 'AED 50,000', 'AED 79,999'],
        ['Std Deviation', 'AED 79,186 (high variance)', 'AED 20,262 (consistent)'],
    ],
    highlight_rows=[0]
)

add_insight(doc, 'Studio rents show extremely high variance (std AED 79K on avg AED 71K) due to a wide range from basic units (AED 35-50K) to premium furnished units (AED 100-150K+). One-bedroom pricing is much more consistent, tightly clustered around AED 70-90K.')

add_image(doc, '01_price_distribution.png')
add_image(doc, '02_boxplot_comparison.png')

doc.add_heading('Price Trend Over Time', level=2)
add_image(doc, '17_price_trend.png')

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 3: PRICE DISTRIBUTION
# ══════════════════════════════════════════════════════════════════════

doc.add_heading('3. Price Distribution (AED 5,000 Increments)', level=1)

doc.add_heading('Studio - Most Common: AED 45,000 - 50,000 (39 contracts, 17.4%)', level=2)

add_table(doc,
    ['Price Range (AED)', 'Contracts', 'Share'],
    [
        ['45,000 - 50,000', '39', '17.4%'],
        ['40,000 - 45,000', '34', '15.2%'],
        ['50,000 - 55,000', '25', '11.2%'],
        ['60,000 - 65,000', '23', '10.3%'],
        ['35,000 - 40,000', '18', '8.0%'],
        ['55,000 - 60,000', '18', '8.0%'],
    ],
    highlight_rows=[0]
)

doc.add_heading('1-Bedroom - Most Common: AED 80,000 - 85,000 (544 contracts, 18.9%)', level=2)

add_table(doc,
    ['Price Range (AED)', 'Contracts', 'Share'],
    [
        ['80,000 - 85,000', '544', '18.9%'],
        ['75,000 - 80,000', '392', '13.6%'],
        ['70,000 - 75,000', '286', '9.9%'],
        ['85,000 - 90,000', '260', '9.0%'],
        ['60,000 - 65,000', '201', '7.0%'],
        ['65,000 - 70,000', '181', '6.3%'],
    ],
    highlight_rows=[0]
)

add_insight(doc, 'Studios concentrate in the AED 35,000-65,000 range (72% of contracts). 1-bedrooms are tightly clustered around AED 70,000-90,000 (51.4%). The market sweet spots are AED 45-50K for studios and AED 80-85K for 1-beds.')

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 4: RENT PER SQFT
# ══════════════════════════════════════════════════════════════════════

doc.add_heading('4. Rent per Square Foot Analysis', level=1)

add_table(doc,
    ['Metric', 'Studio', '1-Bedroom'],
    [
        ['Average Rent/sqft', 'AED 158', 'AED 102'],
        ['Median Rent/sqft', 'AED 150', 'AED 100'],
        ['Max Rent/sqft', 'AED 402', 'AED 340'],
        ['Avg Unit Size', '428 sqft', '809 sqft'],
        ['Studio Premium per sqft', '+55%', '(baseline)'],
    ],
    highlight_rows=[4]
)

add_image(doc, '04_rent_per_sqft.png')

doc.add_heading('Unit Size vs Rent Relationship', level=2)
add_image(doc, '18_size_vs_rent.png')

add_insight(doc, 'Studios command a 55% premium per square foot (AED 158 vs AED 102) despite being roughly half the size. This makes studios more efficient from a landlord yield perspective.')

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 5: COMMUNITIES & COMMENTS
# ══════════════════════════════════════════════════════════════════════

doc.add_heading('5. Top Communities & Highest-Paying Comments', level=1)

doc.add_heading('Top Communities by Average Rent', level=2)

add_table(doc,
    ['Community', 'Type', 'Avg Rent', 'Max Rent', 'Contracts', 'Avg/sqft'],
    [
        ['Eden House', 'Studio', 'AED 146,005', 'AED 282,000', '24', 'AED 265'],
        ['Eden House', '1-Bed', 'AED 130,613', 'AED 289,895', '279', 'AED 140'],
        ['Jumeirah Garden City', 'Studio', 'AED 65,746', 'AED 961,000', '82', 'AED 162'],
        ['Jumeirah Garden City', '1-Bed', 'AED 82,043', 'AED 270,000', '1,097', 'AED 105'],
        ['South Heights Tower', 'Studio', 'AED 46,749', 'AED 63,000', '29', 'AED 120'],
        ['South Heights Tower', '1-Bed', 'AED 68,310', 'AED 93,000', '378', 'AED 85'],
    ],
    highlight_rows=[0, 1]
)

add_image(doc, '03_top_communities.png')
add_image(doc, '08_community_comparison.png')

doc.add_heading('Comments with Highest Rents', level=2)
add_insight(doc, 'Listings with "Furnished", "Brand New", "Burj Khalifa View" consistently command premiums of AED 150,000-290,000 - roughly 2-3x the market average.')

add_image(doc, '09_comments_highest_rents.png')

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 6: OCCUPANCY
# ══════════════════════════════════════════════════════════════════════

doc.add_heading('6. Occupancy Rate Analysis', level=1)

doc.add_heading('Contract Type Distribution (Occupancy Proxy)', level=2)

add_table(doc,
    ['Metric', 'Studio', '1-Bedroom', 'All Types'],
    [
        ['Renewals', '113 (50.4%)', '946 (32.8%)', '2,390 (37.3%)'],
        ['New Contracts', '70 (31.2%)', '570 (19.8%)', '1,145 (17.9%)'],
        ['Est. Occupancy Rate', '50.4%', '32.8%', '37.3%'],
    ],
    highlight_rows=[2]
)

add_insight(doc, 'Studios show notably higher tenant retention (50.4% renewal) vs 1-bedrooms (32.8%), suggesting the studio market is tighter with fewer alternatives.')

add_image(doc, '05_occupancy_new_vs_renewal.png')
add_image(doc, '06_monthly_volume.png')

doc.add_heading('Contract Duration', level=2)

add_table(doc,
    ['Duration', 'Count', 'Share'],
    [
        ['Short-term (<6 months)', '1,416', '45.6%'],
        ['Standard (6-12 months)', '1,583', '50.9%'],
        ['Long-term (>12 months)', '108', '3.5%'],
    ],
)

add_image(doc, '07_contract_duration.png')

doc.add_heading('Airbnb / Short-Term Indicators', level=2)

add_table(doc,
    ['Indicator', 'Studio', '1-Bedroom'],
    [
        ['Furnished/All-bills listings', '12 (5.4%)', '263 (9.1%)'],
        ['Avg rent (furnished keywords)', 'AED 118,375', 'AED 107,625'],
        ['Premium vs market average', '+67%', '+36%'],
    ],
    highlight_rows=[2]
)

add_image(doc, '10_airbnb_indicators.png')

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 7: BUILDING PROJECTIONS
# ══════════════════════════════════════════════════════════════════════

doc.add_heading('7. Building Projections: 24 Studios + 32 One-Beds', level=1)

doc.add_heading('Expected Rent Per Unit (Market Rate, 100% Occupancy)', level=2)

add_table(doc,
    ['Unit Type', 'Per Unit/Year', 'Per Unit/Month', 'All Units/Year'],
    [
        ['Studio Unfurnished', 'AED 68,319', 'AED 5,693', 'AED 1,639,656'],
        ['Studio Furnished (+73.3%)', 'AED 118,375', 'AED 9,865', 'AED 2,841,000'],
        ['1-Bed Unfurnished', 'AED 76,132', 'AED 6,344', 'AED 2,436,224'],
        ['1-Bed Furnished (+41.5%)', 'AED 107,724', 'AED 8,977', 'AED 3,447,168'],
        ['TOTAL (Unfurnished)', '', '', 'AED 4,075,880'],
        ['TOTAL (Furnished)', '', '', 'AED 6,288,168'],
    ],
    highlight_rows=[4, 5]
)

doc.add_heading('Optimal Pricing for Target Occupancy', level=2)

add_table(doc,
    ['Unit Type', '90% Occ Price/yr', '90% Monthly', '80% Occ Price/yr', '80% Monthly'],
    [
        ['Studio Unfurnished', 'AED 40,000', 'AED 3,333', 'AED 53,000', 'AED 4,417'],
        ['Studio Furnished', 'AED 69,320', 'AED 5,777', 'AED 91,849', 'AED 7,654'],
        ['1-Bed Unfurnished', 'AED 60,000', 'AED 5,000', 'AED 70,000', 'AED 5,833'],
        ['1-Bed Furnished', 'AED 84,900', 'AED 7,075', 'AED 99,050', 'AED 8,254'],
    ],
)

add_insight(doc, 'To guarantee 90% occupancy, price ~25% below market average. For 80%, price ~10-15% below. The revenue-maximizing sweet spot is at 72-76% occupancy.')

doc.add_heading('Demand Curves & Revenue Optimization', level=2)
add_image(doc, '22_demand_curves.png')

doc.add_heading('Revenue Maximization Sweet Spots', level=2)

add_table(doc,
    ['Unit Type', 'Optimal Price', 'Occupancy', 'Total Revenue/Year'],
    [
        ['Studio Unfurnished', 'AED 60,000/yr', '72%', 'AED 1,036,800'],
        ['Studio Furnished', 'AED 100,000/yr', '75%', 'AED 1,794,142'],
        ['1-Bed Unfurnished', 'AED 75,000/yr', '75%', 'AED 1,800,000'],
        ['1-Bed Furnished', 'AED 105,000/yr', '76%', 'AED 2,546,714'],
    ],
    highlight_rows=[0, 1, 2, 3]
)

add_image(doc, '13_revenue_optimization.png')
add_image(doc, '19_building_summary.png')

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 8: FURNISHED VS UNFURNISHED
# ══════════════════════════════════════════════════════════════════════

doc.add_heading('8. Furnished vs Unfurnished ROI', level=1)

doc.add_heading('Furnishing Investment', level=2)

add_table(doc,
    ['Item', 'Cost'],
    [
        ['Studio furnishing (x24 @ AED 25,000)', 'AED 600,000'],
        ['1-Bed furnishing (x32 @ AED 40,000)', 'AED 1,280,000'],
        ['Total Investment', 'AED 1,880,000'],
        ['Annual amortization (4yr cycle)', 'AED 470,000/yr'],
    ],
    highlight_rows=[2]
)

doc.add_heading('Net Revenue Comparison - 80% Occupancy', level=2)

add_table(doc,
    ['Metric', 'Unfurnished', 'Furnished', 'Difference'],
    [
        ['Studio Rent/yr', 'AED 53,000', 'AED 91,849', '+AED 38,849'],
        ['1-Bed Rent/yr', 'AED 70,000', 'AED 99,050', '+AED 29,050'],
        ['Gross Revenue/yr', 'AED 2,757,000', 'AED 4,221,381', '+AED 1,464,381'],
        ['Furniture Cost/yr', 'AED 0', 'AED 470,000', ''],
        ['Net Revenue/Year', 'AED 2,757,000', 'AED 3,751,381', '+AED 994,381'],
        ['Net Revenue/Month', 'AED 229,750', 'AED 312,615', '+AED 82,865'],
        ['Year 1 ROI', '', '', '77.9%'],
    ],
    highlight_rows=[4, 5, 6]
)

doc.add_heading('Net Revenue Comparison - 90% Occupancy', level=2)

add_table(doc,
    ['Metric', 'Unfurnished', 'Furnished', 'Difference'],
    [
        ['Studio Rent/yr', 'AED 40,000', 'AED 69,320', '+AED 29,320'],
        ['1-Bed Rent/yr', 'AED 60,000', 'AED 84,900', '+AED 24,900'],
        ['Gross Revenue/yr', 'AED 2,520,000', 'AED 3,832,920', '+AED 1,312,920'],
        ['Furniture Cost/yr', 'AED 0', 'AED 470,000', ''],
        ['Net Revenue/Year', 'AED 2,520,000', 'AED 3,362,920', '+AED 842,920'],
        ['Net Revenue/Month', 'AED 210,000', 'AED 280,243', '+AED 70,243'],
        ['Year 1 ROI', '', '', '69.8%'],
    ],
    highlight_rows=[4, 5, 6]
)

add_image(doc, '21_furnished_roi.png')

add_recommendation(doc, 'Furnished is clearly worth the investment',
    'The AED 1.88M furnishing investment pays back within 1.9-2.2 years and delivers an additional AED 843K-994K per year in net revenue. Over a 5-year period, the cumulative benefit is AED 3-4 million.')

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 9: HOLIDAY HOME
# ══════════════════════════════════════════════════════════════════════

doc.add_heading('9. Holiday Home / Airbnb Analysis', level=1)

doc.add_heading('Seasonal Occupancy & Nightly Rates', level=2)

add_table(doc,
    ['Month', 'Season', 'Occupancy', 'Studio Rate', '1-Bed Rate'],
    [
        ['January', 'Peak', '82%', 'AED 450', 'AED 600'],
        ['February', 'Peak', '85%', 'AED 450', 'AED 600'],
        ['March', 'Peak', '78%', 'AED 450', 'AED 600'],
        ['April', 'Shoulder', '68%', 'AED 350', 'AED 480'],
        ['May', 'Low', '45%', 'AED 250', 'AED 350'],
        ['June', 'Low', '35%', 'AED 250', 'AED 350'],
        ['July', 'Low', '38%', 'AED 250', 'AED 350'],
        ['August', 'Low', '40%', 'AED 250', 'AED 350'],
        ['September', 'Shoulder', '48%', 'AED 350', 'AED 480'],
        ['October', 'Peak', '72%', 'AED 450', 'AED 600'],
        ['November', 'Peak', '80%', 'AED 450', 'AED 600'],
        ['December', 'Peak', '88%', 'AED 450', 'AED 600'],
    ],
)

p = doc.add_paragraph()
run = p.add_run('Average annual occupancy: 63%')
run.font.bold = True

add_image(doc, '20_holiday_seasonal.png')
add_image(doc, '12_holiday_home_monthly.png')

doc.add_heading('Holiday Home Operating Costs (All 56 Units)', level=2)

add_table(doc,
    ['Cost Item', 'Amount'],
    [
        ['Gross Revenue', 'AED 6,073,284'],
        ['Management fee (20%)', '-AED 1,214,657'],
        ['Cleaning/turnovers (3,226 turnovers)', '-AED 576,075'],
        ['Utilities (AED 500/unit/month)', '-AED 336,000'],
        ['DTCM Licensing', '-AED 85,120'],
        ['Insurance', '-AED 112,000'],
        ['Furniture replacement (3yr cycle)', '-AED 626,667'],
        ['Total Costs', '-AED 2,950,518'],
        ['NET Revenue', 'AED 3,122,766 (AED 260K/month)'],
    ],
    highlight_rows=[8]
)

p = doc.add_paragraph()
run = p.add_run('Warning: ')
run.font.bold = True
run.font.color.rgb = RGBColor(230, 81, 0)
run = p.add_run('While holiday homes generate the highest gross (AED 6.07M), operating costs consume 49% of revenue. Summer months (May-Aug) see occupancy drop to 35-45%, creating cash flow volatility.')

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# SECTION 10: STRATEGY COMPARISON & RECOMMENDATION
# ══════════════════════════════════════════════════════════════════════

doc.add_heading('10. Strategy Comparison & Final Recommendation', level=1)

doc.add_heading('All Strategies Compared', level=2)

add_table(doc,
    ['Strategy', 'Gross Rev/yr', 'Costs/yr', 'Net Rev/yr', 'Net Rev/mo'],
    [
        ['A: All Long-Term Unfurnished (90%)', 'AED 2,520,000', 'AED 0', 'AED 2,520,000', 'AED 210,000'],
        ['B: All Long-Term Furnished (90%)', 'AED 3,832,920', 'AED 470,000', 'AED 3,362,920', 'AED 280,243'],
        ['C: All Holiday Homes (56 units)', 'AED 6,073,284', 'AED 2,950,518', 'AED 3,122,766', 'AED 260,230'],
        ['D: Hybrid Light (5S+5B holiday)', 'AED 4,278,100', 'AED 905,508', 'AED 3,372,592', 'AED 281,049'],
        ['E: Hybrid Medium (8S+8B holiday)', 'AED 4,452,676', 'AED 1,166,814', 'AED 3,285,862', 'AED 273,822'],
        ['F: Hybrid Heavy (10S+10B holiday)', 'AED 4,569,060', 'AED 1,341,017', 'AED 3,228,043', 'AED 269,004'],
        ['G: Hybrid Optimized (5S+10B)', 'AED 4,463,222', 'AED 1,149,307', 'AED 3,313,915', 'AED 276,160'],
    ],
    highlight_rows=[3]
)

add_image(doc, '11_strategy_comparison.png')
add_image(doc, '14_all_strategies_comparison.png')

doc.add_heading('RECOMMENDED: Strategy D - Hybrid Light', level=2)

p = doc.add_paragraph()
run = p.add_run('19 Studios + 27 One-Beds as Long-Term Furnished')
run.font.bold = True
run.font.size = Pt(13)
run.font.color.rgb = RGBColor(46, 125, 50)

p = doc.add_paragraph()
run = p.add_run('5 Studios + 5 One-Beds as Holiday Homes')
run.font.bold = True
run.font.size = Pt(13)
run.font.color.rgb = RGBColor(230, 81, 0)

add_table(doc,
    ['Revenue Component', 'Amount'],
    [
        ['Long-term rental income', 'AED 3,216,040'],
        ['Holiday home income', 'AED 1,062,060'],
        ['Total gross', 'AED 4,278,100'],
        ['Total costs', '-AED 905,508'],
        ['NET ANNUAL REVENUE', 'AED 3,372,592'],
        ['NET MONTHLY REVENUE', 'AED 281,049'],
    ],
    highlight_rows=[4, 5]
)

p = doc.add_paragraph()
run = p.add_run('+33.8% uplift vs all-unfurnished baseline (AED +852,592/yr additional revenue)')
run.font.bold = True
run.font.color.rgb = RGBColor(46, 125, 50)
run.font.size = Pt(12)

add_image(doc, '15_hybrid_breakdown.png')

doc.add_heading('Why This Strategy Wins', level=2)

reasons = [
    ('Highest net revenue', 'AED 3.37M beats both pure long-term (AED 3.36M) and pure holiday home (AED 3.12M)'),
    ('Diversified income', '75% stable long-term + 25% variable short-term reduces overall risk'),
    ('Manageable complexity', 'Only 10 units need holiday home management vs 56 in the all-holiday-home strategy'),
    ('Summer protection', '46 long-term units provide steady income during the May-August low season'),
    ('Lower costs', 'AED 906K vs AED 2.95M for all holiday homes; costs are only 21% of gross revenue'),
    ('Upside optionality', 'Can convert more units to holiday homes during peak season if demand justifies it'),
]

for title, desc in reasons:
    p = doc.add_paragraph()
    run = p.add_run(f'{title}: ')
    run.font.bold = True
    run.font.color.rgb = RGBColor(21, 101, 192)
    p.add_run(desc)

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════
# KEY TAKEAWAYS PAGE
# ══════════════════════════════════════════════════════════════════════

doc.add_heading('Key Takeaways', level=1)

takeaways = [
    'Furnished always beats unfurnished - 70-78% ROI on the AED 1.88M furnishing investment in Year 1 alone.',
    'Pure holiday home is NOT the best - Despite highest gross (AED 6M), operating costs (AED 2.95M) eat into margins, netting only AED 3.12M vs AED 3.37M for the hybrid.',
    'The hybrid light model wins - Just 10 units as holiday homes with 46 as long-term furnished delivers the highest net revenue at AED 3,372,592/yr.',
    'More holiday homes = diminishing returns - Each additional holiday home unit adds operational complexity and cost that outweighs the revenue premium.',
    'Pricing sweet spots: Studios AED 40-53K unfurnished / AED 69-92K furnished. 1-Beds AED 60-70K unfurnished / AED 85-99K furnished.',
    'Summer (May-Aug) is the holiday home weakness - Occupancy drops to 35-45%, making the all-holiday-home strategy risky.',
    'Revenue maximization prices (72-76% occupancy sweet spot): Studio furnished AED 100K/yr, 1-Bed furnished AED 105K/yr.',
    'Eden House dominates premium rents across both categories at approximately 2x the area average.',
]

for i, t in enumerate(takeaways, 1):
    p = doc.add_paragraph()
    run = p.add_run(f'{i}. ')
    run.font.bold = True
    run.font.color.rgb = RGBColor(21, 101, 192)
    run.font.size = Pt(11)
    run = p.add_run(t)
    run.font.size = Pt(11)
    p.paragraph_format.space_after = Pt(8)

# ══════════════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════════════

doc.add_paragraph()
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Al Satwa Rental Market Analysis & Building Projections Report')
run.font.color.rgb = RGBColor(150, 150, 150)
run.font.size = Pt(9)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Generated March 12, 2026 | Based on 6,414 rental contracts | Al Satwa, Dubai')
run.font.color.rgb = RGBColor(150, 150, 150)
run.font.size = Pt(9)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('Data Source: Al Satwa Market Data (Eva Real Estate LLC)')
run.font.color.rgb = RGBColor(150, 150, 150)
run.font.size = Pt(9)

# ══════════════════════════════════════════════════════════════════════
# SAVE
# ══════════════════════════════════════════════════════════════════════

output_path = 'report/Al_Satwa_Rental_Analysis_Report.docx'
doc.save(output_path)
print(f"Word document saved: {output_path}")
print(f"File size: {os.path.getsize(output_path) / 1024 / 1024:.1f} MB")
