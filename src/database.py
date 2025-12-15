"""
Database layer for Content Engine.
Stores watchlist creators and synced videos.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "content_engine.db"

def get_connection():
    """Get database connection, creating tables if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    create_tables(conn)
    return conn

def create_tables(conn):
    """Create database tables if they don't exist."""
    cursor = conn.cursor()

    # Creators watchlist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS creators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            username TEXT NOT NULL,
            url TEXT NOT NULL,
            display_name TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_synced TIMESTAMP,
            UNIQUE(platform, username)
        )
    """)

    # Videos from creators
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER NOT NULL,
            platform_video_id TEXT NOT NULL,
            title TEXT,
            url TEXT,
            view_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            duration INTEGER,
            upload_date TEXT,
            thumbnail TEXT,
            outlier_score REAL DEFAULT 0,
            transcript TEXT,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES creators(id),
            UNIQUE(creator_id, platform_video_id)
        )
    """)

    # Remixed content history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remixes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER NOT NULL,
            remixed_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (video_id) REFERENCES videos(id)
        )
    """)

    conn.commit()

# ============================================
# CREATOR OPERATIONS
# ============================================

def add_creator(platform: str, username: str, url: str, display_name: str = None) -> int:
    """Add a creator to watchlist. Returns creator ID."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO creators (platform, username, url, display_name)
            VALUES (?, ?, ?, ?)
        """, (platform.lower(), username.lower(), url, display_name or username))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # Already exists, return existing ID
        cursor.execute("""
            SELECT id FROM creators WHERE platform = ? AND username = ?
        """, (platform.lower(), username.lower()))
        row = cursor.fetchone()
        return row['id'] if row else None
    finally:
        conn.close()

def remove_creator(creator_id: int) -> bool:
    """Remove creator and their videos from watchlist."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Delete videos first (foreign key)
        cursor.execute("DELETE FROM videos WHERE creator_id = ?", (creator_id,))
        cursor.execute("DELETE FROM creators WHERE id = ?", (creator_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_all_creators() -> list:
    """Get all creators in watchlist."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT c.*,
                   COUNT(v.id) as video_count,
                   MAX(v.synced_at) as latest_video_sync
            FROM creators c
            LEFT JOIN videos v ON c.id = v.creator_id
            GROUP BY c.id
            ORDER BY c.added_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_creator_by_id(creator_id: int) -> dict:
    """Get single creator by ID."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM creators WHERE id = ?", (creator_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def update_creator_sync_time(creator_id: int):
    """Update last_synced timestamp for creator."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE creators SET last_synced = CURRENT_TIMESTAMP WHERE id = ?
        """, (creator_id,))
        conn.commit()
    finally:
        conn.close()

# ============================================
# VIDEO OPERATIONS
# ============================================

def upsert_videos(creator_id: int, videos: list):
    """Insert or update videos for a creator."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        for video in videos:
            cursor.execute("""
                INSERT INTO videos (
                    creator_id, platform_video_id, title, url, view_count,
                    like_count, comment_count, duration, upload_date,
                    thumbnail, outlier_score, synced_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(creator_id, platform_video_id) DO UPDATE SET
                    view_count = excluded.view_count,
                    like_count = excluded.like_count,
                    comment_count = excluded.comment_count,
                    outlier_score = excluded.outlier_score,
                    synced_at = CURRENT_TIMESTAMP
            """, (
                creator_id,
                video.get('id') or video.get('platform_video_id'),
                video.get('title'),
                video.get('url'),
                video.get('view_count', 0),
                video.get('like_count', 0),
                video.get('comment_count', 0),
                video.get('duration'),
                video.get('upload_date'),
                video.get('thumbnail'),
                video.get('outlier_score', 0)
            ))
        conn.commit()
        update_creator_sync_time(creator_id)
    finally:
        conn.close()

def get_videos_for_creator(creator_id: int, limit: int = 50) -> list:
    """Get videos for a specific creator."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM videos
            WHERE creator_id = ?
            ORDER BY outlier_score DESC
            LIMIT ?
        """, (creator_id, limit))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_all_outliers(min_score: float = 2.0, limit: int = 100) -> list:
    """Get top outliers across all creators."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT v.*, c.username, c.platform, c.display_name as creator_name
            FROM videos v
            JOIN creators c ON v.creator_id = c.id
            WHERE v.outlier_score >= ?
            ORDER BY v.outlier_score DESC
            LIMIT ?
        """, (min_score, limit))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_video_by_id(video_id: int) -> dict:
    """Get single video by ID."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT v.*, c.username, c.platform, c.display_name as creator_name
            FROM videos v
            JOIN creators c ON v.creator_id = c.id
            WHERE v.id = ?
        """, (video_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def save_transcript(video_id: int, transcript: str):
    """Save transcript for a video."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE videos SET transcript = ? WHERE id = ?
        """, (transcript, video_id))
        conn.commit()
    finally:
        conn.close()

# ============================================
# REMIX OPERATIONS
# ============================================

def save_remix(video_id: int, content: str) -> int:
    """Save a remixed version of video content."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO remixes (video_id, remixed_content)
            VALUES (?, ?)
        """, (video_id, content))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def get_remixes_for_video(video_id: int) -> list:
    """Get all remixes for a video."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT * FROM remixes WHERE video_id = ?
            ORDER BY created_at DESC
        """, (video_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

# ============================================
# UTILITY
# ============================================

def parse_youtube_url(url: str) -> tuple:
    """Parse YouTube URL to extract username/channel info."""
    url = url.strip()

    # Handle @username format
    if '/@' in url:
        parts = url.split('/@')
        username = parts[1].split('/')[0].split('?')[0]
        return ('youtube', username, url.split('/videos')[0].split('/shorts')[0])

    # Handle /channel/ format
    if '/channel/' in url:
        parts = url.split('/channel/')
        channel_id = parts[1].split('/')[0].split('?')[0]
        return ('youtube', channel_id, url)

    # Handle /c/ format
    if '/c/' in url:
        parts = url.split('/c/')
        username = parts[1].split('/')[0].split('?')[0]
        return ('youtube', username, url)

    return ('youtube', 'unknown', url)
