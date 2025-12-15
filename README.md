# 🏰 Content Engine

Local Sandcastles.ai alternative for finding viral content outliers and remixing them.

## Status
- **Version:** v0.5 (Full watchlist + outlier feed)
- **Last Updated:** Dec 14, 2025
- **YouTube:** ✅ Fully working
- **TikTok/IG:** 🔒 Pending (needs Apify)

## Quick Start

```bash
cd content_engine

# Install dependencies
pip install -r requirements.txt

# Set up API keys
cp .env.example .env
# Edit .env with your Anthropic key

# Run
streamlit run src/app.py
```

Opens at http://localhost:8501

## Features

### 1. Watchlist
- Add YouTube creators by URL
- Auto-syncs videos on add
- Track multiple creators

### 2. Outlier Feed
- Combined feed across all creators
- Filter by outlier score (2x, 3x, etc.)
- One-click remix

### 3. Remix Studio
- Fetch transcripts
- Rewrite in your voice using Claude
- Download/copy output

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| YouTube | ✅ Ready | Free via yt-dlp |
| TikTok | 🔒 Pending | Needs Apify token |
| Instagram | 🔒 Pending | Needs Apify token |

## API Keys Required

| Key | Purpose | Required? |
|-----|---------|-----------|
| Anthropic | Claude remix | ✅ Yes |
| OpenAI | Whisper (TT/IG only) | Only for TikTok/IG |
| Apify | TT/IG scraping | Only for TikTok/IG |

## File Structure

```
content_engine/
├── src/
│   ├── app.py           # Streamlit UI (3 views)
│   ├── scraper.py       # yt-dlp wrapper
│   ├── remix_engine.py  # Claude + voice prompt
│   └── database.py      # SQLite storage
├── data/
│   └── content_engine.db  # Auto-created
├── .env                 # Your API keys
├── .env.example         # Template
└── requirements.txt
```

## Cost Comparison

| Service | Your Cost | Sandcastles |
|---------|-----------|-------------|
| YouTube | Free | $29-99/mo |
| TikTok/IG | ~$0.015/video | included |
| Remix | ~$0.01-0.03 | included |
| **Monthly (heavy use)** | **~$10-15** | **$29-99** |

## Voice Guidelines

The remix engine uses custom "Rahul Voice" prompt:
- Em dashes for pauses
- Extended vowels ("goooood")
- Casual annotations
- Peer-to-peer tone
- Tool name-dropping

See `src/remix_engine.py` for full prompt.

---
*Built for RSL/A*
