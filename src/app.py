"""
Content Engine - Sandcastles.ai Alternative
Find viral outliers from your watchlist and remix them.
"""
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables first
load_dotenv(Path(__file__).parent.parent / ".env")

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Content Engine",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# AUTHENTICATION - @rsla.io only
# ============================================
ALLOWED_EMAILS = ["rahul@rsla.io", "siddharth@rsla.io"]

def check_auth():
    """Check if user is authenticated with allowed email."""
    # Check if running on Streamlit Cloud with auth
    if hasattr(st, 'experimental_user') and st.experimental_user.email:
        email = st.experimental_user.email
        if email in ALLOWED_EMAILS or email.endswith("@rsla.io"):
            return True, email
        return False, email

    # For local development or if auth not configured
    # Check for password in secrets/env
    auth_password = os.getenv("AUTH_PASSWORD") or st.secrets.get("AUTH_PASSWORD", "")

    if auth_password:
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False

        if not st.session_state.authenticated:
            return False, None

    return True, "local"

def show_login():
    """Show login form for password auth."""
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: #111;
            border-radius: 12px;
            border: 1px solid #222;
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔒 Content Engine")
        st.caption("Enter password to continue")

        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary", use_container_width=True):
            auth_password = os.getenv("AUTH_PASSWORD") or st.secrets.get("AUTH_PASSWORD", "")
            if password == auth_password:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid password")

# Check authentication
is_authed, user_email = check_auth()

if not is_authed:
    if user_email:
        # User logged in but not authorized
        st.error(f"Access denied. {user_email} is not authorized.")
        st.stop()
    else:
        # Show password login
        show_login()
        st.stop()

# Import app modules after auth check
from scraper import YouTubeScraper
from remix_engine import Remixer
from database import (
    add_creator, remove_creator, get_all_creators, get_creator_by_id,
    upsert_videos, get_videos_for_creator, get_all_outliers, get_video_by_id,
    save_transcript, save_remix, parse_youtube_url
)

# ============================================
# RSL/A BRAND STYLING
# ============================================
# Brand Colors: Blue #0070f3, Black #0a0a0a, White #ffffff
# Fonts: Satoshi (display), Inter (body)
st.markdown("""
<style>
    @import url('https://api.fontshare.com/v2/css?f[]=satoshi@700,900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    /* Base */
    .stApp {
        background-color: #0a0a0a;
    }
    .block-container {
        padding-top: 2rem;
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
    }
    /* Body text - avoid overriding span to preserve icon fonts */
    p, label, .stMarkdown > div {
        font-family: 'Inter', system-ui, sans-serif;
    }

    /* Brand accent color */
    .stButton > button[kind="primary"] {
        background-color: #0070f3 !important;
        border-color: #0070f3 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #0060d0 !important;
        border-color: #0060d0 !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: #111 !important;
        border: 1px solid #333 !important;
        color: #999 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #0070f3 !important;
        color: #fff !important;
    }

    /* Outlier score colors */
    .outlier-high {
        color: #0070f3 !important;
        font-weight: bold;
    }
    .outlier-medium {
        color: #60a5fa;
    }
    .outlier-low {
        color: #6b7280;
    }

    /* Cards */
    .creator-card, .video-card {
        background: #111;
        border: 1px solid #222;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }

    /* Metric box with brand accent */
    .metric-box {
        background: #111;
        border: 1px solid #0070f3;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #0d0d0d !important;
        border-right: 1px solid #222 !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #111 !important;
        border: 1px solid #333 !important;
        color: #fff !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #0070f3 !important;
        box-shadow: 0 0 0 1px #0070f3 !important;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background-color: #111 !important;
        border: 1px solid #333 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #111 !important;
        border: 1px solid #222 !important;
        border-radius: 8px !important;
    }

    /* Slider */
    .stSlider > div > div > div > div {
        background-color: #0070f3 !important;
    }

    /* Text areas */
    .stTextArea > div > div > textarea {
        background-color: #111 !important;
        border: 1px solid #333 !important;
        color: #fff !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Captions */
    .stCaption {
        color: #888 !important;
    }

    /* Links */
    a {
        color: #0070f3 !important;
    }

    /* RSL/A Logo in sidebar */
    .rsla-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0 16px 0;
    }
    .rsla-logo .icon {
        width: 40px;
        height: 40px;
        background: #0070f3;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
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
        width: 6px;
        height: 20px;
        background: #0070f3;
        transform: skewX(-20deg);
        margin: 0 3px;
        display: inline-block;
    }
    .tool-label {
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
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

    anthropic_key = os.getenv("ANTHROPIC_API_KEY") or st.text_input(
        "Anthropic API Key",
        type="password",
        help="For remixing content"
    )

    openai_key = os.getenv("OPENAI_API_KEY") or st.text_input(
        "OpenAI API Key",
        type="password",
        help="For Whisper transcription (TikTok/IG)"
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
    st.caption("YouTube: ✅ Ready")
    st.caption("TikTok/IG: 🔒 Need Apify")

# ============================================
# MAIN CONTENT
# ============================================

def sync_creator(creator_id: int, limit: int = 30):
    """Sync videos for a creator."""
    creator = get_creator_by_id(creator_id)
    if not creator:
        return False

    scraper = st.session_state.scraper

    with st.spinner(f"Syncing {creator['display_name']}..."):
        videos = scraper.get_channel_videos(creator['url'], limit=limit)
        if videos:
            analyzed = scraper.calculate_outliers(videos)
            upsert_videos(creator_id, analyzed)
            return True
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
    st.title("🔥 Outlier Feed")
    st.caption("Top performing videos across your watchlist")

    # Controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        min_score = st.slider("Minimum Outlier Score", 1.0, 5.0, 2.0, 0.5)
    with col2:
        limit = st.selectbox("Show", [25, 50, 100], index=0)
    with col3:
        if st.button("🔄 Sync All", use_container_width=True):
            sync_all_creators()
            st.rerun()

    st.markdown("---")

    # Get outliers
    outliers = get_all_outliers(min_score=min_score, limit=limit)

    if not outliers:
        st.info("No outliers found. Add creators to your watchlist and sync them first!")
    else:
        # Display as cards
        for video in outliers:
            score = video['outlier_score']
            score_class = 'outlier-high' if score >= 3 else 'outlier-medium' if score >= 2 else 'outlier-low'

            col_thumb, col_info, col_actions = st.columns([1, 3, 1])

            with col_thumb:
                if video.get('thumbnail'):
                    st.image(video['thumbnail'], use_container_width=True)

            with col_info:
                st.markdown(f"**{video['title'][:80]}{'...' if len(video.get('title', '')) > 80 else ''}**")
                st.caption(f"@{video['username']} • {video['platform'].upper()}")
                st.markdown(f"<span class='{score_class}'>{score}x</span> • {video.get('view_count', 0):,} views", unsafe_allow_html=True)

            with col_actions:
                if st.button("Remix →", key=f"remix_{video['id']}"):
                    st.session_state.selected_video_id = video['id']
                    st.session_state.current_view = 'remix'
                    st.rerun()

            st.markdown("---")

# ============================================
# VIEW: WATCHLIST
# ============================================
elif st.session_state.current_view == 'watchlist':
    st.title("👥 Watchlist")
    st.caption("Creators you're tracking")

    # Add Creator Form
    with st.expander("➕ Add Creator", expanded=True):
        new_url = st.text_input(
            "YouTube Channel URL",
            placeholder="https://www.youtube.com/@creatorname"
        )

        col1, col2 = st.columns([3, 1])
        with col1:
            display_name = st.text_input("Display Name (optional)")
        with col2:
            st.write("")  # Spacer
            st.write("")
            add_btn = st.button("Add to Watchlist", type="primary", use_container_width=True)

        if add_btn and new_url:
            platform, username, clean_url = parse_youtube_url(new_url)
            creator_id = add_creator(platform, username, clean_url, display_name or username)

            if creator_id:
                st.success(f"Added @{username} to watchlist!")
                # Auto-sync
                sync_creator(creator_id)
                st.rerun()

    st.markdown("---")

    # List Creators
    creators = get_all_creators()

    if not creators:
        st.info("Your watchlist is empty. Add some creators above!")
    else:
        for creator in creators:
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.markdown(f"**{creator['display_name']}**")
                st.caption(f"@{creator['username']} • {creator['platform'].upper()} • {creator['video_count'] or 0} videos")

            with col2:
                if creator.get('last_synced'):
                    st.caption(f"Synced: {creator['last_synced'][:10]}")
                else:
                    st.caption("Never synced")

            with col3:
                if st.button("🔄", key=f"sync_{creator['id']}", help="Sync videos"):
                    sync_creator(creator['id'])
                    st.rerun()

            with col4:
                if st.button("🗑️", key=f"del_{creator['id']}", help="Remove"):
                    remove_creator(creator['id'])
                    st.rerun()

            # Show top videos for this creator
            videos = get_videos_for_creator(creator['id'], limit=5)
            if videos:
                with st.expander(f"Top {len(videos)} videos"):
                    for v in videos:
                        st.markdown(f"**{v['outlier_score']}x** | {v['title'][:60]}... | {v.get('view_count', 0):,} views")

            st.markdown("---")

# ============================================
# VIEW: REMIX STUDIO
# ============================================
elif st.session_state.current_view == 'remix':
    st.title("✨ Remix Studio")

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
            st.subheader("📝 Transcript")

            if video.get('transcript'):
                transcript = video['transcript']
                st.text_area("Original", value=transcript, height=400, disabled=True)
            else:
                if st.button("Fetch Transcript", type="primary"):
                    scraper = st.session_state.scraper
                    with st.spinner("Fetching transcript..."):
                        transcript = scraper.get_transcript(video['url'])
                        save_transcript(video['id'], transcript)
                        st.rerun()

        with col_remix:
            st.subheader("✨ Remixed Version")

            transcript_to_remix = video.get('transcript') or st.session_state.get('direct_transcript')

            if transcript_to_remix and anthropic_key:
                if st.button("🪄 Remix in My Voice", type="primary", use_container_width=True):
                    with st.spinner("Remixing with Claude..."):
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
                        key="remix_output"
                    )
                    st.download_button(
                        "📋 Copy to Clipboard",
                        st.session_state.remixed_content,
                        file_name="remixed_post.txt"
                    )
            elif not anthropic_key:
                st.warning("Enter Anthropic API key in sidebar to enable remixing")
            else:
                st.info("Fetch transcript first, then remix")

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
