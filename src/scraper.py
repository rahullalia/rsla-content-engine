import yt_dlp
import statistics
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import ssl
import certifi

# Fix for macOS SSL certificate issues
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

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
