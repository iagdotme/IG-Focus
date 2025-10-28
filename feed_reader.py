#!/usr/bin/env python3
"""
Instagram Feed Reader using instagrapi
This script allows you to access posts from your Instagram feed (people you follow)
"""

from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired
import json
from datetime import datetime
from pathlib import Path
import getpass


def login_user(username: str, password: str = None, session_file: str = "session.json") -> Client:
    """
    Login to Instagram and save session for reuse
    Handles 2FA authentication if required

    Args:
        username: Your Instagram username
        password: Your Instagram password (optional if session exists)
        session_file: File to store session data

    Returns:
        Authenticated Client instance
    """
    cl = Client()
    session_path = Path(session_file)

    # Try to load existing session WITHOUT logging in again
    if session_path.exists():
        print(f"✓ Reusing existing session from {session_file}...")
        try:
            cl.load_settings(session_path)
            # Set the username
            cl.set_user_agent(cl.user_agent)

            # Test if session is still valid by making a simple API call
            try:
                cl.get_timeline_feed()
                print("✓ Session is still valid - no login needed!")
                return cl
            except Exception:
                print("Session expired, need to login again...")
                if not password:
                    raise ValueError("Password required - session expired")
                # Session expired, continue to fresh login
        except Exception as e:
            print(f"Could not load session: {e}")
            if not password:
                raise ValueError("Password required - could not load session")

    # Fresh login with 2FA handling
    if not password:
        raise ValueError("Password required for fresh login")

    print("Performing fresh login to Instagram...")
    try:
        cl.login(username, password)
    except TwoFactorRequired:
        print("\n🔐 Two-Factor Authentication Required")
        print("Check your authentication app or SMS for the verification code.")
        verification_code = input("Enter 2FA verification code: ").strip()

        if not verification_code:
            raise ValueError("2FA code is required to proceed")

        cl.login(username, password, verification_code=verification_code)
        print("✓ 2FA verification successful")

    # Save session for next time
    cl.dump_settings(session_path)
    print(f"✓ Session saved to {session_file}")

    return cl


def get_feed_posts(cl: Client, amount: int = 20) -> list:
    """
    Get posts from your Instagram feed (timeline)

    Args:
        cl: Authenticated Client instance
        amount: Number of posts to fetch

    Returns:
        List of feed posts
    """
    print(f"\nFetching {amount} posts from your feed...")

    try:
        # Get the timeline feed - returns a dict with 'feed_items' key
        feed_result = cl.get_timeline_feed()

        # Extract posts from the dict structure
        if isinstance(feed_result, dict):
            # The feed is a dict, extract the media items
            if 'feed_items' in feed_result:
                posts = [item['media_or_ad'] for item in feed_result['feed_items'] if 'media_or_ad' in item]
            elif 'items' in feed_result:
                posts = feed_result['items']
            else:
                # Try to get values if it's a simple dict
                posts = list(feed_result.values())
        elif isinstance(feed_result, list):
            posts = feed_result
        else:
            print(f"Unexpected feed type: {type(feed_result)}")
            posts = []

        # Return only the requested amount
        posts = posts[:amount] if len(posts) > amount else posts
        print(f"✓ Retrieved {len(posts)} posts")
        return posts
    except Exception as e:
        print(f"✗ Error fetching feed: {e}")
        import traceback
        traceback.print_exc()
        return []


def display_post_info(post) -> None:
    """Display information about a single post (handles both dict and object)"""

    # Handle both dict and object formats
    if isinstance(post, dict):
        post_id = post.get('id') or post.get('pk')
        user = post.get('user', {}).get('username') if isinstance(post.get('user'), dict) else post.get('user')
        caption = post.get('caption_text') or post.get('caption', {}).get('text') if isinstance(post.get('caption'), dict) else post.get('caption')
        likes = post.get('like_count', 0)
        comments = post.get('comment_count', 0)
        timestamp = post.get('taken_at')
        media_type = post.get('media_type')
        thumbnail_url = post.get('thumbnail_url')
        video_url = post.get('video_url')
    else:
        # Object format
        post_id = post.id
        user = post.user.username
        caption = post.caption_text
        likes = post.like_count
        comments = post.comment_count
        timestamp = post.taken_at
        media_type = post.media_type
        thumbnail_url = getattr(post, 'thumbnail_url', None)
        video_url = getattr(post, 'video_url', None)

    # Truncate long captions
    if caption and len(str(caption)) > 100:
        caption = str(caption)[:100] + "..."

    print(f"\n{'='*80}")
    print(f"Post ID: {post_id}")
    print(f"User: @{user}")
    print(f"Type: {media_type}")
    print(f"Posted: {timestamp}")
    print(f"Likes: {likes:,} | Comments: {comments:,}")
    if caption:
        print(f"Caption: {caption}")

    # Show media URLs
    if thumbnail_url:
        print(f"Thumbnail: {thumbnail_url}")
    if video_url:
        print(f"Video: {video_url}")


def save_feed_to_json(posts: list, filename: str = "feed_data.json") -> None:
    """Save feed posts to JSON file (handles both dict and object formats)"""

    # Convert posts to dict for JSON serialization
    posts_data = []
    for post in posts:
        if isinstance(post, dict):
            # Already a dict, just extract what we need
            post_dict = {
                "id": post.get('id') or post.get('pk'),
                "user": post.get('user', {}).get('username') if isinstance(post.get('user'), dict) else post.get('user'),
                "user_id": str(post.get('user', {}).get('pk', '')) if isinstance(post.get('user'), dict) else None,
                "caption": post.get('caption_text') or (post.get('caption', {}).get('text') if isinstance(post.get('caption'), dict) else post.get('caption')),
                "likes": post.get('like_count', 0),
                "comments": post.get('comment_count', 0),
                "timestamp": str(post.get('taken_at')) if post.get('taken_at') else None,
                "media_type": str(post.get('media_type')),
                "thumbnail_url": post.get('thumbnail_url'),
                "video_url": post.get('video_url'),
            }
        else:
            # Object format
            post_dict = {
                "id": post.id,
                "user": post.user.username,
                "user_id": str(post.user.pk),
                "caption": post.caption_text,
                "likes": post.like_count,
                "comments": post.comment_count,
                "timestamp": post.taken_at.isoformat() if post.taken_at else None,
                "media_type": str(post.media_type),
                "thumbnail_url": post.thumbnail_url if hasattr(post, 'thumbnail_url') else None,
                "video_url": post.video_url if hasattr(post, 'video_url') else None,
            }
        posts_data.append(post_dict)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(posts_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Feed data saved to {filename}")


def save_credentials(username: str):
    """Save username to a file for convenience"""
    cred_file = Path(".instagram_user")
    with open(cred_file, 'w') as f:
        f.write(username)


def load_credentials():
    """Load saved username if exists"""
    cred_file = Path(".instagram_user")
    if cred_file.exists():
        with open(cred_file, 'r') as f:
            return f.read().strip()
    return None


def main():
    """Main function to run the feed reader"""

    print("="*80)
    print("Instagram Feed Reader".center(80))
    print("="*80)

    session_file = Path("session.json")
    saved_username = load_credentials()

    # Check if we have a saved session
    if session_file.exists() and saved_username:
        print(f"\n✓ Found saved session for @{saved_username}")
        use_saved = input("Continue with saved session? (Y/n): ").strip().lower()

        if use_saved != 'n':
            username = saved_username
            print(f"Using saved username: @{username}")

            # Try to use session without password first
            try:
                cl = login_user(username, password=None)
            except ValueError as e:
                # Session expired or invalid, need password
                print(f"Note: {e}")
                password = getpass.getpass("Password: ")

                if not password:
                    print("✗ Password is required!")
                    return

                try:
                    cl = login_user(username, password)
                except Exception as e:
                    print(f"✗ Login failed: {e}")
                    return
        else:
            # User wants fresh login
            print("\nEnter new credentials:")
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ")

            if not username or not password:
                print("✗ Username and password are required!")
                return

            save_credentials(username)
            cl = login_user(username, password)
    else:
        # No saved session, need credentials
        print("\nEnter your Instagram credentials:")
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")

        if not username or not password:
            print("✗ Username and password are required!")
            return

        save_credentials(username)
        try:
            # Login
            cl = login_user(username, password)
        except Exception as e:
            print(f"\n✗ Login failed: {e}")
            return

    try:
        # Get feed posts
        amount = int(input("\nHow many posts to fetch? (default: 20): ").strip() or "20")
        posts = get_feed_posts(cl, amount)

        if not posts:
            print("No posts found in your feed.")
            return

        # Display posts
        print("\n" + "="*80)
        print("FEED POSTS".center(80))
        print("="*80)

        for i, post in enumerate(posts, 1):
            print(f"\n[{i}/{len(posts)}]", end="")
            display_post_info(post)

        # Auto-save with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"feed_{timestamp}.json"
        save_feed_to_json(posts, filename)

        print("\n✓ Done!")

    except Exception as e:
        print(f"\n✗ An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
