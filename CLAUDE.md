# Content Engine - Claude Context

**Last Updated:** 2025-12-15 (Instagram scraping via Apify working)

## ⚠️ CRITICAL: Pre-Compact Context Preservation

**MANDATORY RULE:** Before ANY auto-compact occurs, Claude MUST run `/wrap` to save session context.

**When to trigger:**
- When you notice context is getting long/heavy
- When the PreCompact hook fires
- Before any summarization or compaction
- If unsure whether compact is imminent, run `/wrap` proactively

**What /wrap does:**
- Saves key decisions, technical details, and progress to CLAUDE.md
- Documents incomplete work and next steps
- Ensures continuity across sessions

**This is non-negotiable.** Context loss degrades work quality. Always preserve before compact.

---

## Project Overview

Sandcastles.ai alternative for finding viral content outliers and remixing them. **Now deployed to Streamlit Cloud.**

**Live URL:** https://rsla-content-engine.streamlit.app/
**GitHub Repo:** https://github.com/rahullalia/rsla-content-engine (public, required for free tier)

**Goal:** Analyze creator profiles across YouTube, TikTok, and Instagram to find viral outliers, get transcripts, and remix into short-form content.

## Deployment & Authentication

**Streamlit Cloud Setup:**
- Viewer whitelist: Only specific emails can access (Sharing settings)
- Password auth: `rsla2025content!` (stored in Streamlit Secrets)
- Session persistence: 24-hour URL tokens survive page refresh
- Secrets configured: `AUTH_PASSWORD`, `ANTHROPIC_API_KEY`

**Authentication Flow:**
1. Streamlit checks if user email is whitelisted
2. User enters password
3. Session token added to URL (`?session=...`)
4. Token valid for 24 hours, checked against time-bucket hash

## Current Architecture

```
content_engine/
├── src/
│   ├── app.py           # Streamlit UI with auth + 3 views + platform filter
│   ├── scraper.py       # YouTubeScraper, InstagramScraper (Apify), AssemblyAITranscriber
│   ├── remix_engine.py  # Claude API (claude-sonnet-4-20250514)
│   ├── database.py      # SQLite storage + URL parsers + migrations
│   └── import_csv.py    # Manual CSV import from Apify exports
├── data/
│   └── content_engine.db  # Auto-created on Streamlit Cloud
├── .streamlit/
│   ├── config.toml           # RSL/A theme (dark mode)
│   └── secrets.toml.example  # Template for Streamlit Cloud secrets
├── .env                 # Local dev only
├── requirements.txt
└── README.md
```

## Tech Stack

- **UI:** Streamlit (Python)
- **Scraping:** yt-dlp (YouTube working, TikTok/IG blocked)
- **Transcripts:** youtube_transcript_api (YouTube only)
- **AI Remix:** Anthropic Claude API
- **Voice:** Custom "Rahul Voice" system prompt

## Platform Support Status (Dec 15, 2025)

| Platform | Video Stats | Profile Scrape | Transcript |
|----------|-------------|----------------|------------|
| YouTube | ✅ yt-dlp | ✅ yt-dlp | ✅ youtube_transcript_api (free) |
| Instagram | ✅ Apify | ✅ Apify | ✅ AssemblyAI (~$0.01-0.02/min) |
| TikTok | ❌ | ❌ | ❌ (needs Apify + AssemblyAI) |

### Instagram Integration (NEW)

**Apify Instagram Reel Scraper:**
- Actor ID: `apify~instagram-reel-scraper` (note: tilde, not slash!)
- Cost: ~$0.0026/reel
- Returns: caption, likes, comments, timestamp, thumbnail, videoUrl
- API endpoint: `POST https://api.apify.com/v2/acts/apify~instagram-reel-scraper/run-sync-get-dataset-items`

**AssemblyAI Transcription:**
- Cost: ~$0.01-0.02 per minute of audio
- Accepts direct video URLs from Apify
- Polls for completion (3s intervals)

### yt-dlp Findings

```bash
# Working extractors
youtube, youtube:playlist, youtube:tab, youtube:shorts:pivot:audio

# Broken/Limited
instagram:user (CURRENTLY BROKEN)
tiktok:effect (CURRENTLY BROKEN)
tiktok:sound (CURRENTLY BROKEN)
tiktok:tag (CURRENTLY BROKEN)

# TikTok needs impersonation
WARNING: The extractor is attempting impersonation, but no impersonate target is available
ERROR: Your IP address is blocked from accessing this post
```

## Multi-Platform Strategy

**For TikTok/Instagram support, recommended approach:**

1. **Apify scrapers** (~$5/1000 videos) — Most reliable
   - Already have Apify token for lead gen automation
   - TikTok Profile Scraper: gets video list + view counts
   - Instagram Profile Scraper: same

2. **Transcription** (since TT/IG don't have caption APIs):
   - Local Whisper: Free, ~1min processing per 1min video
   - Whisper API: $0.006/min, fast

3. **Cost per video analyzed:**
   - YouTube: Free
   - TikTok/IG: ~$0.005 (Apify) + $0.01 (Whisper) = ~$0.015

## Voice Guidelines (remix_engine.py)

The "Rahul Voice" system prompt includes:
- Em dashes for pauses (—)
- Extended vowels ("goooood")
- Casual annotations ("<- cannot stress this enough")
- Specific numbers with context
- Peer-to-peer tone (not expert teaching)
- Tool name-dropping for credibility

## Integration with tools.rsla.io

**Target:** Add as 3rd tab alongside Logo Builder and Image Compressor

**Blockers:**
1. Current stack is Streamlit (Python server required)
2. Need to convert to static HTML/JS
3. API key handling needs secure approach (env vars or user-provided)

**Options discussed:**
- A) Vercel serverless API routes (recommended)
- B) Client-side only with user-provided API key
- C) Iframe Streamlit (ugly, not recommended)

## Running the Tool

```bash
cd /Users/rahullalia/Developer/1-Projects/rsla.io-website/content_engine

# Install deps
pip install streamlit yt-dlp youtube_transcript_api anthropic

# Run
python3 -m streamlit run src/app.py
```

## Known Issues

1. **YouTube transcript IP blocking:** Streamlit Cloud IPs may be blocked by YouTube. Transcripts work for most videos but some fail. "Re-fetch Transcript" button added for retries.

2. **SQLite data persistence:** Streamlit Cloud may reset data on redeploy or container restart. For critical data, consider migrating to Supabase/PlanetScale.

3. **Model updates:** Using `claude-sonnet-4-20250514`. If deprecated, update in `remix_engine.py`.

## API Costs

**Per remix/regenerate operation: ~$0.02-0.04**

| Component | Tokens | Cost |
|-----------|--------|------|
| System prompt (VoiceDNA) | ~2,000 | - |
| Transcript input | ~2,000-5,000 | - |
| Output (max) | 1,024 | - |
| **Input total** | ~4,000-7,000 | ~$0.012-0.021 |
| **Output total** | ~500-1,000 | ~$0.0075-0.015 |

**Claude Sonnet pricing:** Input $3/1M tokens, Output $15/1M tokens

At 100 remixes: ~$2-4 total cost.

## Session Log (Dec 14, 2025)

**Completed:**
- Deployed to Streamlit Cloud
- Fixed auth error (`st.experimental_user.email` doesn't exist on free tier)
- Fixed Claude model (updated to `claude-sonnet-4-20250514`)
- Added transcript validation before remix
- Fixed API key retrieval from `st.secrets`
- Added "Re-fetch Transcript" button for failed fetches
- Fixed Sync All button alignment (28px spacer)
- Added 24-hour session persistence via URL token

**Commits pushed:** 06e70cd, b39fb38, 8440dbe, 9bc40db, 17b8f9d, 2b2e0e5, fcf38fa

## Session Log (Dec 15, 2025)

**Completed:**
- Added Instagram scraping via Apify (`apify~instagram-reel-scraper`)
- Added AssemblyAI transcription for Instagram videos
- Fixed Apify actor ID format (tilde vs slash)
- Added platform filter tabs (All/YouTube/Instagram) to Outlier Feed
- Added sidebar API token inputs for Apify and AssemblyAI
- Added `video_url` column to videos table with migration
- Created `import_csv.py` for manual CSV imports from Apify exports
- Imported 90 reels (nick_saraev, heytony.agency, jasperhighlevel) to local DB

**Key Bug Fix:**
- Actor ID must use tilde: `apify~instagram-reel-scraper` NOT `apify/instagram-reel-scraper`

**Commits pushed:** cb8b895, a2c56e9, 0cdb6ad, b2912c0

**API Keys (in Streamlit Secrets):**
- `APIFY_API_TOKEN` - For Instagram scraping
- `ASSEMBLYAI_API_KEY` - For Instagram transcription
- `ANTHROPIC_API_KEY` - For content remixing

## Next Session TODO

1. ~~**Add Apify integration** for Instagram profile scraping~~ ✅ DONE
2. ~~**Add AssemblyAI transcription** for Instagram~~ ✅ DONE
3. **Add TikTok support** - needs Apify TikTok scraper
4. **Add CSV upload to Streamlit app** - for manual imports to cloud DB
5. **Consider cloud database** if SQLite persistence becomes an issue
6. **Debug Matt's IG** - some accounts don't return reels (reason unknown)

## Related Files

- Parent workspace CLAUDE.md: `/Users/rahullalia/Developer/CLAUDE.md`
- Apify credentials: Check `.env` in `leadGeneration/automation/`
- Voice research: `socialMedia/` folder
