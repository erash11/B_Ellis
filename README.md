# Force Plate Decision Grid - Automated Dashboard

## Quick Start

### Local Development (Fastest way to demo)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the app:**
```bash
streamlit run force_plate_dashboard.py
```

3. **Open browser:**
The app will automatically open at `http://localhost:8501`

---

## Customizing for Real Data

Currently the app uses generated demo data. To connect to your actual ForceDecks/Hawkin data:

### Option 1: CSV Import

Replace the `generate_demo_data()` function with:

```python
@st.cache_data
def load_force_plate_data(filepath: str) -> pd.DataFrame:
    """Load actual force plate data from CSV"""
    df = pd.read_csv(filepath, parse_dates=['Date'])
    
    # Map your column names to standard names
    column_mapping = {
        'Athlete Name': 'Athlete_Name',
        'Test Date': 'Date',
        'Peak Force (N)': 'IMTP_Peak_Force',
        # Add all your column mappings here
    }
    
    df = df.rename(columns=column_mapping)
    return df
```

Then in `main()`:
```python
# Replace this line:
df = generate_demo_data()

# With this:
uploaded_file = st.sidebar.file_uploader("Upload Force Plate CSV", type=['csv'])
if uploaded_file:
    df = load_force_plate_data(uploaded_file)
else:
    st.warning("Please upload a CSV file")
    return
```

### Option 2: Direct Database Connection

```python
import sqlalchemy

@st.cache_data
def load_from_database():
    """Connect to your database"""
    engine = sqlalchemy.create_engine('postgresql://user:pass@host/db')
    query = """
        SELECT 
            athlete_name,
            test_date,
            imtp_peak_force,
            rsi_mod,
            -- ... all metrics
        FROM force_plate_tests
        WHERE test_date >= CURRENT_DATE - INTERVAL '1 year'
        ORDER BY test_date
    """
    return pd.read_sql(query, engine)
```

### Option 3: ForceDecks API (if available)

```python
import requests

def fetch_from_forcedecks_api(api_key: str):
    """Fetch data from ForceDecks API"""
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get(
        'https://api.forcedecks.com/v1/tests',
        headers=headers,
        params={'from_date': '2024-01-01'}
    )
    return pd.DataFrame(response.json()['data'])
```

---

## Deployment Options

### Option 1: Streamlit Cloud (Free, Public)

1. Push code to GitHub repo
2. Go to https://share.streamlit.io
3. Connect your GitHub account
4. Deploy from repo
5. Share the URL with coaching staff

**Pros:** Free, easy, automatic updates
**Cons:** Data is on public cloud (can add password protection)

### Option 2: Internal Server

If Baylor has a server you can deploy to:

```bash
# On your server
git clone <your-repo>
cd force-plate-dashboard
pip install -r requirements.txt

# Run with nohup to keep running
nohup streamlit run force_plate_dashboard.py --server.port 8501 &
```

Access at: `http://your-server-ip:8501`

### Option 3: Docker Container

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "force_plate_dashboard.py"]
```

Deploy:
```bash
docker build -t force-plate-dashboard .
docker run -p 8501:8501 force-plate-dashboard
```

---

## Customization Guide

### Adjusting SWC Thresholds

In the `ForcePlateDecisionEngine` class:

```python
@staticmethod
def calculate_swc(baseline_data: pd.Series, method: str = '0.2sd') -> float:
    # Change to 0.3 for more conservative (fewer flags)
    return 0.3 * baseline_data.std()
    
    # Or use 5% method:
    # return 0.05 * baseline_data.mean()
```

### Adding Sport-Specific Rules

```python
SPORT_MODIFIERS = {
    'Football': {
        'positions': {
            'Big': {'strength_weight': 1.5, 'rfd_weight': 0.8},
            'Skill': {'strength_weight': 0.8, 'rfd_weight': 1.5}
        }
    },
    'Basketball': {
        'positions': {
            'Guard': {'ssc_weight': 1.3},
            'Post': {'strength_weight': 1.2}
        }
    }
}
```

### Changing Re-Eval Windows

Edit the `DECISION_RULES` dictionary:

```python
1: {
    'category': 'Maximal Strength Capacity',
    # ... other fields
    'reeval_days': 14  # Change from 9 to 14 days
}
```

### Email Notifications

Add at the end of `main()`:

```python
if flags and any(f['severity'] == 'red' for f in flags):
    send_email_alert(selected_athlete, flags)

def send_email_alert(athlete: str, flags: List[Dict]):
    import smtplib
    from email.mime.text import MIMEText
    
    red_flags = [f for f in flags if f['severity'] == 'red']
    
    msg = MIMEText(f"""
    CRITICAL ALERT: {athlete}
    
    {len(red_flags)} red flags detected:
    {', '.join([f['category'] for f in red_flags])}
    
    View dashboard: http://your-dashboard-url
    """)
    
    msg['Subject'] = f'Force Plate Alert: {athlete}'
    msg['From'] = 'forceplate@baylor.edu'
    msg['To'] = 'coach@baylor.edu'
    
    # Configure your SMTP server
    with smtplib.SMTP('smtp.baylor.edu', 587) as server:
        server.starttls()
        server.login('user', 'pass')
        server.send_message(msg)
```

---

## Integration with Existing Systems

### Power BI Integration

Export data for Power BI:

```python
# Add to sidebar
if st.button("Export for Power BI"):
    export_data = prepare_powerbi_export(df, flags)
    export_data.to_csv('powerbi_export.csv', index=False)
    st.download_button(
        "Download CSV",
        data=export_data.to_csv(index=False),
        file_name='force_plate_decisions.csv'
    )
```

### TeamBuildr Integration

If you use TeamBuildr for program delivery:

```python
def push_to_teambuildr(athlete_id: str, recommendations: Dict):
    """Send workout modifications to TeamBuildr"""
    # Use TeamBuildr API to adjust programming
    pass
```

---

## Troubleshooting

### "Module not found" errors
```bash
pip install --upgrade -r requirements.txt
```

### Port already in use
```bash
streamlit run force_plate_dashboard.py --server.port 8502
```

### Slow performance with large datasets
Add these to the top of your script:
```python
st.set_page_config(layout="wide")  # Use full screen width

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    # Your data loading function
```

---

## Next Steps

1. **Test with demo data** - Run the app as-is to see functionality
2. **Map your data** - Identify which ForceDecks columns map to required metrics
3. **Validate thresholds** - Use historical data to tune SWC calculations
4. **Train staff** - Walk coaches through the interface
5. **Collect feedback** - Iterate based on real-world use
6. **Scale up** - Deploy to production once validated

---

## Support & Questions

This is a prototype designed for rapid iteration. Expect to customize heavily based on:
- Your specific force plate system
- Your testing protocols
- Your staff's workflow
- Your organization's data infrastructure

Key files:
- `force_plate_dashboard.py` - Main application
- `force_plate_automation_guide.md` - Comprehensive implementation guide
- `Force_Plate_Decision_Grid_copy.xlsx` - Original decision rules

---

## License & Attribution

Built for Baylor University Athletics - B.A.I.R. Initiative
Based on decision framework developed by [Your Colleague's Name]
