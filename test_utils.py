"""
Test script to verify utility modules work correctly
Run this before proceeding with page extraction
"""
import sys
import pandas as pd

print("=" * 80)
print("TESTING UTILITY MODULES")
print("=" * 80)

# Test 1: Import utils
print("\n1. Testing imports...")
try:
    from utils import (
        get_connection,
        normalize_program_name,
        load_programs,
        load_cohort_data,
        check_marketing_data_exists,
        generate_insights
    )
    print("✓ All utility imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Database connection
print("\n2. Testing database connection...")
try:
    conn = get_connection()
    print(f"✓ Database connection successful: {type(conn)}")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
    sys.exit(1)

# Test 3: Program name normalization
print("\n3. Testing program name normalization...")
test_cases = [
    ("Flex Online Mba", "MBA"),
    ("Flex Online Accounting", "ACCT"),
    ("MBA", "MBA"),
    ("MS ACCT", "ACCT"),
]
all_passed = True
for input_name, expected in test_cases:
    result = normalize_program_name(input_name)
    if result == expected:
        print(f"✓ '{input_name}' → '{result}'")
    else:
        print(f"✗ '{input_name}' → '{result}' (expected '{expected}')")
        all_passed = False

if not all_passed:
    print("✗ Some normalization tests failed")
    sys.exit(1)

# Test 4: Load programs
print("\n4. Testing load_programs()...")
try:
    programs_df = load_programs()
    print(f"✓ Loaded {len(programs_df)} programs")
    if len(programs_df) > 0:
        print(f"  Sample programs: {', '.join(programs_df['program_code'].head(3).tolist())}")
except Exception as e:
    print(f"✗ load_programs() failed: {e}")
    sys.exit(1)

# Test 5: Load cohort data
print("\n5. Testing load_cohort_data()...")
try:
    cohort_data = load_cohort_data(2028)
    print(f"✓ Loaded {len(cohort_data)} records for cohort 2028")
    if len(cohort_data) > 0:
        print(f"  Date range: {cohort_data['report_date'].min()} to {cohort_data['report_date'].max()}")
except Exception as e:
    print(f"✗ load_cohort_data() failed: {e}")
    sys.exit(1)

# Test 6: Check marketing data
print("\n6. Testing check_marketing_data_exists()...")
try:
    has_data, message = check_marketing_data_exists()
    print(f"✓ Marketing data check: {has_data} - {message}")
except Exception as e:
    print(f"✗ check_marketing_data_exists() failed: {e}")
    sys.exit(1)

# Test 7: Generate insights
print("\n7. Testing generate_insights()...")
try:
    if len(cohort_data) > 0:
        latest_date = cohort_data['report_date'].max()
        latest_data = cohort_data[cohort_data['report_date'] == latest_date]
        insights = generate_insights(cohort_data, latest_data)
        print(f"✓ Generated {len(insights)} insights")
        for insight in insights[:2]:  # Show first 2
            print(f"  - {insight}")
    else:
        print("⚠ No data to generate insights from")
except Exception as e:
    print(f"✗ generate_insights() failed: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("ALL TESTS PASSED ✓")
print("=" * 80)
print("\nUtility modules are working correctly!")
print("You can now proceed with Phase 2: Page extraction")
