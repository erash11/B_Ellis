# Baylor Football Force Plate Training Report System

**Automated force plate data analysis and training report generation**

Built for Baylor University Athletics - B.A.I.R. Initiative

---

## 📋 Overview

This system analyzes force plate testing data (CMJ and IMTP) from ForceDecks/Hawkin software and generates actionable training reports for coaching staff. The reports categorize athletes into 7 performance categories and provide execution-style recommendations without prescribing specific exercises.

### What This System Does:

- ✅ Analyzes 6 months of CMJ and IMTP force plate data
- ✅ Identifies declining performance trends using Smallest Worthwhile Change (SWC) methodology
- ✅ Categorizes athletes into 7 performance categories
- ✅ Generates professional HTML and text reports
- ✅ Provides actionable weight room and field recommendations
- ✅ Prioritizes athletes by severity (Critical 🔴, Warning 🟠, Caution 🟡)

---

## 🚀 Quick Start Guide

### Option 1: Run Demo Report (Sample Data)

Perfect for understanding how the system works before using real data.

```bash
# Install dependencies
pip install pandas numpy openpyxl

# Generate demo report with sample data
python demo_report.py
```

This creates:
- `Baylor_Training_Report_DEMO.html` - Interactive report
- `Baylor_Training_Report_DEMO.txt` - Text version

**Open the HTML file in your browser to view the report.**

### Option 2: Run Real Data Report

Use your actual ForceDecks data.

```bash
# Ensure you have the required data files:
# - CMJ export CSV
# - IMTP export CSV
# - Roster file with positions

# Generate real report
python generate_real_report.py
```

This creates:
- `Baylor_Training_Report_REAL.html` - Interactive report with real data
- `Baylor_Training_Report_REAL.txt` - Text version

---

## 📊 Complete Workflow: From ForceDecks to Report

### Step 1: Export Data from ForceDecks

**Export CMJ Tests:**
1. Open ForceDecks software
2. Navigate to **Reports** → **Export Data**
3. Select test type: **CMJ (Countermovement Jump)**
4. Date range: Last 6 months
5. Include these metrics:
   - Peak Power
   - RSI-modified
   - Contraction Time
   - Eccentric Mean Braking Force
   - Eccentric Braking RFD
6. Export as CSV
7. Save as: `YYYY-MM-DD-CMJ_Last6mnths.csv`

**Export IMTP Tests:**
1. In ForceDecks, go to **Reports** → **Export Data**
2. Select test type: **IMTP (Isometric Mid-Thigh Pull)**
3. Same date range as CMJ
4. Include these metrics:
   - Peak Vertical Force
   - Net Peak Vertical Force
   - Force at 50ms, 100ms, 200ms
   - Peak Vertical Force % (Asymmetry)
   - Start Time to Peak Force
5. Export as CSV
6. Save as: `YYYY-MM-DD-IMTP_Last6mnths.csv`

**Prepare Roster File:**
1. Create Excel or CSV with two columns:
   - `Name` - Athlete full name (must match ForceDecks exactly)
   - `Position` - Position abbreviation (WR, RB, OL, DL, etc.)
2. Save as: `YYYY-MM-DD_FB_Roster.csv`

### Step 2: Place Files in Repository

Copy all three files to your B_Ellis project folder:
```
B_Ellis/
├── 2025-11-27-CMJ_Last6mnths.csv
├── 2025-11-27-IMTP_Last6mnths.csv
├── 2025-11-27_FB_Roster.csv
└── generate_real_report.py
```

### Step 3: Update File Paths (if needed)

If your filenames are different, edit `generate_real_report.py`:

```python
# Update these lines near the top of the file:
ROSTER_FILE = 'YOUR_ROSTER_FILE.csv'
CMJ_FILE = 'YOUR_CMJ_FILE.csv'
IMTP_FILE = 'YOUR_IMTP_FILE.csv'
```

### Step 4: Generate Reports

```bash
python generate_real_report.py
```

Output:
```
Loading data files...
✓ Loaded roster: 115 athletes
✓ Loaded CMJ data: 1,875 tests from 113 athletes
✓ Loaded IMTP data: 1,979 tests from 156 athletes

Categorizing athletes...
✓ Found 7 categories with issues
✓ Flagged 114 athletes needing intervention

✓ HTML report saved: Baylor_Training_Report_REAL.html
✓ Text report saved: Baylor_Training_Report_REAL.txt
```

### Step 5: Review and Share Reports

**Open the HTML report:**
- Double-click `Baylor_Training_Report_REAL.html`
- Opens in your default browser
- Professional formatting with full analysis

**Share with coaching staff:**
- Email the HTML file
- Print the text version
- Present in team meetings

---

## 🎯 Understanding the Reports

### 7 Performance Categories

The system analyzes athletes across these categories:

**Category 1: Maximal Strength Capacity**
- Metrics: IMTP Peak Force, Net Peak Vertical Force
- Declining maximal force production

**Category 2: Explosive Strength / RFD**
- Metrics: Force at 50ms, 100ms, 200ms
- Early-phase rate of force development declining

**Category 3: Power Output**
- Metrics: CMJ Peak Power
- Reduced power production in jumping

**Category 4: SSC Efficiency**
- Metrics: RSI-modified, Eccentric Braking RFD
- Stretch-shortening cycle compromised

**Category 5: Eccentric Control & Braking**
- Metrics: Eccentric Mean Braking Force
- Reduced ability to absorb force

**Category 6: Technical / Coordination**
- Metrics: Contraction Time, Time to Peak Force
- Movement efficiency declining

**Category 7: Asymmetry / Limb Imbalance**
- Metrics: L-R Force Asymmetry
- Imbalances > 10% between limbs

### Severity Levels

Each athlete is classified by severity:

- 🔴 **Critical** - Deviation > 2× SWC (Immediate attention needed)
- 🟠 **Warning** - Deviation 1.5-2× SWC (Monitor closely)
- 🟡 **Caution** - Deviation 1-1.5× SWC (Be aware)
- 🟢 **Normal** - Within SWC range (No intervention needed)

### Report Sections

**Executive Summary:**
- Total athletes tested
- Number and percentage flagged
- Categories with issues

**Category Breakdown:**
- Weight room recommendations
- Field recommendations
- List of flagged athletes
- Distribution by severity
- Interpretation and execution notes

**Coaching Recommendations:**
- Top 3 priorities for next phase
- Specific action items

---

## 🔄 Regular Usage Workflow

### Monthly/Phase-End Process

1. **Export latest data** from ForceDecks (see Step 1 above)
2. **Update file paths** in `generate_real_report.py` if using new filenames
3. **Run report generation**: `python generate_real_report.py`
4. **Review reports** with coaching staff
5. **Plan next phase** based on recommendations
6. **Archive reports** with date stamps for historical tracking

### When to Generate Reports

**Recommended timing:**
- End of each training phase (4-6 weeks)
- Before major competitions
- After extended breaks (summer, winter)
- When significant performance changes are observed

**Not recommended:**
- Daily or weekly (too much noise, not enough signal)
- Mid-phase (disrupts planned programming)

---

## 📁 Repository Files

### Report Generation Scripts

- **`demo_report.py`** - Generates demo reports with sample data
- **`generate_real_report.py`** - Processes real ForceDecks data and generates reports
- **`generate_training_report.py`** - Original training report generator (legacy)
- **`generate_html_report.py`** - HTML report generator (legacy)

### Interactive Dashboard

- **`force_plate_dashboard.py`** - Streamlit web dashboard for interactive exploration

### Documentation

- **`README.md`** - This file - Complete usage guide
- **`START_HERE.md`** - Quick navigation guide
- **`Force_Plate_Training_Report_Design.md`** - Complete system design and decision rules
- **`IMPLEMENTATION_SUMMARY.md`** - 10-week implementation roadmap
- **`data_mapping_template.md`** - ForceDecks column mapping reference
- **`TIMEFRAME_ADJUSTMENT_GUIDE.md`** - How to adjust report timeframes
- **`force_plate_automation_guide.md`** - Multiple deployment options

### HTML Templates

- **`Training_Report_Mockup.html`** - Visual mockup shown to stakeholders
- **`Baylor_Training_Report_HTML.html`** - Example full report

### Generated Reports (After Running Scripts)

- **`Baylor_Training_Report_DEMO.html`** - Demo report with sample data
- **`Baylor_Training_Report_DEMO.txt`** - Demo report text version
- **`Baylor_Training_Report_REAL.html`** - Real report with your data
- **`Baylor_Training_Report_REAL.txt`** - Real report text version

### Data Files (After Upload)

- **`2025-11-27-CMJ_Last6mnthscsv.csv`** - CMJ test data
- **`2025-11-27-IMTP_Last6mnthscsv.csv`** - IMTP test data
- **`2025-11-27_FB_Roster_2025_ER.csv`** - Athlete roster with positions

---

## ⚙️ Customization Options

### Adjust Timeframe

Edit `generate_real_report.py`:

```python
# Change the number of months to include
MONTHS_TO_INCLUDE = 6  # Change to 3, 6, 9, or 12
```

### Adjust Severity Thresholds

Edit the `SEVERITY_THRESHOLDS` dictionary:

```python
SEVERITY_THRESHOLDS = {
    'red': 2.0,      # Critical (change to 2.5 for less sensitive)
    'orange': 1.5,   # Warning
    'yellow': 1.0    # Caution (change to 1.2 for more sensitive)
}
```

### Modify Team Information

Edit configuration variables:

```python
TEAM_NAME = "Baylor Football"  # Change team name
TRAINING_PHASE = "Fall Training Block"  # Current phase name
NEXT_PHASE = "Winter Preparation Phase"  # Upcoming phase
```

### Add Custom Categories

Extend the `DECISION_RULES` dictionary in `generate_real_report.py`:

```python
8: {
    'name': 'CUSTOM CATEGORY',
    'trend_desc': 'Description of what you're tracking',
    'metrics': ['Your_Metric_Name'],
    'trend': 'decrease',  # or 'increase'
    'wr_suggestions': ['Recommendation 1', 'Recommendation 2'],
    'field_suggestions': ['Field drill 1', 'Field drill 2'],
    'interpretation': 'What this means',
    'execution_note': 'How to implement'
}
```

---

## 🔧 Advanced Usage

### Running Interactive Streamlit Dashboard

For real-time exploration and individual athlete analysis:

```bash
pip install streamlit plotly
streamlit run force_plate_dashboard.py
```

Opens interactive web dashboard at `http://localhost:8501`

### Batch Processing Multiple Teams

Create a wrapper script:

```python
teams = ['Football', 'Basketball', 'Baseball']
data_paths = {
    'Football': {'cmj': 'fb_cmj.csv', 'imtp': 'fb_imtp.csv', 'roster': 'fb_roster.csv'},
    'Basketball': {'cmj': 'bb_cmj.csv', 'imtp': 'bb_imtp.csv', 'roster': 'bb_roster.csv'},
}

for team in teams:
    # Update file paths
    # Run generate_real_report.py
    # Save with team-specific names
```

### Automating Report Generation

**Windows Task Scheduler:**
Create a batch file `run_report.bat`:
```batch
@echo off
cd C:\Path\To\B_Ellis
python generate_real_report.py
echo Report generated at %date% %time% >> report_log.txt
```

Schedule to run weekly/monthly in Task Scheduler.

**Mac/Linux Cron:**
```bash
# Edit crontab
crontab -e

# Add line to run every Monday at 8am
0 8 * * 1 cd /path/to/B_Ellis && python generate_real_report.py
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue: "ModuleNotFoundError: No module named 'pandas'"**
```bash
pip install pandas numpy openpyxl
```

**Issue: "FileNotFoundError: No such file or directory"**
- Verify data files are in the same folder as the script
- Check filenames match exactly (including .csv extension)
- Update file paths in `generate_real_report.py`

**Issue: "No athletes flagged" or "All athletes flagged"**
- Check SWC threshold sensitivity
- Verify data quality (look for outliers or missing data)
- Ensure sufficient test history (need 5+ tests per athlete)

**Issue: Excel file won't open as CSV**
- Rename file extension to `.xlsx` instead of `.csv`
- Or export from Excel as true CSV format

**Issue: Athlete names don't match between files**
- Ensure exact spelling match (case-sensitive)
- Check for extra spaces before/after names
- Use consistent name format (First Last vs Last, First)

---

## 📈 Data Quality Guidelines

### Minimum Requirements

- **5+ tests per athlete** over the analysis period
- **Consistent test conditions** (time of day, warmup protocol)
- **Valid test reps** (exclude failed attempts)
- **Complete metric capture** for all required fields

### Red Flags to Investigate

- Sudden jumps/drops >50% between consecutive tests
- Asymmetry values >30%
- Force values <500N or >10,000N (check units)
- Missing data for >20% of athletes

### Best Practices

- Test at same time of day (avoid fatigue/circadian effects)
- Standardize warmup protocol
- Train staff on proper test administration
- Regularly calibrate force plates
- Exclude tests with protocol violations

---

## 📚 Additional Resources

### Documentation Files

- **START_HERE.md** - Quick navigation to get oriented
- **Force_Plate_Training_Report_Design.md** - Complete technical specification
- **data_mapping_template.md** - Column mapping guide for your ForceDecks exports
- **TIMEFRAME_ADJUSTMENT_GUIDE.md** - How to modify analysis windows
- **force_plate_automation_guide.md** - 4 deployment pathways (Power BI, Google Sheets, etc.)

### Example Reports

- Open `Training_Report_Mockup.html` to see the visual design
- Open `Baylor_Training_Report_REAL.html` to see actual report with data

---

## 🎓 Training Your Staff

### For Coaches (Report Consumers)

**Key points to communicate:**
1. Reports are generated every 4-6 weeks (phase-end)
2. Focus on execution style, not exercise selection
3. Recommendations don't replace coaching judgment
4. Color codes indicate urgency: 🔴 Critical → 🟠 Warning → 🟡 Caution
5. All athletes in a category get the same general approach

### For Sports Science Staff (Report Generators)

**Workflow checklist:**
1. [ ] Export CMJ and IMTP data from ForceDecks
2. [ ] Update roster file with current athletes
3. [ ] Place files in B_Ellis folder
4. [ ] Run `python generate_real_report.py`
5. [ ] Review HTML report for quality/errors
6. [ ] Share with coaching staff
7. [ ] Archive report with date stamp

---

## 🔐 Data Privacy & Security

### Recommendations

- **Do not commit data files to public repositories**
- Store sensitive data locally or on secure servers
- Add data files to `.gitignore`:
  ```
  *.csv
  *_REAL.html
  *_REAL.txt
  ```
- Use password protection for HTML reports if emailing
- Follow university FERPA/data protection policies

---

## 📞 Support & Maintenance

### Getting Help

1. **Check documentation** in this repository first
2. **Review example files** (demo reports, mockups)
3. **Test with demo data** to isolate issues
4. **Contact sports science team** for Baylor-specific questions

### System Maintenance

**Monthly:**
- Review report accuracy with coaching feedback
- Update roster file with new athletes
- Archive previous reports

**Quarterly:**
- Validate SWC thresholds against outcomes
- Review athlete categorization accuracy
- Update recommendations based on staff input

**Annually:**
- Full system audit
- Update decision rules if needed
- Retrain staff on any changes

---

## 🚀 Future Enhancements

**Potential additions:**
- Automated email distribution
- Integration with training management software
- Longitudinal tracking dashboards
- Predictive injury risk modeling
- Mobile app for coaches
- Multi-sport expansion

---

## 📄 License & Attribution

**Built for:** Baylor University Athletics - B.A.I.R. Initiative
**Created:** November 2024
**System Design:** Force plate decision framework based on SWC methodology
**Report Generation:** Automated Python-based analysis pipeline

For questions or contributions, contact the Baylor Sports Science team.
