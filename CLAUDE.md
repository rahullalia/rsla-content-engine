# Content Engine - Claude Context

**Last Updated:** 2025-12-14 (Streamlit Cloud deployment)

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
│   ├── app.py           # Streamlit UI with auth + 3 views
│   ├── scraper.py       # yt-dlp + youtube_transcript_api
│   ├── remix_engine.py  # Claude API (claude-sonnet-4-20250514)
│   └── database.py      # SQLite storage
├── data/
│   └── content_engine.db  # Auto-created on Streamlit Cloud
├── .streamlit/
│   └── config.toml      # RSL/A theme (dark mode)
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

## Platform Support Status (Dec 14, 2025)

| Platform | yt-dlp Extractor | Video Stats | Profile Scrape | Transcript |
|----------|------------------|-------------|----------------|------------|
| YouTube | ✅ Working | ✅ | ✅ | ✅ youtube_transcript_api |
| TikTok | ⚠️ IP blocked | ❌ | ❌ | ❌ Need Whisper |
| Instagram | ⚠️ Needs auth | ❌ | ❌ (BROKEN upstream) | ❌ Need Whisper |

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

## Next Session TODO

1. **Add Apify integration** for TikTok/Instagram profile scraping
2. **Add Whisper transcription** (local or API) for non-YouTube
3. **Test end-to-end** with real TikTok/IG creator profiles
4. **Consider cloud database** if SQLite persistence becomes an issue

## Related Files

- Parent workspace CLAUDE.md: `/Users/rahullalia/Developer/CLAUDE.md`
- Apify credentials: Check `.env` in `leadGeneration/automation/`
- Voice research: `socialMedia/` folder
