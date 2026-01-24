"""
Mays Online Flex Recruiting Analytics Platform
Single-Page Application with Navigation
"""
import streamlit as st
from version import VERSION_FULL

# Page config
st.set_page_config(
    page_title="Mays Online Flex Recruiting Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Remove top padding and adjust layout for sidebar
st.markdown("""
<style>
    .main .block-container {
        padding-left: 1rem !important; 
        padding-right: 1rem !important;
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    div[data-testid="stAppViewContainer"] > .main {
        padding-top: 0rem !important;
    }
    .stApp > header {
        display: none !important;
    }
    /* div[data-testid="stToolbar"] {
        display: none !important;
    } */
</style>
""", unsafe_allow_html=True)

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

# CSS for the entire application
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
.indicator-excellent { background: #d4edda; color: #155724; }
.indicator-good { background: #fff3cd; color: #856404; }
.indicator-needs-attention { background: #f8d7da; color: #721c24; }

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

# Professional Mays Business School Banner
st.markdown("""
    <div style='background: linear-gradient(135deg, #500000 0%, #700000 50%, #500000 100%); 
                padding: 1.5rem 2rem; 
                border-radius: 10px; 
                text-align: center;
                border: 3px solid #C5A572;
                margin-bottom: 1rem;'>
        <img src='data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyBpZD0iTGF5ZXJfMSIgZGF0YS1uYW1lPSJMYXllciAxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDgwIDEwODAiPgogIDxkZWZzPgogICAgPHN0eWxlPgogICAgICAuY2xzLTEgewogICAgICAgIGZpbGw6ICM1MDAwMDA7CiAgICAgIH0KCiAgICAgIC5jbHMtMSwgLmNscy0yLCAuY2xzLTMgewogICAgICAgIHN0cm9rZS13aWR0aDogMHB4OwogICAgICB9CgogICAgICAuY2xzLTIgewogICAgICAgIGZpbGw6ICNiMWIzYjY7CiAgICAgIH0KCiAgICAgIC5jbHMtMyB7CiAgICAgICAgZmlsbDogI2ZmZjsKICAgICAgfQogICAgPC9zdHlsZT4KICA8L2RlZnM+CiAgPHJlY3QgY2xhc3M9ImNscy0xIiB4PSIyMDEuMjgiIHk9IjIyMi41NyIgd2lkdGg9IjYyOS43OSIgaGVpZ2h0PSI2MzQuNzkiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTMiIHBvaW50cz0iNzQ3LjQ0IDQ3NS4yMiA3MDAuNjcgNDc1LjIyIDY5Ny45NyA0NzUuMjIgNjk2Ljc1IDQ3Ny42NyA2NjIuODQgNTQ4LjI3IDYyOC44IDQ3Ny42MyA2MjcuNjEgNDc1LjIyIDYyNC45MiA0NzUuMjIgNTc5LjcxIDQ3NS4yMiA1NzUuNDQgNDc1LjIyIDU3NS40NCA0NzkuNTIgNTc1LjQ0IDUwMy41OSA1NzUuNDQgNTA3LjkgNTc5LjcxIDUwNy45IDU4Ny40NCA1MDcuOSA1ODcuNDQgNjA5LjAxIDU3OS4wOCA2MDkuMDEgNTc0Ljc4IDYwOS4wMSA1NzQuNzggNjEzLjMyIDU3NC43OCA2MzcuMzkgNTc0Ljc4IDY0MS42OSA1NzkuMDggNjQxLjY5IDYyOS44NSA2NDEuNjkgNjM0LjE1IDY0MS42OSA2MzQuMTUgNjM3LjM5IDYzNC4xNSA2MTMuMzIgNjM0LjE1IDYwOS4wMSA2MjkuODUgNjA5LjAxIDYyMS4wNyA2MDkuMDEgNjIxLjA3IDUzNy4yNSA2NTguOTkgNjE1LjQ1IDY2Mi44NCA2MjMuNDMgNjY2Ljc2IDYxNS40NSA3MDUuMDcgNTM3LjA4IDcwNS4wNyA2MDkuMDEgNjk2LjcxIDYwOS4wMSA2OTIuMzcgNjA5LjAxIDY5Mi4zNyA2MTMuMzIgNjkyLjM3IDYzNy4zOSA2OTIuMzcgNjQxLjY5IDY5Ni43MSA2NDEuNjkgNzQ3LjQ0IDY0MS42OSA3NTEuNzUgNjQxLjY5IDc1MS43NSA2MzcuMzkgNzUxLjc1IDYxMy4zMiA3NTEuNzUgNjA5LjAxIDc0Ny40NCA2MDkuMDEgNzM4LjcgNjA5LjAxIDczOC43IDUwNy45IDc0Ny40NCA1MDcuOSA3NTEuNzUgNTA3LjkgNzUxLjc1IDUwMy41OSA3NTEuNzUgNDc5LjUyIDc1MS43NSA0NzUuMjIgNzQ3LjQ0IDQ3NS4yMiIvPgogIDxwYXRoIGNsYXNzPSJjbHMtMyIgZD0iTTQ1Mi42LDYwOC45MWgtMTMuNTFsLTQzLjk1LTEwMS40N2g4LjQ3di0zMi44MmgtNzAuNTR2MzIuNzFoOS43M2wtNDMuOTEsMTAxLjQ3aC0xOC4zdjMyLjcxaDY0LjAzdi0zMi43MWgtOS4zMWw3LjMxLTE2LjloNTIuODNsNy4yOCwxNi45aC05LjgzdjMyLjcxaDY0LjA2di0zMi43MWwtNC4zNy4xMVpNMzgxLjI5LDU1OS4zM2gtMjQuNDlsMTIuMjUtMjguMzgsMTIuMjUsMjguMzhaIi8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0zIiBwb2ludHM9IjY5My43IDM0OC4yNSAzMzcuNDkgMzQ4LjI1IDMzMi41NiAzNDguMjUgMzMyLjU2IDM1My4xOCAzMzIuNTYgNDQ4LjM1IDMzMi41NiA0NTMuMjggMzM3LjQ5IDQ1My4yOCAzOTkgNDUzLjI4IDQwMy45MyA0NTMuMjggNDAzLjkzIDQ0OC4zNSA0MDMuOTMgNDEzLjAxIDQ3OS45MyA0MTMuMDEgNDc5LjkzIDY2My43NyA0NDQuNTUgNjYzLjc3IDQzOS42NSA2NjMuNzcgNDM5LjY1IDY2OC43IDQzOS42NSA3MzAuMjEgNDM5LjY1IDczNS4xNSA0NDQuNTUgNzM1LjE1IDU4Ni42IDczNS4xNSA1OTEuNTQgNzM1LjE1IDU5MS41NCA3MzAuMjEgNTkxLjU0IDY2OC43IDU5MS41NCA2NjMuNzcgNTg2LjYgNjYzLjc3IDU1MS4zIDY2My43NyA1NTEuMyA0MTMuMDEgNjI2Ljg0IDQxMy4wMSA2MjYuODQgNDQ3Ljg5IDYyNi44NCA0NTIuODMgNjMxLjc3IDQ1Mi44MyA2OTMuNyA0NTIuODMgNjk4LjY0IDQ1Mi44MyA2OTguNjQgNDQ3Ljg5IDY5OC42NCAzNTMuMTggNjk4LjY0IDM0OC4yNSA2OTMuNyAzNDguMjUiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iNTYxLjgzIDY5My4wNiA1NzYuODggNjc3LjU2IDU3Ni44OCA3MjAuMDMgNTYxLjgzIDcwNS42NSA1NjEuODMgNjkzLjA2Ii8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0yIiBwb2ludHM9IjUzNi43OCA2NzguNjggNTIxLjcgNjkzLjUxIDUyMS43IDM4My40NSA1MzYuNzggMzk4LjQ2IDUzNi43OCA2NzguNjgiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iMzYyLjcyIDM3Ny45OSAzNDcuMjUgMzYyLjk0IDY3Ni40NSAzNjIuOTQgNjU3IDM3Ny45OSAzNjIuNzIgMzc3Ljk5Ii8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0yIiBwb2ludHM9IjY4NC40MyA0MzkuMDQgNjY5LjM5IDQyNC42NiA2NjkuMzkgMzg2LjM4IDY4NC40MyAzNzAuOTIgNjg0LjQzIDQzOS4wNCIvPgogIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTg1My40Niw4NDQuOGMwLTYuOTgsNS42NS0xMi42MywxMi42My0xMi42M3MxMi42Myw1LjY1LDEyLjYzLDEyLjYzLTUuNjUsMTIuNjMtMTIuNjMsMTIuNjMtMTIuNjMtNS42NS0xMi42My0xMi42M2gwWk04NzUuNjQsODQ0LjhjLS4zNS01LjI2LTQuOS05LjI1LTEwLjE2LTguOS01LjI2LjM1LTkuMjUsNC45LTguOSwxMC4xNi4zMyw1LjAxLDQuNDksOC45MSw5LjUxLDguOTIsNS4zNS0uMDcsOS42My00LjQ3LDkuNTYtOS44MiwwLS4xMiwwLS4yNC0uMDEtLjM2Wk04NjEuMjMsODM3LjU5aDUuMzJjMy41LDAsNS4yOCwxLjE5LDUuMjgsNC4yLjIsMS45Mi0xLjIsMy42NC0zLjEyLDMuODQtLjIxLjAyLS40Mi4wMi0uNjIsMGwzLjg1LDYuMjZoLTIuNzNsLTMuNzQtNi4yM2gtMS42MXY2LjEyaC0yLjY2bC4wNC0xNC4yMVpNODYzLjg4LDg0My43MWgyLjM0YzEuNTcsMCwyLjk0LS4yMSwyLjk0LTIuMTNzLTEuNTQtMS45Ni0yLjktMS45NmgtMi4zOHY0LjA5WiIvPgo8L3N2Zz4=' 
             style='width: 90px; height: 90px; margin-bottom: 0.5rem;' />
        <h1 style='color: white; margin: 0.3rem 0; font-size: 2.5rem; font-weight: bold;'>
            Mays Online Flex Recruiting Analytics Platform
        </h1>
        <p style='color: #C5A572; margin: 0.3rem 0; font-size: 1.1rem;'>
            Admissions Analytics & Strategic Insights
        </p>
        <p style='color: white; margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;'>
            MBA • ACCT • HRM • MISY • MKTG • ENLD • SPBA
        </p>
    </div>
""", unsafe_allow_html=True)

# Navigation Menu with forced equal heights using aggressive CSS
st.markdown("""
<style>
/* Active navigation button styling */
div[data-testid="stButton"] button[kind="primary"] {
    background-color: #500000 !important;
    color: white !important;
    border: 2px solid #500000 !important;
}
div[data-testid="stButton"] button[kind="secondary"] {
    background-color: white !important;
    color: #500000 !important;
    border: 2px solid #e0e0e0 !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation with elegant design
with st.sidebar:
    st.markdown("""
    <style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Sidebar overlay behavior on ALL screen sizes - never shrink content */
    [data-testid="stSidebar"][aria-expanded="true"] {
        position: fixed !important;
        z-index: 999999 !important;
        left: 0 !important;
        top: 0 !important;
        height: 100vh !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.3) !important;
    }
    
    /* Hide sidebar when collapsed - no space taken */
    [data-testid="stSidebar"][aria-expanded="false"] {
        display: none !important;
    }
    
    /* Main content always stays full width - no shifting */
    .main .block-container {
        max-width: 100% !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        transition: none !important;
    }
    
    /* Prevent any margin/padding changes on main content */
    .main {
        margin-left: 0 !important;
        transition: none !important;
    }
    
    /* Reduce top padding of sidebar */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 10px;
    }
    
    /* Elegant logo/brand section - more compact */
    .sidebar-brand {
        text-align: center;
        padding: 5px 10px 10px 10px;
        margin-bottom: 15px;
        border-bottom: 2px solid #C5A572;
    }
    
    .sidebar-brand-title {
        color: #500000;
        font-size: 18px;
        font-weight: bold;
        margin: 8px 0 3px 0;
    }
    
    .sidebar-brand-subtitle {
        color: #666;
        font-size: 11px;
        margin: 0;
    }
    
    /* Navigation section divider */
    .nav-section-title {
        color: #500000;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 20px 0 10px 0;
        padding-left: 5px;
        opacity: 0.7;
    }
    
    /* Style sidebar buttons - elegant and minimal */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        text-align: left !important;
        padding: 10px 15px !important;
        margin: 2px 0 !important;
        border-radius: 8px !important;
        border: none !important;
        background: transparent !important;
        color: #495057 !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #f0f2f6 !important;
        color: #500000 !important;
        transform: translateX(3px) !important;
    }
    
    /* Active/Primary button styling - elegant highlight */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #500000 0%, #700000 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(80, 0, 0, 0.2) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        transform: translateX(3px) !important;
        box-shadow: 0 4px 12px rgba(80, 0, 0, 0.3) !important;
    }
    
    /* Info cards in sidebar */
    .sidebar-info-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        margin: 15px 0;
        font-size: 12px;
    }
    
    .sidebar-info-card strong {
        color: #500000;
        display: block;
        margin-bottom: 5px;
    }
    
    .sidebar-stat {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-left: 3px solid #C5A572;
        padding: 10px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 11px;
    }
    
    .sidebar-stat-value {
        color: #500000;
        font-size: 18px;
        font-weight: bold;
        display: block;
    }
    
    .sidebar-stat-label {
        color: #666;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Brand/Logo Section - more compact
    st.markdown("""
    <div class="sidebar-brand">
        <img src='data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyBpZD0iTGF5ZXJfMSIgZGF0YS1uYW1lPSJMYXllciAxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDgwIDEwODAiPgogIDxkZWZzPgogICAgPHN0eWxlPgogICAgICAuY2xzLTEgewogICAgICAgIGZpbGw6ICM1MDAwMDA7CiAgICAgIH0KCiAgICAgIC5jbHMtMSwgLmNscy0yLCAuY2xzLTMgewogICAgICAgIHN0cm9rZS13aWR0aDogMHB4OwogICAgICB9CgogICAgICAuY2xzLTIgewogICAgICAgIGZpbGw6ICNiMWIzYjY7CiAgICAgIH0KCiAgICAgIC5jbHMtMyB7CiAgICAgICAgZmlsbDogI2ZmZjsKICAgICAgfQogICAgPC9zdHlsZT4KICA8L2RlZnM+CiAgPHJlY3QgY2xhc3M9ImNscy0xIiB4PSIyMDEuMjgiIHk9IjIyMi41NyIgd2lkdGg9IjYyOS43OSIgaGVpZ2h0PSI2MzQuNzkiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTMiIHBvaW50cz0iNzQ3LjQ0IDQ3NS4yMiA3MDAuNjcgNDc1LjIyIDY5Ny45NyA0NzUuMjIgNjk2Ljc1IDQ3Ny42NyA2NjIuODQgNTQ4LjI3IDYyOC44IDQ3Ny42MyA2MjcuNjEgNDc1LjIyIDYyNC45MiA0NzUuMjIgNTc5LjcxIDQ3NS4yMiA1NzUuNDQgNDc1LjIyIDU3NS40NCA0NzkuNTIgNTc1LjQ0IDUwMy41OSA1NzUuNDQgNTA3LjkgNTc5LjcxIDUwNy45IDU4Ny40NCA1MDcuOSA1ODcuNDQgNjA5LjAxIDU3OS4wOCA2MDkuMDEgNTc0Ljc4IDYwOS4wMSA1NzQuNzggNjEzLjMyIDU3NC43OCA2MzcuMzkgNTc0Ljc4IDY0MS42OSA1NzkuMDggNjQxLjY5IDYyOS44NSA2NDEuNjkgNjM0LjE1IDY0MS42OSA2MzQuMTUgNjM3LjM5IDYzNC4xNSA2MTMuMzIgNjM0LjE1IDYwOS4wMSA2MjkuODUgNjA5LjAxIDYyMS4wNyA2MDkuMDEgNjIxLjA3IDUzNy4yNSA2NTguOTkgNjE1LjQ1IDY2Mi44NCA2MjMuNDMgNjY2Ljc2IDYxNS40NSA3MDUuMDcgNTM3LjA4IDcwNS4wNyA2MDkuMDEgNjk2LjcxIDYwOS4wMSA2OTIuMzcgNjA5LjAxIDY5Mi4zNyA2MTMuMzIgNjkyLjM3IDYzNy4zOSA2OTIuMzcgNjQxLjY5IDY5Ni43MSA2NDEuNjkgNzQ3LjQ0IDY0MS42OSA3NTEuNzUgNjQxLjY5IDc1MS43NSA2MzcuMzkgNzUxLjc1IDYxMy4zMiA3NTEuNzUgNjA5LjAxIDc0Ny40NCA2MDkuMDEgNzM4LjcgNjA5LjAxIDczOC43IDUwNy45IDc0Ny40NCA1MDcuOSA3NTEuNzUgNTA3LjkgNzUxLjc1IDUwMy41OSA3NTEuNzUgNDc5LjUyIDc1MS43NSA0NzUuMjIgNzQ3LjQ0IDQ3NS4yMiIvPgogIDxwYXRoIGNsYXNzPSJjbHMtMyIgZD0iTTQ1Mi42LDYwOC45MWgtMTMuNTFsLTQzLjk1LTEwMS40N2g4LjQ3di0zMi44MmgtNzAuNTR2MzIuNzFoOS43M2wtNDMuOTEsMTAxLjQ3aC0xOC4zdjMyLjcxaDY0LjAzdi0zMi43MWgtOS4zMWw3LjMxLTE2LjloNTIuODNsNy4yOCwxNi45aC05LjgzdjMyLjcxaDY0LjA2di0zMi43MWwtNC4zNy4xMVpNMzgxLjI5LDU1OS4zM2gtMjQuNDlsMTIuMjUtMjguMzgsMTIuMjUsMjguMzhaIi8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0zIiBwb2ludHM9IjY5My43IDM0OC4yNSAzMzcuNDkgMzQ4LjI1IDMzMi41NiAzNDguMjUgMzMyLjU2IDM1My4xOCAzMzIuNTYgNDQ4LjM1IDMzMi41NiA0NTMuMjggMzM3LjQ5IDQ1My4yOCAzOTkgNDUzLjI4IDQwMy45MyA0NTMuMjggNDAzLjkzIDQ0OC4zNSA0MDMuOTMgNDEzLjAxIDQ3OS45MyA0MTMuMDEgNDc5LjkzIDY2My43NyA0NDQuNTUgNjYzLjc3IDQzOS42NSA2NjMuNzcgNDM5LjY1IDY2OC43IDQzOS42NSA3MzAuMjEgNDM5LjY1IDczNS4xNSA0NDQuNTUgNzM1LjE1IDU4Ni42IDczNS4xNSA1OTEuNTQgNzM1LjE1IDU5MS41NCA3MzAuMjEgNTkxLjU0IDY2OC43IDU5MS41NCA2NjMuNzcgNTg2LjYgNjYzLjc3IDU1MS4zIDY2My43NyA1NTEuMyA0MTMuMDEgNjI2Ljg0IDQxMy4wMSA2MjYuODQgNDQ3Ljg5IDYyNi44NCA0NTIuODMgNjMxLjc3IDQ1Mi44MyA2OTMuNyA0NTIuODMgNjk4LjY0IDQ1Mi44MyA2OTguNjQgNDQ3Ljg5IDY5OC42NCAzNTMuMTggNjk4LjY0IDM0OC4yNSA2OTMuNyAzNDguMjUiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iNTYxLjgzIDY5My4wNiA1NzYuODggNjc3LjU2IDU3Ni44OCA3MjAuMDMgNTYxLjgzIDcwNS42NSA1NjEuODMgNjkzLjA2Ii8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0yIiBwb2ludHM9IjUzNi43OCA2NzguNjggNTIxLjcgNjkzLjUxIDUyMS43IDM4My40NSA1MzYuNzggMzk4LjQ2IDUzNi43OCA2NzguNjgiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iMzYyLjcyIDM3Ny45OSAzNDcuMjUgMzYyLjk0IDY3Ni40NSAzNjIuOTQgNjU3IDM3Ny45OSAzNjIuNzIgMzc3Ljk5Ii8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0yIiBwb2ludHM9IjY4NC40MyA0MzkuMDQgNjY5LjM5IDQyNC42NiA2NjkuMzkgMzg2LjM4IDY4NC40MyAzNzAuOTIgNjg0LjQzIDQzOS4wNCIvPgogIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTg1My40Niw4NDQuOGMwLTYuOTgsNS42NS0xMi42MywxMi42My0xMi42M3MxMi42Myw1LjY1LDEyLjYzLDEyLjYzLTUuNjUsMTIuNjMtMTIuNjMsMTIuNjMtMTIuNjMtNS42NS0xMi42My0xMi42M2gwWk04NzUuNjQsODQ0LjhjLS4zNS01LjI2LTQuOS05LjI1LTEwLjE2LTguOS01LjI2LjM1LTkuMjUsNC45LTguOSwxMC4xNi4zMyw1LjAxLDQuNDksOC45MSw5LjUxLDguOTIsNS4zNS0uMDcsOS42My00LjQ3LDkuNTYtOS44MiwwLS4xMiwwLS4yNC0uMDEtLjM2Wk04NjEuMjMsODM3LjU5aDUuMzJjMy41LDAsNS4yOCwxLjE5LDUuMjgsNC4yLjIsMS45Mi0xLjIsMy42NC0zLjEyLDMuODQtLjIxLjAyLS40Mi4wMi0uNjIsMGwzLjg1LDYuMjZoLTIuNzNsLTMuNzQtNi4yM2gtMS42MXY2LjEyaC0yLjY2bC4wNC0xNC4yMVpNODYzLjg4LDg0My43MWgyLjM0YzEuNTcsMCwyLjk0LS4yMSwyLjk0LTIuMTNzLTEuNTQtMS45Ni0yLjktMS45NmgtMi4zOHY0LjA5WiIvPgo8L3N2Zz4=' 
             style='width: 40px; height: 40px;' />
        <div class="sidebar-brand-title">Mays Analytics</div>
        <div class="sidebar-brand-subtitle">Flex Online Programs</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Section
    
    if st.button("Home Dashboard", key="sidebar_nav_home", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Home' else "secondary"):
        st.session_state.current_page = 'Home'
        st.rerun()
    
    if st.button("Executive Dive", key="sidebar_nav_executive", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Executive_Deep_Dive' else "secondary"):
        st.session_state.current_page = 'Executive_Deep_Dive'
        st.rerun()
    
    if st.button("Comparison Tool", key="sidebar_nav_comparison", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Comparison_Tool' else "secondary"):
        st.session_state.current_page = 'Comparison_Tool'
        st.rerun()
    
    if st.button("Marketing Analysis", key="sidebar_nav_marketing", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Marketing_Analysis' else "secondary"):
        st.session_state.current_page = 'Marketing_Analysis'
        st.rerun()
    
    if st.button("Data Explorer", key="sidebar_nav_database", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Database' else "secondary"):
        st.session_state.current_page = 'Database'
        st.rerun()
    
    if st.button("Predictive Analytics", key="sidebar_nav_predictive", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Predictive_Analytics' else "secondary"):
        st.session_state.current_page = 'Predictive_Analytics'
        st.rerun()
    
    st.markdown('<div style="margin: 15px 0; border-top: 1px solid #e0e0e0;"></div>', unsafe_allow_html=True)
    
    if st.button("Documentation", key="sidebar_nav_help", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Help' else "secondary"):
        st.session_state.current_page = 'Help'
        st.rerun()
    
    # Footer with version
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 10px; margin-top: 30px; border-top: 1px solid #e0e0e0; font-size: 10px; color: #999;">
        <div>{VERSION_FULL}</div>
    </div>
    """, unsafe_allow_html=True)

# Display current page indicator
current_page_info = {
    'Home': {'icon': '🏠', 'title': 'Home Dashboard'},
    'Executive_Deep_Dive': {'icon': '📊', 'title': 'Executive Dive'},
    'Comparison_Tool': {'icon': '🔄', 'title': 'Comparison Tool'},
    'Marketing_Analysis': {'icon': '📢', 'title': 'Marketing Analysis'},
    'Database': {'icon': '🗄️', 'title': 'Data Explorer'},
    'Predictive_Analytics': {'icon': '🔮', 'title': 'Predictive Analytics'},
    'Help': {'icon': '📖', 'title': 'Documentation'}
}

current_info = current_page_info[st.session_state.current_page]
st.markdown(f"""
<div style="text-align: center; padding: 8px; background: #f8f9fa; border-radius: 8px; margin-bottom: 15px;">
    <h2 style="margin: 0; color: #500000; font-size: 24px;">{current_info['title']}</h2>
</div>
""", unsafe_allow_html=True)

# Page Content Based on Navigation
if st.session_state.current_page == 'Home':
    # HOME PAGE CONTENT
    from modules import home_dashboard
    home_dashboard.render()

elif st.session_state.current_page == 'Executive_Deep_Dive':
    # EXECUTIVE DEEP DIVE PAGE
    from modules import executive_deep_dive
    executive_deep_dive.render()

elif st.session_state.current_page == 'Comparison_Tool':
    # COMPARISON TOOL PAGE
    from modules import comparison_tool
    comparison_tool.render()

elif st.session_state.current_page == 'Marketing_Analysis':
    # MARKETING ANALYSIS PAGE
    from modules import marketing_analysis
    marketing_analysis.render()

elif st.session_state.current_page == 'Database':
    # DATA EXPLORER PAGE
    from modules import database
    database.render()

elif st.session_state.current_page == 'Predictive_Analytics':
    # PREDICTIVE ANALYTICS PAGE
    from modules import predictive_analytics
    predictive_analytics.render()

elif st.session_state.current_page == 'Help':
    # HELP & DOCUMENTATION PAGE
    from modules import help as help_page
    help_page.render()
