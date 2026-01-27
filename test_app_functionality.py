"""
Quick test to verify app functionality after program name standardization
"""
import sqlite3
import pandas as pd

def test_database_consistency():
    """Test that database has standardized program names"""
    print("=" * 80)
    print("TEST 1: Database Consistency")
    print("=" * 80)
    
    conn = sqlite3.connect('edulytix.db')
    
    # Check admissions_metrics
    admissions_programs = pd.read_sql(
        "SELECT DISTINCT program FROM admissions_metrics ORDER BY program", 
        conn
    )
    print("\n📊 Programs in admissions_metrics:")
    for prog in admissions_programs['program']:
        print(f"   • {prog}")
    
    # Check programs table
    programs_table = pd.read_sql(
        "SELECT program_code, program_name FROM programs ORDER BY program_code", 
        conn
    )
    print("\n📊 Programs table mapping:")
    for _, row in programs_table.iterrows():
        print(f"   {row['program_code']:10} → {row['program_name']}")
    
    # Check marketing_spend
    marketing_programs = pd.read_sql(
        "SELECT DISTINCT program FROM marketing_spend ORDER BY program", 
        conn
    )
    print("\n📊 Programs in marketing_spend:")
    for prog in marketing_programs['program']:
        print(f"   • {prog}")
    
    conn.close()
    
    # Verify all use full names
    short_codes = ['MBA', 'MS ACCT', 'MS ENLD', 'MS HRM', 'MS MISY', 'MS MKTG', 'MS SPBA']
    has_short_codes = any(code in admissions_programs['program'].values for code in short_codes)
    
    if has_short_codes:
        print("\n❌ FAIL: Found short codes in admissions_metrics!")
        return False
    else:
        print("\n✅ PASS: All programs use full names!")
        return True

def test_query_functionality():
    """Test that queries with full names return data"""
    print("\n" + "=" * 80)
    print("TEST 2: Query Functionality")
    print("=" * 80)
    
    conn = sqlite3.connect('edulytix.db')
    
    test_cases = [
        ("Flex Online MBA", True),
        ("MBA", False),
        ("Flex Online MS Accounting", True),
        ("MS ACCT", False),
    ]
    
    all_passed = True
    for program_name, should_have_data in test_cases:
        result = pd.read_sql(
            f"SELECT COUNT(*) as count FROM admissions_metrics WHERE program = ?",
            conn,
            params=[program_name]
        )
        count = result['count'].iloc[0]
        
        if should_have_data:
            if count > 0:
                print(f"   ✅ '{program_name}' → {count} records")
            else:
                print(f"   ❌ '{program_name}' → {count} records (expected > 0)")
                all_passed = False
        else:
            if count == 0:
                print(f"   ✅ '{program_name}' → {count} records (correctly returns nothing)")
            else:
                print(f"   ❌ '{program_name}' → {count} records (expected 0)")
                all_passed = False
    
    conn.close()
    
    if all_passed:
        print("\n✅ PASS: All queries work correctly!")
    else:
        print("\n❌ FAIL: Some queries failed!")
    
    return all_passed

def test_dropdown_values():
    """Test that dropdown values match database"""
    print("\n" + "=" * 80)
    print("TEST 3: Dropdown Values")
    print("=" * 80)
    
    conn = sqlite3.connect('edulytix.db')
    
    # Simulate what the app does
    programs_df = pd.read_sql('SELECT * FROM programs WHERE is_active = 1', conn)
    
    # What the app NOW uses (after fix)
    program_options_correct = ['All Programs'] + sorted(programs_df['program_name'].tolist())
    
    # What the app USED TO use (before fix)
    program_options_old = ['All Programs'] + sorted(programs_df['program_code'].tolist())
    
    print("\n📊 Dropdown values (AFTER FIX - CORRECT):")
    for opt in program_options_correct[:5]:  # Show first 5
        print(f"   • {opt}")
    
    print("\n📊 Dropdown values (BEFORE FIX - WRONG):")
    for opt in program_options_old[:5]:  # Show first 5
        print(f"   • {opt}")
    
    # Test if dropdown values can query data
    print("\n🔍 Testing if dropdown values can query data:")
    
    test_program = program_options_correct[1]  # First real program (not "All Programs")
    result = pd.read_sql(
        "SELECT COUNT(*) as count FROM admissions_metrics WHERE program = ?",
        conn,
        params=[test_program]
    )
    count = result['count'].iloc[0]
    
    if count > 0:
        print(f"   ✅ Dropdown value '{test_program}' returns {count} records")
        print("\n✅ PASS: Dropdown values match database!")
        conn.close()
        return True
    else:
        print(f"   ❌ Dropdown value '{test_program}' returns 0 records")
        print("\n❌ FAIL: Dropdown values don't match database!")
        conn.close()
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("TESTING APP FUNCTIONALITY AFTER PROGRAM NAME STANDARDIZATION")
    print("=" * 80)
    
    results = {
        'Database Consistency': test_database_consistency(),
        'Query Functionality': test_query_functionality(),
        'Dropdown Values': test_dropdown_values(),
    }
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS PASSED! App should work correctly.")
        print("=" * 80)
        print("\n✅ You can now use the app at http://localhost:8502")
        print("✅ Dropdowns will show full program names")
        print("✅ Queries will return data correctly")
    else:
        print("\n" + "=" * 80)
        print("⚠️  SOME TESTS FAILED! Review errors above.")
        print("=" * 80)
    
    return all_passed

if __name__ == '__main__':
    run_all_tests()
