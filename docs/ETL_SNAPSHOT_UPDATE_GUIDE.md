# ETL Snapshot Update Guide

**Version:** 1.0  
**Last Updated:** February 6, 2026  
**Purpose:** Step-by-step guide for AI agents and developers to add new timestamp snapshots to the Flex Online Analytics Platform

---

## Overview

The Flex Online Analytics Platform uses a **state snapshot ETL methodology** where each Excel file represents a point-in-time snapshot of admissions data for a specific cohort. This guide provides a systematic approach to adding new snapshots without corrupting existing data.

---

## Understanding the Data Structure

### File Naming Convention

```
MBS-Flex-Online-Admissions-YYYY-MM-DD[_season].xlsx
```

**Examples:**
- `MBS-Flex-Online-Admissions-2024-07-31_fall.xlsx` - Class 2026 (completed)
- `MBS-Flex-Online-Admissions-2025-07-31_fall.xlsx` - Class 2027 (in progress)
- `MBS-Flex-Online-Admissions-2026-02-28.xlsx` - Class 2028 (current)

**Notes:**
- `YYYY-MM-DD` = Snapshot date (when the data was extracted)
- `_season` = Optional suffix (fall/spring), defaults to "fall" if omitted
- Each file tracks ONE cohort across multiple months

### Cohort Mapping

| File Date | Cohort Year | Status |
|-----------|-------------|--------|
| 2024-07-31 | 2026 | Completed (historical) |
| 2025-07-31 | 2027 | In Progress |
| 2026-02-28 | 2028 | Current (active recruiting) |

**Key Principle:** The snapshot date does NOT equal the cohort year. A 2026 snapshot tracks the Class of 2028.

---

## Step-by-Step Process for Adding New Snapshots

### STEP 1: Receive and Validate the New File

**1.1 Check File Location**
```bash
ls -la Dataset/
```

**Expected:** New file should be in the `Dataset/` folder

**1.2 Validate File Name Format**
- Must match pattern: `MBS-Flex-Online-Admissions-YYYY-MM-DD[_season].xlsx`
- Date should be end-of-month (e.g., 2026-02-28, 2026-03-31)
- Season suffix is optional

**1.3 Identify Which Cohort This Snapshot Tracks**

Ask yourself:
- Is this an UPDATE to an existing cohort? (Replace old file)
- Is this a NEW cohort? (Add new file, keep old ones)

**Example Decision Tree:**
```
New file: MBS-Flex-Online-Admissions-2026-03-31.xlsx

Question: What cohort does this track?
Answer: Class of 2028 (same as Feb 2026 file)

Action: This REPLACES the Feb 2026 file (it's a newer snapshot of the same cohort)
```

---

### STEP 2: Update the ETL Pipeline Configuration

**2.1 Open the ETL Pipeline File**
```bash
# File to edit
etl_pipeline.py
```

**2.2 Update the Cohort Mapping Dictionary**

Location: `parse_filename_cohort()` function

```python
file_cohort_map = {
    'MBS-Flex-Online-Admissions-2024-07-31_fall.xlsx': 2026,  # Class 2026 (completed)
    'MBS-Flex-Online-Admissions-2025-07-31_fall.xlsx': 2027,  # Class 2027 (in progress)
    'MBS-Flex-Online-Admissions-2026-02-28.xlsx': 2028,       # Class 2028 (OLD - to be replaced)
    'MBS-Flex-Online-Admissions-2026-03-31.xlsx': 2028        # Class 2028 (NEW - current)
}
```

**Action:** Add the new filename with its corresponding cohort year

**2.3 Update the Dataset Files List**

Location: `load_all_data()` function

```python
dataset_files = [
    'Dataset/MBS-Flex-Online-Admissions-2024-07-31_fall.xlsx',  # Class 2026
    'Dataset/MBS-Flex-Online-Admissions-2025-07-31_fall.xlsx',  # Class 2027
    'Dataset/MBS-Flex-Online-Admissions-2026-03-31.xlsx'        # Class 2028 (updated Mar 2026)
]
```

**Action:** Replace the old file path with the new one (if updating same cohort)

---

### STEP 3: Backup the Database (CRITICAL!)

**3.1 Create a Backup**
```bash
# Create timestamped backup
cp edulytix.db edulytix_backup_$(date +%Y%m%d_%H%M%S).db

# Verify backup exists
ls -la edulytix_backup_*.db
```

**Why?** If the ETL fails or corrupts data, you can restore from backup

**3.2 Document the Backup**
```bash
# Create a backup log
echo "$(date): Backup created before loading $(NEW_FILE_NAME)" >> backup_log.txt
```

---

### STEP 4: Run the ETL Pipeline

**4.1 Activate Virtual Environment**
```bash
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```

**4.2 Run the ETL Pipeline**
```bash
python etl_pipeline.py
```

**4.3 Monitor the Output**

Look for these key indicators:

✅ **SUCCESS Indicators:**
```
INFO - 🔄 Starting State Snapshot ETL Pipeline...
INFO - Processing Dataset/MBS-Flex-Online-Admissions-2026-03-31.xlsx...
INFO - Parsed MBS-Flex-Online-Admissions-2026-03-31.xlsx: Start 2026, Season fall, Cohort 2028
INFO - Discovered program sheets: ['MBA', 'MS ACCT', 'MS ENLD', 'MS HRM', 'MS MISY', 'MS MKTG']
INFO - Processing 5 date columns with actual data in MBA
INFO - Extracted 95 state snapshot records from Flex Online MBA
INFO - Total state snapshot records processed: 2059
INFO - ✅ State Snapshot ETL completed successfully!
INFO - Summary: 2059 snapshots, 6 programs, 3 cohorts
```

❌ **ERROR Indicators:**
```
ERROR - Error processing file: ...
ERROR - Cannot parse cohort info from filename: ...
WARNING - No date row found in ...
```

**4.4 Verify Final States**

The ETL output shows final states for each cohort:

```
INFO - Class 2028 Final States (latest non-zero data per program):
INFO -   - MBA: 1688.0 inquiries (as of 2026-02-28)
INFO -   - MS Accounting: 362.0 inquiries (as of 2026-02-28)
...
```

**Action:** Compare these numbers with the Excel file to ensure accuracy

---

### STEP 5: Validate the Data

**5.1 Check Database Record Counts**
```bash
sqlite3 edulytix.db "SELECT COUNT(*) FROM admissions_metrics;"
```

**Expected:** Should match or exceed the "Total state snapshot records" from ETL output

**5.2 Verify Cohort Data**
```bash
sqlite3 edulytix.db "SELECT DISTINCT cohort_year FROM admissions_metrics ORDER BY cohort_year;"
```

**Expected Output:**
```
2026
2027
2028
```

**5.3 Check Latest Snapshot Date for Class 2028**
```bash
sqlite3 edulytix.db "
SELECT 
    program, 
    MAX(report_date) as latest_date,
    file_source
FROM admissions_metrics 
WHERE cohort_year = 2028
GROUP BY program
ORDER BY program;
"
```

**Expected:** All programs should show the new snapshot date (e.g., 2026-03-31)

**5.4 Spot Check Key Metrics**
```bash
sqlite3 edulytix.db "
SELECT 
    program,
    metric_name,
    metric_value,
    report_date
FROM admissions_metrics
WHERE cohort_year = 2028 
    AND metric_name = 'inquiries_received'
    AND report_date = '2026-03-31'
ORDER BY program;
"
```

**Action:** Compare these values with the Excel file manually

---

### STEP 6: Remove Old Snapshot File

**6.1 Identify the Old File**
```bash
ls -la Dataset/MBS-Flex-Online-Admissions-2026-*.xlsx
```

**6.2 Delete the Old File (ONLY if ETL succeeded)**
```bash
# Move to archive instead of deleting (safer)
mkdir -p Dataset/archive
mv Dataset/MBS-Flex-Online-Admissions-2026-02-28.xlsx Dataset/archive/

# OR delete permanently (use with caution)
rm Dataset/MBS-Flex-Online-Admissions-2026-02-28.xlsx
```

**CRITICAL:** Only delete after confirming:
- ETL ran successfully
- Data validation passed
- Dashboard displays correct data

---

### STEP 7: Test the Dashboard

**7.1 Start the Streamlit Server**
```bash
streamlit run main_app.py
```

**7.2 Navigate to Key Pages**

Test these pages in order:

1. **Executive Dashboard**
   - Check "Anticipated Cohort Size" for Class 2028
   - Verify numbers match the new snapshot

2. **Director's Deep Dive**
   - Select "Class of 2028"
   - Check "Cohort Analysis" tab
   - Verify latest data point shows new snapshot date

3. **Predictive Analytics**
   - Run a forecast for Class 2028
   - Ensure it uses the new data

4. **Data Explorer**
   - Filter: Cohort = 2028
   - Check that latest report_date is the new snapshot date

**7.3 Verify No Errors**
- No "KeyError" or "ValueError" messages
- All charts render correctly
- Filters work as expected

---

### STEP 8: Update Documentation

**8.1 Update the README.md**

Location: `README.md` - "Data Coverage" section

```markdown
### Admissions Data
- **Records**: 2,100+ admissions records (updated)
- **Programs**: 6 graduate programs
- **Cohorts**: Classes of 2026, 2027, 2028
- **Metrics**: 20+ tracked metrics per application
- **Date Range**: July 2024 - March 2026 (updated)
```

**8.2 Update PROJECT_SUMMARY**

Location: `PROJECT_SUMMARY_V1_TO_V9.txt`

Add a note at the end:
```
DATA UPDATE LOG
===============
- March 13, 2026: Added Class 2028 snapshot (2026-03-31), replaced Feb 2026 snapshot
```

**8.3 Update CHANGELOG**

Location: `docs/CHANGELOG.md`

Add entry:
```markdown
## Data Update - March 13, 2026

### Data Refresh
- Added new Class 2028 snapshot (as of March 31, 2026)
- Removed old February 2026 snapshot
- Total records: 2,100+ admissions snapshots
```

---

## Common Issues and Troubleshooting

### Issue 1: "Cannot parse cohort info from filename"

**Cause:** Filename doesn't match expected pattern or not in cohort mapping

**Solution:**
1. Check filename format: `MBS-Flex-Online-Admissions-YYYY-MM-DD[_season].xlsx`
2. Add filename to `file_cohort_map` in `etl_pipeline.py`
3. Ensure date format is correct (YYYY-MM-DD)

---

### Issue 2: "No date row found in [sheet]"

**Cause:** Excel file structure changed or dates not in expected row

**Solution:**
1. Open Excel file manually
2. Check that Row 2 or 3 contains dates (e.g., "1/19/2024")
3. If structure changed, update `extract_program_data()` function

---

### Issue 3: Duplicate Records or Data Overwrite

**Cause:** Same cohort loaded twice or old data not replaced

**Solution:**
1. Check `UNIQUE` constraint in database schema:
   ```sql
   UNIQUE(report_date, program, cohort_year, cohort_season, metric_name)
   ```
2. ETL uses `INSERT OR REPLACE` - newer data overwrites old
3. If duplicates persist, clear table and reload:
   ```bash
   sqlite3 edulytix.db "DELETE FROM admissions_metrics WHERE cohort_year = 2028;"
   python etl_pipeline.py
   ```

---

### Issue 4: Missing Programs in New Snapshot

**Cause:** Program sheet name changed or excluded

**Solution:**
1. Check `discover_program_sheets()` function
2. Verify `excluded_sheets` list doesn't include your program
3. Check Excel file has the program sheet

---

### Issue 5: Suspicious Zeros or Missing Data

**Cause:** ETL's smart backfill logic skipped data

**Solution:**
1. Check ETL logs for "Skipping suspicious zero" messages
2. Review `check_date_has_other_metrics()` logic
3. If data is valid, adjust threshold in `extract_program_data()`

---

## Rollback Procedure

If something goes wrong, follow these steps:

### Step 1: Stop the Streamlit Server
```bash
# Find the process
ps aux | grep streamlit

# Kill it
kill -9 [PID]
```

### Step 2: Restore Database from Backup
```bash
# Find your backup
ls -la edulytix_backup_*.db

# Restore (replace with your backup filename)
cp edulytix_backup_20260313_135900.db edulytix.db
```

### Step 3: Revert ETL Pipeline Changes
```bash
# Use git to revert
git checkout etl_pipeline.py

# OR manually restore old file paths in dataset_files list
```

### Step 4: Restart and Verify
```bash
streamlit run main_app.py
```

---

## Best Practices

### DO:
✅ Always create a database backup before running ETL  
✅ Validate data in Excel file before loading  
✅ Test on a copy of the database first (if possible)  
✅ Check ETL logs for warnings and errors  
✅ Verify dashboard displays correct data after loading  
✅ Document what you changed and why  
✅ Keep old snapshot files in an archive folder  

### DON'T:
❌ Run ETL without backing up the database  
❌ Delete old files before confirming new data loaded correctly  
❌ Skip data validation steps  
❌ Ignore ETL warnings (they indicate potential issues)  
❌ Load multiple snapshots for the same cohort simultaneously  
❌ Modify the database directly (always use ETL pipeline)  

---

## Quick Reference Checklist

Use this checklist when adding a new snapshot:

- [ ] New Excel file received and placed in `Dataset/` folder
- [ ] Identified which cohort this snapshot tracks
- [ ] Updated `file_cohort_map` in `etl_pipeline.py`
- [ ] Updated `dataset_files` list in `etl_pipeline.py`
- [ ] Created database backup: `edulytix_backup_YYYYMMDD_HHMMSS.db`
- [ ] Ran ETL pipeline: `python etl_pipeline.py`
- [ ] Verified ETL completed successfully (no errors)
- [ ] Checked database record counts match expected
- [ ] Validated latest snapshot date in database
- [ ] Spot-checked key metrics against Excel file
- [ ] Removed old snapshot file (moved to archive)
- [ ] Tested dashboard locally (all pages load correctly)
- [ ] Updated README.md data coverage section
- [ ] Updated CHANGELOG.md with data refresh entry
- [ ] Documented changes in backup log
- [ ] **DEPLOYED TO STREAMLIT CLOUD:**
  - [ ] Force added database: `git add -f edulytix.db`
  - [ ] Committed database with descriptive message
  - [ ] Pushed to GitHub: `git push origin main`
  - [ ] Rebooted Streamlit Cloud app
  - [ ] Verified production app shows new data

---

## Deploying to Streamlit Cloud

**CRITICAL:** After updating the database locally, you MUST push it to GitHub and reboot the Streamlit Cloud app for changes to appear in production.

### Why This is Necessary

The database file (`edulytix.db`) is in `.gitignore` by default, which means it won't be pushed to GitHub automatically. Your Streamlit Cloud deployment will continue using the OLD database until you explicitly update it.

### Step-by-Step Deployment Process

**Step 1: Force Add the Database to Git**
```bash
# Force add the database (overrides .gitignore)
git add -f edulytix.db
```

**Step 2: Commit the Database**
```bash
git commit -m "data: Update database with [Month Year] snapshot for Class [YYYY]

- Added [Month Year] data for all programs
- Class [YYYY] now has data through [Date]
- Total: [X] admissions records across [Y] programs and [Z] cohorts"
```

**Example:**
```bash
git commit -m "data: Update database with Feb 2026 snapshot for Class 2028

- Added Feb 2026 data for all programs
- Class 2028 now has data through Feb 28, 2026
- Total: 2,059 admissions records across 6 programs and 3 cohorts"
```

**Step 3: Push to GitHub**
```bash
git push origin main
```

**Step 4: Reboot Streamlit Cloud App**
1. Go to https://share.streamlit.io/
2. Find your app (mays-recruiting-analytics)
3. Click the **⋮** (three dots menu)
4. Click **"Reboot app"**
5. Wait 2-3 minutes for the reboot to complete

**Step 5: Verify Deployment**
1. Open your Streamlit Cloud app URL
2. Navigate to Executive Dashboard
3. Check that Class 2028 shows the latest data
4. Verify the date range matches your new snapshot

### Troubleshooting Deployment Issues

**Issue: App still shows old data after reboot**
- Clear your browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check GitHub to confirm the database file was pushed (check file size and commit date)
- Try rebooting the app again

**Issue: App fails to start after database update**
- Check Streamlit Cloud logs for errors
- Verify the database file is not corrupted (test locally first)
- Ensure the database schema matches what the app expects

**Issue: Database file too large for GitHub**
- GitHub has a 100MB file size limit
- If your database exceeds this, consider:
  - Using Git LFS (Large File Storage)
  - Hosting the database elsewhere (AWS S3, Google Cloud Storage)
  - Archiving old data and keeping only recent snapshots

### Important Notes

⚠️ **Always test locally before deploying to production**
- Run the ETL pipeline locally
- Test the dashboard thoroughly
- Verify all data looks correct
- Only then push to GitHub and reboot Streamlit Cloud

⚠️ **Database updates are NOT automatic**
- Unlike code changes, database updates require manual deployment
- Remember to force add (`git add -f`) the database file
- Don't forget to reboot the Streamlit Cloud app

⚠️ **Keep track of deployments**
- Document when you deployed database updates
- Note which snapshot version is in production
- Keep a log of deployment dates for reference

---

## Contact and Support

**For Questions:**
- Technical Issues: Check logs in ETL output
- Data Discrepancies: Compare database queries with Excel file
- Dashboard Errors: Check Streamlit terminal output

**Escalation:**
- If ETL fails repeatedly, restore from backup and investigate
- If data looks incorrect, do NOT proceed - investigate first
- If unsure about cohort mapping, consult with stakeholders

---

## Appendix: SQL Queries for Validation

### Check Total Records by Cohort
```sql
SELECT 
    cohort_year,
    COUNT(*) as total_records,
    COUNT(DISTINCT program) as programs,
    MIN(report_date) as earliest_date,
    MAX(report_date) as latest_date
FROM admissions_metrics
GROUP BY cohort_year
ORDER BY cohort_year;
```

### Check Latest Snapshot for Each Program
```sql
SELECT 
    program,
    cohort_year,
    MAX(report_date) as latest_snapshot,
    file_source
FROM admissions_metrics
GROUP BY program, cohort_year
ORDER BY cohort_year, program;
```

### Check Inquiries Trend for Class 2028
```sql
SELECT 
    report_date,
    program,
    metric_value as inquiries
FROM admissions_metrics
WHERE cohort_year = 2028 
    AND metric_name = 'inquiries_received'
ORDER BY program, report_date;
```

### Find Missing Data (NULL values)
```sql
SELECT 
    program,
    cohort_year,
    metric_name,
    COUNT(*) as null_count
FROM admissions_metrics
WHERE metric_value IS NULL
GROUP BY program, cohort_year, metric_name
HAVING null_count > 0;
```

### Check for Duplicate Records
```sql
SELECT 
    report_date,
    program,
    cohort_year,
    metric_name,
    COUNT(*) as duplicate_count
FROM admissions_metrics
GROUP BY report_date, program, cohort_year, metric_name
HAVING duplicate_count > 1;
```

---

**Document Version:** 1.0  
**Last Updated:** February 6, 2026  
**Maintained By:** Tirth Shah  
**Review Frequency:** Update after each major ETL change
