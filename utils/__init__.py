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
    load_yoy_comparison_data
)

from .data_processing import generate_insights
from .table_display import process_table_display

__all__ = [
    # Database functions
    'get_connection',
    'normalize_program_name',
    'load_programs',
    'load_cohort_data',
    'load_yoy_comparison_data',
    # Data processing
    'generate_insights',
    # Table display
    'process_table_display'
]
