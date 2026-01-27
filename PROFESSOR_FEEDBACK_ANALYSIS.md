# Professor Feedback - Data Analysis & Implementation Plan

## CRITICAL DATA ISSUES FOUND ⚠️

### Issue 1: Program Name Inconsistency Across Tables

**Admissions Data (admissions_metrics table):**
- Uses SHORT CODES: `MBA`, `MS ACCT`, `MS ENLD`, `MS HRM`, `MS MISY`, `MS MKTG`, `MS SPBA`

**Marketing Data (marketing_spend table):**
- Uses FULL NAMES: `Flex Online Mba`, `Flex Online Accounting`, `Flex Online Hrm`, etc.

**Programs Lookup Table:**
- Has BOTH: `program_code` (MBA) and `program_name` (Flex Online MBA)

**PROBLEM:** When we try to JOIN admissions and marketing data, they don't match!
- Admissions: `MBA`
- Marketing: `Flex Online Mba`
- Result: NO MATCH = Missing data in charts

### Issue 2: Marketing Program Names Are Inconsistent

Current marketing data has:
```
Flex Online Accounting          ❌ (should be "MS Accounting")
Flex Online Ai and Business Program  ❌ (should be "AI in Business Program")
Flex Online Hrm                 ❌ (should be "Human Resource Management")
Flex Online Marketing           ❌ (should be "MS Marketing")
Flex Online Mba                 ❌ (should be "MBA")
Flex Online Mis                 ❌ (should be "Management Information Systems")
Flex Online Ms Entrepreneurial Leadership  ✅ (close, but capitalization)
General Awareness               ❓ (not in admissions data)
```

### Issue 3: Program Name Mapping Needed

**Professor wants:**
1. Flex Online MBA
2. Flex Online MS Accounting
3. Flex Online MS Entrepreneurial Leadership
4. Flex Online MS Human Resource Management
5. Flex Online MS Management Information Systems
6. Flex Online MS Marketing
7. Flex Online AI in Business Program

**Current admissions codes:**
1. MBA → Flex Online MBA ✅
2. MS ACCT → Flex Online MS Accounting ✅
3. MS ENLD → Flex Online MS Entrepreneurial Leadership ✅
4. MS HRM → Flex Online MS Human Resource Management ✅
5. MS MISY → Flex Online MS Management Information Systems ✅
6. MS MKTG → Flex Online MS Marketing ✅
7. MS SPBA → Flex Online AI in Business Program ✅

---

## IMPLEMENTATION PLAN

### Phase 1: Data Standardization (CRITICAL - DO FIRST)

**Step 1.1: Create Program Mapping Function**
- Create a centralized mapping function that converts ALL program names to standard format
- Use this function in ALL queries across ALL pages

**Step 1.2: Update Programs Table**
```sql
UPDATE programs SET program_name = 'Flex Online MBA' WHERE program_code = 'MBA';
UPDATE programs SET program_name = 'Flex Online MS Accounting' WHERE program_code = 'MS ACCT';
UPDATE programs SET program_name = 'Flex Online MS Entrepreneurial Leadership' WHERE program_code = 'MS ENLD';
UPDATE programs SET program_name = 'Flex Online MS Human Resource Management' WHERE program_code = 'MS HRM';
UPDATE programs SET program_name = 'Flex Online MS Management Information Systems' WHERE program_code = 'MS MISY';
UPDATE programs SET program_name = 'Flex Online MS Marketing' WHERE program_code = 'MS MKTG';
UPDATE programs SET program_name = 'Flex Online AI in Business Program' WHERE program_code = 'MS SPBA';
```

**Step 1.3: Update Marketing Data**
- Re-run marketing ETL with corrected program name mapping
- OR update existing records with SQL UPDATE statements

**Step 1.4: Create Utility Function**
```python
# utils/program_mapping.py
PROGRAM_CODE_TO_NAME = {
    'MBA': 'Flex Online MBA',
    'MS ACCT': 'Flex Online MS Accounting',
    'MS ENLD': 'Flex Online MS Entrepreneurial Leadership',
    'MS HRM': 'Flex Online MS Human Resource Management',
    'MS MISY': 'Flex Online MS Management Information Systems',
    'MS MKTG': 'Flex Online MS Marketing',
    'MS SPBA': 'Flex Online AI in Business Program',
}

PROGRAM_NAME_TO_CODE = {v: k for k, v in PROGRAM_CODE_TO_NAME.items()}

def get_program_display_name(code_or_name):
    """Convert any program identifier to display name"""
    if code_or_name in PROGRAM_CODE_TO_NAME:
        return PROGRAM_CODE_TO_NAME[code_or_name]
    return code_or_name

def get_program_code(name):
    """Convert display name to code"""
    if name in PROGRAM_NAME_TO_CODE:
        return PROGRAM_NAME_TO_CODE[name]
    return name
```

---

### Phase 2: Page Restructuring

**2.1: Rename Home Dashboard → Executive Dashboard**
- File: `modules/home_dashboard.py` → `modules/executive_dashboard.py`
- Update imports in `main_app.py`
- Update navigation menu

**2.2: Add Marketing Insights to Executive Dashboard**
- Add high-level marketing overview section
- Show: Total spend, Spend by program (chart), Top channels
- Keep it simple - just overview, not detailed analysis

**2.3: Add Multi-Select Filters to Executive Dashboard**
- Replace single program dropdown with multi-select
- Apply to EACH chart independently (like Marketing Analysis)
- Default: All programs selected

**2.4: Rename Executive Deep Dive → Director's Deep Dive**
- File: `modules/executive_deep_dive.py` → `modules/directors_deep_dive.py`
- Update imports in `main_app.py`
- Update navigation menu

**2.5: Move Comparison Tool into Director's Deep Dive**
- Add as 5th tab in Director's Deep Dive
- Remove standalone Comparison Tool page
- Update navigation menu

---

### Phase 3: Color Palette Changes

**3.1: Define New Color Palette**
```python
# 7 distinct colors for 7 programs
PROGRAM_COLORS = {
    'Flex Online MBA': '#500000',  # Maroon (primary)
    'Flex Online MS Accounting': '#0066CC',  # Blue
    'Flex Online MS Entrepreneurial Leadership': '#FF6B35',  # Orange
    'Flex Online MS Human Resource Management': '#2ECC71',  # Green
    'Flex Online MS Management Information Systems': '#9B59B6',  # Purple
    'Flex Online MS Marketing': '#F39C12',  # Gold
    'Flex Online AI in Business Program': '#E74C3C',  # Red
}
```

**3.2: Apply to All Charts**
- Update Executive Dashboard charts
- Update Director's Deep Dive charts
- Update Marketing Analysis charts
- Ensure consistency across all pages

---

### Phase 4: Global Naming Updates

**4.1: Update Platform Name**
- Change: "Mays Analytics" → "Mays Flex Online Recruiting Analytics Platform"
- Files to update:
  - `main_app.py` (header)
  - `README.md`
  - `docs/*.md`
  - All page headers

**4.2: Update All Program References**
- Search and replace across ALL files
- Use the new standardized names
- Update filters, dropdowns, legends, tooltips

---

## QUESTIONS FOR YOU

Before I start implementation, I need clarification on:

### Q1: Marketing Data Mapping
The marketing data has "General Awareness" which doesn't map to any admissions program. Should we:
- A) Keep it as a separate category
- B) Distribute it across all programs
- C) Exclude it from program-specific analysis

### Q2: Excel File Program Names
The Excel files have sheet names like "MBA", "MS ACCT", etc. (short codes).
Should I:
- A) Keep reading short codes and map them in code
- B) Update Excel files to use full names (requires manual Excel editing)
- **Recommendation: Option A** (safer, no Excel changes needed)

### Q3: Database Migration
To fix the data issues, should I:
- A) Update existing database records (UPDATE statements)
- B) Re-run ETL pipelines from scratch (clean slate)
- **Recommendation: Option B** (cleaner, ensures consistency)

### Q4: Multi-Select Filter Behavior
For the multi-select filters on Executive Dashboard:
- A) Each chart has its own independent filter
- B) One global filter affects all charts on the page
- **Recommendation: Option A** (more flexible, like Marketing Analysis)

---

## ESTIMATED TIMELINE

| Phase | Tasks | Time Estimate |
|-------|-------|---------------|
| **Phase 1: Data Fix** | Program mapping, ETL updates, database updates | 2-3 hours |
| **Phase 2: Page Restructure** | Rename pages, move comparison tool, add marketing insights | 2-3 hours |
| **Phase 3: Colors** | New palette, update all charts | 1-2 hours |
| **Phase 4: Naming** | Global search/replace, update all references | 1-2 hours |
| **Testing** | Test all pages, verify data accuracy | 1-2 hours |
| **Total** | | **7-12 hours** |

---

## NEXT STEPS

1. **YOU:** Answer the 4 questions above
2. **ME:** Fix data issues (Phase 1) - MOST CRITICAL
3. **ME:** Implement page changes (Phase 2-4)
4. **BOTH:** Test thoroughly before deployment
5. **ME:** Update version to 6.2, deploy to production

---

**CRITICAL:** We MUST fix the data mapping issues (Phase 1) before making any UI changes. Otherwise, the charts will show incorrect or missing data.

