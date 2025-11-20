# Data Mapping Template - Force Plate Decision Grid

## Required Columns for Decision Engine

The automation system needs these standardized column names. Use this template to map YOUR actual column names.

---

## Core Identification Fields

| Required Name | Your Column Name | Example Value | Notes |
|--------------|------------------|---------------|-------|
| Athlete_Name | | "John Smith" | Unique identifier for athlete |
| AthleteID | | "FB_2024_001" | Optional: Unique numeric/string ID |
| Sport | | "Football" | Sport name |
| Position | | "WR" | Position abbreviation |
| Date | | "2024-11-15" | Test date (YYYY-MM-DD format) |
| TestType | | "CMJ" or "IMTP" | Type of test performed |

---

## Metric Mapping - IMTP (Isometric Mid-Thigh Pull)

| Required Name | Your Column Name | ForceDecks Default | Hawkin Default | Units | Notes |
|--------------|------------------|-------------------|----------------|-------|-------|
| IMTP_Peak_Force | | "Peak Force" | "Peak Force (N)" | Newtons | Absolute peak force |
| IMTP_Force_50ms | | "Force @ 50ms" | "RFD 0-50ms" | Newtons | Early-phase RFD |
| IMTP_Force_100ms | | "Force @ 100ms" | "RFD 0-100ms" | Newtons | Mid-phase RFD |
| IMTP_Force_200ms | | "Force @ 200ms" | "RFD 0-200ms" | Newtons | Late-phase RFD |
| Net_Peak_Vertical_Force | | "Net Peak Force" | "Net Force (N)" | Newtons | Peak - Body Weight |

---

## Metric Mapping - CMJ (Countermovement Jump)

| Required Name | Your Column Name | ForceDecks Default | Hawkin Default | Units | Notes |
|--------------|------------------|-------------------|----------------|-------|-------|
| Jump_Height | | "Jump Height (Flight Time)" | "Jump Height" | Meters | 0.35 = 35cm |
| Peak_Power | | "Peak Power" | "Peak Power (W)" | Watts | Usually 4000-6000W |
| RSI_mod | | "RSI-modified" | "RSI-mod" | Ratio | Usually 0.3-0.7 |
| Contraction_Time | | "Time to Takeoff" | "Contraction Time (ms)" | Seconds | Usually 0.5-0.9s |
| Time_to_Peak_Force | | "Time to Peak Force" | "Peak Force Time (ms)" | Seconds | Time to max force |

---

## Metric Mapping - Eccentric Phase

| Required Name | Your Column Name | ForceDecks Default | Hawkin Default | Units | Notes |
|--------------|------------------|-------------------|----------------|-------|-------|
| Eccentric_Mean_Braking_Force | | "Eccentric Mean Force" | "Braking Force Avg" | Newtons | Average during braking |
| Eccentric_Braking_RFD | | "Eccentric RFD" | "Braking RFD" | N/s | Rate during braking |
| Eccentric_RFD | | "Eccentric RFD Peak" | "Peak Ecc RFD" | N/s | Peak eccentric RFD |
| Eccentric_Impulse | | "Eccentric Impulse" | "Braking Impulse" | N·s | Force × time |

---

## Metric Mapping - Asymmetry

| Required Name | Your Column Name | ForceDecks Default | Hawkin Default | Units | Notes |
|--------------|------------------|-------------------|----------------|-------|-------|
| LR_Force_Asymmetry | | "L/R Peak Force %" | "Asymmetry (%)" | Percent | % difference L vs R |
| LR_Impulse_Asymmetry | | "L/R Impulse %" | "Impulse Asym (%)" | Percent | Optional |
| LR_Power_Asymmetry | | "L/R Power %" | "Power Asym (%)" | Percent | Optional |

---

## Step-by-Step Mapping Process

### Step 1: Export Sample Data

Export a CSV from your force plate software with ~20 tests from multiple athletes.

Example structure you might see:
```
Athlete Name, Test Date, Test Type, Jump Height (m), Peak Power (W), RSI-mod, ...
John Smith, 2024-11-15, CMJ, 0.42, 5234, 0.58, ...
```

### Step 2: Create Mapping Dictionary

Fill in YOUR actual column names:

```python
COLUMN_MAPPING = {
    # Core fields
    'Athlete Name': 'Athlete_Name',
    'Test Date': 'Date',
    'Sport': 'Sport',  # May need to add this if not in export
    
    # CMJ metrics
    'Jump Height (m)': 'Jump_Height',
    'Peak Power (W)': 'Peak_Power',
    'RSI-modified': 'RSI_mod',
    'Time to Takeoff (s)': 'Contraction_Time',
    
    # IMTP metrics
    'Peak Force (N)': 'IMTP_Peak_Force',
    'Force @ 50ms (N)': 'IMTP_Force_50ms',
    'Force @ 100ms (N)': 'IMTP_Force_100ms',
    
    # Eccentric
    'Eccentric Mean Force (N)': 'Eccentric_Mean_Braking_Force',
    'Eccentric RFD (N/s)': 'Eccentric_Braking_RFD',
    
    # Asymmetry
    'L/R Peak Force (%)': 'LR_Force_Asymmetry',
}
```

### Step 3: Handle Missing Columns

Some metrics might need to be calculated:

```python
def calculate_derived_metrics(df):
    """Calculate metrics not directly exported"""
    
    # If you have left and right force separately
    if 'Left_Peak_Force' in df.columns and 'Right_Peak_Force' in df.columns:
        df['LR_Force_Asymmetry'] = (
            abs(df['Left_Peak_Force'] - df['Right_Peak_Force']) / 
            df[['Left_Peak_Force', 'Right_Peak_Force']].max(axis=1) * 100
        )
    
    # If RSI-mod not exported but you have jump height and contact time
    if 'RSI_mod' not in df.columns:
        if 'Jump_Height' in df.columns and 'Contraction_Time' in df.columns:
            df['RSI_mod'] = df['Jump_Height'] / df['Contraction_Time']
    
    # Convert units if needed
    if df['Jump_Height'].max() > 1:  # Probably in cm, not meters
        df['Jump_Height'] = df['Jump_Height'] / 100
    
    return df
```

### Step 4: Add Missing Metadata

If Sport/Position not in exports:

```python
# Create lookup table
ATHLETE_METADATA = {
    'John Smith': {'Sport': 'Football', 'Position': 'WR'},
    'Jane Doe': {'Sport': 'Basketball', 'Position': 'Guard'},
    # ... add all athletes
}

def add_metadata(df):
    """Add sport/position if not in export"""
    df['Sport'] = df['Athlete_Name'].map(lambda x: ATHLETE_METADATA.get(x, {}).get('Sport', 'Unknown'))
    df['Position'] = df['Athlete_Name'].map(lambda x: ATHLETE_METADATA.get(x, {}).get('Position', 'Unknown'))
    return df
```

---

## Complete Data Preparation Function

```python
import pandas as pd
from datetime import datetime

def prepare_force_plate_data(filepath: str) -> pd.DataFrame:
    """
    Complete data preparation pipeline
    Customize this based on YOUR specific data source
    """
    
    # 1. Load raw data
    df = pd.read_csv(filepath)
    
    # 2. Apply column mapping (fill in your actual column names)
    COLUMN_MAPPING = {
        'Athlete Name': 'Athlete_Name',
        'Test Date': 'Date',
        # ... add your mappings here
    }
    df = df.rename(columns=COLUMN_MAPPING)
    
    # 3. Fix data types
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Convert numeric columns
    numeric_cols = [
        'IMTP_Peak_Force', 'Peak_Power', 'RSI_mod', 'Jump_Height',
        'Contraction_Time', 'Eccentric_Mean_Braking_Force'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 4. Calculate derived metrics
    df = calculate_derived_metrics(df)
    
    # 5. Add metadata if needed
    df = add_metadata(df)
    
    # 6. Quality control
    df = quality_control_checks(df)
    
    # 7. Sort by athlete and date
    df = df.sort_values(['Athlete_Name', 'Date'])
    
    return df

def quality_control_checks(df: pd.DataFrame) -> pd.DataFrame:
    """Flag physiologically impossible values"""
    
    # Remove impossible values
    if 'IMTP_Peak_Force' in df.columns:
        df.loc[df['IMTP_Peak_Force'] < 500, 'IMTP_Peak_Force'] = None  # Too low
        df.loc[df['IMTP_Peak_Force'] > 8000, 'IMTP_Peak_Force'] = None  # Too high
    
    if 'Jump_Height' in df.columns:
        df.loc[df['Jump_Height'] > 1.0, 'Jump_Height'] = None  # > 1m unlikely
        df.loc[df['Jump_Height'] < 0.1, 'Jump_Height'] = None  # < 10cm unlikely
    
    if 'RSI_mod' in df.columns:
        df.loc[df['RSI_mod'] > 2.0, 'RSI_mod'] = None  # > 2.0 extremely rare
        df.loc[df['RSI_mod'] < 0.1, 'RSI_mod'] = None  # < 0.1 indicates poor effort
    
    # Flag tests with too many missing metrics
    metrics_present = df[numeric_cols].notna().sum(axis=1)
    df['QC_Flag'] = metrics_present < 5  # Flag if < 5 metrics present
    
    return df
```

---

## Testing Your Mapping

```python
# Test the mapping with your sample file
df = prepare_force_plate_data('your_sample_export.csv')

# Check that required columns exist
required_columns = [
    'Athlete_Name', 'Date', 'Sport', 'Position',
    'IMTP_Peak_Force', 'Peak_Power', 'RSI_mod'
]

missing = [col for col in required_columns if col not in df.columns]
if missing:
    print(f"WARNING: Missing required columns: {missing}")
else:
    print("✓ All required columns present")

# Check data quality
print(f"\nTotal tests: {len(df)}")
print(f"Unique athletes: {df['Athlete_Name'].nunique()}")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"\nNull values per column:")
print(df[required_columns].isnull().sum())

# Preview
print("\nFirst 5 rows:")
print(df.head())
```

---

## ForceDecks-Specific Notes

### ForceDecks Pro CSV Export
- Menu → Tests → Export → CSV
- Enable "Include All Metrics" option
- Default units: N, W, m, s
- Date format: MM/DD/YYYY or DD/MM/YYYY (check your settings)

### ForceDecks Teams Export
- Uses different column naming convention
- Check "Metrics Guide" in ForceDecks for exact names
- May need to export from each test type separately (CMJ vs IMTP)

### Common ForceDecks Columns to Map:
```
"Name" → Athlete_Name
"Date" → Date
"Jump Height (Flight Time)" → Jump_Height
"Peak Power / BM" → Peak_Power_Relative
"Modified RSI" → RSI_mod
"Average Braking Force" → Eccentric_Mean_Braking_Force
"L-R Peak Force Variance %" → LR_Force_Asymmetry
```

---

## Hawkin Dynamics-Specific Notes

### Hawkin Cloud Export
- Dashboard → Export → Custom Report
- Select date range and athletes
- Include all jump phases (Unweighting, Braking, Propulsion, Flight)

### Common Hawkin Columns to Map:
```
"Athlete" → Athlete_Name
"Test Date" → Date
"Jump Height" → Jump_Height
"Peak Power" → Peak_Power
"mRSI" → RSI_mod
"Eccentric Mean Force" → Eccentric_Mean_Braking_Force
"System Weight" → Body_Weight
```

---

## Multi-System Integration

If you have multiple force plate systems:

```python
def load_from_multiple_sources():
    """Combine data from ForceDecks and Hawkin"""
    
    # Load ForceDecks data
    forcedecks_df = prepare_force_plate_data('forcedecks_export.csv')
    forcedecks_df['DataSource'] = 'ForceDecks'
    
    # Load Hawkin data
    hawkin_df = prepare_force_plate_data('hawkin_export.csv')
    hawkin_df['DataSource'] = 'Hawkin'
    
    # Combine
    combined = pd.concat([forcedecks_df, hawkin_df], ignore_index=True)
    
    # Deduplicate (keep most recent if duplicate test on same day)
    combined = combined.sort_values('Date').drop_duplicates(
        subset=['Athlete_Name', 'Date', 'TestType'],
        keep='last'
    )
    
    return combined
```

---

## Next Steps After Mapping

1. **Validate sample data** - Run preparation function on 10-20 tests
2. **Check distributions** - Are values reasonable for your population?
3. **Test decision engine** - Run through automation with mapped data
4. **Establish baselines** - Calculate initial SWC values
5. **Deploy** - Connect to your chosen dashboard platform

---

## Troubleshooting Common Issues

**Issue: Column not found**
→ Check exact spelling and capitalization in your export
→ Some systems use "Jump Height" vs "Jump Height (m)"

**Issue: Date parsing errors**
→ Check date format in your export settings
→ Use: `pd.to_datetime(df['Date'], format='%m/%d/%Y')`

**Issue: Values seem wrong (too high/low)**
→ Check units (meters vs cm, Newtons vs kg)
→ Apply conversion factors as needed

**Issue: Missing sport/position data**
→ Create manual lookup table (see ATHLETE_METADATA above)
→ Or add to your force plate system's athlete profiles

---

## Contact & Support

For Baylor-specific implementation questions:
- Check with your ForceDecks administrator for exact column names
- Review your current data pipeline (manual export vs API)
- Coordinate with IT if database integration needed
