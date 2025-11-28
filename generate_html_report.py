"""
Baylor Football Force Plate Training Report - HTML Generator
Matches the Training_Report_Mockup.html design
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Load processed data
df = pd.read_csv('/home/claude/force_plate_data_processed.csv')
df['Date'] = pd.to_datetime(df['Date'])

# ============================================================================
# DATE FILTERING - ADJUST THESE TO CHANGE REPORT TIMEFRAME
# ============================================================================

# Option A: Use last N months of data
MONTHS_TO_INCLUDE = 3  # Change this number (1-12)
cutoff_date = datetime.now() - timedelta(days=MONTHS_TO_INCLUDE * 30)
df = df[df['Date'] >= cutoff_date]

# Option B: Specific date range (comment out Option A and uncomment this)
# START_DATE = '2025-09-01'  # YYYY-MM-DD format
# END_DATE = '2025-11-24'    # YYYY-MM-DD format
# df = df[(df['Date'] >= START_DATE) & (df['Date'] <= END_DATE)]

# Option C: Only use data from current training phase (comment out Option A)
# PHASE_START_DATE = '2025-09-01'  # When current phase started
# df = df[df['Date'] >= PHASE_START_DATE]

# ============================================================================

# Configuration
REPORT_DATE = datetime.now()
TEAM_NAME = "Baylor Football"
TRAINING_PHASE = "Fall Training Block"
DATA_WINDOW = f"{MONTHS_TO_INCLUDE}-month period ({df['Date'].min().date()} to {df['Date'].max().date()})"
NEXT_PHASE = "Winter Preparation Phase"
TOTAL_ATHLETES = df['Athlete_Name'].nunique()

# Decision Rules (matching mockup structure)
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
        'interpretation': 'Large group showing strength decline. Consider making cluster sets and extended rest a phase emphasis for these athletes. Multiple interventions needed given the number of critical flags.'
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
        'interpretation': 'Moderate group needing RFD work. Consider contrast training emphasis in next phase for these athletes.'
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
        'interpretation': 'Power output declining across multiple athletes. Focus on moving submaximal loads with maximal intent.'
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
        'interpretation': 'Stretch-shortening cycle efficiency compromised. Emphasize quick ground contacts and reactive training.'
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
        'interpretation': 'Injury risk concern. Prioritize eccentric strength development. Add tempo work or reverse bands.'
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
        'interpretation': 'Movement efficiency declining. Reduce intensity and focus on movement quality.'
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
        'interpretation': 'Limb imbalances requiring attention. Address through unilateral training.'
    }
}

def calculate_swc(data):
    return 0.2 * np.std(data)

def classify_severity(deviation, swc):
    abs_dev = abs(deviation)
    if abs_dev > 2 * swc:
        return 'critical', '🔴'
    elif abs_dev > 1.5 * swc:
        return 'warning', '🟠'
    elif abs_dev > 1 * swc:
        return 'caution', '🟡'
    return 'normal', '🟢'

# Analyze athletes
print("Analyzing athlete data...")
results = {'categories': {}}
athletes = df['Athlete_Name'].unique()

for cat_num, rule in DECISION_RULES.items():
    category_athletes = []
    
    for athlete in athletes:
        athlete_data = df[df['Athlete_Name'] == athlete].sort_values('Date')
        
        if len(athlete_data) < 4:
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
            
            # Baseline calculation method:
            # Option A: Use first 60% of available data as baseline, last 40% as current
            split = int(len(metric_data) * 0.6)
            baseline = metric_data.iloc[:split]
            current = metric_data.iloc[-1]
            
            # Option B: Use first half as baseline, compare to recent average
            # split = len(metric_data) // 2
            # baseline = metric_data.iloc[:split]
            # current = metric_data.iloc[split:].mean()  # Average of recent tests
            
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
            pos = athlete_data['Position'].iloc[-1] if 'Position' in athlete_data.columns else ''
            # Get jersey number if available
            number = ''
            category_athletes.append({
                'name': athlete,
                'number': number,
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
            'interpretation': rule['interpretation']
        }

total_flagged = len(set([a['name'] for cat in results['categories'].values() for a in cat['athletes']]))
categories_flagged = len(results['categories'])

print(f"Analysis complete: {categories_flagged} categories flagged, {total_flagged} athletes")

# Generate HTML Report
print("Generating HTML report...")

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
                <div><strong>Data Window:</strong> <span>{DATA_WINDOW}</span></div>
                <div><strong>Next Phase:</strong> <span>{NEXT_PHASE}</span></div>
                <div><strong>Total Athletes:</strong> <span>{TOTAL_ATHLETES}</span></div>
            </div>
        </div>
        
        <div class="summary-box">
            <h2>📊 EXECUTIVE SUMMARY</h2>
            <p><strong>{categories_flagged} categories flagged</strong> with <strong>{total_flagged} total athletes</strong> needing intervention ({total_flagged/TOTAL_ATHLETES*100:.0f}% of roster)</p>
            <p style="margin-top: 10px;">Primary concern: Widespread performance decline across multiple categories. Recommend phase-wide adjustments to execution style and rest periods.</p>
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
    
    for athlete in cat_data['athletes'][:20]:  # Show first 20
        detail = f"#{athlete['number']}, " if athlete['number'] else ""
        detail += str(athlete['position']) if athlete['position'] and not pd.isna(athlete['position']) else ""
        detail += f" - {athlete['severity'].title()}"
        
        html += f"""                        <div class="athlete-item {athlete['severity']}">
                            <span class="emoji">{athlete['emoji']}</span>
                            <div>
                                <div class="athlete-name">{athlete['name']}</div>
                                <div class="athlete-detail">{detail}</div>
                            </div>
                        </div>
"""
    
    if len(cat_data['athletes']) > 20:
        html += f"""                        <div class="athlete-item" style="grid-column: 1 / -1; background: #f0f0f0; border: none; justify-content: center;">
                            <em>... and {len(cat_data['athletes'])-20} more athletes</em>
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

# Prioritize by critical count
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

# Save HTML report
output_path = '/mnt/user-data/outputs/Baylor_Training_Report_HTML.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ HTML report generated: {output_path}")
print(f"\nReport Summary:")
print(f"  Categories Flagged: {categories_flagged}")
print(f"  Athletes Flagged: {total_flagged}")
print(f"  File Size: {len(html):,} bytes")
