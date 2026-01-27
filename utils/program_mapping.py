"""
Program Name Mapping Utility
Centralizes all program name conversions to ensure consistency
"""

# Official program mapping (SHORT CODE → FULL DISPLAY NAME)
PROGRAM_CODE_TO_NAME = {
    'MBA': 'Flex Online MBA',
    'MS ACCT': 'Flex Online MS Accounting',
    'MS ENLD': 'Flex Online MS Entrepreneurial Leadership',
    'MS HRM': 'Flex Online MS Human Resource Management',
    'MS MISY': 'Flex Online MS Management Information Systems',
    'MS MKTG': 'Flex Online MS Marketing',
    'MS SPBA': 'Flex Online AI in Business Program',
}

# Reverse mapping (FULL NAME → SHORT CODE)
PROGRAM_NAME_TO_CODE = {v: k for k, v in PROGRAM_CODE_TO_NAME.items()}

# All valid program codes
PROGRAM_CODES = list(PROGRAM_CODE_TO_NAME.keys())

# All valid program names
PROGRAM_NAMES = list(PROGRAM_CODE_TO_NAME.values())

# Color palette for programs (7 distinct colors)
PROGRAM_COLORS = {
    'Flex Online MBA': '#500000',  # Maroon (Texas A&M primary)
    'Flex Online MS Accounting': '#0066CC',  # Blue
    'Flex Online MS Entrepreneurial Leadership': '#FF6B35',  # Orange
    'Flex Online MS Human Resource Management': '#2ECC71',  # Green
    'Flex Online MS Management Information Systems': '#9B59B6',  # Purple
    'Flex Online MS Marketing': '#F39C12',  # Gold
    'Flex Online AI in Business Program': '#E74C3C',  # Red
}

def get_program_display_name(code_or_name):
    """
    Convert any program identifier to official display name.
    
    Args:
        code_or_name: Program code (e.g., 'MBA') or any name variant
        
    Returns:
        Official display name (e.g., 'Flex Online MBA')
        
    Examples:
        >>> get_program_display_name('MBA')
        'Flex Online MBA'
        >>> get_program_display_name('Flex Online Mba')
        'Flex Online MBA'
        >>> get_program_display_name('MS ACCT')
        'Flex Online MS Accounting'
    """
    # If it's a short code, return the official name
    if code_or_name in PROGRAM_CODE_TO_NAME:
        return PROGRAM_CODE_TO_NAME[code_or_name]
    
    # If it's already the official name, return as-is
    if code_or_name in PROGRAM_NAMES:
        return code_or_name
    
    # Try case-insensitive matching for variants
    code_or_name_lower = str(code_or_name).lower()
    for official_name in PROGRAM_NAMES:
        if official_name.lower() == code_or_name_lower:
            return official_name
    
    # Handle marketing Excel variations (abbreviated names)
    marketing_variations = {
        'flex online accounting': 'Flex Online MS Accounting',
        'flex online hrm': 'Flex Online MS Human Resource Management',
        'flex online marketing': 'Flex Online MS Marketing',
        'flex online mis': 'Flex Online MS Management Information Systems',
        'flex online ai and business program': 'Flex Online AI in Business Program',
        'flex online mba': 'Flex Online MBA',
        'flex online ms entrepreneurial leadership': 'Flex Online MS Entrepreneurial Leadership',
    }
    
    if code_or_name_lower in marketing_variations:
        return marketing_variations[code_or_name_lower]
    
    # Special case: "General Awareness" (marketing only)
    if 'general' in code_or_name_lower and 'awareness' in code_or_name_lower:
        return 'General Awareness'
    
    # If no match found, return original (for backwards compatibility)
    return code_or_name

def get_program_code(name):
    """
    Convert display name to short code.
    
    Args:
        name: Program display name
        
    Returns:
        Short code (e.g., 'MBA')
        
    Examples:
        >>> get_program_code('Flex Online MBA')
        'MBA'
        >>> get_program_code('Flex Online MS Accounting')
        'MS ACCT'
    """
    if name in PROGRAM_NAME_TO_CODE:
        return PROGRAM_NAME_TO_CODE[name]
    
    # Try case-insensitive matching
    name_lower = str(name).lower()
    for official_name, code in PROGRAM_NAME_TO_CODE.items():
        if official_name.lower() == name_lower:
            return code
    
    # If no match, return original
    return name

def get_program_color(program_name):
    """
    Get the color for a program.
    
    Args:
        program_name: Program display name or code
        
    Returns:
        Hex color code
    """
    # Convert to display name first
    display_name = get_program_display_name(program_name)
    
    # Return color if found, otherwise default to gray
    return PROGRAM_COLORS.get(display_name, '#95A5A6')

def standardize_program_list(programs):
    """
    Standardize a list of program names/codes to display names.
    
    Args:
        programs: List of program codes or names
        
    Returns:
        List of standardized display names
    """
    return [get_program_display_name(p) for p in programs]

def get_all_programs_display():
    """
    Get all program display names in order.
    
    Returns:
        List of all official program display names
    """
    return PROGRAM_NAMES.copy()

def get_all_programs_with_colors():
    """
    Get all programs with their colors.
    
    Returns:
        Dict mapping program names to colors
    """
    return PROGRAM_COLORS.copy()
