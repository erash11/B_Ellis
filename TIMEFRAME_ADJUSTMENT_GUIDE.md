# Adjusting Report Timeframes - Complete Guide

## Overview

The force plate report uses historical data to detect trends. You can adjust the timeframe in several ways depending on your needs.

---

## 🎯 **Common Use Cases**

| Use Case | Timeframe | Why |
|----------|-----------|-----|
| **End of Season Review** | Full season (4-6 months) | See overall trends |
| **Phase Transition** | Current phase only (4-6 weeks) | Plan next phase |
| **Monthly Check-In** | Last 4-8 weeks | Quick status update |
| **Post-Training Block** | Just that block (3-4 weeks) | Assess block effectiveness |
| **In-Season Monitoring** | Last 2-4 weeks | Detect acute fatigue |
| **Off-Season Assessment** | Last 8-12 weeks | Track capacity building |

---

## ⚙️ **Method 1: Edit the Python Script (Recommended)**

### Open `generate_html_report.py` and find this section:

```python
# ============================================================================
# DATE FILTERING - ADJUST THESE TO CHANGE REPORT TIMEFRAME
# ============================================================================

# Option A: Use last N months of data
MONTHS_TO_INCLUDE = 3  # Change this number (1-12)
cutoff_date = datetime.now() - timedelta(days=MONTHS_TO_INCLUDE * 30)
df = df[df['Date'] >= cutoff_date]
```

### Example Adjustments:

**Last 1 Month (4 weeks):**
```python
MONTHS_TO_INCLUDE = 1
```

**Last 2 Months (8 weeks):**
```python
MONTHS_TO_INCLUDE = 2
```

**Last 6 Months (full season):**
```python
MONTHS_TO_INCLUDE = 6
```

---

## 📅 **Method 2: Specific Date Range**

### For a specific training phase:

Comment out Option A and use Option B:

```python
# Option A: Use last N months of data
# MONTHS_TO_INCLUDE = 3
# cutoff_date = datetime.now() - timedelta(days=MONTHS_TO_INCLUDE * 30)
# df = df[df['Date'] >= cutoff_date]

# Option B: Specific date range
START_DATE = '2025-09-01'  # Phase start date
END_DATE = '2025-11-24'    # Phase end date
df = df[(df['Date'] >= START_DATE) & (df['Date'] <= END_DATE)]
```

### Example: Fall Training Block (Sept 1 - Nov 24)
```python
START_DATE = '2025-09-01'
END_DATE = '2025-11-24'
```

### Example: Summer Strength Phase (June 1 - Aug 15)
```python
START_DATE = '2025-06-01'
END_DATE = '2025-08-15'
```

---

## 🔄 **Method 3: Phase-Based Filtering**

### For current phase only:

Comment out Option A and use Option C:

```python
# Option C: Only use data from current training phase
PHASE_START_DATE = '2025-09-01'  # When current phase started
df = df[df['Date'] >= PHASE_START_DATE]
```

This automatically includes everything from phase start to today.

---

## 📊 **Baseline Calculation Methods**

The script also has options for HOW to calculate baselines:

### Current Method (60/40 Split):
```python
# Use first 60% of data as baseline, last 40% as current
split = int(len(metric_data) * 0.6)
baseline = metric_data.iloc[:split]
current = metric_data.iloc[-1]
```

**When to use:** Standard approach, works for most timeframes

### Alternative Method (50/50 with Average):
```python
# Use first half as baseline, compare to recent average
split = len(metric_data) // 2
baseline = metric_data.iloc[:split]
current = metric_data.iloc[split:].mean()  # Average of recent tests
```

**When to use:** Shorter timeframes (4-8 weeks), reduces sensitivity to single bad test

---

## 🧪 **Examples for Different Scenarios**

### Scenario 1: Post-Training Block Report (4 weeks)

**Goal:** See if the training block worked

```python
# Use exact 4-week block dates
START_DATE = '2025-10-28'  # Block start
END_DATE = '2025-11-24'    # Block end
df = df[(df['Date'] >= START_DATE) & (df['Date'] <= END_DATE)]

# Use 50/50 split for short timeframe
split = len(metric_data) // 2
baseline = metric_data.iloc[:split]  # First 2 weeks
current = metric_data.iloc[split:].mean()  # Last 2 weeks average
```

### Scenario 2: Monthly Check-In (Rolling 6 weeks)

**Goal:** Quick status update, not too sensitive

```python
# Last 6 weeks
MONTHS_TO_INCLUDE = 1.5  # 6 weeks ≈ 1.5 months
cutoff_date = datetime.now() - timedelta(days=int(MONTHS_TO_INCLUDE * 30))
df = df[df['Date'] >= cutoff_date]

# Standard 60/40 split
```

### Scenario 3: End of Season Review (Full Season)

**Goal:** Comprehensive assessment

```python
# Entire season (6 months)
MONTHS_TO_INCLUDE = 6
cutoff_date = datetime.now() - timedelta(days=MONTHS_TO_INCLUDE * 30)
df = df[df['Date'] >= cutoff_date]

# Use 60/40 split to see overall trend
```

### Scenario 4: In-Season Fatigue Monitoring (2 weeks)

**Goal:** Detect acute fatigue quickly

```python
# Last 2 weeks only
START_DATE = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
END_DATE = datetime.now().strftime('%Y-%m-%d')
df = df[(df['Date'] >= START_DATE) & (df['Date'] <= END_DATE)]

# Use 50/50 split for very short timeframe
split = len(metric_data) // 2
baseline = metric_data.iloc[:split]
current = metric_data.iloc[split:].mean()
```

---

## 🎛️ **Using Claude Code to Adjust Timeframes**

### Quick Adjustment:

```bash
claude-code
```

**Prompt:**
```
Modify generate_html_report.py to only include data from the last 4 weeks
```

**Claude Code response:**
```
Updated! Now using last 4 weeks of data.
Run: python3 generate_html_report.py
```

### Multiple Timeframes:

**Prompt:**
```
Generate 3 separate reports:
1. Last 4 weeks (current phase)
2. Last 8 weeks (recent training)
3. Last 6 months (full season)

Save as:
- Baylor_Report_4wk.html
- Baylor_Report_8wk.html
- Baylor_Report_6mo.html
```

---

## ⚖️ **Choosing the Right Timeframe**

### Too Short (< 3 weeks):
❌ Not enough data for reliable trends  
❌ Single bad test can flag athlete  
❌ Baseline calculations unstable  
✅ Good for: Acute fatigue detection only

### Sweet Spot (4-8 weeks):
✅ Captures training phase effects  
✅ Enough data for trends  
✅ Recent enough to be actionable  
✅ Good for: Phase-end planning

### Longer (3-6 months):
✅ Comprehensive view  
✅ Stable baselines  
❌ May miss recent changes  
❌ Less actionable for immediate training  
✅ Good for: Season reviews, program evaluation

---

## 📏 **Impact on Results**

### Shorter Timeframe (4 weeks) → More Sensitive
- More athletes flagged
- Picks up recent changes quickly
- Good for in-season adjustments
- Higher "false alarm" rate

### Longer Timeframe (6 months) → More Stable
- Fewer athletes flagged
- Only shows sustained trends
- Good for program assessment
- May miss recent issues

---

## 🔧 **Advanced: Dynamic Timeframe**

### Automatically use current training phase:

```python
# Define your training phases
TRAINING_PHASES = {
    'Summer Strength': ('2025-06-01', '2025-08-15'),
    'Fall Training': ('2025-09-01', '2025-11-24'),
    'Winter Power': ('2025-12-01', '2026-01-31'),
}

# Auto-detect current phase
current_date = datetime.now()
for phase_name, (start, end) in TRAINING_PHASES.items():
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    if start_date <= current_date <= end_date:
        df = df[(df['Date'] >= start) & (df['Date'] <= end)]
        TRAINING_PHASE = phase_name
        break
```

---

## 📝 **Quick Reference Commands**

### Generate 4-Week Report:
```python
# In generate_html_report.py, line ~17:
MONTHS_TO_INCLUDE = 1
```
```bash
python3 generate_html_report.py
```

### Generate 8-Week Report:
```python
MONTHS_TO_INCLUDE = 2
```

### Generate Phase-Specific Report:
```python
START_DATE = '2025-09-01'
END_DATE = '2025-11-24'
```

### Generate Multiple Timeframes at Once:

**With Claude Code:**
```
Generate reports for 4-week, 8-week, and 6-month timeframes, 
save as separate HTML files
```

---

## 🎯 **Recommended Settings by Goal**

| Goal | Timeframe | Baseline Method | Sensitivity |
|------|-----------|-----------------|-------------|
| **Phase Planning** | 4-6 weeks | 60/40 split | Standard (2.0× SWC) |
| **Season Review** | 4-6 months | 60/40 split | Standard (2.0× SWC) |
| **Fatigue Monitoring** | 2-3 weeks | 50/50 + average | High (1.5× SWC) |
| **Block Assessment** | Exact block dates | 50/50 split | Standard (2.0× SWC) |
| **Monthly Check** | 6-8 weeks | 60/40 split | Low (2.5× SWC) |

---

## ⚠️ **Important Considerations**

### 1. Minimum Data Requirements

**Absolute minimum:** 3 tests per athlete in timeframe  
**Recommended minimum:** 5-6 tests per athlete  
**Ideal:** 8-10 tests per athlete

**If you go too short:** Athletes without enough tests will be excluded from analysis

### 2. Test Frequency Matters

- **Testing 2x/week:** Can use 4-week timeframes
- **Testing 1x/week:** Need 6-8 week timeframes
- **Testing every 2 weeks:** Need 3+ month timeframes

### 3. Training Phase Alignment

**Best practice:** Align report timeframe with training phase

Example:
```
Fall Strength Block: Sept 1 - Nov 24 (12 weeks)
→ Use those exact dates in report
```

---

## 🚀 **Quick Start for Your Next Report**

1. **Decide your timeframe:**
   - End of phase? → Use phase dates
   - Monthly check? → Last 6-8 weeks
   - Season review? → Last 4-6 months

2. **Edit the script:**
   ```python
   # Line ~17 in generate_html_report.py
   MONTHS_TO_INCLUDE = 2  # Change this number
   ```

3. **Run:**
   ```bash
   python3 generate_html_report.py
   ```

4. **Review output:**
   - Too many flags? → Increase timeframe
   - Too few flags? → Decrease timeframe

---

## 📞 **Need Help?**

**With Claude Code:**
```bash
claude-code

# Prompt:
"I want to generate reports for the last 4 weeks only. 
Can you modify generate_html_report.py?"
```

Claude Code will make the changes and explain what it did!

---

**Most Common Setting:** 4-6 weeks for phase-end planning

**Try it:** Change line 17 to `MONTHS_TO_INCLUDE = 1.5` (6 weeks) and regenerate!
