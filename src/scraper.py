import yt_dlp
import statistics
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import ssl
import certifi
import os
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# Fix for macOS SSL certificate issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


# ============================================
# INSTAGRAM SCRAPER (APIFY)
# ============================================

class InstagramScraper:
    """
    Scrapes Instagram reels using Apify's Instagram Reel Scraper.
    Cost: ~$0.0026/reel (metadata only, no transcripts)
    """

    # Note: Actor ID uses tilde (~) not slash (/)
    APIFY_ACTOR_ID = "apify~instagram-reel-scraper"
    APIFY_API_BASE = "https://api.apify.com/v2"

    def __init__(self, api_token: str = None):
        self.api_token = api_token or os.getenv("APIFY_API_TOKEN")
        if not self.api_token:
            raise ValueError("APIFY_API_TOKEN required. Set in .env or pass to constructor.")

    def get_reels(self, username: str, limit: int = 10) -> list:
        """
        Fetch reels from an Instagram profile.

        Args:
            username: Instagram username (without @)
            limit: Max number of reels to fetch

        Returns:
            List of reel dictionaries with metadata
        """
        url = f"{self.APIFY_API_BASE}/acts/{self.APIFY_ACTOR_ID}/run-sync-get-dataset-items"

        headers = {
            "Content-Type": "application/json"
        }

        params = {
            "token": self.api_token
        }

        payload = {
            "username": [username],
            "resultsLimit": limit
        }

        try:
            print(f"Fetching {limit} reels from @{username}...")
            print(f"API URL: {url}")
            print(f"Payload: {payload}")

            response = requests.post(url, json=payload, headers=headers, params=params, timeout=300)

            # Log response details for debugging
            print(f"Response status: {response.status_code}")

            if response.status_code != 200:
                print(f"Error response: {response.text[:500]}")

            response.raise_for_status()

            data = response.json()
            print(f"Got {len(data)} items from API")

            # Transform Apify response to our standard format
            reels = []
            for item in data:
                reels.append({
                    'id': item.get('id') or item.get('shortCode'),
                    'platform_video_id': item.get('id') or item.get('shortCode'),
                    'title': item.get('caption', '')[:200] if item.get('caption') else 'No caption',
                    'url': item.get('url') or f"https://www.instagram.com/reel/{item.get('shortCode')}",
                    'view_count': item.get('videoPlayCount') or item.get('playCount', 0),
                    'like_count': item.get('likesCount', 0),
                    'comment_count': item.get('commentsCount', 0),
                    'duration': item.get('videoDuration'),
                    'upload_date': item.get('timestamp', '').split('T')[0] if item.get('timestamp') else None,
                    'thumbnail': item.get('displayUrl') or item.get('thumbnailUrl'),
                    'video_url': item.get('videoUrl'),  # Direct video URL for transcription
                    'owner_username': item.get('ownerUsername', username)
                })

            print(f"Fetched {len(reels)} reels from @{username}")
            return reels

        except requests.exceptions.RequestException as e:
            print(f"Error fetching Instagram reels: {e}")
            return []

    def calculate_outliers(self, videos: list) -> list:
        """
        Calculate outlier score for each video.
        Score = Video Views / Average Views of the batch.
        """
        if not videos:
            return []

        # Filter videos with valid view counts
        valid_videos = [v for v in videos if v.get('view_count') is not None and v.get('view_count', 0) > 0]

        if not valid_videos:
            return videos

        total_views = sum(v['view_count'] for v in valid_videos)
        avg_views = total_views / len(valid_videos) if len(valid_videos) > 0 else 0

        for video in videos:
            views = video.get('view_count') or 0
            if avg_views > 0:
                video['outlier_score'] = round(views / avg_views, 2)
            else:
                video['outlier_score'] = 0

            video['avg_views_benchmark'] = round(avg_views)

        # Sort by outlier score descending
        videos.sort(key=lambda x: x.get('outlier_score', 0), reverse=True)
        return videos


# ============================================
# ASSEMBLYAI TRANSCRIPTION
# ============================================

class AssemblyAITranscriber:
    """
    Transcribe video/audio using AssemblyAI.
    Cost: ~$0.01-0.02 per minute of audio.
    """

    API_BASE = "https://api.assemblyai.com/v2"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ASSEMBLYAI_API_KEY")
        if not self.api_key:
            raise ValueError("ASSEMBLYAI_API_KEY required. Set in .env or pass to constructor.")

        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }

    def transcribe_url(self, video_url: str) -> str:
        """
        Transcribe audio from a video URL.
        AssemblyAI can directly process video URLs.

        Args:
            video_url: Direct URL to video file

        Returns:
            Transcript text or error message
        """
        if not video_url:
            return "Error: No video URL provided"

        try:
            # Start transcription job
            response = requests.post(
                f"{self.API_BASE}/transcript",
                json={"audio_url": video_url},
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()

            transcript_id = response.json()['id']
            print(f"Transcription job started: {transcript_id}")

            # Poll for completion
            polling_endpoint = f"{self.API_BASE}/transcript/{transcript_id}"

            while True:
                poll_response = requests.get(polling_endpoint, headers=self.headers, timeout=30)
                poll_response.raise_for_status()

                result = poll_response.json()
                status = result['status']

                if status == 'completed':
                    return result['text'] or "No speech detected"
                elif status == 'error':
                    return f"Transcription error: {result.get('error', 'Unknown error')}"

                print(f"Transcription status: {status}...")
                time.sleep(3)  # Poll every 3 seconds

        except requests.exceptions.RequestException as e:
            return f"Error transcribing: {e}"

    def transcribe_instagram_reel(self, reel: dict) -> str:
        """
        Transcribe an Instagram reel using its video URL.

        Args:
            reel: Reel dictionary with 'video_url' key

        Returns:
            Transcript text
        """
        video_url = reel.get('video_url')
        if not video_url:
            return "Error: Reel has no video URL. Re-scrape with video URLs enabled."

        return self.transcribe_url(video_url)

class YouTubeScraper:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'extract_flat': True, # Don't download video files
            'force_generic_extractor': False,
        }

    def get_channel_videos(self, channel_url, limit=50):
        """
        Fetches the latest videos from a channel.
        Handles single video URLs by resolving them to the channel first.
        """
        # 1. Handle Single Video URLs (detect 'watch?v=' or 'youtu.be/')
        if 'watch?v=' in channel_url or 'youtu.be/' in channel_url:
            print(f"Detected video URL: {channel_url}. Resolving channel...")
            try:
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(channel_url, download=False)
                    if info and 'uploader_url' in info:
                        channel_url = info['uploader_url']
                        print(f"Resolved to channel: {channel_url}")
                    else:
                        print("Could not resolve channel from video.")
            except Exception as e:
                print(f"Error resolving channel: {e}")
                # Fall through and try anyway, though it will likely fail if it's a video link

        # 2. Add /videos to ensure we get the video tab if a generic channel URL is passed
        # Only do this if it looks like a standard channel URL
        if '/@' in channel_url and not channel_url.endswith('/videos'):
             target_url = channel_url.rstrip('/') + '/videos'
        else:
            target_url = channel_url

        ydl_opts = self.ydl_opts.copy()
        ydl_opts['playlistend'] = limit

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(target_url, download=False)
                
                if 'entries' not in info:
                    return []
                
                videos = []
                for entry in info['entries']:
                    if not entry:
                        continue
                        
                    # Filter out Shorts if possible, or keep them. 
                    # Usually shorts have 60s length or less, but we might want them.
                    # For now, let's include everything.
                    
                    videos.append({
                        'id': entry.get('id'),
                        'title': entry.get('title'),
                        'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                        'view_count': entry.get('view_count', 0),
                        'upload_date': entry.get('upload_date'),
                        'duration': entry.get('duration'),
                        'thumbnail': entry.get('thumbnail') # yt-dlp usually provides a thumbnail url
                    })
                
                return videos
        except Exception as e:
            print(f"Error fetching channel: {e}")
            return []

    def calculate_outliers(self, videos):
        """
        Calculates outlier score for each video.
        Score = Video Views / Average Views of the fetched batch.
        """
        if not videos:
            return []

        # Filter out videos with None view counts just in case
        valid_videos = [v for v in videos if v.get('view_count') is not None]
        
        if not valid_videos:
            return videos

        total_views = sum(v['view_count'] for v in valid_videos)
        avg_views = total_views / len(valid_videos) if len(valid_videos) > 0 else 0

        for video in videos:
            views = video.get('view_count') or 0
            if avg_views > 0:
                video['outlier_score'] = round(views / avg_views, 2)
            else:
                video['outlier_score'] = 0
            
            video['avg_views_benchmark'] = round(avg_views)

        # Sort by outlier score descending
        videos.sort(key=lambda x: x.get('outlier_score', 0), reverse=True)
        return videos



    def get_transcript(self, video_url):
        """
        Fetches transcript for a video using youtube_transcript_api.
        """
        try:
            video_id = video_url.split('v=')[-1].split('&')[0]
            # Handle short URLs or other formats if needed, but standard watch URLs work with this split usually.
            # A more robust way:
            if "youtu.be" in video_url:
                video_id = video_url.split('/')[-1]
            
            # transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            # v1.2.3 usage seems to require instance and fetch?
            transcript_list = YouTubeTranscriptApi().fetch(video_id)
            
            # Format transcript - transcript_list is a list of objects in this version
            full_text = " ".join([item.text for item in transcript_list])
            return full_text
            
        except TranscriptsDisabled:
            return "Transcripts are disabled for this video."
        except NoTranscriptFound:
            return "No transcript found for this video."
        except Exception as e:
            return f"Error fetching transcript: {e}"

if __name__ == "__main__":
    # Quick test
    scraper = YouTubeScraper()
    # Mock data to test logic without network if needed, but let's try real if user runs it.
