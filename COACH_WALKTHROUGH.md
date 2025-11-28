# Force Plate Training Report - Coach's Guide

**A simple step-by-step guide to generate your training reports**

---

## What You'll Get

After following these steps, you'll have:
- ✅ A professional HTML report you can open in any web browser
- ✅ A list of athletes organized by what they need (strength, power, etc.)
- ✅ Specific training recommendations for each group
- ✅ Color-coded priorities (🔴 Red = urgent, 🟠 Orange = important, 🟡 Yellow = monitor)

**Time needed:** 10-15 minutes (most of it is just waiting for the computer)

---

## Before You Start - What You Need

### 1. Your Force Plate Data Files

You need **three files** from your sports science staff:

📄 **CMJ Data** - Jumping test results (file ends with `CMJ` in the name)
📄 **IMTP Data** - Pulling test results (file ends with `IMTP` in the name)
📄 **Roster** - List of athletes with their positions

**Ask your sports science staff:** "Can you export the last 6 months of CMJ and IMTP data as CSV files, plus our current roster?"

### 2. The Report Software

This is already set up in your `B_Ellis` folder. You don't need to install anything new.

---

## Step-by-Step Instructions

### STEP 1: Get Your Data Files in the Right Place

**What to do:**
1. Find the three data files (CMJ, IMTP, Roster) - they should be on your computer
2. Open your `B_Ellis` folder (this is where all the report files live)
3. **Copy** the three data files into the `B_Ellis` folder
4. They should be sitting right next to files like `generate_real_report.py`

**How it should look:**
```
B_Ellis folder should contain:
  ✓ Your CMJ file (example: 2025-11-27-CMJ_Last6mnths.csv)
  ✓ Your IMTP file (example: 2025-11-27-IMTP_Last6mnths.csv)
  ✓ Your roster file (example: 2025-11-27_FB_Roster.csv)
  ✓ generate_real_report.py (already there)
```

---

### STEP 2: Update the File Names (One-Time Setup)

**Why?** The computer needs to know which files to read. You only need to do this once, or when file names change.

**What to do:**

1. In your `B_Ellis` folder, find the file called **`generate_real_report.py`**
2. **Right-click** on it and select **"Open with" → "Notepad"** (Windows) or **"TextEdit"** (Mac)
3. Look at the very top of the file - you'll see lines like this:

```python
# File paths
ROSTER_FILE = '2025-11-27_FB_Roster_2025_ER.csv'
CMJ_FILE = '2025-11-27-CMJ_Last6mnthscsv.csv'
IMTP_FILE = '2025-11-27-IMTP_Last6mnthscsv.csv'
```

4. **Change these file names** to match YOUR files exactly
   - Make sure the spelling is EXACTLY the same
   - Include the `.csv` at the end
   - Keep the quote marks

**Example:**
If your CMJ file is named `2025-12-15-CMJ-Data.csv`, change the line to:
```python
CMJ_FILE = '2025-12-15-CMJ-Data.csv'
```

5. **Save the file** (File → Save)
6. **Close Notepad/TextEdit**

**⚠️ Important:**
- File names must match EXACTLY (including capital letters)
- Don't delete the quote marks (' ')
- Don't change anything else in the file

---

### STEP 3: Run the Report Generator

**Now for the easy part!**

#### On Windows:

1. **Open Command Prompt:**
   - Click the Windows Start button
   - Type `cmd`
   - Press Enter
   - A black window will open

2. **Navigate to your folder:**
   - Type this (replace with YOUR actual folder path):
   ```
   cd C:\Users\YourName\Documents\B_Ellis
   ```
   - Press Enter
   - **Tip:** If you don't know the path, open your B_Ellis folder, click in the address bar at the top, copy the path, and paste it

3. **Run the report:**
   - Type exactly:
   ```
   python generate_real_report.py
   ```
   - Press Enter
   - **Wait** - You'll see text scrolling. This is normal! It takes 30-60 seconds

#### On Mac:

1. **Open Terminal:**
   - Press `Command + Space`
   - Type `terminal`
   - Press Enter

2. **Navigate to your folder:**
   - Type this (replace with YOUR actual folder path):
   ```
   cd /Users/YourName/Documents/B_Ellis
   ```
   - Press Enter

3. **Run the report:**
   - Type exactly:
   ```
   python generate_real_report.py
   ```
   - Press Enter
   - **Wait** - You'll see text scrolling. This is normal! It takes 30-60 seconds

---

### STEP 4: Success! Open Your Report

**You'll know it worked when you see:**

```
✓ HTML report saved: Baylor_Training_Report_REAL.html
✓ Text report saved: Baylor_Training_Report_REAL.txt
```

**To view your report:**

1. Go back to your `B_Ellis` folder
2. Find the file: **`Baylor_Training_Report_REAL.html`**
3. **Double-click it** - it will open in your web browser (Chrome, Safari, Edge, etc.)
4. **That's it!** You're looking at your training report

**What you'll see:**
- Executive summary at the top
- 7 categories of athletes (strength, power, speed, etc.)
- Each athlete listed with their severity level (🔴🟠🟡)
- Training recommendations for each category
- Priorities for your next training phase

---

## Reading Your Report

### Color Codes (Traffic Light System)

- 🔴 **Red (Critical)** - Address immediately in next phase
- 🟠 **Orange (Warning)** - Needs attention soon
- 🟡 **Yellow (Caution)** - Keep an eye on them
- 🟢 **Green (Normal)** - All good, no changes needed

### The 7 Categories

Your athletes will be sorted into these groups:

1. **Maximal Strength Capacity** - Need to build base strength
2. **Explosive Strength / RFD** - Need to improve rate of force development
3. **Power Output** - Need more explosive power
4. **SSC Efficiency** - Need better jumping/landing mechanics
5. **Eccentric Control** - Need better braking/deceleration
6. **Technical / Coordination** - Movement quality issues
7. **Asymmetry** - Left/right imbalances

### What the Recommendations Mean

**The report tells you HOW to train, not WHAT exercises to do.**

❌ **It won't say:** "Do trap bar deadlifts instead of squats"
✅ **It will say:** "Use cluster sets with longer rest periods"

You still choose the exercises - the report suggests how to execute them.

---

## Sharing Your Report

### Option 1: Email It
- The HTML file can be emailed directly
- Anyone can open it in their web browser
- No special software needed

### Option 2: Print It
- Open the HTML file in your browser
- Click File → Print
- Choose "Save as PDF" for a clean copy

### Option 3: Present It
- Open the HTML file during your staff meeting
- Scroll through the categories
- Discuss priorities as a group

---

## Common Problems & Solutions

### Problem 1: "Python is not recognized" or "Command not found"

**Solution:** Python isn't installed or isn't in your PATH.
- **Quick fix:** Ask your IT department or sports science staff to install Python
- **Or:** They can run the report for you

### Problem 2: "FileNotFoundError: No such file"

**Solution:** The file names don't match.
- Check the file names are spelled EXACTLY the same in Step 2
- Make sure the files are actually in the B_Ellis folder
- File names are case-sensitive (CMJ vs cmj is different)

### Problem 3: "ModuleNotFoundError: No module named 'pandas'"

**Solution:** Missing required software.
- Open Command Prompt/Terminal
- Type: `pip install pandas numpy openpyxl`
- Press Enter and wait
- Then try running the report again

### Problem 4: Report shows "0 athletes" or everyone is flagged

**Solution:** Data quality issue or wrong settings.
- Make sure you have at least 5 tests per athlete
- Check that dates are in the last 6 months
- Contact your sports science staff to verify the data export

### Problem 5: Athletes names don't match between files

**Solution:** Name formatting is inconsistent.
- Make sure athlete names are spelled EXACTLY the same in all three files
- Example: "John Smith" vs "Smith, John" won't match
- No extra spaces before or after names

---

## When to Run Reports

### ✅ Good Times to Generate Reports:

- **End of training phase** (every 4-6 weeks)
- **Before planning next phase**
- **After summer/winter break**
- **Before major competitions** (to check readiness)

### ❌ Don't Generate Reports:

- Daily or weekly (data needs time to show trends)
- In the middle of a training phase
- When you only have 1-2 tests per athlete
- Right after an athlete returns from injury

---

## Quick Reference Card

**Copy this and keep it handy:**

```
QUICK STEPS TO RUN REPORT:
1. Get 3 data files from sports science staff
2. Copy files into B_Ellis folder
3. Open Command Prompt (cmd) or Terminal
4. Type: cd [path to B_Ellis folder]
5. Type: python generate_real_report.py
6. Wait 30-60 seconds
7. Open Baylor_Training_Report_REAL.html
```

---

## Getting Help

### For Technical Issues:
- **Contact:** Your sports science staff or IT department
- **Tell them:** "I'm having trouble running the force plate report generator"
- **Have ready:** The exact error message you're seeing

### For Report Interpretation:
- **Contact:** Your sports science or strength staff
- **Ask about:** Specific athletes or categories you want to understand better
- **Discuss:** How recommendations fit with your current programming

### For System Updates:
- **Contact:** Sports science team
- **When:** New athletes join, roster changes, or you want to adjust report settings

---

## Tips for Success

### 💡 First Time Users:

1. **Run a test report first** with your sports science staff present
2. **Ask questions** if anything is unclear
3. **Keep old reports** in a separate folder (label with dates)
4. **Review with your staff** before making major program changes

### 💡 Regular Users:

1. **Create a routine** - Same day each phase (e.g., Friday of week 6)
2. **Archive old reports** - Create folders like "2025-Fall-Phase1", "2025-Fall-Phase2"
3. **Track changes** - Note which athletes improve or decline over time
4. **Share with staff** - Get input from assistant coaches before finalizing plans

### 💡 Best Practices:

- Generate reports at the **same point** in each training phase
- Use reports for **planning**, not daily decisions
- Trust your coaching judgment - reports inform, not dictate
- Focus on **trends over time**, not single data points

---

## Example Workflow

**Here's how Coach Smith uses this system:**

**Week 6 of Training Phase:**
1. Monday: Asks sports science to export latest data
2. Tuesday morning: Runs report (takes 5 minutes)
3. Tuesday afternoon: Reviews report, highlights key findings
4. Wednesday: Staff meeting - discusses top 3 priorities from report
5. Thursday-Friday: Plans next phase incorporating recommendations
6. Archives report in folder labeled "2025-Fall-Phase2"

**Week 1 of New Phase:**
- Implements execution changes (cluster sets, tempo work, etc.)
- Keeps exercises mostly the same, just changes HOW they're done
- Monitors athletes flagged as critical

**Week 6 of New Phase:**
- Repeats the process
- Compares new report to previous one
- Notes improvements

---

## Final Notes

**Remember:**
- ✅ This is a **tool to inform** your decisions, not make them for you
- ✅ You're the expert on your athletes and your program
- ✅ The report shows **what the data says**, you decide **what to do about it**
- ✅ When in doubt, ask your sports science team

**You've got this!** After the first time, this process takes less than 5 minutes.

---

**Questions or need help?**
Contact the Baylor Sports Science Team

**Version:** November 2024
**Created for:** Baylor University Athletics - B.A.I.R. Initiative
