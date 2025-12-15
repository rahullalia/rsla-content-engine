"""
Import Instagram reels from Apify CSV exports into Content Engine database.
Usage: python import_csv.py /path/to/csv/folder
"""
import csv
import sys
from pathlib import Path
from database import add_creator, upsert_videos, get_all_creators

def parse_csv_row(row: dict) -> dict:
    """Transform Apify CSV row to our video format."""
    # Extract shortcode from URL (e.g., https://www.instagram.com/p/ABC123/)
    url = row.get('url', '')
    shortcode = url.split('/')[-2] if url else ''

    # Parse likes (might have commas or be empty)
    likes_str = row.get('likesCount', '0').replace(',', '')
    likes = int(likes_str) if likes_str.isdigit() else 0

    # Parse comments
    comments_str = row.get('commentsCount', '0').replace(',', '')
    comments = int(comments_str) if comments_str.isdigit() else 0

    # Parse timestamp to date
    timestamp = row.get('timestamp', '')
    upload_date = timestamp.split('T')[0] if timestamp else None

    return {
        'id': shortcode,
        'platform_video_id': shortcode,
        'title': (row.get('caption', '') or 'No caption')[:200],
        'url': url,
        'video_url': None,  # CSV doesn't include video URLs
        'view_count': 0,  # CSV doesn't include view counts, will use likes as proxy
        'like_count': likes,
        'comment_count': comments,
        'duration': None,
        'upload_date': upload_date,
        'thumbnail': row.get('displayUrl', ''),
        'owner_username': row.get('ownerUsername', ''),
    }

def calculate_outliers(videos: list) -> list:
    """Calculate outlier score based on likes (since views not available)."""
    if not videos:
        return []

    # Use likes as the metric since views aren't in CSV
    valid_videos = [v for v in videos if v.get('like_count', 0) > 0]

    if not valid_videos:
        for v in videos:
            v['outlier_score'] = 0
        return videos

    total_likes = sum(v['like_count'] for v in valid_videos)
    avg_likes = total_likes / len(valid_videos)

    for video in videos:
        likes = video.get('like_count', 0)
        if avg_likes > 0:
            video['outlier_score'] = round(likes / avg_likes, 2)
            # Also set view_count to likes for display purposes
            video['view_count'] = likes
        else:
            video['outlier_score'] = 0

    videos.sort(key=lambda x: x.get('outlier_score', 0), reverse=True)
    return videos

def import_csv_file(csv_path: Path) -> tuple:
    """Import a single CSV file. Returns (username, video_count)."""
    videos_by_user = {}

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            video = parse_csv_row(row)
            username = video['owner_username'].lower()

            if username not in videos_by_user:
                videos_by_user[username] = []
            videos_by_user[username].append(video)

    total_imported = 0
    for username, videos in videos_by_user.items():
        if not username:
            continue

        # Add creator if not exists
        creator_id = add_creator(
            platform='instagram',
            username=username,
            url=f'https://www.instagram.com/{username}',
            display_name=videos[0].get('owner_username', username) if videos else username
        )

        if creator_id:
            # Calculate outliers and save
            analyzed = calculate_outliers(videos)
            upsert_videos(creator_id, analyzed)
            total_imported += len(videos)
            print(f"  ✅ Imported {len(videos)} reels from @{username}")

    return len(videos_by_user), total_imported

def main():
    if len(sys.argv) < 2:
        print("Usage: python import_csv.py /path/to/csv/folder")
        print("       python import_csv.py /path/to/file.csv")
        sys.exit(1)

    path = Path(sys.argv[1])

    if path.is_file() and path.suffix == '.csv':
        csv_files = [path]
    elif path.is_dir():
        csv_files = list(path.glob('*.csv'))
    else:
        print(f"Error: {path} is not a valid CSV file or directory")
        sys.exit(1)

    if not csv_files:
        print(f"No CSV files found in {path}")
        sys.exit(1)

    print(f"Found {len(csv_files)} CSV file(s) to import\n")

    total_users = 0
    total_videos = 0

    for csv_file in csv_files:
        print(f"📁 Importing {csv_file.name}...")
        users, videos = import_csv_file(csv_file)
        total_users += users
        total_videos += videos

    print(f"\n✨ Done! Imported {total_videos} reels from {total_users} creators")

    # Show current creators
    print("\n📊 Current creators in database:")
    for creator in get_all_creators():
        platform_icon = "📺" if creator['platform'] == 'youtube' else "📸"
        print(f"  {platform_icon} @{creator['username']} ({creator['platform']}) - {creator['video_count'] or 0} videos")

if __name__ == "__main__":
    main()
