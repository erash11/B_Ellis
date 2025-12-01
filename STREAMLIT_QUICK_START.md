# Streamlit App - Quick Start Guide

**The easiest way to generate force plate training reports**

---

## What Is This?

A web-based app that runs on your computer - no technical skills needed!

**Instead of command line:** Just open your web browser and upload files.

---

## How to Start the App

### Step 1: Open Command Prompt (Windows) or Terminal (Mac)

**Windows:**
- Press `Windows Key + R`
- Type `cmd` and press Enter

**Mac:**
- Press `Command + Space`
- Type `terminal` and press Enter

### Step 2: Navigate to Your Folder

Type this command (replace with your actual path):

**Windows:**
```
cd C:\Users\YourName\Documents\B_Ellis
```

**Mac:**
```
cd /Users/YourName/Documents/B_Ellis
```

### Step 3: Start the App

Type exactly:
```
streamlit run generate_report_app.py
```

Press Enter and wait a few seconds.

**The app will automatically open in your web browser!**

If it doesn't open automatically, look for a message like:
```
Local URL: http://localhost:8501
```

Copy that URL and paste it into your web browser.

---

## How to Use the App

### 1. Upload Your Files

You'll see three upload boxes:

📁 **CMJ Data** - Click "Browse files" and select your CMJ test file
📁 **IMTP Data** - Click "Browse files" and select your IMTP test file
📁 **Roster** - Click "Browse files" and select your roster file

You can also **drag and drop** files directly onto the upload boxes!

### 2. Adjust Settings (Optional)

On the left sidebar, you can change:
- Team Name
- Current Training Phase
- Next Phase Name

### 3. Generate Report

Click the big **"🚀 Generate Report"** button

Wait 30-60 seconds while it processes (you'll see a spinner).

### 4. View Your Report

The report appears right in the browser!

Scroll through to see:
- Executive Summary
- Each category with athletes and recommendations
- Color-coded severity levels (🔴🟠🟡)

### 5. Download Your Report

Three buttons at the bottom:

**📄 Download HTML** - Full interactive report (share with coaches)
**📝 Download Text** - Simple text version (for printing)
**🖨️ Print to PDF** - Click this, then use your browser's Print function and choose "Save as PDF"

---

## Creating a PDF

### Method 1: Browser Print-to-PDF (Recommended)

1. After viewing your report in the app
2. Click **File → Print** (or press Ctrl+P / Cmd+P)
3. Change the "Destination" or "Printer" to **"Save as PDF"**
4. Click **Save**
5. Choose where to save your PDF

### Method 2: Download HTML, then Print

1. Click "📄 Download HTML" button
2. Open the downloaded HTML file in your browser
3. Click **File → Print**
4. Choose **"Save as PDF"**
5. Click **Save**

---

## Tips for Success

✅ **Keep the app running** - Don't close the command prompt/terminal window
✅ **Use Chrome, Firefox, or Edge** - Works best in modern browsers
✅ **File names don't matter** - Upload any CMJ/IMTP/Roster files
✅ **Drag and drop works** - Easier than clicking "Browse files"
✅ **Generate multiple times** - Upload different files and regenerate as needed

---

## Stopping the App

When you're done:
1. Go to the Command Prompt/Terminal window
2. Press `Ctrl+C` (Windows) or `Command+C` (Mac)
3. Close the window

The app will stop running and the browser tab won't work anymore.

---

## Troubleshooting

### App won't start

**Error: "streamlit is not recognized"**
- Solution: Install Streamlit first
- Type: `pip install streamlit`
- Then try again: `streamlit run generate_report_app.py`

### Browser doesn't open automatically

- Look for the message: `Local URL: http://localhost:8501`
- Copy that URL and paste it into your browser

### File upload fails

- Make sure files are `.csv` format
- Check that file names don't have special characters
- Try re-exporting from ForceDecks

### Report shows weird data

- Verify athlete names match exactly between all three files
- Check that you uploaded the correct files (CMJ vs IMTP)
- Make sure files have at least 5 tests per athlete

---

## Advantages Over Command Line

| Feature | Command Line | Streamlit App |
|---------|--------------|---------------|
| **File Upload** | Copy files + edit paths | Drag & drop |
| **Ease of Use** | Technical | Point & click |
| **Preview** | Must open separately | Instant view |
| **Download** | Find file manually | One click |
| **PDF Export** | Complicated | Browser print |
| **Settings** | Edit Python file | Web form |

---

## Common Workflow

**Monday morning (Phase-end):**
1. Get data files from sports science staff
2. Open Command Prompt → `cd B_Ellis` → `streamlit run generate_report_app.py`
3. Upload the 3 files
4. Click "Generate Report"
5. Review in browser
6. Download HTML and PDF
7. Share with coaching staff
8. Stop app with Ctrl+C

**Next time:**
- Just repeat! Same process every time.

---

## Sharing the App

**Want multiple coaches to use it?**

Two options:

1. **Everyone runs it locally**
   - Each coach follows this guide on their own computer
   - They need Python and the B_Ellis folder

2. **Deploy to a server** (Advanced)
   - Contact IT to host on a Baylor server
   - Everyone accesses the same URL
   - No installation needed for coaches

---

## Need Help?

**For app issues:**
- Check this guide first
- Try closing and restarting the app
- Contact sports science or IT team

**For report interpretation:**
- Contact sports science staff
- Reference the main documentation files

---

**You're all set!** The app makes report generation as easy as uploading files and clicking a button.

---

**Baylor University Athletics - B.A.I.R. Initiative**
**Version:** 1.0 | **Created:** November 2024
