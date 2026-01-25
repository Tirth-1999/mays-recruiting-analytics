#!/usr/bin/env python3
"""
Deployment Verification Script
Checks if all required files are updated before pushing to production
"""

import re
import sys
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def check_version_py():
    """Check if version.py is properly updated"""
    print_header("Checking version.py")
    
    try:
        with open('version.py', 'r') as f:
            content = f.read()
        
        # Extract version
        version_match = re.search(r'VERSION = ["\']([^"\']+)["\']', content)
        if version_match:
            version = version_match.group(1)
            print_success(f"Version found: {version}")
        else:
            print_error("VERSION not found in version.py")
            return False, None
        
        # Check other fields
        checks = [
            ('VERSION_NAME', r'VERSION_NAME = ["\']([^"\']+)["\']'),
            ('VERSION_STATUS', r'VERSION_STATUS = ["\']([^"\']+)["\']'),
            ('LAST_UPDATED', r'LAST_UPDATED = ["\']([^"\']+)["\']')
        ]
        
        for field, pattern in checks:
            if re.search(pattern, content):
                print_success(f"{field} is set")
            else:
                print_error(f"{field} is missing")
                return False, version
        
        return True, version
    except FileNotFoundError:
        print_error("version.py not found!")
        return False, None

def check_readme(version):
    """Check if README.md is updated with current version"""
    print_header("Checking README.md")
    
    try:
        with open('README.md', 'r') as f:
            content = f.read()
        
        # Check version in header
        if f"**Version {version}**" in content:
            print_success(f"Version {version} found in header")
        else:
            print_error(f"Version {version} NOT found in header")
            return False
        
        # Check version badge
        if f"version-{version}-blue" in content:
            print_success(f"Version badge updated to {version}")
        else:
            print_error(f"Version badge NOT updated to {version}")
            return False
        
        # Check for "What's New in Version X.X"
        if f"## What's New in Version {version}" in content:
            print_success(f"'What's New in Version {version}' section found")
        else:
            print_error(f"'What's New in Version {version}' section NOT found")
            return False
        
        # Count "What's New" sections (should be only 1)
        whats_new_count = content.count("## What's New in Version")
        if whats_new_count == 1:
            print_success("Only current version in 'What's New' (old versions removed)")
        else:
            print_warning(f"Found {whats_new_count} 'What's New' sections - should remove old versions!")
            return False
        
        return True
    except FileNotFoundError:
        print_error("README.md not found!")
        return False

def check_docs_readme(version):
    """Check if docs/README.md is updated"""
    print_header("Checking docs/README.md")
    
    try:
        with open('docs/README.md', 'r') as f:
            content = f.read()
        
        # Check for version section
        if f"## What's New in Version {version}" in content:
            print_success(f"Version {version} section found in docs/README.md")
            return True
        else:
            print_error(f"Version {version} section NOT found in docs/README.md")
            return False
    except FileNotFoundError:
        print_error("docs/README.md not found!")
        return False

def check_versioning_md(version):
    """Check if VERSIONING.md is updated"""
    print_header("Checking VERSIONING.md")
    
    try:
        with open('VERSIONING.md', 'r') as f:
            content = f.read()
        
        # Check for version entry
        if f"## Version {version}" in content:
            print_success(f"Version {version} entry found")
        else:
            print_error(f"Version {version} entry NOT found")
            return False
        
        # Check if it's marked as current
        version_section = content.split(f"## Version {version}")[1].split("##")[0]
        if "**Status**: Current Release" in version_section:
            print_success("Marked as Current Release")
        else:
            print_warning("Not marked as Current Release")
        
        return True
    except FileNotFoundError:
        print_error("VERSIONING.md not found!")
        return False
    except IndexError:
        print_error("Could not parse VERSIONING.md")
        return False

def check_changelog_md(version):
    """Check if CHANGELOG.md is updated"""
    print_header("Checking CHANGELOG.md")
    
    try:
        with open('CHANGELOG.md', 'r') as f:
            content = f.read()
        
        # Extract version number for changelog format [X.X.X]
        version_parts = version.split('.')
        if len(version_parts) == 2:
            changelog_version = f"{version}.0"
        else:
            changelog_version = version
        
        # Check for version entry
        if f"## [{changelog_version}]" in content:
            print_success(f"Version [{changelog_version}] entry found")
            return True
        else:
            print_error(f"Version [{changelog_version}] entry NOT found")
            return False
    except FileNotFoundError:
        print_error("CHANGELOG.md not found!")
        return False

def check_git_status():
    """Check git status for uncommitted changes"""
    print_header("Checking Git Status")
    
    import subprocess
    
    try:
        # Check for uncommitted changes
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print_warning("Uncommitted changes detected:")
            print(result.stdout)
            return False
        else:
            print_success("No uncommitted changes")
            return True
    except Exception as e:
        print_error(f"Could not check git status: {e}")
        return False

def check_temp_files():
    """Check for temporary files that shouldn't be committed"""
    print_header("Checking for Temporary Files")
    
    temp_patterns = [
        '**/*_temp.md',
        '**/*_test.md',
        '**/*_backup.md',
        '**/*.tmp',
        '**/.DS_Store'
    ]
    
    found_temp = False
    for pattern in temp_patterns:
        for file in Path('.').glob(pattern):
            if not any(part.startswith('.') for part in file.parts[:-1]):  # Skip hidden dirs
                print_warning(f"Temporary file found: {file}")
                found_temp = True
    
    if not found_temp:
        print_success("No temporary files found")
        return True
    else:
        print_error("Remove temporary files before deployment!")
        return False

def main():
    """Run all checks"""
    print(f"\n{Colors.BOLD}🚀 Deployment Verification Script{Colors.END}")
    print(f"{Colors.BOLD}Checking if all files are ready for production...{Colors.END}")
    
    all_passed = True
    
    # Check version.py first to get version number
    passed, version = check_version_py()
    all_passed = all_passed and passed
    
    if not version:
        print_error("\nCannot continue without version number!")
        sys.exit(1)
    
    # Run all other checks
    checks = [
        (check_readme, version),
        (check_docs_readme, version),
        (check_versioning_md, version),
        (check_changelog_md, version),
        (check_temp_files, ),
        (check_git_status, )
    ]
    
    for check_func, *args in checks:
        passed = check_func(*args)
        all_passed = all_passed and passed
    
    # Final summary
    print_header("Deployment Check Summary")
    
    if all_passed:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED!{Colors.END}")
        print(f"{Colors.GREEN}Ready to deploy version {version} to production.{Colors.END}")
        print(f"\n{Colors.BOLD}Next steps:{Colors.END}")
        print("1. git add -A")
        print(f"2. git commit -m 'Release v{version}: ...'")
        print(f"3. git tag -a v{version} -m '...'")
        print("4. git push origin main")
        print(f"5. git push origin v{version}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME CHECKS FAILED!{Colors.END}")
        print(f"{Colors.RED}Please fix the issues above before deploying.{Colors.END}")
        print(f"\n{Colors.BOLD}See DEPLOYMENT_CHECKLIST.md for detailed instructions.{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
