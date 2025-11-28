"""
Baylor Football Force Plate Training Report - REAL DATA VERSION
Processes actual CMJ and IMTP data from ForceDecks exports
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

REPORT_DATE = datetime.now()
TEAM_NAME = "Baylor Football"
TRAINING_PHASE = "Fall Training Block"
NEXT_PHASE = "Winter Preparation Phase"
MONTHS_TO_INCLUDE = 6

# File paths
ROSTER_FILE = '2025-11-27_FB_Roster_2025_ER.csv'
CMJ_FILE = '2025-11-27-CMJ_Last6mnthscsv.csv'
IMTP_FILE = '2025-11-27-IMTP_Last6mnthscsv.csv'

DECISION_RULES = {
    1: {
        'name': 'MAXIMAL STRENGTH CAPACITY',
        'trend_desc': 'IMTP Peak Force and Net Peak Vertical Force declining',
        'metrics': ['IMTP_Peak_Force', 'IMTP_Net_Peak_Force'],
        'trend': 'decrease',
        'wr_suggestions': [
            'Heavy isometrics with 3-5 second holds',
            'Cluster sets (≥80% 1RM) - 3 reps, 20s rest, repeat 3×',
            'Wave loading (vary intensity within session)',
            'Extend rest periods to 4-5 minutes between sets'
        ],
        'field_suggestions': [
            'Resisted sprints (50-60% vdec)',
            'Heavy sled pushes',
            'Focus on max force production over speed'
        ],
        'interpretation': 'Maximal strength capacity declining. Consider making cluster sets and extended rest a phase emphasis for these athletes.',
        'execution_note': 'Still do your planned exercises (trap bar, safety bar, whatever), but execute them with longer rest, cluster structure, or add isometric holds.'
    },
    2: {
        'name': 'EXPLOSIVE STRENGTH / RFD',
        'trend_desc': 'Early-phase RFD (50-200ms) declining',
        'metrics': ['IMTP_Force_50ms', 'IMTP_Force_100ms', 'IMTP_Force_200ms'],
        'trend': 'decrease',
        'wr_suggestions': [
            'Contrast/complex training (heavy → explosive superset)',
            'Olympic lift variations (60-70% 1RM)',
            'Accommodating resistance with explosive intent',
            'Example: Trap bar (heavy) → Box jumps (explosive)'
        ],
        'field_suggestions': [
            'Resisted sprints (10-30% vdec)',
            'Contrast sprints (resisted → unresisted)'
        ],
        'interpretation': 'Rate of force development declining. Consider contrast training emphasis in next phase for these athletes.',
        'execution_note': 'If you planned trap bar deadlifts, pair them with vertical jumps in a superset. Still the same movements, just executed as contrasts.'
    },
    3: {
        'name': 'POWER OUTPUT',
        'trend_desc': 'Peak Power declining',
        'metrics': ['CMJ_Peak_Power'],
        'trend': 'decrease',
        'wr_suggestions': [
            'Contrast/complex training',
            'Cluster sets (70-80% 1RM)',
            'Olympic lift variations',
            'Ballistic movements emphasis'
        ],
        'field_suggestions': [
            'Contrast/complex training',
            'Resisted sprints (30-50% vdec)'
        ],
        'interpretation': 'Power output declining. Focus on moving submaximal loads with maximal intent.',
        'execution_note': 'Focus on moving submaximal loads with maximal intent. Use cluster sets for Olympic lifts.'
    },
    4: {
        'name': 'SSC EFFICIENCY',
        'trend_desc': 'RSI-modified and Eccentric Braking RFD declining',
        'metrics': ['CMJ_RSI_modified', 'CMJ_Eccentric_Braking_RFD'],
        'trend': 'decrease',
        'wr_suggestions': [
            'Reactive/ballistic techniques',
            'Drop jumps, altitude landings',
            'Reactive medicine ball work'
        ],
        'field_suggestions': [
            'Plyometric training (pogos, bounds, hurdle hops)',
            'Reactive agility drills'
        ],
        'interpretation': 'Stretch-shortening cycle efficiency compromised. Emphasize quick ground contacts and reactive training.',
        'execution_note': 'Emphasize quick ground contacts. Think "hot ground" mentality rather than max height.'
    },
    5: {
        'name': 'ECCENTRIC CONTROL & BRAKING',
        'trend_desc': 'Eccentric braking force declining',
        'metrics': ['CMJ_Eccentric_Mean_Braking_Force'],
        'trend': 'decrease',
        'wr_suggestions': [
            'Tempo eccentrics (5-second down on squats/RDLs)',
            'Accentuated eccentric overload (105-120% 1RM)',
            'Reverse band work (overload eccentric phase)',
            'Example: Safety bar squat with 5-count down'
        ],
        'field_suggestions': [
            'Change of direction drills',
            'Deceleration-focused agility work'
        ],
        'interpretation': 'Eccentric strength declining - potential injury risk concern. Prioritize eccentric strength development.',
        'execution_note': 'If doing safety bar squats, add a 5-count down. Or use reverse bands. We\'ve done this before.'
    },
    6: {
        'name': 'TECHNICAL / COORDINATION',
        'trend_desc': 'Contraction Time and Time to Peak Force increasing',
        'metrics': ['CMJ_Contraction_Time', 'IMTP_Time_to_Peak_Force'],
        'trend': 'increase',
        'wr_suggestions': [
            'Wave loading (vary intensity within session)',
            'Cluster sets',
            'Rhythmic tempo work (consistent cadence)',
            'Motor control focus'
        ],
        'field_suggestions': [
            'Movement skill retraining',
            'Motor control drills',
            'Technical sprint work (not conditioning)'
        ],
        'interpretation': 'Movement efficiency declining. Reduce intensity and focus on movement quality.',
        'execution_note': 'Think movement quality over load. Use wave loading to get quality reps at different intensities.'
    },
    7: {
        'name': 'ASYMMETRY / LIMB IMBALANCE',
        'trend_desc': 'L-R Force Asymmetry > 10%',
        'metrics': ['IMTP_Asymmetry'],
        'trend': 'absolute',
        'threshold': 10,
        'wr_suggestions': [
            'Single-leg/unilateral strength work',
            'Split-stance patterns (split squats, SL RDLs)',
            'Unilateral jumps and landings',
            'Offset loading'
        ],
        'field_suggestions': [
            'Unilateral jumps',
            'Single-leg bounds',
            'Asymmetrical agility work'
        ],
        'interpretation': 'Limb imbalances detected. Address through unilateral training to reduce injury risk.',
        'execution_note': 'If squats are programmed, replace with split squats. Address the imbalance through exercise selection.'
    }
}

SEVERITY_THRESHOLDS = {
    'red': 2.0,      # >2× SWC
    'orange': 1.5,   # 1.5-2× SWC
    'yellow': 1.0    # 1-1.5× SWC
}

# ============================================================================
# DATA LOADING AND PROCESSING
# ============================================================================

def load_and_merge_data():
    """Load all data files and merge into single DataFrame"""
    print("Loading data files...")

    # Load roster (Excel file despite .csv extension)
    roster = pd.read_excel(ROSTER_FILE)
    print(f"✓ Loaded roster: {len(roster)} athletes")

    # Load CMJ data
    cmj = pd.read_csv(CMJ_FILE)
    cmj['Date'] = pd.to_datetime(cmj['Date'])
    print(f"✓ Loaded CMJ data: {len(cmj)} tests from {cmj['Name'].nunique()} athletes")

    # Load IMTP data
    imtp = pd.read_csv(IMTP_FILE)
    imtp['Date'] = pd.to_datetime(imtp['Date'])
    print(f"✓ Loaded IMTP data: {len(imtp)} tests from {imtp['Name'].nunique()} athletes")

    # Clean column names (remove trailing spaces)
    cmj.columns = cmj.columns.str.strip()
    imtp.columns = imtp.columns.str.strip()

    # Rename columns to match our expected format
    cmj_renamed = cmj.rename(columns={
        'Name': 'Athlete_Name',
        'Peak Power [W]': 'CMJ_Peak_Power',
        'RSI-modified [m/s]': 'CMJ_RSI_modified',
        'Contraction Time [ms]': 'CMJ_Contraction_Time',
        'Eccentric Mean Braking Force [N]': 'CMJ_Eccentric_Mean_Braking_Force',
        'Eccentric Braking RFD [N/s]': 'CMJ_Eccentric_Braking_RFD',
        'Jump Height (Imp-Mom) in Inches [in]': 'CMJ_Jump_Height'
    })

    imtp_renamed = imtp.rename(columns={
        'Name': 'Athlete_Name',
        'Peak Vertical Force [N]': 'IMTP_Peak_Force',
        'Net Peak Vertical Force [N]': 'IMTP_Net_Peak_Force',
        'Force at 50ms [N]': 'IMTP_Force_50ms',
        'Force at 100ms [N]': 'IMTP_Force_100ms',
        'Force at 200ms [N]': 'IMTP_Force_200ms',
        'Peak Vertical Force % (Asym) (%)': 'IMTP_Asymmetry_Raw',
        'Start Time to Peak Force [s]': 'IMTP_Time_to_Peak_Force'
    })

    # Convert IMTP Time to Peak Force from seconds to milliseconds
    imtp_renamed['IMTP_Time_to_Peak_Force'] = imtp_renamed['IMTP_Time_to_Peak_Force'] * 1000

    # Convert CMJ Contraction Time to seconds (it's in ms)
    imtp_renamed['CMJ_Contraction_Time_s'] = cmj_renamed['CMJ_Contraction_Time'] / 1000

    # Process asymmetry: extract numeric value and convert to absolute percentage
    def extract_asymmetry(val):
        if pd.isna(val):
            return np.nan
        if isinstance(val, (int, float)):
            return abs(float(val))
        # Handle "6.6 L" or "6.6 R" format
        val_str = str(val).strip()
        try:
            # Extract number part
            num = float(val_str.split()[0])
            return abs(num)
        except:
            return np.nan

    imtp_renamed['IMTP_Asymmetry'] = imtp_renamed['IMTP_Asymmetry_Raw'].apply(extract_asymmetry)

    # Select relevant columns
    cmj_cols = ['Athlete_Name', 'Date', 'CMJ_Peak_Power', 'CMJ_RSI_modified',
                'CMJ_Contraction_Time', 'CMJ_Eccentric_Mean_Braking_Force',
                'CMJ_Eccentric_Braking_RFD', 'CMJ_Jump_Height']

    imtp_cols = ['Athlete_Name', 'Date', 'IMTP_Peak_Force', 'IMTP_Net_Peak_Force',
                 'IMTP_Force_50ms', 'IMTP_Force_100ms', 'IMTP_Force_200ms',
                 'IMTP_Asymmetry', 'IMTP_Time_to_Peak_Force']

    cmj_clean = cmj_renamed[cmj_cols].copy()
    imtp_clean = imtp_renamed[imtp_cols].copy()

    # Merge CMJ and IMTP on athlete and date (outer join to keep all tests)
    merged = pd.merge(cmj_clean, imtp_clean, on=['Athlete_Name', 'Date'], how='outer')

    # Add position from roster
    merged = pd.merge(merged, roster.rename(columns={'Name': 'Athlete_Name'}),
                     on='Athlete_Name', how='left')

    # Sort by athlete and date
    merged = merged.sort_values(['Athlete_Name', 'Date']).reset_index(drop=True)

    print(f"\n✓ Merged dataset: {len(merged)} tests from {merged['Athlete_Name'].nunique()} athletes")
    print(f"  Date range: {merged['Date'].min().date()} to {merged['Date'].max().date()}")

    return merged

# ============================================================================
# ANALYSIS FUNCTIONS
# ============================================================================

def calculate_swc(data):
    """Calculate Smallest Worthwhile Change"""
    return 0.2 * np.std(data)

def classify_severity(deviation, swc):
    """Classify deviation severity"""
    abs_dev = abs(deviation)
    if abs_dev > SEVERITY_THRESHOLDS['red'] * swc:
        return 'critical', '🔴'
    elif abs_dev > SEVERITY_THRESHOLDS['orange'] * swc:
        return 'warning', '🟠'
    elif abs_dev > SEVERITY_THRESHOLDS['yellow'] * swc:
        return 'caution', '🟡'
    return 'normal', '🟢'

def categorize_athletes(df):
    """Categorize athletes based on force plate trends"""
    print("\nCategorizing athletes...")

    results = {'categories': {}}
    athletes = df['Athlete_Name'].unique()

    for cat_num, rule in DECISION_RULES.items():
        category_athletes = []

        for athlete in athletes:
            athlete_data = df[df['Athlete_Name'] == athlete].sort_values('Date')

            if len(athlete_data) < 5:  # Need minimum 5 tests
                continue

            all_flagged = True
            worst_severity = 'normal'
            sev_order = {'critical': 0, 'warning': 1, 'caution': 2, 'normal': 3}

            for metric in rule['metrics']:
                if metric not in df.columns:
                    all_flagged = False
                    break

                metric_data = athlete_data[metric].dropna()
                if len(metric_data) < 3:
                    all_flagged = False
                    break

                # Use first 60% as baseline, compare last value
                split = int(len(metric_data) * 0.6)
                baseline = metric_data.iloc[:split]
                current = metric_data.iloc[-1]

                if len(baseline) < 2:
                    all_flagged = False
                    break

                baseline_mean = baseline.mean()
                swc = calculate_swc(baseline)

                if rule.get('trend') == 'absolute':
                    if current > rule['threshold']:
                        severity, emoji = 'critical', '🔴'
                    else:
                        all_flagged = False
                        break
                else:
                    if rule['trend'] == 'decrease':
                        deviation = baseline_mean - current
                    else:
                        deviation = current - baseline_mean

                    severity, emoji = classify_severity(deviation, swc)

                    if severity == 'normal':
                        all_flagged = False
                        break

                if sev_order[severity] < sev_order[worst_severity]:
                    worst_severity = severity

            if all_flagged:
                pos = athlete_data['Position'].iloc[-1] if 'Position' in athlete_data.columns and pd.notna(athlete_data['Position'].iloc[-1]) else ''

                category_athletes.append({
                    'name': athlete,
                    'position': pos,
                    'severity': worst_severity,
                    'emoji': {'critical': '🔴', 'warning': '🟠', 'caution': '🟡'}[worst_severity]
                })

        category_athletes.sort(key=lambda x: {'critical': 0, 'warning': 1, 'caution': 2}[x['severity']])

        if category_athletes:
            results['categories'][cat_num] = {
                'name': rule['name'],
                'trend_desc': rule['trend_desc'],
                'athletes': category_athletes,
                'count': len(category_athletes),
                'critical': sum(1 for a in category_athletes if a['severity'] == 'critical'),
                'warning': sum(1 for a in category_athletes if a['severity'] == 'warning'),
                'caution': sum(1 for a in category_athletes if a['severity'] == 'caution'),
                'wr_suggestions': rule['wr_suggestions'],
                'field_suggestions': rule['field_suggestions'],
                'interpretation': rule['interpretation'],
                'execution_note': rule['execution_note']
            }

    total_flagged = len(set([a['name'] for cat in results['categories'].values() for a in cat['athletes']]))
    categories_flagged = len(results['categories'])

    print(f"✓ Found {categories_flagged} categories with issues")
    print(f"✓ Flagged {total_flagged} athletes needing intervention")

    return results, df

# ============================================================================
# REPORT GENERATION
# ============================================================================

def generate_text_report(results, df):
    """Generate text report"""
    print("\nGenerating text report...")

    total_athletes = df['Athlete_Name'].nunique()
    total_flagged = len(set([a['name'] for cat in results['categories'].values() for a in cat['athletes']]))
    categories_flagged = len(results['categories'])

    report = []
    report.append("="*80)
    report.append("FORCE PLATE TRAINING REPORT".center(80))
    report.append("="*80)
    report.append(f"\nTeam: {TEAM_NAME}")
    report.append(f"Report Date: {REPORT_DATE.strftime('%B %d, %Y')}")
    report.append(f"Training Phase: {TRAINING_PHASE}")
    report.append(f"Data Window: {df['Date'].min().date()} to {df['Date'].max().date()}")
    report.append("-"*80)

    report.append(f"\nSUMMARY:")
    report.append(f"  Total Athletes: {total_athletes}")
    report.append(f"  Athletes Flagged: {total_flagged} ({total_flagged/total_athletes*100:.0f}%)")
    report.append(f"  Categories Flagged: {categories_flagged}")
    report.append("")

    for cat_num in sorted(results['categories'].keys()):
        cat_data = results['categories'][cat_num]

        report.append("\n" + "="*80)
        report.append(f"CATEGORY {cat_num}: {cat_data['name']}")
        report.append("="*80)
        report.append(f"📉 Trend: {cat_data['trend_desc']}")

        report.append("\n🏋️ WEIGHT ROOM RECOMMENDATIONS:")
        for suggestion in cat_data['wr_suggestions']:
            report.append(f"  • {suggestion}")

        report.append("\n⚡ FIELD RECOMMENDATIONS:")
        for suggestion in cat_data['field_suggestions']:
            report.append(f"  • {suggestion}")

        report.append(f"\n👥 ATHLETES IN THIS CATEGORY: {cat_data['count']}")
        for athlete in cat_data['athletes']:
            pos_str = f", {athlete['position']}" if athlete['position'] else ""
            report.append(
                f"  {athlete['emoji']} {athlete['name']}{pos_str} - {athlete['severity'].title()}"
            )

        report.append(
            f"\n  Distribution: {cat_data['critical']} Critical | "
            f"{cat_data['warning']} Warning | {cat_data['caution']} Caution"
        )

        report.append(f"\n💡 INTERPRETATION:")
        report.append(f"  {cat_data['interpretation']}")

        report.append(f"\n💡 EXECUTION NOTE:")
        report.append(f"  {cat_data['execution_note']}")
        report.append("")

    all_categories = set(DECISION_RULES.keys())
    flagged_categories = set(results['categories'].keys())
    normal_categories = all_categories - flagged_categories

    if normal_categories:
        report.append("\n" + "="*80)
        report.append("✅ CATEGORIES NOT FLAGGED (All athletes within normal range)")
        report.append("="*80)
        for cat_num in sorted(normal_categories):
            report.append(f"  ✓ Category {cat_num}: {DECISION_RULES[cat_num]['name']}")

    report.append("\n" + "="*80)
    report.append("END OF REPORT".center(80))
    report.append("="*80)

    return "\n".join(report)

def generate_html_report(results, df):
    """Generate HTML report"""
    print("Generating HTML report...")

    total_athletes = df['Athlete_Name'].nunique()
    total_flagged = len(set([a['name'] for cat in results['categories'].values() for a in cat['athletes']]))
    categories_flagged = len(results['categories'])
    data_window = f"{df['Date'].min().date()} to {df['Date'].max().date()}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Force Plate Training Report - {TEAM_NAME}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
            color: #333;
        }}

        .page {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header {{
            border-bottom: 4px solid #1B5E20;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}

        .header h1 {{
            color: #1B5E20;
            font-size: 32px;
            margin-bottom: 15px;
        }}

        .header-info {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }}

        .header-info div {{
            display: flex;
            gap: 10px;
        }}

        .header-info strong {{
            color: #1B5E20;
            min-width: 150px;
        }}

        .summary-box {{
            background: #E3F2FD;
            border-left: 5px solid #1976D2;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}

        .summary-box h2 {{
            color: #1976D2;
            font-size: 18px;
            margin-bottom: 10px;
        }}

        .category-card {{
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            margin: 25px 0;
            overflow: hidden;
        }}

        .category-header {{
            background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
            color: white;
            padding: 20px;
        }}

        .category-header h3 {{
            font-size: 22px;
            margin-bottom: 8px;
        }}

        .category-header p {{
            opacity: 0.9;
            font-size: 14px;
        }}

        .category-body {{
            padding: 20px;
        }}

        .recommendations {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }}

        .rec-section h4 {{
            color: #1B5E20;
            font-size: 16px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .rec-section ul {{
            list-style: none;
            padding-left: 0;
        }}

        .rec-section li {{
            padding: 8px 0 8px 25px;
            position: relative;
            line-height: 1.5;
        }}

        .rec-section li:before {{
            content: "→";
            position: absolute;
            left: 0;
            color: #1B5E20;
            font-weight: bold;
        }}

        .athletes-section {{
            background: #fafafa;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
        }}

        .athletes-section h4 {{
            color: #1B5E20;
            font-size: 16px;
            margin-bottom: 15px;
        }}

        .athlete-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 10px;
        }}

        .athlete-item {{
            padding: 12px 15px;
            border-radius: 5px;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
        }}

        .athlete-item.critical {{
            background: #FFEBEE;
            border-left: 4px solid #C62828;
        }}

        .athlete-item.warning {{
            background: #FFF3E0;
            border-left: 4px solid #EF6C00;
        }}

        .athlete-item.caution {{
            background: #FFFDE7;
            border-left: 4px solid #F57F17;
        }}

        .emoji {{
            font-size: 18px;
        }}

        .athlete-name {{
            font-weight: 600;
        }}

        .athlete-detail {{
            color: #666;
            font-size: 12px;
        }}

        .distribution {{
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 5px;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }}

        .dist-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .interpretation-box {{
            background: #E8F5E9;
            border-left: 4px solid #4CAF50;
            padding: 15px;
            margin-top: 15px;
            border-radius: 5px;
        }}

        .interpretation-box strong {{
            color: #1B5E20;
        }}

        .execution-box {{
            background: #E3F2FD;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin-top: 15px;
            border-radius: 5px;
        }}

        .execution-box strong {{
            color: #1565C0;
        }}

        .no-flags {{
            background: #E8F5E9;
            border: 2px solid #4CAF50;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}

        .no-flags h3 {{
            color: #2E7D32;
            margin-bottom: 10px;
        }}

        .no-flags ul {{
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}

        .no-flags li {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .action-box {{
            background: #FFF9E6;
            border: 2px solid #FBC02D;
            border-radius: 8px;
            padding: 25px;
            margin: 30px 0;
        }}

        .action-box h3 {{
            color: #F57F17;
            margin-bottom: 20px;
            font-size: 20px;
        }}

        .priority-item {{
            margin-bottom: 20px;
            padding-left: 20px;
            border-left: 3px solid #FBC02D;
        }}

        .priority-item h4 {{
            color: #E65100;
            margin-bottom: 10px;
        }}

        .priority-item ul {{
            list-style: none;
            padding-left: 20px;
        }}

        .priority-item li {{
            padding: 5px 0;
            position: relative;
        }}

        .priority-item li:before {{
            content: "✓";
            position: absolute;
            left: -20px;
            color: #4CAF50;
            font-weight: bold;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}

        .note {{
            background: #E3F2FD;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="page">
        <div class="header">
            <h1>⚡ FORCE PLATE TRAINING REPORT</h1>
            <div class="header-info">
                <div><strong>Team:</strong> <span>{TEAM_NAME}</span></div>
                <div><strong>Report Date:</strong> <span>{REPORT_DATE.strftime('%B %d, %Y')}</span></div>
                <div><strong>Training Phase:</strong> <span>{TRAINING_PHASE}</span></div>
                <div><strong>Data Window:</strong> <span>{data_window}</span></div>
                <div><strong>Next Phase:</strong> <span>{NEXT_PHASE}</span></div>
                <div><strong>Total Athletes:</strong> <span>{total_athletes}</span></div>
            </div>
        </div>

        <div class="summary-box">
            <h2>📊 EXECUTIVE SUMMARY</h2>
            <p><strong>{categories_flagged} categories flagged</strong> with <strong>{total_flagged} total athletes</strong> needing intervention ({total_flagged/total_athletes*100:.0f}% of roster)</p>
            <p style="margin-top: 10px;">Recommendations based on 6 months of force plate testing data. Focus on execution-style modifications for next training phase.</p>
        </div>
"""

    # Add category cards
    for cat_num in sorted(results['categories'].keys()):
        cat_data = results['categories'][cat_num]

        html += f"""
        <div class="category-card">
            <div class="category-header">
                <h3>CATEGORY {cat_num}: {cat_data['name']}</h3>
                <p>📉 Trend: {cat_data['trend_desc']}</p>
            </div>
            <div class="category-body">
                <div class="recommendations">
                    <div class="rec-section">
                        <h4>🏋️ WEIGHT ROOM RECOMMENDATIONS:</h4>
                        <ul>
"""

        for sug in cat_data['wr_suggestions']:
            html += f"                            <li>{sug}</li>\n"

        html += """                        </ul>
                    </div>
                    <div class="rec-section">
                        <h4>⚡ FIELD RECOMMENDATIONS:</h4>
                        <ul>
"""

        for sug in cat_data['field_suggestions']:
            html += f"                            <li>{sug}</li>\n"

        html += f"""                        </ul>
                    </div>
                </div>

                <div class="athletes-section">
                    <h4>👥 ATHLETES IN THIS CATEGORY: {cat_data['count']}</h4>
                    <div class="athlete-list">
"""

        for athlete in cat_data['athletes']:
            pos_str = f"{athlete['position']} - " if athlete['position'] else ""
            detail = f"{pos_str}{athlete['severity'].title()}"

            html += f"""                        <div class="athlete-item {athlete['severity']}">
                            <span class="emoji">{athlete['emoji']}</span>
                            <div>
                                <div class="athlete-name">{athlete['name']}</div>
                                <div class="athlete-detail">{detail}</div>
                            </div>
                        </div>
"""

        html += f"""                    </div>

                    <div class="distribution">
                        <div class="dist-item">
                            <span class="emoji">🔴</span>
                            <strong>{cat_data['critical']} Critical</strong>
                        </div>
                        <div class="dist-item">
                            <span class="emoji">🟠</span>
                            <strong>{cat_data['warning']} Warning</strong>
                        </div>
                        <div class="dist-item">
                            <span class="emoji">🟡</span>
                            <strong>{cat_data['caution']} Caution</strong>
                        </div>
                    </div>
                </div>

                <div class="interpretation-box">
                    <strong>💡 INTERPRETATION:</strong> {cat_data['interpretation']}
                </div>

                <div class="execution-box">
                    <strong>⚡ EXECUTION NOTE:</strong> {cat_data['execution_note']}
                </div>
            </div>
        </div>
"""

    # Categories not flagged
    all_cats = set(range(1, 8))
    flagged_cats = set(results['categories'].keys())
    normal_cats = all_cats - flagged_cats

    if normal_cats:
        html += """
        <div class="no-flags">
            <h3>✅ CATEGORIES NOT FLAGGED (All athletes within normal range)</h3>
            <ul>
"""
        for cat_num in sorted(normal_cats):
            html += f"""                <li><span style="color: #4CAF50;">✓</span> Category {cat_num}: {DECISION_RULES[cat_num]['name']}</li>
"""
        html += """            </ul>
        </div>
"""

    # Action recommendations
    if results['categories']:
        html += f"""
        <div class="action-box">
            <h3>🎯 COACHING RECOMMENDATIONS FOR NEXT PHASE</h3>
"""

        priority_cats = sorted(results['categories'].items(), key=lambda x: x[1]['critical'], reverse=True)[:3]

        for idx, (cat_num, cat_data) in enumerate(priority_cats, 1):
            html += f"""
            <div class="priority-item">
                <h4>Priority {idx}: Category {cat_num} ({cat_data['name'].title()}) - {cat_data['critical']} CRITICAL FLAGS</h4>
                <ul>
"""
            for sug in cat_data['wr_suggestions'][:3]:
                html += f"                    <li>{sug}</li>\n"
            html += """                </ul>
            </div>
"""

        html += """        </div>
"""

    html += """
        <div class="note">
            <strong>NOTE:</strong> These recommendations can be implemented without changing planned exercises - just modify execution style, rest periods, and exercise pairing/sequencing.
        </div>

        <div class="footer">
            <p><strong>Report generated:</strong> """ + REPORT_DATE.strftime('%B %d, %Y at %I:%M %p') + """</p>
            <p><strong>Next report:</strong> End of """ + NEXT_PHASE + """</p>
            <p style="margin-top: 10px;">Questions? Contact: Sports Science Team</p>
        </div>
    </div>
</body>
</html>
"""

    return html

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("BAYLOR FOOTBALL FORCE PLATE TRAINING REPORT - REAL DATA".center(80))
    print("="*80)
    print()

    # Load and merge data
    df = load_and_merge_data()

    # Analyze
    results, df = categorize_athletes(df)

    # Generate reports
    text_report = generate_text_report(results, df)
    html_report = generate_html_report(results, df)

    # Save reports
    print("\nSaving reports...")

    with open('Baylor_Training_Report_REAL.txt', 'w', encoding='utf-8') as f:
        f.write(text_report)
    print("✓ Text report saved: Baylor_Training_Report_REAL.txt")

    with open('Baylor_Training_Report_REAL.html', 'w', encoding='utf-8') as f:
        f.write(html_report)
    print("✓ HTML report saved: Baylor_Training_Report_REAL.html")

    print("\n" + "="*80)
    print("REAL DATA REPORT COMPLETE!".center(80))
    print("="*80)
    print("\nNext steps:")
    print("1. Open 'Baylor_Training_Report_REAL.html' in your browser")
    print("2. Review the categorized athletes and recommendations")
    print("3. Share with your colleague!")
    print("="*80)
