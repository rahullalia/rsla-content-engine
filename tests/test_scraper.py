import unittest
from src.scraper import YouTubeScraper

class TestScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = YouTubeScraper()

    def test_outlier_calculation(self):
        videos = [
            {'view_count': 100},
            {'view_count': 200}, # Avg = 150
            {'view_count': 300}, # 300/150 = 2.0
            {'view_count': None} # Should be ignored or handled
        ]
        results = self.scraper.calculate_outliers(videos)
        # 3 valid videos. Sum=600, Avg=200.
        # Wait, my mental math vs code logic:
        # Code: sum(100,200,300) = 600. len=3. avg=200.
        # Video 300: 300/200 = 1.5
        # Video 200: 200/200 = 1.0
        # Video 100: 100/200 = 0.5
        
        # Finding the one with 1.5 score
        top_video = results[0] # Sorted desc
        self.assertEqual(top_video['outlier_score'], 1.5)
    
    def test_transcript_fetching_real(self):
        # Using a stable video ID, e.g., "YouTube Rewind 2018" or essentially any short stable video.
        # Let's use a very short test video if possible, or just check it returns a string.
        # Video: "Me at the zoo" (ID: jNQXAC9IVRw) - First YouTube video, likely has captions?
        # Actually correct ID for "Me at the zoo": jNQXAC9IVRw
        video_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
        transcript = self.scraper.get_transcript(video_url)
        print(f"Transcript Result: {transcript[:50]}...")
        self.assertIsInstance(transcript, str)
        self.assertNotEqual(transcript, "Error fetching transcript")

if __name__ == '__main__':
    unittest.main()
