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
    'red': 2.0,
    'orange': 1.5,
    'yellow': 1.0
}

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
    """Categorize athletes based on trends"""
    results = {'categories': {}}
    athletes = df['Athlete_Name'].unique()

    for cat_num, rule in DECISION_RULES.items():
        category_athletes = []

        for athlete in athletes:
            athlete_data = df[df['Athlete_Name'] == athlete].sort_values('Date')

            if len(athlete_data) < 5:
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
                        severity, emoji = 'critical', '●'
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
                    'emoji': {'critical': '●', 'warning': '●', 'caution': '●'}[worst_severity]
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

    return results

def generate_html_report(results, df, team_name, training_phase, next_phase):
    """Generate HTML report"""

    total_athletes = df['Athlete_Name'].nunique()
    total_flagged = len(set([a['name'] for cat in results['categories'].values() for a in cat['athletes']]))
    categories_flagged = len(results['categories'])
    data_window = f"{df['Date'].min().date()} to {df['Date'].max().date()}"
    report_date = datetime.now()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Force Plate Training Report - {team_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f5f5; padding: 20px; color: #333; }}
        .page {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ border-bottom: 4px solid #1B5E20; padding-bottom: 20px; margin-bottom: 30px; }}
        .header h1 {{ color: #1B5E20; font-size: 32px; margin-bottom: 15px; }}
        .header-info {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; background: #f8f9fa; padding: 15px; border-radius: 5px; }}
        .header-info div {{ display: flex; gap: 10px; }}
        .header-info strong {{ color: #1B5E20; min-width: 150px; }}
        .summary-box {{ background: #E3F2FD; border-left: 5px solid #1976D2; padding: 20px; margin: 20px 0; border-radius: 5px; }}
        .summary-box h2 {{ color: #1976D2; font-size: 18px; margin-bottom: 10px; }}
        .category-card {{ border: 2px solid #e0e0e0; border-radius: 8px; margin: 25px 0; overflow: hidden; page-break-inside: avoid; }}
        .category-header {{ background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%); color: white; padding: 20px; }}
        .category-header h3 {{ font-size: 22px; margin-bottom: 8px; }}
        .category-header p {{ opacity: 0.9; font-size: 14px; }}
        .category-body {{ padding: 20px; }}
        .recommendations {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px; }}
        .rec-section h4 {{ color: #1B5E20; font-size: 16px; margin-bottom: 12px; }}
        .rec-section ul {{ list-style: none; padding-left: 0; }}
        .rec-section li {{ padding: 8px 0 8px 25px; position: relative; line-height: 1.5; }}
        .rec-section li:before {{ content: "→"; position: absolute; left: 0; color: #1B5E20; font-weight: bold; }}
        .athletes-section {{ background: #fafafa; padding: 20px; border-radius: 5px; margin-top: 20px; }}
        .athletes-section h4 {{ color: #1B5E20; font-size: 16px; margin-bottom: 15px; }}
        .athlete-list {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px; }}
        .athlete-item {{ padding: 12px 15px; border-radius: 5px; display: flex; align-items: center; gap: 10px; font-size: 14px; }}
        .athlete-item.critical {{ background: #FFEBEE; border-left: 4px solid #C62828; }}
        .athlete-item.warning {{ background: #FFF3E0; border-left: 4px solid #EF6C00; }}
        .athlete-item.caution {{ background: #FFFDE7; border-left: 4px solid #F57F17; }}
        .emoji {{ font-size: 18px; }}
        .athlete-name {{ font-weight: 600; }}
        .athlete-detail {{ color: #666; font-size: 12px; }}
        .distribution {{ margin-top: 15px; padding: 15px; background: white; border-radius: 5px; display: flex; gap: 20px; flex-wrap: wrap; }}
        .dist-item {{ display: flex; align-items: center; gap: 8px; }}
        .interpretation-box {{ background: #E8F5E9; border-left: 4px solid #4CAF50; padding: 15px; margin-top: 15px; border-radius: 5px; }}
        .interpretation-box strong {{ color: #1B5E20; }}
        .execution-box {{ background: #E3F2FD; border-left: 4px solid #2196F3; padding: 15px; margin-top: 15px; border-radius: 5px; }}
        .execution-box strong {{ color: #1565C0; }}
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

        <div class="summary-box">
            <h2>EXECUTIVE SUMMARY</h2>
            <p><strong>{categories_flagged} categories flagged</strong> with <strong>{total_flagged} total athletes</strong> needing intervention ({total_flagged/total_athletes*100:.0f}% of roster)</p>
            <p style="margin-top: 10px;">Recommendations based on force plate testing data. Focus on execution-style modifications for next training phase.</p>
        </div>
"""

    # Add category cards
    for cat_num in sorted(results['categories'].keys()):
        cat_data = results['categories'][cat_num]

        html += f"""
        <div class="category-card">
            <div class="category-header">
                <h3>CATEGORY {cat_num}: {cat_data['name']}</h3>
                <p>Trend: {cat_data['trend_desc']}</p>
            </div>
            <div class="category-body">
                <div class="recommendations">
                    <div class="rec-section">
                        <h4>WEIGHT ROOM RECOMMENDATIONS:</h4>
                        <ul>
"""

        for sug in cat_data['wr_suggestions']:
            html += f"                            <li>{sug}</li>\n"

        html += """                        </ul>
                    </div>
                    <div class="rec-section">
                        <h4>FIELD RECOMMENDATIONS:</h4>
                        <ul>
"""

        for sug in cat_data['field_suggestions']:
            html += f"                            <li>{sug}</li>\n"

        html += f"""                        </ul>
                    </div>
                </div>

                <div class="athletes-section">
                    <h4>ATHLETES IN THIS CATEGORY: {cat_data['count']}</h4>
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
                        <div class="dist-item"><strong>{cat_data['critical']} Critical</strong></div>
                        <div class="dist-item"><strong>{cat_data['warning']} Warning</strong></div>
                        <div class="dist-item"><strong>{cat_data['caution']} Caution</strong></div>
                    </div>
                </div>

                <div class="interpretation-box">
                    <strong>INTERPRETATION:</strong> {cat_data['interpretation']}
                </div>

                <div class="execution-box">
                    <strong>EXECUTION NOTE:</strong> {cat_data['execution_note']}
                </div>
            </div>
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
    """Generate text report"""

    total_athletes = df['Athlete_Name'].nunique()
    total_flagged = len(set([a['name'] for cat in results['categories'].values() for a in cat['athletes']]))
    categories_flagged = len(results['categories'])

    report = []
    report.append("="*80)
    report.append("FORCE PLATE TRAINING REPORT".center(80))
    report.append("="*80)
    report.append(f"\nTeam: {team_name}")
    report.append(f"Report Date: {datetime.now().strftime('%B %d, %Y')}")
    report.append(f"Training Phase: {training_phase}")
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
        report.append(f"Trend: {cat_data['trend_desc']}")

        report.append("\nWEIGHT ROOM RECOMMENDATIONS:")
        for suggestion in cat_data['wr_suggestions']:
            report.append(f"  • {suggestion}")

        report.append("\nFIELD RECOMMENDATIONS:")
        for suggestion in cat_data['field_suggestions']:
            report.append(f"  • {suggestion}")

        report.append(f"\nATHLETES IN THIS CATEGORY: {cat_data['count']}")
        for athlete in cat_data['athletes']:
            pos_str = f", {athlete['position']}" if athlete['position'] else ""
            report.append(f"  {athlete['emoji']} {athlete['name']}{pos_str} - {athlete['severity'].title()}")

        report.append(f"\n  Distribution: {cat_data['critical']} Critical | {cat_data['warning']} Warning | {cat_data['caution']} Caution")
        report.append(f"\nINTERPRETATION: {cat_data['interpretation']}")
        report.append(f"\nEXECUTION NOTE: {cat_data['execution_note']}")
        report.append("")

    report.append("\n" + "="*80)
    report.append("END OF REPORT".center(80))
    report.append("="*80)

    return "\n".join(report)

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
                total_flagged = len(set([a['name'] for cat in results['categories'].values() for a in cat['athletes']]))
                st.success(f"Found {len(results['categories'])} categories with {total_flagged} athletes flagged")

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
                st.info("PDF export requires additional setup. Use browser's Print to PDF feature from the HTML report.")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px;'>
        <p>Force Plate Training Report System | Baylor University Athletics</p>
        <p>Report Generation v1.0 | November 2024</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
