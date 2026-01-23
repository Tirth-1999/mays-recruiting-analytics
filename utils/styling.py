"""
Styling utility functions for Mays Analytics Platform
Common CSS and styling functions used across pages
"""
import streamlit as st


def apply_global_css():
    """Apply global CSS styling for the entire application"""
    st.markdown("""
    <style>
    .nav-menu {
        background: #f8f9fa;
        padding: 10px 20px;
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .nav-button {
        display: inline-block;
        padding: 10px 20px;
        margin: 0 5px;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    .nav-button.active {
        background: #500000;
        color: white !important;
        border-color: #500000;
    }
    .nav-button.inactive {
        background: white;
        color: #500000;
        border-color: #e9ecef;
    }
    .nav-button.inactive:hover {
        background: #e9ecef;
        border-color: #500000;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        text-align: center;
    }
    .insight-card {
        background: linear-gradient(135deg, #500000 0%, #700000 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    .section-divider {
        height: 3px;
        background: linear-gradient(90deg, #500000, #B00000);
        border: none;
        border-radius: 2px;
        margin: 2rem 0;
    }
    .performance-indicator {
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
    }
    .data-insight {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #500000;
        margin: 1rem 0;
        font-size: 0.95rem;
    }
    .metric-highlight {
        background: #500000;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .indicator-excellent { background: #d4edda; color: #155724; }
    .indicator-good { background: #fff3cd; color: #856404; }
    .indicator-needs-attention { background: #f8d7da; color: #721c24; }
    .data-insight {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #500000;
        margin: 1rem 0;
    }
    .metric-highlight {
        background: #500000;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        display: inline-block;
        font-weight: bold;
        margin: 0.25rem;
    }

    /* Remove bottom border from block container */
    .block-container {
        padding-bottom: 1rem !important;
        border-bottom: none !important;
    }

    /* Footer responsive styling */
    @media (max-width: 768px) {
        .footer-content {
            text-align: center !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def apply_chrome_tabs_css():
    """Apply Chrome-style tabs CSS for Marketing Analysis and Data Explorer"""
    st.markdown("""
    <style>
    /* Chrome-style tabs - Base styles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px !important;
        justify-content: center !important;
        background-color: transparent !important;
        padding: 0px 20px !important;
        border-bottom: none !important;
        margin-bottom: 30px !important;
        display: flex !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        scroll-behavior: smooth !important;
        -webkit-overflow-scrolling: touch !important;
        scrollbar-width: thin !important;
        scrollbar-color: #500000 #f0f0f0 !important;
        box-sizing: border-box !important;
    }
    
    /* Always show scrollbar when content overflows */
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        height: 10px !important;
        display: block !important;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
        background: #f0f0f0 !important;
        border-radius: 5px !important;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
        background: #500000 !important;
        border-radius: 5px !important;
        min-width: 50px !important;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb:hover {
        background: #700000 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px !important;
        padding: 0px 32px !important;
        background-color: #f5f5f5 !important;
        border-radius: 8px 8px 0px 0px !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        border: none !important;
        border-bottom: 3px solid transparent !important;
        color: #666 !important;
        margin-bottom: -2px !important;
        flex-shrink: 0 !important;
        white-space: nowrap !important;
        min-width: fit-content !important;
        box-sizing: border-box !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #500000 !important;
        border-bottom: 3px solid #500000 !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e8e8e8 !important;
        color: #500000 !important;
    }
    
    .stTabs [aria-selected="true"]:hover {
        background-color: white !important;
    }
    
    /* Tablet adjustments - switch to left-aligned */
    @media screen and (max-width: 1024px) {
        .stTabs [data-baseweb="tab-list"] {
            justify-content: flex-start !important;
            padding: 0px 15px !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0px 24px !important;
            font-size: 14px !important;
        }
        
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
            height: 12px !important;
        }
    }
    
    /* Mobile adjustments - left-aligned */
    @media screen and (max-width: 768px) {
        .stTabs [data-baseweb="tab-list"] {
            justify-content: flex-start !important;
            padding: 0px 10px !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0px 20px !important;
            font-size: 13px !important;
            height: 42px !important;
        }
    }
    
    /* Small mobile adjustments - left-aligned */
    @media screen and (max-width: 480px) {
        .stTabs [data-baseweb="tab-list"] {
            justify-content: flex-start !important;
            padding: 0px 10px !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0px 16px !important;
            font-size: 12px !important;
            height: 40px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def apply_section_header_css():
    """Apply section header CSS styling"""
    st.markdown("""
    <style>
    /* Section headers with centered styling */
    .section-header {
        text-align: center;
        padding: 12px;
        background: #e9ecef;
        border-radius: 8px;
        margin: 20px 0 15px 0;
    }
    .section-header h3 {
        margin: 0;
        color: #500000;
        font-size: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
