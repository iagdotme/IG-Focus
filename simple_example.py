#!/usr/bin/env python3
"""
Simple example: Get 5 posts from your Instagram feed
Note: For 2FA support, use login_with_2fa.py or feed_reader.py instead
"""

from instagrapi import Client
from instagrapi.exceptions import TwoFactorRequired

# Initialize client
cl = Client()

# Login (replace with your credentials)
username = "YOUR_USERNAME"
password = "YOUR_PASSWORD"

print("Logging in...")
try:
    cl.login(username, password)
    print("✓ Logged in successfully!")
except TwoFactorRequired:
    print("\n✗ 2FA is enabled on your account.")
    print("Please use login_with_2fa.py or feed_reader.py for 2FA support.")
    exit(1)

# Get 5 posts from your feed
print("\nFetching 5 posts from your feed...")
posts = cl.get_timeline_feed()[:5]

# Display basic info about each post
for i, post in enumerate(posts, 1):
    print(f"\n--- Post {i} ---")
    print(f"User: @{post.user.username}")
    print(f"Likes: {post.like_count:,}")
    print(f"Comments: {post.comment_count:,}")
    print(f"Caption: {post.caption_text[:100] if post.caption_text else 'No caption'}...")

print("\n✓ Done!")
