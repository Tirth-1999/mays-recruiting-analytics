"""
Utility modules for Mays Analytics Platform
Shared functions and resources across all pages
"""

# Import all utility functions for easy access
from .database import (
    get_connection,
    normalize_program_name,
    load_programs,
    load_cohort_data,
    load_yoy_comparison_data,
    check_marketing_data_exists,
    get_quick_insights,
    answer_question
)

from .data_processing import generate_insights

from .styling import (
    apply_global_css,
    apply_chrome_tabs_css,
    apply_section_header_css
)

from .table_display import process_table_display

__all__ = [
    # Database functions
    'get_connection',
    'normalize_program_name',
    'load_programs',
    'load_cohort_data',
    'load_yoy_comparison_data',
    'check_marketing_data_exists',
    'get_quick_insights',
    'answer_question',
    # Data processing
    'generate_insights',
    # Styling
    'apply_global_css',
    'apply_chrome_tabs_css',
    'apply_section_header_css',
    # Table display
    'process_table_display'
]

