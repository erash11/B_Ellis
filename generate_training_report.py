"""
Force Plate Training Report Generator
Based on conversation with colleague - November 20, 2024

This script generates training reports that categorize athletes and provide
execution-style recommendations (not specific exercises) based on force plate trends.
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

DECISION_RULES = {
    1: {
        'name': 'Maximal Strength Capacity',
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
        'execution_note': 'Still do your planned exercises (trap bar, safety bar, whatever), but execute them with longer rest, cluster structure, or add isometric holds.'
    },
    2: {
        'name': 'Explosive Strength / RFD',
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
        'execution_note': 'If you planned trap bar deadlifts, pair them with vertical jumps in a superset. Still the same movements, just executed as contrasts.'
    },
    3: {
        'name': 'Power Output',
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
        'execution_note': 'Focus on moving submaximal loads with maximal intent. Use cluster sets for Olympic lifts.'
    },
    4: {
        'name': 'SSC Efficiency',
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
        'execution_note': 'Emphasize quick ground contacts. Think "hot ground" mentality rather than max height.'
    },
    5: {
        'name': 'Eccentric Control & Braking',
        'metrics': ['Eccentric_Mean_Braking_Force', 'Eccentric_RFD'],
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
        'execution_note': 'If doing safety bar squats, add a 5-count down. Or use reverse bands. We\'ve done this before.'
    },
    6: {
        'name': 'Technical / Coordination',
        'metrics': ['Contraction_Time', 'Time_to_Peak_Force'],
        'trend': 'increase',  # Note: increase indicates degradation
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
        'execution_note': 'Think movement quality over load. Use wave loading to get quality reps at different intensities.'
    },
    7: {
        'name': 'Asymmetry / Limb Imbalance',
        'metrics': ['LR_Force_Asymmetry'],
        'trend': 'increase',
        'threshold_type': 'absolute',
        'threshold_value': 10,  # percent
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
        'execution_note': 'If squats are programmed, replace with split squats. Address the imbalance through exercise selection.'
    }
}

# Color coding thresholds
SEVERITY_THRESHOLDS = {
    'red': 2.0,      # >2× SWC
    'orange': 1.5,   # 1.5-2× SWC
    'yellow': 1.0    # 1-1.5× SWC
}

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def calculate_swc(baseline_series: pd.Series, method: str = '0.2sd') -> float:
    """Calculate Smallest Worthwhile Change"""
    if method == '0.2sd':
        return 0.2 * baseline_series.std()
    elif method == '5pct':
        return 0.05 * baseline_series.mean()
    return baseline_series.std() * 0.2


def get_severity(deviation: float, swc: float) -> Tuple[str, str, str]:
    """
    Classify deviation severity
    Returns: (color_code, emoji, label)
    """
    abs_dev = abs(deviation)
    
    if abs_dev > SEVERITY_THRESHOLDS['red'] * swc:
        return 'red', '🔴', 'Critical'
    elif abs_dev > SEVERITY_THRESHOLDS['orange'] * swc:
        return 'orange', '🟠', 'Warning'
    elif abs_dev > SEVERITY_THRESHOLDS['yellow'] * swc:
        return 'yellow', '🟡', 'Caution'
    else:
        return 'green', '🟢', 'Normal'


def categorize_athletes(df: pd.DataFrame, 
                        baseline_days: int = 180,
                        rolling_window_weeks: int = 4) -> Dict:
    """
    Main function to categorize athletes based on force plate trends
    
    Args:
        df: DataFrame with force plate data
        baseline_days: Number of days for baseline calculation
        rolling_window_weeks: Window for rolling average
        
    Returns:
        Dictionary with categorized athletes
    """
    results = {
        'report_date': datetime.now(),
        'data_window': f"{rolling_window_weeks}-week rolling average",
        'categories': {},
        'summary': {
            'total_athletes': 0,
            'athletes_flagged': 0,
            'categories_flagged': 0
        }
    }
    
    # Get unique athletes
    athletes = df['Athlete_Name'].unique()
    results['summary']['total_athletes'] = len(athletes)
    
    flagged_athletes = set()
    
    # For each category
    for cat_num, rule in DECISION_RULES.items():
        category_athletes = []
        
        # For each athlete
        for athlete in athletes:
            athlete_data = df[df['Athlete_Name'] == athlete].sort_values('Date')
            
            if len(athlete_data) < 5:  # Need minimum tests
                continue
            
            # Check if ALL metrics in category follow the trend
            all_metrics_flag = True
            worst_severity = 'green'
            severity_scores = {'red': 4, 'orange': 3, 'yellow': 2, 'green': 1}
            
            for metric in rule['metrics']:
                if metric not in athlete_data.columns:
                    all_metrics_flag = False
                    break
                
                # Get baseline
                cutoff_date = athlete_data['Date'].max() - timedelta(days=baseline_days)
                baseline_data = athlete_data[
                    athlete_data['Date'] >= cutoff_date
                ][metric].dropna()
                
                if len(baseline_data) < 3:
                    all_metrics_flag = False
                    break
                
                baseline_mean = baseline_data.mean()
                swc = calculate_swc(baseline_data)
                
                # Get current value (most recent)
                current_value = athlete_data[metric].iloc[-1]
                
                # Calculate deviation based on trend direction
                if rule['trend'] == 'decrease':
                    deviation = baseline_mean - current_value  # Positive = worse
                elif rule['trend'] == 'increase':
                    deviation = current_value - baseline_mean  # Positive = worse
                else:
                    all_metrics_flag = False
                    break
                
                # Check if flagged
                severity_color, _, _ = get_severity(deviation, swc)
                
                if severity_color == 'green':
                    all_metrics_flag = False
                    break
                
                # Track worst severity
                if severity_scores[severity_color] > severity_scores[worst_severity]:
                    worst_severity = severity_color
            
            # If all metrics flagged, add athlete to category
            if all_metrics_flag:
                _, emoji, label = get_severity(1, 1)  # Just to get emoji/label
                
                # Get athlete details
                athlete_row = athlete_data.iloc[-1]
                
                category_athletes.append({
                    'name': athlete,
                    'number': athlete_row.get('Number', ''),
                    'position': athlete_row.get('Position', ''),
                    'severity': worst_severity,
                    'emoji': {'red': '🔴', 'orange': '🟠', 'yellow': '🟡'}[worst_severity],
                    'label': {'red': 'Critical', 'orange': 'Warning', 'yellow': 'Caution'}[worst_severity]
                })
                
                flagged_athletes.add(athlete)
        
        # Sort by severity (red first)
        severity_order = {'red': 0, 'orange': 1, 'yellow': 2}
        category_athletes.sort(key=lambda x: severity_order[x['severity']])
        
        # Add to results if any athletes
        if category_athletes:
            results['categories'][cat_num] = {
                'name': rule['name'],
                'athletes': category_athletes,
                'count': len(category_athletes),
                'critical_count': sum(1 for a in category_athletes if a['severity'] == 'red'),
                'warning_count': sum(1 for a in category_athletes if a['severity'] == 'orange'),
                'caution_count': sum(1 for a in category_athletes if a['severity'] == 'yellow'),
                'wr_suggestions': rule['wr_suggestions'],
                'field_suggestions': rule['field_suggestions'],
                'execution_note': rule['execution_note']
            }
    
    results['summary']['athletes_flagged'] = len(flagged_athletes)
    results['summary']['categories_flagged'] = len(results['categories'])
    
    return results


def generate_text_report(results: Dict, team_name: str = 'Football') -> str:
    """Generate formatted text report"""
    
    report = []
    report.append("="*80)
    report.append("FORCE PLATE TRAINING REPORT".center(80))
    report.append("="*80)
    report.append(f"\nTeam: {team_name}")
    report.append(f"Report Date: {results['report_date'].strftime('%B %d, %Y')}")
    report.append(f"Data Window: {results['data_window']}")
    report.append("-"*80)
    
    # Summary
    report.append(f"\nSUMMARY:")
    report.append(f"  Total Athletes: {results['summary']['total_athletes']}")
    report.append(f"  Athletes Flagged: {results['summary']['athletes_flagged']}")
    report.append(f"  Categories Flagged: {results['summary']['categories_flagged']}")
    report.append("")
    
    # Each category
    for cat_num, cat_data in results['categories'].items():
        report.append("\n" + "="*80)
        report.append(f"CATEGORY {cat_num}: {cat_data['name'].upper()}")
        report.append("="*80)
        
        # Weight room suggestions
        report.append("\n🏋️ WEIGHT ROOM RECOMMENDATIONS:")
        for suggestion in cat_data['wr_suggestions']:
            report.append(f"  • {suggestion}")
        
        # Field suggestions
        report.append("\n⚡ FIELD RECOMMENDATIONS:")
        for suggestion in cat_data['field_suggestions']:
            report.append(f"  • {suggestion}")
        
        # Athletes
        report.append(f"\n👥 ATHLETES IN THIS CATEGORY: {cat_data['count']}")
        for athlete in cat_data['athletes']:
            report.append(
                f"  {athlete['emoji']} {athlete['name']} "
                f"(#{athlete['number']}, {athlete['position']}) - {athlete['label']}"
            )
        
        # Distribution
        report.append(
            f"\n  Distribution: {cat_data['critical_count']} Critical | "
            f"{cat_data['warning_count']} Warning | {cat_data['caution_count']} Caution"
        )
        
        # Execution note
        report.append(f"\n💡 EXECUTION NOTE:")
        report.append(f"  {cat_data['execution_note']}")
        report.append("")
    
    # Categories not flagged
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


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    # Example: Load your data
    # df = pd.read_csv('force_plate_data.csv')
    
    # For demo, create sample data
    print("Generating sample force plate data...")
    
    np.random.seed(42)
    athletes = [f"Athlete_{i}" for i in range(1, 21)]
    dates = pd.date_range(end=datetime.now(), periods=20, freq='W')
    
    data = []
    for athlete in athletes:
        for date in dates:
            # Simulate declining trend for some athletes
            trend_factor = 1.0
            if athlete in ['Athlete_1', 'Athlete_2', 'Athlete_3']:
                # These athletes show strength decline
                trend_factor = 0.95 - (date - dates[0]).days / 1000
            
            data.append({
                'Athlete_Name': athlete,
                'Date': date,
                'Number': np.random.randint(1, 99),
                'Position': np.random.choice(['WR', 'RB', 'LB', 'DB', 'OL', 'DL']),
                'IMTP_Peak_Force': np.random.normal(3000, 300) * trend_factor,
                'Net_Peak_Vertical_Force': np.random.normal(2800, 300) * trend_factor,
                'IMTP_Force_50ms': np.random.normal(900, 100) * trend_factor,
                'IMTP_Force_100ms': np.random.normal(1500, 150) * trend_factor,
                'IMTP_Force_200ms': np.random.normal(2200, 200) * trend_factor,
                'Peak_Power': np.random.normal(5000, 500) * trend_factor,
                'RSI_mod': np.random.normal(0.55, 0.08) * trend_factor,
                'Eccentric_Mean_Braking_Force': np.random.normal(2400, 250) * trend_factor,
                'Eccentric_Braking_RFD': np.random.normal(6000, 600) * trend_factor,
                'Eccentric_RFD': np.random.normal(4500, 450) * trend_factor,
                'LR_Force_Asymmetry': abs(np.random.normal(5, 3)),
                'Contraction_Time': np.random.normal(0.65, 0.08),
                'Time_to_Peak_Force': np.random.normal(0.3, 0.05)
            })
    
    df = pd.DataFrame(data)
    
    print("\nCategorizing athletes...")
    results = categorize_athletes(df)
    
    print("\nGenerating report...")
    report = generate_text_report(results)
    
    print(report)
    
    # Save to file
    with open('training_report.txt', 'w') as f:
        f.write(report)
    
    print("\n✅ Report saved to: training_report.txt")
    
    # Example: How to access results programmatically
    print("\n" + "="*80)
    print("PROGRAMMATIC ACCESS EXAMPLE")
    print("="*80)
    
    print(f"\nTotal categories flagged: {results['summary']['categories_flagged']}")
    
    for cat_num, cat_data in results['categories'].items():
        print(f"\nCategory {cat_num}: {cat_data['name']}")
        print(f"  Total athletes: {cat_data['count']}")
        print(f"  Critical flags: {cat_data['critical_count']}")
        
        # Get names of critical athletes
        critical_athletes = [
            a['name'] for a in cat_data['athletes'] 
            if a['severity'] == 'red'
        ]
        
        if critical_athletes:
            print(f"  Critical athletes: {', '.join(critical_athletes)}")
