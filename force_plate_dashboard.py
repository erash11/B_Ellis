import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Page configuration
st.set_page_config(
    page_title="Force Plate Decision Grid",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better visuals
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .red-flag {
        background-color: #ffebee;
        border-left: 5px solid #c62828;
    }
    .yellow-flag {
        background-color: #fff9e6;
        border-left: 5px solid #f57f17;
    }
    .green-flag {
        background-color: #e8f5e9;
        border-left: 5px solid #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DECISION ENGINE CLASS
# ============================================================================

class ForcePlateDecisionEngine:
    """Core decision logic for Force Plate Decision Grid"""
    
    DECISION_RULES = {
        1: {
            'category': 'Maximal Strength Capacity',
            'metrics': ['IMTP_Peak_Force', 'Net_Peak_Vertical_Force'],
            'trend': 'decrease',
            'threshold_multiplier': 1.0,
            'interpretation': 'Loss of total force output or neural drive',
            'wr_rx': 'Heavy isometrics / TUT, Cluster Sets (≥80% 1RM)',
            'field_rx': 'Resisted Sprints (50-60% vdec)',
            'reeval_days': 9
        },
        2: {
            'category': 'Explosive Strength / RFD',
            'metrics': ['IMTP_Force_50ms', 'IMTP_Force_100ms', 'IMTP_Force_200ms'],
            'trend': 'decrease',
            'threshold_multiplier': 1.0,
            'interpretation': 'Diminished early-phase RFD; neural or tendon stiffness',
            'wr_rx': 'Contrast/complex training, Olympic lifts (60-70% 1RM)',
            'field_rx': 'Resisted Sprints (10-30% vdec)',
            'reeval_days': 7
        },
        3: {
            'category': 'Power Output',
            'metrics': ['Peak_Power'],
            'trend': 'decrease',
            'threshold_multiplier': 1.0,
            'interpretation': 'Fatigue or inability to express strength at velocity',
            'wr_rx': 'Contrast/complex training, Cluster sets (70-80% 1RM)',
            'field_rx': 'Resisted Sprints (30-50% vdec)',
            'reeval_days': 7
        },
        4: {
            'category': 'SSC Efficiency',
            'metrics': ['RSI_mod', 'Eccentric_Braking_RFD'],
            'trend': 'decrease',
            'threshold_multiplier': 1.0,
            'interpretation': 'Reduced elasticity / tendon stiffness efficiency',
            'wr_rx': 'Reactive / Ballistic Techniques',
            'field_rx': 'Plyometric Training',
            'reeval_days': 5
        },
        5: {
            'category': 'Eccentric Control',
            'metrics': ['Eccentric_Mean_Braking_Force', 'Eccentric_RFD'],
            'trend': 'decrease',
            'threshold_multiplier': 1.0,
            'interpretation': 'Poor braking; elevated soft-tissue risk',
            'wr_rx': 'Eccentrics / TUT (3-5s), Overload (105-120% 1RM)',
            'field_rx': 'COD / Deceleration Drills',
            'reeval_days': 12
        },
        6: {
            'category': 'Technical / Coordination',
            'metrics': ['Contraction_Time', 'Time_to_Peak_Force'],
            'trend': 'increase',
            'threshold_multiplier': 1.0,
            'interpretation': 'Movement efficiency degradation / timing disruption',
            'wr_rx': 'Wave Loading, Cluster Sets, Rhythmic Tempo',
            'field_rx': 'Motor-control drills, skill retraining',
            'reeval_days': 6
        },
        7: {
            'category': 'Asymmetry',
            'metrics': ['LR_Force_Asymmetry'],
            'trend': 'increase',
            'threshold_type': 'absolute',
            'threshold_value': 10,  # percent
            'interpretation': 'Functional asymmetry or compensation',
            'wr_rx': 'Single-leg / unilateral work, split-stance',
            'field_rx': 'Unilateral jumps',
            'reeval_days': 9
        },
        8: {
            'category': 'Fatigue / Strategy Shift',
            'metrics': ['Contraction_Time', 'Jump_Height'],
            'trend': 'cluster',
            'cluster_logic': 'CT_increase_AND_JH_decrease',
            'interpretation': 'Fatigue-driven protective motor strategy',
            'wr_rx': 'Reduce tonnage 10-20%, increase rest',
            'field_rx': 'Active recovery',
            'reeval_days': 4
        },
        9: {
            'category': 'Systemic Fatigue',
            'metrics': ['RSI_mod', 'Peak_Power'],
            'trend': 'cluster',
            'cluster_logic': 'Both_decrease_>10pct',
            'interpretation': 'Global CNS / metabolic fatigue',
            'wr_rx': 'Deload block (-20% load), active recovery',
            'field_rx': 'Restoration micro-cycle',
            'reeval_days': 12
        }
    }
    
    @staticmethod
    def calculate_swc(baseline_data: pd.Series, method: str = '0.2sd') -> float:
        """Calculate Smallest Worthwhile Change"""
        if method == '0.2sd':
            return 0.2 * baseline_data.std()
        elif method == '5pct':
            return 0.05 * baseline_data.mean()
        return baseline_data.std() * 0.2
    
    @staticmethod
    def calculate_rolling_avg(data: pd.Series, window: int = 4) -> pd.Series:
        """Calculate rolling average for trend detection"""
        return data.rolling(window=window, min_periods=2).mean()
    
    @staticmethod
    def classify_severity(deviation: float, swc: float) -> Tuple[str, str]:
        """Classify deviation severity and return color + label"""
        abs_dev = abs(deviation)
        
        if abs_dev <= swc:
            return 'green', 'Normal'
        elif abs_dev <= 1.5 * swc:
            return 'yellow', 'Caution'
        elif abs_dev <= 2 * swc:
            return 'orange', 'Warning'
        else:
            return 'red', 'Critical'
    
    @classmethod
    def evaluate_athlete(cls, athlete_data: pd.DataFrame, 
                        baseline_period_days: int = 180) -> List[Dict]:
        """
        Evaluate athlete against all decision rules
        Returns list of flagged categories with recommendations
        """
        flags = []
        
        # Get baseline data (last 6 months)
        cutoff_date = athlete_data['Date'].max() - timedelta(days=baseline_period_days)
        baseline_data = athlete_data[athlete_data['Date'] >= cutoff_date]
        
        # Get most recent test
        current_test = athlete_data.iloc[-1]
        
        for cat_num, rule in cls.DECISION_RULES.items():
            # Check each metric in the category
            for metric in rule['metrics']:
                if metric not in athlete_data.columns:
                    continue
                
                # Calculate baseline and SWC
                baseline_values = baseline_data[metric].dropna()
                if len(baseline_values) < 3:
                    continue  # Need at least 3 tests for baseline
                
                baseline_mean = baseline_values.mean()
                swc = cls.calculate_swc(baseline_values)
                
                # Get current value
                current_value = current_test[metric]
                
                # Calculate deviation based on trend direction
                if rule['trend'] == 'decrease':
                    deviation = baseline_mean - current_value  # Positive = got worse
                elif rule['trend'] == 'increase':
                    deviation = current_value - baseline_mean  # Positive = got worse
                else:  # cluster logic
                    continue  # Handle separately
                
                # Classify severity
                severity, severity_label = cls.classify_severity(deviation, swc)
                
                # Only flag if yellow or worse
                if severity in ['yellow', 'orange', 'red']:
                    reeval_date = current_test['Date'] + timedelta(days=rule['reeval_days'])
                    
                    flags.append({
                        'category_num': cat_num,
                        'category': rule['category'],
                        'metric': metric,
                        'current_value': current_value,
                        'baseline_value': baseline_mean,
                        'swc': swc,
                        'deviation': deviation,
                        'severity': severity,
                        'severity_label': severity_label,
                        'interpretation': rule['interpretation'],
                        'wr_rx': rule['wr_rx'],
                        'field_rx': rule['field_rx'],
                        'reeval_date': reeval_date.strftime('%Y-%m-%d'),
                        'reeval_days': rule['reeval_days']
                    })
                    break  # Only flag category once
        
        # Sort by severity (red first) then category priority
        priority_map = {5: 1, 7: 2, 9: 3, 1: 4, 2: 5, 3: 6, 4: 7, 6: 8, 8: 9}
        severity_map = {'red': 0, 'orange': 1, 'yellow': 2}
        
        flags.sort(key=lambda x: (severity_map.get(x['severity'], 3), 
                                  priority_map.get(x['category_num'], 10)))
        
        return flags

# ============================================================================
# DATA GENERATION (Demo purposes - replace with real data loader)
# ============================================================================

@st.cache_data
def generate_demo_data(n_athletes: int = 10, n_tests: int = 20) -> pd.DataFrame:
    """Generate realistic demo force plate data"""
    np.random.seed(42)
    
    athletes = [f"Athlete_{i+1}" for i in range(n_athletes)]
    sports = ['Football', 'Basketball', 'Track', 'Volleyball']
    positions = ['Skill', 'Big', 'Jumper', 'Sprinter']
    
    data = []
    
    for athlete in athletes:
        sport = np.random.choice(sports)
        position = np.random.choice(positions)
        
        # Baseline values (with some athlete-to-athlete variation)
        base_imtp = np.random.normal(3000, 400)
        base_rsi = np.random.normal(0.55, 0.08)
        base_power = np.random.normal(5000, 600)
        base_jump = np.random.normal(0.45, 0.05)
        
        # Generate tests over time
        start_date = datetime(2024, 6, 1)
        
        for test_num in range(n_tests):
            test_date = start_date + timedelta(days=test_num * 7)
            
            # Add realistic trends and noise
            fatigue_factor = 1 - (test_num % 4) * 0.02  # Simulate training cycle
            noise = np.random.normal(1, 0.03)
            
            data.append({
                'Athlete_Name': athlete,
                'Sport': sport,
                'Position': position,
                'Date': test_date,
                'IMTP_Peak_Force': base_imtp * fatigue_factor * noise,
                'IMTP_Force_50ms': base_imtp * 0.3 * fatigue_factor * noise,
                'IMTP_Force_100ms': base_imtp * 0.5 * fatigue_factor * noise,
                'IMTP_Force_200ms': base_imtp * 0.75 * fatigue_factor * noise,
                'Peak_Power': base_power * fatigue_factor * noise,
                'RSI_mod': base_rsi * fatigue_factor * noise,
                'Jump_Height': base_jump * fatigue_factor * noise,
                'Contraction_Time': 0.65 / fatigue_factor * noise,
                'Time_to_Peak_Force': 0.3 / fatigue_factor * noise,
                'Eccentric_Mean_Braking_Force': base_imtp * 0.8 * fatigue_factor * noise,
                'Eccentric_Braking_RFD': base_imtp * 2 * fatigue_factor * noise,
                'Eccentric_RFD': base_imtp * 1.5 * fatigue_factor * noise,
                'LR_Force_Asymmetry': abs(np.random.normal(5, 3)),
                'Net_Peak_Vertical_Force': base_imtp * 1.1 * fatigue_factor * noise
            })
    
    return pd.DataFrame(data)

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def create_category_status_heatmap(flags: List[Dict]) -> go.Figure:
    """Create visual grid showing 9-category status"""
    
    categories = [
        '1. Max Strength', '2. RFD', '3. Power',
        '4. SSC', '5. Eccentric', '6. Coordination',
        '7. Asymmetry', '8. Fatigue', '9. Systemic'
    ]
    
    # Initialize all green
    colors = ['#4caf50'] * 9  # Green
    hover_texts = ['Normal Range'] * 9
    
    # Update based on flags
    for flag in flags:
        idx = flag['category_num'] - 1
        if flag['severity'] == 'red':
            colors[idx] = '#c62828'
            hover_texts[idx] = f"🔴 CRITICAL<br>{flag['interpretation']}"
        elif flag['severity'] == 'orange':
            colors[idx] = '#ef6c00'
            hover_texts[idx] = f"🟠 WARNING<br>{flag['interpretation']}"
        elif flag['severity'] == 'yellow':
            colors[idx] = '#f57f17'
            hover_texts[idx] = f"🟡 CAUTION<br>{flag['interpretation']}"
    
    fig = go.Figure(data=[go.Bar(
        x=categories,
        y=[1] * 9,
        marker=dict(color=colors),
        text=['●'] * 9,
        textposition='inside',
        textfont=dict(size=40, color='white'),
        hovertext=hover_texts,
        hoverinfo='text',
        showlegend=False
    )])
    
    fig.update_layout(
        title="9-Category Status Overview",
        xaxis=dict(title='', tickangle=-45),
        yaxis=dict(visible=False, range=[0, 1.5]),
        height=300,
        margin=dict(t=50, b=100),
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_trend_chart(athlete_data: pd.DataFrame, metric: str, 
                      baseline_mean: float, swc: float) -> go.Figure:
    """Create trend chart with SWC bands"""
    
    fig = go.Figure()
    
    # SWC bands
    fig.add_hrect(
        y0=baseline_mean - swc, y1=baseline_mean + swc,
        fillcolor="green", opacity=0.1, line_width=0,
        annotation_text="Normal", annotation_position="right"
    )
    fig.add_hrect(
        y0=baseline_mean + swc, y1=baseline_mean + 1.5*swc,
        fillcolor="yellow", opacity=0.1, line_width=0
    )
    fig.add_hrect(
        y0=baseline_mean - 1.5*swc, y1=baseline_mean - swc,
        fillcolor="yellow", opacity=0.1, line_width=0
    )
    
    # Baseline line
    fig.add_hline(y=baseline_mean, line_dash="dash", line_color="gray",
                  annotation_text="Baseline")
    
    # Actual data
    fig.add_trace(go.Scatter(
        x=athlete_data['Date'],
        y=athlete_data[metric],
        mode='lines+markers',
        name='Actual',
        line=dict(color='#1976d2', width=2),
        marker=dict(size=6)
    ))
    
    # Rolling average
    rolling_avg = ForcePlateDecisionEngine.calculate_rolling_avg(athlete_data[metric])
    fig.add_trace(go.Scatter(
        x=athlete_data['Date'],
        y=rolling_avg,
        mode='lines',
        name='4-Week Avg',
        line=dict(color='#d32f2f', width=2, dash='dot')
    ))
    
    fig.update_layout(
        title=f"{metric} - Trend Analysis",
        xaxis_title="Date",
        yaxis_title="Value",
        height=400,
        hovermode='x unified'
    )
    
    return fig

# ============================================================================
# STREAMLIT APP
# ============================================================================

def main():
    st.title("💪 Force Plate Decision Grid")
    st.markdown("*Automated decision support for force plate interpretation*")
    
    # Load data
    df = generate_demo_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    selected_sport = st.sidebar.selectbox(
        "Sport",
        options=['All'] + sorted(df['Sport'].unique().tolist())
    )
    
    if selected_sport != 'All':
        athlete_list = df[df['Sport'] == selected_sport]['Athlete_Name'].unique()
    else:
        athlete_list = df['Athlete_Name'].unique()
    
    selected_athlete = st.sidebar.selectbox(
        "Athlete",
        options=sorted(athlete_list)
    )
    
    # Filter data
    athlete_data = df[df['Athlete_Name'] == selected_athlete].sort_values('Date').reset_index(drop=True)
    
    # Get athlete info
    sport = athlete_data['Sport'].iloc[0]
    position = athlete_data['Position'].iloc[0]
    last_test = athlete_data['Date'].max().strftime('%Y-%m-%d')
    days_since = (datetime.now() - athlete_data['Date'].max()).days
    
    # Header section
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sport", sport)
    with col2:
        st.metric("Position", position)
    with col3:
        st.metric("Last Test", last_test)
    with col4:
        st.metric("Days Since", f"{days_since} days")
    
    st.markdown("---")
    
    # Run decision engine
    flags = ForcePlateDecisionEngine.evaluate_athlete(athlete_data)
    
    # Status overview
    col1, col2, col3 = st.columns(3)
    with col1:
        red_count = sum(1 for f in flags if f['severity'] == 'red')
        st.metric("🔴 Critical Flags", red_count)
    with col2:
        yellow_count = sum(1 for f in flags if f['severity'] in ['yellow', 'orange'])
        st.metric("🟡 Caution Flags", yellow_count)
    with col3:
        green_count = 9 - len(flags)
        st.metric("🟢 Normal", green_count)
    
    # Category status heatmap
    fig_heatmap = create_category_status_heatmap(flags)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    st.markdown("---")
    
    # Recommendations
    if flags:
        st.header("⚠️ Intervention Recommendations")
        
        for i, flag in enumerate(flags):
            severity_emoji = {'red': '🔴', 'orange': '🟠', 'yellow': '🟡'}[flag['severity']]
            
            with st.expander(f"{severity_emoji} **{flag['category']}** - {flag['severity_label'].upper()}", expanded=(i==0)):
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown(f"**Metric Flagged:** `{flag['metric']}`")
                    st.markdown(f"**Current Value:** {flag['current_value']:.2f}")
                    st.markdown(f"**Baseline:** {flag['baseline_value']:.2f}")
                    st.markdown(f"**Deviation:** {flag['deviation']:.2f} (SWC: {flag['swc']:.2f})")
                
                with col2:
                    st.markdown(f"**Re-Eval Date:** {flag['reeval_date']}")
                    st.markdown(f"**Re-Test In:** {flag['reeval_days']} days")
                
                st.markdown(f"**🎯 Interpretation:** {flag['interpretation']}")
                st.markdown(f"**🏋️ Weight Room:** {flag['wr_rx']}")
                if flag['field_rx']:
                    st.markdown(f"**⚡ Field Work:** {flag['field_rx']}")
                
                # Show trend chart for flagged metric
                baseline_vals = athlete_data[flag['metric']].iloc[:-5]  # Baseline from earlier tests
                baseline_mean = baseline_vals.mean()
                swc = ForcePlateDecisionEngine.calculate_swc(baseline_vals)
                
                fig_trend = create_trend_chart(athlete_data, flag['metric'], baseline_mean, swc)
                st.plotly_chart(fig_trend, use_container_width=True)
    
    else:
        st.success("✅ **All systems normal!** No interventions needed at this time.")
    
    st.markdown("---")
    
    # Metric explorer
    st.header("📊 Metric Explorer")
    
    all_metrics = [
        'IMTP_Peak_Force', 'IMTP_Force_50ms', 'Peak_Power', 'RSI_mod',
        'Jump_Height', 'Contraction_Time', 'Eccentric_Mean_Braking_Force',
        'LR_Force_Asymmetry'
    ]
    
    selected_metric = st.selectbox("Select metric to visualize", all_metrics)
    
    baseline_vals = athlete_data[selected_metric].iloc[:-5]
    baseline_mean = baseline_vals.mean()
    swc = ForcePlateDecisionEngine.calculate_swc(baseline_vals)
    
    fig_explorer = create_trend_chart(athlete_data, selected_metric, baseline_mean, swc)
    st.plotly_chart(fig_explorer, use_container_width=True)
    
    # Raw data table
    with st.expander("📋 View Raw Test Data"):
        st.dataframe(
            athlete_data[['Date'] + all_metrics].sort_values('Date', ascending=False),
            hide_index=True
        )

if __name__ == "__main__":
    main()
