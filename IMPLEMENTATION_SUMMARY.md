# Force Plate Decision Grid - Automation Package Summary

**Created for:** Baylor Athletics - B.A.I.R. Initiative  
**Date:** November 2024  
**Purpose:** Automate the Force Plate Decision Grid framework to make it accessible to coaching staff

---

## 📦 What's in This Package

This automation package contains everything you need to deploy an automated decision support system for your force plate data. Your colleague's framework has been translated into working code with multiple deployment options.

### Core Files

1. **force_plate_dashboard.py** (21 KB)
   - Complete Streamlit web application
   - Ready to run with demo data
   - 9-category status visualization
   - Automatic flagging and recommendations
   - Trend charts with SWC bands

2. **force_plate_automation_guide.md** (12 KB)
   - Comprehensive implementation guide
   - 4 deployment options (Power BI, Google Sheets, Streamlit, R Shiny)
   - Step-by-step roadmap
   - Architecture diagrams

3. **PowerBI_DAX_Measures.txt** (12 KB)
   - Production-ready DAX measures
   - All 9 categories implemented
   - Baseline, SWC, and severity calculations
   - Dashboard setup instructions

4. **data_mapping_template.md** (12 KB)
   - Column mapping guide for ForceDecks/Hawkin
   - Data preparation functions
   - Quality control checks
   - Troubleshooting common issues

5. **README.md** (7 KB)
   - Quick start guide
   - Deployment instructions
   - Customization examples

6. **requirements.txt**
   - Python dependencies for Streamlit app

---

## 🚀 Quick Start - Three Paths

### Path 1: Demo the Streamlit App (5 minutes)

```bash
pip install -r requirements.txt
streamlit run force_plate_dashboard.py
```

Opens a fully functional dashboard with simulated athlete data. Use this to:
- Show your colleague what's possible
- Get coaching staff feedback on UI/UX
- Test the decision logic flow
- Demonstrate to stakeholders

### Path 2: Power BI Integration (If already using Power BI)

1. Open `PowerBI_DAX_Measures.txt`
2. Copy DAX measures into your Power BI model
3. Connect to your force plate data source
4. Build dashboard pages following the guide
5. Set up automated refresh + email alerts

**Best for:** Organizations with existing Power BI infrastructure

### Path 3: Google Sheets (Lowest technical barrier)

1. Export ForceDecks data to CSV
2. Upload to Google Drive
3. Create sheets following the automation guide
4. Use Apps Script for daily automation
5. Share with coaching staff

**Best for:** Quick deployment, minimal IT dependency

---

## 🎯 What the System Does

### Automated Analysis
- ✅ Calculates athlete-specific baselines (6-month rolling average)
- ✅ Computes Smallest Worthwhile Change (0.2 × SD)
- ✅ Detects sustained trends (≥3 tests beyond SWC)
- ✅ Classifies severity (Green/Yellow/Red)
- ✅ Evaluates all 9 decision categories
- ✅ Prioritizes interventions when multiple flags occur

### For Coaches
- **Traffic light dashboard**: Quick visual status across all athletes
- **Automatic recommendations**: Weight room + field prescriptions
- **Re-eval scheduling**: Calculated timelines based on category
- **Trend visualization**: Metric history with SWC bands
- **Pattern detection**: Cluster logic (fatigue states, strategy shifts)

### For Sport Scientists
- **Transparent calculations**: No black box, all logic visible
- **Customizable thresholds**: Adjust SWC multipliers by sport/position
- **Quality control**: Flags physiologically impossible values
- **Audit trail**: Track decisions and outcomes

---

## 📊 How the Decision Logic Works

### Example: Maximal Strength Category

**Input Data:**
- Current IMTP Peak Force: 2,800 N
- Baseline (6-month avg): 3,100 N
- Standard Deviation: 200 N

**Calculations:**
```
SWC = 0.2 × 200 = 40 N
Deviation = 3,100 - 2,800 = 300 N

Classification:
  300 > 2×40 (80) → RED FLAG
  
Interpretation: "Loss of total force output or neural drive"
Recommendation: "Heavy isometrics / TUT, Cluster Sets (≥80% 1RM)"
Field Work: "Resisted Sprints (50-60% vdec)"
Re-eval: 7-10 days
```

### Cluster Logic Example: Systemic Fatigue

**Conditions:**
- RSI-mod drops >10% from baseline AND
- Peak Power drops >10% from baseline

**Result:**
- RED FLAG: "Global CNS / metabolic fatigue"
- Action: "DELOAD: Reduce volume 20%, active recovery"
- Re-eval: 10-14 days

---

## 🔧 Customization Options

### Adjust Sensitivity

Make the system more or less sensitive to changes:

```python
# More conservative (fewer flags)
SWC = 0.3 * baseline_std  # Instead of 0.2

# More sensitive (more flags)
SWC = 0.15 * baseline_std
```

### Sport-Specific Thresholds

```python
SPORT_MODIFIERS = {
    'Football': {
        'Big': {'strength_weight': 1.5},
        'Skill': {'rfd_weight': 1.3}
    },
    'Basketball': {'ssc_weight': 1.2}
}
```

### Custom Re-Eval Windows

Edit the `DECISION_RULES` dictionary to match your training cycles:

```python
1: {
    'category': 'Maximal Strength',
    'reeval_days': 10  # Change from 7 to 10
}
```

---

## 📈 Implementation Roadmap

### Week 1-2: Foundation
- [ ] Export sample data from ForceDecks/Hawkin
- [ ] Complete data mapping using template
- [ ] Test data preparation pipeline
- [ ] Validate baseline calculations

### Week 3-4: System Build
- [ ] Choose deployment platform (Streamlit/Power BI/Sheets)
- [ ] Implement decision engine
- [ ] Build dashboard visualizations
- [ ] Test with historical data

### Week 5-6: Validation
- [ ] Parallel run alongside manual interpretation
- [ ] Collect coach feedback on UI/recommendations
- [ ] Refine thresholds based on population data
- [ ] Document edge cases

### Week 7-8: Automation
- [ ] Set up data pipelines (daily refresh)
- [ ] Configure email alerts for red flags
- [ ] Create re-eval reminder system
- [ ] Integrate with training management software

### Week 9-10: Training & Deployment
- [ ] Conduct staff training sessions
- [ ] Create user documentation
- [ ] Go live with pilot group (1-2 teams)
- [ ] Monitor usage and accuracy

### Week 11+: Iteration
- [ ] Collect outcome data (did interventions work?)
- [ ] Refine decision rules based on results
- [ ] Scale to full department
- [ ] Build case studies

---

## 🎓 Training Your Staff

### For Coaches (30-minute session)

**Learning objectives:**
1. How to read the traffic light dashboard
2. What each category means in plain English
3. How to interpret recommendations
4. When to override the system (use coaching judgment)

**Demo flow:**
- Show athlete with all green → "Keep doing what you're doing"
- Show athlete with yellow flag → "Monitor, continue programming"
- Show athlete with red flag → "Intervention needed, here's what to do"
- Show cluster flag (systemic fatigue) → "This takes priority, time to deload"

### For Sport Scientists (60-minute session)

**Learning objectives:**
1. How SWC is calculated (and why 0.2 × SD)
2. How to adjust thresholds for specific populations
3. How to troubleshoot data quality issues
4. How to add new metrics to the system

**Technical deep dive:**
- Walk through the decision engine code
- Explain rolling average vs. fixed baseline
- Show how cluster logic works
- Demonstrate customization options

---

## 🛠️ Technical Architecture

### Data Flow

```
┌─────────────────────┐
│  Force Plate Test   │
│  (ForceDecks/Hawkin)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Data Export/API   │
│   (CSV or Real-time)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Data Preparation   │
│  • Column mapping   │
│  • Quality control  │
│  • Derived metrics  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Decision Engine    │
│  • Baseline calc    │
│  • SWC calculation  │
│  • Trend detection  │
│  • Category flagging│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Dashboard Output  │
│  • Visual status    │
│  • Recommendations  │
│  • Trend charts     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Actions/Alerts     │
│  • Email coaches    │
│  • Schedule re-eval │
│  • Log decisions    │
└─────────────────────┘
```

### System Requirements

**Minimal:**
- Python 3.8+ (for Streamlit) OR
- Power BI Desktop (for Power BI) OR
- Google Workspace account (for Sheets)

**Recommended:**
- 4 GB RAM
- Modern web browser (Chrome/Firefox/Edge)
- Stable internet connection

**For Production Deployment:**
- Server or cloud hosting (if self-hosting Streamlit)
- Database (optional, for large datasets)
- Email server (for automated alerts)

---

## 💡 Success Factors

### What Makes This Work

1. **Coaching Buy-In**
   - Frame as "decision support" not "replacement"
   - Allow overrides with notes
   - Transparent logic builds trust

2. **Data Quality**
   - Consistent testing protocols
   - Trained technicians
   - Regular equipment calibration

3. **Appropriate Thresholds**
   - Use YOUR population's baselines
   - Adjust for sport/position differences
   - Refine based on outcomes

4. **Continuous Improvement**
   - Log whether interventions worked
   - Iterate on decision rules
   - Add context the system can't know

### Common Pitfalls to Avoid

❌ Trusting the system blindly without coaching judgment  
❌ Using generic SWC values from literature instead of your population  
❌ Not accounting for offseason vs. in-season baselines  
❌ Ignoring athletes who chronically live in yellow/red zones  
❌ Over-complicating with too many custom rules at first  

---

## 📞 Next Steps

### Immediate Actions (This Week)

1. **Review the Streamlit demo**
   - Run `streamlit run force_plate_dashboard.py`
   - Show to your colleague
   - Get feedback on UI/flow

2. **Export sample data**
   - Get 20-30 tests from multiple athletes
   - Use the data mapping template
   - Test the preparation pipeline

3. **Choose deployment path**
   - Power BI (if already infrastructure)
   - Streamlit (for standalone app)
   - Google Sheets (for simplicity)

### This Month

4. **Build proof of concept**
   - Connect your actual data
   - Validate decision logic with known cases
   - Demo to coaching staff

5. **Gather requirements**
   - What features do coaches need most?
   - What's the desired workflow?
   - Mobile access required?

### Next Quarter

6. **Pilot deployment**
   - Start with 1-2 teams
   - Run parallel with manual interpretation
   - Collect feedback and refine

7. **Full deployment**
   - Scale to entire department
   - Integrate with other systems
   - Document case studies

---

## 📚 Additional Resources

### Included in This Package

- [x] Streamlit dashboard (working prototype)
- [x] Power BI DAX measures (production-ready)
- [x] Data mapping template (ForceDecks/Hawkin)
- [x] Implementation guide (4 deployment options)
- [x] README (quick start)

### Not Included (But Easy to Add)

- [ ] Mobile app version
- [ ] Integration with TeamBuildr/Bridge
- [ ] Predictive modeling (injury risk)
- [ ] Automated report generation (PDF export)
- [ ] Multi-language support

---

## 🤝 Collaboration Opportunities

This framework is designed to be:
- **Shareable**: Other institutions could benefit
- **Researchable**: Validate thresholds, test interventions
- **Publishable**: Novel approach to force plate interpretation

Consider:
- Presenting at NSCA/CSCCa conferences
- Publishing validation study
- Sharing with B.A.I.R. consortium partners
- Contributing to open-source sports science tools

---

## 📝 Final Notes

This automation package represents your colleague's thoughtful decision framework translated into working software. The goal wasn't to create a black box that makes decisions FOR coaches, but a transparent tool that makes their decision-making MORE CONSISTENT and FASTER.

The system should:
- ✅ Reduce decision fatigue during busy training weeks
- ✅ Catch trends humans might miss
- ✅ Standardize interpretation across staff
- ✅ Free up time for higher-level coaching

But it should NOT:
- ❌ Replace coaching expertise and context
- ❌ Ignore athlete feedback and feel
- ❌ Be trusted blindly without validation
- ❌ Prevent necessary clinical judgment

Start simple. Deploy the core system. Gather feedback. Iterate. Add complexity only when needed.

---

**Questions or need help with implementation?**

This package gives you everything to get started, but every organization's data infrastructure is unique. Don't hesitate to customize heavily based on your specific needs and constraints.

Good luck with the deployment! 🚀
