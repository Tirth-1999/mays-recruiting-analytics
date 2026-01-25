"""
Mays Online Flex Recruiting Analytics Platform
Single-Page Application with Navigation
"""
import streamlit as st
import streamlit.components.v1 as components
from version import VERSION_FULL
from utils import auth

# Page config
st.set_page_config(
    page_title="Mays Online Flex Recruiting Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize authentication session state
auth.init_session_state()

# Handle OAuth callback
if 'code' in st.query_params and not st.session_state.get('auth_processed', False):
    st.session_state.auth_processed = True
    code = st.query_params['code']
    state = st.query_params.get('state', '')
    
    # Note: State validation is tricky in Streamlit Cloud due to session persistence
    # We'll validate if state exists, but won't block if it's missing
    stored_state = st.session_state.get('oauth_state', '')
    if stored_state and state != stored_state:
        st.error("⚠️ Security error: Invalid state parameter. Please try signing in again.")
        st.query_params.clear()
        st.session_state.auth_processed = False
        if 'oauth_state' in st.session_state:
            del st.session_state.oauth_state
        st.stop()
    
    # Get the redirect URI from auth module (matches production or localhost)
    try:
        from utils.auth import GOOGLE_REDIRECT_URI
        full_url = f"{GOOGLE_REDIRECT_URI}?code={code}&state={state}"
    except:
        # Fallback to localhost for development
        full_url = f"http://localhost:8501/?code={code}&state={state}"
    
    try:
        user_info = auth.handle_oauth_callback(full_url)
        if user_info:
            if auth.login_user(user_info):
                st.success(f"✅ Welcome, {user_info['name']}!")
                st.query_params.clear()
                st.session_state.auth_processed = False
                if 'oauth_state' in st.session_state:
                    del st.session_state.oauth_state
                st.rerun()
            else:
                st.error("❌ Failed to create user account. Please contact support.")
                st.query_params.clear()
                st.session_state.auth_processed = False
        else:
            st.error("❌ Authentication failed. Please try again.")
            st.query_params.clear()
            st.session_state.auth_processed = False
    except Exception as e:
        st.error(f"❌ Authentication error: {str(e)}")
        st.query_params.clear()
        st.session_state.auth_processed = False
elif 'code' not in st.query_params:
    st.session_state.auth_processed = False

# Handle logout via query param
if 'logout' in st.query_params:
    auth.logout_user()
    st.query_params.clear()
    st.rerun()
    st.query_params.clear()
    st.rerun()

# Global CSS
st.markdown("""
<style>
    /* Main content styling */
    .main .block-container {
        padding-left: 1rem !important; 
        padding-right: 1rem !important;
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
        padding-bottom: 1rem !important;
        border-bottom: none !important;
    }
    div[data-testid="stAppViewContainer"] > .main {
        padding-top: 0rem !important;
    }
    .stApp > header {
        display: none !important;
    }
    section.main {
        scroll-behavior: auto !important;
    }
    
    /* Sidebar overlay - never shrink content */
    [data-testid="stSidebar"][aria-expanded="true"] {
        position: fixed !important;
        z-index: 999999 !important;
        left: 0 !important;
        top: 0 !important;
        height: 100vh !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.3) !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        display: none !important;
    }
    .main .block-container {
        max-width: 100% !important;
        transition: none !important;
    }
    .main {
        margin-left: 0 !important;
        transition: none !important;
    }
    
    /* Remove all top padding from sidebar */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    [data-testid="stSidebarContent"] {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    
    /* Remove default gaps between sidebar elements - AGGRESSIVE */
    [data-testid="stSidebar"] .element-container {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    [data-testid="stSidebar"] .stMarkdown {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    [data-testid="stSidebar"] > div > div {
        gap: 0px !important;
    }
    [data-testid="stSidebar"] .stMarkdown > div {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
    }
    /* Force remove all vertical spacing in sidebar */
    [data-testid="stSidebar"] * {
        margin-block-start: 0px !important;
        margin-block-end: 0px !important;
    }
    
    /* Sidebar brand/header */
    .sidebar-brand {
        text-align: center;
        padding: 8px 10px 6px 10px;
        margin-top: 0px;
        margin-bottom: 0px;
        border-bottom: 2px solid #C5A572;
    }
    .sidebar-logo {
        width: 32px;
        height: 32px;
    }
    .sidebar-brand-title {
        color: #500000;
        font-size: 13px;
        font-weight: bold;
        margin: 4px 0 2px 0;
    }
    .sidebar-brand-subtitle {
        color: #666;
        font-size: 10px;
        margin: 0;
    }
    
    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        text-align: left !important;
        padding: 6px 12px !important;
        margin: 0px 0 !important;
        border-radius: 6px !important;
        border: none !important;
        background: white !important;
        color: #495057 !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #f0f2f6 !important;
        color: #500000 !important;
        transform: translateX(3px) !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #500000 0%, #700000 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(80, 0, 0, 0.2) !important;
    }
    
    /* Responsive spacing - Desktop (>900px height) */
    @media (min-height: 900px) {
        .sidebar-brand { padding: 12px 10px 12px 10px; margin-bottom: 0px; }
        .sidebar-logo { width: 40px !important; height: 40px !important; }
        .sidebar-brand-title { font-size: 15px !important; margin: 6px 0 2px 0 !important; }
        .sidebar-brand-subtitle { font-size: 11px !important; }
        [data-testid="stSidebar"] .stButton > button { padding: 8px 15px !important; margin: 0px 0 !important; font-size: 14px !important; }
        .sidebar-divider { margin: 12px 0 !important; }
        .sidebar-profile-card { padding: 15px !important; margin-top: 10px !important; margin-bottom: 12px !important; }
        .sidebar-profile-img { width: 50px !important; height: 50px !important; }
        .sidebar-profile-name { font-size: 14px !important; }
        .sidebar-profile-email { font-size: 11px !important; }
        .sidebar-logout-btn { padding: 9px 12px !important; font-size: 11px !important; }
        .sidebar-footer { padding: 12px 10px !important; margin-top: 12px !important; font-size: 10px !important; }
    }
    
    /* Responsive spacing - Laptop (700-900px height) */
    @media (min-height: 700px) and (max-height: 899px) {
        .sidebar-brand { padding: 8px 10px 6px 10px; margin-bottom: 0px; }
        .sidebar-logo { width: 34px !important; height: 34px !important; }
        .sidebar-brand-title { font-size: 13px !important; margin: 4px 0 2px 0 !important; }
        .sidebar-brand-subtitle { font-size: 10px !important; }
        [data-testid="stSidebar"] .stButton > button { padding: 6px 12px !important; margin: 0px 0 !important; font-size: 13px !important; }
        .sidebar-divider { margin: 10px 0 !important; }
        .sidebar-profile-card { padding: 10px !important; margin-top: 10px !important; margin-bottom: 10px !important; }
        .sidebar-profile-img { width: 36px !important; height: 36px !important; }
        .sidebar-profile-name { font-size: 12px !important; }
        .sidebar-profile-email { font-size: 9px !important; }
        .sidebar-logout-btn { padding: 7px 10px !important; font-size: 10px !important; }
        .sidebar-footer { padding: 10px 10px !important; margin-top: 10px !important; font-size: 9px !important; }
    }
    
    /* Responsive spacing - Tablet (<700px height) */
    @media (max-height: 699px) {
        .sidebar-brand { padding: 6px 10px 6px 10px; margin-bottom: 0px; }
        .sidebar-logo { width: 28px !important; height: 28px !important; }
        .sidebar-brand-title { font-size: 11px !important; margin: 3px 0 1px 0 !important; }
        .sidebar-brand-subtitle { font-size: 9px !important; }
        [data-testid="stSidebar"] .stButton > button { padding: 5px 10px !important; margin: 0px 0 !important; font-size: 12px !important; }
        .sidebar-divider { margin: 8px 0 !important; }
        .sidebar-profile-card { padding: 8px !important; margin-top: 10px !important; margin-bottom: 8px !important; }
        .sidebar-profile-img { width: 30px !important; height: 30px !important; }
        .sidebar-profile-name { font-size: 11px !important; }
        .sidebar-profile-email { font-size: 8px !important; }
        .sidebar-logout-btn { padding: 6px 8px !important; font-size: 9px !important; }
        .sidebar-footer { padding: 8px 5px !important; margin-top: 8px !important; font-size: 8px !important; }
    }

    /* Navigation and content styling */
    .nav-button { display: inline-block; padding: 10px 20px; margin: 0 5px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; border: 2px solid transparent; }
    .nav-button.active { background: #500000; color: white !important; border-color: #500000; }
    .nav-button.inactive { background: white; color: #500000; border-color: #e9ecef; }
    .nav-button.inactive:hover { background: #e9ecef; border-color: #500000; }
    .metric-card { background: white; padding: 1.5rem; border-radius: 12px; border: 1px solid #e0e0e0; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1rem; text-align: center; }
    .insight-card { background: linear-gradient(135deg, #500000 0%, #700000 100%); color: white; padding: 1.5rem; border-radius: 12px; margin: 1rem 0; }
    .section-divider { height: 3px; background: linear-gradient(90deg, #500000, #B00000); border: none; border-radius: 2px; margin: 2rem 0; }
    .performance-indicator { padding: 1rem; border-radius: 8px; text-align: center; font-weight: 600; }
    .data-insight { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 1.5rem; border-radius: 8px; border-left: 4px solid #500000; margin: 1rem 0; }
    .metric-highlight { background: #500000; color: white; padding: 0.5rem 1rem; border-radius: 6px; display: inline-block; font-weight: bold; margin: 0.25rem; }
    .indicator-excellent { background: #d4edda; color: #155724; }
    .indicator-good { background: #fff3cd; color: #856404; }
    .indicator-needs-attention { background: #f8d7da; color: #721c24; }
    
    @media (max-width: 768px) {
        .footer-content { text-align: center !important; }
    }
</style>
""", unsafe_allow_html=True)

# Page top anchor - MUST be at the very top
st.markdown('<div id="page-top"></div>', unsafe_allow_html=True)

# Professional Banner
st.markdown("""
<div style='background: linear-gradient(135deg, #500000 0%, #700000 50%, #500000 100%); 
            padding: 1.5rem 2rem; border-radius: 10px; text-align: center;
            border: 3px solid #C5A572; margin-bottom: 1rem;'>
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

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

# Sidebar Navigation
with st.sidebar:
    # Compact Header with Logo
    st.markdown("""
    <div class="sidebar-brand">
        <img src='data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyBpZD0iTGF5ZXJfMSIgZGF0YS1uYW1lPSJMYXllciAxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDgwIDEwODAiPgogIDxkZWZzPgogICAgPHN0eWxlPgogICAgICAuY2xzLTEgewogICAgICAgIGZpbGw6ICM1MDAwMDA7CiAgICAgIH0KCiAgICAgIC5jbHMtMSwgLmNscy0yLCAuY2xzLTMgewogICAgICAgIHN0cm9rZS13aWR0aDogMHB4OwogICAgICB9CgogICAgICAuY2xzLTIgewogICAgICAgIGZpbGw6ICNiMWIzYjY7CiAgICAgIH0KCiAgICAgIC5jbHMtMyB7CiAgICAgICAgZmlsbDogI2ZmZjsKICAgICAgfQogICAgPC9zdHlsZT4KICA8L2RlZnM+CiAgPHJlY3QgY2xhc3M9ImNscy0xIiB4PSIyMDEuMjgiIHk9IjIyMi41NyIgd2lkdGg9IjYyOS43OSIgaGVpZ2h0PSI2MzQuNzkiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTMiIHBvaW50cz0iNzQ3LjQ0IDQ3NS4yMiA3MDAuNjcgNDc1LjIyIDY5Ny45NyA0NzUuMjIgNjk2Ljc1IDQ3Ny42NyA2NjIuODQgNTQ4LjI3IDYyOC44IDQ3Ny42MyA2MjcuNjEgNDc1LjIyIDYyNC45MiA0NzUuMjIgNTc5LjcxIDQ3NS4yMiA1NzUuNDQgNDc1LjIyIDU3NS40NCA0NzkuNTIgNTc1LjQ0IDUwMy41OSA1NzUuNDQgNTA3LjkgNTc5LjcxIDUwNy45IDU4Ny40NCA1MDcuOSA1ODcuNDQgNjA5LjAxIDU3OS4wOCA2MDkuMDEgNTc0Ljc4IDYwOS4wMSA1NzQuNzggNjEzLjMyIDU3NC43OCA2MzcuMzkgNTc0Ljc4IDY0MS42OSA1NzkuMDggNjQxLjY5IDYyOS44NSA2NDEuNjkgNjM0LjE1IDY0MS42OSA2MzQuMTUgNjM3LjM5IDYzNC4xNSA2MTMuMzIgNjM0LjE1IDYwOS4wMSA2MjkuODUgNjA5LjAxIDYyMS4wNyA2MDkuMDEgNjIxLjA3IDUzNy4yNSA2NTguOTkgNjE1LjQ1IDY2Mi44NCA2MjMuNDMgNjY2Ljc2IDYxNS40NSA3MDUuMDcgNTM3LjA4IDcwNS4wNyA2MDkuMDEgNjk2LjcxIDYwOS4wMSA2OTIuMzcgNjA5LjAxIDY5Mi4zNyA2MTMuMzIgNjkyLjM3IDYzNy4zOSA2OTIuMzcgNjQxLjY5IDY5Ni43MSA2NDEuNjkgNzQ3LjQ0IDY0MS42OSA3NTEuNzUgNjQxLjY5IDc1MS43NSA2MzcuMzkgNzUxLjc1IDYxMy4zMiA3NTEuNzUgNjA5LjAxIDc0Ny40NCA2MDkuMDEgNzM4LjcgNjA5LjAxIDczOC43IDUwNy45IDc0Ny40NCA1MDcuOSA3NTEuNzUgNTA3LjkgNzUxLjc1IDUwMy41OSA3NTEuNzUgNDc5LjUyIDc1MS43NSA0NzUuMjIgNzQ3LjQ0IDQ3NS4yMiIvPgogIDxwYXRoIGNsYXNzPSJjbHMtMyIgZD0iTTQ1Mi42LDYwOC45MWgtMTMuNTFsLTQzLjk1LTEwMS40N2g4LjQ3di0zMi44MmgtNzAuNTR2MzIuNzFoOS43M2wtNDMuOTEsMTAxLjQ3aC0xOC4zdjMyLjcxaDY0LjAzdi0zMi43MWgtOS4zMWw3LjMxLTE2LjloNTIuODNsNy4yOCwxNi45aC05LjgzdjMyLjcxaDY0LjA2di0zMi43MWwtNC4zNy4xMVpNMzgxLjI5LDU1OS4zM2gtMjQuNDlsMTIuMjUtMjguMzgsMTIuMjUsMjguMzhaIi8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0zIiBwb2ludHM9IjY5My43IDM0OC4yNSAzMzcuNDkgMzQ4LjI1IDMzMi41NiAzNDguMjUgMzMyLjU2IDM1My4xOCAzMzIuNTYgNDQ4LjM1IDMzMi41NiA0NTMuMjggMzM3LjQ5IDQ1My4yOCAzOTkgNDUzLjI4IDQwMy45MyA0NTMuMjggNDAzLjkzIDQ0OC4zNSA0MDMuOTMgNDEzLjAxIDQ3OS45MyA0MTMuMDEgNDc5LjkzIDY2My43NyA0NDQuNTUgNjYzLjc3IDQzOS42NSA2NjMuNzcgNDM5LjY1IDY2OC43IDQzOS42NSA3MzAuMjEgNDM5LjY1IDczNS4xNSA0NDQuNTUgNzM1LjE1IDU4Ni42IDczNS4xNSA1OTEuNTQgNzM1LjE1IDU5MS41NCA3MzAuMjEgNTkxLjU0IDY2OC43IDU5MS41NCA2NjMuNzcgNTg2LjYgNjYzLjc3IDU1MS4zIDY2My43NyA1NTEuMyA0MTMuMDEgNjI2Ljg0IDQxMy4wMSA2MjYuODQgNDQ3Ljg5IDYyNi44NCA0NTIuODMgNjMxLjc3IDQ1Mi44MyA2OTMuNyA0NTIuODMgNjk4LjY0IDQ1Mi44MyA2OTguNjQgNDQ3Ljg5IDY5OC42NCAzNTMuMTggNjk4LjY0IDM0OC4yNSA2OTMuNyAzNDguMjUiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iNTYxLjgzIDY5My4wNiA1NzYuODggNjc3LjU2IDU3Ni44OCA3MjAuMDMgNTYxLjgzIDcwNS42NSA1NjEuODMgNjkzLjA2Ii8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0yIiBwb2ludHM9IjUzNi43OCA2NzguNjggNTIxLjcgNjkzLjUxIDUyMS43IDM4My40NSA1MzYuNzggMzk4LjQ2IDUzNi43OCA2NzguNjgiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iMzYyLjcyIDM3Ny45OSAzNDcuMjUgMzYyLjk0IDY3Ni40NSAzNjIuOTQgNjU3IDM3Ny45OSAzNjIuNzIgMzc3Ljk5Ii8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0yIiBwb2ludHM9IjY4NC40MyA0MzkuMDQgNjY5LjM5IDQyNC42NiA2NjkuMzkgMzg2LjM4IDY4NC40MyAzNzAuOTIgNjg0LjQzIDQzOS4wNCIvPgogIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTg1My40Niw4NDQuOGMwLTYuOTgsNS42NS0xMi42MywxMi42My0xMi42M3MxMi42Myw1LjY1LDEyLjYzLDEyLjYzLTUuNjUsMTIuNjMtMTIuNjMsMTIuNjMtMTIuNjMtNS42NS0xMi42My0xMi42M2gwWk04NzUuNjQsODQ0LjhjLS4zNS01LjI2LTQuOS05LjI1LTEwLjE2LTguOS01LjI2LjM1LTkuMjUsNC45LTguOSwxMC4xNi4zMyw1LjAxLDQuNDksOC45MSw5LjUxLDguOTIsNS4zNS0uMDcsOS42My00LjQ3LDkuNTYtOS44MiwwLS4xMiwwLS4yNC0uMDEtLjM2Wk04NjEuMjMsODM3LjU5aDUuMzJjMy41LDAsNS4yOCwxLjE5LDUuMjgsNC4yLjIsMS45Mi0xLjIsMy42NC0zLjEyLDMuODQtLjIxLjAyLS40Mi4wMi0uNjIsMGwzLjg1LDYuMjZoLTIuNzNsLTMuNzQtNi4yM2gtMS42MXY2LjEyaC0yLjY2bC4wNC0xNC4yMVpNODYzLjg4LDg0My43MWgyLjM0YzEuNTcsMCwyLjk0LS4yMSwyLjk0LTIuMTNzLTEuNTQtMS45Ni0yLjktMS45NmgtMi4zOHY0LjA5WiIvPgo8L3N2Zz4=' 
             class="sidebar-logo" />
        <div class="sidebar-brand-title">Mays Analytics</div>
        <div class="sidebar-brand-subtitle">Flex Online Programs</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Consolidated Profile Section with inline logout
    if auth.is_authenticated():
        user = auth.get_current_user()
        user_role = auth.get_user_role()
        
        # Smaller, subtle role text
        role_text = user_role.capitalize() if user_role else 'User'
        
        st.markdown(f"""
        <div class="sidebar-profile-card" style="background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 10px; margin-top: 10px; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <img src="{user.get('profile_picture', '')}" 
                     class="sidebar-profile-img"
                     style="width: 36px; height: 36px; border-radius: 50%; border: 2px solid #C5A572;" 
                     onerror="this.style.display='none'"/>
                <div style="flex: 1; min-width: 0;">
                    <div class="sidebar-profile-name" style="font-weight: 600; font-size: 12px; color: #212529; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        {user['name']}
                    </div>
                    <div class="sidebar-profile-email" style="font-size: 9px; color: #6c757d; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-bottom: 2px;">
                        {user['email']}
                    </div>
                    <div style="font-size: 9px; color: #999; font-style: italic;">
                        {role_text}
                    </div>
                </div>
            </div>
            <a href="?logout=true" style="text-decoration: none; display: block;">
                <button class="sidebar-logout-btn" style="width: 100%; background: #f8f9fa; border: 1px solid #e0e0e0; color: #495057; padding: 8px 12px; border-radius: 4px; font-size: 11px; font-weight: 500; cursor: pointer;">
                    Logout
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Use link_button for OAuth - more reliable than JavaScript redirects
        try:
            auth_url = auth.get_authorization_url()
            st.link_button("🔐 Sign in with Google", auth_url, use_container_width=True, type="primary")
        except Exception as e:
            st.error(f"❌ Error generating login URL: {str(e)}")
    
    # Gold divider
    st.markdown('<div style="border-top: 2px solid #C5A572;"></div>', unsafe_allow_html=True)
    
    # Navigation - 6 main pages
    if st.button("Home Dashboard", key="nav_home", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Home' else "secondary"):
        st.session_state.current_page = 'Home'
        st.rerun()
    
    if st.button("Executive Dive", key="nav_executive", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Executive_Deep_Dive' else "secondary"):
        st.session_state.current_page = 'Executive_Deep_Dive'
        st.rerun()
    
    if st.button("Comparison Tool", key="nav_comparison", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Comparison_Tool' else "secondary"):
        st.session_state.current_page = 'Comparison_Tool'
        st.rerun()
    
    if st.button("Marketing Analysis", key="nav_marketing", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Marketing_Analysis' else "secondary"):
        st.session_state.current_page = 'Marketing_Analysis'
        st.rerun()
    
    if st.button("Predictive Analytics", key="nav_predictive", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Predictive_Analytics' else "secondary"):
        st.session_state.current_page = 'Predictive_Analytics'
        st.rerun()
    
    if st.button("Data Explorer", key="nav_database", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Database' else "secondary"):
        st.session_state.current_page = 'Database'
        st.rerun()
    
    # Gold divider
    st.markdown('<div style="border-top: 2px solid #C5A572;"></div>', unsafe_allow_html=True)
    
    # Documentation & Help
    if st.button("Documentation & Help", key="nav_help", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Help' else "secondary"):
        st.session_state.current_page = 'Help'
        st.rerun()
    
    # Footer with version
    st.markdown(f"""
    <div style="text-align: center; padding: 8px 5px; border-top: 2px solid #C5A572; font-size: 9px; color: #999;">
        {VERSION_FULL}
    </div>
    """, unsafe_allow_html=True)

# Current page indicator
current_page_info = {
    'Home': {'title': 'Home Dashboard'},
    'Executive_Deep_Dive': {'title': 'Executive Dive'},
    'Comparison_Tool': {'title': 'Comparison Tool'},
    'Marketing_Analysis': {'title': 'Marketing Analysis'},
    'Database': {'title': 'Data Explorer'},
    'Predictive_Analytics': {'title': 'Predictive Analytics'},
    'Help': {'title': 'Documentation & Help'}
}

current_info = current_page_info[st.session_state.current_page]

st.markdown(f"""
<div style="text-align: center; padding: 8px; background: #f8f9fa; border-radius: 8px; margin-bottom: 15px;">
    <h2 style="margin: 0; color: #500000; font-size: 24px;">{current_info['title']}</h2>
</div>
""", unsafe_allow_html=True)

# Page Content Routing
if st.session_state.current_page == 'Home':
    from modules import home_dashboard
    home_dashboard.render()

elif st.session_state.current_page == 'Executive_Deep_Dive':
    from modules import executive_deep_dive
    executive_deep_dive.render()

elif st.session_state.current_page == 'Comparison_Tool':
    from modules import comparison_tool
    comparison_tool.render()

elif st.session_state.current_page == 'Marketing_Analysis':
    from modules import marketing_analysis
    marketing_analysis.render()

elif st.session_state.current_page == 'Database':
    from modules import database
    database.render()

elif st.session_state.current_page == 'Predictive_Analytics':
    from modules import predictive_analytics
    predictive_analytics.render()

elif st.session_state.current_page == 'Help':
    from modules import help as help_page
    help_page.render()

# Footer
st.markdown("<hr style='margin-top: 3rem; margin-bottom: 1rem; border: none; border-top: 2px solid #e0e0e0;'>", unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align: center; padding: 1rem; color: #666; font-size: 0.9rem;'>
    <p style='margin: 0.5rem 0;'>
        <strong>Mays Business School</strong> | Texas A&M University<br>
        Flex Online Programs Analytics Platform
    </p>
    <p style='margin: 0.5rem 0; font-size: 0.8rem; color: #999;'>
        {VERSION_FULL} | © 2026 Texas A&M University
    </p>
</div>
""", unsafe_allow_html=True)

# Back to Top Button with smooth scroll
st.markdown("""
<style>
    /* Back to Top Button - Chevron Style with Circular Border */
    .back-to-top {
        position: fixed;
        bottom: 30px;
        right: 30px;
        background: linear-gradient(135deg, #500000 0%, #700000 100%);
        color: white !important;
        width: 56px;
        height: 56px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 6px 18px rgba(80, 0, 0, 0.22);
        z-index: 999999;
        transition: all 0.4s ease;
        text-decoration: none;
        border: 1.5px solid rgba(255, 255, 255, 0.15);
        font-size: 26px;
        font-weight: bold;
    }
    
    .back-to-top:hover {
        background: linear-gradient(135deg, #700000 0%, #900000 100%);
        box-shadow: 0 8px 24px rgba(80, 0, 0, 0.3);
        transform: translateY(-3px) scale(1.03);
        border-color: rgba(255, 255, 255, 0.25);
        color: white !important;
    }
    
    .back-to-top:active {
        transform: translateY(-1px) scale(1.01);
        box-shadow: 0 4px 12px rgba(80, 0, 0, 0.25);
    }
    
    .back-to-top-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        color: white !important;
        line-height: 1;
        width: 100%;
        height: 100%;
    }
    
    /* Smooth and slow scroll behavior */
    html {
        scroll-behavior: smooth;
    }
    
    section.main {
        scroll-behavior: smooth !important;
    }
    
    /* Make scroll animation slower with CSS */
    @media (prefers-reduced-motion: no-preference) {
        * {
            scroll-behavior: smooth;
        }
    }
    
    /* Slow down the scroll with transition */
    section.main {
        scroll-padding-top: 0;
    }
    
    /* Mobile responsive */
    @media screen and (max-width: 768px) {
        .back-to-top {
            width: 50px;
            height: 50px;
            bottom: 20px;
            right: 20px;
            font-size: 22px;
        }
    }
</style>

<a href="#page-top" class="back-to-top" onclick="smoothScrollToTop(event)" title="Back to Top">
    <div class="back-to-top-icon">▲</div>
</a>
""", unsafe_allow_html=True)

# Smooth scroll JavaScript
components.html("""
<script>
function smoothScrollToTop(e) {
    if (e) e.preventDefault();
    
    const mainContent = window.parent.document.querySelector('section.main');
    if (!mainContent) return;
    
    const startPosition = mainContent.scrollTop;
    const duration = 2500; // 2.5 seconds
    const startTime = performance.now();
    
    function easeInOutQuad(t) {
        return t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    }
    
    function animateScroll(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easeProgress = easeInOutQuad(progress);
        
        mainContent.scrollTop = startPosition * (1 - easeProgress);
        
        if (progress < 1) {
            requestAnimationFrame(animateScroll);
        }
    }
    
    requestAnimationFrame(animateScroll);
}

// Make function globally available
window.parent.smoothScrollToTop = smoothScrollToTop;
</script>
""", height=0)

# Scroll to top on page load
st.markdown("""
<script>
    // Scroll to top on page load
    window.addEventListener('load', function() {
        setTimeout(function() {
            var mainContent = window.parent.document.querySelector('section.main');
            if (mainContent) {
                mainContent.scrollTop = 0;
            }
        }, 50);
    });
</script>
""", unsafe_allow_html=True)
