# Mays Analytics Platform - Modular Refactoring Plan

## Overview
This document outlines the phased approach to refactoring the monolithic `main_app.py` (5,551 lines) into a modular architecture with separate page modules and shared utilities.

## Current Status: ✅ Phase 1 Complete

### Phase 1: Infrastructure Setup (COMPLETED)
**Date**: January 23, 2026

**What was done:**
1. ✅ Created folder structure (`pages/`, `utils/`)
2. ✅ Extracted shared database functions to `utils/database.py`
3. ✅ Extracted data processing functions to `utils/data_processing.py`
4. ✅ Extracted styling functions to `utils/styling.py`
5. ✅ Extracted table display functions to `utils/table_display.py`
6. ✅ Created comprehensive test suite (`test_utils.py`)
7. ✅ All tests passing - utilities verified working

**Files Created:**
```
utils/
├── __init__.py          # Exports all utility functions
├── database.py          # Database connections and data loading
├── data_processing.py   # Data insights and processing
├── styling.py           # CSS and styling functions
└── table_display.py     # Data Explorer table display

pages/
└── __init__.py          # Ready for page modules

test_utils.py            # Verification test suite
REFACTORING_PLAN.md      # This file
```

**Test Results:**
- ✓ All utility imports successful
- ✓ Database connection working
- ✓ Program name normalization working
- ✓ Data loading functions working (7 programs, 348 records loaded)
- ✓ Marketing data check working
- ✓ Insight generation working

---

## Next Steps: Phase 2-7 (One Page Per Session)

### Phase 2: Extract Help Page (NEXT)
**Estimated Time**: 30 minutes  
**Risk Level**: LOW (no dependencies, stateless)

**Tasks:**
1. Create `pages/help.py`
2. Extract lines 5028-5551 from `main_app.py`
3. Add `render()` function wrapper
4. Import only `streamlit` (no other dependencies)
5. Test Help page works independently
6. Update `main_app.py` to import and call `help.render()`
7. Verify no functional changes
8. Commit to Git

**Why Help First?**
- Simplest page (no database queries, no session state)
- Pure content display
- Good test case for the refactoring pattern

---

### Phase 3: Extract Database/Data Explorer Page
**Estimated Time**: 45 minutes  
**Risk Level**: LOW-MEDIUM (uses table_display utility)

**Tasks:**
1. Create `pages/database.py`
2. Extract lines 4618-5027 from `main_app.py`
3. Import `process_table_display` from utils
4. Add `render()` function wrapper
5. Test Data Explorer works
6. Update `main_app.py` routing
7. Verify filtering, search, export all work
8. Commit to Git

---

### Phase 4: Extract Home Dashboard Page
**Estimated Time**: 60 minutes  
**Risk Level**: MEDIUM (session state, multiple charts)

**Tasks:**
1. Create `pages/home.py`
2. Extract lines 905-1520 from `main_app.py`
3. Import database and styling utilities
4. Handle session state variables (7 vars)
5. Test all filters and charts work
6. Update `main_app.py` routing
7. Verify funnel, program comparison, trends all work
8. Commit to Git

**Session State Variables:**
- `home_reset_count`
- `home_funnel_log_scale`
- `prog_home_show_inquiries`
- `prog_home_show_applications`
- `prog_home_show_accepted`
- `prog_home_show_cohort`
- `prog_home_log_scale`

---

### Phase 5: Extract Executive Deep Dive Page
**Estimated Time**: 90 minutes  
**Risk Level**: HIGH (complex, 4 tabs, many session state vars)

**Tasks:**
1. Create `pages/executive_dive.py`
2. Extract lines 1521-2579 from `main_app.py`
3. Import all necessary utilities
4. Handle session state for tabs and filters
5. Test all 4 tabs work correctly
6. Update `main_app.py` routing
7. Verify Performance, Trends, Program Deep Dive, Data Tables all work
8. Commit to Git

---

### Phase 6: Extract Comparison Tool Page
**Estimated Time**: 75 minutes  
**Risk Level**: MEDIUM-HIGH (complex logic, statistical calculations)

**Tasks:**
1. Create `pages/comparison_tool.py`
2. Extract lines 2580-3231 from `main_app.py`
3. Import database utilities
4. Handle comparison logic and session state
5. Test YoY comparisons work
6. Update `main_app.py` routing
7. Verify all statistical calculations correct
8. Commit to Git

---

### Phase 7: Extract Marketing Analysis Page
**Estimated Time**: 90 minutes  
**Risk Level**: HIGH (most complex, 4 tabs, global filters)

**Tasks:**
1. Create `pages/marketing_analysis.py`
2. Extract lines 3232-4617 from `main_app.py`
3. Import database and styling utilities
4. Handle global filter system (3 independent filters)
5. Test all 4 tabs work correctly
6. Update `main_app.py` routing
7. Verify Overview, Advanced Analytics, Channel Analytics, Notes all work
8. Commit to Git

---

## Final Structure After All Phases

```
main_app.py                    # ~500 lines (routing, sidebar, config)
├── Imports and page config
├── Global CSS
├── Sidebar navigation
├── Page routing (if/elif)
└── Footer

pages/
├── __init__.py
├── home.py                    # ~600 lines
├── executive_dive.py          # ~1,000 lines
├── comparison_tool.py         # ~650 lines
├── marketing_analysis.py      # ~1,400 lines
├── database.py                # ~400 lines
└── help.py                    # ~500 lines

utils/
├── __init__.py
├── database.py                # Database functions
├── data_processing.py         # Data insights
├── styling.py                 # CSS functions
└── table_display.py           # Table display

test_utils.py                  # Utility tests
REFACTORING_PLAN.md           # This file
```

---

## Testing Checklist (After Each Phase)

- [ ] Page loads without errors
- [ ] All filters work correctly
- [ ] All charts render identically
- [ ] Session state persists across page changes
- [ ] Database queries return same results
- [ ] Styling is identical to original
- [ ] Export/download functionality works
- [ ] No console errors or warnings
- [ ] Navigation between pages works
- [ ] Sidebar highlights correct page

---

## Rollback Plan

If any phase fails:
1. Git revert to previous commit
2. Identify the issue
3. Fix in isolation
4. Re-test before committing

**Git Commit Strategy:**
- One commit per phase
- Descriptive commit messages
- Tag each phase completion

Example commits:
```
git commit -m "Phase 1: Extract utility modules - all tests passing"
git commit -m "Phase 2: Extract Help page - verified working"
git commit -m "Phase 3: Extract Database page - verified working"
```

---

## Benefits of This Approach

1. **Incremental Testing**: Test after each extraction
2. **Easy Rollback**: Can revert any single phase
3. **Low Risk**: One page at a time minimizes errors
4. **Production Safe**: Can deploy after each successful phase
5. **Clear Progress**: Easy to track what's done vs. remaining

---

## Notes

- **Current main_app.py**: Backed up in Git (commit before Phase 1)
- **All utilities tested**: 100% passing
- **Database verified**: 7 programs, 348 records, marketing data present
- **Ready for Phase 2**: Help page extraction

---

## Contact

For questions or issues during refactoring:
- **Developer**: Tirth Shah (tirth.shah@tamu.edu)
- **Platform Version**: 2.4
- **Refactoring Start Date**: January 23, 2026
