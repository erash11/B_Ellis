# ⏱️ Quick Reference: Adjusting Report Timeframes

## 🎯 One-Line Changes

### Open: `generate_html_report.py`
### Find: Line ~17
### Change: `MONTHS_TO_INCLUDE = X`

---

## 📅 Common Settings

```python
MONTHS_TO_INCLUDE = 1    # Last 4 weeks (monthly check-in)
MONTHS_TO_INCLUDE = 2    # Last 8 weeks (phase planning) ⭐ RECOMMENDED
MONTHS_TO_INCLUDE = 3    # Last 12 weeks (training block)
MONTHS_TO_INCLUDE = 6    # Last 6 months (season review)
```

---

## 🎪 Your Data Availability

Based on your Baylor data:

| Timeframe | Tests Available | Athletes (5+ tests) | Best For |
|-----------|----------------|---------------------|----------|
| **4 weeks** | 751 | 98 | Phase-end (if testing 2x/week) |
| **8 weeks** | 1,620 | 107 | ⭐ **Phase planning** |
| **12 weeks** | 2,420 | 109 | Training block assessment |
| **6 months** | 3,853 | 115 | Season review |

---

## ⚡ Quick Examples

### For Next Phase Planning:
```python
# Line 17:
MONTHS_TO_INCLUDE = 2  # 8 weeks - captures current phase
```

### For Season Review:
```python
# Line 17:
MONTHS_TO_INCLUDE = 6  # Full season
```

### For Specific Training Block:
```python
# Comment out line 17-19, add this instead:
START_DATE = '2025-09-01'  # Block start
END_DATE = '2025-11-24'    # Block end
df = df[(df['Date'] >= START_DATE) & (df['Date'] <= END_DATE)]
```

---

## 🔄 Generate Multiple Reports at Once

### Using Claude Code:

```bash
claude-code
```

**Prompt:**
```
Generate 3 reports with different timeframes:
1. Last 4 weeks → Baylor_Report_4wk.html
2. Last 8 weeks → Baylor_Report_8wk.html  
3. Last 6 months → Baylor_Report_6mo.html
```

**Done!** Three reports in 30 seconds.

---

## ⚠️ When to Change Timeframe

### Use SHORTER timeframe (4 weeks) when:
- ✅ End of short training block
- ✅ Testing frequently (2x/week)
- ✅ Want to detect recent changes quickly
- ✅ In-season fatigue monitoring

### Use LONGER timeframe (6 months) when:
- ✅ End of season review
- ✅ Program effectiveness evaluation
- ✅ Want stable, reliable trends
- ✅ Testing less frequently

### Use MEDIUM timeframe (8 weeks) when:
- ✅ **Phase-end planning** ⭐ Most Common
- ✅ Monthly check-ins
- ✅ Standard training block assessment
- ✅ Balanced sensitivity

---

## 💡 Pro Tips

1. **Match your training phases:**
   ```python
   # If your Fall Block was Sept 1 - Nov 24:
   START_DATE = '2025-09-01'
   END_DATE = '2025-11-24'
   ```

2. **Test the impact:**
   - Run with 4 weeks → See results
   - Run with 8 weeks → Compare
   - Choose the one that "feels right"

3. **Consistency matters:**
   - Use same timeframe for all monthly reports
   - Makes trends easier to track

4. **Your test frequency guides timeframe:**
   - Testing 2x/week → Can use 4 weeks
   - Testing 1x/week → Need 8+ weeks
   - Testing every 2 weeks → Need 12+ weeks

---

## 🚀 Right Now Action

### To generate an 8-week report (recommended):

1. Open: `generate_html_report.py`
2. Line 17: Change to `MONTHS_TO_INCLUDE = 2`
3. Save
4. Run: `python3 generate_html_report.py`
5. Open: `reports/Baylor_Training_Report.html`

**Done!** Report now shows last 8 weeks only.

---

## 📊 What Changes in the Report

When you adjust timeframe:

### Data Window Changes:
```
Before: "6-month period (2025-06-04 to 2025-11-24)"
After:  "2-month period (2025-09-29 to 2025-11-24)"
```

### Number of Athletes May Change:
- Shorter timeframe → Some athletes excluded (not enough tests)
- Longer timeframe → More athletes included

### Sensitivity Changes:
- Shorter timeframe → More sensitive (more flags)
- Longer timeframe → Less sensitive (fewer flags)

---

## 🎓 Understanding the Math

### Current Setup (60/40 Split):
```
If timeframe = 8 weeks (16 tests per athlete):
  Baseline = First 60% = First 9-10 tests
  Current = Last 40% = Last 6-7 tests
  
Compares: Early phase vs. Late phase
```

### Why This Matters:
- Detects if performance changed during the phase
- Baseline = "how you started"
- Current = "how you finished"

---

## ❓ FAQ

**Q: What timeframe did the report I received use?**
**A:** 6 months (full dataset). Change to 8 weeks for phase planning.

**Q: Can I do less than 4 weeks?**
**A:** Yes, but need at least 3 tests per athlete. Not recommended.

**Q: Can I compare two different time periods?**
**A:** Yes! Generate two reports with different date ranges.

**Q: Will this affect sensitivity?**
**A:** Yes. Shorter = more sensitive. Adjust thresholds if needed.

---

## 🔗 Related Guides

- **[TIMEFRAME_ADJUSTMENT_GUIDE.md](TIMEFRAME_ADJUSTMENT_GUIDE.md)** - Detailed explanations
- **[CLAUDE_CODE_WORKFLOW.md](CLAUDE_CODE_WORKFLOW.md)** - Using Claude Code to adjust
- **[Baylor_Training_Report_SUMMARY.md](Baylor_Training_Report_SUMMARY.md)** - Current results

---

**Bottom Line:** Change line 17 to `MONTHS_TO_INCLUDE = 2` for 8-week phase reports.
