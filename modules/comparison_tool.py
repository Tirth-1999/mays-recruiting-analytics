"""
Comparison Tool Page Module
Extracted from main_app.py as part of Phase 5 refactoring
"""

import streamlit as st
from modules.comparison_tool_content import render_comparison_tool


def render():
    """Render the Comparison Tool page"""
    render_comparison_tool(key_prefix="comparison_tool")
