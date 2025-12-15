# Content Engine - Claude Context

**Last Updated:** 2025-12-14

## Project Overview

Local "Sandcastles.ai" alternative for finding viral content outliers and remixing them. Built with Antigravity (Google).

**Goal:** Analyze creator profiles across YouTube, TikTok, and Instagram to find viral outliers, get transcripts, and remix into short-form content.

## Current Architecture

```
content_engine/
├── src/
│   ├── app.py           # Streamlit UI
│   ├── scraper.py       # yt-dlp wrapper for video metadata
│   └── remix_engine.py  # Claude API integration with voice guidelines
├── tests/
│   ├── test_scraper.py
│   └── test_remix.py
├── docs/
│   ├── task.md          # Development checklist
│   ├── walkthrough.md   # Feature documentation
│   └── implementation_plan.md
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

## Next Session TODO

1. **Add Apify integration** for TikTok/Instagram profile scraping
2. **Add Whisper transcription** (local or API) for non-YouTube
3. **Test end-to-end** with real TikTok/IG creator profiles
4. **Plan conversion** to static HTML/JS for tools platform

## Related Files

- Parent workspace CLAUDE.md: `/Users/rahullalia/Developer/CLAUDE.md`
- Apify credentials: Check `.env` in `leadGeneration/automation/`
- Voice research: `socialMedia/` folder
