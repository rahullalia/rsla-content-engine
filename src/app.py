"""
Content Engine - Sandcastles.ai Alternative
Find viral outliers from your watchlist and remix them.
"""
import streamlit as st
import pandas as pd
import os
import hashlib
import time
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables first
load_dotenv(Path(__file__).parent.parent / ".env")

# Page config must be first Streamlit command
# Using RSL/A brand favicon (blue square with white slash)
st.set_page_config(
    page_title="Content Engine | RSL/A",
    page_icon="https://rsla.io/favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# AUTHENTICATION - with session persistence
# ============================================
SESSION_DURATION_HOURS = 24  # Session lasts 24 hours

def get_auth_password():
    """Get auth password from secrets or env."""
    try:
        return st.secrets.get("AUTH_PASSWORD", "") or os.getenv("AUTH_PASSWORD", "")
    except Exception:
        return os.getenv("AUTH_PASSWORD", "")

def generate_session_token(password):
    """Generate a time-based session token."""
    # Token valid for SESSION_DURATION_HOURS
    time_bucket = int(time.time() // (SESSION_DURATION_HOURS * 3600))
    token_input = f"{password}:{time_bucket}"
    return hashlib.sha256(token_input.encode()).hexdigest()[:32]

def verify_session_token(token):
    """Verify if session token is valid."""
    auth_password = get_auth_password()
    if not auth_password:
        return True  # No password configured

    # Check current time bucket
    current_token = generate_session_token(auth_password)
    if token == current_token:
        return True

    # Also check previous time bucket (for sessions created near boundary)
    time_bucket_prev = int(time.time() // (SESSION_DURATION_HOURS * 3600)) - 1
    token_input_prev = f"{auth_password}:{time_bucket_prev}"
    prev_token = hashlib.sha256(token_input_prev.encode()).hexdigest()[:32]

    return token == prev_token

def check_auth():
    """Check if user is authenticated."""
    auth_password = get_auth_password()

    # No password configured - allow access
    if not auth_password:
        return True, "local"

    # Check URL token first (persists across refreshes)
    params = st.query_params
    url_token = params.get("session", "")

    if url_token and verify_session_token(url_token):
        st.session_state.authenticated = True
        return True, "authenticated"

    # Check session state
    if st.session_state.get('authenticated'):
        return True, "authenticated"

    return False, None

def show_login():
    """Show login form for password auth."""
    st.markdown("""
    <style>
        @import url('https://api.fontshare.com/v2/css?f[]=satoshi@700,900&display=swap');

        .login-wrapper {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(180deg, #0a0a0a 0%, #0d0d0d 100%);
        }
        .login-wrapper::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background:
                radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0, 112, 243, 0.2), transparent),
                radial-gradient(ellipse 60% 40% at 50% 120%, rgba(0, 112, 243, 0.15), transparent);
            pointer-events: none;
        }
        .login-card {
            max-width: 380px;
            margin: 0 auto;
            padding: 48px 40px;
            background: rgba(17, 17, 17, 0.8);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5), 0 0 100px rgba(0, 112, 243, 0.1);
            position: relative;
            z-index: 1;
        }
        .login-logo {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            margin-bottom: 32px;
        }
        .login-logo .icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #0070f3 0%, #0050c0 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 20px rgba(0, 112, 243, 0.4);
        }
        .login-logo .icon::after {
            content: '';
            width: 8px;
            height: 32px;
            background: white;
            transform: skewX(-20deg);
        }
        .login-logo .wordmark {
            font-family: 'Satoshi', sans-serif;
            font-size: 28px;
            font-weight: 900;
            letter-spacing: -0.04em;
            color: white;
        }
        .login-logo .slash {
            width: 6px;
            height: 21px;
            background: linear-gradient(180deg, #0070f3 0%, #00a0ff 100%);
            transform: skewX(-20deg);
            margin: 0 -1px 0 6px;
            display: inline-block;
            box-shadow: 0 0 15px rgba(0, 112, 243, 0.6);
        }
        .login-title {
            text-align: center;
            font-family: 'Satoshi', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: white;
            margin-bottom: 8px;
        }
        .login-subtitle {
            text-align: center;
            color: #888;
            font-size: 14px;
            margin-bottom: 32px;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="login-logo">
            <div class="icon"></div>
            <div class="wordmark">RSL<span class="slash"></span>A</div>
        </div>
        <div class="login-title">Content Engine</div>
        <div class="login-subtitle">Enter password to continue</div>
        """, unsafe_allow_html=True)

        password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Enter password...")

        if st.button("🔓 Unlock", type="primary", use_container_width=True):
            auth_password = get_auth_password()
            if password == auth_password:
                st.session_state.authenticated = True
                # Set session token in URL for persistence
                token = generate_session_token(auth_password)
                st.query_params["session"] = token
                st.rerun()
            else:
                st.error("Invalid password")

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("🔒 Secured with 24-hour session tokens")

# Check authentication
is_authed, user_email = check_auth()

if not is_authed:
    if user_email:
        st.error(f"Access denied. {user_email} is not authorized.")
        st.stop()
    else:
        show_login()
        st.stop()

# Import app modules after auth check
from scraper import YouTubeScraper, InstagramScraper, AssemblyAITranscriber
from remix_engine import Remixer
from database import (
    add_creator, remove_creator, get_all_creators, get_creator_by_id,
    upsert_videos, get_videos_for_creator, get_all_outliers, get_video_by_id,
    save_transcript, save_remix, parse_youtube_url, parse_instagram_url, parse_creator_url
)

# ============================================
# RSL/A BRAND STYLING - Enhanced UI
# ============================================
# Brand Colors: Blue #0070f3, Black #0a0a0a, White #ffffff
# Fonts: Satoshi (display), Inter (body)
st.markdown("""
<style>
    @import url('https://api.fontshare.com/v2/css?f[]=satoshi@700,900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    /* Base with subtle gradient */
    .stApp {
        background: linear-gradient(180deg, #0a0a0a 0%, #0d0d0d 50%, #0a0a0a 100%);
        background-attachment: fixed;
    }
    .block-container {
        padding-top: 2rem;
    }

    /* Animated gradient background effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background:
            radial-gradient(ellipse 80% 50% at 20% -20%, rgba(0, 112, 243, 0.15), transparent),
            radial-gradient(ellipse 60% 40% at 80% 100%, rgba(0, 112, 243, 0.1), transparent);
        pointer-events: none;
        z-index: 0;
    }

    /* Typography */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Satoshi', system-ui, sans-serif !important;
        font-weight: 700 !important;
    }
    h1 {
        font-size: 2.5rem !important;
        letter-spacing: -0.02em !important;
        background: linear-gradient(135deg, #ffffff 0%, #0070f3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    /* Body text - avoid overriding span to preserve icon fonts */
    p, label, .stMarkdown > div {
        font-family: 'Inter', system-ui, sans-serif;
    }

    /* Brand accent color - Primary buttons with glow */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0070f3 0%, #0050c0 100%) !important;
        border: none !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(0, 112, 243, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 112, 243, 0.5) !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: rgba(17, 17, 17, 0.8) !important;
        border: 1px solid #333 !important;
        color: #999 !important;
        backdrop-filter: blur(10px) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #0070f3 !important;
        color: #fff !important;
        box-shadow: 0 0 20px rgba(0, 112, 243, 0.2) !important;
    }

    /* Outlier score colors with glow */
    .outlier-high {
        color: #0070f3 !important;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 112, 243, 0.5);
    }
    .outlier-medium {
        color: #60a5fa;
    }
    .outlier-low {
        color: #6b7280;
    }

    /* Glass Cards */
    .creator-card, .video-card {
        background: rgba(17, 17, 17, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    .creator-card:hover, .video-card:hover {
        border-color: rgba(0, 112, 243, 0.5);
        box-shadow: 0 8px 32px rgba(0, 112, 243, 0.1);
    }

    /* Metric box with brand accent and glow */
    .metric-box {
        background: rgba(17, 17, 17, 0.8);
        border: 1px solid #0070f3;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 0 30px rgba(0, 112, 243, 0.15);
    }

    /* Sidebar styling - glass effect */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(13, 13, 13, 0.95) 0%, rgba(10, 10, 10, 0.98) 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px) !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    /* Input fields with glow on focus */
    .stTextInput > div > div > input {
        background-color: rgba(17, 17, 17, 0.8) !important;
        border: 1px solid rgba(51, 51, 51, 0.8) !important;
        color: #fff !important;
        font-family: 'Inter', sans-serif !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #0070f3 !important;
        box-shadow: 0 0 0 1px #0070f3, 0 0 20px rgba(0, 112, 243, 0.3) !important;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background-color: rgba(17, 17, 17, 0.8) !important;
        border: 1px solid rgba(51, 51, 51, 0.8) !important;
        border-radius: 8px !important;
    }

    /* Expander with glass effect */
    .streamlit-expanderHeader {
        background: rgba(17, 17, 17, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px) !important;
    }

    /* Slider with glow */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #0070f3 0%, #00a0ff 100%) !important;
        box-shadow: 0 0 10px rgba(0, 112, 243, 0.5) !important;
    }

    /* Text areas with glass effect */
    .stTextArea > div > div > textarea {
        background-color: rgba(17, 17, 17, 0.8) !important;
        border: 1px solid rgba(51, 51, 51, 0.8) !important;
        color: #fff !important;
        font-family: 'Inter', sans-serif !important;
        border-radius: 8px !important;
    }
    .stTextArea > div > div > textarea:focus {
        border-color: #0070f3 !important;
        box-shadow: 0 0 20px rgba(0, 112, 243, 0.2) !important;
    }

    /* Captions */
    .stCaption {
        color: #888 !important;
    }

    /* Links with hover effect */
    a {
        color: #0070f3 !important;
        transition: all 0.2s ease !important;
    }
    a:hover {
        color: #00a0ff !important;
        text-shadow: 0 0 10px rgba(0, 112, 243, 0.5) !important;
    }

    /* Divider styling */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
        margin: 1.5rem 0 !important;
    }

    /* Image thumbnails with hover effect */
    .stImage > img {
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    .stImage > img:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3) !important;
    }

    /* Progress bar styling */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #0070f3 0%, #00a0ff 100%) !important;
        box-shadow: 0 0 15px rgba(0, 112, 243, 0.5) !important;
    }

    /* Success/Warning/Info messages */
    .stSuccess {
        background: rgba(0, 200, 83, 0.1) !important;
        border: 1px solid rgba(0, 200, 83, 0.3) !important;
        border-radius: 8px !important;
    }
    .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        border: 1px solid rgba(255, 193, 7, 0.3) !important;
        border-radius: 8px !important;
    }
    .stInfo {
        background: rgba(0, 112, 243, 0.1) !important;
        border: 1px solid rgba(0, 112, 243, 0.3) !important;
        border-radius: 8px !important;
    }

    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #0070f3 !important;
    }

    /* Video card hover effect */
    .video-row {
        padding: 16px;
        margin: 8px 0;
        background: rgba(17, 17, 17, 0.4);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    .video-row:hover {
        background: rgba(17, 17, 17, 0.8);
        border-color: rgba(0, 112, 243, 0.3);
        transform: translateX(4px);
    }

    /* RSL/A Logo in sidebar with glow */
    .rsla-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0 16px 0;
    }
    .rsla-logo .icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, #0070f3 0%, #0050c0 100%);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 4px 15px rgba(0, 112, 243, 0.4);
    }
    .rsla-logo .icon::after {
        content: '';
        width: 7px;
        height: 28px;
        background: white;
        transform: skewX(-20deg);
    }
    .rsla-logo .wordmark {
        font-family: 'Satoshi', sans-serif;
        font-size: 24px;
        font-weight: 900;
        letter-spacing: -0.04em;
        display: flex;
        align-items: center;
        color: white;
    }
    .rsla-logo .slash {
        width: 5px;
        height: 18px;
        background: linear-gradient(180deg, #0070f3 0%, #00a0ff 100%);
        transform: skewX(-20deg);
        margin: 0 -1px 0 5px;
        display: inline-block;
        box-shadow: 0 0 10px rgba(0, 112, 243, 0.5);
    }
    .tool-label {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }

    /* Stats badge */
    .stat-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(0, 112, 243, 0.15);
        border: 1px solid rgba(0, 112, 243, 0.3);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 13px;
        color: #0070f3;
        font-weight: 600;
    }

    /* Animated pulse for live indicators */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    .pulse {
        animation: pulse 2s ease-in-out infinite;
    }

    /* Gradient text utility */
    .gradient-text {
        background: linear-gradient(135deg, #0070f3 0%, #00a0ff 50%, #0070f3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE
# ============================================
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'outliers'
if 'selected_video_id' not in st.session_state:
    st.session_state.selected_video_id = None
if 'scraper' not in st.session_state:
    st.session_state.scraper = YouTubeScraper()

# Initialize Instagram scraper if API token available
def get_instagram_scraper(manual_token: str = None):
    """Get Instagram scraper instance if Apify token is available."""
    apify_token = manual_token  # Use manually passed token first

    # Try Streamlit secrets (for Streamlit Cloud)
    if not apify_token:
        try:
            apify_token = st.secrets.get("APIFY_API_TOKEN", "")
        except Exception:
            pass

    # Fall back to environment variable (for local dev)
    if not apify_token:
        apify_token = os.getenv("APIFY_API_TOKEN", "")

    # Check session state for sidebar-entered token
    if not apify_token and 'apify_token_input' in st.session_state:
        apify_token = st.session_state.apify_token_input

    if apify_token:
        try:
            return InstagramScraper(apify_token)
        except Exception as e:
            st.error(f"Failed to initialize Instagram scraper: {e}")
            return None

    return None

def get_assemblyai_transcriber():
    """Get AssemblyAI transcriber if API key available."""
    try:
        api_key = st.secrets.get("ASSEMBLYAI_API_KEY", "") or os.getenv("ASSEMBLYAI_API_KEY", "")
        if api_key:
            return AssemblyAITranscriber(api_key)
    except Exception:
        api_key = os.getenv("ASSEMBLYAI_API_KEY", "")
        if api_key:
            return AssemblyAITranscriber(api_key)
    return None

# ============================================
# SIDEBAR - API KEYS & SETTINGS
# ============================================
with st.sidebar:
    # RSL/A Logo
    st.markdown("""
    <div class="rsla-logo">
        <div class="icon"></div>
        <div>
            <div class="wordmark">RSL<span class="slash"></span>A</div>
            <div class="tool-label">Content Engine</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # API Keys
    st.subheader("🔑 API Keys")

    # Try secrets first (Streamlit Cloud), then env vars (local), then manual input
    try:
        anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", "") or os.getenv("ANTHROPIC_API_KEY", "")
    except Exception:
        anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")

    if not anthropic_key:
        anthropic_key = st.text_input(
            "Anthropic API Key",
            type="password",
            help="For remixing content"
        )

    # Apify API Token for Instagram
    try:
        apify_token = st.secrets.get("APIFY_API_TOKEN", "") or os.getenv("APIFY_API_TOKEN", "")
    except Exception:
        apify_token = os.getenv("APIFY_API_TOKEN", "")

    if not apify_token:
        apify_token = st.text_input(
            "Apify API Token",
            type="password",
            help="For Instagram scraping (~$0.003/reel)",
            key="apify_token_input"
        )
    # Store in session state for use by sync functions
    if apify_token:
        st.session_state.apify_token_input = apify_token

    # AssemblyAI API Key for transcription
    try:
        assemblyai_key = st.secrets.get("ASSEMBLYAI_API_KEY", "") or os.getenv("ASSEMBLYAI_API_KEY", "")
    except Exception:
        assemblyai_key = os.getenv("ASSEMBLYAI_API_KEY", "")

    if not assemblyai_key:
        assemblyai_key = st.text_input(
            "AssemblyAI API Key",
            type="password",
            help="For Instagram transcription (~$0.01/min)"
        )

    st.markdown("---")

    # Navigation
    st.subheader("📍 Navigation")

    if st.button("🔥 Outlier Feed", use_container_width=True, type="primary" if st.session_state.current_view == 'outliers' else "secondary"):
        st.session_state.current_view = 'outliers'
        st.rerun()

    if st.button("👥 Watchlist", use_container_width=True, type="primary" if st.session_state.current_view == 'watchlist' else "secondary"):
        st.session_state.current_view = 'watchlist'
        st.rerun()

    if st.button("✨ Remix Studio", use_container_width=True, type="primary" if st.session_state.current_view == 'remix' else "secondary"):
        st.session_state.current_view = 'remix'
        st.rerun()

    st.markdown("---")

    # Platform status with better styling - dynamic based on API keys
    ig_active = bool(apify_token)
    ig_color = "#22c55e" if ig_active else "#666"
    ig_text_color = "#ccc" if ig_active else "#888"
    ig_glow = "box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);" if ig_active else ""

    st.markdown(f"""
    <div style="margin-bottom: 16px;">
        <div style="font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Platform Status</div>
        <div style="display: flex; flex-direction: column; gap: 6px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="width: 8px; height: 8px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);"></span>
                <span style="color: #ccc; font-size: 13px;">YouTube</span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="width: 8px; height: 8px; background: {ig_color}; border-radius: 50%; {ig_glow}"></span>
                <span style="color: {ig_text_color}; font-size: 13px;">Instagram (Apify)</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Footer with link to rsla.io
    st.markdown("""
    <div style="text-align: center; padding: 8px 0;">
        <a href="https://rsla.io" target="_blank" style="
            color: #666 !important;
            text-decoration: none;
            font-size: 12px;
            transition: color 0.2s;
        ">Built by RSL/A</a>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# MAIN CONTENT
# ============================================

def sync_creator(creator_id: int, limit: int = 30):
    """Sync videos for a creator (YouTube or Instagram)."""
    creator = get_creator_by_id(creator_id)
    if not creator:
        st.error("Creator not found")
        return False

    platform = creator.get('platform', 'youtube').lower()

    with st.spinner(f"Syncing {creator['display_name']} ({platform})..."):
        if platform == 'instagram':
            # Use Instagram scraper (Apify)
            try:
                ig_scraper = get_instagram_scraper()
                if not ig_scraper:
                    st.error("❌ Apify API token required for Instagram. Add it in the sidebar or configure in Streamlit secrets.")
                    return False

                st.info(f"📡 Fetching reels from @{creator['username']}...")
                videos = ig_scraper.get_reels(creator['username'], limit=limit)

                if videos:
                    st.info(f"✅ Got {len(videos)} reels, calculating outliers...")
                    analyzed = ig_scraper.calculate_outliers(videos)
                    upsert_videos(creator_id, analyzed)
                    st.success(f"✅ Synced {len(videos)} reels from @{creator['username']}")
                    return True
                else:
                    st.warning(f"⚠️ No reels found for @{creator['username']}. Check if the username is correct.")
                    return False
            except Exception as e:
                st.error(f"❌ Instagram sync error: {str(e)}")
                return False
        else:
            # Use YouTube scraper
            try:
                scraper = st.session_state.scraper
                videos = scraper.get_channel_videos(creator['url'], limit=limit)
                if videos:
                    analyzed = scraper.calculate_outliers(videos)
                    upsert_videos(creator_id, analyzed)
                    st.success(f"✅ Synced {len(videos)} videos from {creator['display_name']}")
                    return True
                else:
                    st.warning(f"⚠️ No videos found for {creator['display_name']}")
                    return False
            except Exception as e:
                st.error(f"❌ YouTube sync error: {str(e)}")
                return False

def sync_all_creators():
    """Sync all creators in watchlist."""
    creators = get_all_creators()
    progress = st.progress(0)

    for i, creator in enumerate(creators):
        sync_creator(creator['id'])
        progress.progress((i + 1) / len(creators))

    progress.empty()
    st.success(f"Synced {len(creators)} creators!")

# ============================================
# VIEW: OUTLIER FEED
# ============================================
if st.session_state.current_view == 'outliers':
    # Header with stats
    st.markdown("""
    <h1 style="margin-bottom: 0;">🔥 Outlier Feed</h1>
    """, unsafe_allow_html=True)
    st.caption("Top performing videos across your watchlist")

    # Quick stats row
    creators = get_all_creators()
    all_vids = get_all_outliers(min_score=1.0, limit=1000)
    yt_vids = [v for v in all_vids if v.get('platform', '').lower() == 'youtube']
    ig_vids = [v for v in all_vids if v.get('platform', '').lower() == 'instagram']

    st.markdown(f"""
    <div style="display: flex; gap: 12px; margin: 16px 0 24px 0;">
        <span class="stat-badge">👥 {len(creators)} creators</span>
        <span class="stat-badge">📹 {len(all_vids)} videos</span>
        <span class="stat-badge pulse">✨ {len([v for v in all_vids if v['outlier_score'] >= 3])} hot outliers</span>
    </div>
    """, unsafe_allow_html=True)

    # Platform filter tabs
    platform_filter = st.radio(
        "Platform",
        ["All", "YouTube", "Instagram"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # Controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        min_score = st.slider("Minimum Outlier Score", 1.0, 5.0, 2.0, 0.5)
    with col2:
        limit = st.selectbox("Show", [25, 50, 100], index=0)
    with col3:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
        if st.button("🔄 Sync All", use_container_width=True):
            sync_all_creators()
            st.rerun()

    st.markdown("---")

    # Get outliers and filter by platform
    outliers = get_all_outliers(min_score=min_score, limit=limit * 2)  # Fetch more to filter

    if platform_filter == "YouTube":
        outliers = [v for v in outliers if v.get('platform', '').lower() == 'youtube'][:limit]
    elif platform_filter == "Instagram":
        outliers = [v for v in outliers if v.get('platform', '').lower() == 'instagram'][:limit]
    else:
        outliers = outliers[:limit]

    if not outliers:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 48px; margin-bottom: 16px;">🔍</div>
            <h3 style="color: #fff; margin-bottom: 8px;">No outliers found</h3>
            <p style="color: #888;">Add creators to your watchlist and sync them first!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Display as cards
        for i, video in enumerate(outliers):
            score = video['outlier_score']

            # Determine score styling
            if score >= 4:
                score_color = "#ff6b6b"
                score_glow = "0 0 20px rgba(255, 107, 107, 0.5)"
                score_label = "🔥 VIRAL"
            elif score >= 3:
                score_color = "#0070f3"
                score_glow = "0 0 15px rgba(0, 112, 243, 0.5)"
                score_label = "⚡ HOT"
            elif score >= 2:
                score_color = "#60a5fa"
                score_glow = "none"
                score_label = "📈 RISING"
            else:
                score_color = "#6b7280"
                score_glow = "none"
                score_label = ""

            col_thumb, col_info, col_actions = st.columns([1, 3, 1])

            with col_thumb:
                if video.get('thumbnail'):
                    st.image(video['thumbnail'], use_container_width=True)

            with col_info:
                st.markdown(f"**{video['title'][:80]}{'...' if len(video.get('title', '')) > 80 else ''}**")
                st.caption(f"@{video['username']} • {video['platform'].upper()}")
                st.markdown(f"""
                <div style="display: flex; align-items: center; gap: 12px; margin-top: 8px;">
                    <span style="
                        font-size: 18px;
                        font-weight: 700;
                        color: {score_color};
                        text-shadow: {score_glow};
                    ">{score}x</span>
                    <span style="color: #888;">•</span>
                    <span style="color: #ccc;">{video.get('view_count', 0):,} views</span>
                    {f'<span style="background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 4px; font-size: 11px; color: {score_color};">{score_label}</span>' if score_label else ''}
                </div>
                """, unsafe_allow_html=True)

            with col_actions:
                st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
                if st.button("✨ Remix", key=f"remix_{video['id']}", type="primary"):
                    st.session_state.selected_video_id = video['id']
                    st.session_state.current_view = 'remix'
                    st.rerun()

            if i < len(outliers) - 1:
                st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 16px 0;'>", unsafe_allow_html=True)

# ============================================
# VIEW: WATCHLIST
# ============================================
elif st.session_state.current_view == 'watchlist':
    st.markdown("""
    <h1 style="margin-bottom: 0;">👥 Watchlist</h1>
    """, unsafe_allow_html=True)
    st.caption("Creators you're tracking")

    # Stats
    creators = get_all_creators()
    total_videos = sum(c.get('video_count') or 0 for c in creators)
    st.markdown(f"""
    <div style="display: flex; gap: 12px; margin: 16px 0 24px 0;">
        <span class="stat-badge">👥 {len(creators)} creators</span>
        <span class="stat-badge">📹 {total_videos} videos tracked</span>
    </div>
    """, unsafe_allow_html=True)

    # Add Creator Form
    with st.expander("➕ Add Creator", expanded=True):
        # Platform selection
        platform_choice = st.radio(
            "Platform",
            ["YouTube", "Instagram"],
            horizontal=True,
            help="Select the platform"
        )

        if platform_choice == "YouTube":
            new_url = st.text_input(
                "YouTube Channel URL",
                placeholder="https://www.youtube.com/@creatorname"
            )
        else:
            new_url = st.text_input(
                "Instagram Profile URL",
                placeholder="https://www.instagram.com/username"
            )
            if not apify_token:
                st.warning("⚠️ Apify API token required for Instagram. Add it in API Keys section above.")

        col1, col2 = st.columns([3, 1])
        with col1:
            display_name = st.text_input("Display Name (optional)")
        with col2:
            st.write("")  # Spacer
            st.write("")
            add_btn = st.button("➕ Add", type="primary", use_container_width=True)

        if add_btn and new_url:
            # Use the unified parser
            platform, username, clean_url = parse_creator_url(new_url)
            creator_id = add_creator(platform, username, clean_url, display_name or username)

            if creator_id:
                st.success(f"Added @{username} ({platform.upper()}) to watchlist!")
                # Auto-sync
                sync_creator(creator_id)
                st.rerun()

    st.markdown("---")

    # List Creators
    if not creators:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 48px; margin-bottom: 16px;">👥</div>
            <h3 style="color: #fff; margin-bottom: 8px;">Your watchlist is empty</h3>
            <p style="color: #888;">Add some creators above to start tracking viral content!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for creator in creators:
            st.markdown(f"""
            <div style="
                background: rgba(17, 17, 17, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 16px 20px;
                margin-bottom: 12px;
            ">
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                platform_icon = "📺" if creator['platform'] == 'youtube' else "📸"
                content_type = "videos" if creator['platform'] == 'youtube' else "reels"
                st.markdown(f"**{platform_icon} {creator['display_name']}**")
                st.caption(f"@{creator['username']} • {creator['platform'].upper()} • {creator['video_count'] or 0} {content_type}")

            with col2:
                if creator.get('last_synced'):
                    st.caption(f"🕐 {creator['last_synced'][:10]}")
                else:
                    st.caption("⏳ Never synced")

            with col3:
                if st.button("🔄 Sync", key=f"sync_{creator['id']}", help="Sync videos"):
                    sync_creator(creator['id'])
                    st.rerun()

            with col4:
                if st.button("🗑️", key=f"del_{creator['id']}", help="Remove"):
                    remove_creator(creator['id'])
                    st.rerun()

            # Show top videos for this creator
            videos = get_videos_for_creator(creator['id'], limit=5)
            if videos:
                with st.expander(f"📊 Top {len(videos)} videos"):
                    for v in videos:
                        score = v['outlier_score']
                        score_color = "#ff6b6b" if score >= 4 else "#0070f3" if score >= 3 else "#60a5fa" if score >= 2 else "#6b7280"
                        st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                            <span style="color: {score_color}; font-weight: 700; min-width: 40px;">{score}x</span>
                            <span style="color: #ccc; flex: 1;">{v['title'][:55]}...</span>
                            <span style="color: #888; font-size: 12px;">{v.get('view_count', 0):,}</span>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

# ============================================
# VIEW: REMIX STUDIO
# ============================================
elif st.session_state.current_view == 'remix':
    st.markdown("""
    <h1 style="margin-bottom: 0;">✨ Remix Studio</h1>
    """, unsafe_allow_html=True)
    st.caption("Transform viral content into your authentic voice")

    st.markdown("""
    <div style="display: flex; gap: 12px; margin: 16px 0 24px 0;">
        <span class="stat-badge">🎯 Powered by Claude</span>
        <span class="stat-badge">🎤 Your VoiceDNA loaded</span>
    </div>
    """, unsafe_allow_html=True)

    # Video selection
    col1, col2 = st.columns([2, 1])

    with col1:
        # Get all videos for dropdown
        all_outliers = get_all_outliers(min_score=1.5, limit=200)
        video_options = {f"{v['outlier_score']}x | {v['title'][:50]}... (@{v['username']})": v['id'] for v in all_outliers}

        selected_label = st.selectbox(
            "Select a video to remix",
            options=[""] + list(video_options.keys()),
            index=0
        )

        if selected_label and selected_label in video_options:
            st.session_state.selected_video_id = video_options[selected_label]

    with col2:
        # Or enter URL directly
        direct_url = st.text_input("Or paste video URL")
        if direct_url and st.button("Load Video"):
            # Fetch transcript directly
            scraper = st.session_state.scraper
            transcript = scraper.get_transcript(direct_url)
            st.session_state.direct_transcript = transcript
            st.session_state.selected_video_id = None

    st.markdown("---")

    # Show selected video and remix
    video = None
    transcript = None

    if st.session_state.selected_video_id:
        video = get_video_by_id(st.session_state.selected_video_id)

    if video:
        col_info, col_thumb = st.columns([2, 1])

        with col_info:
            st.subheader(video['title'])
            st.caption(f"@{video['username']} • {video['platform'].upper()}")
            st.markdown(f"**{video['outlier_score']}x** outlier • {video.get('view_count', 0):,} views")

        with col_thumb:
            if video.get('thumbnail'):
                st.image(video['thumbnail'], use_container_width=True)

        st.markdown("---")

        # Transcript Section
        col_trans, col_remix = st.columns(2)

        with col_trans:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
                <span style="font-size: 20px;">📝</span>
                <span style="font-size: 18px; font-weight: 600; color: white;">Transcript</span>
            </div>
            """, unsafe_allow_html=True)

            transcript_text = video.get('transcript', '')
            has_error = transcript_text and any(err in transcript_text for err in ["Error", "disabled", "No transcript"])

            if transcript_text and not has_error:
                st.text_area("Original", value=transcript_text, height=400, disabled=True, label_visibility="collapsed")
            else:
                if transcript_text and has_error:
                    st.warning(transcript_text)

                # Determine transcription method based on platform
                is_instagram = video.get('platform', '').lower() == 'instagram'

                if is_instagram:
                    btn_label = "🔄 Re-transcribe" if has_error else "🎙️ Transcribe with AssemblyAI"
                    if not assemblyai_key:
                        st.warning("⚠️ AssemblyAI API key required for Instagram transcription.")
                    elif st.button(btn_label, type="primary", use_container_width=True):
                        transcriber = get_assemblyai_transcriber()
                        if transcriber:
                            with st.spinner("Transcribing with AssemblyAI... (may take 30-60s)"):
                                # Instagram videos need direct video URL
                                video_url = video.get('video_url') or video.get('url')
                                transcript = transcriber.transcribe_url(video_url)
                                save_transcript(video['id'], transcript)
                                st.rerun()
                        else:
                            st.error("AssemblyAI transcriber not available")
                else:
                    # YouTube - use free transcript API
                    btn_label = "🔄 Re-fetch Transcript" if has_error else "📥 Fetch Transcript"
                    if st.button(btn_label, type="primary", use_container_width=True):
                        scraper = st.session_state.scraper
                        with st.spinner("Fetching transcript..."):
                            transcript = scraper.get_transcript(video['url'])
                            save_transcript(video['id'], transcript)
                            st.rerun()

        with col_remix:
            st.markdown("""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 16px;">
                <span style="font-size: 20px;">✨</span>
                <span style="font-size: 18px; font-weight: 600; background: linear-gradient(135deg, #0070f3, #00a0ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Your Version</span>
            </div>
            """, unsafe_allow_html=True)

            transcript_to_remix = video.get('transcript') or st.session_state.get('direct_transcript')

            if transcript_to_remix and anthropic_key:
                if st.button("🪄 Remix in My Voice", type="primary", use_container_width=True):
                    with st.spinner("✨ Claude is writing in your voice..."):
                        remixer = Remixer(anthropic_key)
                        remixed = remixer.remix_content(transcript_to_remix)
                        st.session_state.remixed_content = remixed

                        if video:
                            save_remix(video['id'], remixed)

                if 'remixed_content' in st.session_state:
                    st.text_area(
                        "Your Version",
                        value=st.session_state.remixed_content,
                        height=400,
                        key="remix_output",
                        label_visibility="collapsed"
                    )
                    col_copy, col_download = st.columns(2)
                    with col_copy:
                        st.download_button(
                            "📋 Download",
                            st.session_state.remixed_content,
                            file_name="remixed_post.txt",
                            use_container_width=True
                        )
                    with col_download:
                        if st.button("🔄 Regenerate", use_container_width=True):
                            with st.spinner("✨ Regenerating..."):
                                remixer = Remixer(anthropic_key)
                                remixed = remixer.remix_content(transcript_to_remix)
                                st.session_state.remixed_content = remixed
                                if video:
                                    save_remix(video['id'], remixed)
                                st.rerun()
            elif not anthropic_key:
                st.markdown("""
                <div style="
                    background: rgba(255, 193, 7, 0.1);
                    border: 1px solid rgba(255, 193, 7, 0.3);
                    border-radius: 8px;
                    padding: 16px;
                    text-align: center;
                ">
                    <div style="font-size: 24px; margin-bottom: 8px;">🔑</div>
                    <div style="color: #ffc107;">Enter Anthropic API key in sidebar</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: rgba(0, 112, 243, 0.1);
                    border: 1px solid rgba(0, 112, 243, 0.3);
                    border-radius: 8px;
                    padding: 16px;
                    text-align: center;
                ">
                    <div style="font-size: 24px; margin-bottom: 8px;">📝</div>
                    <div style="color: #0070f3;">Fetch transcript first, then remix</div>
                </div>
                """, unsafe_allow_html=True)

    elif 'direct_transcript' in st.session_state:
        # Direct URL mode
        st.subheader("📝 Transcript (Direct URL)")

        col_trans, col_remix = st.columns(2)

        with col_trans:
            st.text_area("Original", value=st.session_state.direct_transcript, height=400, disabled=True)

        with col_remix:
            st.subheader("✨ Remixed Version")

            if anthropic_key:
                if st.button("🪄 Remix in My Voice", type="primary", use_container_width=True):
                    with st.spinner("Remixing with Claude..."):
                        remixer = Remixer(anthropic_key)
                        remixed = remixer.remix_content(st.session_state.direct_transcript)
                        st.session_state.remixed_content = remixed

                if 'remixed_content' in st.session_state:
                    st.text_area(
                        "Your Version",
                        value=st.session_state.remixed_content,
                        height=400
                    )
            else:
                st.warning("Enter Anthropic API key in sidebar")
    else:
        st.info("Select a video from the dropdown or paste a URL to get started")
