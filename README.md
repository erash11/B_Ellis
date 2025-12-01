# Force Plate Training Report Generator

**Simple web-based force plate analysis for coaching staff**

Built for Baylor University Athletics - B.A.I.R. Initiative

---

## 📋 What This Does

Analyzes force plate testing data (CMJ and IMTP) from ForceDecks and generates actionable training reports. The web app categorizes athletes into 7 performance categories and provides execution-style recommendations for coaching staff.

**Key Features:**
- ✅ Web-based interface - no command line needed
- ✅ Drag & drop file upload
- ✅ Instant report generation
- ✅ Download HTML, Text, or PDF reports
- ✅ Color-coded athlete priorities (🔴 Critical, 🟠 Warning, 🟡 Caution)
- ✅ Configurable team and phase settings

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: Streamlit, Pandas, NumPy, Plotly, and openpyxl

### Step 2: Launch the Web App

```bash
streamlit run generate_report_app.py
```

The app will automatically open in your browser at `http://localhost:8501`

### Step 3: Upload Your Data

1. **Upload CMJ data** (Countermovement Jump tests from ForceDecks)
2. **Upload IMTP data** (Isometric Mid-Thigh Pull tests from ForceDecks)
3. **Upload Roster** (Athlete names and positions)

Drag & drop files or click to browse.

### Step 4: Generate Report

1. Adjust team name and training phase in sidebar (optional)
2. Click the **"Generate Report"** button
3. Wait 30-60 seconds for processing
4. View report preview in browser

### Step 5: Download & Share

- **HTML Report** - Full interactive report for email/sharing
- **Text Report** - Simple text version for printing
- **PDF** - Use browser's Print-to-PDF feature (File → Print → Save as PDF)

---

## 📊 Exporting Data from ForceDecks

### CMJ Data Export

1. Open ForceDecks software
2. Navigate to **Reports → Export Data**
3. Select **CMJ (Countermovement Jump)**
4. Date range: Last 6 months
5. Include metrics:
   - Peak Power
   - RSI-modified
   - Contraction Time
   - Eccentric Mean Braking Force
   - Eccentric Braking RFD
6. Export as CSV

### IMTP Data Export

1. In ForceDecks → **Reports → Export Data**
2. Select **IMTP (Isometric Mid-Thigh Pull)**
3. Same 6-month date range
4. Include metrics:
   - Peak Vertical Force
   - Net Peak Vertical Force
   - Force at 50ms, 100ms, 200ms
   - Peak Vertical Force % (Asymmetry)
   - Start Time to Peak Force
5. Export as CSV

### Roster File

Create a CSV or Excel file with two columns:
- **Name** - Athlete full name (must match ForceDecks exactly)
- **Position** - Position abbreviation (WR, RB, OL, DL, LB, DB, etc.)

---

## 🎯 Understanding the Reports

### 7 Performance Categories

Athletes are categorized based on declining trends:

1. **Maximal Strength Capacity** - IMTP Peak Force declining
2. **Explosive Strength / RFD** - Early-phase RFD (50-200ms) declining
3. **Power Output** - CMJ Peak Power declining
4. **SSC Efficiency** - RSI-modified, Eccentric Braking RFD declining
5. **Eccentric Control & Braking** - Eccentric braking force declining
6. **Technical / Coordination** - Contraction time, time to peak force increasing
7. **Asymmetry / Limb Imbalance** - L-R asymmetry > 10%

### Severity Levels

- 🔴 **Critical** - Deviation > 2× SWC (immediate attention)
- 🟠 **Warning** - Deviation 1.5-2× SWC (monitor closely)
- 🟡 **Caution** - Deviation 1-1.5× SWC (be aware)
- 🟢 **Normal** - Within expected range

### Report Sections

- **Executive Summary** - Total athletes tested and percentage flagged
- **Category Breakdown** - Weight room and field recommendations
- **Athlete Lists** - Organized by category with severity levels
- **Coaching Priorities** - Top 3 actions for next training phase

---

## 🔄 Regular Usage

### When to Generate Reports

**✅ Good Times:**
- End of each training phase (4-6 weeks)
- Before planning next mesocycle
- After extended breaks (summer, winter)
- Before major competitions

**❌ Avoid:**
- Daily or weekly (not enough time to show trends)
- Mid-phase (disrupts planned programming)
- With < 5 tests per athlete

### Typical Workflow

1. **Phase Week 6:** Export latest data from ForceDecks
2. **Launch app:** `streamlit run generate_report_app.py`
3. **Upload files:** Drag & drop CMJ, IMTP, and Roster
4. **Generate report:** Click button and wait
5. **Review:** Check report preview in browser
6. **Download:** Save HTML and PDF versions
7. **Staff meeting:** Discuss findings and plan next phase
8. **Archive:** Save reports with date stamps

---

## 📁 Repository Files

### Essential Files

- **`generate_report_app.py`** - Streamlit web application (main tool)
- **`requirements.txt`** - Python dependencies
- **`STREAMLIT_QUICK_START.md`** - Detailed usage guide
- **`README.md`** - This file

### Documentation

- **`Force_Plate_Training_Report_Design.md`** - System design and decision rules

### Templates

- **`Training_Report_Mockup.html`** - Visual mockup for stakeholders

### Data Files (Your Files)

- **`*-CMJ_*.csv`** - Your CMJ test data
- **`*-IMTP_*.csv`** - Your IMTP test data
- **`*_Roster*.csv`** - Your athlete roster

---

## ⚙️ Configuration

### Adjust Settings in App

Use the sidebar to configure:
- **Team Name** (e.g., "Baylor Football")
- **Current Training Phase** (e.g., "Fall Training Block")
- **Next Phase** (e.g., "Winter Preparation Phase")

### Data Requirements

**Minimum for valid analysis:**
- At least **5 tests per athlete** over the analysis period
- **Consistent test conditions** (time of day, warmup)
- **6 months of data** recommended
- **Matching athlete names** across all three files

---

## 🐛 Troubleshooting

### App Won't Start

**Error: "streamlit is not recognized"**
```bash
pip install streamlit
```

**Error: "No module named 'pandas'"**
```bash
pip install -r requirements.txt
```

### Upload Issues

**"Invalid file format"**
- Ensure files are CSV format
- Check that columns are correctly named
- Re-export from ForceDecks if needed

**"No athletes found"**
- Verify athlete names match **exactly** between all 3 files
- Check for extra spaces or spelling differences
- Use consistent name format (First Last)

### Report Issues

**"No athletes flagged" or "Everyone flagged"**
- Check you have 5+ tests per athlete
- Verify data covers at least 3-4 months
- Ensure data quality (no major outliers)

**Athletes missing from report**
- Need minimum 5 tests to be included
- Check athlete name spelling matches roster
- Verify test dates are within analysis window

---

## 💡 Tips for Success

### First Time Users

1. **Test with your data files** - Make sure exports work correctly
2. **Review with sports science staff** - Verify categories make sense
3. **Start a staff meeting** - Don't make changes alone
4. **Keep it simple** - Focus on top 1-2 priorities

### Regular Users

1. **Export data consistently** - Same day each phase
2. **Archive old reports** - Label with date and phase
3. **Track trends** - Compare reports across phases
4. **Trust your judgment** - Reports inform, coaches decide

### Best Practices

- Generate reports at the **same point** each training phase
- Use for **phase planning**, not daily adjustments
- Focus on **execution style**, not exercise changes
- Share reports **before** staff planning meetings
- Archive reports for **longitudinal tracking**

---

## 📖 Additional Documentation

- **STREAMLIT_QUICK_START.md** - Step-by-step usage guide with screenshots
- **Force_Plate_Training_Report_Design.md** - Complete technical specification

---

## 🔐 Data Privacy

**Important:**
- Do NOT commit athlete data to public repositories
- Data files are listed in `.gitignore` by default
- Use password protection when emailing HTML reports
- Follow university FERPA/data protection policies
- Archive reports securely on Baylor servers

---

## 📞 Support

### Getting Help

1. Check **STREAMLIT_QUICK_START.md** for detailed instructions
2. Review **Force_Plate_Training_Report_Design.md** for system details
3. Contact Baylor Sports Science team for assistance
4. Contact IT for installation/deployment issues

### Common Questions

**Q: Can I use this for multiple teams?**
A: Yes! Just upload different roster files and data for each team.

**Q: How do I share reports with assistant coaches?**
A: Download the HTML file and email it. Opens in any browser.

**Q: Can this run on a server for the whole staff?**
A: Yes! Streamlit apps can be deployed to cloud or local servers. Contact IT.

**Q: What if I only have CMJ or only IMTP data?**
A: The app will analyze whatever data you provide, but results are best with both.

**Q: How do I create PDFs?**
A: View the HTML report in your browser, then File → Print → Save as PDF.

---

## 🚀 Deployment Options

### Option 1: Run Locally (Current)

Each coach runs on their own computer:
```bash
streamlit run generate_report_app.py
```

### Option 2: Deploy to Streamlit Cloud (Free)

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect GitHub and deploy
4. Share URL with coaching staff

### Option 3: Deploy to Baylor Server

Contact Baylor IT to host on internal server:
- Accessible via Baylor network
- No installation needed for coaches
- Single URL for entire staff

---

## 📄 License & Credits

**Built for:** Baylor University Athletics
**Initiative:** B.A.I.R. (Baylor A.I.R.)
**Created:** November 2024
**System Design:** Force plate decision framework based on SWC methodology

**Version:** 1.0 - Streamlit Web App

For questions or support, contact the Baylor Sports Science Team.
