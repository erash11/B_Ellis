"""
Baylor Football Force Plate Training Report - DEMO VERSION
Generates realistic sample data and creates both text and HTML reports
Perfect for demonstration purposes
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
MONTHS_TO_INCLUDE = 3

DECISION_RULES = {
    1: {
        'name': 'MAXIMAL STRENGTH CAPACITY',
        'trend_desc': 'IMTP Peak Force and Net Peak Vertical Force declining',
        'metrics': ['IMTP_Peak_Force', 'Net_Peak_Vertical_Force'],
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
        'interpretation': 'Large group showing strength decline. Consider making cluster sets and extended rest a phase emphasis for these athletes. Multiple interventions needed given the number of critical flags.',
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
        'interpretation': 'Moderate group needing RFD work. Consider contrast training emphasis in next phase for these athletes.',
        'execution_note': 'If you planned trap bar deadlifts, pair them with vertical jumps in a superset. Still the same movements, just executed as contrasts.'
    },
    3: {
        'name': 'POWER OUTPUT',
        'trend_desc': 'Peak Power declining',
        'metrics': ['Peak_Power'],
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
        'interpretation': 'Power output declining across multiple athletes. Focus on moving submaximal loads with maximal intent.',
        'execution_note': 'Focus on moving submaximal loads with maximal intent. Use cluster sets for Olympic lifts.'
    },
    4: {
        'name': 'SSC EFFICIENCY',
        'trend_desc': 'RSI-modified and Eccentric Braking RFD declining',
        'metrics': ['RSI_mod', 'Eccentric_Braking_RFD'],
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
        'trend_desc': 'Eccentric braking force and RFD declining',
        'metrics': ['Eccentric_Mean_Braking_Force'],
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
        'interpretation': 'Injury risk concern. Prioritize eccentric strength development. Add tempo work or reverse bands.',
        'execution_note': 'If doing safety bar squats, add a 5-count down. Or use reverse bands. We\'ve done this before.'
    },
    6: {
        'name': 'TECHNICAL / COORDINATION',
        'trend_desc': 'Contraction Time and Time to Peak Force increasing',
        'metrics': ['Contraction_Time', 'Time_to_Peak_Force'],
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
        'metrics': ['LR_Force_Asymmetry'],
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
        'interpretation': 'Limb imbalances requiring attention. Address through unilateral training.',
        'execution_note': 'If squats are programmed, replace with split squats. Address the imbalance through exercise selection.'
    }
}

SEVERITY_THRESHOLDS = {
    'red': 2.0,      # >2× SWC
    'orange': 1.5,   # 1.5-2× SWC
    'yellow': 1.0    # 1-1.5× SWC
}

# ============================================================================
# SAMPLE DATA GENERATION
# ============================================================================

def generate_realistic_data(num_athletes=45, num_tests=20):
    """Generate realistic force plate data for demonstration"""
    print("Generating realistic force plate data...")

    np.random.seed(42)

    # Realistic athlete names
    first_names = ['James', 'Michael', 'Robert', 'David', 'William', 'Richard', 'Joseph', 'Thomas', 'Charles', 'Daniel',
                   'Matthew', 'Anthony', 'Mark', 'Donald', 'Steven', 'Paul', 'Andrew', 'Joshua', 'Kenneth', 'Kevin',
                   'Brian', 'George', 'Timothy', 'Ronald', 'Edward', 'Jason', 'Jeffrey', 'Ryan', 'Jacob', 'Gary',
                   'Nicholas', 'Eric', 'Jonathan', 'Stephen', 'Larry', 'Justin', 'Scott', 'Brandon', 'Benjamin', 'Samuel',
                   'Raymond', 'Gregory', 'Alexander', 'Patrick', 'Frank']

    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                  'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
                  'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
                  'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
                  'Green', 'Adams', 'Nelson', 'Baker', 'Hall']

    positions = {
        'WR': 8, 'RB': 5, 'TE': 4, 'QB': 3,  # Offense skill
        'OL': 10,  # Offensive line
        'DL': 8, 'LB': 7, 'DB': 10  # Defense
    }

    # Generate athlete roster
    athletes = []
    numbers = list(range(1, 100))
    np.random.shuffle(numbers)

    idx = 0
    for position, count in positions.items():
        for _ in range(count):
            if idx >= num_athletes:
                break
            athletes.append({
                'name': f"{first_names[idx % len(first_names)]} {last_names[idx % len(last_names)]}",
                'number': numbers[idx],
                'position': position
            })
            idx += 1

    # Generate test dates (weekly tests over the past 5 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=150)
    dates = pd.date_range(start=start_date, end=end_date, freq='W')[:num_tests]

    # Position-based baseline values
    baselines = {
        'QB': {'force': 2800, 'power': 4500, 'size_factor': 0.9},
        'WR': {'force': 2600, 'power': 4800, 'size_factor': 0.85},
        'RB': {'force': 3200, 'power': 5200, 'size_factor': 1.0},
        'TE': {'force': 3400, 'power': 5000, 'size_factor': 1.1},
        'OL': {'force': 3800, 'power': 5500, 'size_factor': 1.3},
        'DL': {'force': 3600, 'power': 5300, 'size_factor': 1.25},
        'LB': {'force': 3300, 'power': 5100, 'size_factor': 1.05},
        'DB': {'force': 2700, 'power': 4700, 'size_factor': 0.88}
    }

    # Generate data
    data = []
    for athlete in athletes:
        baseline = baselines[athlete['position']]

        # Determine if athlete will show decline (40% of athletes)
        shows_decline = np.random.random() < 0.40
        decline_severity = np.random.choice(['critical', 'warning', 'caution'], p=[0.3, 0.4, 0.3]) if shows_decline else None

        # Which categories to decline in (if applicable)
        decline_categories = []
        if shows_decline:
            num_categories = np.random.choice([1, 2], p=[0.7, 0.3])
            decline_categories = np.random.choice([1, 2, 3, 4, 5], size=num_categories, replace=False)

        for test_num, date in enumerate(dates):
            # Progress factor (0 at start, 1 at end)
            progress = test_num / len(dates)

            # Calculate trend factors
            if shows_decline and decline_severity:
                if decline_severity == 'critical':
                    trend_factor = 1.0 - (progress * 0.25)  # 25% decline
                elif decline_severity == 'warning':
                    trend_factor = 1.0 - (progress * 0.15)  # 15% decline
                else:
                    trend_factor = 1.0 - (progress * 0.08)  # 8% decline
            else:
                # Normal variation
                trend_factor = 1.0 + np.random.normal(0, 0.02)

            # Apply decline to specific categories
            cat1_factor = trend_factor if 1 in decline_categories else 1.0 + np.random.normal(0, 0.03)
            cat2_factor = trend_factor if 2 in decline_categories else 1.0 + np.random.normal(0, 0.03)
            cat3_factor = trend_factor if 3 in decline_categories else 1.0 + np.random.normal(0, 0.03)
            cat4_factor = trend_factor if 4 in decline_categories else 1.0 + np.random.normal(0, 0.03)
            cat5_factor = trend_factor if 5 in decline_categories else 1.0 + np.random.normal(0, 0.03)

            # Generate metrics
            data.append({
                'Athlete_Name': athlete['name'],
                'Date': date,
                'Number': athlete['number'],
                'Position': athlete['position'],
                'IMTP_Peak_Force': np.random.normal(baseline['force'], 150) * cat1_factor,
                'Net_Peak_Vertical_Force': np.random.normal(baseline['force'] * 0.95, 150) * cat1_factor,
                'IMTP_Force_50ms': np.random.normal(baseline['force'] * 0.30, 50) * cat2_factor,
                'IMTP_Force_100ms': np.random.normal(baseline['force'] * 0.50, 80) * cat2_factor,
                'IMTP_Force_200ms': np.random.normal(baseline['force'] * 0.75, 100) * cat2_factor,
                'Peak_Power': np.random.normal(baseline['power'], 300) * cat3_factor,
                'RSI_mod': np.random.normal(0.55, 0.08) * cat4_factor,
                'Eccentric_Braking_RFD': np.random.normal(6000, 600) * cat4_factor,
                'Eccentric_Mean_Braking_Force': np.random.normal(2400, 250) * cat5_factor,
                'Eccentric_RFD': np.random.normal(4500, 450) * cat5_factor,
                'LR_Force_Asymmetry': abs(np.random.normal(5, 4)),
                'Contraction_Time': np.random.normal(0.65, 0.08),
                'Time_to_Peak_Force': np.random.normal(0.3, 0.05)
            })

    df = pd.DataFrame(data)
    print(f"✓ Generated {len(data)} test records for {num_athletes} athletes")
    return df

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
                pos = athlete_data['Position'].iloc[-1]
                num = athlete_data['Number'].iloc[-1]

                category_athletes.append({
                    'name': athlete,
                    'number': num,
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
            report.append(
                f"  {athlete['emoji']} {athlete['name']} "
                f"(#{athlete['number']}, {athlete['position']}) - {athlete['severity'].title()}"
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
            <p style="margin-top: 10px;">Primary concern: Performance decline detected across multiple categories. Recommend phase-wide adjustments to execution style and rest periods.</p>
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
            detail = f"#{athlete['number']}, {athlete['position']} - {athlete['severity'].title()}"

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
    print("BAYLOR FOOTBALL FORCE PLATE TRAINING REPORT - DEMO VERSION".center(80))
    print("="*80)
    print()

    # Generate data
    df = generate_realistic_data(num_athletes=45, num_tests=20)

    # Analyze
    results, df = categorize_athletes(df)

    # Generate reports
    text_report = generate_text_report(results, df)
    html_report = generate_html_report(results, df)

    # Save reports
    print("\nSaving reports...")

    with open('Baylor_Training_Report_DEMO.txt', 'w', encoding='utf-8') as f:
        f.write(text_report)
    print("✓ Text report saved: Baylor_Training_Report_DEMO.txt")

    with open('Baylor_Training_Report_DEMO.html', 'w', encoding='utf-8') as f:
        f.write(html_report)
    print("✓ HTML report saved: Baylor_Training_Report_DEMO.html")

    print("\n" + "="*80)
    print("DEMO COMPLETE!".center(80))
    print("="*80)
    print("\nNext steps:")
    print("1. Open 'Baylor_Training_Report_DEMO.html' in your browser")
    print("2. Review the categorized athletes and recommendations")
    print("3. Show your colleague the working prototype!")
    print("\nTo use real data:")
    print("- Place your CSV file in this directory")
    print("- Update the scripts to load your actual data")
    print("- The column mapping guide is in 'data_mapping_template.md'")
    print("="*80)
