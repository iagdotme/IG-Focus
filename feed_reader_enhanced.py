#!/usr/bin/env python3
"""
Enhanced Instagram Feed Reader with Media Downloads and Comments

PERFORMANCE OPTIMIZATIONS:
- Works directly with Media objects from get_timeline_feed() (no extra media_info() calls)
- Uses instagrapi best practices for session management (no slow validation checks)
- Adds random delays between requests (1-3 seconds) to avoid rate limiting
- All needed data including sponsor_tags is available in the feed response
"""

from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired
import json
from datetime import datetime
from pathlib import Path
import getpass
import os


def login_user(username: str, password: str = None, session_file: str = "session.json") -> Client:
    """Login with session reuse - following instagrapi best practices"""
    cl = Client()
    cl.request_timeout = 30  # Increase timeout for downloads
    cl.delay_range = [1, 3]  # Add random delays between requests (best practice)
    
    session_path = Path(session_file)
    
    # Try to load existing session
    if session_path.exists():
        print(f"✓ Loading saved session...")
        try:
            cl.load_settings(session_path)
            
            # Re-login with session (instagrapi will use session, not actual login)
            # This is the recommended approach from the docs
            if password:
                try:
                    cl.login(username, password)
                    print("✓ Session reused successfully!")
                    return cl
                except Exception as e:
                    print(f"Session invalid: {e}")
                    print("Need fresh login...")
            else:
                # No password provided, just try to use the session
                print("✓ Session loaded (no validation - will check on first request)")
                return cl
                
        except Exception as e:
            print(f"Could not load session: {e}")
            if not password:
                raise ValueError("Session load failed and no password provided")
    
    # Fresh login required
    if not password:
        raise ValueError("Password required for fresh login")
    
    print("Performing fresh login to Instagram...")
    try:
        cl.login(username, password)
    except TwoFactorRequired:
        print("\n🔐 Two-Factor Authentication Required")
        verification_code = input("Enter 2FA code: ").strip()
        if not verification_code:
            raise ValueError("2FA code is required")
        cl.login(username, password, verification_code=verification_code)
        print("✓ 2FA verification successful")
    
    cl.dump_settings(session_path)
    print(f"✓ Session saved")
    return cl


def extract_post_data(cl: Client, media) -> dict:
    """Extract all available data from a Media object (already from feed)"""
    
    # The feed already returns proper Media objects, so we work directly with them
    # No need to call media_info() which makes an extra API call per post!
    
    try:
        # Check if it's a proper Media object or a dict
        is_media_object = hasattr(media, 'id') and hasattr(media, 'user')
        
        if is_media_object:
            # Extract from the Media object directly
            post_id = media.id
            code = media.code
            username = media.user.username
            user_id = str(media.user.pk)
            user_full_name = media.user.full_name
            is_verified = media.user.is_verified if hasattr(media.user, 'is_verified') else False
            user_avatar_url = media.user.profile_pic_url if hasattr(media.user, 'profile_pic_url') else None
            user_bio = media.user.biography if hasattr(media.user, 'biography') else None
            caption = media.caption_text
            likes = media.like_count
            comments_count = media.comment_count
            timestamp = int(media.taken_at.timestamp()) if media.taken_at else None
            timestamp_human = media.taken_at.strftime("%Y-%m-%d %H:%M:%S") if media.taken_at else None
            media_type = media.media_type
            media_type_name = {1: "photo", 2: "video", 8: "album"}.get(media_type, str(media_type))
            thumbnail_url = media.thumbnail_url
            video_url = media.video_url if hasattr(media, 'video_url') else None
            carousel_count = len(media.resources) if hasattr(media, 'resources') and media.resources else 0
            location_name = media.location.name if hasattr(media, 'location') and media.location else None

            # SPONSOR FIELDS - available in feed Media objects
            is_paid_partnership = media.is_paid_partnership if hasattr(media, 'is_paid_partnership') else False
            sponsor_tags = []
            if hasattr(media, 'sponsor_tags') and media.sponsor_tags:
                sponsor_tags = [{"username": s.username, "user_id": str(s.pk)} for s in media.sponsor_tags]

            # Additional metadata
            filter_type = media.filter_type if hasattr(media, 'filter_type') else None
            has_audio = media.has_audio if hasattr(media, 'has_audio') else None
        else:
            # Fallback to dict extraction
            post_dict = media if isinstance(media, dict) else (media.dict() if hasattr(media, 'dict') else media.__dict__)

            post_id = post_dict.get('id') or post_dict.get('pk')
            code = post_dict.get('code')
            user_data = post_dict.get('user', {})
            username = user_data.get('username') if isinstance(user_data, dict) else str(user_data)
            user_id = str(user_data.get('pk')) if isinstance(user_data, dict) else None
            user_full_name = user_data.get('full_name') if isinstance(user_data, dict) else None
            is_verified = user_data.get('is_verified') if isinstance(user_data, dict) else False
            user_avatar_url = user_data.get('profile_pic_url') if isinstance(user_data, dict) else None
            user_bio = user_data.get('biography') if isinstance(user_data, dict) else None

            caption_data = post_dict.get('caption')
            caption = caption_data.get('text') if isinstance(caption_data, dict) else (post_dict.get('caption_text') or caption_data)

            likes = post_dict.get('like_count', 0)
            comments_count = post_dict.get('comment_count', 0)

            timestamp = post_dict.get('taken_at')
            if timestamp:
                if isinstance(timestamp, int):
                    dt = datetime.fromtimestamp(timestamp)
                else:
                    dt = timestamp
                timestamp = int(dt.timestamp()) if hasattr(dt, 'timestamp') else timestamp
                timestamp_human = dt.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dt, 'strftime') else None
            else:
                timestamp_human = None

            media_type = post_dict.get('media_type')
            media_type_name = {1: "photo", 2: "video", 8: "album"}.get(media_type, str(media_type))

            image_versions = post_dict.get('image_versions2', {})
            candidates = image_versions.get('candidates', [])
            thumbnail_url = candidates[0].get('url') if candidates else None

            video_versions = post_dict.get('video_versions', [])
            video_url = video_versions[0].get('url') if video_versions else None

            carousel_count = len(post_dict.get('carousel_media', [])) or len(post_dict.get('resources', []))
            location = post_dict.get('location')
            location_name = location.get('name') if location and isinstance(location, dict) else None

            is_paid_partnership = post_dict.get('is_paid_partnership', False)
            sponsor_tags = []
            filter_type = post_dict.get('filter_type')
            has_audio = post_dict.get('has_audio')

    except Exception as e:
        print(f"  ⚠ Warning: Error extracting post data: {e}")
        # Return minimal data
        return {
            "id": "unknown",
            "error": str(e),
            "raw_type": str(type(media))
        }

    return {
        "id": str(post_id),
        "code": code,
        "url": f"https://www.instagram.com/p/{code}/" if code else None,
        "user": username,
        "user_id": user_id,
        "user_full_name": user_full_name,
        "is_verified": is_verified,
        "user_avatar_url": user_avatar_url,
        "user_bio": user_bio,
        "caption": caption,
        "likes": likes,
        "comments_count": comments_count,
        "timestamp": timestamp,
        "timestamp_human": timestamp_human,
        "media_type": media_type,
        "media_type_name": media_type_name,
        "thumbnail_url": thumbnail_url,
        "video_url": video_url,
        "carousel_media_count": carousel_count,
        "location": location_name,
        "filter_type": filter_type,
        "is_paid_partnership": is_paid_partnership,
        "sponsor_tags": sponsor_tags,
        "is_sponsored": is_paid_partnership or len(sponsor_tags) > 0,
        "has_audio": has_audio,
    }


def get_feed_posts(cl: Client, amount: int = 20) -> list:
    """Get feed posts with full metadata (with pagination)"""
    print(f"\nFetching {amount} posts from your feed...")

    all_posts = []
    max_attempts = 5  # Maximum pagination attempts
    attempt = 0

    try:
        while len(all_posts) < amount and attempt < max_attempts:
            attempt += 1
            print(f"  Fetching batch {attempt}... (have {len(all_posts)} posts so far)")

            feed_result = cl.get_timeline_feed()

            if isinstance(feed_result, dict):
                if 'feed_items' in feed_result:
                    posts = [item['media_or_ad'] for item in feed_result['feed_items'] if 'media_or_ad' in item]
                elif 'items' in feed_result:
                    posts = feed_result['items']
                else:
                    posts = list(feed_result.values())
            else:
                posts = feed_result

            if not posts:
                print(f"  No more posts available")
                break

            # Add new posts (avoid duplicates)
            existing_ids = {p.get('id') or p.get('pk') for p in all_posts}
            new_posts = [p for p in posts if (p.get('id') or p.get('pk')) not in existing_ids]

            if not new_posts:
                print(f"  No new posts found, stopping")
                break

            # Show details of new posts
            for post in new_posts:
                try:
                    # Try to extract basic info for display
                    username = post.user.username if hasattr(post, 'user') else post.get('user', {}).get('username', 'unknown')
                    media_type = post.media_type if hasattr(post, 'media_type') else post.get('media_type', 0)
                    media_name = {1: "photo", 2: "video", 8: "album"}.get(media_type, str(media_type))
                    caption = (post.caption_text if hasattr(post, 'caption_text') else post.get('caption_text', ''))[:50]
                    print(f"    • @{username} - {media_name} - {caption}...")
                except Exception as e:
                    print(f"    • Post fetched (details hidden)")

            all_posts.extend(new_posts)
            print(f"  ✓ Got {len(new_posts)} new posts")

            # If we have enough, stop
            if len(all_posts) >= amount:
                break

            # Small delay to be nice to Instagram's API
            import time
            time.sleep(1)

        # Return only the requested amount
        all_posts = all_posts[:amount]
        print(f"✓ Retrieved {len(all_posts)} posts total")
        return all_posts

    except Exception as e:
        print(f"✗ Error fetching feed: {e}")
        import traceback
        traceback.print_exc()
        return all_posts  # Return what we got so far  # Return what we got so far


def get_post_comments(cl: Client, post_id: str, max_comments: int = 50) -> list:
    """Fetch comments for a post"""
    try:
        comments = cl.media_comments(post_id, amount=max_comments)
        return [
            {
                "user": c.user.username,
                "text": c.text,
                "created_at": c.created_at_utc.isoformat() if hasattr(c, 'created_at_utc') else None,
                "likes": c.like_count if hasattr(c, 'like_count') else 0
            }
            for c in comments
        ]
    except Exception as e:
        print(f"  Warning: Could not fetch comments: {e}")
        return []


def download_media(cl: Client, post_data: dict, download_dir: str = "downloads", max_retries: int = 2) -> dict:
    """Download media files for a post with retry logic"""
    Path(download_dir).mkdir(exist_ok=True)

    post_id = post_data['id']
    media_type = post_data['media_type_name']
    username = post_data['user']

    downloaded_files = []

    def download_with_retry(download_func, *args, **kwargs):
        """Helper to retry downloads"""
        for attempt in range(max_retries):
            try:
                download_func(*args, **kwargs)
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  ⚠ Retry {attempt + 1}/{max_retries}...")
                    import time
                    time.sleep(2)  # Wait 2 seconds before retry
                else:
                    raise e
        return False

    try:
        if media_type == "photo":
            # Download photo (instagrapi adds extension automatically, so don't include it)
            print(f"  → Downloading photo...")
            filename = f"{username}_{post_id}"
            filepath = Path(download_dir) / filename
            if download_with_retry(cl.photo_download_by_url, post_data['thumbnail_url'], filepath):
                # Find the actual file created (might be .jpg or .png)
                actual_files = list(Path(download_dir).glob(f"{username}_{post_id}.*"))
                if actual_files:
                    downloaded_files.append(str(actual_files[0]))
                    print(f"  ✓ Downloaded photo: {actual_files[0].name}")

        elif media_type == "video":
            # Download video (instagrapi adds .mp4 automatically, so don't include it)
            print(f"  → Downloading video...")
            filename = f"{username}_{post_id}"
            filepath = Path(download_dir) / filename
            if download_with_retry(cl.video_download_by_url, post_data['video_url'], filepath):
                # Find the actual file created
                actual_files = list(Path(download_dir).glob(f"{username}_{post_id}.*"))
                if actual_files:
                    downloaded_files.append(str(actual_files[0]))
                    print(f"  ✓ Downloaded video: {actual_files[0].name}")

        elif media_type == "album":
            # Download album - need to get full media info
            media_pk = int(post_id.split('_')[0])
            print(f"  → Fetching album details...")
            media_info = cl.media_info(media_pk)

            if hasattr(media_info, 'resources'):
                total_items = len(media_info.resources)
                print(f"  → Downloading {total_items} items from album...")
                
                for idx, resource in enumerate(media_info.resources, 1):
                    item_type = "photo" if resource.media_type == 1 else "video"
                    print(f"    [{idx}/{total_items}] Downloading {item_type}...", end=" ")
                    
                    if resource.media_type == 1:  # Photo
                        filename = f"{username}_{post_id}_{idx}"  # No extension!
                        filepath = Path(download_dir) / filename
                        if download_with_retry(cl.photo_download_by_url, resource.thumbnail_url, filepath):
                            actual_files = list(Path(download_dir).glob(f"{username}_{post_id}_{idx}.*"))
                            if actual_files:
                                downloaded_files.append(str(actual_files[0]))
                                print(f"✓ {actual_files[0].name}")
                    elif resource.media_type == 2:  # Video
                        filename = f"{username}_{post_id}_{idx}"  # No extension!
                        filepath = Path(download_dir) / filename
                        if download_with_retry(cl.video_download_by_url, resource.video_url, filepath):
                            actual_files = list(Path(download_dir).glob(f"{username}_{post_id}_{idx}.*"))
                            if actual_files:
                                downloaded_files.append(str(actual_files[0]))
                                print(f"✓ {actual_files[0].name}")
                
                print(f"  ✓ Downloaded album: {len(downloaded_files)}/{total_items} files")

    except Exception as e:
        print(f"  ✗ Error downloading media: {e}")
        print(f"  💡 Tip: Check your internet connection or try again later")

    return {"downloaded_files": downloaded_files}


def display_post_info(post_data: dict) -> None:
    """Display formatted post information"""
    print(f"\n{'='*80}")
    print(f"Post: {post_data['url']}")
    print(f"User: @{post_data['user']}" + (f" ({post_data['user_full_name']})" if post_data['user_full_name'] else ""))
    if post_data['is_verified']:
        print(f"  ✓ Verified")

    # Sponsored content indicators
    if post_data.get('is_sponsored'):
        print("  💰 SPONSORED", end="")
        if post_data.get('sponsor_tags'):
            sponsors = ", ".join([f"@{s['username']}" for s in post_data['sponsor_tags']])
            print(f" - Paid partnership with {sponsors}")
        else:
            print(" - Paid partnership")

    print(f"Type: {post_data['media_type_name']}")
    if post_data['carousel_media_count'] > 0:
        print(f"  ({post_data['carousel_media_count']} items in album)")
    print(f"Posted: {post_data['timestamp_human']}")
    print(f"Likes: {post_data['likes']:,} | Comments: {post_data['comments_count']:,}")
    if post_data['location']:
        print(f"Location: {post_data['location']}")
    if post_data['caption']:
        caption = post_data['caption']
        if len(caption) > 150:
            caption = caption[:150] + "..."
        print(f"Caption: {caption}")


def load_existing_posts(directory: str = ".") -> dict:
    """Load all existing post IDs from previous feed JSON files"""
    existing_posts = {}
    
    # Find all feed_enhanced_*.json files
    json_files = list(Path(directory).glob("feed_enhanced_*.json"))
    
    if not json_files:
        return existing_posts
    
    print(f"\n🔍 Checking {len(json_files)} existing feed file(s) for duplicates...")
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Handle both array and object formats
            posts = data if isinstance(data, list) else data.get('posts', [])
            
            for post in posts:
                post_id = post.get('id')
                if post_id:
                    existing_posts[post_id] = {
                        'file': json_file.name,
                        'user': post.get('user'),
                        'timestamp': post.get('timestamp_human')
                    }
        except Exception as e:
            print(f"  ⚠ Warning: Could not read {json_file.name}: {e}")
            continue
    
    if existing_posts:
        print(f"  ✓ Found {len(existing_posts)} existing posts across all files")
    
    return existing_posts


def main():
    """Enhanced feed reader with all features"""

    print("="*80)
    print("Enhanced Instagram Feed Reader".center(80))
    print("="*80)

    # Load saved credentials
    cred_file = Path(".instagram_user")
    saved_username = cred_file.read_text().strip() if cred_file.exists() else None

    # Login
    if saved_username and Path("session.json").exists():
        print(f"\n✓ Found saved session for @{saved_username}")
        use_saved = input("Continue with saved session? (Y/n): ").strip().lower()

        if use_saved != 'n':
            username = saved_username
            try:
                cl = login_user(username, password=None)
            except ValueError as e:
                print(f"Note: {e}")
                password = getpass.getpass("Password: ")
                cl = login_user(username, password)
        else:
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ")
            cl = login_user(username, password)
            cred_file.write_text(username)
    else:
        username = input("\nUsername: ").strip()
        password = getpass.getpass("Password: ")
        cl = login_user(username, password)
        cred_file.write_text(username)

    # Options
    print("\n" + "="*80)
    amount = int(input("How many posts to fetch? (default: 20): ").strip() or "20")
    skip_duplicates = input("Skip posts you've already downloaded? (Y/n): ").strip().lower() != 'n'
    skip_sponsored = input("Skip sponsored/paid partnership posts? (y/N): ").strip().lower() == 'y'
    sort_chronological = input("Sort chronologically (newest first)? (y/N): ").strip().lower() == 'y'
    fetch_comments = input("Fetch comments? (y/N): ").strip().lower() == 'y'
    download_media_files = input("Download media files? (y/N): ").strip().lower() == 'y'

    # Load existing posts for duplicate detection
    existing_posts = load_existing_posts() if skip_duplicates else {}

    # Fetch posts
    posts = get_feed_posts(cl, amount)

    if not posts:
        print("No posts found.")
        return

    # Process posts
    print("\n" + "="*80)
    print("EXTRACTING POST DATA (fetching full info for each post...)".center(80))
    print("="*80)

    all_posts_data = []
    skipped_duplicates = 0
    skipped_sponsored = 0

    for i, post in enumerate(posts, 1):
        print(f"\n[{i}/{len(posts)}] Processing...", end=" ")

        # Extract data with proper Media object (includes sponsor_tags!)
        post_data = extract_post_data(cl, post)

        # Skip duplicates if requested
        if skip_duplicates and post_data['id'] in existing_posts:
            existing_info = existing_posts[post_data['id']]
            print(f"⏭ Skipping duplicate (already in {existing_info['file']})")
            print(f"   @{existing_info['user']} - {existing_info['timestamp']}")
            skipped_duplicates += 1
            continue

        # Skip sponsored posts if requested
        if skip_sponsored and post_data['is_sponsored']:
            print(f"⏭ Skipping sponsored post from @{post_data['user']}")
            skipped_sponsored += 1
            continue

        print("✓")
        display_post_info(post_data)

        # Get comments if requested
        if fetch_comments and post_data['comments_count'] > 0:
            print(f"\n  Fetching comments...")
            comments = get_post_comments(cl, post_data['id'])
            post_data['comments'] = comments
            print(f"  ✓ Fetched {len(comments)} comments")

        # Download media if requested
        if download_media_files:
            print(f"\n  Downloading media...")
            download_info = download_media(cl, post_data)
            post_data.update(download_info)

        all_posts_data.append(post_data)

    # Sort chronologically if requested
    if sort_chronological and all_posts_data:
        print("\n📅 Sorting posts chronologically (newest first)...")
        all_posts_data.sort(key=lambda p: p['timestamp'] or 0, reverse=True)

    # Save to JSON with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "_chrono" if sort_chronological else ""
    suffix += "_no_ads" if skip_sponsored else ""
    filename = f"feed_enhanced_{timestamp}{suffix}.json"

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_posts_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Feed data saved to {filename}")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY".center(80))
    print("="*80)
    print(f"Posts processed: {len(posts)}")
    print(f"Posts saved: {len(all_posts_data)}")
    if skipped_duplicates > 0:
        print(f"Duplicates skipped: {skipped_duplicates} ⏭")
    if skipped_sponsored > 0:
        print(f"Sponsored skipped: {skipped_sponsored} ⏭")
    print(f"\nPhotos: {sum(1 for p in all_posts_data if p['media_type_name'] == 'photo')}")
    print(f"Videos: {sum(1 for p in all_posts_data if p['media_type_name'] == 'video')}")
    print(f"Albums: {sum(1 for p in all_posts_data if p['media_type_name'] == 'album')}")
    sponsored_count = sum(1 for p in all_posts_data if p.get('is_sponsored', False))
    if sponsored_count > 0:
        print(f"Sponsored posts included: {sponsored_count}")
    if fetch_comments:
        total_comments = sum(len(p.get('comments', [])) for p in all_posts_data)
        print(f"Comments fetched: {total_comments}")
    if download_media_files:
        total_downloads = sum(len(p.get('downloaded_files', [])) for p in all_posts_data)
        print(f"Files downloaded: {total_downloads}")

    print("\n✓ Done!")


if __name__ == "__main__":
    main()
