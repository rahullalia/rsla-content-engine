# 🏰 Content Engine

Sandcastles.ai alternative for finding viral content outliers and remixing them.

## Status
- **Version:** v1.1 (Instagram Support Added)
- **Last Updated:** Dec 15, 2025
- **Live URL:** https://rsla-content-engine.streamlit.app/
- **YouTube:** ✅ Fully working
- **Instagram:** ✅ Working (via Apify + AssemblyAI)
- **TikTok:** 🔒 Pending (needs Apify TikTok scraper)

## Access

**Production (Streamlit Cloud):**
1. Visit https://rsla-content-engine.streamlit.app/
2. Sign in with whitelisted Google account
3. Enter password: `rsla2025content!`
4. Session persists for 24 hours

**Local Development:**

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
| YouTube | ✅ Ready | Free via yt-dlp + youtube_transcript_api |
| Instagram | ✅ Ready | Apify (~$0.003/reel) + AssemblyAI (~$0.01/min) |
| TikTok | 🔒 Pending | Needs Apify TikTok scraper |

## API Keys Required

| Key | Purpose | Required? |
|-----|---------|-----------|
| Anthropic | Claude remix | ✅ Yes |
| Apify | Instagram scraping | For Instagram |
| AssemblyAI | Instagram transcription | For Instagram |

## File Structure

```
content_engine/
├── src/
│   ├── app.py           # Streamlit UI (3 views + platform filter)
│   ├── scraper.py       # YouTubeScraper, InstagramScraper, AssemblyAITranscriber
│   ├── remix_engine.py  # Claude + voice prompt
│   ├── database.py      # SQLite storage + URL parsers
│   └── import_csv.py    # Manual CSV import utility
├── data/
│   └── content_engine.db  # Auto-created
├── .streamlit/
│   ├── config.toml           # RSL/A theme
│   └── secrets.toml.example  # Template for Streamlit Cloud
├── .env                 # Your API keys (local dev)
├── .env.example         # Template
└── requirements.txt
```

## Manual CSV Import

If the API scraping times out, you can export from Apify console and import manually:

```bash
cd content_engine/src
python3 import_csv.py /path/to/csv/folder
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
