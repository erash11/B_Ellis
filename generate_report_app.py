"""
Force Plate Training Report Generator - Streamlit App
Easy-to-use web interface for coaches to generate training reports
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io
import base64
from typing import Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Force Plate Report Generator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONFIGURATION & DECISION RULES
# ============================================================================

DECISION_RULES = {
    1: {
        'name': 'MAXIMAL STRENGTH CAPACITY',
        'short_name': 'Maximal Strength',
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
        'short_name': 'Explosive/RFD',
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
        'short_name': 'Power Output',
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
        'short_name': 'SSC Efficiency',
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
        'short_name': 'Eccentric Control',
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
        'short_name': 'Technical',
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
        'short_name': 'Asymmetry',
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
    'red': 2.0,
    'orange': 1.5,
    'yellow': 1.0
}

# Position group mappings
POSITION_GROUPS = {
    'Skill': ['WR', 'CB', 'S', 'RB'],
    'Mid': ['QB', 'TE', 'OLB', 'MLB', 'SPEC'],
    'Big': ['OL', 'DL']
}

def get_position_group(position):
    """Map position to position group"""
    if pd.isna(position) or position == '':
        return 'Unknown'

    position = str(position).upper().strip()
    for group, positions in POSITION_GROUPS.items():
        if position in positions:
            return group
    return 'Unknown'

# ============================================================================
# DATA PROCESSING FUNCTIONS
# ============================================================================

def load_and_validate_files(cmj_file, imtp_file, roster_file):
    """Load and validate uploaded files"""
    try:
        # Load CMJ data
        cmj = pd.read_csv(cmj_file)
        cmj['Date'] = pd.to_datetime(cmj['Date'])
        cmj.columns = cmj.columns.str.strip()

        # Load IMTP data
        imtp = pd.read_csv(imtp_file)
        imtp['Date'] = pd.to_datetime(imtp['Date'])
        imtp.columns = imtp.columns.str.strip()

        # Load roster
        try:
            roster = pd.read_excel(roster_file)
        except:
            roster = pd.read_csv(roster_file)

        return cmj, imtp, roster, None

    except Exception as e:
        return None, None, None, str(e)

def process_data(cmj, imtp, roster):
    """Process and merge data files"""

    # Rename columns
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

    # Process IMTP time to milliseconds
    imtp_renamed['IMTP_Time_to_Peak_Force'] = imtp_renamed['IMTP_Time_to_Peak_Force'] * 1000

    # Process asymmetry
    def extract_asymmetry(val):
        if pd.isna(val):
            return np.nan
        if isinstance(val, (int, float)):
            return abs(float(val))
        val_str = str(val).strip()
        try:
            num = float(val_str.split()[0])
            return abs(num)
        except:
            return np.nan

    imtp_renamed['IMTP_Asymmetry'] = imtp_renamed['IMTP_Asymmetry_Raw'].apply(extract_asymmetry)

    # Select columns
    cmj_cols = ['Athlete_Name', 'Date', 'CMJ_Peak_Power', 'CMJ_RSI_modified',
                'CMJ_Contraction_Time', 'CMJ_Eccentric_Mean_Braking_Force',
                'CMJ_Eccentric_Braking_RFD', 'CMJ_Jump_Height']

    imtp_cols = ['Athlete_Name', 'Date', 'IMTP_Peak_Force', 'IMTP_Net_Peak_Force',
                 'IMTP_Force_50ms', 'IMTP_Force_100ms', 'IMTP_Force_200ms',
                 'IMTP_Asymmetry', 'IMTP_Time_to_Peak_Force']

    cmj_clean = cmj_renamed[cmj_cols].copy()
    imtp_clean = imtp_renamed[imtp_cols].copy()

    # Merge
    merged = pd.merge(cmj_clean, imtp_clean, on=['Athlete_Name', 'Date'], how='outer')
    merged = pd.merge(merged, roster.rename(columns={'Name': 'Athlete_Name'}),
                     on='Athlete_Name', how='left')

    merged = merged.sort_values(['Athlete_Name', 'Date']).reset_index(drop=True)

    return merged

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
    """Categorize athletes based on trends - organized by athlete rather than category"""
    athlete_results = {}
    athletes = df['Athlete_Name'].unique()

    # Check each athlete against all categories
    for athlete in athletes:
        athlete_data = df[df['Athlete_Name'] == athlete].sort_values('Date')

        if len(athlete_data) < 5:
            continue

        # Get athlete position info
        position = athlete_data['Position'].iloc[-1] if 'Position' in athlete_data.columns and pd.notna(athlete_data['Position'].iloc[-1]) else ''
        position_group = get_position_group(position)

        flagged_categories = []

        # Check each category
        for cat_num, rule in DECISION_RULES.items():
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
                flagged_categories.append({
                    'cat_num': cat_num,
                    'name': rule['name'],
                    'short_name': rule['short_name'],
                    'severity': worst_severity,
                    'emoji': {'critical': '🔴', 'warning': '🟠', 'caution': '🟡'}[worst_severity],
                    'wr_suggestions': rule['wr_suggestions'],
                    'field_suggestions': rule['field_suggestions'],
                    'interpretation': rule['interpretation'],
                    'execution_note': rule['execution_note']
                })

        # Only add athlete if they have flagged categories
        if flagged_categories:
            # Sort categories by severity (most severe first)
            flagged_categories.sort(key=lambda x: {'critical': 0, 'warning': 1, 'caution': 2}[x['severity']])

            athlete_results[athlete] = {
                'position': position,
                'position_group': position_group,
                'flagged_categories': flagged_categories
            }

    # Group athletes by position group
    position_group_results = {
        'Skill': [],
        'Mid': [],
        'Big': [],
        'Unknown': []
    }

    for athlete, data in athlete_results.items():
        position_group_results[data['position_group']].append({
            'name': athlete,
            'position': data['position'],
            'flagged_categories': data['flagged_categories']
        })

    # Sort athletes within each group by name
    for group in position_group_results:
        position_group_results[group].sort(key=lambda x: x['name'])

    return {
        'athletes': athlete_results,
        'position_groups': position_group_results
    }

def generate_html_report(results, df, team_name, training_phase, next_phase):
    """Generate HTML report grouped by position"""

    total_athletes = df['Athlete_Name'].nunique()
    total_flagged = len(results['athletes'])
    data_window = f"{df['Date'].min().date()} to {df['Date'].max().date()}"
    report_date = datetime.now()

    # Count unique categories flagged and athletes per category
    category_counts = {}
    for athlete_data in results['athletes'].values():
        for cat in athlete_data['flagged_categories']:
            cat_num = cat['cat_num']
            if cat_num not in category_counts:
                category_counts[cat_num] = 0
            category_counts[cat_num] += 1
    categories_flagged = len(category_counts)

    # Calculate stats per position group
    position_group_stats = {}
    for group_name in ['Skill', 'Mid', 'Big']:
        # Total athletes in this position group in the dataset
        group_positions = POSITION_GROUPS[group_name]
        total_in_group = df[df['Position'].isin(group_positions)]['Athlete_Name'].nunique()

        # Flagged athletes in this position group
        flagged_in_group = len(results['position_groups'][group_name])

        # Category breakdown for this position group
        group_category_counts = {}
        for athlete in results['position_groups'][group_name]:
            for cat in athlete['flagged_categories']:
                cat_num = cat['cat_num']
                if cat_num not in group_category_counts:
                    group_category_counts[cat_num] = 0
                group_category_counts[cat_num] += 1

        position_group_stats[group_name] = {
            'total': total_in_group,
            'flagged': flagged_in_group,
            'category_counts': group_category_counts
        }

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Force Plate Training Report - {team_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; padding: 20px; color: #333; }}
        .page {{ max-width: 1400px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ border-bottom: 4px solid #1B5E20; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #1B5E20; font-size: 32px; margin-bottom: 15px; }}
        .header-info {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; background: #f8f9fa; padding: 15px; border-radius: 5px; }}
        .header-info div {{ display: flex; gap: 10px; }}
        .header-info strong {{ color: #1B5E20; min-width: 150px; }}
        .summary-box {{ background: #E3F2FD; border-left: 5px solid #1976D2; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .summary-box h2 {{ color: #1976D2; font-size: 18px; margin-bottom: 10px; }}
        .summary-box h3 {{ color: #1976D2; font-size: 16px; margin: 15px 0 10px 0; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px; }}
        .summary-card {{ background: white; border: 2px solid #1976D2; border-radius: 8px; padding: 15px; }}
        .summary-card h3 {{ color: #1B5E20; font-size: 16px; margin: 0 0 10px 0; border-bottom: 2px solid #1B5E20; padding-bottom: 5px; }}
        .summary-stat {{ display: flex; justify-content: space-between; padding: 5px 0; font-size: 14px; }}
        .summary-stat strong {{ color: #333; }}
        .category-breakdown {{ margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd; font-size: 13px; }}
        .category-breakdown-item {{ padding: 3px 0; }}

        /* Position group styling */
        .position-group {{ border: 2px solid #e0e0e0; border-radius: 8px; margin: 25px 0; overflow: hidden; page-break-inside: avoid; }}
        .position-header {{ background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%); color: white; padding: 15px 20px; }}
        .position-header h3 {{ font-size: 20px; margin: 0; }}
        .position-summary {{ background: #E3F2FD; border-left: 5px solid #1976D2; padding: 15px 20px; margin: 0; }}
        .position-summary-stats {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 10px; }}
        .position-summary-stat {{ display: flex; justify-content: space-between; padding: 5px 0; font-size: 14px; }}
        .position-summary-stat strong {{ color: #333; }}
        .position-summary-categories {{ margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.3); }}
        .position-summary-categories strong {{ display: block; margin-bottom: 5px; font-size: 13px; }}
        .position-summary-cat-item {{ font-size: 12px; padding: 2px 0; }}
        .position-body {{ padding: 20px; }}

        /* Athlete row styling */
        .athlete-row {{ display: grid; grid-template-columns: 200px 1fr; gap: 15px; padding: 12px 0; border-bottom: 1px solid #e0e0e0; align-items: start; }}
        .athlete-row:last-child {{ border-bottom: none; }}
        .athlete-info {{ display: flex; flex-direction: column; }}
        .athlete-name {{ font-weight: 600; font-size: 15px; color: #1B5E20; }}
        .athlete-position {{ font-size: 13px; color: #666; margin-top: 2px; }}

        /* Category badges */
        .category-badges {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }}
        .category-badge {{ display: inline-flex; align-items: center; padding: 5px 10px; border-radius: 3px; font-size: 12px; white-space: nowrap; }}
        .category-badge.critical {{ background: #FFEBEE; border-left: 3px solid #C62828; color: #C62828; font-weight: 500; }}
        .category-badge.warning {{ background: #FFF3E0; border-left: 3px solid #EF6C00; color: #EF6C00; font-weight: 500; }}
        .category-badge.caution {{ background: #FFFDE7; border-left: 3px solid #F57F17; color: #F57F17; font-weight: 500; }}
        .category-name {{ font-weight: 500; }}

        /* Legend */
        .legend {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .legend h4 {{ font-size: 14px; margin-bottom: 10px; color: #1B5E20; }}
        .legend-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 8px; font-size: 13px; }}
        .legend-item {{ padding: 5px 0; }}
        .legend-num {{ font-weight: 600; color: #1B5E20; display: inline-block; min-width: 20px; }}

        /* Training recommendations section */
        .recommendations-section {{ margin: 40px 0; }}
        .recommendations-title {{ color: #1B5E20; font-size: 24px; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 3px solid #1B5E20; }}
        .category-recommendations {{ border: 2px solid #e0e0e0; border-radius: 8px; margin: 20px 0; overflow: hidden; page-break-inside: avoid; }}
        .category-rec-header {{ background: linear-gradient(135deg, #1565C0 0%, #1976D2 100%); color: white; padding: 12px 20px; }}
        .category-rec-header h4 {{ font-size: 16px; margin: 0; }}
        .category-rec-body {{ padding: 20px; }}
        .rec-columns {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
        .rec-column h5 {{ color: #1B5E20; font-size: 14px; margin-bottom: 10px; }}
        .rec-column ul {{ list-style: none; padding-left: 0; margin: 0; }}
        .rec-column li {{ padding: 6px 0 6px 20px; position: relative; line-height: 1.4; font-size: 13px; }}
        .rec-column li:before {{ content: "→"; position: absolute; left: 0; color: #1B5E20; font-weight: bold; }}
        .rec-note {{ background: #E8F5E9; padding: 12px; border-left: 3px solid #4CAF50; margin-top: 15px; border-radius: 3px; font-size: 13px; }}
        .rec-note strong {{ color: #1B5E20; }}

        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #e0e0e0; text-align: center; color: #666; font-size: 14px; }}
        @media print {{ .page {{ box-shadow: none; }} }}
    </style>
</head>
<body>
    <div class="page">
        <div class="header">
            <h1>FORCE PLATE TRAINING REPORT</h1>
            <div class="header-info">
                <div><strong>Team:</strong> <span>{team_name}</span></div>
                <div><strong>Report Date:</strong> <span>{report_date.strftime('%B %d, %Y')}</span></div>
                <div><strong>Training Phase:</strong> <span>{training_phase}</span></div>
                <div><strong>Data Window:</strong> <span>{data_window}</span></div>
                <div><strong>Next Phase:</strong> <span>{next_phase}</span></div>
                <div><strong>Total Athletes:</strong> <span>{total_athletes}</span></div>
            </div>
        </div>

        <div class="legend">
            <h4>DEVELOPMENTAL CATEGORY LEGEND:</h4>
            <div class="legend-grid">
"""

    # Add category legend
    for cat_num, rule in sorted(DECISION_RULES.items()):
        html += f'                <div class="legend-item"><span class="legend-num">{cat_num}.</span> {rule["name"]}</div>\n'

    html += """            </div>
        </div>
"""

    # Add training recommendations section (moved before athlete lists)
    html += """
        <div class="recommendations-section">
            <h2 class="recommendations-title">TRAINING RECOMMENDATIONS BY CATEGORY</h2>
"""

    for cat_num in sorted(category_counts.keys()):
        rule = DECISION_RULES[cat_num]
        count = category_counts[cat_num]

        html += f"""
            <div class="category-recommendations">
                <div class="category-rec-header">
                    <h4>CATEGORY {cat_num}: {rule['name'].upper()} ({count} athletes flagged)</h4>
                </div>
                <div class="category-rec-body">
                    <div class="rec-columns">
                        <div class="rec-column">
                            <h5>WEIGHT ROOM RECOMMENDATIONS:</h5>
                            <ul>
"""

        for suggestion in rule['wr_suggestions']:
            html += f"                                <li>{suggestion}</li>\n"

        html += """                            </ul>
                        </div>
                        <div class="rec-column">
                            <h5>FIELD RECOMMENDATIONS:</h5>
                            <ul>
"""

        for suggestion in rule['field_suggestions']:
            html += f"                                <li>{suggestion}</li>\n"

        html += f"""                            </ul>
                        </div>
                    </div>
                    <div class="rec-note">
                        <strong>Interpretation:</strong> {rule['interpretation']}
                    </div>
                    <div class="rec-note" style="background: #E3F2FD; border-left-color: #2196F3;">
                        <strong>Execution Note:</strong> {rule['execution_note']}
                    </div>
                </div>
            </div>
"""

    html += """        </div>

        <h2 style="color: #1B5E20; font-size: 24px; margin: 40px 0 20px 0; padding-bottom: 10px; border-bottom: 3px solid #1B5E20;">FLAGGED ATHLETES BY POSITION</h2>
"""

    # Add position groups (moved after recommendations)
    for group_name in ['Skill', 'Mid', 'Big']:
        group_athletes = results['position_groups'][group_name]

        if not group_athletes:
            continue

        # Get position list for this group
        position_list = ', '.join(POSITION_GROUPS[group_name])
        stats = position_group_stats[group_name]
        pct = (stats['flagged'] / stats['total'] * 100) if stats['total'] > 0 else 0

        html += f"""
        <div class="position-group">
            <div class="position-header">
                <h3>{group_name.upper()} POSITIONS ({position_list})</h3>
            </div>
            <div class="position-summary">
                <div class="position-summary-stats">
                    <div class="position-summary-stat">
                        <span>Total Athletes:</span>
                        <strong>{stats['total']}</strong>
                    </div>
                    <div class="position-summary-stat">
                        <span>Athletes Flagged:</span>
                        <strong>{stats['flagged']} ({pct:.0f}%)</strong>
                    </div>
                </div>
"""

        if stats['category_counts']:
            html += """                <div class="position-summary-categories">
                    <strong>Categories Flagged in this Group:</strong>
"""
            for cat_num in sorted(stats['category_counts'].keys()):
                count = stats['category_counts'][cat_num]
                cat_name = DECISION_RULES[cat_num]['short_name']
                html += f"""                    <div class="position-summary-cat-item">• Cat {cat_num} ({cat_name}): {count} athletes</div>
"""
            html += """                </div>
"""

        html += """            </div>
            <div class="position-body">
"""

        for athlete in group_athletes:
            html += f"""                <div class="athlete-row">
                    <div class="athlete-info">
                        <div class="athlete-name">{athlete['name']}</div>
                        <div class="athlete-position">{athlete['position']}</div>
                    </div>
                    <div class="category-badges">
"""

            for cat in athlete['flagged_categories']:
                html += f"""                        <div class="category-badge {cat['severity']}">
                            <span class="category-name">{cat['short_name']}</span>
                        </div>
"""

            html += """                    </div>
                </div>
"""

        html += """            </div>
        </div>
"""

    html += f"""
        <div class="footer">
            <p><strong>Report generated:</strong> {report_date.strftime('%B %d, %Y at %I:%M %p')}</p>
            <p><strong>Next report:</strong> End of {next_phase}</p>
            <p style="margin-top: 10px;">Baylor University Athletics - Applied Performance</p>
        </div>
    </div>
</body>
</html>
"""

    return html

def generate_text_report(results, df, team_name, training_phase):
    """Generate text report grouped by position"""

    total_athletes = df['Athlete_Name'].nunique()
    total_flagged = len(results['athletes'])

    # Count unique categories and athletes per category
    category_counts = {}
    for athlete_data in results['athletes'].values():
        for cat in athlete_data['flagged_categories']:
            cat_num = cat['cat_num']
            if cat_num not in category_counts:
                category_counts[cat_num] = 0
            category_counts[cat_num] += 1
    categories_flagged = len(category_counts)

    # Calculate stats per position group
    position_group_stats = {}
    for group_name in ['Skill', 'Mid', 'Big']:
        group_positions = POSITION_GROUPS[group_name]
        total_in_group = df[df['Position'].isin(group_positions)]['Athlete_Name'].nunique()
        flagged_in_group = len(results['position_groups'][group_name])

        group_category_counts = {}
        for athlete in results['position_groups'][group_name]:
            for cat in athlete['flagged_categories']:
                cat_num = cat['cat_num']
                if cat_num not in group_category_counts:
                    group_category_counts[cat_num] = 0
                group_category_counts[cat_num] += 1

        position_group_stats[group_name] = {
            'total': total_in_group,
            'flagged': flagged_in_group,
            'category_counts': group_category_counts
        }

    report = []
    report.append("="*80)
    report.append("FORCE PLATE TRAINING REPORT".center(80))
    report.append("="*80)
    report.append(f"\nTeam: {team_name}")
    report.append(f"Report Date: {datetime.now().strftime('%B %d, %Y')}")
    report.append(f"Training Phase: {training_phase}")
    report.append(f"Data Window: {df['Date'].min().date()} to {df['Date'].max().date()}")
    report.append("-"*80)

    report.append("\n" + "="*80)
    report.append("DEVELOPMENTAL CATEGORY LEGEND".center(80))
    report.append("="*80)
    for cat_num, rule in sorted(DECISION_RULES.items()):
        report.append(f"  {cat_num}. {rule['name']}")
    report.append("")

    # Add training recommendations (before athlete lists)
    report.append("\n" + "="*80)
    report.append("TRAINING RECOMMENDATIONS BY CATEGORY".center(80))
    report.append("="*80)

    for cat_num in sorted(category_counts.keys()):
        rule = DECISION_RULES[cat_num]
        count = category_counts[cat_num]

        report.append(f"\nCATEGORY {cat_num}: {rule['name'].upper()} ({count} athletes flagged)")
        report.append("-"*80)

        report.append("\nWEIGHT ROOM RECOMMENDATIONS:")
        for suggestion in rule['wr_suggestions']:
            report.append(f"  → {suggestion}")

        report.append("\nFIELD RECOMMENDATIONS:")
        for suggestion in rule['field_suggestions']:
            report.append(f"  → {suggestion}")

        report.append(f"\nINTERPRETATION: {rule['interpretation']}")
        report.append(f"\nEXECUTION NOTE: {rule['execution_note']}")
        report.append("")

    # Add flagged athletes section (after recommendations)
    report.append("\n" + "="*80)
    report.append("FLAGGED ATHLETES BY POSITION".center(80))
    report.append("="*80)

    for group_name in ['Skill', 'Mid', 'Big']:
        group_athletes = results['position_groups'][group_name]

        if not group_athletes:
            continue

        position_list = ', '.join(POSITION_GROUPS[group_name])
        stats = position_group_stats[group_name]
        pct = (stats['flagged'] / stats['total'] * 100) if stats['total'] > 0 else 0

        report.append(f"\n{group_name.upper()} POSITIONS ({position_list})")
        report.append("-"*80)

        # Position-specific executive summary
        report.append(f"\nEXECUTIVE SUMMARY:")
        report.append(f"  Total Athletes: {stats['total']}")
        report.append(f"  Athletes Flagged: {stats['flagged']} ({pct:.0f}%)")

        if stats['category_counts']:
            report.append(f"\n  Categories Flagged in this Group:")
            for cat_num in sorted(stats['category_counts'].keys()):
                count = stats['category_counts'][cat_num]
                cat_name = DECISION_RULES[cat_num]['short_name']
                report.append(f"    • Cat {cat_num} ({cat_name}): {count} athletes")

        report.append(f"\nFLAGGED ATHLETES:")
        for athlete in group_athletes:
            report.append(f"\n  {athlete['name']} ({athlete['position']})")

            # List flagged categories (abbreviated)
            cat_strs = []
            for cat in athlete['flagged_categories']:
                cat_strs.append(f"  • {cat['short_name']} ({cat['severity'].title()})")

            for cat_str in cat_strs:
                report.append(f"    {cat_str}")

        report.append("")

    report.append("\n" + "="*80)
    report.append("END OF REPORT".center(80))
    report.append("="*80)

    return "\n".join(report)

def generate_pdf_report(html_content):
    """Convert HTML report to PDF using WeasyPrint"""
    if not WEASYPRINT_AVAILABLE:
        return None

    try:
        # Create PDF in memory
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
    except Exception as e:
        st.error(f"PDF generation error: {str(e)}")
        return None

def create_download_link(content, filename, file_type):
    """Create download link for file"""
    if file_type == 'html':
        b64 = base64.b64encode(content.encode()).decode()
        return f'<a href="data:text/html;base64,{b64}" download="{filename}">Download {filename}</a>'
    elif file_type == 'text':
        b64 = base64.b64encode(content.encode()).decode()
        return f'<a href="data:text/plain;base64,{b64}" download="{filename}">Download {filename}</a>'

# ============================================================================
# STREAMLIT APP
# ============================================================================

def main():
    # Header
    st.title("Force Plate Training Report Generator")
    st.markdown("**Baylor University Athletics - Applied Performance**")
    st.markdown("---")

    # Sidebar - Settings
    st.sidebar.header("Report Settings")

    team_name = st.sidebar.text_input("Team Name", "Baylor Football")
    training_phase = st.sidebar.text_input("Current Training Phase", "Fall Training Block")
    next_phase = st.sidebar.text_input("Next Phase", "Winter Preparation Phase")

    st.sidebar.markdown("---")
    st.sidebar.header("Data Window")

    date_window_option = st.sidebar.selectbox(
        "Select time period for analysis",
        options=["All Data", "Last 1 Month", "Last 3 Months", "Last 6 Months", "Last 12 Months", "Custom Date Range"],
        index=2  # Default to Last 3 Months
    )

    # Custom date range inputs (only shown if Custom is selected)
    start_date = None
    end_date = None
    if date_window_option == "Custom Date Range":
        col_start, col_end = st.sidebar.columns(2)
        with col_start:
            start_date = st.date_input("Start Date", value=pd.Timestamp.now() - pd.DateOffset(months=6))
        with col_end:
            end_date = st.date_input("End Date", value=pd.Timestamp.now())

    st.sidebar.markdown("---")
    st.sidebar.header("Instructions")
    st.sidebar.markdown("""
    1. Upload your three data files
    2. Select date window for analysis
    3. Click "Generate Report"
    4. Download HTML, Text, or PDF
    """)

    # Main content
    st.header("Upload Data Files")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("CMJ Data")
        cmj_file = st.file_uploader(
            "Upload CMJ Test Data",
            type=['csv'],
            help="Countermovement Jump data from ForceDecks"
        )
        if cmj_file:
            st.success(f"Uploaded: {cmj_file.name}")

    with col2:
        st.subheader("IMTP Data")
        imtp_file = st.file_uploader(
            "Upload IMTP Test Data",
            type=['csv'],
            help="Isometric Mid-Thigh Pull data from ForceDecks"
        )
        if imtp_file:
            st.success(f"Uploaded: {imtp_file.name}")

    with col3:
        st.subheader("Roster")
        roster_file = st.file_uploader(
            "Upload Roster File",
            type=['csv', 'xlsx'],
            help="Athlete roster with positions"
        )
        if roster_file:
            st.success(f"Uploaded: {roster_file.name}")

    st.markdown("---")

    # Generate button
    if st.button("Generate Report", type="primary", use_container_width=True):
        if not all([cmj_file, imtp_file, roster_file]):
            st.error("Please upload all three files before generating the report.")
        else:
            with st.spinner("Loading and validating data files..."):
                cmj, imtp, roster, error = load_and_validate_files(cmj_file, imtp_file, roster_file)

                if error:
                    st.error(f"Error loading files: {error}")
                    return

                st.success(f"Loaded CMJ: {len(cmj)} tests from {cmj['Name'].nunique()} athletes")
                st.success(f"Loaded IMTP: {len(imtp)} tests from {imtp['Name'].nunique()} athletes")
                st.success(f"Loaded Roster: {len(roster)} athletes")

            with st.spinner("Processing and merging data..."):
                merged_df = process_data(cmj, imtp, roster)
                st.success(f"Merged dataset: {len(merged_df)} tests from {merged_df['Athlete_Name'].nunique()} athletes")

            # Apply date filtering based on user selection
            with st.spinner("Applying date filter..."):
                if date_window_option == "All Data":
                    filtered_df = merged_df.copy()
                elif date_window_option == "Custom Date Range":
                    filtered_df = merged_df[
                        (merged_df['Date'] >= pd.to_datetime(start_date)) &
                        (merged_df['Date'] <= pd.to_datetime(end_date))
                    ].copy()
                else:
                    # Extract months from option (e.g., "Last 3 Months" -> 3)
                    months = int(date_window_option.split()[1])
                    cutoff_date = pd.Timestamp.now() - pd.DateOffset(months=months)
                    filtered_df = merged_df[merged_df['Date'] >= cutoff_date].copy()

                st.success(f"Date filter applied: {len(filtered_df)} tests from {filtered_df['Athlete_Name'].nunique()} athletes in selected window")

            with st.spinner("Categorizing athletes and analyzing trends..."):
                results = categorize_athletes(filtered_df)
                total_flagged = len(results['athletes'])

                # Count unique categories flagged
                all_categories = set()
                for athlete_data in results['athletes'].values():
                    for cat in athlete_data['flagged_categories']:
                        all_categories.add(cat['cat_num'])

                st.success(f"Found {len(all_categories)} categories with {total_flagged} athletes flagged")

            with st.spinner("Generating reports..."):
                html_report = generate_html_report(results, filtered_df, team_name, training_phase, next_phase)
                text_report = generate_text_report(results, filtered_df, team_name, training_phase)

            st.success("Reports generated successfully!")

            # Display report
            st.markdown("---")
            st.header("Report Preview")

            # Show HTML in iframe
            st.components.v1.html(html_report, height=600, scrolling=True)

            # Download buttons
            st.markdown("---")
            st.header("Download Reports")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.download_button(
                    label="Download HTML",
                    data=html_report,
                    file_name=f"Training_Report_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html"
                )

            with col2:
                st.download_button(
                    label="Download Text",
                    data=text_report,
                    file_name=f"Training_Report_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )

            with col3:
                if WEASYPRINT_AVAILABLE:
                    with st.spinner("Generating PDF..."):
                        pdf_data = generate_pdf_report(html_report)

                    if pdf_data:
                        st.download_button(
                            label="Download PDF",
                            data=pdf_data,
                            file_name=f"Training_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.error("PDF generation failed. Use browser's Print to PDF feature from the HTML report.")
                else:
                    st.info("PDF library not available. Use browser's Print to PDF feature from the HTML report.")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #667; font-size: 12px;'>
        <p>Force Plate Training Report System | Baylor University Athletics</p>
        <p>Report Generation v1.0 | November 2025</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
