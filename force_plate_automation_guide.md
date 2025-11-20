# Force Plate Decision Grid - Automation Implementation Guide

## Overview
This guide provides multiple automation pathways to make the Force Plate Decision Grid accessible to coaching staff without requiring manual interpretation.

---

## Option 1: Power BI Dashboard (Recommended for Baylor)
**Best for**: Organizations already using Power BI with technical support available

### Architecture
```
ForceDecks/Hawkin → CSV Export → OneDrive/SharePoint → Power BI Dataflow → Dashboard
                                                                ↓
                                                    Decision Engine (DAX/M)
                                                                ↓
                                        Coach View: Traffic Light + Recommendations
```

### Implementation Steps

#### Step 1: Data Connection
- Set up automated CSV exports from ForceDecks to shared OneDrive folder
- Create Power BI dataflow that refreshes daily at 6 AM
- Map metrics to standardized column names

#### Step 2: DAX Measures for Decision Logic
```dax
// Calculate SWC (0.2 × SD method)
SWC_IMTP_PeakForce = 
VAR AthleteBaseline = 
    CALCULATE(
        AVERAGE('ForcePlate'[IMTP_Peak_Force]),
        DATESINPERIOD('Calendar'[Date], MAX('Calendar'[Date]), -6, MONTH)
    )
VAR AthleteSD = 
    CALCULATE(
        STDEV.P('ForcePlate'[IMTP_Peak_Force]),
        DATESINPERIOD('Calendar'[Date], MAX('Calendar'[Date]), -6, MONTH)
    )
RETURN 0.2 * AthleteSD

// Detect sustained trend
Flag_MaxStrength = 
VAR CurrentValue = AVERAGE('ForcePlate'[IMTP_Peak_Force])
VAR Baseline = [Baseline_IMTP_PeakForce]
VAR SWC = [SWC_IMTP_PeakForce]
VAR Deviation = ABS(CurrentValue - Baseline)
VAR Severity = 
    SWITCH(
        TRUE(),
        Deviation > 2 * SWC, "Red",
        Deviation > 1.5 * SWC, "Yellow",
        "Green"
    )
RETURN Severity

// Cluster detection (Fatigue State)
Flag_FatigueCluster = 
VAR RSI_Drop = [RSI_mod_Current] < [RSI_mod_Baseline] * 0.9
VAR Power_Drop = [PeakPower_Current] < [PeakPower_Baseline] * 0.9
VAR IsFlagged = RSI_Drop && Power_Drop
RETURN 
    IF(IsFlagged, 
       "🔴 SYSTEMIC FATIGUE: Deload -20%, Active Recovery", 
       BLANK()
    )
```

#### Step 3: Dashboard Layout
**Page 1: Team Overview**
- Heat map: Athletes × Categories (color-coded by severity)
- Quick filters: Sport, Position, Date Range
- Summary cards: Total red flags, yellow flags, athletes needing re-eval

**Page 2: Individual Athlete Deep Dive**
- Profile header: Name, Sport, Position, Last test date
- 9-category status grid with traffic lights
- Trend charts (4-week rolling avg) for flagged metrics
- **Action Panel**: 
  - Priority intervention (if multiple flags)
  - Weight room prescription
  - Field prescription
  - Re-eval date (auto-calculated)
  - Notes field for coach override

**Page 3: Metric Trends**
- Line charts for all athletes in a sport/group
- SWC bands visualized as shaded regions
- Click athlete → drillthrough to individual view

### Automation Features
- **Daily refresh**: New test data auto-processed overnight
- **Email alerts**: Power Automate sends digest to coaching staff when athletes move to Red
- **Re-eval reminders**: Athletes due for re-test appear in "Action Needed" queue

---

## Option 2: Google Sheets + Apps Script (Low-Tech, High Access)
**Best for**: Staff who live in Google Workspace, minimal IT dependency

### Architecture
```
ForceDecks CSV → Google Drive → Apps Script → Analysis Sheet → Dashboard Tab
```

### Implementation

#### File Structure
1. **Data Import Sheet**: Raw CSV dumps
2. **Athlete Profiles**: Baseline values, rolling averages
3. **Decision Engine**: Lookup tables + formulas
4. **Coach Dashboard**: Visual summary

#### Key Formulas
```
// SWC Calculation (in Athlete Profile sheet)
=0.2 * STDEV(QUERY(DataImport!A:Z, 
    "SELECT F WHERE B = '"&A2&"' AND C >= date '"&TEXT(TODAY()-180,"yyyy-mm-dd")&"'"))

// Traffic Light Logic
=IF(ABS(Current - Baseline) > 2*SWC, "🔴", 
    IF(ABS(Current - Baseline) > 1.5*SWC, "🟡", "🟢"))

// Intervention Lookup
=IFERROR(VLOOKUP(FlaggedCategory, DecisionGrid!A:G, 5, FALSE), "No action needed")
```

#### Apps Script Automation
```javascript
function dailyDataRefresh() {
  // 1. Import new CSVs from Drive folder
  // 2. Append to master data sheet
  // 3. Recalculate rolling averages
  // 4. Update dashboard
  // 5. Send notifications for new red flags
  
  var sheet = SpreadsheetApp.getActiveSpreadsheet();
  // ... implementation
}

function sendCoachAlerts() {
  var athletes = getRedFlagAthletes();
  athletes.forEach(function(athlete) {
    MailApp.sendEmail({
      to: athlete.coachEmail,
      subject: "Force Plate Alert: " + athlete.name,
      body: generateAlertEmail(athlete)
    });
  });
}

// Set up daily trigger
function createTrigger() {
  ScriptApp.newTrigger('dailyDataRefresh')
    .timeBased()
    .atHour(6)
    .everyDays(1)
    .create();
}
```

---

## Option 3: Python Web App (Streamlit)
**Best for**: Teams with Python expertise, desire for custom features

### Why Streamlit?
- Rapid development (50-100 lines of code)
- Native plotting (Plotly integration)
- Can host on Streamlit Cloud (free) or internal server
- Easy authentication integration

### App Structure
```python
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from decision_engine import ForcePlateDecisionEngine  # Our class from earlier

st.set_page_config(page_title="Force Plate Decision Grid", layout="wide")

# Sidebar: Filters
sport = st.sidebar.selectbox("Sport", ["All", "Football", "Basketball", "Track"])
athlete = st.sidebar.selectbox("Athlete", get_athlete_list(sport))

# Main Dashboard
col1, col2, col3 = st.columns(3)
col1.metric("Red Flags", count_red_flags(athlete))
col2.metric("Days Since Last Test", days_since_test(athlete))
col3.metric("Next Re-Eval", next_reeval_date(athlete))

# Category Status Grid
st.subheader("9-Category Status")
fig = create_status_heatmap(athlete)
st.plotly_chart(fig)

# Recommendations Panel
flags = engine.check_category_flags(get_athlete_data(athlete))
if flags:
    st.error("⚠️ Interventions Needed")
    for flag in flags:
        with st.expander(f"{flag['category']} - {flag['severity'].upper()}"):
            st.write(f"**Interpretation**: {flag['interpretation']}")
            st.write(f"**Weight Room**: {flag['wr_rx']}")
            st.write(f"**Field**: {flag['field_rx']}")
            st.write(f"**Re-evaluate**: {flag['reeval_date']}")
else:
    st.success("✅ All systems normal")

# Trend Visualization
st.subheader("Metric Trends (4-Week Rolling)")
selected_metric = st.selectbox("Metric", ["IMTP Peak Force", "RSI-mod", "Peak Power"])
fig = plot_trend_with_swc(athlete, selected_metric)
st.plotly_chart(fig)
```

### Deployment Options
1. **Streamlit Cloud** (Free): Public or password-protected
2. **Internal Server**: Deploy on Baylor's infrastructure
3. **Docker Container**: Portable across environments

---

## Option 4: R Shiny Dashboard
**Best for**: Teams already using R for analytics

### Key Advantages
- Seamless integration with existing R workflows
- Excellent statistical packages (already familiar to sport scientists)
- Can embed into RStudio Connect for enterprise deployment

### Sample Structure
```r
library(shiny)
library(tidyverse)
library(plotly)

ui <- fluidPage(
  titlePanel("Force Plate Decision Grid"),
  
  sidebarLayout(
    sidebarPanel(
      selectInput("athlete", "Select Athlete:", choices = athlete_list),
      dateRangeInput("date_range", "Date Range:", start = Sys.Date() - 180),
      actionButton("refresh", "Refresh Data")
    ),
    
    mainPanel(
      tabsetPanel(
        tabPanel("Status Overview", 
          valueBoxOutput("red_flags"),
          plotlyOutput("category_heatmap")
        ),
        tabPanel("Interventions",
          uiOutput("recommendations")
        ),
        tabPanel("Trends",
          plotlyOutput("metric_trends")
        )
      )
    )
  )
)

server <- function(input, output, session) {
  
  athlete_data <- reactive({
    load_force_plate_data(input$athlete, input$date_range)
  })
  
  flags <- reactive({
    evaluate_decision_grid(athlete_data())
  })
  
  output$category_heatmap <- renderPlotly({
    create_status_viz(flags())
  })
  
  output$recommendations <- renderUI({
    generate_intervention_cards(flags())
  })
}

shinyApp(ui = ui, server = server)
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Finalize metric naming conventions across platforms
- [ ] Establish baseline values for all current athletes
- [ ] Calculate sport-specific SWC thresholds
- [ ] Document cluster interpretation rules

### Phase 2: Core Engine (Weeks 3-4)
- [ ] Build decision logic (Python class or DAX measures)
- [ ] Create test cases for all 9 categories
- [ ] Validate against historical data
- [ ] Get colleague buy-in on logic

### Phase 3: Dashboard Build (Weeks 5-6)
- [ ] Choose platform (Power BI, Sheets, Streamlit, Shiny)
- [ ] Build UI mockups
- [ ] Implement visualizations
- [ ] Add intervention text

### Phase 4: Automation (Weeks 7-8)
- [ ] Set up data pipelines
- [ ] Schedule automated refreshes
- [ ] Configure email notifications
- [ ] Create re-eval reminder system

### Phase 5: Validation & Training (Weeks 9-10)
- [ ] Parallel run with manual interpretation
- [ ] Collect coach feedback
- [ ] Refine thresholds and logic
- [ ] Conduct staff training sessions

### Phase 6: Deployment (Week 11+)
- [ ] Go live with full team
- [ ] Monitor usage and accuracy
- [ ] Iterate based on real-world use
- [ ] Document case studies

---

## Data Pipeline Architecture

### Minimal Viable Pipeline
```
1. Export CSVs from ForceDecks/Hawkin (manual or automated)
2. Save to shared folder (OneDrive/Google Drive)
3. Trigger script/dataflow refresh
4. Dashboard updates
5. Coaches view updates
```

### Advanced Pipeline
```
1. API connection to force plate software
2. Real-time data streaming to database
3. Event-driven processing (new test → immediate analysis)
4. Push notifications to coach mobile devices
5. Integration with training management system (TeamBuildr, etc.)
6. Bi-directional feedback loop (coach notes → system learning)
```

---

## Critical Success Factors

### 1. Data Quality
- **Standardized testing protocols**: CMJ, IMTP procedures must be consistent
- **Technician training**: Bad input = bad output
- **Quality control checks**: Flag physiologically impossible values

### 2. Baseline Establishment
- **New athletes**: Need 4-6 tests before meaningful SWC calculation
- **Returning from injury**: Reset baseline, don't compare to pre-injury
- **Offseason vs. in-season**: Consider separate baselines

### 3. Coaching Adoption
- **Don't replace coaching judgment**: Frame as "decision support," not "autopilot"
- **Allow overrides**: Coaches should be able to add context the system can't know
- **Show the math**: Transparent calculations build trust

### 4. Continuous Improvement
- **Log outcomes**: Did the prescribed intervention work?
- **Refine thresholds**: SWC values may need sport/position adjustments
- **Add nuance**: As you learn, add subcategories or conditional logic

---

## Next Steps - Let's Get Specific

To move forward, I need to know:

1. **Your data source details**:
   - ForceDecks, Hawkin, or other?
   - Do you have API access or exporting CSVs?
   - How many tests per athlete per week?

2. **Your technical environment**:
   - Do you currently use Power BI?
   - Is Python/R already in your workflow?
   - What do coaches currently use daily? (Excel, Google Sheets, etc.)

3. **Your colleague's vision**:
   - Who is the primary user? (Strength coaches, sport coaches, sport scientists)
   - Real-time or daily batch updates?
   - Mobile access required?

Once I know these details, I can build you a specific implementation rather than general options.

What's your current setup look like?
